"""Semantic contract tests use full valid design artifacts and graph mutations."""
import copy
import hashlib
import json
from pathlib import Path
import unittest
from test_design_io import make_design, design_io

ROOT = Path(__file__).resolve().parents[1]
SEEDS = ROOT / 'evals/seeded-defects/v2'


def make_semantic_design():
    d = make_design()
    d['schemaVersion']='1.1'
    c=d['stages']['components']['items'][0]
    c['data']['outputs']=['recommendation:string!', 'amount:number!', 'customerId:string!', 'date:string!']
    writer=copy.deepcopy(c); writer['id']='C2'; writer['title']='Persist refund'
    writer['data'].update(group='Code: tools', inputs=['customerId:string!','amount:number!','date:string!'], outputs=['recordId:string!'], whyCode='Deterministic write contract')
    d['stages']['components']['items'].append(writer)
    guard=copy.deepcopy(writer);guard['id']='C3';guard['title']='Verify committed record proof'
    guard['data'].update(group='Code: validation',inputs=['recordId:string!'],outputs=['recordVerified:boolean!'],whyCode='Reject missing or empty trusted record proof before confirming completion.')
    d['stages']['components']['items'].append(guard)
    base=d['stages']['workflow']['items'][0]
    specs=[('W1','validation',[('W2','valid','normal')]),('W2','write',[('W3','committed','normal'),('W5','timeout','TIMEOUT'),('W5','unknown','unknown_commit')]),('W3','human_wait',[('W4','notice','notice'),('W6','approved','normal')]),('W4','requester_notice',[('W6','delivered','normal')]),('W5','reconcile',[('W2','absent','repeat'),('W6','found','normal')]),('W6','record_id_guard',[('W7','record exists','normal')]),('W7','completion',[])]
    nodes=[]; semantic=[]; edges=[]
    for ident,kind,transitions in specs:
        w=copy.deepcopy(base); w['id']=ident; w['title']=kind
        w['data'].update(componentId='C2' if kind=='write' else 'C3' if kind=='record_id_guard' else 'C1', next=list(dict.fromkeys(x[0] for x in transitions)), decision=len(set(x[0] for x in transitions))>1)
        contract=json.loads(w['description']); contract['state']=kind.upper(); contract['transitions']=[{'to':to,'when':when,'mode':'conditional'} for to,when,outcome in transitions]
        if kind=='record_id_guard':contract['bindings']={'recordId':{'sourceComponentId':'C2','sourceField':'recordId'}}
        w['description']=json.dumps(contract); nodes.append(w)
        n={'id':ident,'kind':kind}
        if kind=='write':
            n.update(actionClass='refund',bindings=[{'field':f,'category':cat,'source':'trusted'} for f,cat in [('customerId','identity'),('amount','money'),('date','date')]])
        if kind=='human_wait': n['waitHours']=48
        if kind=='record_id_guard':n['recordProof']={'field':'recordId','sourceComponentId':'C2','sourceField':'recordId'}
        semantic.append(n)
        edges.extend({'from':ident,'to':to,'when':when,'outcome':outcome} for to,when,outcome in transitions)
    d['stages']['workflow']['items']=nodes
    ev=d['stages']['evals']['items'][0]
    ev['data']['input']=json.dumps({'customerId':'CUS1','amount':100,'date':'2026-10-28'})
    ev['data']['expected']=json.dumps({'writes':0,'disposition':'REJECTED'})
    ev['data']['componentIds']=['C1','C2'];ev['data']['passRule']=json.dumps({'equals':{'writes':0,'disposition':'REJECTED'}})
    pos=copy.deepcopy(ev); pos['id']='EV5'; pos['data']['expected']=json.dumps({'writes':1,'recordId':'REF1'})
    pos['data']['passRule']=json.dumps({'equals':{'writes':1,'recordId':'REF1'}})
    d['stages']['evals']['items'].append(pos)
    d['stages']['fmea']['items'][0]['data']['evalIds'].append('EV5')
    d['semantics']={'version':'1.1','entrypoints':['W1'],'nodes':semantic,'transitions':edges,'componentEffects':[{'componentId':'C1','effect':'none'},{'componentId':'C2','effect':'write'},{'componentId':'C3','effect':'none'}], 'modelOutputs':[{'componentId':'C1','field':f,'category':cat} for f,cat in [('recommendation','other'),('amount','money'),('customerId','identity'),('date','date')]],'writeActions':[{'actionClass':'refund','nodeIds':['W2']}], 'goldens':[{'evalId':e['id'],'actionClass':'refund','polarity':polarity,'fixture':{'input':json.loads(e['data']['input']),'expected':json.loads(e['data']['expected'])}} for e,polarity in [(ev,'negative'),(pos,'positive')]]}
    return d


