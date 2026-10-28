# Case journal, owner timers and status projection part 1

> PASS | DESIGN ONLY. self-review; round 2.

Depends on earlier milestones where their outputs are inputs below. Cross-milestone shared types are read by ID from ../design.json, not copied.

## Selected contracts

### C8 · Case journal, owner timers and status projection

Durable local transaction saves terminal status plus reason, ownerRole, ackDueAt/nextReadAt, operation linkage, receipt and audit. Statuses: COMPLETED, CANCELLED_PROPOSAL, OWNED_MANUAL, UNKNOWN_HELD. COMPLETED requires actual C6/C7 receipt and means ticket action recorded, never equipment repaired. Urgent and ordinary queue entries notify only internal configured console; out-of-hours delivery contract must be verified before launch. Owner ACK does not close case. Timer persists after operator logout, overdue changes owner to duty supervisor, then at another 2 urgent elapsed/30 routine staffed minutes escalate service manager console. Reconciliation outage also escalates IT operations. Manual outcomes are recorded resolution events; cannot fabricate ticket receipt. Unknown holds freeze fresh writes for same businessKey; watchdog creates W7 read-only reconciliation instance, never restarts W1. Before-send cancellation wins if CAS before journal MAY_HAVE_SENT; after that freeze and reconcile. Input reason mapping is exact upstream C1/C2/C3/C4/C5/C6 reason string; C7 NOT_COMMITTED maps WRITE_NOT_COMMITTED, UNKNOWN maps COMMIT_UNKNOWN, AUTH_DENIED maps RECOVERY_AUTH_DENIED, INVALID_CALLBACK maps INVALID_CALLBACK. W9/W10 explicitly dispatch failed finalization; their terminal projection nodes are idempotent no-op reads of already saved status. Urgent ackDueAt is intake.receivedAt + 2 elapsed minutes even when model/retrieval took time; routine due is queueCreatedAt + 30 staffed minutes using the frozen calendar version. Retention worker runs daily with data-owner-approved versioned H6 policy; removes restricted raw data at day 30 and recommendation snapshots at day 90, minimizes audit until day 365, emits deletion receipts. Unresolved operation IDs, immutable action payload/digest, approvals and receipt proof are not automatically purged while UNKNOWN_HELD; retention exception is visible to data owner for review. This evidence contains no reporter contact; real backup/legal-hold deletion behavior remains H6 verification dependency.

Reasoning: Chosen to make the stated workflow explicit and bounded.

Assumptions:

- H3: Each ticket write requires a currently authorized operator approval; tenant is city ID, and operation, resource, report revision, immutable payload digest and policy version are bound to approval.

- H4: Potential exposed wires, fallen poles, sparks or fire enter a staffed urgent manual queue immediately; proposed acknowledgement 2 elapsed minutes and supervisor escalation at 2 minutes; routine exceptions acknowledge within 30 staffed minutes and escalate at 30.

- H6: Proposed data policy: redact reporter contact before LLM use; raw local intake expires after 30 days, recommendation snapshots after 90 days, minimal audit receipts after 365 days; residency and legal retention require city approval.

- H10: Proposed operational limits: each read attempt 5 seconds, one read retry; LLM attempt 10 seconds with one retry; ticket write timeout 5 seconds with zero automatic write retry; reconciliation reads at 5, 30 and 120 seconds, then owned unknown hold with 15-minute read-only watchdog. Proposed additional limits: snapshot age at plan creation 60 seconds, plan/approval expiry 5 elapsed minutes, routine nonhuman response p95 30 seconds, and unknown-held >1 hour escalates service manager. These limits require verification, not established policy.

Data:

```json
{
  "group": "Code: human triggers",
  "taskIds": [
    "T8"
  ],
  "inputs": [
    "event:{caseId,expectedCaseVersion,disposition:COMPLETED|CANCELLED_PROPOSAL|OWNED_MANUAL|UNKNOWN_HELD,reason,ownerRole,operationId?,receipt?,urgency,cancelRequested}; required shape by disposition",
    "trustedClock:UTC; staffedCalendar:{id,version,intervals}; required",
    "case and operation journal current versions; required",
    "timing:{intakeReceivedAt:UTC,queueCreatedAt:UTC}; server-owned required for queue; retentionPolicy?:{version,approved:boolean,rawDays,snapshotDays,auditDays,legalHold}; required for scheduled purge"
  ],
  "outputs": [
    "terminal:{caseId,caseVersion,status:COMPLETED|CANCELLED_PROPOSAL|OWNED_MANUAL|UNKNOWN_HELD,reason,ownerRole,queueId?,ackDueAt?,nextReadAt?,receiptId?}; persisted",
    "timerResult:ACKNOWLEDGED|OVERDUE|ESCALATED|RECOVERY_SCHEDULED|NONE; durable",
    "audit:{actor,cityId,eventId,occurredAt,oldVersion,newVersion,operationId?,digest?,receiptId?}; append-only minimized",
    "persistResult:TERMINAL_SAVED|RECEIPT_MISSING|CANCEL_RACE|SAVE_FAILED; required. terminal required only TERMINAL_SAVED; other results retain safe pending journal and owner; retry local persistence transaction by event ID only.",
    "deletionReceipt?:{jobId,policyVersion,objectIds:string[],deletedAt:UTC,exceptionIds:string[]}; required retention job; no raw report text"
  ],
  "whyCode": "Owned status, conditional updates, clocks, durable receipts and escalation must remain deterministic and visible.",
  "approvalRule": "Local case access restricted by city/role. No work-order closure or equipment command. Real internal alert delivery is H4 integration dependency."
}
```


