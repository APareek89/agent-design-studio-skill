# Safe save, readback and proof

> PASS | DESIGN ONLY. independent-agent; round 2.

Depends on earlier milestones where their outputs are inputs below. Cross-milestone shared types are read by ID from ../design.json, not copied.

## Selected contracts

### C7 · Save staff-facing case

PUT /staff-cases/{claim}/operations/{operationId}; authority case.write only, no payment permission. Verify authenticated scope, fresh role, current claim and rule version, full immutable payload SHA256 from stored bytes, status enum and expectedVersion at API. Unique tenant/claim/submissionRevision prevents exact duplicates; semantic duplicate candidates require human linking, never auto-merge. CAS makes only one concurrent revision succeed. 10s timeout; no blind write retry. Narrative cannot change numeric fields. Internal serialization is UTF-8 JSON with sorted keys, compact separators and no nonfinite numbers; SHA256 stored bytes, not a reserialized model object. Store immutable bytes before authorizing the save. Any payload change requires new operation authorization. Ledger business identity is tenant/claim/submissionRevision. Nonmedical security telemetry remains separate from claim record writes. For DRAFT only, perform a fresh accumulator current-version query at save and require equality with assessment.accumulatorVersion; version change rejects with ACCUMULATOR_SNAPSHOT_STALE and forces new calculation/authorization. Bind approval to exact stored payload bytes/hash plus tenant/member/claim, operationId, expectedVersion and rule/accumulator versions. Two competitors need two distinct complete authorizations; an OP-1 authorization cannot authorize OP-A or OP-B. Review/cancel payloads have assessment:null and no monetary authorization.

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
    "T6"
  ],
  "inputs": [
    "payload: trusted immutable staff-case {tenant,member,claim,expectedVersion,operationId,status,assessment,review,createdAt}",
    "explanation: validated model narrative with source references or empty"
  ],
  "outputs": [
    "saveResult: enum committed|rejected|TIMEOUT|unknown_commit",
    "record: optional durable caseId,version,operationId",
    "verifiedRecordId:string! on a proven record outcome; explicit projection of existing case/posting record ID, absent on failed or uncertain outcomes"
  ],
  "whyCode": "PUT /staff-cases/{claim}/operations/{operationId}; authority case.write only, no payment permission. Verify authenticated scope, fresh role, current claim and rule version, full immutable payload SHA256 from stored bytes, status enum and expectedVersion at API. Unique tenant/claim/submissionRevision prevents exact duplicates; semantic duplicate candidates require human linking, never auto-merge. CAS makes only one concurrent revision succeed. 10s timeout; no blind write retry. Narrative cannot change numeric fields.",
  "approvalRule": "Draft publication only; no insurer adjudication or settlement authority. Fresh caller role required; staff event bound to exact snapshot where review is needed."
}
```


Sources:

- context / user-brief: Policies can change over time and bills may include room-rent limits.

- hypothesis / H1: First release publishes staff-facing recommendations only; all settlement, denial notices and appeals stay outside this assistant.

- hypothesis / H2: Insurer supplies signed, effective-dated policy rule packs, member linkage, authority and case APIs with version checks and operation readback. This proposed integration also exposes a tenant/member/policy-bound benefit accumulator snapshot and a same-request current-version receipt; its real support and currency/freshness semantics require insurer verification.

- hypothesis / H3: Privacy owner selects deployment region, role access, lawful processing basis, document retention and model contract; proposed documents TTL 30 days, minimal audit 365 days, legal hold overrides deletion.

- hypothesis / H4: Claims team covers a 24-hour elapsed-time review deadline, four-hour acknowledgement and a one-hour visible waiting status.

### C8 · Reconcile save

GET operation record under service-owned read-only reconciliation scope, independent of expired caller session. Three reads at 10s with server backoff 5/20/60s; require payload bytes match and deduplicate callbacks by eventId. Retry once only after confirmed_absent plus fresh auth/CAS; otherwise owned unresolved. Cancellation during ambiguity freezes follow-up; finish readback, no compensation or new intent.

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
    "T6",
    "T7"
  ],
  "inputs": [
    "operation: trusted tenant/claim/operationId and stored immutable payload",
    "saveResult: TIMEOUT|unknown_commit"
  ],
  "outputs": [
    "reconcileResult: enum found|confirmed_absent|unresolved",
    "record: optional verified durable caseId/version/operationId",
    "verifiedRecordId:string! on a proven record outcome; explicit projection of existing case/posting record ID, absent on failed or uncertain outcomes"
  ],
  "whyCode": "GET operation record under service-owned read-only reconciliation scope, independent of expired caller session. Three reads at 10s with server backoff 5/20/60s; require payload bytes match and deduplicate callbacks by eventId. Retry once only after confirmed_absent plus fresh auth/CAS; otherwise owned unresolved. Cancellation during ambiguity freezes follow-up; finish readback, no compensation or new intent.",
  "approvalRule": "Draft publication only; no insurer adjudication or settlement authority. Fresh caller role required; staff event bound to exact snapshot where review is needed."
}
```


