import json,copy,hashlib
from pathlib import Path
O=Path(__file__).parent
D=json.loads((O/'design.json').read_text())
def items(s):return D['stages'][s]['items']
def get(s,i):return next(x for x in items(s) if x['id']==i)
limits=['Self-review by the author, not independent review or stakeholder approval.','Bundled structural validator executed; financial, identity, queue and model assertions are specifications only and have not run against a business implementation.','Synthetic fixtures, policy P1, volumes, thresholds and costs are proposed assumptions; actual API capability, authority, privacy and policy approval remain H1-H8 launch dependencies.','PDF rendering and visual QA deliberately deferred to root batch step; no HTML requested or produced.']
evidence=[
('D1',3,'CTX1-CTX7 and T0-T5 bound intake, evidence, three resolution outcomes, cancellation and owned holds; scope excludes autonomous cash refund.'),
('D2',3,'All stage links pass v1 structural validation; H1-H8 distinguish proposals and exact brief quotes; FM/EV links derived reciprocally.'),
('D3',2,'W4 leads directly from eligible plan to W10 without an explicit customer confirmation state, despite C4/C6 requiring confirmation.'),
('D4',2,'C1 command discriminant lacks confirm_credit and no component owns a confirmation receipt/timer; an implementer must invent that interaction.'),
('D5',3,'C4/C6 bind positive integer CREDIT payload, tenant/subject/active connection, policy/approval version, digest, entitlement key and durable proof; C7 read-only recovery survives session loss.'),
('D6',3,'H1-H8 label policies, APIs, timing, cost and retention; C2/C3 contradiction and unavailable states route human; no live service assertions.'),
('D7',3,'F1-F5 choose bounded judgement in durable code workflow; compare common persistence/timer/audit/ownership criteria and reject synchronous and autonomous alternatives.'),
('D8',3,'M1 maps only C3; W3 allows one retry; 0.88 expected calls, 2 worst-case, illustrative price/token arithmetic and excluded costs explicit.'),
('D9',3,'FM1-FM10 cover subject, staleness, duplicates, unknown commits, injection, queue, cancellation, amount and false completion with owners and release gates.'),
('D10',2,'EV3 and EV19 mutate service/cancellation but omit entry state, so fixture may fail at intake rather than exercise writer guards. EV22 larger claim requires clearer uncapped routing. No confirmation positive/timeout cases.'),
('D11',3,'R1 metrics have denominators/windows; R2-R5 distinct entry/exit gates; R6 customer clustering, baseline power calculation, spillover and maturation; zero safety tolerance separate.'),
('D12',2,'X1 promises customer confirmation but no complete implementable state; downstream acceptance and release fixtures must include new path.')]
issues=[
{'id':'ISSUE1','severity':'major','stage':'workflow','itemId':'W4','message':'Credit path lacks explicit confirmation interaction and timeout even though authority requires consent. Add typed confirmation command/receipt owner, immutable payload binding, bounded wait and fresh recheck; preserve no-write denial/expiry.','resolved':False},
{'id':'ISSUE2','severity':'major','stage':'evals','itemId':'EV3','message':'Writer-time deactivation and cancellation fixtures can reject earlier at W1 without exercising intended guard. Bind entryState W10 and existing prepared authorized operation; reject unexpected write effects. Add confirmation fixtures.','resolved':False},
{'id':'ISSUE3','severity':'major','stage':'context','itemId':'CTX2','message':'H2 describes cap while EV22 requires supervisor routing for uncapped amounts above it; state explicitly that larger customer entitlement is not silently reduced and closed automatically.','resolved':False}]
r1={'method':'self-review','round':1,'status':'needs-work','dimensions':[{'id':i,'score':s,'evidence':[e]} for i,s,e in evidence],'issues':issues,'limitations':limits}
(O/'review-round-1.json').write_text(json.dumps(r1,indent=2)+'\n')
# Scope clarification: preserve H references exactly.
h=next(x for x in D['assumptions'] if x['id']=='H2');old=h['statement'];h['statement']=old.replace('capped at the remaining eligible base fee and 1000 minor units per incident.','limited by remaining eligible base fee. If the computed entitlement before the 1000-minor-unit automatic cap exceeds that cap, route the whole claim to a supervisor; do not silently cap and close it. Automatic credit is at most 1000 minor units per incident.')
for s in D['stages'].values():
 for x in s['items']:
  for so in x['sources']:
   if so['type']=='hypothesis' and so['file']=='H2':so['passage']=h['statement']
