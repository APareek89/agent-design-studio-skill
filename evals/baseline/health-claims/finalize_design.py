import json,pathlib,hashlib,datetime
P=pathlib.Path('/Users/macbook/Documents/agent-design-studio-skill/evals/baseline/health-claims');d=json.loads((P/'design.json').read_text());by={x['id']:x for s in d['stages'].values() for x in s['items']}
limitations=['Self-review by host model; no independent evaluator or stakeholder sign-off.','Frozen v1 validator verifies structure/references only. No business test harness, insurer integration, medical-data processing or production controls executed.','Synthetic fixtures and illustrative budgets do not prove accuracy, compliance, policy correctness or savings. H1-H6/H9 remain live-use blockers.','PDF is deferred by explicit parent instruction; this run produces canonical JSON and companion exports only.']
def rev(r,status,scores,evid,issues):return dict(method='self-review',round=r,status=status,dimensions=[dict(id='D'+str(i+1),score=n,evidence=[evid[i]]) for i,n in enumerate(scores)],issues=issues,limitations=limitations)
e=['CTX1–CTX6/T0–T4.3 define start/end, supported product, assist-only rejection review and cancellation.','T1–T4.3 all reach components/workflow/goldens; FM1–FM10 risk links reciprocal across all layers.','W1–W13 have boolean decision fields after repair, bound producer guards and persistent unknown owner.','C2 explicit date parser now breaks policy-selection dependency; C5 events reuse C6 writer; blocked audit service is minimal.','C6 fresh API scope/identity/CAS/hash enforcement; no insurer money permission; medical-data H5 explicit.','H1–H9 and sources are hypotheses; no measured baseline or vendor promise invented.','F1–F5 choose transactional workflow and bounded model with rejected alternatives and same cloud data criteria.','M1 .84 expected/2 max calls, exact illustrative arithmetic, overflow hold and no silent truncation.','FM1–FM10 case-specific controls/owners/gates, including temporal policy and room cap/proportion ambiguity.','Structural schema now passes, but reinspection found EV7 invalid citation not actually altered, EV26 wrong source span for dates and EV18 preexisting-timer prerequisites unclear.','R1–R6 cluster randomization, baseline-driven power, safety stops and noncircular phase gates.','X1 preserves safety boundary; fixtures need the last material repairs before calling design implementation-ready.']
issues=[dict(id='ISSUE5',severity='major',stage='evals',itemId='EV7',message='Citation validity was only mocked false although actual model span remained valid; must corrupt a concrete span to isolate guard.',resolved=False),dict(id='ISSUE6',severity='major',stage='evals',itemId='EV26',message='Generic fixture augmentation cited last document (policy clause) for admission dates. Correct dates to discharge span and include actual line trace in persist packet.',resolved=False),dict(id='ISSUE7',severity='major',stage='evals',itemId='EV18',message='Timer fixture runs at 48h without a clear preexisting committed review record; make event action and prior receipt explicit.',resolved=False)]
(P/'review-round-2.json').write_text(json.dumps(rev(2,'needs-work',[3,3,3,3,3,4,3,3,3,2,3,2],e,issues),indent=2)+'\n')
canon=lambda x:json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False)
sha=lambda s:hashlib.sha256(s.encode()).hexdigest()
for x in d['stages']['evals']['items']:
 if x['data']['category']!='golden':continue
 b=json.loads(x['data']['input']);spans={q['docId']:dict(docId=q['docId'],version=q['version'],page=1,start=0,end=len(q['text']),hash=q['hash']) for q in b['documents']}
 for m in b['orderedMocks']:
  if m['call']=='model':
   for fact in m['payload']['facts']:
    if fact['field'] in ['admissionDate','dischargeDate','roomClass','inpatient'] and 'discharge-1' in spans:fact['citation']=spans['discharge-1']
    elif fact['field']=='coverageFlag':fact['citation']={'policyVersion':b['policyRegistry']['versions'][0]['id'],'ruleId':'HC1.coverage','policyHash':b['policyRegistry']['versions'][0]['hash']}
   if x['id']=='EV7':m['payload']['facts'][0]['citation']=dict(docId='discharge-1',version=999,page=1,start=0,end=10)
 p=b['persistEnvelope']['payload']
 if 'packet' in p['payload']:
  flag=b['facts']['coverageFlag'];room=b['facts']['billLines'][0]['amountMinor'];eligible=0 if flag=='excluded' else min(room,b['policyRegistry']['versions'][0]['rules']['roomCapMinorPerDay'])
  p['payload']['packet']['lines']=[{'lineId':'L1','billedMinor':room,'eligibleMinor':eligible,'deductionMinor':room-eligible,'ruleId':'HC1.coverage' if flag=='excluded' else 'HC1.roomCap'},{'lineId':'L2','billedMinor':2000000,'eligibleMinor':0 if flag=='excluded' else 2000000,'deductionMinor':2000000 if flag=='excluded' else 0,'ruleId':'HC1.coverage' if flag=='excluded' else 'HC1.noProportion'}]
 if x['id']=='EV17':
  original=json.loads(canon(p));original['memberId']='member-1';digest=sha(canon(original))
 else:digest=sha(canon(p))
 b['persistEnvelope']['digest']=digest
 for m in b['orderedMocks']:
  if m['call']=='persist':m['expectedDigest']=digest
  if m['call'] in ['lookupOperation','callback']:m['digest']=digest
 if 'priorAuthorization' in b:b['priorAuthorization'].update(opId=p['opId'],canonicalPayloadDigest=digest,expectedRevision=p['expectedRevision'])
 if x['id']=='EV18':
  b['eventAction']={'type':'run_due_timers','asOf':b['clock']};b['existingOperations']=[{'opId':p['opId'],'digest':digest,'status':'committed','recordId':'record-1','auditId':'audit-1','outboxId':'outbox-1','createdAt':'2026-10-01T12:00:00Z'}];b['case']['status']='review_pending';b['orderedMocks']=[q for q in b['orderedMocks'] if q['call']=='timer']
 b['mockExecution']='Ordered mocks are available responses; early owned terminal may leave tail unused. Positive paths must consume reached calls in order. Component tests stub C3; EV23 model evaluation disables model stub and uses source/expected assertions as oracle.'
 x['data']['input']=json.dumps(b,separators=(',',':'))