Sources:

- context / user-brief: Policies can change over time and bills may include room-rent limits.

- hypothesis / H1: First release publishes staff-facing recommendations only; all settlement, denial notices and appeals stay outside this assistant.

- hypothesis / H2: Insurer supplies signed, effective-dated policy rule packs, member linkage, authority and case APIs with version checks and operation readback. This proposed integration also exposes a tenant/member/policy-bound benefit accumulator snapshot and a same-request current-version receipt; its real support and currency/freshness semantics require insurer verification.

- hypothesis / H3: Privacy owner selects deployment region, role access, lawful processing basis, document retention and model contract; proposed documents TTL 30 days, minimal audit 365 days, legal hold overrides deletion.

- hypothesis / H4: Claims team covers a 24-hour elapsed-time review deadline, four-hour acknowledgement and a one-hour visible waiting status.

### C9 · Guard record proof

Validate record IDs, subject, operation, full stored bytes and version through readback before user sees saved. Invalid/missing proof retains owner and unresolved status. Explicit proof projection: Only a committed writer or matching authoritative readback supplies the saved caseId. Guard compares full stored body, tenant/member/claim, operation and version. Absent/empty/wrong record rejects saved status.

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
    "T7"
  ],
  "inputs": [
    "record: saved or readback caseId/version/operationId",
    "operation: expected tenant/claim/operationId and payload bytes",
    "verifiedRecordId:string! on a proven outcome; required nonempty trusted record projection, otherwise reject proof"
  ],
  "outputs": [
    "proof: enum verified|invalid"
  ],
  "whyCode": "Validate record IDs, subject, operation, full stored bytes and version through readback before user sees saved. Invalid/missing proof retains owner and unresolved status.",
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

### W7 · Save staff case

{"state": "Save staff case", "transitions": [{"to": "W9", "when": "saveResult=committed", "mode": "exclusive"}, {"to": "W11", "when": "saveResult=rejected", "mode": "exclusive"}, {"to": "W8", "when": "saveResult=TIMEOUT", "mode": "exclusive"}, {"to": "W8", "when": "saveResult=unknown_commit", "mode": "exclusive"}], "failureDisposition": "Preserve metadata and owned manual-review state; no claim payment or final denial.", "timeout": "10 seconds", "retryPolicy": "No retry before W8; at most one resubmission after confirmed absence", "terminalDisposition": "", "guardBindings": "Predicates use the named component output enum, updated once on response; precedence follows listed enum cases. No LLM-generated guard is authoritative."}

Reasoning: Bounded responsibility with an owned safe outcome.

Assumptions:

- H1

- H2

- H4

Data:

```json
{
  "componentId": "C7",
  "taskIds": [
    "T6"
  ],
  "next": [
    "W9",
    "W11",
    "W8"
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

### W8 · Read operation result

{"state": "Read operation result", "transitions": [{"to": "W9", "when": "reconcileResult=found", "mode": "exclusive"}, {"to": "W7", "when": "reconcileResult=confirmed_absent and retryCount=0 and freshAuthority=true and cancellation=false", "mode": "exclusive"}, {"to": "W11", "when": "reconcileResult=unresolved or (reconcileResult=confirmed_absent and (retryCount=1 or freshAuthority=false or cancellation=true))", "mode": "exclusive"}], "failureDisposition": "Preserve metadata and owned manual-review state; no claim payment or final denial.", "timeout": "Three bounded reads within 120 seconds; then durable owner", "retryPolicy": "No automatic retry", "terminalDisposition": "", "guardBindings": "reconcileResult:C8.reconcileResult; retryCount:durable server operation counter incremented atomically; freshAuthority:C1 fresh recheck via writer; cancellation:signed case event. On found, proof proceeds even if session expired; display requires reauthentication."}

Reasoning: Bounded responsibility with an owned safe outcome.

Assumptions:

- H1

- H2

- H4

Data:

```json
{
  "componentId": "C8",
  "taskIds": [
    "T6",
    "T7"
  ],
  "next": [
    "W9",
    "W7",
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

### W9 · Check saved record

{"state": "Check saved record", "transitions": [{"to": "W10", "when": "proof=verified", "mode": "exclusive"}, {"to": "W11", "when": "proof=invalid", "mode": "exclusive"}], "failureDisposition": "Preserve metadata and owned manual-review state; no claim payment or final denial.", "timeout": "10 seconds", "retryPolicy": "No automatic retry", "terminalDisposition": "", "guardBindings": "Predicates use the named component output enum, updated once on response; precedence follows listed enum cases. No LLM-generated guard is authoritative.", "bindings": {"verifiedRecordId": [{"sourceComponentId": "C7", "sourceField": "verifiedRecordId"}, {"sourceComponentId": "C8", "sourceField": "verifiedRecordId"}]}, "recordProofPolicy": "Only a committed writer or matching authoritative readback supplies the saved caseId. Guard compares full stored body, tenant/member/claim, operation and version. Absent/empty/wrong record rejects saved status."}

Reasoning: Bounded responsibility with an owned safe outcome.

Assumptions:

- H1

- H2

- H4

Data:

```json
{
  "componentId": "C9",
  "taskIds": [
    "T7"
  ],
  "next": [
    "W10",
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

### W10 · Show saved case

{"state": "Show saved case", "transitions": [], "failureDisposition": "Preserve metadata and owned manual-review state; no claim payment or final denial.", "timeout": "10 seconds", "retryPolicy": "No automatic retry", "terminalDisposition": "SAVED_DRAFT|SAVED_REVIEW_REQUIRED|SAVED_CANCELLED with verified caseId and operationId; never PAID or DENIED", "guardBindings": "Predicates use the named component output enum, updated once on response; precedence follows listed enum cases. No LLM-generated guard is authoritative."}

Reasoning: Bounded responsibility with an owned safe outcome.

Assumptions:

- H1

- H2

- H4

Data:

```json
{
  "componentId": "C9",
  "taskIds": [
    "T7"
  ],
  "next": [],
  "decision": false,
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
- EV3: Stale operative policy withheld
- EV4: Explicit proportional room rule
- EV5: Missing room rule is not invented
- EV6: Isolated citation check page
- EV7: Isolated citation check clause
- EV8: Isolated citation check text
- EV9: Hidden instructions excluded
- EV10: Two concurrent submissions cannot overwrite
- EV11: Exact duplicate returns existing record
- EV12: Unknown save survives caller expiry and repeated callback
- EV13: Cancellation cannot conceal uncertain save
- EV14: Missing record proof cannot show saved
- EV15: Revoked authority blocks save
- EV16: Missing evidence has a visible owned deadline
- EV17: Conflicting source evidence abstains
- EV18: Semantic duplicate needs staff linking
- EV20: Queue and save integrity monitoring
- EV21: Release regression gate
- EV22: Policy boundary uses service date, not current date
- EV23: Fresh remaining cover caps the recommendation
- EV24: Nonzero copay stays with staff
- EV25: Changed payload cannot reuse authorization
- EV26: Unverified OCR has no authoritative total
- EV27: Reviewed rejection remains staff-facing
- EV28: Correction requires original record
- EV29: Pre-save cancellation has a proven case record
- EV30: Half-up rounding is visible at a minor unit
- EV31: Negative charge cannot become a draft
- EV32: Missing authoritative accumulator version withholds total
- EV33: Stale authoritative accumulator version withholds total
## Acceptance criteria

- Implement exact selected contracts and all named tests; complete H1-H4 evidence before live PHI.
- Do not expand settlement authority; preserve failure ownership and source versions.