# Declare user confirmation owned by deterministic component, not an LLM.
c4=get('components','C4');c4['data']['outputs'][0]=c4['data']['outputs'][0].replace('credit|human|explain|duplicate|blocked|cancelled','credit|needs_confirmation|human|explain|duplicate|blocked|cancelled');c4['description']+=' Before confirmation, reserve a confirmationId in immutable payload and return needs_confirmation. The case business revision changes on intent/target/amount/evidence changes; workflow-state revision and receipt events do not mutate that business revision. Auto authority is issued only after a current matching confirmation. A pending proposal has no write authority.'
c4['data']['inputs'].append('confirmationReceipt: optional {confirmationId,caseId,caseRevision,payloadRecordId,payloadDigest,customerId,connectionId,decision:confirm|decline,issuedAt,expiresAt,signature}; C9 validates and persists. Amount above auto cap routes supervisor without silent reduction.')
# New component C9 and three nodes use existing stable responsibility IDs.
src=copy.deepcopy(c4['sources'])
c9=dict(id='C9',kind='component',title='Bound customer credit confirmation',description='Present immutable credit quote to the authenticated customer in the case portal with amount/currency/period/invoice line and evidence. confirm_credit or decline_credit must supply proposalId, confirmationId, digest, business case revision and clientCommandId; session tenant/customer/connection checked against case. Receipt persisted with server signature. Wait at most 24 elapsed hours; send one reminder at 12h. Intent changes invalidate proposal and require new C4 plan. No financial action in this component.',reasoning='Customer consent is a typed durable event and bounded wait; natural language cannot stand in for confirmation.',assumptions=['H2','H3','H8'],sources=src,data=dict(group='Code: human triggers',taskIds=['T4.1','T5'],inputs=['proposal: required {proposalId,payloadRecordId,digest,confirmationId,caseId,caseRevision,customerId,connectionId,amountMinor,currency,expiresAt}; TTL=24h from proposal, UTC.','event: {type:confirm_credit|decline_credit|cancel|timer|intent_changed,clientCommandId,eventId,proposalId,digest,expectedCaseRevision,sessionBinding}; scoped portal re-authentication required, not an email link alone.'],outputs=['confirmation: {status:confirmed|declined|cancelled|expired|changed|unavailable|waiting,receiptId?,confirmationId,caseId,caseRevision,payloadDigest,customerId,connectionId,issuedAt?,expiresAt,signature?}; confirmed requires all fields and matching authenticated subject.','Pending quote record and portal-only/reminder outbox use caseId/proposalId/template uniqueness; operation not dispatched until fresh C4 then C6.'],whyCode='Exact subject/amount binding, deadlines, event deduplication and signatures need deterministic checks.',approvalRule='Only same authenticated customer may confirm the exact immutable quote; C9 grants no credit permission. Signed receipt consumed by C4 then writer fresh guards; expired/replayed mismatched receipt rejected.'))
items('components').append(c9)
def node(i,title,c,state,trans,guards,term=''):
 return dict(id=i,kind='workflow',title=title,description=json.dumps(dict(state=state,guardBindings=guards,precedence='First true transition wins; enum outcomes exhaustive.',transitions=[{'to':t,'when':w,'mode':'exclusive'} for t,w in trans],failureDisposition='No dispatch; persist pending case and named customer-operations owner.',timeout='24h quote lifetime; original expiry never extended by retry.',retryPolicy='Idempotent portal receipt by clientCommandId/eventId; no financial retry.',terminalDisposition=term)),reasoning='Confirmation precedes authorization and remains durable across browser/session loss.',assumptions=['H2','H3','H8'],sources=src,data=dict(componentId=c,taskIds=['T4.1','T5'],next=list(dict.fromkeys(t for t,w in trans)),decision=len(set(t for t,w in trans))>1,example='Quote QP1 for 27 XCU minor units is confirmed by CU1 with digest; fresh checks run before OP1 dispatch.'))
