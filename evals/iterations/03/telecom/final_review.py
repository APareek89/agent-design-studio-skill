import json,pathlib
p=pathlib.Path(__file__).parent;r=json.loads((p/'review-round-2.json').read_text());r['round']=3;r['status']='pass'
for i in r['issues']:i['resolved']=True
proof={
'D1':'CTX1 and T0/T3 sequence/choice cover active-service investigation, outage credit, supervisor, cancellation and owned unknown outcomes; cash payouts and network repair excluded.',
'D2':'Every leaf T1,T2,T3.1,T3.2,T3.3,T4 is served by C/W and goldens. FM1-FM9 links derive from EV1-EV23 and are reciprocal. Source brief exact quote; H1-H6 separate proposed policies and adapters.',
'D3':'W6 durable timers, W5 notice scheduling, W7 actual send, W10 all unknown paths reconcile, same-key one retry after final absence; W14 proof before W15; W16 owned unresolved terminal. EV6 now CREDITED plus cancellation flag.',
'D4':'C1-C9 define scope/evidence/status fields, required immutable command content, write response enums, 5s adapter deadlines, durable queue acknowledgement/escalation and read-only lookup beyond session.',
'D5':'C1 and C7 scope/active joins precede private reads and credit. C4 exact approved command, C7 fresh versions/authority and atomic uniqueness; C3 has explanation-only output with citation verification. H4 privacy is explicit launch gate.',
'D6':'H1-H4/H6 block launch on unverified policy, integration, staffing, privacy and notice evidence. H5/M1 illustrative volume/prices and all fixtures synthetic. Missing/conflicting records yield owned investigation.',
'D7':'F1 rejects open-ended/synchronous chain for durable code state machine; same comparison criteria persistence/timers/dedup/authority/recovery. F2 scopes principals; F3 compares relational/evidence/audit patterns across cloud/open-source as unverified candidates.',
'D8':'One M1 matches C3/W3. 2400*1/1e6+450*4/1e6=.0042 USD/call, <=.9 calls gives .00378/case and <=37.80/10000 cases; worst one call. No retries, timeout fallback, fine-tune only after labeled held-out improvement.',
'D9':'FM1-FM9 are case-specific with hypothetical S/O/D, actionable owners, gates and objective metrics. High severity and high RPN have no invented acceptance; guard failures tie to actual scoped tests.',
'D10':'EV1 valid arithmetic, EV2 wrong customer, EV3/14 stale/revoked, EV4 two concurrent operations, EV5/20 conflict/invented citation, EV6/16 uncertain/logout/cancel, EV7 proof failure, EV8 48h queue, EV9 missing policy, EV10/11/15 notices, EV12 cap overflow, EV13 signed supervisor, EV17 cancel, EV18 inactive, EV19 speed. Self-contained inputs and expected effects; EV21-EV23 explicitly release all 20 goldens.',
'D11':'R1 denominators/windows and censored resolution, R2 non-circular Shadow/Assist/Pilot/Scale gates and stop/reconcile policy, R3 account randomization and binary/log-hours sample-size methods, R4 proposed accountable role sign-offs.',
'D12':'X1 preserves exact C/W boundaries and shared state ownership; four milestones cover all components and linked tests. Full fixtures indexed outside build packets. No claim of executing business controls or receiving policy approval.'}
r['dimensions']=[{'id':k,'score':3,'evidence':[v]} for k,v in proof.items()]
r['limitations']=['Self-review by author, not independent review or stakeholder approval.','Structural and semantic declarations passed helper; goldens are specifications, no business harness or real API tests ran.','H1-H4,H6 remain launch blockers; policy legality, API support, continuous staffing and actual vendor performance have not been verified.','PDF rendering and visual layout inspection are delegated to root and are not claimed complete in this source-only subtask.']
(p/'review-round-3.json').write_text(json.dumps(r,indent=2));(p/'review.json').write_text(json.dumps(r,indent=2))
