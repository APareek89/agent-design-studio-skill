from pathlib import Path
import json,copy,hashlib,shutil
S=Path('/Users/macbook/Documents/agent-design-studio-skill/evals/iterations/04/health-claims');O=Path(__file__).parent
D=json.loads((S/'design.json').read_text())
for p in S.glob('review-round-*.json'):shutil.copy2(p,O/p.name)
shutil.copy2(S/'review.json',O/'review-round-04-independent.json')
st=D['stages'];components={x['id']:x for x in st['components']['items']}
# The new source is an explicit insurer read, not a field reverse-copied from expected amounts.
h=next(x for x in D['assumptions'] if x['id']=='H2');old=h['statement'];h['statement']+=' This proposed integration also exposes a tenant/member/policy-bound benefit accumulator snapshot and a same-request current-version receipt; its real support and currency/freshness semantics require insurer verification.';h['validation']+=' Verify accumulator GET response fields, current-version receipt, source authentication, version-race behavior and writer freshness check with insurer.'
for stage in st.values():
 for item in stage['items']:
  for source in item['sources']:
   if source['type']=='hypothesis' and source['file']=='H2':source['passage']=h['statement']
c2=components['C2'];c2['data']['outputs'].append('accumulatorSnapshot: required for calculation {tenant:string,member:string,policyId:string,currency:string,remainingCoverMinor:int64,accumulatorVersion:int64,asOf:string,readRequestId:string,versionReceipt:{requestId:string,currentVersion:int64,checkedAt:string}}; may be absent only on owned review/cancel path')
c2['description']+=' Proposed H2 accumulator source: authenticated GET /benefit-accumulators/{policyId}/members/{member} under tenant scope, paired with current-version receipt in the same read request. Fields match accumulatorSnapshot output. This read never reserves or spends benefits. Both are insurer API source facts, never model/policy-document values. Missing/failed source data uses existing unavailable path; a returned incomplete/stale snapshot reaches C4 review. Ordinary 10s/read retry bound applies.'
c4=components['C4'];c4['data']['inputs'].append('accumulatorSnapshot: insurer source snapshot from C2 with exact tenant/member/policyId/currency, nonnegative remainingCoverMinor, required accumulatorVersion and same-request versionReceipt')
c4['description']+=' Accumulator guard contract: require C2 source response tenant/member/policyId/currency equals authenticated case, accumulatorVersion is a positive integer, receipt.requestId equals readRequestId, and receipt.currentVersion equals accumulatorVersion. Receipt.checkedAt must be at/after asOf and at/before calculation server time. Missing accumulatorVersion => ACCUMULATOR_VERSION_MISSING; mismatched receipt version => ACCUMULATOR_SNAPSHOT_STALE; mismatched scope/currency or absent receipt => review. Only source.remainingCoverMinor is used for min(cap); policy documents and operation.assessment are never source inputs. Assessment carries the validated source version; operation creation follows calculation, not the reverse.'
c7=components['C7'];c7['description']+=' For DRAFT only, perform a fresh accumulator current-version query at save and require equality with assessment.accumulatorVersion; version change rejects with ACCUMULATOR_SNAPSHOT_STALE and forces new calculation/authorization. Bind approval to exact stored payload bytes/hash plus tenant/member/claim, operationId, expectedVersion and rule/accumulator versions. Two competitors need two distinct complete authorizations; an OP-1 authorization cannot authorize OP-A or OP-B. Review/cancel payloads have assessment:null and no monetary authorization.'
for wi,detail in [('W2','bindings.accumulatorSnapshot = C2.accumulatorSnapshot, produced by authenticated insurer source GET and same-request version receipt; missing source read uses unavailable outcome.'),('W4','bindings.accumulatorSnapshot = C2.accumulatorSnapshot; calcStatus review on missing version, stale receipt or scope mismatch. C4 server time is authoritative; no model field supplies source freshness.')]:
 w=next(x for x in st['workflow']['items'] if x['id']==wi);data=json.loads(w['description']);data['guardBindings']+=' '+detail;w['description']=json.dumps(data)

def digest(payload):return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
def authorize(op):
 p=op['payload'];op['sha256']=digest(p);op['authorization']={'authorizationId':'AUTH-'+p['operationId'],'issuer':'insurer-case-authorization-service','principal':op.get('authorizedBy','service-role:case-draft-writer'),'tenant':p['tenant'],'member':p['member'],'claim':p['claim'],'operationId':p['operationId'],'expectedVersion':p['expectedVersion'],'payloadSha256':op['sha256'],'ruleVersion':(p.get('assessment') or {}).get('ruleVersion'),'accumulatorVersion':(p.get('assessment') or {}).get('accumulatorVersion'),'decision':'allow-case-record-only','verifiedSignatureBy':'synthetic-insurer-verifier'};return op

