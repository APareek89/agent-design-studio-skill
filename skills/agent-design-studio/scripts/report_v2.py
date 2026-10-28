"""Compact, vector PDF reports. Full contracts remain in linked companion files."""
from __future__ import annotations
import html
import io
import json
import math
from pathlib import Path
import re
import textwrap

GLOSSARY = {
    'canonical': 'agreed', 'discriminated': 'typed', 'payload binding': 'approved details',
    'digest': 'fingerprint', 'idempotency': 'duplicate-write protection',
    'reciprocal': 'two-way', 'terminal disposition': 'final outcome',
    'calc_digest': 'a fingerprint of the approved amount',
}
GROUPS = {'Agents (LLM)': '#E8E0FA', 'Code: tools': '#E0EDF8',
          'Code: validation': '#DDF2E9', 'Code: human triggers': '#FFF0D5'}


def plain(value):
    value = str(value)
    for old, new in sorted(GLOSSARY.items(), key=lambda pair: -len(pair[0])):
        value = re.sub(re.escape(old), new, value, flags=re.I)
    return value.replace('\u2011', '-').replace('\u2013', '-').replace('\u2014', ' - ')


def sentence(value, words=22):
    # An explicitly labelled summary, never the contract or build-file source.
    text = re.sub(r'\s+', ' ', plain(value)).strip()
    if len(text.split()) <= words:
        return text
    return ' '.join(text.split()[:words]).rstrip('.,;:') + '...'


def brief_data(design):
    p = design.get('presentation', {})
    calls = p.get('designCalls', [])
    if not calls:
        calls = [{'choice': sentence(x['data']['choice'], 12),
                  'rejected': sentence('; '.join(x['data']['alternatives']), 10),
                  'why': sentence(x['data']['tradeoffs'], 12)}
                 for x in design['stages']['framework']['items']][:5]
    autonomy = p.get('autonomy', [])
    if not autonomy:
        autonomy = [{'action': sentence(x['title'], 8),
                     'level': 'suggests' if x['data']['group'] == 'Agents (LLM)' else
                              'human decides' if x['data']['group'] == 'Code: human triggers' else 'acts alone'}
                    for x in design['stages']['components']['items']]
    risk = sorted(design['stages']['fmea']['items'],
                  key=lambda x: math.prod(x['data'][k] for k in ('severity','occurrence','detection')), reverse=True)
    cost = sum(x['data']['callsPerCase'] * (x['data']['inputTokens'] * x['data']['inputPrice'] +
               x['data']['outputTokens'] * x['data']['outputPrice']) / 1e6
               for x in design['stages']['models']['items'])
    priced = all(x['data']['inputPrice'] > 0 and x['data']['outputPrice'] > 0
                 for x in design['stages']['models']['items'])
    return {'sentence': p.get('systemSentence', sentence(design['title'], 20)), 'calls': calls,
            'autonomy': autonomy, 'risks': risk[:5],
            'blockers': [h for h in design['assumptions'] if h['launchBlocker']],
            'cost': cost, 'priced': priced}


