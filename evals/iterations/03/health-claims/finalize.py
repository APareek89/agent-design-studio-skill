import json,copy,hashlib
from pathlib import Path
O=Path(__file__).parent;D=json.loads((O/'design.json').read_text());s=D['stages']
r=json.loads((O/'review-round-1.json').read_text());r['round']=2;r['issues']=[{'id':'ISSUE4','severity':'major','stage':'workflow','itemId':'W6','message':'Notice transition targets W6, but semantic role is other rather than requester_notice; SEM002 fails despite actual status projection. Declare exact role.','resolved':False},{'id':'ISSUE5','severity':'major','stage':'components','itemId':'C5','message':'Owned exception terminal W11 serves T7 but its human ownership component lists only T5. Add T7 ownership to actual component responsibility and tests.','resolved':False}]
for v in r['dimensions']:
 v['score']=2 if v['id'] in ['D2','D3','D12'] else 3
 if v['id']=='D10':v['evidence']=['EV1-EV26 now have full effective inputs and immutable bytes; added service-period, remaining-cover, copay, hash and OCR cases.']
r['dimensions'][2]['evidence']=['W6 has an actual one-hour notice branch, but the missing semantic requester_notice declaration fails SEM002. W8 overlap has been fixed.'];r['dimensions'][11]['evidence']=['Export still blocked by component T7 mapping and semantic notice metadata.']
(O/'review-round-2.json').write_text(json.dumps(r,indent=2)+'\n')
next(x for x in D['semantics']['nodes'] if x['id']=='W6')['kind']='requester_notice'
c5=next(x for x in s['components']['items'] if x['id']=='C5');c5['data']['taskIds'].append('T7');c5['description']+=' Own W11 unresolved operation tickets across caller expiry and denied security outcomes without revealing medical data. For signed resolution, authenticate examiner identity/role, exact case version and immutable review event before constructing review payload; reject changed snapshot, stale or unsigned events.'
c4=next(x for x in s['components']['items'] if x['id']=='C4');c4['description']+=' Monetary inputs must be nonnegative signed-64-bit integers in one trusted currency. Reject negative/overflow values. Day count must match certified admission/discharge convention; do not use a model date. Missing accumulator version or staleness => review.'
base=json.loads(next(x for x in s['evals']['items'] if x['id']=='EV1')['data']['input']);template=next(x for x in s['evals']['items'] if x['id']=='EV5')
def newev(i,title,mutate,expected,fm,ts,cs,pol='negative'):
 inp=copy.deepcopy(base);mutate(inp)
 if i!='EV25':inp['operation']['sha256']=hashlib.sha256(json.dumps(inp['operation']['payload'],sort_keys=True,separators=(',',':')).encode()).hexdigest()
 x=copy.deepcopy(template);x.update(id=i,title=title);x['data'].update(taskIds=ts,componentIds=cs,failureModeIds=[fm],input=json.dumps(inp),expected=json.dumps(expected),passRule=json.dumps({'assertions':[f'output.{k} == {json.dumps(v)}' for k,v in expected.items()],'forbidden':['payment API calls','final denial notices'],'orderedMocks':True}));s['evals']['items'].append(x);D['semantics']['goldens'].append({'evalId':i,'actionClass':'record_recommendation','polarity':pol,'fixture':{'input':inp,'expected':expected}});next(f for f in s['fmea']['items'] if f['id']==fm)['data']['evalIds'].append(i)
def resolved(a):
 a['events']=[{'type':'ack','elapsedHours':2,'actor':'EX-1','role':'examiner','signed':True},{'type':'resolve','elapsedHours':3,'actor':'EX-1','role':'examiner','signed':True,'snapshotVersion':3,'disposition':'manual-review-required','rationale':'Possible exclusion needs insurer adjudication'}];a['operation']['payload']['status']='REVIEW_REQUIRED';a['operation']['payload']['review']=copy.deepcopy(a['events'][-1]);a['operation']['payload']['assessment']=None
newev('EV27','Reviewed rejection remains staff-facing',resolved,{'writes':1,'state':'SAVED_REVIEW_REQUIRED','reviewActor':'EX-1','finalDenialNotices':0},'FM8',['T5','T6','T7'],['C5','C7','C9'],'positive')
def correction(a):a['command']='correction';a['originalCaseId']=None;a['case']['expectedVersion']=3
newev('EV28','Correction requires original record',correction,{'writes':0,'reason':'ORIGINAL_CASE_REQUIRED','medicalReads':0},'FM7',['T1'],['C1'])
def cancel(a):
 a['command']='cancel';a['originalCaseId']='CASE-0';a['case']['expectedVersion']=3;a['events']=[{'type':'cancel','actor':'EX-1','signed':True,'snapshotVersion':3}];a['operation']['payload']['status']='CANCELLED';a['operation']['payload']['assessment']=None;a['operation']['payload']['review']=None;a['documents']=[];a['bill']=None
newev('EV29','Pre-save cancellation has a proven case record',cancel,{'writes':1,'state':'SAVED_CANCELLED','modelCalls':0,'paymentCalls':0},'FM8',['T1','T5','T6','T7'],['C1','C5','C7','C9'],'positive')
def rounding(a):
 a['policy']['version']='RV2';a['policy']['roomReduction']='proportional-linked';a['bill']={'currency':'INR','days':2,'roomMinor':1200000,'linkedMinor':3,'unlinkedMinor':0};a['operation']['payload']['assessment']['eligibleMinor']=1000003;a['operation']['payload']['assessment']['ruleVersion']='RV2';a['mocks'][1]['result']='RV2 current for service date'
newev('EV30','Half-up rounding is visible at a minor unit',rounding,{'writes':1,'eligibleMinor':1000003,'roundedLinkedMinor':3,'state':'SAVED_DRAFT'},'FM2',['T4','T6'],['C4','C7'],'positive')
newev('EV31','Negative charge cannot become a draft',lambda a:a['bill'].update(roomMinor=-1),{'writes':0,'reason':'NEGATIVE_CHARGE','authoritativeTotal':None},'FM2',['T4'],['C4'])
rel=next(x for x in s['evals']['items'] if x['id']=='EV21');ids=[x['id'] for x in s['evals']['items'] if x['data']['category']=='golden'];rel['data']['testSet']=', '.join(ids)+'; EV19 holdout and EV20 alarm drills';rel['description']='Execute every exact assertion in '+', '.join(ids)+', then EV19 heldout and EV20 alarm drills. H2 adapter, H3 deletion/privacy evidence remain launch gates. Never substitute schema validation for business execution.';rel['data']['expected']=rel['description'];rel['data']['input']='Versioned self-contained synthetic golden fixtures: '+', '.join(ids)
for m in D['milestones']:m['evalIds']=[x['id'] for x in s['evals']['items'] if set(x['data']['componentIds']) & set(m['componentIds'])]
x=s['export']['items'][0];x['data']['acceptanceCriteria'][0]='All T1-T7 leaves and C1-C9 contracts have EV1-EV31 coverage; EV21 release set explicitly names every golden.'
(O/'design.json').write_text(json.dumps(D,indent=2)+'\n')
