"""Lean companion export with bounded, selected milestone context."""
from __future__ import annotations
import hashlib
import json
import os
import re
from pathlib import Path
import tempfile
import importlib.util

EVIDENCE='_evidence/'
COMPANIONS=('PRD.md','architecture.md','eval-set.json','fmea-register.csv','assumptions.md')


def _module(name):
    spec=importlib.util.spec_from_file_location('studio_export_'+name,Path(__file__).with_name(name+'.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


def coverage_lines(structural):
    cov=structural.get('coverage') if isinstance(structural,dict) else None
    if not cov:return []
    lines=['## Expected information','',f"{cov['coveredRequired']} of {cov['required']} required items covered"+(f"; justified: {', '.join(cov['justified'])}" if cov['justified'] else '')+'.']
    if cov['missingRequired']:lines.append('Missing: '+'; '.join(f"{c['id']} {c['title']} ({c['evidence']})" for c in cov['checks'] if c['id'] in cov['missingRequired']))
    if cov['missingRecommended']:lines.append('Recommended: '+'; '.join(f"{c['id']} {c['title']}" for c in cov['checks'] if c['id'] in cov['missingRecommended']))
    lines.append('Coverage checks look for expected information; they do not judge its quality. Details: validation.json.')
    lines.append('')
    return lines


# A build file quotes the brief; it never copies it. A 60 KB brief used to be
# pasted whole into build/00-overview.md, which broke the standard export with
# an error about splitting milestones - advice that could not help, because the
# milestones were not the problem.
BRIEF_QUOTE_BYTES=2000
FILE_LIMIT=25000
TOTAL_LIMIT=100000


def quote_brief(brief,limit=BRIEF_QUOTE_BYTES):
    """The first `limit` characters of the brief, cut on a word, and whether it was cut."""
    text=str(brief or '')
    if len(text)<=limit:return text,False
    head=text[:limit]
    cut=head.rsplit(' ',1)[0] if ' ' in head[-200:] else head
    return cut.rstrip()+' [...]',True


def biggest_field(name,text,design):
    """Which part of the design makes this build file big.

    "Split milestones" is useless advice when the overview is large because the
    brief is 60 KB, so the error names the field a reader can actually act on.
    """
    if name.endswith('00-overview.md'):
        brief=len(str(design.get('brief','')).encode())
        if brief>len(text.encode())/3:return '$.brief (%s bytes)'%f'{brief:,}'
        return '$.milestones (the overview lists %d)'%len(design.get('milestones') or [])
    widest,size=None,0
    for key in ('components','workflow'):
        for item in design['stages'][key]['items']:
            length=len(str(item.get('description','')).encode())
            if length>size and item['id'] in text:widest,size=item['id'],length
    return ('$.stages contract %s (%s bytes)'%(widest,f'{size:,}')) if widest else 'the selected contracts'


def size_error(files,oversize,total,design):
    named=', '.join('%s: %s bytes, largest part %s'%(f,f'{len(files[f].encode()):,}',biggest_field(f,files[f],design))
                    for f in oversize)
    parts=[]
    if oversize:parts.append('over the %s KB file limit -> %s'%(FILE_LIMIT//1000,named))
    if total>TOTAL_LIMIT:parts.append('the build folder is %s bytes, over the %s KB total'%(f'{total:,}',TOTAL_LIMIT//1000))
    return ('Build context exceeds standard limits (%s KB/file, %s KB total): %s. Keep full contracts in companions; '
            'the brief is quoted, not copied.'%(FILE_LIMIT//1000,TOTAL_LIMIT//1000,'; '.join(parts)))


def readme(design, review, mode, milestone_count, structural=None):
    lines=['# '+design['title'],'',f'> {review["status"].upper()} | DESIGN ONLY. {review["method"]}; round {review["round"]}. A proposed design, not an approved or built system.','',
           '## Open first','','1. `DESIGN.html`: the clickable read-only view. Decision brief, then the ten steps, then assumptions and review.',
           '2. `DESIGN.pdf`: the same design as a readable report'+(' (at most 12 pages).' if mode=='standard' else ' with appendices.' if mode=='full' else ' (four pages).'),'',
           '## Files','']
    rows=[('DESIGN.html','Read-only visual view; no approval controls, no network assets.'),('DESIGN.pdf','Decision brief on page 1, then the design steps.'),('design.json','The single source for every ID, contract and fixture.'),
          ('review.json','Review record; earlier rounds are kept as review-round-N.json.'),('validation.json','Structural checks and generated-file hashes.'),('run-report.json','Timing, sizes, pages and validator results, when recorded.')]
    if mode!='lite':
        rows.insert(2,('build/',f'00-overview.md plus {milestone_count} milestone file(s), each under 25 KB in standard mode.'))
        rows+= [('_evidence/eval-set.json','Complete evaluation fixtures and assertions.'),('_evidence/fmea-register.csv','Scored risks with controls, owners and linked tests.'),('_evidence/assumptions.md','Proposed facts with owners, verification and launch blockers.'),
                ('_evidence/PRD.md','Readable summary of all ten stages.'),('_evidence/architecture.md','Exact component, workflow, architecture and model contracts.')]
    lines+=[f'- `{name}`: {text}' for name,text in rows]
    lines+=['']+coverage_lines(structural)+['Code owns money, identity, dates and limits. Models suggest or explain; they hold no write authority. A design review is not stakeholder approval, measured accuracy or an executed business control.','']
    return '\n'.join(lines)


def dump(value):return json.dumps(value,ensure_ascii=False,indent=2)+'\n'


def make_docs(D, design, review, structural, rr, design_hash, review_hash, mode):
    # Reuse exact risk/eval/assumption exports; do not duplicate the whole design in prose.
    R=_module('report_v2')
    base=D.render_exports(design,review,structural,rr,design_hash,review_hash)
    docs={(EVIDENCE+name if name in COMPANIONS else name):text for name,text in base.items()}
    banner=f'> {review["status"].upper()} | DESIGN ONLY. {review["method"]}; round {review["round"]}.\n\n'
    prd='# '+design['title']+'\n\n'+banner+'## Original brief\n\n'+design['brief']+'\n\n'
    for key in D.STAGES:
        prd+='## '+key.title()+'\n\n'
        for item in design['stages'][key]['items']:
            prd+=D._item_md(item)+'\n' if key in ('framework','rollout','export') else f"- **{item['id']} {item['title']}**: {item['description']}\n"
        prd+='\n'
    prd+='Full exact data and source evidence: [design.json](../design.json). Launch facts and owners: [assumptions.md](assumptions.md).\n'
    docs[EVIDENCE+'PRD.md']=prd
    tasks,flow=D._graphs(design)
    architecture='# Architecture\n\n'+banner+'## Task tree\n\n'+D._fence(tasks,'mermaid')+'\n## Workflow\n\n'+D._fence(flow,'mermaid')
    architecture+='\n## Exact component and branch contracts\n\n'
    for key in ('components','workflow','framework','models'):
        architecture+=D._stage_md(design,key)+'\n'
    docs[EVIDENCE+'architecture.md']=architecture
    milestones=design.get('milestones')
    if not milestones:
        # Compatibility for old designs: one responsibility per milestone.
        milestones=[]
        for i,comp in enumerate(design['stages']['components']['items'],1):
            milestones.append({'id':f'{i:02d}','title':comp['title'],'componentIds':[comp['id']],
                               'taskIds':comp['data']['taskIds'],'evalIds':[e['id'] for e in design['stages']['evals']['items'] if comp['id'] in e['data']['componentIds']],
                               'acceptanceCriteria':['Implement the declared contract and all named assertions; do not execute live actions without user authority.']})
    quote,trimmed=quote_brief(design['brief'])
    overview='# Build overview\n\n'+banner+quote+'\n\n'
    if trimmed:
        overview+=('The brief above is the first %d characters of a %s-character brief. '
                   'The full brief is design.json -> brief; the full PDF carries it as an appendix.\n\n'
                   %(len(quote),f"{len(design['brief']):,}"))
    overview+='Load one milestone file at a time. Contracts below are selected by component; full source is ../design.json. Test IDs resolve to complete fixtures in ../_evidence/eval-set.json. Do not load the entire design unless a dependency requires it.\n\n'
    overview+='Code owns money, identity, dates and limits. The agent never holds write authority. Keep proposed policies and owners distinct from verified facts. Launch blockers: ../_evidence/assumptions.md. Complete rollout gates and owners: ../_evidence/PRD.md#rollout.\n\n'
    overview+=R.HTML_NOTE+' Deliver DESIGN.html and DESIGN.pdf together; neither grants write authority.\n\n'
    comps={c['id']:c for c in design['stages']['components']['items']}
    used=set(); covered_workflow=set(); files={}; component_files={}
    for index,m in enumerate(milestones,1):
        ids=set(m['componentIds'])
        if not ids or not ids<=comps.keys():raise ValueError('A milestone must select real component IDs.')
        used.update(ids)
        filename=f'build/{index:02d}-milestone.md'
        overview+=f'- [{m["title"]}]({Path(filename).name}) — '+', '.join(sorted(ids))+'\n'
        text='# '+m['title']+'\n\n'+banner
        text+='Depends on earlier milestones where their outputs are inputs below. Cross-milestone shared types are read by ID from ../design.json, not copied.\n\n'
        text+='## Selected contracts\n\n'
        for cid in sorted(ids):
            if cid in component_files:
                text+=f'Exact shared {cid} contract: [{component_files[cid]}]({component_files[cid]}). Load that contract before this part; it is unchanged.\n\n'
            else:
                text+=D._item_md(comps[cid])+'\n'
                component_files[cid]=Path(filename).name
        text+='## Workflow rules\n\n'
        workflow_ids=m.get('workflowIds')
        eligible={w['id'] for w in design['stages']['workflow']['items'] if w['data']['componentId'] in ids}
        if workflow_ids is not None and (not isinstance(workflow_ids,list) or not set(workflow_ids)<=eligible):raise ValueError('Milestone workflowIds must belong to selected components.')
        covered_workflow.update(eligible if workflow_ids is None else workflow_ids)
        for w in design['stages']['workflow']['items']:
            if w['data']['componentId'] in ids and (workflow_ids is None or w['id'] in workflow_ids):text+=D._item_md(w)+'\n'
        text+='## Required tests\n\nFor each ID below, load ../_evidence/eval-set.json items[id].data.input, .expected and .passRule. These are the full fixture, expected result and exact assertions; no inherited test context is assumed.\n\n'
        wanted=set(m['evalIds'])
        actual={e['id'] for e in design['stages']['evals']['items'] if ids.intersection(e['data']['componentIds'])}
        if not actual<=wanted:raise ValueError(f'Milestone {m["id"]} omits tests {sorted(actual-wanted)}.')
        for e in design['stages']['evals']['items']:
            if e['id'] in wanted:
                d=e['data'];text+=f"- {e['id']}: {e['title']}\n"
        text+='## Acceptance criteria\n\n'+'\n'.join('- '+v for v in m['acceptanceCriteria'])+'\n'
        files[filename]=text
    if used!=comps.keys():raise ValueError('Every component must belong to at least one milestone.')
    if covered_workflow!={w['id'] for w in design['stages']['workflow']['items']}:raise ValueError('Every workflow contract must belong to a milestone.')
    files['build/00-overview.md']=overview
    files['README.md']=readme(design,review,mode,len(milestones),structural)
    if mode=='standard':
        oversize=[f for f,v in files.items() if len(v.encode())>FILE_LIMIT]
        total=sum(len(v.encode()) for v in files.values())
        if oversize or total>TOTAL_LIMIT:
            raise ValueError(size_error(files,oversize,total,design))
    docs.pop('build-prompt.md')
    docs.update(files)
    report=json.loads(docs['validation.json']);report['mode']=mode;report['generatedFiles']=list(docs)
    report['fileSha256']={name:hashlib.sha256(value.encode()).hexdigest() for name,value in docs.items() if name!='validation.json'}
    docs['validation.json']=dump(report)
    if mode=='lite':
        # User-facing artifacts are the four-page PDF, DESIGN.html and design.json; review and check evidence are retained.
        docs={name:docs[name] for name in ('validation.json',)}
        report['generatedFiles']=list(docs);report['fileSha256']={};docs['validation.json']=dump(report)
    return docs


def add_html(docs, design, review, mode, rounds):
    """Render DESIGN.html as a tracked generated file; the manifest hash covers it."""
    html=_module('design_html').render_html(design,review,mode,rounds)
    report=json.loads(docs['validation.json'])
    docs['DESIGN.html']=html
    report['generatedFiles']=list(docs)
    report.setdefault('fileSha256',{})['DESIGN.html']=hashlib.sha256(html.encode()).hexdigest()
    docs['validation.json']=dump(report)
    return docs


def export_mode(D,design_path,out,review_path,mode,html=True):
    if mode not in ('lite','standard','full'):raise ValueError('Unknown output mode.')
    design_path,review_path,out=Path(design_path),Path(review_path),Path(out)
    design=D.load_json(design_path);structural=D.validate_design(design)
    if not structural['valid']:return {'ok':False,'status':'structural-errors','errors':structural['errors']}
    review=D.load_json(review_path);rr=D.validate_review(review,True)
    if not rr['valid']:return {'ok':False,'status':'invalid-review','errors':rr['errors']}
    R=_module('report_v2')
    docs=make_docs(D,design,review,structural,rr,hashlib.sha256(design_path.read_bytes()).hexdigest(),hashlib.sha256(review_path.read_bytes()).hexdigest(),mode)
    if html:
        rounds=sorted({p.name for folder in {review_path.parent,out} if folder.is_dir() for p in folder.glob('review-round-*.json') if p.is_file()})
        docs=add_html(docs,design,review,mode,rounds)
    if out.is_symlink() or out.exists() and not out.is_dir():raise ValueError('Output must be an ordinary directory.')
    prior={}; recognized=False
    manifest=out/'validation.json'
    if manifest.is_file():
        previous=D.load_json(manifest)
        if previous.get('generator')==D.GENERATOR and isinstance(previous.get('fileSha256'),dict):
            prior=previous['fileSha256'];recognized=True
    protected={design_path.resolve(),review_path.resolve()}
    for name in docs:
        dest=out/name
        if dest.resolve() in protected or dest.is_symlink() or dest.parent.is_symlink():raise ValueError('Refusing input or symlink output alias: '+str(dest))
        if dest.exists():
            if not dest.is_file():raise ValueError('Output target is not a file: '+str(dest))
            for inp in (design_path,review_path):
                if os.path.samefile(dest,inp):raise ValueError('Refusing hardlink input alias.')
            if name=='validation.json':
                if not recognized:raise ValueError('Existing validation file has no v2 generated-file hashes; use a fresh folder.')
            elif prior.get(name)!=hashlib.sha256(dest.read_bytes()).hexdigest():
                raise ValueError('Refusing to overwrite an unrelated or edited file: '+str(dest))
    stale=[]
    allowed={'PRD.md','architecture.md','build-prompt.md','eval-set.json','fmea-register.csv','assumptions.md','DESIGN.html','README.md'}|{EVIDENCE+c for c in COMPANIONS}
    for name,expected_hash in prior.items():
        if name in docs:continue
        if name not in allowed and not re.fullmatch(r'build/(?:00-overview|[0-9]{2}-milestone)\.md',name):raise ValueError('Unexpected prior generated path; refusing cleanup: '+name)
        old=out/name
        if not old.exists() and not old.is_symlink():continue
        if old.is_symlink() or old.parent.is_symlink() or not old.is_file() or old.resolve() in protected:raise ValueError('Unsafe obsolete generated target: '+str(old))
        if any(os.path.samefile(old,inp) for inp in (design_path,review_path)):raise ValueError('Obsolete target aliases input.')
        if hashlib.sha256(old.read_bytes()).hexdigest()!=expected_hash:raise ValueError('Obsolete generated file was edited; refusing cleanup: '+str(old))
        stale.append(old)
    out.mkdir(parents=True,exist_ok=True)
    for name in [n for n in docs if n!='validation.json']+['validation.json']:
        text=docs[name]
        dest=out/name;dest.parent.mkdir(parents=True,exist_ok=True)
        tmp=None
        try:
            with tempfile.NamedTemporaryFile('w',dir=dest.parent,delete=False,encoding='utf-8') as f:
                tmp=Path(f.name);f.write(text)
            os.replace(tmp,dest)
        finally:
            if tmp and tmp.exists():tmp.unlink()
    for old in stale:old.unlink()
    for sub in ('build','_evidence'):
        folder=out/sub
        if folder.is_dir() and not folder.is_symlink() and not any(folder.iterdir()):folder.rmdir()
    return {'ok':True,'mode':mode,'status':rr['status'],'html':html,'files':[str((out/name).resolve()) for name in docs],'designOnly':True}
