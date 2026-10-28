# Staff review and waiting status

> PASS | DESIGN ONLY. independent-agent; round 2.

Depends on earlier milestones where their outputs are inputs below. Cross-milestone shared types are read by ID from ../design.json, not copied.

## Selected contracts

### C5 · Own human review

Queue: claims-review; proposed lead H4, ack four elapsed hours, resolve 24 elapsed hours, escalate unacked at four to backup supervisor. Rejections/unknown rules never leave as automated final decisions. Resolution may record manual-review-required; adding rules requires separately certified new registry version. Own W11 unresolved operation tickets across caller expiry and denied security outcomes without revealing medical data. For signed resolution, authenticate examiner identity/role, exact case version and immutable review event before constructing review payload; reject changed snapshot, stale or unsigned events.

Reasoning: Bounded responsibility with an owned safe outcome.

Assumptions:

- H1

- H2

- H3

- H4

Data:

```json
{
  "group": "Code: human triggers",
  "taskIds": [
    "T5",
    "T7"
  ],
  "inputs": [
    "caseContext: bound metadata and optional withheld draft",
    "event: signed ack|resolve|cancel|overdue or server timer"
  ],
  "outputs": [
    "review: enum pending|resolved|cancelled|overdue",
    "reviewRecord: signed actor, snapshotVersion, disposition and rationale"
  ],
  "whyCode": "Queue: claims-review; proposed lead H4, ack four elapsed hours, resolve 24 elapsed hours, escalate unacked at four to backup supervisor. Rejections/unknown rules never leave as automated final decisions. Resolution may record manual-review-required; adding rules requires separately certified new registry version.",
  "approvalRule": "Draft publication only; no insurer adjudication or settlement authority. Fresh caller role required; staff event bound to exact snapshot where review is needed."
}
```


Sources:

- context / user-brief: Policies can change over time and bills may include room-rent limits.

- hypothesis / H1: First release publishes staff-facing recommendations only; all settlement, denial notices and appeals stay outside this assistant.

- hypothesis / H2: Insurer supplies signed, effective-dated policy rule packs, member linkage, authority and case APIs with version checks and operation readback. This proposed integration also exposes a tenant/member/policy-bound benefit accumulator snapshot and a same-request current-version receipt; its real support and currency/freshness semantics require insurer verification.

- hypothesis / H3: Privacy owner selects deployment region, role access, lawful processing basis, document retention and model contract; proposed documents TTL 30 days, minimal audit 365 days, legal hold overrides deletion.

- hypothesis / H4: Claims team covers a 24-hour elapsed-time review deadline, four-hour acknowledgement and a one-hour visible waiting status.

### C6 · Show waiting status

Render read-only case status through authenticated dashboard pull; no email or external message. One-hour timer does not renew the 24h deadline. UI unavailable raises operations alert and keeps queue ownership.

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
    "T5"
  ],
  "inputs": [
    "queueState: trusted pending case and deadline"
  ],
  "outputs": [
    "visibleState: waiting; queue owner and next deadline"
  ],
  "whyCode": "Render read-only case status through authenticated dashboard pull; no email or external message. One-hour timer does not renew the 24h deadline. UI unavailable raises operations alert and keeps queue ownership.",
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

### W5 · Wait for staff

{"state": "Wait for staff", "transitions": [{"to": "W6", "when": "review=pending and elapsed>=1h and noticeShown=false", "mode": "exclusive"}, {"to": "W7", "when": "review in {resolved,cancelled,overdue}", "mode": "exclusive"}], "failureDisposition": "Preserve metadata and owned manual-review state; no claim payment or final denial.", "timeout": "24 elapsed hours from initial queue entry, never extended by notice", "retryPolicy": "No automatic retry", "terminalDisposition": "", "guardBindings": "review:C5.review from signed staff event or trusted server clock; elapsed:server clock minus queue enteredAt; noticeShown:C6 visible-state event. Pending without due notice remains durable wait. At 4h unacked escalation stays same queue; at 24h overdue creates manual-review-required payload, no adjudication. Cancellation on pre-save stops computation and records cancelled; cancellation on unknown save is reconciled first."}

Reasoning: Bounded responsibility with an owned safe outcome.

Assumptions:

- H1

- H2

- H4

Data:

```json
{
  "componentId": "C5",
  "taskIds": [
    "T5"
  ],
  "next": [
    "W6",
    "W7"
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

### W6 · Show owner and due time

{"state": "Show owner and due time", "transitions": [{"to": "W5", "when": "visibleState emitted or dashboard unavailable", "mode": "exclusive"}], "failureDisposition": "Preserve metadata and owned manual-review state; no claim payment or final denial.", "timeout": "10 seconds", "retryPolicy": "One notice projection per queue entry; failure alerts owner, no timer reset", "terminalDisposition": "", "guardBindings": "Predicates use the named component output enum, updated once on response; precedence follows listed enum cases. No LLM-generated guard is authoritative."}

Reasoning: Bounded responsibility with an owned safe outcome.

Assumptions:

- H1

- H2

- H4

Data:

```json
{
  "componentId": "C6",
  "taskIds": [
    "T5"
  ],
  "next": [
    "W5"
  ],
  "decision": false,
  "example": "HC-1 follows only the matching output enum."
}
```


Sources:

- context / user-brief: Policies can change over time and bills may include room-rent limits.

- hypothesis / H1: First release publishes staff-facing recommendations only; all settlement, denial notices and appeals stay outside this assistant.

- hypothesis / H2: Insurer supplies signed, effective-dated policy rule packs, member linkage, authority and case APIs with version checks and operation readback. This proposed integration also exposes a tenant/member/policy-bound benefit accumulator snapshot and a same-request current-version receipt; its real support and currency/freshness semantics require insurer verification.

- hypothesis / H4: Claims team covers a 24-hour elapsed-time review deadline, four-hour acknowledgement and a one-hour visible waiting status.

### W11 · Retain owned exception

{"state": "Retain owned exception", "transitions": [], "failureDisposition": "Preserve metadata and owned manual-review state; no claim payment or final denial.", "timeout": "10 seconds", "retryPolicy": "No automatic retry", "terminalDisposition": "ACCESS_DENIED without medical details; or SAVE_REJECTED/UNRESOLVED_OPERATION owned by claims operations, readback ticket and next check within 4h. Never claim saved or settled.", "guardBindings": "Predicates use the named component output enum, updated once on response; precedence follows listed enum cases. No LLM-generated guard is authoritative."}

Reasoning: Bounded responsibility with an owned safe outcome.

Assumptions:

- H1

- H2

- H4

Data:

```json
{
  "componentId": "C5",
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

- EV13: Cancellation cannot conceal uncertain save
- EV16: Missing evidence has a visible owned deadline
- EV20: Queue and save integrity monitoring
- EV21: Release regression gate
- EV27: Reviewed rejection remains staff-facing
- EV29: Pre-save cancellation has a proven case record
## Acceptance criteria

- Implement exact selected contracts and all named tests; complete H1-H4 evidence before live PHI.
- Do not expand settlement authority; preserve failure ownership and source versions.