Sources:

- hypothesis / H3: Each ticket write requires a currently authorized operator approval; tenant is city ID, and operation, resource, report revision, immutable payload digest and policy version are bound to approval.

- hypothesis / H4: Potential exposed wires, fallen poles, sparks or fire enter a staffed urgent manual queue immediately; proposed acknowledgement 2 elapsed minutes and supervisor escalation at 2 minutes; routine exceptions acknowledge within 30 staffed minutes and escalate at 30.

- hypothesis / H6: Proposed data policy: redact reporter contact before LLM use; raw local intake expires after 30 days, recommendation snapshots after 90 days, minimal audit receipts after 365 days; residency and legal retention require city approval.

- hypothesis / H10: Proposed operational limits: each read attempt 5 seconds, one read retry; LLM attempt 10 seconds with one retry; ticket write timeout 5 seconds with zero automatic write retry; reconciliation reads at 5, 30 and 120 seconds, then owned unknown hold with 15-minute read-only watchdog. Proposed additional limits: snapshot age at plan creation 60 seconds, plan/approval expiry 5 elapsed minutes, routine nonhuman response p95 30 seconds, and unknown-held >1 hour escalates service manager. These limits require verification, not established policy.

## Workflow rules

### W8 · Persist owned manual disposition

{"state":"OWNED_MANUAL","guardBindings":{"reason":"upstream enum/reason mapped to case.reason:string","urgency":"C1.deterministicHazard OR C3.urgency POTENTIAL_HAZARD; missing upstream => routine except deterministic hazard"},"transitions":[],"failureDisposition":"If local queue save fails, do not claim handoff; block new intake and display IT incident + operator manual fallback.","timeout":"2s local persistence","retryPolicy":"0 effect retry beyond transactional event-id dedup","terminalDisposition":"Durable OWNED_MANUAL with owner, reason, calendar-bound due time, visible queue and escalation; manual resubmission requires new revision/plan/approval after any operation lock clears."}

Reasoning: Chosen to make the stated workflow explicit and bounded.

Assumptions:

- H3: Each ticket write requires a currently authorized operator approval; tenant is city ID, and operation, resource, report revision, immutable payload digest and policy version are bound to approval.

- H4: Potential exposed wires, fallen poles, sparks or fire enter a staffed urgent manual queue immediately; proposed acknowledgement 2 elapsed minutes and supervisor escalation at 2 minutes; routine exceptions acknowledge within 30 staffed minutes and escalate at 30.

- H10: Proposed operational limits: each read attempt 5 seconds, one read retry; LLM attempt 10 seconds with one retry; ticket write timeout 5 seconds with zero automatic write retry; reconciliation reads at 5, 30 and 120 seconds, then owned unknown hold with 15-minute read-only watchdog. Proposed additional limits: snapshot age at plan creation 60 seconds, plan/approval expiry 5 elapsed minutes, routine nonhuman response p95 30 seconds, and unknown-held >1 hour escalates service manager. These limits require verification, not established policy.

Data:

```json
{
  "componentId": "C8",
  "taskIds": [
    "T8"
  ],
  "next": [],
  "decision": false,
  "example": "NEEDS_LOCATION case owned by supervisor, no external write."
}
```


Sources:

- hypothesis / H3: Each ticket write requires a currently authorized operator approval; tenant is city ID, and operation, resource, report revision, immutable payload digest and policy version are bound to approval.

- hypothesis / H4: Potential exposed wires, fallen poles, sparks or fire enter a staffed urgent manual queue immediately; proposed acknowledgement 2 elapsed minutes and supervisor escalation at 2 minutes; routine exceptions acknowledge within 30 staffed minutes and escalate at 30.

- hypothesis / H10: Proposed operational limits: each read attempt 5 seconds, one read retry; LLM attempt 10 seconds with one retry; ticket write timeout 5 seconds with zero automatic write retry; reconciliation reads at 5, 30 and 120 seconds, then owned unknown hold with 15-minute read-only watchdog. Proposed additional limits: snapshot age at plan creation 60 seconds, plan/approval expiry 5 elapsed minutes, routine nonhuman response p95 30 seconds, and unknown-held >1 hour escalates service manager. These limits require verification, not established policy.

