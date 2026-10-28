import json,copy,hashlib
from pathlib import Path
O=Path(__file__).parent;D=json.loads((O/'design.json').read_text());s=D['stages']
review={'method':'self-review','round':1,'status':'needs-work','dimensions':[],'issues':[{'id':'ISSUE1','severity':'major','stage':'workflow','itemId':'W8','message':'The fallback predicate overlaps a found record when retryCount=1. Make found precedence explicit and restrict fallback to confirmed absence/unresolved.','resolved':False},{'id':'ISSUE2','severity':'major','stage':'evals','itemId':'EV15','message':'Revocation is present at initial input instead of between initial authorization and save; initial fixture also lacks full immutable approval bytes/hash. Add actual save-time revocation and immutable-byte fixtures plus date/remaining-benefit boundary tests.','resolved':False},{'id':'ISSUE3','severity':'major','stage':'export','itemId':'X1','message':'Validator found type errors in workflow decision, framework alternatives, rollout AI metrics and autonomy enum. Correct types and revalidate before export.','resolved':False}],'limitations':['Self-review only; no independent agent review. Golden assertions specify future business tests and have not executed. No API or policy truth has been established.']}
evidence=['CTX1-CTX4 and T0-T7 cover bounded assist-only scope','Sources use exact brief excerpt and H1-H6 hypotheses','W8 fallback overlap needs repair','C1-C9 name typed resources and enum errors','C4 code authority and C7 fresh writer check; H3 privacy gate','H1-H6 record unverified operational facts','F1-F4 compare generic platform candidates without live claims','M1 reproduces expected USD0.02112/case and two-call bound','FM1-FM8 concrete case-specific failure controls','EV1-EV21 useful coverage but missing time-of-revocation and full-byte fixtures','R1-R4 define baseline, cluster study and assist-only end state','X1 handoff blocked on structural type failures']
for i,e in enumerate(evidence,1):review['dimensions'].append({'id':'D'+str(i),'score':2 if i in [3,10,12] else 3,'evidence':[e]})
(O/'review-round-1.json').write_text(json.dumps(review,indent=2)+'\n')
for x in s['workflow']['items']:x['data']['decision']=len(x['data']['next'])>1
for x in s['framework']['items']:x['data']['alternatives']=[x['data']['alternatives']]
for x in s['rollout']['items']:x['data']['aiMetrics']=[x['data']['aiMetrics']]
for x,l in zip(D['presentation']['autonomy'],['acts alone','suggests','acts alone','human decides','human decides']):x['level']=l
w8=next(x for x in s['workflow']['items'] if x['id']=='W8');v=json.loads(w8['description']);old=v['transitions'][-1]['when'];new='reconcileResult=unresolved or (reconcileResult=confirmed_absent and (retryCount=1 or freshAuthority=false or cancellation=true))';v['transitions'][-1]['when']=new;w8['description']=json.dumps(v)
for x in D['semantics']['transitions']:
 if x['from']=='W8' and x['when']==old:x['when']=new
c4=next(x for x in s['components']['items'] if x['id']=='C4');c4['description']+=' First release supports only explicit zero deductible and zero copay; nonzero values, mixed currency or service dates spanning rule periods route review. Apply min(calculated eligible, fresh remainingCoverMinor); remaining cover comes from an authoritative accumulator version, not document text. This recommendation reserves no benefits; fresh recheck by insurer is mandatory before settlement. Exclude clinical necessity, fraud and medically coded exclusion judgement from automated calculation; route these to staff.'
c7=next(x for x in s['components']['items'] if x['id']=='C7');c7['description']+=' Internal serialization is UTF-8 JSON with sorted keys, compact separators and no nonfinite numbers; SHA256 stored bytes, not a reserialized model object. Store immutable bytes before authorizing the save. Any payload change requires new operation authorization. Ledger business identity is tenant/claim/submissionRevision. Nonmedical security telemetry remains separate from claim record writes.'
# Complete immutable operation payload in every existing write fixture; no external fixture inheritance.
for x in s['evals']['items']:
 if x['data']['category']!='golden':continue
 inp=json.loads(x['data']['input']);inp['case']['tenant']='INS-A';inp['case']['member']='MEM-1';inp['case']['submissionRevision']=3
 payload={'tenant':'INS-A','member':'MEM-1','claim':'HC-1','expectedVersion':3,'operationId':'OP-1','submissionRevision':3,'status':'DRAFT','assessment':{'currency':'INR','eligibleMinor':3000000,'ruleVersion':'RV1','accumulatorVersion':7,'sourceDocumentHash':'DOC1'},'review':None,'createdAt':'2026-06-03T10:00:00Z'}
 raw=json.dumps(payload,sort_keys=True,separators=(',',':'));inp['operation']={'payload':payload,'serialization':'json-sorted-compact-utf8-v1','sha256':hashlib.sha256(raw.encode()).hexdigest(),'authorizedBy':'service-role:case-draft-writer'}
 # Inputs describe initial proposal. No external model money is bound to the command; engine recomputes it.
 if x['id']=='EV4':payload['assessment']['eligibleMinor']=2700000;payload['assessment']['ruleVersion']='RV2';inp['policy']['version']='RV2';inp['mocks'][1]['result']='RV2 current for service date'
 if x['id']=='EV15':inp['principal']['active']=True;inp['events']=[{'type':'revoke-role','between':'initial authorization and case.write','role':'examiner','newActive':False}];inp['mocks'][2]['result']='AUTH_REVOKED at writer fresh check'
 if x['id']=='EV12':inp['previouslyAuthorized']['operation']=copy.deepcopy(inp['operation'])
 if x['id']=='EV13':inp['previouslyAuthorized']['operation']=copy.deepcopy(inp['operation'])
 inp['operation']['sha256']=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()
 if 'previouslyAuthorized' in inp:inp['previouslyAuthorized']['operation']=copy.deepcopy(inp['operation'])
 x['data']['input']=json.dumps(inp)
 for g in D['semantics']['goldens']:
  if g['evalId']==x['id']:g['fixture']['input']=inp