def edge(d, source, target, when='bypass', outcome='normal'):
    w=next(w for w in d['stages']['workflow']['items'] if w['id']==source)
    w['data']['next']=list(dict.fromkeys(w['data']['next']+[target])); w['data']['decision']=len(w['data']['next'])>1
    c=json.loads(w['description']); c['transitions'].append({'to':target,'when':when,'mode':'conditional'}); w['description']=json.dumps(c)
    d['semantics']['transitions'].append({'from':source,'to':target,'when':when,'outcome':outcome})


def mutate(d, n):
    s=d['semantics']
    if n==1: s['nodes'][0]['kind']='other'
    if n==2:
        s['transitions'][4]['outcome']='normal'  # W3 notice edge
    if n==3:
        s['goldens']=[g for g in s['goldens'] if g['polarity']!='positive']
        d['stages']['evals']['items']=[e for e in d['stages']['evals']['items'] if e['id']!='EV5']
        d['stages']['fmea']['items'][0]['data']['evalIds'].remove('EV5')
    if n==4:
        g=s['goldens'][0]; g['base']={'id':'shared-refund'}; g.pop('fixture')
    if n==5: s['nodes'][1]['bindings'][1].update(source='llm',sourceComponentId='C1',sourceField='amount')
    if n==6: edge(d,'W2','W2','uncertain repeat','TIMEOUT')
    if n==7: edge(d,'W3','W7','unguarded completion')
    return d


