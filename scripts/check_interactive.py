#!/usr/bin/env python3
"""Exercise a persisted task-removal checkpoint and rebuild, without a real user run."""
from pathlib import Path
import argparse,copy,hashlib,importlib.util,json
ROOT=Path(__file__).resolve().parents[1];SD=ROOT/'skills/agent-design-studio/scripts'
def module(name):
 s=importlib.util.spec_from_file_location(name,SD/(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def run(out):
 D=module('design_io');S=module('design_session');out=Path(out);out.mkdir(parents=True,exist_ok=True)
 original=D.load_json(ROOT/'evals/seeded-defects/v2/passing-v1.1.json')
 after=copy.deepcopy(original);after['runOptions']={'mode':'standard','interactive':True}
 before=copy.deepcopy(after)
 t=copy.deepcopy(before['stages']['tasks']['items'][1]);t['id']='T99';t['title']='Optional internal audit note';t['data'].update(parentId='T0',risk='low')
 before['stages']['tasks']['items'].append(t)
 c=copy.deepcopy(before['stages']['components']['items'][0]);c['id']='C99';c['title']='Optional audit-note check';c['data'].update(group='Code: validation',taskIds=['T99'],inputs=['note:string!'],outputs=['checked:boolean!'],whyCode='Check a local note without external effects.')
 before['stages']['components']['items'].append(c)
 w=copy.deepcopy(before['stages']['workflow']['items'][0]);w['id']='W99';w['title']='Optional audit check';w['data'].update(componentId='C99',taskIds=['T99'],next=[],decision=False)
 wc=json.loads(w['description']);wc.update(state='OPTIONAL_AUDIT',transitions=[],terminalDisposition='Owned optional note only, no business completion.');w['description']=json.dumps(wc)
 before['stages']['workflow']['items'].append(w)
 first=before['stages']['workflow']['items'][0];first['data']['next'].append('W99');first['data']['decision']=True
 wc=json.loads(first['description']);wc['transitions'].append({'to':'W99','when':'not valid and optionalAudit','mode':'conditional'});first['description']=json.dumps(wc)
 before['stages']['components']['items'][0]['data']['outputs'].append('optionalAudit:boolean!')
 sem=before['semantics'];sem['nodes'].append({'id':'W99','kind':'other'});sem['componentEffects'].append({'componentId':'C99','effect':'none'})
 sem['modelOutputs'].append({'componentId':'C1','field':'optionalAudit','category':'other'})
 sem['transitions'].append({'from':'W1','to':'W99','when':'not valid and optionalAudit','outcome':'normal'})
 assert D.validate_design(before)['valid'],D.validate_design(before)
 (out/'before.json').write_text(json.dumps(before,indent=2)+'\n')
 edits={'removeTaskIds':['T99']};(out/'edits.json').write_text(json.dumps(edits,indent=2)+'\n')
 cp=out/'checkpoint.json'
 if cp.exists():raise ValueError('Use a fresh interactive proof folder.')
 S.checkpoint(before,'tasks',cp)
 edited,removed=S.apply_task_edits(before,edits)
 assert all(not edited['stages'][key]['items'] for key in S.ORDER[2:])
 # A scripted author rebuild from the accepted task tree, not stale graph pruning.
 for stage in S.ORDER[2:]:edited['stages'][stage]=copy.deepcopy(after['stages'][stage])
 edited['semantics']=copy.deepcopy(after['semantics'])
 assert D.validate_design(edited)['valid'],D.validate_design(edited)
 (out/'after.json').write_text(json.dumps(edited,indent=2)+'\n')
 result={'scripted':True,'beforeDesign':'before.json','afterDesign':'after.json','edits':'edits.json','checkpoint':'checkpoint.json',
         'removedTaskIds':removed,'removedComponentIds':['C99'],
         'sourceHashes':{name:hashlib.sha256((out/name).read_bytes()).hexdigest() for name in ('before.json','after.json','edits.json','checkpoint.json')},
         'notes':'Functional checkpoint test, not a claim the user selected interactive mode for a normal brief-only run.'}
 (out/'evidence.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'ok':True,'folder':str(out),'removed':removed,'validator':'pass'}));return result
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('out');run(p.parse_args().out)
