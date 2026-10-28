import json,pathlib
O=pathlib.Path(__file__).parent
d=json.loads((O/'design.json').read_text())
def save_review(path,round,status,issues,low):
 evidence={'D1':'CTX1/CTX3 and T1-T5 bound draft-only inpatient review and owned pending outcomes.','D2':'T1-T5 link C1-C7/W1-W8 and EV1-EV20; FM links derived in both directions.','D3':'W4 timeout/unknown to W5; W5 bounded reads; W6 proof before W7; W8 owns unresolved outcomes.','D4':'C1-C7 typed contracts separate read, draft-write and readback; H3 marks adapter capability unverified.','D5':'C3 uses approved policy and human-verified facts; C4 cannot pay/deny; C6 durable assignment proof.','D6':'H1-H6 mark proposed scope, rules, ownership, privacy and budgets; no clinical/legal claims.','D7':'F1-F4 select code worker; reject in-memory and unconstrained agents; candidates explicitly unverified.','D8':'M1 gives W2-only calls 1.05 expected/2 maximum, USD .0378 illustrative and fallback.','D9':'FM1-FM7 specific subject, policy, room-cap, injection, duplicate, uncertainty and queue risks, owner gates.','D10':'EV1-EV17 self-contained synthetic fixtures, EV18 held-out, EV19 operations and EV20 inclusion assertions.','D11':'R1-R7 define denominators, baseline, mean-test power plan, cluster assignment and assist-only scale.','D12':'X1 and milestones select exact contracts; no final claim writes or fabricated launch evidence.'}
 r={'method':'self-review','round':round,'status':status,'dimensions':[{'id':f'D{i}','score':2 if f'D{i}' in low else 3,'evidence':[evidence[f'D{i}']]} for i in range(1,13)],'issues':issues,'limitations':['Self-review by design author; independent reviewer has not evaluated these files.','Schema and semantic declarations do not execute business controls or establish provenance truth.','Synthetic policy, proposed API support, privacy rules and human queue SLA require H1-H5 owner evidence.','No live claim, medical advice, final decision, cost quote or measured savings is represented.']}
 (O/path).write_text(json.dumps(r,indent=2)+'\n')
save_review('review-round-1.json',1,'needs-work',[{'id':'ISSUE1','severity':'major','stage':'context','itemId':'CTX1','message':'Initial artifact left descriptions empty on many cards; validator rejects incomplete cards. Fill specific summaries and revalidate.','resolved':False},{'id':'ISSUE2','severity':'major','stage':'workflow','itemId':'W8','message':'W8 lists T1/T4 but C7 serves only T5. Align display responsibility with T5.','resolved':False},{'id':'ISSUE3','severity':'major','stage':'evals','itemId':'EV9','message':'Missing-proof fixture says start after prior operation but includes a POST in mocks. Explicitly start proof stage and remove POST to isolate guard.','resolved':False}],['D2','D4','D10','D12'])
for stage,packet in d['stages'].items():
 for i in packet['items']:
  if not i['description']:
   data=i['data'];i['description']= {
    'context':lambda:data['value'],
    'tasks':lambda:' '.join(data.get('basis',[])) or 'Load trusted attributes from '+data.get('sourceSystem','')+'; model proposals are separate.',
    'framework':lambda:data['choice']+' '+data['tradeoffs'],
    'models':lambda:data['rationale'],
    'evals':lambda:'Planned verification: '+i['title']+'. Inspect full input, expected state and assertions; these are not executed tests.',
    'rollout':lambda:data['phase']+'. '+data['gate'],
    'export':lambda:'Implement only the bounded inpatient review-packet workflow. Preserve evidence gates and draft-only permissions.'
   }[stage]()
for w in d['stages']['workflow']['items']:
 if w['id']=='W8':w['data']['taskIds']=['T5']
for e in d['stages']['evals']['items']:
 if e['id']=='EV9':
  x=json.loads(e['data']['input']);x['startAt']='proof_stage_after_prior_authorized_save';x['mockSequence']=x['mockSequence'][1:];e['data']['input']=json.dumps(x)
  next(g for g in d['semantics']['goldens'] if g['evalId']=='EV9')['fixture']['input']=x
(O/'design.json').write_text(json.dumps(d,indent=2)+'\n')
