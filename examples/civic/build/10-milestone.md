# Case journal, owner timers and status projection part 3

> PASS | DESIGN ONLY. self-review; round 2.

Depends on earlier milestones where their outputs are inputs below. Cross-milestone shared types are read by ID from ../design.json, not copied.

## Selected contracts

Exact shared C8 contract: [08-milestone.md](08-milestone.md). Load that contract before this part; it is unchanged.

## Workflow rules

### W12 · Project durable ticket receipt

{"state":"COMPLETED","guardBindings":{"terminal":"C8 already persisted terminal by eventId and case version"},"transitions":[],"failureDisposition":"Projection read unavailable: show pending status and IT incident, never fabricate completion/cancellation. Durable underlying status recoverable by case read.","timeout":"2s local read","retryPolicy":"one local read retry; no ticket mutation","terminalDisposition":"COMPLETED only for matching persisted ticket/link receipt; if cancelRequested true display FOLLOWUP_REQUIRED and supervisor owner, never mark equipment repaired."}

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
  "example": "Read saved TK-101 receipt and present ticket action recorded."
}
```


Sources:

- hypothesis / H3: Each ticket write requires a currently authorized operator approval; tenant is city ID, and operation, resource, report revision, immutable payload digest and policy version are bound to approval.

- hypothesis / H4: Potential exposed wires, fallen poles, sparks or fire enter a staffed urgent manual queue immediately; proposed acknowledgement 2 elapsed minutes and supervisor escalation at 2 minutes; routine exceptions acknowledge within 30 staffed minutes and escalate at 30.

- hypothesis / H10: Proposed operational limits: each read attempt 5 seconds, one read retry; LLM attempt 10 seconds with one retry; ticket write timeout 5 seconds with zero automatic write retry; reconciliation reads at 5, 30 and 120 seconds, then owned unknown hold with 15-minute read-only watchdog. Proposed additional limits: snapshot age at plan creation 60 seconds, plan/approval expiry 5 elapsed minutes, routine nonhuman response p95 30 seconds, and unknown-held >1 hour escalates service manager. These limits require verification, not established policy.

### W13 · Project durable proposal cancellation

{"state":"CANCELLED_PROPOSAL","guardBindings":{"terminal":"C8 already persisted terminal by eventId and case version"},"transitions":[],"failureDisposition":"Projection read unavailable: show pending status and IT incident, never fabricate completion/cancellation. Durable underlying status recoverable by case read.","timeout":"2s local read","retryPolicy":"one local read retry; no ticket mutation","terminalDisposition":"CANCELLED_PROPOSAL only after saved no-send CAS; original intake audit retained."}

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
  "example": "No action sent; show proposal cancelled."
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