class SemanticTests(unittest.TestCase):
    def rules(self,d): return {e.get('ruleId') for e in design_io.validate_design(d)['errors'] if e.get('ruleId')}
    def test_valid_full_v11_and_legacy(self):
        for d in (make_design(),make_semantic_design()):
            r=design_io.validate_design(d); self.assertTrue(r['valid'],r['errors'])
        r=design_io.validate_design(make_design()); self.assertEqual(r['semanticCoverage'],'unverified'); self.assertIn('unverified',str(r['warnings']))
    def test_seven_single_defect_contracts(self):
        for n in range(1,8):
            with self.subTest(rule=n): self.assertEqual(self.rules(mutate(make_semantic_design(),n)),{'SEM00'+str(n)})
    def test_validation_and_record_guard_bypass(self):
        d=make_semantic_design(); d['semantics']['nodes'][0]['kind']='start'
        edge(d,'W1','W2'); self.assertIn('SEM001',self.rules(d))
        d=make_semantic_design(); edge(d,'W4','W7'); self.assertIn('SEM007',self.rules(d))
    def test_metadata_cannot_remove_paths(self):
        d=make_semantic_design(); edge(d,'W3','W7'); d['semantics']['transitions'].pop()
        self.assertTrue({'SEM000','SEM007'}<=self.rules(d))
    def test_missing_incomplete_and_shadow_declarations_fail(self):
        for field in ('semantics','nodes','componentEffects','modelOutputs','writeActions'):
            d=make_semantic_design()
            if field=='semantics': del d[field]
            else: d['semantics'][field]=[]
            self.assertIn('SEM000',self.rules(d))
        d=make_semantic_design(); d['semantics']['nodes'][1]['kind']='other'; self.assertIn('SEM000',self.rules(d))
    def test_llm_identity_and_disguised_trusted_source(self):
        for source in ('llm','trusted'):
            d=make_semantic_design(); d['semantics']['nodes'][1]['bindings'][0].update(source=source,sourceComponentId='C1',sourceField='customerId')
            self.assertIn('SEM005',self.rules(d))
    def test_fixture_must_match_actual_eval(self):
        d=make_semantic_design(); d['semantics']['goldens'][0]['fixture']['input']['customerId']='FAKE'
        self.assertIn('SEM004',self.rules(d))
    def test_guard_on_one_branch_cannot_mask_bypass(self):
        d=make_semantic_design()
        start=copy.deepcopy(d['stages']['workflow']['items'][0]); start['id']='W0'
        c=json.loads(start['description']); c['transitions']=[]
        start['description']=json.dumps(c); start['data']['next']=[]
        d['stages']['workflow']['items'].insert(0,start)
        d['semantics']['nodes'].append({'id':'W0','kind':'start'})
        d['semantics']['entrypoints']=['W0']
        edge(d,'W0','W1','validated route'); edge(d,'W0','W2','bypass route')
        self.assertEqual(self.rules(d),{'SEM001'})
    def test_reconcile_branch_cannot_mask_direct_repeat(self):
        d=mutate(make_semantic_design(),6)
        self.assertEqual(self.rules(d),{'SEM006'})
    def test_malformed_metadata_reports_diagnostics(self):
        mutations=[lambda s:s['nodes'][0].update(kind=[]), lambda s:s['transitions'][0].update(to={}), lambda s:s['goldens'][0].update(evalId={}), lambda s:s.update(entrypoints=[{}]), lambda s:s['nodes'][1]['bindings'][0].update(sourceComponentId=[])]
        for mutate_metadata in mutations:
            d=make_semantic_design(); mutate_metadata(d['semantics'])
            self.assertIn('SEM000',self.rules(d))
    def test_versioned_inheritance_and_llm_date(self):
        d=make_semantic_design(); g=d['semantics']['goldens'][0]; fixture=g.pop('fixture')
        g.update(base={'id':'refund','version':'1.0'},mergeRule='deep-merge-v1',overrides={},resolvedFixture=fixture)
        self.assertTrue(design_io.validate_design(d)['valid'])
        d['semantics']['nodes'][1]['bindings'][2].update(source='llm',sourceComponentId='C1',sourceField='date')
        self.assertEqual(self.rules(d),{'SEM005'})
    def test_positive_and_negative_writes_assertions_are_typed_and_consistent(self):
        for index,bad in ((1,0),(1,True),(1,'1'),(1,None),(0,1),(0,False)):
            with self.subTest(index=index,assertion=bad):
                d=make_semantic_design();g=d['semantics']['goldens'][index]
                e=next(e for e in d['stages']['evals']['items'] if e['id']==g['evalId'])
                e['data']['passRule']=json.dumps({'equals':{'writes':bad}})
                self.assertEqual(self.rules(d),{'SEM003'})
    def test_write_coverage_requires_the_action_writer_component(self):
        for index in (0,1):
            d=make_semantic_design();g=d['semantics']['goldens'][index]
            e=next(e for e in d['stages']['evals']['items'] if e['id']==g['evalId'])
            e['data']['componentIds']=['C1']
            self.assertEqual(self.rules(d),{'SEM003'})
    def test_supplemental_math_golden_cannot_replace_positive_writer_case(self):
        d=make_semantic_design();d['semantics']['goldens'][1]['actionClass']=''
        self.assertEqual(self.rules(d),{'SEM003'})
        # A supplementary read-only calculation remains legal alongside both full write cases.
        base=copy.deepcopy(d['stages']['evals']['items'][0]);base['id']='EV6'
        base['data'].update(componentIds=['C1'],input=json.dumps({'a':2,'b':3}),expected=json.dumps({'sum':5}),passRule=json.dumps({'equals':{'sum':5}}))
        d['semantics']['goldens'][1]['actionClass']='refund'
        d['stages']['evals']['items'].append(base)
        d['semantics']['goldens'].append({'evalId':'EV6','actionClass':'','polarity':'positive','fixture':{'input':{'a':2,'b':3},'expected':{'sum':5}}})
        d['stages']['fmea']['items'][0]['data']['evalIds'].append('EV6')
        self.assertTrue(design_io.validate_design(d)['valid'])
    def test_vacuous_llm_or_untyped_record_guard_is_rejected(self):
        for defect in ('missing_proof','llm_guard','missing_input','optional_input','missing_source_output','missing_binding','wrong_binding','llm_source'):
            with self.subTest(defect=defect):
                d=make_semantic_design();g=d['semantics']['nodes'][5]
                c=d['stages']['components']['items'][2];w=d['stages']['workflow']['items'][5]
                if defect=='missing_proof':g.pop('recordProof')
                if defect=='llm_guard':w['data']['componentId']='C1'
                if defect=='missing_input':c['data']['inputs']=['requestId:string!']
                if defect=='optional_input':c['data']['inputs']=['recordId:string']
                if defect=='missing_source_output':d['stages']['components']['items'][1]['data']['outputs']=['result:object!']
                if defect in ('missing_binding','wrong_binding'):
                    contract=json.loads(w['description']);contract['bindings']={} if defect=='missing_binding' else {'recordId':{'sourceComponentId':'C1','sourceField':'customerId'}};w['description']=json.dumps(contract)
                if defect=='llm_source':g['recordProof']['sourceComponentId']='C1'
                self.assertIn('SEM007',self.rules(d))
    def test_record_guard_accepts_explicit_nested_and_conditional_string_projection(self):
        d=make_semantic_design();p=d['semantics']['nodes'][5]['recordProof']
        p.update(field='receipt.recordId',sourceField='result.recordId')
        d['stages']['components']['items'][2]['data']['inputs']=['receipt.recordId:string!']
        d['stages']['components']['items'][1]['data']['outputs']=['result.recordId:string! on COMMITTED; absent on TIMEOUT']
        w=d['stages']['workflow']['items'][5];c=json.loads(w['description']);c['bindings']={'receipt.recordId':{'sourceComponentId':'C2','sourceField':'result.recordId'}};w['description']=json.dumps(c)
        self.assertTrue(design_io.validate_design(d)['valid'])
    def test_original_flawed_passing_seed_is_retained_as_invalid_history(self):
        original=json.loads((SEEDS.parent/'passing-v1.1.json').read_text())
        self.assertTrue({'SEM003','SEM007'}<=self.rules(original))
    def test_record_guard_accepts_writer_and_authoritative_read_alternatives(self):
        d=make_semantic_design()
        read=copy.deepcopy(d['stages']['components']['items'][1]);read['id']='C4'
        read['data'].update(inputs=['requestId:string!'],outputs=['recordId:string! on FOUND'])
        d['stages']['components']['items'].append(read)
        d['stages']['workflow']['items'][4]['data']['componentId']='C4'
        d['semantics']['componentEffects'].append({'componentId':'C4','effect':'read'})
        proofs=[{'field':'recordId','sourceComponentId':cid,'sourceField':'recordId'} for cid in ('C2','C4')]
        d['semantics']['nodes'][5]['recordProof']=proofs
        w=d['stages']['workflow']['items'][5];c=json.loads(w['description']);c['bindings']={'recordId':[{'sourceComponentId':p['sourceComponentId'],'sourceField':p['sourceField']} for p in proofs]};w['description']=json.dumps(c)
        self.assertTrue(design_io.validate_design(d)['valid'])
        # A valid alternative cannot cover for a fabricated or model-produced one.
        d['semantics']['nodes'][5]['recordProof'][1]['sourceComponentId']='C1'
        self.assertIn('SEM007',self.rules(d))
    def test_all_stored_seeds_are_full_single_rule_defects(self):
        manifest=json.loads((SEEDS/'manifest.json').read_text())
        self.assertTrue(design_io.validate_design(json.loads((SEEDS/manifest['passing']).read_text()))['valid'])
        for name,expected in manifest['provenance']['historicalSha256'].items():
            self.assertEqual(hashlib.sha256((SEEDS.parent/name).read_bytes()).hexdigest(),expected,name)
        for row in manifest['cases']:
            with self.subTest(seed=row['file']):
                d=json.loads((SEEDS/row['file']).read_text()); self.assertEqual(self.rules(d),{row['ruleId']})


if __name__=='__main__': unittest.main()
