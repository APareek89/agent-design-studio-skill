import json,pathlib,hashlib
P=pathlib.Path('/Users/macbook/Documents/agent-design-studio-skill/evals/baseline/health-claims');d=json.loads((P/'design.json').read_text());by={x['id']:x for s in d['stages'].values() for x in s['items']}
limitations=['Host-model self-review, not independent review or stakeholder approval.','Frozen v1 schema/reference checks only; no business harness, provider, medical-data processing, live API or production control executed.','All insurer rules, roles, thresholds, budgets and cloud candidates are proposals or synthetic fixtures. H1-H6/H9 require verification before real data.','PDF deliberately deferred by parent evaluation instruction; companion export is not PDF completion.']
def review(round,status,scores,evidence,issues):return dict(method='self-review',round=round,status=status,dimensions=[dict(id='D'+str(i+1),score=s,evidence=[evidence[i]]) for i,s in enumerate(scores)],issues=issues,limitations=limitations)
ev=['CTX1/CTX3 and T1–T4.3 bound an assist-only inpatient workflow with owned holds/cancellation.','All 10 risk links derive reciprocally from 25 evaluation records; leaf/component/workflow IDs are explicit.','W8/W10/W11 cover unknown local commits, but initial decision fields violate boolean schema.','C1–C7 contracts define enums and writers; initial C2 admission-date source and C5 event persistence need precision.','No payment/denial authority; C6 fresh checks and isolation. W13 blocked-record service identity needs clarification.','H1–H9 distinguish synthetic policy, prices and launch prerequisites; no live advice claimed.','F1–F5 choose DB state machine and single model; compare cloud categories on same criteria as unverified candidates.','M1 derives .84 calls/case and $32.256/1000, bounded schema retries; token overflow needs explicit disposition.','FM1–FM10 describe temporal coverage, room cap, identity, prompt injection, duplicates, unknown commits and queue failure.','EV1–EV22 are full resolved records, but hash placeholders and model mock payloads omit exact spans/digests. Additional proposed rejection control missing.','R1–R6 state baseline, causal metrics, noncircular phase entry and powered cluster experiment.','X1 preserves assist scope, but type/fixture fixes must propagate before structural export.']
issues=[dict(id='ISSUE1',severity='major',stage='workflow',itemId='W1',message='All W data.decision values are prose strings instead of required booleans. Fix type and retain exclusivity prose in description; structural validation fails.',resolved=False),dict(id='ISSUE2',severity='major',stage='evals',itemId='EV14',message='Fixtures use symbolic hash strings, no exact canonical persist payload/digest and incomplete model outputs; implementer must invent material test data. Resolve actual spans/hashes and command payloads; add rejection proposal positive control.',resolved=False),dict(id='ISSUE3',severity='major',stage='components',itemId='C2',message='Date needed to select policy before model extraction lacks a concrete normalized parser path; C5 human event persistence and W13 revoked-principal blocked audit need defined service ownership.',resolved=False),dict(id='ISSUE4',severity='minor',stage='models',itemId='M1',message='12k token budget vs page bound requires explicit overflow hold rather than silent truncation.',resolved=False)]
(P/'review-round-1.json').write_text(json.dumps(review(1,'needs-work',[3,3,2,2,2,4,3,3,3,2,3,2],ev,issues),indent=2)+'\n')
# schema and contracts repair
for w in d['stages']['workflow']['items']:
 c=json.loads(w['description']);c['precedence']='Cancellation first at each work boundary; listed enum guards are mutually exclusive; unknown internal errors map to hold. At W1 status is C1 sole enum. W8 uses atomic cancel override before commit.';w['description']=json.dumps(c);w['data']['decision']=len(w['data']['next'])>1
