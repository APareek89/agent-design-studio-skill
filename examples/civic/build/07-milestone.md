# Read-only commit reconciler part 1

> PASS | DESIGN ONLY. self-review; round 2.

Depends on earlier milestones where their outputs are inputs below. Cross-milestone shared types are read by ID from ../design.json, not copied.

## Selected contracts

### C7 · Read-only commit reconciler

Proposed GET operation(cityId,operationId,businessKey) with service reconciliation identity independent of caller session. Read at 5/30/120s; durable callback and watchdog use same operation/city/digest, deduplicate callback eventId. Returns COMMITTED with receipt, NOT_COMMITTED only with authoritative final noncommit + released uniqueness reservation, UNKNOWN, or AUTH_DENIED. Not-found alone is UNKNOWN until ledger proves final noncommit. 15-minute watchdog retries read-only after unknown hold and alerts IT; no elapsed timeout means permission to write again. Changed intent/cancel is recorded but frozen while unknown. On receipt, cancel becomes follow-up-required; ticket cancellation/correction is outside scope and separately authorized manually. For BUSINESS_KEY_EXISTS recover the authoritative winning operation/plan/digest, not the losing proposal; any different intended action remains unapplied with supervisor follow-up.

Reasoning: Chosen to make the stated workflow explicit and bounded.

Assumptions:

- H2: A city-scoped ticket ledger, GIS asset registry and versioned crew routing table can provide read APIs; create-ticket and attach-report commands require a verified adapter.

- H3: Each ticket write requires a currently authorized operator approval; tenant is city ID, and operation, resource, report revision, immutable payload digest and policy version are bound to approval.

- H10: Proposed operational limits: each read attempt 5 seconds, one read retry; LLM attempt 10 seconds with one retry; ticket write timeout 5 seconds with zero automatic write retry; reconciliation reads at 5, 30 and 120 seconds, then owned unknown hold with 15-minute read-only watchdog. Proposed additional limits: snapshot age at plan creation 60 seconds, plan/approval expiry 5 elapsed minutes, routine nonhuman response p95 30 seconds, and unknown-held >1 hour escalates service manager. These limits require verification, not established policy.

Data:

```json
{
  "group": "Code: tools",
  "taskIds": [
    "T7"
  ],
  "inputs": [
    "journal:C6.journal with state=MAY_HAVE_SENT; required",
    "reconcileIdentity:{cityId,scope:operations.read,expiresAt}; service credential refresh independent of operator",
    "callback?:{eventId,operationId,cityId,payloadDigest,receipt,signature}; verify and dedup if supplied"
  ],
  "outputs": [
    "reconcileResult:COMMITTED|NOT_COMMITTED|UNKNOWN|AUTH_DENIED|INVALID_CALLBACK; required",
    "receipt:C6.receipt; required COMMITTED, must match city/businessKey/digest",
    "recovery:{attempt:int[1..3],cancelRequested:boolean,ownerRole:string,nextReadAt?:UTC,status:RECOVERED|SAFE_NOT_COMMITTED|UNKNOWN_HELD}; durable"
  ],
  "whyCode": "Unknown external effect requires durable readback rather than a second possibly duplicate write.",
  "approvalRule": "Read-only scoped recovery credential; follow-up writes require new plan and approval after final noncommit proof."
}
```


Sources:

- hypothesis / H2: A city-scoped ticket ledger, GIS asset registry and versioned crew routing table can provide read APIs; create-ticket and attach-report commands require a verified adapter.

- hypothesis / H3: Each ticket write requires a currently authorized operator approval; tenant is city ID, and operation, resource, report revision, immutable payload digest and policy version are bound to approval.

- hypothesis / H10: Proposed operational limits: each read attempt 5 seconds, one read retry; LLM attempt 10 seconds with one retry; ticket write timeout 5 seconds with zero automatic write retry; reconciliation reads at 5, 30 and 120 seconds, then owned unknown hold with 15-minute read-only watchdog. Proposed additional limits: snapshot age at plan creation 60 seconds, plan/approval expiry 5 elapsed minutes, routine nonhuman response p95 30 seconds, and unknown-held >1 hour escalates service manager. These limits require verification, not established policy.

