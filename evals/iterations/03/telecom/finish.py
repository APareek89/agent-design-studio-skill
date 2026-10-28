import json,pathlib,copy
p=pathlib.Path(__file__).parent;d=json.loads((p/'design.json').read_text());r=json.loads((p/'review-round-1.json').read_text())
r['round']=2
for x in r['issues']:x['resolved']=True
r['issues'] += [dict(id='ISS4',severity='major',stage='workflow',itemId='W6',message='Wait notice edge targets a write node rather than a separate requester_notice role. Add durable notice scheduling node W5, then external delivery W7.',resolved=False),dict(id='ISS5',severity='major',stage='export',itemId='X1',message='Several descriptions empty and W12 claims T3.3 outside C6 task contract. Populate meaningful descriptions and constrain W12 task claim.',resolved=False)]
for x in r['dimensions']:
 if x['id'] in ['D3','D12']:x['score']=2
 if x['id']=='D10':x['score']=3;x['evidence']=['EV6 terminal enum repaired; EV7 now starts after uncertain submission and asserts no additional effects.']
(p/'review-round-2.json').write_text(json.dumps(r,indent=2))
for stage,packet in d['stages'].items():
 for x in packet['items']:
  if not x['description']:
   data=x['data']
   x['description']={
    'context':lambda:data['value'],
    'tasks':lambda: ('Load authoritative attributes from '+data['sourceSystem']) if x['kind']=='attribute' else ('Outcome: '+x['title']+'. '+data['basis'][0]),
    'framework':lambda:data['choice']+' Rejected: '+str(data['alternatives']),
    'models':lambda:data['rationale'],
    'evals':lambda:'Planned '+data['category']+' verification: '+x['title']+'. Inspect exact input, expected effects and assertions below; not executed business evidence.',
    'rollout':lambda:data['gate'],
    'export':lambda:'Coding handoff preserves the first-release credit boundary, exact authority and recovery contracts, and launch evidence gates.'
   }[stage]()
# Separate durable requester-notice role from actual external send.
c5=next(c for c in d['stages']['components']['items'] if c['id']=='C5');c5['data']['taskIds'].append('T4')
w6=next(w for w in d['stages']['workflow']['items'] if w['id']=='W6');wc=json.loads(w6['description'])
for tr in wc['transitions']:
 if tr['to']=='W7':tr['to']='W5'
w6['description']=json.dumps(wc);w6['data']['next']=['W5' if n=='W7' else n for n in w6['data']['next']]
for tr in d['semantics']['transitions']:
 if tr['from']=='W6' and tr['to']=='W7':tr['to']='W5'
w5=copy.deepcopy(w6);w5.update(id='W5',title='Schedule customer waiting notice');w5['data'].update(componentId='C5',taskIds=['T4'],next=['W7'],decision=False,example='At intake create one queued status notice event before external send.');w5['description']=json.dumps(dict(state='C5 reduces NOTICE_DUE event with stable eventId; persist statusRef, verified destinationRef and noticeKey from scoped account and current case. It records nextUpdateAt from server clock. Schedule once; overdue/ack/reminder events never reset original queue clock. External delivery failure never cancels queue ownership.',transitions=[dict(to='W7',when='noticeEventPersisted == true',mode='exclusive')],failureDisposition='Durable outbox retries internal persistence once then leaves duty-manager incident and authenticated in-app status; no unowned wait.',timeout='Immediate internal transaction, 2 seconds; one persistence retry.',retryPolicy='Deduplicate internal event ID; no repeated notice for same event.',terminalDisposition=''))
d['stages']['workflow']['items'].insert(4,w5);d['semantics']['nodes'].append(dict(id='W5',kind='requester_notice'));d['semantics']['transitions'].append({'from':'W5','to':'W7','when':'noticeEventPersisted == true','outcome':'normal'})
next(w for w in d['stages']['workflow']['items'] if w['id']=='W12')['data']['taskIds']=['T4']
d['presentation']['workflowLabels']['W5']='Schedule waiting update'
for m in d['milestones']:
 if m['id']=='02':
  m['taskIds'].append('T4');m['evalIds']=sorted(set(m['evalIds'])|{e['id'] for e in d['stages']['evals']['items'] if 'C5' in e['data']['componentIds']})
(p/'design.json').write_text(json.dumps(d,indent=2,ensure_ascii=False))