# Add isolated boundary fixtures from the explicit full positive fixture.
base=json.loads(next(x for x in s['evals']['items'] if x['id']=='EV1')['data']['input'])
baseev=next(x for x in s['evals']['items'] if x['id']=='EV5')
def newev(i,title,mutate,expected,fm,ts,cs,pol='negative'):
 inp=copy.deepcopy(base);mutate(inp);x=copy.deepcopy(baseev);x.update(id=i,title=title);x['data'].update(taskIds=ts,componentIds=cs,failureModeIds=[fm],input=json.dumps(inp),expected=json.dumps(expected),passRule=json.dumps({'assertions':[f'output.{k} == {json.dumps(v)}' for k,v in expected.items()],'forbidden':['payment API calls','final denial notices'],'orderedMocks':True}));s['evals']['items'].append(x);D['semantics']['goldens'].append({'evalId':i,'actionClass':'record_recommendation','polarity':pol,'fixture':{'input':inp,'expected':expected}});next(f for f in s['fmea']['items'] if f['id']==fm)['data']['evalIds'].append(i)
newev('EV22','Policy boundary uses service date, not current date',lambda a:a['case'].update(serviceDates=['2025-12-31','2026-01-01']),{'writes':0,'reason':'SERVICE_PERIOD_SPLIT_UNSUPPORTED','authoritativeTotal':None},'FM2',['T4'],['C4'])
newev('EV23','Fresh remaining cover caps the recommendation',lambda a:a['policy'].update(remainingCoverMinor=2500000,accumulatorVersion=7),{'writes':1,'eligibleMinor':2500000,'state':'SAVED_DRAFT'},'FM2',['T4','T6'],['C4','C7'],'positive')
newev('EV24','Nonzero copay stays with staff',lambda a:a['policy'].update(copayBps=1000),{'writes':0,'reason':'COPAY_RULE_OUT_OF_RELEASE_SCOPE','authoritativeTotal':None},'FM2',['T4'],['C4'])
newev('EV25','Changed payload cannot reuse authorization',lambda a:a['operation']['payload']['assessment'].update(eligibleMinor=9999999),{'writes':0,'reason':'IMMUTABLE_PAYLOAD_HASH_MISMATCH'},'FM7',['T6'],['C7'])
newev('EV26','Unverified OCR has no authoritative total',lambda a:a['documents'][0].update(ocrVerified=False),{'writes':0,'reason':'OCR_UNVERIFIED','authoritativeTotal':None},'FM3',['T2','T3'],['C2','C3'])
# Some positive fixtures intentionally change inputs that trigger recomputation, then bind the derived payload.
a=next(x for x in s['evals']['items'] if x['id']=='EV23');inp=json.loads(a['data']['input']);inp['operation']['payload']['assessment']['eligibleMinor']=2500000;inp['operation']['sha256']=hashlib.sha256(json.dumps(inp['operation']['payload'],sort_keys=True,separators=(',',':')).encode()).hexdigest();a['data']['input']=json.dumps(inp);next(g for g in D['semantics']['goldens'] if g['evalId']=='EV23')['fixture']['input']=inp
# Make newly added goldens part of the actual release suite, without broadening unrelated risk links.
rel=next(x for x in s['evals']['items'] if x['id']=='EV21');rel['description']='Execute every exact assertion in EV1-EV18 and EV22-EV26, then EV19 heldout and EV20 alarm drills; H2 adapter, H3 deletion/privacy evidence remain launch gates. Never substitute schema validation for business execution.';rel['data']['expected']=rel['description'];rel['data']['testSet']='EV1-EV18 and EV22-EV26; EV19 holdout manifest and EV20 drills'
for m in D['milestones']:m['evalIds']=[x['id'] for x in s['evals']['items'] if set(x['data']['componentIds']) & set(m['componentIds'])]
# Resolve completed repair findings in new review only. Keep prior file byte-for-byte.
(O/'design.json').write_text(json.dumps(D,indent=2)+'\n')