by['C2']['description']+=' Before version selection, a deterministic supported-format parser reads explicit Admission YYYY-MM-DD and Discharge YYYY-MM-DD labels and verifies document subject. It emits date values and exact spans; missing, non-ISO or contradictory date labels hold with MISSING or UNREADABLE/FACT_CONFLICT through C4, without a model deciding temporal applicability. C2 retrieves full authoritative version list then selects half-open interval using that confirmed date. Unsupported language/date forms route to intake operator. This narrow parsing support is part of H9, not a claimed OCR capability.'
by['C2']['data']['outputs'].append('confirmedDates:{admissionDate:ISO date,dischargeDate:ISO date,citations:SpanRef[]}; optional only when hold; required ready. Normalized parser must have exactly one consistent pair.')
by['C5']['description']+=' Durable queue assignment and timers are part of C6 transaction/outbox, not a separate best-effort action. Acknowledgment/resolution APIs use command kind human_event with actorId, tenant/member/case, expectedRevision, eventId, eventType ack|reviewed|request_evidence, notesRef and UTC time; fresh role checks are required, rejected events never change status. Accepted events are processed through W8–W11 with opId=eventId and full digest, preserving queue assignment for request_evidence; reviewed records only internal completion. Human updates never write insurer decisions. C5 has no independent database writer.'
by['C6']['data']['inputs'].append('persist discriminator: disposition|human_event; human_event requires eventId,eventType:ack|reviewed|request_evidence,actorId,notesRef and expectedRevision; action-specific medical fields are absent. All fields are digest-bound; fresh reviewer role required.')
by['C6']['description']+=' Blocked metadata audit uses a separately scoped service identity allowed only requestId/caseId/reason/owner/UTC/opId, no medical content or new recommendation. It never reuses revoked actor scope. Durable ingress receipt exists before work begins; if blocked-event update fails, platform recovery owns original ingress receipt and never reports completion. The service identity cannot change claim disposition or review payload.'
by['W13']['description']=json.dumps({**json.loads(by['W13']['description']),'failureDisposition':'C6 blocked-event service identity writes minimal operational metadata only under separately scoped append:blocked authority; revoked requester never gets a write. On event-store failure, durable original ingress receipt remains assigned platform recovery and status is blocked_owned; no successful recommendation. New revision needs fresh actor authority.'})
by['C3']['description']+=' Inference input hard maximum is 12000 estimated tokenizer tokens including instructions/schema/evidence. If full evidence cannot fit, hold with INSUFFICIENT_EVIDENCE; never truncate bill lines or select a convenient subset. The 50-page/200-line cap is additional, not an assurance of token fit.'
# Add explicit medical/coverage synthetic rule and exact fixture material. No inheritance.
by['C4']['description']+=' HC1 synthetic eligibility requires inpatient=true, bound active member interval covering selected admission and diagnosis coverageFlag=covered explicitly established by approved rule pack; excluded flag proposes rejection with zero eligible amount for human review, never final denial. Unknown clinical interpretation goes to policy/adjudicator hold. No medical necessity inference is supported.'
# add rejection positive control using local previous eval copy, then replace identifiers and inputs
rej=copy=None
for e in d['stages']['evals']['items']:
 if e['data']['category']!='golden':continue
 b=json.loads(e['data']['input']);b['facts']['inpatient']=True;b['facts']['coverageFlag']='covered';b['policyRegistry']['versions'][0]['rules']['coverageFlag']='covered'
 for v in b['policyRegistry']['versions']:v['rules']['coverageFlag']='covered'
 e['data']['input']=json.dumps(b)