def accumulator(amount):return {'tenant':'INS-A','member':'MEM-1','policyId':'POL-1','currency':'INR','remainingCoverMinor':amount,'accumulatorVersion':7,'asOf':'2026-06-03T09:59:55Z','readRequestId':'ACC-READ-1','versionReceipt':{'requestId':'ACC-READ-1','currentVersion':7,'checkedAt':'2026-06-03T10:00:00Z'}}
for ev in st['evals']['items']:
 if ev['data']['category']!='golden':continue
 a=json.loads(ev['data']['input']);eid=ev['id'];a['case']['policyId']='POL-1';a['policy']['policyId']='POL-1'
 # Source amount comes from preexisting test's insurer input, not the output operation.
 remaining=a['policy'].pop('remainingCoverMinor',10000000);a['policy'].pop('accumulatorVersion',None)
 a['accumulatorSnapshot']=accumulator(remaining);a['clock']={'calculationAt':'2026-06-03T10:00:00Z','writerCheckAt':'2026-06-03T10:00:00Z'}
 accmock={'service':'benefit-accumulator.get','request':{'tenant':'INS-A','member':'MEM-1','policyId':'POL-1','readRequestId':'ACC-READ-1'},'result':copy.deepcopy(a['accumulatorSnapshot'])}
 # Ordered source mock precedes any writer result; documents/authorization guards can stop before consuming it.
 idx=next((i for i,x in enumerate(a['mocks']) if 'case.write' in x['service']),len(a['mocks']));a['mocks'].insert(idx,accmock)
 a['mocks'].insert(idx+1,{'service':'benefit-accumulator.current-version-at-save','request':{'tenant':'INS-A','member':'MEM-1','policyId':'POL-1'},'result':{'currentVersion':7,'checkedAt':'2026-06-03T10:00:00Z'}})
 # Materialize every normal operation's approval. EV25 intentionally mutates after the valid authorization.
 op=a['operation'];bad=None
 if eid=='EV25':bad=op['payload']['assessment']['eligibleMinor'];op['payload']['assessment']['eligibleMinor']=3000000
 if eid=='EV16':op['payload']['status']='REVIEW_REQUIRED';op['payload']['assessment']=None;op['payload']['review']={'type':'overdue','owner':'Claims operations lead','elapsedHours':24,'disposition':'manual-review-required','snapshotVersion':3}
 authorize(op)
 if eid=='EV25':op['payload']['assessment']['eligibleMinor']=bad
 # Earlier authorization and stored bytes must exactly match the operation on recovery paths.
 if 'previouslyAuthorized' in a:a['previouslyAuthorized']['operation']=copy.deepcopy(op)
 if eid=='EV10':
  template=copy.deepcopy(op);a.pop('operation');a['case'].pop('operationId',None)
  a['operations']=[]
  for oid in ['OP-A','OP-B']:
   own=copy.deepcopy(template);own['payload']['operationId']=oid;authorize(own)
   a['operations'].append({'operationId':oid,'expectedVersion':3,'operation':own,'request':{'method':'PUT','tenant':'INS-A','claim':'HC-1','path':'/staff-cases/HC-1/operations/'+oid,'expectedVersion':3,'authorizationId':own['authorization']['authorizationId']}})
  a['concurrencySchedule']=['Both operations finish C4 from authoritative accumulator version 7 and claim version 3','Both independently store payload bytes and pass hash, source, resource and approval guards','OP-A executes CAS from version 3 to 4 and commits CASE-1','OP-B attempts same expectedVersion 3 after OP-A commit; returns CAS_CONFLICT without overwrite']
  a['mocks']=[{'service':'benefit-accumulator.get','result':copy.deepcopy(a['accumulatorSnapshot'])},{'service':'authorization.verify OP-A','result':copy.deepcopy(a['operations'][0]['operation']['authorization'])},{'service':'authorization.verify OP-B','result':copy.deepcopy(a['operations'][1]['operation']['authorization'])},{'service':'case.write OP-A','request':copy.deepcopy(a['operations'][0]['request']),'result':{'saveResult':'committed','caseId':'CASE-1','version':4,'operationId':'OP-A','storedPayloadSha256':a['operations'][0]['operation']['sha256']}},{'service':'case.write OP-B','request':copy.deepcopy(a['operations'][1]['request']),'result':{'saveResult':'rejected','reason':'CAS_CONFLICT','currentVersion':4}},{'service':'operation.read OP-A','result':{'caseId':'CASE-1','version':4,'operationId':'OP-A','storedPayload':copy.deepcopy(a['operations'][0]['operation']['payload']),'storedPayloadSha256':a['operations'][0]['operation']['sha256']}}]
  expected=json.loads(ev['data']['expected']);expected.update(winnerOperationId='OP-A',loserReason='CAS_CONFLICT',winnerPayloadSha256=a['operations'][0]['operation']['sha256'],overwrites=0)
  ev['data']['expected']=json.dumps(expected)
  rule=json.loads(ev['data']['passRule']);rule['equals'].update(expected);rule['assertions'] += [f'output.{k} == {json.dumps(v)}' for k,v in expected.items() if k in ['winnerOperationId','loserReason','winnerPayloadSha256','overwrites']];rule['fixturePreconditions']=['For each competitor: recompute sha256(payload) == operation.sha256 == authorization.payloadSha256','request path operationId == operationId == payload.operationId == authorization.operationId','Every competitor authorization binds its exact tenant/member/claim/expectedVersion and source versions'];ev['data']['passRule']=json.dumps(rule)
 ev['data']['input']=json.dumps(a)
 # Semantic fixtures remain the actual exact effective fixtures; strict write equals/proof metadata is retained unchanged.
 g=next(g for g in D['semantics']['goldens'] if g['evalId']==eid);g['fixture']={'input':a,'expected':json.loads(ev['data']['expected'])}