class Report:
    def __init__(self, design, review, mode):
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.platypus import Paragraph
        self.colors, self.Paragraph, self.Style = colors, Paragraph, ParagraphStyle
        self.design, self.review, self.mode = design, review, mode
        self.buf = io.BytesIO()
        self.c = canvas.Canvas(self.buf, pagesize=A4, pageCompression=1)
        self.c.setTitle(design['title'])
        self.c.setAuthor('Agent Design Studio')
        self.width, self.height = A4
        self.left, self.right, self.top, self.bottom = 42, 553, 792, 48
        self.y, self.pages = self.top, 0
        self.styles = {name: ParagraphStyle(name, fontName=font, fontSize=size, leading=leading,
                       textColor=colors.HexColor('#18324A'), splitLongWords=True)
                       for name, font, size, leading in [('body','Helvetica',10,14), ('small','Helvetica',8.3,11),
                                                        ('title','Helvetica-Bold',20,24), ('head','Helvetica-Bold',12,16)]}

    def text(self, text, style='body', width=None, x=None):
        x = self.left if x is None else x
        width = self.right-x if width is None else width
        para = self.Paragraph(html.escape(str(text)).replace('\n','<br/>'), self.styles[style])
        _, height = para.wrap(width, 1000)
        if self.y-height < self.bottom:
            raise ValueError(f'Page {self.pages+1} is too dense near {str(text)[:60]!r}; shorten the summary or use full mode. No content was silently hidden.')
        para.drawOn(self.c, x, self.y-height)
        self.y -= height+5

    def heading(self, title):
        self.y -= 5
        self.text(title, 'head')

    def table(self, headers, rows, widths=None, small=True, heat=False):
        from reportlab.platypus import Table, TableStyle
        widths = widths or [(self.right-self.left)/len(headers)]*len(headers)
        def cell(v, bold=False):
            txt = html.escape(str(v)).replace('\n','<br/>')
            return self.Paragraph(('<b>'+txt+'</b>') if bold else txt, self.styles['small' if small else 'body'])
        cells = [[cell(v,True) for v in headers]]+[[cell(v) for v in row] for row in rows]
        tab = Table(cells,colWidths=widths,hAlign='LEFT')
        tab.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BACKGROUND',(0,0),(-1,0),self.colors.HexColor('#DCE9F1')),
                                ('ROWBACKGROUNDS',(0,1),(-1,-1),[self.colors.white,self.colors.HexColor('#F3F7FA')]),
                                ('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),
                                ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)]))
        if heat:
            for row in range(1,len(rows)+1):
                severity=11-row
                for col in range(1,11):
                    score=severity*col
                    shade='#DFF1E4' if score<15 else '#FFF0CB' if score<40 else '#F8DCD9'
                    tab.setStyle(TableStyle([('BACKGROUND',(col,row),(col,row),self.colors.HexColor(shade))]))
        _,height=tab.wrap(self.right-self.left,1000)
        if self.y-height < self.bottom:
            raise ValueError(f'Page {self.pages+1} table exceeds readable capacity; split or summarize, never shrink silently.')
        tab.drawOn(self.c,self.left,self.y-height)
        self.y-=height+7

    def finish_page(self):
        self.pages+=1
        self.c.setStrokeColor(self.colors.HexColor('#D9E3EB'))
        self.c.line(self.left,35,self.right,35)
        self.c.setFillColor(self.colors.HexColor('#566879'))
        self.c.setFont('Helvetica',8)
        self.c.drawString(self.left,22,'Agent Design Studio | '+self.mode+' | DESIGN ONLY')
        self.c.drawRightString(self.right,22,str(self.pages))
        self.c.showPage(); self.y=self.top

    def box(self,x,y,w,h,lines,fill,decision=False):
        c=self.c; c.setFillColor(self.colors.HexColor(fill)); c.setStrokeColor(self.colors.HexColor('#7191A8'))
        if decision:
            p=c.beginPath(); p.moveTo(x+w/2,y+h); p.lineTo(x+w,y+h/2); p.lineTo(x+w/2,y); p.lineTo(x,y+h/2); p.close()
            c.drawPath(p,fill=1,stroke=1)
        else:
            c.roundRect(x,y,w,h,5,fill=1,stroke=1)
        c.setFillColor(self.colors.HexColor('#18324A')); c.setFont('Helvetica',8.5)
        for i,line in enumerate(lines):
            c.drawCentredString(x+w/2,y+h/2+(len(lines)-1)*5-i*10,line)

    def arrow(self,x1,y1,x2,y2):
        c=self.c; c.setLineWidth(.7); c.setStrokeColor(self.colors.HexColor('#8BA1B1'))
        c.line(x1,y1,x2,y2)
        angle=math.atan2(y2-y1,x2-x1); size=4
        for delta in (-.45,.45):
            c.line(x2,y2,x2-size*math.cos(angle+delta),y2-size*math.sin(angle+delta))

    def task_tree(self):
        items=[t for t in self.design['stages']['tasks']['items'] if t['kind']=='task']
        lookup={t['id']:t for t in items}; children={i:[] for i in lookup}
        root=next(t['id'] for t in items if not t['data']['parentId'])
        for t in items:
            if t['data']['parentId']: children[t['data']['parentId']].append(t['id'])
        span={}
        def size(i):
            span[i]=sum(size(ch) for ch in children[i]) or 1
            return span[i]
        size(root)
        if span[root]>6:
            # Every node is still drawn; readable vertical tree accommodates wide trees.
            return self.task_tree_rows(items,lookup)
        positions={}; unit=(self.right-self.left)/span[root]; h=72
        top=self.y-20
        def layout(i,start,depth):
            mid=start+span[i]/2
            positions[i]=(self.left+mid*unit,top-depth*150)
            cursor=start
            for ch in children[i]: layout(ch,cursor,depth+1); cursor+=span[ch]
        layout(root,0,0)
        for i,(x,y) in positions.items():
            par=lookup[i]['data']['parentId']
            if par:
                px,py=positions[par]; self.arrow(px,py-h,x,y)
        for i,(x,y) in positions.items():
            t=lookup[i]; w=min(220,max(76,span[i]*unit-8))
            title=self.design.get('presentation',{}).get('taskLabels',{}).get(i,t['title'])
            lines=[i]+textwrap.wrap(plain(title),int(w/4.5))
            lines += [t['data']['mode']+' | '+t['data']['risk']+' risk']
            if len(lines)*10>h-6: raise ValueError(f'Task {i} label needs a shorter plain taskLabels entry.')
            self.box(x-w/2,y-h,w,h,lines,'#E0EDF8')
        self.y=min(y-h for x,y in positions.values())-16

    def task_tree_rows(self,items,lookup):
        if len(items)>22: raise ValueError('More than 22 tasks need a dedicated multi-page task diagram; use a narrower first release or full diagram extension.')
        yy=self.y-20
        for item in items:
            depth=0; parent=item['data']['parentId']
            while parent: depth+=1; parent=lookup[parent]['data']['parentId']
            x=self.left+depth*36
            self.box(x,yy-25,self.right-x,25,[item['id']+' | '+sentence(item['title'],9)+' | '+item['data']['mode']+' | '+item['data']['risk']+' risk'],'#E0EDF8')
            if depth:self.arrow(x-16,yy+8,x-16,yy-12); self.arrow(x-16,yy-12,x,yy-12)
            yy-=31
        self.y=yy-8

    def workflow(self):
        nodes=self.design['stages']['workflow']['items']; comps={c['id']:c for c in self.design['stages']['components']['items']}
        if len(nodes)>18: raise ValueError('Workflow exceeds 18 readable nodes on one page; author a multi-page diagram before delivery.')
        cols=2; rows=math.ceil(len(nodes)/cols); rowheight=min(98,540/max(rows,1)); boxh=min(58,rowheight-18); boxw=215
        top=self.y-10; pos={n['id']:(self.left+(i%cols)*284,top-(i//cols)*rowheight-boxh) for i,n in enumerate(nodes)}
        for n in nodes:
            x,y=pos[n['id']]
            for target in n['data']['next']:
                tx,ty=pos[target]
                # All real edges are drawn; back edges route outside the boxes.
                if ty>=y and tx==x:
                    side=x-12; self.c.line(x,y+boxh/2,side,y+boxh/2); self.c.line(side,y+boxh/2,side,ty+boxh/2); self.arrow(side,ty+boxh/2,tx,ty+boxh/2)
                else:self.arrow(x+boxw/2,y,tx+boxw/2,ty+boxh)
        for n in nodes:
            x,y=pos[n['id']]; comp=comps[n['data']['componentId']]
            title=self.design.get('presentation',{}).get('workflowLabels',{}).get(n['id'],sentence(n['title'],7))
            lines=[n['id']+' / '+comp['id']]+textwrap.wrap(plain(title),36)
            if len(lines)>4:raise ValueError(f'Workflow {n["id"]} needs a shorter label.')
            self.box(x,y,boxw,boxh,lines,GROUPS[comp['data']['group']],bool(n['data']['decision']))
        self.y=top-rows*rowheight-5
        self.text('Diamonds mark choices. Arrows show all routes, including retry and recovery. Exact branch rules are in architecture.md.','small')
        self.table(['Colour','Role'],[[colour,group] for group,colour in GROUPS.items()],[100,411])

    def decision(self):
        data=brief_data(self.design)
        old_head=self.styles['head']
        self.styles['head']=self.Style('BriefHead',fontName='Helvetica-Bold',fontSize=10,leading=12,textColor=self.colors.HexColor('#18324A'))
        self.text(plain(self.design['title']),'title')
        self.heading('The system in one sentence'); self.text(plain(data['sentence']))
        self.heading('Key design calls')
        for call in data['calls']:
            self.text(plain(call['choice'])+' Rejected: '+plain(call['rejected'])+'. Why: '+plain(call['why']),'small')
        self.heading('Who acts and who decides')
        self.table(['Action','Autonomy'],[[plain(a['action']),a['level']] for a in data['autonomy']],[355,156])
        self.heading('Top risks by RPN')
        for risk in data['risks']:
            d=risk['data']; score=d['severity']*d['occurrence']*d['detection']
            self.text(f'{risk["id"]} | {sentence(risk["title"],11)} | RPN {score}','small')
        self.heading('Launch blockers and owners')
        # Group by owner, preserving every blocker ID. Statements remain in the ledger.
        if not data['blockers']:self.text('No blockers recorded. Confirm missing facts before launch.','small')
        grouped={}
        for h in data['blockers']:grouped.setdefault(h['owner'],[]).append(h)
        for owner,items in grouped.items():
            ids=', '.join(h['id'] for h in items)
            summary='; '.join(sentence(h['statement'],5) for h in items)
            self.text(ids+': '+summary+' Owner: '+plain(owner)+'.','small')
        self.heading('Illustrative cost per case')
        note='Provider costs are unknown.' if not data['priced'] else 'This is an estimate, not a current provider quote.'
        self.text(f'USD {data["cost"]:.5f} per case in the model budget. '+note+' Staff and tools cost extra.','small')
        self.text(f'Review status: {self.review["method"]}; round {self.review["round"]}; {self.review["status"]}.','small')
        self.text('Proposed design. Full rules and blockers: design.json and assumptions.md.','small')
        self.styles['head']=old_head

    def risks(self):
        risks=self.design['stages']['fmea']['items']
        self.heading('Risk heat table - severity x occurrence')
        self.text('Each cell names the risks at that severity and occurrence. The full scores, causes, controls and owners are in fmea-register.csv.','small')
        rows=[]
        for sev in range(10,0,-1):
            rows.append([str(sev)]+[', '.join(x['id'] for x in risks if x['data']['severity']==sev and x['data']['occurrence']==occ) or '-' for occ in range(1,11)])
        self.table(['S / O']+[str(i) for i in range(1,11)],rows,[43]+[46.8]*10,heat=True)
        self.table(['Risk','Control summary / full register linked'],[[x['id']+' '+sentence(x['title'],6),sentence(x['data']['control'],21)] for x in risks],[160,351])
        self.text('Risk scores are proposed estimates. They are not measured odds or risk acceptance.','small')

    def coverage(self):
        self.heading('Evaluation coverage matrix')
        tests=[e for e in self.design['stages']['evals']['items'] if e['data']['category']=='golden']
        targets=[(r['id'],'failureModeIds') for r in self.design['stages']['fmea']['items']]
        targets += [(t['id'],'taskIds') for t in self.design['stages']['tasks']['items'] if t['kind']=='task' and t['data']['mode']=='leaf' and t['data']['risk']=='high']
        for start in range(0,max(1,len(tests)),12):
            batch=tests[start:start+12]
            if start:
                self.finish_page(); self.heading('Evaluation coverage matrix - continued')
            self.table(['Risk / task']+[e['id'] for e in batch],[[ident]+['X' if ident in e['data'][key] else '-' for e in batch] for ident,key in targets], [85]+[426/max(1,len(batch))]*len(batch))
        self.text('X means the test is linked to that risk or task. It does not mean the test passed. Complete fixtures and assertions: eval-set.json.','small')

    def summary_stage(self,key):
        for item in self.design['stages'][key]['items']:
            self.heading(item['id']+' - '+item['title'])
            self.text(sentence(item['description'],38))
            self.text('Why: '+sentence(item['reasoning'],26),'small')

    def build(self):
        self.decision(); self.finish_page()
        self.heading('Task tree'); self.task_tree()
        self.text('Labels show each leaf mode and risk. Full task inputs, examples and limits are in design.json and PRD.md.','small')
        self.heading('Plain words and scope')
        self.text(plain(self.design.get('presentation',{}).get('scopeSummary','Only the actions shown in this plan are in scope. Missing policies and access rights must be checked before launch.')))
        self.text('A fingerprint is a check that the approved details have not changed. A record ID is proof from a tool that the change was saved.','small')
        self.finish_page()
        self.heading('Workflow diagram'); self.workflow(); self.finish_page()
        self.heading('Top risks and release checks'); self.risks()
        if self.mode=='lite':
            self.text('Full design and test links are in design.json. This short brief omits detailed contracts.','small')
            self.finish_page(); return
        self.finish_page()
        self.heading('Components and contracts')
        self.text('This inventory is a summary. Exact typed inputs, outputs and permission rules are in architecture.md and the build milestone files.','small')
        self.table(['Component / group','Responsibility','Task IDs'],[[c['id']+' / '+c['data']['group'],sentence(c['title'],10),', '.join(c['data']['taskIds'])] for c in self.design['stages']['components']['items']],[153,261,97])
        self.heading('Shared control boundary'); self.text('Code checks identity, money, dates and limits. A model may suggest a choice. It cannot authorise or perform a business write.')
        self.finish_page()
        self.heading('Architecture and model budget'); self.summary_stage('framework')
        data=brief_data(self.design)
        self.heading('Model cost')
        self.text(f'Illustrative model cost is USD {data["cost"]:.5f} per case. Unknown prices are not free service. Confirm rates, traffic, staff and tools before launch.')
        self.text('Full call counts, token budgets, rejected choices and costs: design.json, architecture.md and assumptions.md.','small'); self.finish_page()
        self.coverage(); self.finish_page()
        self.heading('Evaluation plan')
        self.table(['Test','Layer','Purpose'],[[item['id'],item['data']['category'],sentence(item['title'],12)] for item in self.design['stages']['evals']['items']],[45,65,401])
        self.text('These are test plans. No business controls, provider quality or user outcomes were measured. See eval-set.json for fixtures and pass rules.','small'); self.finish_page()
        self.heading('Measurement and rollout'); self.summary_stage('rollout'); self.finish_page()
        self.heading('Build handoff and review')
        self.text('Start with build/00-overview.md. Load one milestone file at a time. Exact source rules remain in design.json; do not treat design approval as live write permission.')
        for item in self.design['stages']['export']['items']:
            self.text(item['id']+': '+sentence(item['description'],28),'small')
        self.heading('Review dimensions - evidence in review.json')
        self.table(['Dimension','Score','Dimension','Score'],[[self.review['dimensions'][i]['id'],str(self.review['dimensions'][i]['score'])+'/4',self.review['dimensions'][i+6]['id'],str(self.review['dimensions'][i+6]['score'])+'/4'] for i in range(6)],[160,95,161,95])
        for issue in self.review['issues']:
            self.text(issue['id']+' '+issue['severity']+' '+('resolved' if issue['resolved'] else 'OPEN')+': '+sentence(issue['message'],24),'small')
        self.heading('Glossary')
        for term,meaning in GLOSSARY.items():self.text(term+': '+meaning,'small')
        self.text('After delivering DESIGN.pdf, ask the user: Would you also like a visual HTML version in the same ten-stage structure as the app? Generate HTML only after opt-in, unless already requested.','small')
        self.text('Full assumptions, owners and evidence: assumptions.md. Review method and failed rounds are preserved in review.json and review-round-*.json.','small')
        self.finish_page()


def render(design,review,out,mode='standard'):
    if mode not in ('lite','standard'):raise ValueError('Compact PDF mode must be lite or standard.')
    r=Report(design,review,mode); r.build(); r.c.save()
    limit=4 if mode=='lite' else 12
    if r.pages>limit:raise ValueError(f'{mode} PDF exceeds {limit} pages; move detailed appendices into companions.')
    path=Path(out); path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('xb') as handle:handle.write(r.buf.getvalue())
    return {'ok':True,'status':review['status'],'mode':mode,'pages':r.pages,'bytes':path.stat().st_size,'file':str(path.resolve()),'designOnly':True,'diagrams':['task-tree-vector','workflow-vector','fmea-heat-table']+(['eval-coverage-matrix'] if mode=='standard' else [])}