import copy
rej=copy.deepcopy(by['EV1']);rej['id']='EV26';rej['title']='Supported exclusion is only a proposed rejection';rej['description']='Self-contained positive control for human-reviewed rejection proposal, never insurer denial.';rej['data']['failureModeIds']=['FM10'];rej['data']['testSet']='HC1 synthetic guard suite v1; fixture EV26'
b=json.loads(rej['data']['input']);b['facts']['coverageFlag']='excluded';b['policyRegistry']['versions'][0]['rules']['coverageFlag']='excluded';b['documents'].append({'docId':'policy-clause','version':1,'hash':'placeholder','tenantId':'insurer-a','memberId':'member-1','page':1,'text':'HC1 synthetic exclusion: coverageFlag excluded means zero eligible for review.','ocrConfidence':1.0});rej['data']['input']=json.dumps(b)
rej['data']['expected']=json.dumps(dict(scope='internal assistance only',status='review_pending',coverage='recommend_reject',totalEligibleMinor=0,reason='EXPLICIT_EXCLUSION',ownerRole='adjudicator',externalPaymentCalls=0,externalDenialCalls=0));rej['data']['passRule']=json.dumps(dict(assertions=['status == review_pending','coverage == recommend_reject','totalEligibleMinor == 0','externalDenialCalls == 0','ownerRole == adjudicator'],compare='Exact equality; proposed rejection does not become final denial.'))
d['stages']['evals']['items'].insert(22,rej);by['EV26']=rej
canon=lambda x:json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False)
sha=lambda s:hashlib.sha256(s.encode()).hexdigest()
for e in d['stages']['evals']['items']:
 if e['data']['category']!='golden':continue
 b=json.loads(e['data']['input']);ex=json.loads(e['data']['expected'])
 # hashes represent actual JSON rules/text bytes, not fabricated external truth
 for doc in b['documents']:doc['hash']=sha(doc['text'])
 for v in b['policyRegistry']['versions']:v['hash']=sha(canon(v['rules']))
 pol=b['policyRegistry']['versions'][0]
 for m in b['orderedMocks']:
  if m['call']=='freshCommitChecks' and m.get('policyHash')=='sha256:synthetic-v1':m['policyHash']=pol['hash']
  elif m['call']=='freshCommitChecks' and m.get('policyHash')=='sha256:synthetic-v2':m['policyHash']=sha('changed-policy-after-calculation')
 # exact available document spans; deliberately missing or conflicting citations preserved by flags
 spans=[dict(docId=x['docId'],version=x['version'],page=1,start=0,end=len(x['text']),hash=x['hash']) for x in b['documents']]
 proposal={'status':'supported','facts':[{'field':k,'value':v,'citation':spans[-1] if k in ['admissionDate','dischargeDate','roomClass','inpatient'] else spans[0]} for k,v in b['facts'].items()],'coverage':'recommend_reject' if b['facts']['coverageFlag']=='excluded' else 'recommend_eligible','evidenceRefs':spans,'uncertainties':[],'explanation':'Synthetic HC1 coverage recommendation; exact amounts are supplied only by deterministic C4.'}
 for m in b['orderedMocks']:
  if m['call']=='model':m['payload']=proposal
 # source scalar values bind to literal normalized values, parser code can directly check all fields
 b['sourceNormalization']={'convention':'Synthetic field annotations are trusted test oracle only, not production input. Source spans reference full page and annotation fixture supplies normalized scalar mapping; original document strings remain evidence for numeric/date claims.','fields':b['facts'],'citationSpans':spans}
 b['operationCanonicalization']='UTF-8 JSON sorted object keys, compact separators, no ASCII escaping; SHA256 excludes digest field, includes opId/action/identity/expectedRevision and payload.'
 payload={'tenantId':b['case']['tenantId'],'memberId':b['case']['memberId'],'caseId':b['case']['caseId'],'expectedRevision':b['case']['revision'],'opId':'op-'+e['id'],'commandType':'disposition','payload':{'kind':ex.get('status','review_pending') if ex.get('status') in ['review_pending','hold_owned','cancelled'] else 'review_pending','reasonCode':ex.get('reason','OK'),'ownerRole':ex.get('ownerRole','adjudicator'),'packet':{'policyVersion':pol['id'],'policyHash':pol['hash'],'ledgerSequence':b['ledger']['sequence'],'totalEligibleMinor':ex.get('totalEligibleMinor',2500000),'currency':'INR','coverage':ex.get('coverage','recommend_eligible'),'evidenceHashes':[x['hash'] for x in b['documents']],'evidenceRefs':spans}}}
 if payload['payload']['kind'] in ['cancelled','hold_owned']:payload['payload'].pop('packet')
 b['persistEnvelope']=dict(payload=payload,digest=sha(canon(payload)),canonicalBytes=canon(payload))
 if e['id']=='EV17':b['persistEnvelope']['payload']['memberId']='member-2';b['persistEnvelope']['canonicalBytes']=canon(b['persistEnvelope']['payload']);b['persistRequest']['digestMatches']=False
 for m in b['orderedMocks']:
  if m['call']=='persist':m['opId']=payload['opId'];m['expectedDigest']=b['persistEnvelope']['digest']
  if m['call'] in ['lookupOperation','callback']:
   m['opId']=payload['opId'];m['digest']=b['persistEnvelope']['digest']
 e['data']['input']=json.dumps(b)
# link new test across risk/release and text
by['FM10']['data']['evalIds'].append('EV26')
for ev in ['EV23','EV25']:
 x=by[ev];x['description']+=' Include EV26 proposed-rejection control.';x['data']['passRule']+=' EV26 is also mandatory.'
 if ev=='EV25':
  inp=json.loads(x['data']['input']);inp['requiredGoldenIds'].append('EV26');x['data']['input']=json.dumps(inp)
by['X1']['data']['acceptanceCriteria'].append('EV26 verifies a supported exclusion yields a proposed rejection in review_pending with an adjudicator owner, never a final insurer denial.')
by['X1']['data']['buildInstructions']+=' Golden suite also includes EV26; canonical requiredGoldenIds is authoritative, so no added golden is omitted.'
(P/'design.json').write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
print('Round 1 recorded and design repaired')