## Workflow rules

### W7 · Reconcile uncertain commit

{"state":"RECONCILE","guardBindings":{"reconcileResult":"C7 enum after bounded read schedule; callback invalidity cannot substitute for final authoritative committed proof"},"transitions":[{"to":"W9","when":"reconcileResult == COMMITTED","mode":"exclusive"},{"to":"W8","when":"reconcileResult == NOT_COMMITTED","mode":"exclusive"},{"to":"W11","when":"reconcileResult in [UNKNOWN,AUTH_DENIED,INVALID_CALLBACK]","mode":"exclusive"}],"failureDisposition":"Invalid callback has no effect; continue scheduled authoritative reads, then UNKNOWN_HELD. NOT_COMMITTED requires final proof and a new separately approved attempt, never an automatic action.","timeout":"reads at 5,30,120 seconds from write timeout","retryPolicy":"3 reads per instance; watchdog only read-only W7 resume every 15m while unresolved","terminalDisposition":""}

Reasoning: Chosen to make the stated workflow explicit and bounded.

Assumptions:

- H3: Each ticket write requires a currently authorized operator approval; tenant is city ID, and operation, resource, report revision, immutable payload digest and policy version are bound to approval.

- H4: Potential exposed wires, fallen poles, sparks or fire enter a staffed urgent manual queue immediately; proposed acknowledgement 2 elapsed minutes and supervisor escalation at 2 minutes; routine exceptions acknowledge within 30 staffed minutes and escalate at 30.

- H10: Proposed operational limits: each read attempt 5 seconds, one read retry; LLM attempt 10 seconds with one retry; ticket write timeout 5 seconds with zero automatic write retry; reconciliation reads at 5, 30 and 120 seconds, then owned unknown hold with 15-minute read-only watchdog. Proposed additional limits: snapshot age at plan creation 60 seconds, plan/approval expiry 5 elapsed minutes, routine nonhuman response p95 30 seconds, and unknown-held >1 hour escalates service manager. These limits require verification, not established policy.

Data:

```json
{
  "componentId": "C7",
  "taskIds": [
    "T7"
  ],
  "next": [
    "W9",
    "W8",
    "W11"
  ],
  "decision": true,
  "example": "Operation OP-9 recovered after operator session expiry -> W9."
}
```


Sources:

- hypothesis / H3: Each ticket write requires a currently authorized operator approval; tenant is city ID, and operation, resource, report revision, immutable payload digest and policy version are bound to approval.

- hypothesis / H4: Potential exposed wires, fallen poles, sparks or fire enter a staffed urgent manual queue immediately; proposed acknowledgement 2 elapsed minutes and supervisor escalation at 2 minutes; routine exceptions acknowledge within 30 staffed minutes and escalate at 30.

- hypothesis / H10: Proposed operational limits: each read attempt 5 seconds, one read retry; LLM attempt 10 seconds with one retry; ticket write timeout 5 seconds with zero automatic write retry; reconciliation reads at 5, 30 and 120 seconds, then owned unknown hold with 15-minute read-only watchdog. Proposed additional limits: snapshot age at plan creation 60 seconds, plan/approval expiry 5 elapsed minutes, routine nonhuman response p95 30 seconds, and unknown-held >1 hour escalates service manager. These limits require verification, not established policy.

## Required tests

For each ID below, load ../eval-set.json items[id].data.input, .expected and .passRule. These are the full fixture, expected result and exact assertions; no inherited test context is assumed.

- EV12: Lost commit recovered after session expiry and duplicate callback
- EV13: Unknown effect remains locked during cancellation/change
- EV20: Full release and live invariant gates
- EV22: Online safety, queue, drift and cost observation
## Acceptance criteria

- Implement these exact branch rules and all named eval assertions. No equipment controls.
