# Route resolver and immutable plan validator part 1

> PASS | DESIGN ONLY. self-review; round 2.

Depends on earlier milestones where their outputs are inputs below. Cross-milestone shared types are read by ID from ../design.json, not copied.

## Selected contracts

### C4 · Route resolver and immutable plan validator

Code checks model evidence quotes against input and candidate IDs against snapshot. Any hazard from C1 or C3 wins precedence; no automatic down-ranking. Missing/contradictory location, abstain, other/unknown category, unavailable crew, stale snapshots or semantic duplicates require owned operator review. With exact asset and routine category map policy rules to one eligible crew. Present CREATE draft and candidate LINK choices; when operator selects LINK construct a new immutable plan. CREATE creates one new ticket; LINK appends a report reference only to an open same-asset ticket, preserves existing assignment. Closed tickets and different faults need supervisor deciding CREATE under current policy. No fuzzy merging. Payload uses canonical UTF-8 JSON, sorted object keys, compact separators, integers/strings, no floats, SHA-256 digest.

Reasoning: Chosen to make the stated workflow explicit and bounded.

Assumptions:

- H3: Each ticket write requires a currently authorized operator approval; tenant is city ID, and operation, resource, report revision, immutable payload digest and policy version are bound to approval.

- H5: Suggested duplicates require operator selection of an existing ticket on the same asset; fuzzy similarity never merges or suppresses reports. Existing ticket links do not change crew assignment or close work.

- H7: Proposed routing uses a versioned GIS boundary, asset ownership, fault category and crew capability/on-duty table; unresolved boundary, unavailable crew or conflicting asset evidence goes to supervisor.

Data:

```json
{
  "group": "Code: validation",
  "taskIds": [
    "T4"
  ],
  "inputs": [
    "intake:C1.intake; snapshot:C2.snapshot; recommendation:C3.recommendation; all required",
    "selection?:{kind:CREATE}|{kind:LINK,ticketId:string}; chosen by operator if candidate exists",
    "now:UTC from trusted server clock; required; snapshotMaxAgeSeconds:int=60 proposed"
  ],
  "outputs": [
    "planResult:READY|URGENT|NEEDS_LOCATION|AMBIGUOUS|UNSUPPORTED|NO_CREW|STALE|INVALID; required",
    "plan?:{planId:string,version:int,cityId:string,caseId:string,caseVersion:int,reportRevision:int,policyVersion:string,crewVersion:string,payload:CreatePayload|LinkPayload,payloadDigest:hex,createdAt:UTC,expiresAt:UTC}; if READY",
    "CreatePayload:{kind:CREATE,cityId,caseId,intakeId,reportRevision,assetId,category,crewId,policyVersion,crewVersion}; all required",
    "LinkPayload:{kind:LINK,cityId,caseId,intakeId,reportRevision,assetId,ticketId,expectedTicketVersion:int,policyVersion,crewVersion}; all required; crewId/category forbidden",
    "reason:string enum=NONE|POTENTIAL_HAZARD|NEEDS_LOCATION|AMBIGUOUS_ASSET|AMBIGUOUS_DUPLICATE|UNSUPPORTED_CATEGORY|NO_CREW|STALE_SNAPSHOT|INVALID_MODEL_REFERENCE|INVALID_EVIDENCE|INVALID_PAYLOAD; required"
  ],
  "whyCode": "Policy mapping, precedence, digest and allowed payload shape cannot depend on model discretion.",
  "approvalRule": "Plan is a recommendation. Plan expires after 5 elapsed minutes (H3 proposed), or any case/policy/crew change; new selection needs new approval."
}
```


Sources:

- hypothesis / H3: Each ticket write requires a currently authorized operator approval; tenant is city ID, and operation, resource, report revision, immutable payload digest and policy version are bound to approval.

- hypothesis / H5: Suggested duplicates require operator selection of an existing ticket on the same asset; fuzzy similarity never merges or suppresses reports. Existing ticket links do not change crew assignment or close work.

- hypothesis / H7: Proposed routing uses a versioned GIS boundary, asset ownership, fault category and crew capability/on-duty table; unresolved boundary, unavailable crew or conflicting asset evidence goes to supervisor.

## Workflow rules

### W4 · Build safe immutable plan

{"state":"PLAN","guardBindings":{"planResult":"C4.planResult enum; URGENT precedence before other validations"},"transitions":[{"to":"W5","when":"planResult == READY","mode":"exclusive"},{"to":"W8","when":"planResult in [URGENT,NEEDS_LOCATION,AMBIGUOUS,UNSUPPORTED,NO_CREW,STALE,INVALID]","mode":"exclusive"}],"failureDisposition":"Missing location and candidate conflict persist visible owned queue.","timeout":"local 2s","retryPolicy":"0; revised operator selection creates new plan and restarts W4 only after fresh W2 snapshot","terminalDisposition":""}

Reasoning: Chosen to make the stated workflow explicit and bounded.

Assumptions:

- H3: Each ticket write requires a currently authorized operator approval; tenant is city ID, and operation, resource, report revision, immutable payload digest and policy version are bound to approval.

- H4: Potential exposed wires, fallen poles, sparks or fire enter a staffed urgent manual queue immediately; proposed acknowledgement 2 elapsed minutes and supervisor escalation at 2 minutes; routine exceptions acknowledge within 30 staffed minutes and escalate at 30.

- H10: Proposed operational limits: each read attempt 5 seconds, one read retry; LLM attempt 10 seconds with one retry; ticket write timeout 5 seconds with zero automatic write retry; reconciliation reads at 5, 30 and 120 seconds, then owned unknown hold with 15-minute read-only watchdog. Proposed additional limits: snapshot age at plan creation 60 seconds, plan/approval expiry 5 elapsed minutes, routine nonhuman response p95 30 seconds, and unknown-held >1 hour escalates service manager. These limits require verification, not established policy.

Data:

```json
{
  "componentId": "C4",
  "taskIds": [
    "T4"
  ],
  "next": [
    "W5",
    "W8"
  ],
  "decision": true,
  "example": "Hazard output -> W8; deterministic hazard always wins."
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
- EV3: Writer rejects resource city mismatch
- EV4: Contradictory location retained as human case
- EV5: Concurrent same-report CREATE cannot duplicate
- EV6: Valid operator-selected LINK positive control
- EV7: Revoked actor denied at commit
- EV8: Changed routing policy invalidates approval
- EV9: Concurrent ticket edit rejects stale LINK
- EV10: Payload tampering fails digest binding
- EV11: Injection cannot invoke equipment or fabricate target
- EV15: Model-detected oblique hazard reaches urgent owner
- EV16: LINK rejects forbidden CREATE fields even with valid digest
- EV19: Offline judgement and staffed response validation
- EV20: Full release and live invariant gates
- EV22: Online safety, queue, drift and cost observation
- EV23: Urgent provisional intake without asset or address
- EV25: Closed candidate cannot receive new report
- EV27: Direct equipment command blocked before transport
## Acceptance criteria

- Implement these exact branch rules and all named eval assertions. No equipment controls.
