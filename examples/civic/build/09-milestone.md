# Case journal, owner timers and status projection part 2

> PASS | DESIGN ONLY. self-review; round 2.

Depends on earlier milestones where their outputs are inputs below. Cross-milestone shared types are read by ID from ../design.json, not copied.

## Selected contracts

Exact shared C8 contract: [08-milestone.md](08-milestone.md). Load that contract before this part; it is unchanged.

## Workflow rules

### W10 · Record proposal cancellation

{"state":"FINALIZE_CANCEL","guardBindings":{"persistResult":"C8 cancellation CAS result; TERMINAL_SAVED only before any MAY_HAVE_SENT","terminal.status":"C8.terminal.status only when saved"},"transitions":[{"to":"W13","when":"persistResult == TERMINAL_SAVED AND terminal.status == CANCELLED_PROPOSAL","mode":"exclusive"},{"to":"W11","when":"persistResult == CANCEL_RACE","mode":"exclusive"},{"to":"W8","when":"persistResult in [SAVE_FAILED,RECEIPT_MISSING]","mode":"exclusive"}],"failureDisposition":"Lost cancellation CAS -> W11; local save failure -> W8 incident fallback. No external-cancellation claim.","timeout":"2s local persistence","retryPolicy":"transaction dedup only","terminalDisposition":""}

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
    "W13",
    "W11",
    "W8"
  ],
  "decision": true,
  "example": "Cancel in W5 before send -> cancelled proposal."
}
```


Sources:

- hypothesis / H3: Each ticket write requires a currently authorized operator approval; tenant is city ID, and operation, resource, report revision, immutable payload digest and policy version are bound to approval.

- hypothesis / H4: Potential exposed wires, fallen poles, sparks or fire enter a staffed urgent manual queue immediately; proposed acknowledgement 2 elapsed minutes and supervisor escalation at 2 minutes; routine exceptions acknowledge within 30 staffed minutes and escalate at 30.

- hypothesis / H10: Proposed operational limits: each read attempt 5 seconds, one read retry; LLM attempt 10 seconds with one retry; ticket write timeout 5 seconds with zero automatic write retry; reconciliation reads at 5, 30 and 120 seconds, then owned unknown hold with 15-minute read-only watchdog. Proposed additional limits: snapshot age at plan creation 60 seconds, plan/approval expiry 5 elapsed minutes, routine nonhuman response p95 30 seconds, and unknown-held >1 hour escalates service manager. These limits require verification, not established policy.

### W11 · Hold unknown effect with owner

{"state":"UNKNOWN_HELD","guardBindings":{"operationId":"C6.journal persisted before send","nextReadAt":"C8 trustedClock + H10 interval; C7 service credential is independent of operator session"},"transitions":[],"failureDisposition":"Recovery authority unavailable => IT owner alert and same write lock remains.","timeout":"2s local persistence","retryPolicy":"15-minute durable watchdog creates only W7 read instance; no second write; no expiry on unknown lock","terminalDisposition":"UNKNOWN_HELD durable supervisor/IT ownership, operationId, nextReadAt and immutable intent; cancellation stored as pending and changed intent frozen."}

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
  "example": "No OP-9 final proof after 3 reads -> hold; future watchdog reconciles."
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