### W9 · Record ticket receipt completion

{"state":"FINALIZE_RECEIPT","guardBindings":{"persistResult":"C8.persistResult after receipt/city/digest checks and local transaction","terminal.status":"C8.terminal.status only when TERMINAL_SAVED","receipt":"C6/C7 durable matching receipt; required; no absence means completion","cancelRequested":"C8 journal boolean at finalization; if committed sets FOLLOWUP_REQUIRED without reversal"},"transitions":[{"to":"W12","when":"persistResult == TERMINAL_SAVED AND terminal.status == COMPLETED","mode":"exclusive"},{"to":"W11","when":"persistResult in [RECEIPT_MISSING,CANCEL_RACE]","mode":"exclusive"},{"to":"W8","when":"persistResult == SAVE_FAILED","mode":"exclusive"}],"failureDisposition":"Missing/mismatched receipt -> W11 owned unknown; local save failure -> W8 owned incident fallback. No completion emitted before persisted receipt.","timeout":"2s local persistence","retryPolicy":"transaction event-id dedup only; durable operation receipt can be recovered on restart","terminalDisposition":""}

Reasoning: Chosen to make the stated workflow explicit and bounded.

Assumptions:

- H3: Each ticket write requires a currently authorized operator approval; tenant is city ID, and operation, resource, report revision, immutable payload digest and policy version are bound to approval.

- H4: Potential exposed wires, fallen poles, sparks or fire enter a staffed urgent manual queue immediately; proposed acknowledgement 2 elapsed minutes and supervisor escalation at 2 minutes; routine exceptions acknowledge within 30 staffed minutes and escalate at 30.

- H10: Proposed operational limits: each read attempt 5 seconds, one read retry; LLM attempt 10 seconds with one retry; ticket write timeout 5 seconds with zero automatic write retry; reconciliation reads at 5, 30 and 120 seconds, then owned unknown hold with 15-minute read-only watchdog. Proposed additional limits: snapshot age at plan creation 60 seconds, plan/approval expiry 5 elapsed minutes, routine nonhuman response p95 30 seconds, and unknown-held >1 hour escalates service manager. These limits require verification, not established policy.

Data:

```json
{
  "componentId": "C8",
  "taskIds": [
    "T8"
  ],
  "next": [
    "W12",
    "W11",
    "W8"
  ],
  "decision": true,
  "example": "CREATE OP-9 ticket TK-101 receipt -> COMPLETED; lamp remains unverified."
}
```


Sources:

- hypothesis / H3: Each ticket write requires a currently authorized operator approval; tenant is city ID, and operation, resource, report revision, immutable payload digest and policy version are bound to approval.

- hypothesis / H4: Potential exposed wires, fallen poles, sparks or fire enter a staffed urgent manual queue immediately; proposed acknowledgement 2 elapsed minutes and supervisor escalation at 2 minutes; routine exceptions acknowledge within 30 staffed minutes and escalate at 30.

- hypothesis / H10: Proposed operational limits: each read attempt 5 seconds, one read retry; LLM attempt 10 seconds with one retry; ticket write timeout 5 seconds with zero automatic write retry; reconciliation reads at 5, 30 and 120 seconds, then owned unknown hold with 15-minute read-only watchdog. Proposed additional limits: snapshot age at plan creation 60 seconds, plan/approval expiry 5 elapsed minutes, routine nonhuman response p95 30 seconds, and unknown-held >1 hour escalates service manager. These limits require verification, not established policy.

## Required tests

For each ID below, load ../eval-set.json items[id].data.input, .expected and .passRule. These are the full fixture, expected result and exact assertions; no inherited test context is assumed.

- EV1: Valid CREATE positive control
- EV2: Immediate deterministic hazard despite missing location
- EV4: Contradictory location retained as human case
- EV6: Valid operator-selected LINK positive control
- EV11: Injection cannot invoke equipment or fabricate target
- EV12: Lost commit recovered after session expiry and duplicate callback
- EV13: Unknown effect remains locked during cancellation/change
- EV14: Urgent queue escalates after logout
- EV15: Model-detected oblique hazard reaches urgent owner
- EV17: Context outage persists owned report without guessing
- EV18: Privacy redaction and proposed retention controls
- EV21: Cancellation before send has no ticket effect
- EV19: Offline judgement and staffed response validation
- EV20: Full release and live invariant gates
- EV22: Online safety, queue, drift and cost observation
- EV23: Urgent provisional intake without asset or address
- EV24: Routine owner deadline uses staffed calendar
- EV26: Invalid model output exhausted into owned fallback
- EV27: Direct equipment command blocked before transport
## Acceptance criteria

- Implement these exact branch rules and all named eval assertions. No equipment controls.
