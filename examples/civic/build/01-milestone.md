# Intake and scope gate part 1

> PASS | DESIGN ONLY. self-review; round 2.

Depends on earlier milestones where their outputs are inputs below. Cross-milestone shared types are read by ID from ../design.json, not copied.

## Selected contracts

### C1 · Intake and scope gate

Local commands SUBMIT {intakeId,revision,text,assetId?,address?} and CANCEL_PROPOSAL {caseId,expectedCaseVersion}; command replaces entire payload. City/actor come from verified identity. Reject unknown keys, >12000 text chars and non-text formats to owned queue. Missing location is allowed provisionally. Same city/intakeId/revision is exactly-once local ingest. Conflicting revision enters owned conflict. Redact contacts before model; untrusted text is data. Preserve original in restricted local store. Fast hazard patterns raise urgency and cannot be downgraded. receivedAt is trusted server ingestion time preserved on replay, never caller time.

Reasoning: Chosen to make the stated workflow explicit and bounded.

Assumptions:

- H1: Proposed first release ingests text typed or pasted by an operator, plus optional asset ID/address; direct citizen-channel integration, photo interpretation and ticket closure are deferred.

- H3: Each ticket write requires a currently authorized operator approval; tenant is city ID, and operation, resource, report revision, immutable payload digest and policy version are bound to approval.

- H6: Proposed data policy: redact reporter contact before LLM use; raw local intake expires after 30 days, recommendation snapshots after 90 days, minimal audit receipts after 365 days; residency and legal retention require city approval.

Data:

```json
{
  "group": "Code: validation",
  "taskIds": [
    "T1"
  ],
  "inputs": [
    "session:{cityId:string,actorId:string,sessionId:string,roles:string[],expiresAt:UTC}; required verified",
    "command:SUBMIT|CANCEL_PROPOSAL discriminated union; required",
    "case?:{caseId:string,version:int,status:enum}; required for CANCEL_PROPOSAL"
  ],
  "outputs": [
    "intake:{caseId:string,cityId:string,intakeId:string,revision:int,receivedAt:UTC,redactedText:string,assetId?:string,address?:string,deterministicHazard:boolean}; on SUBMIT success",
    "entryResult:ELIGIBLE|URGENT|CANCELLED|UNKNOWN_LOCKED|INVALID|UNAUTHORIZED|UNSUPPORTED|CONFLICT; required",
    "errorReason?:INVALID_FORMAT|WRONG_CITY|STALE_REVISION|COMMIT_UNKNOWN|AUTH_DENIED; required on noneligible",
    "caseVersion:int; status receipt:string; durable local persistence required",
    "reason:string enum=NONE|URGENT_INDICATOR|INVALID_FORMAT|AUTH_DENIED|WRONG_CITY|STALE_REVISION|COMMIT_UNKNOWN|UNSUPPORTED_FORMAT|INTAKE_CONFLICT|CANCELLED_BEFORE_SEND; required; deterministic producer"
  ],
  "whyCode": "Identity, payload validation, revisions, redaction and exact ingest uniqueness are deterministic.",
  "approvalRule": "Local storage only under verified city actor; no external write."
}
```


Sources:

- hypothesis / H1: Proposed first release ingests text typed or pasted by an operator, plus optional asset ID/address; direct citizen-channel integration, photo interpretation and ticket closure are deferred.

- hypothesis / H3: Each ticket write requires a currently authorized operator approval; tenant is city ID, and operation, resource, report revision, immutable payload digest and policy version are bound to approval.

- hypothesis / H6: Proposed data policy: redact reporter contact before LLM use; raw local intake expires after 30 days, recommendation snapshots after 90 days, minimal audit receipts after 365 days; residency and legal retention require city approval.

## Workflow rules

### W1 · Register or cancel intake

{"state":"ENTRY","guardBindings":{"entryResult":"C1.entryResult enum; priority CANCEL_PROPOSAL evaluated against journal state before other branches"},"transitions":[{"to":"W2","when":"entryResult == ELIGIBLE","mode":"exclusive"},{"to":"W10","when":"entryResult == CANCELLED","mode":"exclusive"},{"to":"W11","when":"entryResult == UNKNOWN_LOCKED","mode":"exclusive"},{"to":"W8","when":"entryResult in [URGENT,INVALID,UNAUTHORIZED,UNSUPPORTED,CONFLICT]","mode":"exclusive"}],"failureDisposition":"Local save failure: return intake unavailable, no accepted-case claim; restricted incident ledger owned by IT.","timeout":"local 2s budget; failure shown to operator","retryPolicy":"0; exact delivery replay returns same case","terminalDisposition":""}

Reasoning: Chosen to make the stated workflow explicit and bounded.

Assumptions:

- H3: Each ticket write requires a currently authorized operator approval; tenant is city ID, and operation, resource, report revision, immutable payload digest and policy version are bound to approval.

- H4: Potential exposed wires, fallen poles, sparks or fire enter a staffed urgent manual queue immediately; proposed acknowledgement 2 elapsed minutes and supervisor escalation at 2 minutes; routine exceptions acknowledge within 30 staffed minutes and escalate at 30.

- H10: Proposed operational limits: each read attempt 5 seconds, one read retry; LLM attempt 10 seconds with one retry; ticket write timeout 5 seconds with zero automatic write retry; reconciliation reads at 5, 30 and 120 seconds, then owned unknown hold with 15-minute read-only watchdog. Proposed additional limits: snapshot age at plan creation 60 seconds, plan/approval expiry 5 elapsed minutes, routine nonhuman response p95 30 seconds, and unknown-held >1 hour escalates service manager. These limits require verification, not established policy.

Data:

```json
{
  "componentId": "C1",
  "taskIds": [
    "T1"
  ],
  "next": [
    "W2",
    "W10",
    "W11",
    "W8"
  ],
  "decision": true,
  "example": "SL-042 normal text -> W2; fallen pole -> W8 urgent queue."
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
- EV18: Privacy redaction and proposed retention controls
- EV21: Cancellation before send has no ticket effect
- EV19: Offline judgement and staffed response validation
- EV20: Full release and live invariant gates
- EV22: Online safety, queue, drift and cost observation
- EV23: Urgent provisional intake without asset or address
## Acceptance criteria

- Implement these exact branch rules and all named eval assertions. No equipment controls.