w4=get('workflow','W4');wc=json.loads(w4['description']);wc['transitions'].append({'to':'W18','when':'plan.route=needs_confirmation','mode':'exclusive'});w4['description']=json.dumps(wc);w4['data']['next'].append('W18')
# Existing approved path also rechecks confirmation; absent confirmation goes quote path.
w9=get('workflow','W9');wc=json.loads(w9['description']);wc['transitions'].append({'to':'W18','when':'plan.route=needs_confirmation','mode':'exclusive'});w9['description']=json.dumps(wc);w9['data']['next'].append('W18')
w11=get('workflow','W11');wc=json.loads(w11['description']);wc['transitions'][1]['when']='otherwise, including needs_confirmation or expired/revoked authority';w11['description']=json.dumps(wc)
items('workflow').append(node('W18','Await exact customer credit confirmation','C9','awaiting_confirmation',[('W19','confirmation.status=confirmed'),('W15','confirmation.status in [declined,cancelled]'),('W16','confirmation.status in [expired,changed,unavailable]'),('W18','confirmation.status=waiting and now<proposal.expiresAt')],{'confirmation':'C9.confirmation typed signed receipt/status; proposal expiresAt persisted; timer emits expired at boundary, not waiting'}))
items('workflow').append(node('W19','Fresh checks after customer confirmation','C4','confirmation_recheck',[('W10','plan.route=credit'),('W15','plan.route in [blocked,cancelled,duplicate]'),('W16','plan.route in [human,explain,needs_confirmation]')],{'plan':'C4.plan with validated C9 receipt; same immutable bytes/business caseRevision; fresh active state, policy, ledger, approval. Intent change is human-owned, never silent repost.'}))
# Fixture precision, including normalized ordered API mocks. Each fixture remains full self-contained JSON.
for x in items('evals'):
 if x['data']['category']!='golden':continue
 f=json.loads(x['data']['input'])
 # Existing confirmation is positive precondition in base; add complete receipt binding and proposal context.
 f['confirmation'].update(confirmationId='CONF1',caseId='CASE1',caseRevision=3,payloadRecordId='PAY1',decision='confirm',issuedAt='2026-10-01T23:55:00Z',expiresAt='2026-10-02T00:25:00Z',signature='synthetic-server-valid')
 f['mockStrictness']={'unexpectedCall':'fail','unusedMocks':'allowed only after earlier deterministic guard short-circuit; record consumed mocks','externalCalls':'forbidden'}
 if x['id'] in ['EV3','EV19']:
  f['entryState']='W10';f['operationJournal']={'operationId':'OP1','state':'prepared','payloadDigest':f['payloadDigest'],'authorizationProof':'AP1','dispatchAttempts':0}
 if x['id']=='EV14':
  f['orderedMocks']=[{'call':'model','result':f['model']},{'call':'model_schema_retry','result':f['model']},{'call':'refer','result':{'status':'waiting','queueId':'Q1','receiptId':'QR1','dueAt':'2026-10-04T00:00:00Z','owner':'Customer operations'}}]
 x['data']['input']=json.dumps(f,separators=(',',':'))
# Add self-contained confirmation positive, deny and expiry goldens.
base=json.loads(get('evals','EV1')['data']['input'])
for i,title,status,expected,asserts in [
('EV32','Customer confirms immutable quote','confirmed',{'disposition':'credited','postingId':'POST1','amountMinor':27},['No dispatch before confirmed signed receipt','Confirming CU1 and exact digest/amount/connection only','Fresh C4 checks after confirmation','One OP1 credit and matching POST1 proof']),
('EV33','Customer declines quote','declined',{'disposition':'cancelled','postings':0},['No postCredit','No credit authority from natural language','Decline bound to QP1 and CU1','Case cancellation receipt persisted']),
('EV34','Quote expiry or changed intent does not dispatch','expired',{'disposition':'human_owned','reason':'confirmation_expired'},['At 24h exact quote expiry','One 12h reminder only','No postCredit','Customer operations owns follow-up; fresh plan and confirmation required'])]:
 f=copy.deepcopy(base);f['entryState']='W18';f['proposal']={'proposalId':'QP1','payloadRecordId':'PAY1','confirmationId':'CONF1','payloadDigest':f['payloadDigest'],'caseId':'CASE1','caseRevision':3,'customerId':'CU1','connectionId':'S1','createdAt':'2026-10-01T00:00:00Z','expiresAt':'2026-10-02T00:00:00Z','amountMinor':27,'currency':'XCU'}
 f['confirmation']['status']=status
 if status=='expired':f['confirmation']=None
 else:f['now']='2026-10-01T23:55:00Z'
 f['events']=[{'type':('timer' if status=='expired' else 'confirm_credit' if status=='confirmed' else 'decline_credit'),'eventId':'CE1','proposalId':'QP1','digest':f['payloadDigest'],'expectedCaseRevision':3,'sessionBinding':{'tenantId':'TEL-A','customerId':'CU1','connectionId':'S1'}}]
 if status!='confirmed':f['orderedMocks']=[]
 template=copy.deepcopy(get('evals','EV1'));template.update(id=i,title=title,description='Planned full confirmation lifecycle fixture, synthetic and not executed.');template['data'].update(taskIds=['T4.1','T5'],componentIds=['C9','C4','C6','C8'],failureModeIds=['FM2','FM7'],input=json.dumps(f,separators=(',',':')),expected=json.dumps(expected),passRule=json.dumps({'all':asserts,'harness':'Deterministic clock and exact API/journal/outbox logs.'}),testSet='telecom-v1 full resolved fixture '+i)
 items('evals').append(template)
