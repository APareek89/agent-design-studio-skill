import json,pathlib
p=pathlib.Path(__file__).parent
d=json.loads((p/'design.json').read_text())
evidence={
'D1':'CTX1/T0-T4 bound outage-credit scope, exceptions and durable owned outcomes.',
'D2':'T leaves reach C/W/evals; FMEA evaluation links derived reciprocally; H1-H6 identify proposals.',
'D3':'W10 reconciliation and wait timers explicit, but EV6 adds an unsupported terminal enum.',
'D4':'C1-C9 typed contracts include exact immutable credit fields, error enums and lookup ownership.',
'D5':'C1/C4/C7 fresh subject/active-service/authority checks; C3 outputs never bind writes.',
'D6':'H1-H6 mark policy, APIs, staffing, privacy and budget as proposals/blockers.',
'D7':'F1-F3 compare durable workflow and cloud/open-source storage patterns; capabilities explicitly unverified.',
'D8':'M1 derives <=0.9 expected calls and one worst-case call; USD .00378 expected upper model cost.',
'D9':'FM1-FM9 cover subject, stale/revoked authority, duplicate, prompt/conflict, unknown commit, proof and queues.',
'D10':'EV1-EV23 contain substantive fixtures and release suite; EV7 incorrectly asserts no physical write after malformed provider response.',
'D11':'R1-R4 specify censored resolution hours, baseline-first experiment, account clusters and phase entry/exit.',
'D12':'X1/milestones provide implementable scope, but structural alternatives/autonomy values need correction.'}
issues=[dict(id='ISS1',severity='major',stage='workflow',itemId='W10',message='EV6 expects CREDITED_CANCEL_REQUESTED outside C9 outcome enum. Keep CREDITED with cancellationRequested flag; otherwise client state handling needs invention.',resolved=False),dict(id='ISS2',severity='major',stage='evals',itemId='EV7',message='A malformed POST response does not prove zero ledger effects. Start fixture after uncertain authorized attempt, assert zero additional writes and UNKNOWN_OWNED with proof lock.',resolved=False),dict(id='ISS3',severity='major',stage='framework',itemId='F1',message='Structural validator rejects alternatives string and presentation autonomy labels. Use array and allowed levels; rerun.',resolved=False)]
r=dict(method='self-review',round=1,status='needs-work',dimensions=[dict(id=k,score=2 if k in ['D3','D10','D12'] else 3,evidence=[v]) for k,v in evidence.items()],issues=issues,limitations=['Design review only. No business control fixtures or API integration tests executed. Proposed policies, provider prices and launch approvals remain unverified.'])
(p/'review-round-1.json').write_text(json.dumps(r,indent=2))
for f in d['stages']['framework']['items']:f['data']['alternatives']=[f['data']['alternatives']]
for row in d['presentation']['autonomy']:row['level']='human decides' if 'Supervisor' in row['level'] else 'acts alone'
# Investigation and explanation remain one bounded workflow; explanation is a suggestion checked by code.
d['presentation']['autonomy'][0]['level']='suggests'
for ev in d['stages']['evals']['items']:
 if ev['id']=='EV6':
  e=json.loads(ev['data']['expected']);e['status']='CREDITED';e['cancellationRequested']=True;ev['data']['expected']=json.dumps(e)
 if ev['id']=='EV7':
  i=json.loads(ev['data']['input']);i['operations'][0]['phase']='SUBMITTED_UNKNOWN';i['mocks']=[{'call':'prior authorized POST OP1','result':{'status':'POSTED','postingId':None}},{'call':'lookup OP1 and posting proof bounded','result':'UNAVAILABLE'}];ev['data']['input']=json.dumps(i)
  e=json.loads(ev['data']['expected']);e['additionalCredits']=0;e['priorCommit']='UNKNOWN';ev['data']['expected']=json.dumps(e)
  ev['data']['passRule']=json.dumps({'assertions':['Fixture begins after prior authorized submission; writes counts additional effects only.','Provider outcome unknown; no CREDITED display or second POST.','Operation lock retained; duty manager owns proof recovery with next update within 2h.']})
for g in d['semantics']['goldens']:
 ev=next(x for x in d['stages']['evals']['items'] if x['id']==g['evalId']);g['fixture']={'input':json.loads(ev['data']['input']),'expected':json.loads(ev['data']['expected'])}
for c in d['stages']['components']['items']:
 if c['id']=='C4':c['description']=c['description'].replace('then min(calculated,50000,chargeMinor-alreadyCreditedMinor).','then compare raw calculated amount to the 50000 automatic cap. Above cap routes HUMAN. Otherwise use min(calculated,chargeMinor-alreadyCreditedMinor).')
(p/'design.json').write_text(json.dumps(d,indent=2,ensure_ascii=False))
