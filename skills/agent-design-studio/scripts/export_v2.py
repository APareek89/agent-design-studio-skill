"""Lean companion export with bounded, selected milestone context."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import tempfile

QUESTION='Would you also like a visual HTML version in the same ten-stage structure as the app?'


def dump(value):return json.dumps(value,ensure_ascii=False,indent=2)+'\n'


def make_docs(D, design, review, structural, rr, design_hash, review_hash, mode):
    # Reuse exact risk/eval/assumption exports; do not duplicate the whole design in prose.
    docs=D.render_exports(design,review,structural,rr,design_hash,review_hash)
    banner=f'> {review["status"].upper()} | DESIGN ONLY. {review["method"]}; round {review["round"]}.\n\n'
    prd='# '+design['title']+'\n\n'+banner+'## Original brief\n\n'+design['brief']+'\n\n'
    for key in D.STAGES:
        prd+='## '+key.title()+'\n\n'
        for item in design['stages'][key]['items']:
            prd+=f"- **{item['id']} {item['title']}**: {item['description']}\n"
        prd+='\n'
    prd+='Full exact data and source evidence: [design.json](design.json). Launch facts and owners: [assumptions.md](assumptions.md).\n'
    docs['PRD.md']=prd
    tasks,flow=D._graphs(design)
    architecture='# Architecture\n\n'+banner+'## Task tree\n\n'+D._fence(tasks,'mermaid')+'\n## Workflow\n\n'+D._fence(flow,'mermaid')
    architecture+='\n## Exact component and branch contracts\n\n'
    for key in ('components','workflow','framework','models'):
        architecture+=D._stage_md(design,key)+'\n'
    docs['architecture.md']=architecture
    milestones=design.get('milestones')
    if not milestones:
        # Compatibility for old designs: one responsibility per milestone.
        milestones=[]
        for i,comp in enumerate(design['stages']['components']['items'],1):
            milestones.append({'id':f'{i:02d}','title':comp['title'],'componentIds':[comp['id']],
                               'taskIds':comp['data']['taskIds'],'evalIds':[e['id'] for e in design['stages']['evals']['items'] if comp['id'] in e['data']['componentIds']],
                               'acceptanceCriteria':['Implement the declared contract and all named assertions; do not execute live actions without user authority.']})
    overview='# Build overview\n\n'+banner+design['brief']+'\n\n'
    overview+='Load one milestone file at a time. Contracts below are selected by component; full source is ../design.json. Test IDs resolve to complete fixtures in ../eval-set.json. Do not load the entire design unless a dependency requires it.\n\n'
    overview+='Code owns money, identity, dates and limits. The agent never holds write authority. Keep proposed policies and owners distinct from verified facts. Launch blockers: ../assumptions.md.\n\n'
    overview+='After delivering DESIGN.pdf, ask the user: '+QUESTION+' Generate HTML only after opt-in, unless already requested.\n\n'
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
        text+='## Required tests\n\nFor each ID below, load ../eval-set.json items[id].data.input, .expected and .passRule. These are the full fixture, expected result and exact assertions; no inherited test context is assumed.\n\n'
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
    if mode=='standard':
        oversize=[f for f,v in files.items() if len(v.encode())>25000]
        if oversize or sum(len(v.encode()) for v in files.values())>100000:
            raise ValueError('Build context exceeds standard limits (25 KB/file, 100 KB total). Split milestones or remove duplicated context; keep full contracts in companions. '+str(oversize))
    docs.pop('build-prompt.md')
    docs.update(files)
    report=json.loads(docs['validation.json']);report['mode']=mode;report['generatedFiles']=list(docs)
    report['fileSha256']={name:hashlib.sha256(value.encode()).hexdigest() for name,value in docs.items() if name!='validation.json'}
    docs['validation.json']=dump(report)
    if mode=='lite':
        # User-facing artifacts are the four-page PDF and design.json; review and check evidence are retained.
        docs={name:docs[name] for name in ('validation.json',)}
        report['generatedFiles']=list(docs);report['fileSha256']={};docs['validation.json']=dump(report)
    return docs


def export_mode(D,design_path,out,review_path,mode):
    if mode not in ('lite','standard','full'):raise ValueError('Unknown output mode.')
    design_path,review_path,out=Path(design_path),Path(review_path),Path(out)
    design=D.load_json(design_path);structural=D.validate_design(design)
    if not structural['valid']:return {'ok':False,'status':'structural-errors','errors':structural['errors']}
    review=D.load_json(review_path);rr=D.validate_review(review,True)
    if not rr['valid']:return {'ok':False,'status':'invalid-review','errors':rr['errors']}
    docs=make_docs(D,design,review,structural,rr,hashlib.sha256(design_path.read_bytes()).hexdigest(),hashlib.sha256(review_path.read_bytes()).hexdigest(),mode)
    if out.is_symlink() or out.exists() and not out.is_dir():raise ValueError('Output must be an ordinary directory.')
    prior={}
    manifest=out/'validation.json'
    if manifest.is_file():
        previous=D.load_json(manifest)
        if previous.get('generator')==D.GENERATOR:prior=previous.get('fileSha256',{})
    protected={design_path.resolve(),review_path.resolve()}
    for name in docs:
        dest=out/name
        if dest.resolve() in protected or dest.is_symlink() or dest.parent.is_symlink():raise ValueError('Refusing input or symlink output alias: '+str(dest))
        if dest.exists():
            if not dest.is_file():raise ValueError('Output target is not a file: '+str(dest))
            for inp in (design_path,review_path):
                if os.path.samefile(dest,inp):raise ValueError('Refusing hardlink input alias.')
            if name=='validation.json':
                if not prior:raise ValueError('Existing validation file has no v2 generated-file hashes; use a fresh folder.')
            elif prior.get(name)!=hashlib.sha256(dest.read_bytes()).hexdigest():
                raise ValueError('Refusing to overwrite an unrelated or edited file: '+str(dest))
    out.mkdir(parents=True,exist_ok=True)
    for name,text in docs.items():
        dest=out/name;dest.parent.mkdir(parents=True,exist_ok=True)
        tmp=None
        try:
            with tempfile.NamedTemporaryFile('w',dir=dest.parent,delete=False,encoding='utf-8') as f:
                tmp=Path(f.name);f.write(text)
            os.replace(tmp,dest)
        finally:
            if tmp and tmp.exists():tmp.unlink()
    return {'ok':True,'mode':mode,'status':rr['status'],'files':[str((out/name).resolve()) for name in docs],'designOnly':True}