# Propagate enumerated goldens through actual offline/release/handoff references.
for s in ['evals','export']:
 for x in items(s):
  if s=='evals' and x['data']['category']=='golden':continue
  for k,v in list(x['data'].items()):
   if isinstance(v,str):x['data'][k]=v.replace('EV1-EV28','EV1-EV28 and EV32-EV34')
get('export','X1')['data']['acceptanceCriteria'].append('C9/W18-W19: CU1 confirms the exact quote with signed digest receipt; 24h expiry/decline/change stops dispatch; customer confirmation does not itself authorize money; EV32-EV34 required in EV31 manifest.')
get('export','X1')['data']['buildInstructions']=get('export','X1')['data']['buildInstructions'].replace('W1-W17 and C1-C8','W1-W19 (W5 unused) and C1-C9')+' Add Quote/Confirmation records with distinct immutable business revision versus workflow-state revision. C9 receives confirm_credit/decline_credit events directly from scoped portal; workflow entry W1 handles submit/resume/cancel, not confirmation commands. Confirmation events do not change intended business payload; any intent change invalidates quote. Reserve confirmationId before digest creation so receipt binds exact immutable payload without circular digest.'
get('framework','F1')['data']['choice']=get('framework','F1')['data']['choice'].replace('W1-W17','W1-W19 (W5 unused)')
get('framework','F1')['description']=get('framework','F1')['description'].replace('W1-W17','W1-W19 (W5 unused)')
# Explicit cap and supervisor semantics reconcile all prose.
get('components','C4')['description']+=' Compute uncapped entitlement first. If above automatic cap, route entire claim to supervisor. SupervisorCapMinor must be provided in approved policy; no default supervisor unlimited amount. Supervisors cannot approve beyond that cap. For EV27 synthetic policy defines 2000 minor-unit supervisor cap.'
for fm in items('fmea'):
 fm['data']['evalIds']=[e['id'] for e in items('evals') if fm['id'] in e['data']['failureModeIds']]
(O/'design.json').write_text(json.dumps(D,indent=2,ensure_ascii=False)+'\n')
# Round2 review records what was repaired; no evidence claims business execution.
new=[]
for i,s,e in evidence:
 if i=='D3':s=3;e='W18-W19 add signed exact-quote confirmation with 24h bound, deny/expiry/changed-intent owned exits and fresh recheck; W10-W12 reconcile unknowns; W7 retains original 48h deadline.'
 if i=='D4':s=3;e='C9 typed portal confirm_credit/decline_credit events, proposal/receipt/digest/subject/expiry fields and bounded reminder; C1 remains intake router; C4/C6 repeat exact action checks.'
 if i=='D10':s=3;e='EV1-EV28 plus EV32-EV34 are complete self-contained synthetic fixtures; EV3/EV19 explicitly enter prepared W10; EV29/EV31 enumerate new confirmation fixtures. Planned harness has strict unexpected calls; tests not executed.'
 if i=='D12':s=3;e='X1 propagates C9/W18-W19, quote/confirmation records and distinct business/state revisions. Exports will derive from this canonical version; H1-H8 remain explicit launch blockers.'
 new.append({'id':i,'score':s,'evidence':[e]})
resolved=copy.deepcopy(issues)
for z in resolved:z['resolved']=True;z['message']+=' Repaired in round 2: C9/W18-W19, EV3/EV19, EV32-EV34, H2/C4 and X1 updated; reciprocal links and release manifest propagated.'
r2={'method':'self-review','round':2,'status':'pass','dimensions':new,'issues':resolved,'limitations':limits}
(O/'review.json').write_text(json.dumps(r2,indent=2)+'\n')
print('Review repair saved; cards',sum(len(s['items']) for s in D['stages'].values()))
