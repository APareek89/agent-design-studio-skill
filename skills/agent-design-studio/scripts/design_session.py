"""Persist opt-in checkpoints and apply task edits without stale downstream stages.

Only the host conversation can establish that edits came from the user. This
helper records supplied edits; it never approves, times out or resumes itself.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
from pathlib import Path

ORDER=('context','tasks','components','workflow','framework','models','fmea','evals','rollout','export')


def apply_task_edits(design, edits):
    result=copy.deepcopy(design)
    tasks=result['stages']['tasks']['items']
    task_ids={t['id'] for t in tasks if t['kind']=='task'}
    removed=set(edits.get('removeTaskIds',[]))
    if not removed<=task_ids:raise ValueError('Cannot remove unknown task IDs.')
    roots={t['id'] for t in tasks if t['kind']=='task' and not t['data']['parentId']}
    if roots & removed:raise ValueError('Edit the root scope instead of removing the whole task tree.')
    while True:
        children={t['id'] for t in tasks if t['kind']=='task' and t['data']['parentId'] in removed}
        if children<=removed:break
        removed|=children
    patches=edits.get('taskEdits',{})
    if not isinstance(patches,dict) or not set(patches)<=task_ids-removed:raise ValueError('Task edits must name retained tasks.')
    retained=[]
    for t in tasks:
        if t['id'] in removed:continue
        if t['kind']=='attribute':
            t['data']['taskIds']=[i for i in t['data']['taskIds'] if i not in removed]
            if not t['data']['taskIds']:continue
        if t['id'] in patches:
            patch=patches[t['id']]
            if not isinstance(patch,dict) or not set(patch)<={'title','description','reasoning','data'}:raise ValueError('Only declared task fields can be edited.')
            if 'data' in patch:
                if not isinstance(patch['data'],dict):raise ValueError('Task data edit must be an object.')
                t['data'].update(patch['data'])
            t.update({k:v for k,v in patch.items() if k!='data'})
        retained.append(t)
    if not any(t['kind']=='task' and t['data']['mode']=='leaf' for t in retained):raise ValueError('At least one leaf must remain.')
    result['stages']['tasks']['items']=retained
    # Rebuild dependency stages from the user's accepted task tree. Partial old
    # contracts must not masquerade as a validated final design.
    for key in ORDER[2:]:result['stages'][key]={'items':[],'assumptions':[]}
    for key in ('semantics','milestones','presentation'):
        result.pop(key,None)
    return result, sorted(removed)


def checkpoint(design, stage, destination):
    if stage not in ('tasks','components'):raise ValueError('Only task and component checkpoints exist.')
    path=Path(destination)
    value={'version':'1.1','state':'awaiting-user','stage':stage,'designSha256':hashlib.sha256(json.dumps(design,sort_keys=True).encode()).hexdigest(),
           'summary':[{'id':i['id'],'title':i['title'],'data':i['data']} for i in design['stages'][stage]['items']]}
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as f:json.dump(value,f,indent=2)
    return value


def main():
    p=argparse.ArgumentParser(description=__doc__); sub=p.add_subparsers(dest='cmd',required=True)
    cp=sub.add_parser('checkpoint');cp.add_argument('design');cp.add_argument('--stage',choices=('tasks','components'),required=True);cp.add_argument('--out',required=True)
    ap=sub.add_parser('apply-tasks');ap.add_argument('design');ap.add_argument('--edits',required=True);ap.add_argument('--checkpoint',required=True);ap.add_argument('--out',required=True)
    a=p.parse_args();design=json.loads(Path(a.design).read_text())
    if a.cmd=='checkpoint':print(json.dumps(checkpoint(design,a.stage,a.out),indent=2))
    else:
        pending=json.loads(Path(a.checkpoint).read_text())
        digest=hashlib.sha256(json.dumps(design,sort_keys=True).encode()).hexdigest()
        if pending.get('state')!='awaiting-user' or pending.get('stage')!='tasks' or pending.get('designSha256')!=digest:raise ValueError('Checkpoint is not pending for this exact task design.')
        edits=json.loads(Path(a.edits).read_text());edited,removed=apply_task_edits(design,edits)
        with Path(a.out).open('x') as f:json.dump(edited,f,indent=2)
        print(json.dumps({'state':'rebuild-components','removedTaskIds':removed,'out':a.out,'finalValidation':'not-run: downstream stages must be reauthored'},indent=2))


if __name__=='__main__':main()
