# Operator decision queue part 1

> PASS | DESIGN ONLY. self-review; round 2.

Depends on earlier milestones where their outputs are inputs below. Cross-milestone shared types are read by ID from ../design.json, not copied.

## Selected contracts

### C5 · Operator decision queue

Persist proposal in city routine review queue; assigned operator ACK deadline 30 staffed minutes then supervisor takes ownership. Hazard is separate urgent manual queue; no approval path auto-dispatches hazard. Events ACK, APPROVE, REJECT, CANCEL, OVERDUE are signed by identity service and server timed. APPROVE binds exact immutable plan/digest plus actor, city, action, resource (asset for CREATE, ticket for LINK), report revision, policy/crew versions, expiresAt and decisionId. Show all action-critical fields and provenance. Any edit produces a new plan/approval. Reject/cancel retains intake audit; no citizen message. A timer job survives caller closure. Routine acknowledgement due time starts at durable queueCreatedAt; plan expiry uses trusted createdAt. Acknowledgement neither authorizes a write nor resets plan expiry.

Reasoning: Chosen to make the stated workflow explicit and bounded.

Assumptions:

- H3: Each ticket write requires a currently authorized operator approval; tenant is city ID, and operation, resource, report revision, immutable payload digest and policy version are bound to approval.

- H4: Potential exposed wires, fallen poles, sparks or fire enter a staffed urgent manual queue immediately; proposed acknowledgement 2 elapsed minutes and supervisor escalation at 2 minutes; routine exceptions acknowledge within 30 staffed minutes and escalate at 30.

Data:

```json
{
  "group": "Code: human triggers",
  "taskIds": [
    "T5"
  ],
  "inputs": [
    "plan:C4.plan; required",
    "event:{kind:ACK|APPROVE|REJECT|CANCEL|OVERDUE,caseId,expectedCaseVersion,actorId?,planId?,planVersion?,payloadDigest?,decisionId?,serverAt:UTC}; APPROVE requires all optional identity/plan fields",
    "currentClaims:{cityId,actorId,roles,revoked:boolean}; live on APPROVE"
  ],
  "outputs": [
    "decisionResult:APPROVED|REJECTED|CANCELLED|OVERDUE|AUTH_DENIED|STALE|WAITING; required",
    "approval?:{approvalId,decisionId,actorId,cityId,planId,planVersion,payloadDigest,action,resourceId,reportRevision,policyVersion,crewVersion,issuedAt,expiresAt}; required on APPROVED",
    "queueReceipt:{queueId,caseId,ownerRole,queueCreatedAt,ackDueAt,status,caseVersion}; durable on every result",
    "reason:string enum=NONE|OPERATOR_REJECTED|APPROVAL_OVERDUE|AUTH_DENIED|STALE_APPROVAL|CANCELLED_BEFORE_SEND; required"
  ],
  "whyCode": "Human events, deadlines and authority binding require deterministic validation.",
  "approvalRule": "APPROVE only current city operator role under H3; supervisor can review but cannot override equipment exclusion or API guards."
}
```


Sources:

- hypothesis / H3: Each ticket write requires a currently authorized operator approval; tenant is city ID, and operation, resource, report revision, immutable payload digest and policy version are bound to approval.

- hypothesis / H4: Potential exposed wires, fallen poles, sparks or fire enter a staffed urgent manual queue immediately; proposed acknowledgement 2 elapsed minutes and supervisor escalation at 2 minutes; routine exceptions acknowledge within 30 staffed minutes and escalate at 30.

## Workflow rules

### W5 · Await payload-bound human decision

{"state":"WAIT_APPROVAL","guardBindings":{"decisionResult":"C5.decisionResult; WAITING resumes same durable wait until event/deadline"},"transitions":[{"to":"W6","when":"decisionResult == APPROVED","mode":"exclusive"},{"to":"W10","when":"decisionResult == CANCELLED","mode":"exclusive"},{"to":"W8","when":"decisionResult in [REJECTED,OVERDUE,AUTH_DENIED,STALE]","mode":"exclusive"}],"failureDisposition":"WAITING is persisted suspension, not a transition. ACK extends no approval expiry.","timeout":"30 staffed minutes ACK deadline; plan expiry 5 elapsed minutes independently enforced","retryPolicy":"0 automatic approval; OVERDUE yields W8","terminalDisposition":""}

Reasoning: Chosen to make the stated workflow explicit and bounded.

Assumptions:

- H3: Each ticket write requires a currently authorized operator approval; tenant is city ID, and operation, resource, report revision, immutable payload digest and policy version are bound to approval.

- H4: Potential exposed wires, fallen poles, sparks or fire enter a staffed urgent manual queue immediately; proposed acknowledgement 2 elapsed minutes and supervisor escalation at 2 minutes; routine exceptions acknowledge within 30 staffed minutes and escalate at 30.

- H10: Proposed operational limits: each read attempt 5 seconds, one read retry; LLM attempt 10 seconds with one retry; ticket write timeout 5 seconds with zero automatic write retry; reconciliation reads at 5, 30 and 120 seconds, then owned unknown hold with 15-minute read-only watchdog. Proposed additional limits: snapshot age at plan creation 60 seconds, plan/approval expiry 5 elapsed minutes, routine nonhuman response p95 30 seconds, and unknown-held >1 hour escalates service manager. These limits require verification, not established policy.

Data:

```json
{
  "componentId": "C5",
  "taskIds": [
    "T5"
  ],
  "next": [
    "W6",
    "W10",
    "W8"
  ],
  "decision": true,
  "example": "APPROVE PL-1 digest -> W6; edit -> stale plan, W8."
}
```


Sources:

- hypothesis / H3: Each ticket write requires a currently authorized operator approval; tenant is city ID, and operation, resource, report revision, immutable payload digest and policy version are bound to approval.

- hypothesis / H4: Potential exposed wires, fallen poles, sparks or fire enter a staffed urgent manual queue immediately; proposed acknowledgement 2 elapsed minutes and supervisor escalation at 2 minutes; routine exceptions acknowledge within 30 staffed minutes and escalate at 30.

- hypothesis / H10: Proposed operational limits: each read attempt 5 seconds, one read retry; LLM attempt 10 seconds with one retry; ticket write timeout 5 seconds with zero automatic write retry; reconciliation reads at 5, 30 and 120 seconds, then owned unknown hold with 15-minute read-only watchdog. Proposed additional limits: snapshot age at plan creation 60 seconds, plan/approval expiry 5 elapsed minutes, routine nonhuman response p95 30 seconds, and unknown-held >1 hour escalates service manager. These limits require verification, not established policy.

## Required tests

For each ID below, load ../eval-set.json items[id].data.input, .expected and .passRule. These are the full fixture, expected result and exact assertions; no inherited test context is assumed.

- EV1: Valid CREATE positive control
- EV6: Valid operator-selected LINK positive control
- EV7: Revoked actor denied at commit
- EV8: Changed routing policy invalidates approval
- EV9: Concurrent ticket edit rejects stale LINK
- EV10: Payload tampering fails digest binding
- EV14: Urgent queue escalates after logout
- EV16: LINK rejects forbidden CREATE fields even with valid digest
- EV21: Cancellation before send has no ticket effect
- EV19: Offline judgement and staffed response validation
- EV20: Full release and live invariant gates
- EV22: Online safety, queue, drift and cost observation
- EV24: Routine owner deadline uses staffed calendar
- EV25: Closed candidate cannot receive new report
## Acceptance criteria

- Implement these exact branch rules and all named eval assertions. No equipment controls.