# Two isolated source failures retain an otherwise valid operation and all other input guards.
base=next(x for x in st['evals']['items'] if x['id']=='EV1')
for eid,title,mutate,reason in [('EV32','Missing authoritative accumulator version withholds total',lambda a:a['accumulatorSnapshot'].pop('accumulatorVersion'),'ACCUMULATOR_VERSION_MISSING'),('EV33','Stale authoritative accumulator version withholds total',lambda a:a['accumulatorSnapshot']['versionReceipt'].update(currentVersion=8),'ACCUMULATOR_SNAPSHOT_STALE')]:
 ev=copy.deepcopy(base);ev.update(id=eid,title=title);a=json.loads(base['data']['input']);mutate(a)
 for m in a['mocks']:
  if m['service']=='benefit-accumulator.get':m['result']=copy.deepcopy(a['accumulatorSnapshot'])
 ex={'writes':0,'reason':reason,'state':'REVIEW_REQUIRED','authoritativeTotal':None};ev['data'].update(input=json.dumps(a),expected=json.dumps(ex),taskIds=['T4','T6'],componentIds=['C2','C4','C7'],failureModeIds=['FM2'],passRule=json.dumps({'equals':ex,'assertions':['output.writes == 0','output.authoritativeTotal is null','no case.write invocation','operation.assessment.accumulatorVersion does not satisfy a missing source field'],'forbidden':['payment API calls','final denial notices'],'orderedMocks':True}));st['evals']['items'].append(ev);D['semantics']['goldens'].append({'evalId':eid,'actionClass':'record_recommendation','polarity':'negative','fixture':{'input':a,'expected':ex}});next(f for f in st['fmea']['items'] if f['id']=='FM2')['data']['evalIds'].append(eid)
fm=next(f for f in st['fmea']['items'] if f['id']=='FM2');fm['data']['control']+=' Require C2 authoritative accumulator snapshot with same-request version receipt; never infer source state from an output payload.';fm['data']['action']+=' Rules owner: EV32/EV33 prove missing/stale accumulator guards before launch.'
release=next(x for x in st['evals']['items'] if x['id']=='EV21');gids=[x['id'] for x in st['evals']['items'] if x['data']['category']=='golden'];release['data']['testSet']=', '.join(gids)+'; EV19 holdout and EV20 alarm drills';release['data']['input']='Versioned complete golden fixtures: '+', '.join(gids);release['description']='Execute exact assertions for '+', '.join(gids)+' plus EV19/EV20. Verify each complete positive precondition including authoritative accumulator and independent concurrency authorizations before exercising a single failure. H2/H3 integration/privacy evidence still blocks launch.';release['data']['expected']=release['description']
for milestone in D['milestones']:milestone['evalIds']=[x['id'] for x in st['evals']['items'] if set(x['data']['componentIds']) & set(milestone['componentIds'])]
x=st['export']['items'][0];x['data']['buildInstructions']+=' Preserve C2->C4 authoritative accumulator provenance and request/version receipt. Run EV32/EV33 source guards. EV10 requires two independently materialized byte/hash/authorization-bound operations before the CAS race. Never use operation output assessment as input evidence.'
(O/'design.json').write_text(json.dumps(D,indent=2)+'\n')
# Mechanical fixture audit checks our repair invariants only; it does not execute a business harness.
checks=[]
for ev in st['evals']['items']:
 if ev['data']['category']!='golden':continue
 a=json.loads(ev['data']['input']);ops=[q['operation'] for q in a['operations']] if ev['id']=='EV10' else [a['operation']]
 for op in ops:
  match=digest(op['payload'])==op['sha256'];assert match == (ev['id']!='EV25'),ev['id']
  au=op['authorization'];assert au['payloadSha256']==op['sha256'];assert au['operationId']==op['payload']['operationId'];assert au['expectedVersion']==op['payload']['expectedVersion']
 if ev['id'] not in ['EV32','EV33']:assert a['accumulatorSnapshot']['accumulatorVersion']==a['accumulatorSnapshot']['versionReceipt']['currentVersion']
 checks.append({'evalId':ev['id'],'payloadHash': 'intentional-mismatch' if ev['id']=='EV25' else 'coherent','sourceVersion': 'intentional-negative' if ev['id'] in ['EV32','EV33'] else 'coherent'})
(O/'fixture-repair-checks.json').write_text(json.dumps({'status':'pass','scope':'Local JSON/hash/provenance consistency audit; no business assertions executed','checks':checks},indent=2)+'\n')