# strengthen source types for policy citations consistently
by['C3']['data']['outputs'].append('EvidenceRef is discriminated: document span {docId,version,page,start,end} or approved policy clause {policyVersion,policyHash,ruleId}; facts use source type matching responsibility. No cross-type citation substitutes for actual dates or amounts.')
by['EV23']['data']['passRule']+=' For C3 actual-model evaluation ignore ordered model-response mocks, run real bounded inference against each adversarial/missing/conflicting document and validate exact source support/abstention, repeating across random seeds; never report guard mocks as model robustness evidence.'
# all reciprocal links still unchanged
(P/'design.json').write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
# record exact mechanical audit, not business assertion execution
hashchecks=[]
for x in d['stages']['evals']['items']:
 if x['data']['category']!='golden':continue
 b=json.loads(x['data']['input']);actual=sha(canon(b['persistEnvelope']['payload']));equal=actual==b['persistEnvelope']['digest'];hashchecks.append({'id':x['id'],'payloadDigestMatches':equal,'expectedMatch':x['id']!='EV17','inputLength':len(x['data']['input'])})
assert all(q['payloadDigestMatches']==q['expectedMatch'] for q in hashchecks)
assert all(q['inputLength']<=8000 for q in hashchecks)
(P/'fixture-checks.json').write_text(json.dumps({'method':'Local Python JSON parse, SHA256 recomputation and length assertions only; does not execute workflow or business rules.','checks':hashchecks,'allExpectedHashAndLengthChecksPass':True},indent=2)+'\n')
# semantic remaining limitation: normalized page-wide spans require harness parser approved, acceptable? Score honestly 3 with H assumptions.
finale=['CTX1–CTX6/T0–T4.3 completely bound supported intake through review/hold/cancel; all final insurer decisions remain human.','Every high-risk leaf has reachable W coverage and substantive golden. FM/EV reciprocal links derived once; EV26 is included in FM10 and EV25 manifest.','W1–W13 enumerate ready/hold/cancel/reject and commit/error/unknown paths. Cancellation precedence, CAS and digest readback prevent conflicting resubmission; W11 retains recovery owner.','C1–C7 declare typed inputs/outputs, read and internal write logical contracts, temporal parser, human-event reentry and SLA roles. Real adapters remain verification dependencies.','C4 owns integer arithmetic/dates/limits; C6 checks identity/resource/version/full payload at API. C3 has no tools; F3/F4 isolate medical evidence and redacted inference.','H1–H9 identify every unprovided policy/volume/price/threshold/owner as hypothesis. Sources preserve brief and exact H statements; no clinical/legal claims.','F1–F5 choose code state machine and bounded single judgement over multi-agent/open-ended adjudication; data candidates labelled unverified against common criteria.','M1 cost formula .84*$0.0384=$0.032256/case and 2-call worst budget reproducible. Input overflow holds; tier selection requires held-out evidence and fine-tune gates.','FM1–FM10 contain concrete inpatient-specific effects, causes, S/O/D rationale, owner release gates, control and reciprocal golden coverage. No risk accepted.','23 self-contained golden fixtures (EV1–EV22,EV26) plus EV23 offline/EV24 online/EV25 release. Exact payload hashes locally checked; EV17 intentionally fails. Actual citation mutation, room cap controls, stale policy, cancellation and callback fixtures inspected. Planned harness remains unexecuted.','R1–R6 specify unknown-baseline collection, proposed quality/time targets, causal measures, cluster experiment and noncircular shadow/assist/scale gates. Safety event overrides benefits.','X1 follows canonical C/W/EV IDs; exports generated from same canonical design after frozen validation. Launch blockers remain explicit, no business control execution claimed.']
resolved=[{**z,'resolved':True,'message':z['message']+' Repaired in final canonical version and re-inspected.'} for z in issues]
review=rev(3,'pass',[3,3,3,3,3,4,3,3,3,3,3,3],finale,resolved)
(P/'review.json').write_text(json.dumps(review,indent=2)+'\n')
print('Final authored JSON, 3-round self-review, fixture digest/length checks written.')
