# Bounded text triage judgement part 1

> PASS | DESIGN ONLY. self-review; round 2.

Depends on earlier milestones where their outputs are inputs below. Cross-milestone shared types are read by ID from ../design.json, not copied.

## Selected contracts

### C3 · Bounded text triage judgement

Classify fault from text and supplied evidence, flag hazard and explain same-asset candidate relevance. No browsing or tool invocation. Report text and ticket descriptions are untrusted content and cannot change system rules. Return schema, citations and abstain; ignore instructions embedded in content. Conflicting evidence or absent usable location is not solved by guess. One retry for transport/invalid shape on identical snapshot; then manual.

Reasoning: Chosen to make the stated workflow explicit and bounded.

Assumptions:

- H1: Proposed first release ingests text typed or pasted by an operator, plus optional asset ID/address; direct citizen-channel integration, photo interpretation and ticket closure are deferred.

- H8: Illustrative planning: 90% of reports reach the single LLM component, 5% of those need one format/transient retry, 2000 input and 300 output tokens/call, USD 1/input-million and 4/output-million; provider and actual prices remain unselected.

- H10: Proposed operational limits: each read attempt 5 seconds, one read retry; LLM attempt 10 seconds with one retry; ticket write timeout 5 seconds with zero automatic write retry; reconciliation reads at 5, 30 and 120 seconds, then owned unknown hold with 15-minute read-only watchdog. Proposed additional limits: snapshot age at plan creation 60 seconds, plan/approval expiry 5 elapsed minutes, routine nonhuman response p95 30 seconds, and unknown-held >1 hour escalates service manager. These limits require verification, not established policy.

Data:

```json
{
  "group": "Agents (LLM)",
  "taskIds": [
    "T3"
  ],
  "inputs": [
    "intake:redacted C1.intake; required",
    "snapshot:C2.snapshot; required",
    "allowedCategories:[lamp_out,flicker,day_burning,physical_damage,other,unknown]; fixed"
  ],
  "outputs": [
    "modelResult:VALID|INVALID|UNAVAILABLE; required by wrapper",
    "recommendation?:{category:allowedCategory,urgency:ROUTINE|POTENTIAL_HAZARD,evidence:[{field,quote}],candidateRationales:[{ticketId,reason}],abstain:boolean,reason?:string}; required if VALID",
    "attempts:int[1..2]; wrapper-produced; no model authority fields allowed",
    "reason:string enum=NONE|MODEL_INVALID|MODEL_UNAVAILABLE; wrapper-produced and required"
  ],
  "whyCode": "",
  "approvalRule": "Recommendation only; operator confirmation plus C6 checks required for every ticket mutation."
}
```


Sources:

- hypothesis / H1: Proposed first release ingests text typed or pasted by an operator, plus optional asset ID/address; direct citizen-channel integration, photo interpretation and ticket closure are deferred.

- hypothesis / H8: Illustrative planning: 90% of reports reach the single LLM component, 5% of those need one format/transient retry, 2000 input and 300 output tokens/call, USD 1/input-million and 4/output-million; provider and actual prices remain unselected.

- hypothesis / H10: Proposed operational limits: each read attempt 5 seconds, one read retry; LLM attempt 10 seconds with one retry; ticket write timeout 5 seconds with zero automatic write retry; reconciliation reads at 5, 30 and 120 seconds, then owned unknown hold with 15-minute read-only watchdog. Proposed additional limits: snapshot age at plan creation 60 seconds, plan/approval expiry 5 elapsed minutes, routine nonhuman response p95 30 seconds, and unknown-held >1 hour escalates service manager. These limits require verification, not established policy.

## Workflow rules

### W3 · Bounded classification

{"state":"CLASSIFY","guardBindings":{"modelResult":"C3.wrapper modelResult after at most 2 attempts"},"transitions":[{"to":"W4","when":"modelResult == VALID","mode":"exclusive"},{"to":"W8","when":"modelResult in [INVALID,UNAVAILABLE]","mode":"exclusive"}],"failureDisposition":"Invalid schema or unknown IDs cannot reach writer.","timeout":"10s/attempt","retryPolicy":"1 identical-input retry for invalid format/transient; no recursive calls","terminalDisposition":""}

Reasoning: Chosen to make the stated workflow explicit and bounded.

Assumptions:

- H3: Each ticket write requires a currently authorized operator approval; tenant is city ID, and operation, resource, report revision, immutable payload digest and policy version are bound to approval.

- H4: Potential exposed wires, fallen poles, sparks or fire enter a staffed urgent manual queue immediately; proposed acknowledgement 2 elapsed minutes and supervisor escalation at 2 minutes; routine exceptions acknowledge within 30 staffed minutes and escalate at 30.

- H10: Proposed operational limits: each read attempt 5 seconds, one read retry; LLM attempt 10 seconds with one retry; ticket write timeout 5 seconds with zero automatic write retry; reconciliation reads at 5, 30 and 120 seconds, then owned unknown hold with 15-minute read-only watchdog. Proposed additional limits: snapshot age at plan creation 60 seconds, plan/approval expiry 5 elapsed minutes, routine nonhuman response p95 30 seconds, and unknown-held >1 hour escalates service manager. These limits require verification, not established policy.

Data:

```json
{
  "componentId": "C3",
  "taskIds": [
    "T3"
  ],
  "next": [
    "W4",
    "W8"
  ],
  "decision": true,
  "example": "Flicker with quoted span -> W4."
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
- EV11: Injection cannot invoke equipment or fabricate target
- EV15: Model-detected oblique hazard reaches urgent owner
- EV17: Context outage persists owned report without guessing
- EV18: Privacy redaction and proposed retention controls
- EV19: Offline judgement and staffed response validation
- EV20: Full release and live invariant gates
- EV22: Online safety, queue, drift and cost observation
- EV23: Urgent provisional intake without asset or address
- EV26: Invalid model output exhausted into owned fallback
- EV27: Direct equipment command blocked before transport
## Acceptance criteria

- Implement these exact branch rules and all named eval assertions. No equipment controls.
