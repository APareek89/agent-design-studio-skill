# Access and admitted evidence

> PASS | DESIGN ONLY. independent-agent; round 2.

Depends on earlier milestones where their outputs are inputs below. Cross-milestone shared types are read by ID from ../design.json, not copied.

## Selected contracts

### C1 · Authorize intake

Identity, command, correction links and permission are enforced before any medical read. Corrections require originalCaseId and expectedVersion; they open a linked draft only, never change settlement.

Reasoning: Bounded responsibility with an owned safe outcome.

Assumptions:

- H1

- H2

- H3

- H4

Data:

```json
{
  "group": "Code: validation",
  "taskIds": [
    "T1"
  ],
  "inputs": [
    "request: {tenant,member,claim,command: initial|cancel|correction,expectedVersion?,originalCaseId?}",
    "principal: authenticated identity"
  ],
  "outputs": [
    "intake: enum ready|missing|unsupported|denied|cancelled",
    "scope: trusted tenant/member/claim binding",
    "snapshot: versioned authoritative membership and case metadata"
  ],
  "whyCode": "Identity, command, correction links and permission are enforced before any medical read. Corrections require originalCaseId and expectedVersion; they open a linked draft only, never change settlement.",
  "approvalRule": "Draft publication only; no insurer adjudication or settlement authority. Fresh caller role required; staff event bound to exact snapshot where review is needed."
}
```


Sources:

- context / user-brief: Policies can change over time and bills may include room-rent limits.

- hypothesis / H1: First release publishes staff-facing recommendations only; all settlement, denial notices and appeals stay outside this assistant.

- hypothesis / H2: Insurer supplies signed, effective-dated policy rule packs, member linkage, authority and case APIs with version checks and operation readback. This proposed integration also exposes a tenant/member/policy-bound benefit accumulator snapshot and a same-request current-version receipt; its real support and currency/freshness semantics require insurer verification.

- hypothesis / H3: Privacy owner selects deployment region, role access, lawful processing basis, document retention and model contract; proposed documents TTL 30 days, minimal audit 365 days, legal hold overrides deletion.

- hypothesis / H4: Claims team covers a 24-hour elapsed-time review deadline, four-hour acknowledgement and a one-hour visible waiting status.

### C2 · Verify source evidence

GET vault documents and rule registry by bound IDs, version and service dates, 10s timeout; one read retry then unavailable. Reject cross-subject records. Strip hidden text, scripts and invisible instructions; low OCR confidence or conflicting layers route to staff. Proposed H2 accumulator source: authenticated GET /benefit-accumulators/{policyId}/members/{member} under tenant scope, paired with current-version receipt in the same read request. Fields match accumulatorSnapshot output. This read never reserves or spends benefits. Both are insurer API source facts, never model/policy-document values. Missing/failed source data uses existing unavailable path; a returned incomplete/stale snapshot reaches C4 review. Ordinary 10s/read retry bound applies.

Reasoning: Bounded responsibility with an owned safe outcome.

Assumptions:

- H1

- H2

- H3

- H4

Data:

```json
{
  "group": "Code: tools",
  "taskIds": [
    "T2"
  ],
  "inputs": [
    "scope: authorized tenant/member/claim",
    "snapshot: membership and case version"
  ],
  "outputs": [
    "evidence: page-indexed admitted text with document hash, visible clause spans and OCR verification status",
    "documentStatus: enum valid|missing|conflict|invalid|unavailable",
    "accumulatorSnapshot: required for calculation {tenant:string,member:string,policyId:string,currency:string,remainingCoverMinor:int64,accumulatorVersion:int64,asOf:string,readRequestId:string,versionReceipt:{requestId:string,currentVersion:int64,checkedAt:string}}; may be absent only on owned review/cancel path"
  ],
  "whyCode": "GET vault documents and rule registry by bound IDs, version and service dates, 10s timeout; one read retry then unavailable. Reject cross-subject records. Strip hidden text, scripts and invisible instructions; low OCR confidence or conflicting layers route to staff.",
  "approvalRule": "Draft publication only; no insurer adjudication or settlement authority. Fresh caller role required; staff event bound to exact snapshot where review is needed."
}
```


Sources:

- context / user-brief: Policies can change over time and bills may include room-rent limits.

- hypothesis / H1: First release publishes staff-facing recommendations only; all settlement, denial notices and appeals stay outside this assistant.

- hypothesis / H2: Insurer supplies signed, effective-dated policy rule packs, member linkage, authority and case APIs with version checks and operation readback. This proposed integration also exposes a tenant/member/policy-bound benefit accumulator snapshot and a same-request current-version receipt; its real support and currency/freshness semantics require insurer verification.

- hypothesis / H3: Privacy owner selects deployment region, role access, lawful processing basis, document retention and model contract; proposed documents TTL 30 days, minimal audit 365 days, legal hold overrides deletion.

- hypothesis / H4: Claims team covers a 24-hour elapsed-time review deadline, four-hour acknowledgement and a one-hour visible waiting status.

## Workflow rules

### W1 · Check access and request

{"state": "Check access and request", "transitions": [{"to": "W2", "when": "intake=ready", "mode": "exclusive"}, {"to": "W5", "when": "intake in {missing,unsupported,cancelled}", "mode": "exclusive"}, {"to": "W11", "when": "intake=denied", "mode": "exclusive"}], "failureDisposition": "Preserve metadata and owned manual-review state; no claim payment or final denial.", "timeout": "10 seconds", "retryPolicy": "No automatic retry", "terminalDisposition": "", "guardBindings": "intake:C1.intake; scope:C1.scope; snapshot:C1.snapshot. Denied terminal logs only nonmedical security telemetry; no case publication."}

Reasoning: Bounded responsibility with an owned safe outcome.

Assumptions:

- H1

- H2

- H4

Data:

```json
{
  "componentId": "C1",
  "taskIds": [
    "T1"
  ],
  "next": [
    "W2",
    "W5",
    "W11"
  ],
  "decision": true,
  "example": "HC-1 follows only the matching output enum."
}
```


Sources:

- context / user-brief: Policies can change over time and bills may include room-rent limits.

- hypothesis / H1: First release publishes staff-facing recommendations only; all settlement, denial notices and appeals stay outside this assistant.

- hypothesis / H2: Insurer supplies signed, effective-dated policy rule packs, member linkage, authority and case APIs with version checks and operation readback. This proposed integration also exposes a tenant/member/policy-bound benefit accumulator snapshot and a same-request current-version receipt; its real support and currency/freshness semantics require insurer verification.

- hypothesis / H4: Claims team covers a 24-hour elapsed-time review deadline, four-hour acknowledgement and a one-hour visible waiting status.

### W2 · Load verified evidence

{"state": "Load verified evidence", "transitions": [{"to": "W3", "when": "documentStatus=valid", "mode": "exclusive"}, {"to": "W5", "when": "documentStatus in {missing,conflict,invalid,unavailable}", "mode": "exclusive"}], "failureDisposition": "Preserve metadata and owned manual-review state; no claim payment or final denial.", "timeout": "10 seconds", "retryPolicy": "No automatic retry", "terminalDisposition": "", "guardBindings": "Predicates use the named component output enum, updated once on response; precedence follows listed enum cases. No LLM-generated guard is authoritative. bindings.accumulatorSnapshot = C2.accumulatorSnapshot, produced by authenticated insurer source GET and same-request version receipt; missing source read uses unavailable outcome."}

Reasoning: Bounded responsibility with an owned safe outcome.

Assumptions:

- H1

- H2

- H4

Data:

```json
{
  "componentId": "C2",
  "taskIds": [
    "T2"
  ],
  "next": [
    "W3",
    "W5"
  ],
  "decision": true,
  "example": "HC-1 follows only the matching output enum."
}
```


Sources:

- context / user-brief: Policies can change over time and bills may include room-rent limits.

- hypothesis / H1: First release publishes staff-facing recommendations only; all settlement, denial notices and appeals stay outside this assistant.

- hypothesis / H2: Insurer supplies signed, effective-dated policy rule packs, member linkage, authority and case APIs with version checks and operation readback. This proposed integration also exposes a tenant/member/policy-bound benefit accumulator snapshot and a same-request current-version receipt; its real support and currency/freshness semantics require insurer verification.

- hypothesis / H4: Claims team covers a 24-hour elapsed-time review deadline, four-hour acknowledgement and a one-hour visible waiting status.

## Required tests

For each ID below, load ../eval-set.json items[id].data.input, .expected and .passRule. These are the full fixture, expected result and exact assertions; no inherited test context is assumed.

- EV1: Valid room-only recommendation
- EV2: Wrong tenant cannot read
- EV6: Isolated citation check page
- EV7: Isolated citation check clause
- EV8: Isolated citation check text
- EV9: Hidden instructions excluded
- EV16: Missing evidence has a visible owned deadline
- EV17: Conflicting source evidence abstains
- EV19: Held-out source and arithmetic validation
- EV20: Queue and save integrity monitoring
- EV21: Release regression gate
- EV26: Unverified OCR has no authoritative total
- EV28: Correction requires original record
- EV29: Pre-save cancellation has a proven case record
- EV32: Missing authoritative accumulator version withholds total
- EV33: Stale authoritative accumulator version withholds total
## Acceptance criteria

- Implement exact selected contracts and all named tests; complete H1-H4 evidence before live PHI.
- Do not expand settlement authority; preserve failure ownership and source versions.
