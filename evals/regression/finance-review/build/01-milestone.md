# Scoped evidence intake

> PASS | DESIGN ONLY. self-review; round 2.

Depends on earlier milestones where their outputs are inputs below. Cross-milestone shared types are read by ID from ../design.json, not copied.

## Selected contracts

### C1 · Check case envelope

Code checks scope, current access, command and version before exposing evidence. Exact duplicate requestId/revision and same frozen source manifest yields intake.state valid with reusedArtifact. W2 supplies existing checked source view; W3 skips model and returns saved draft; W4 rechecks scope/source freshness and receipt. Replacement with changed inputs requires next revision; semantic duplicates are candidates only.

Reasoning: Bound the work and make the result reviewable.

Data:

```json
{
  "group": "Code: validation",
  "taskIds": [
    "T1"
  ],
  "inputs": [
    "request: object; staff principal, scope, requestId, command initial|replace|cancel, expectedRevision",
    "bundle: supplied documents and approved current manifest"
  ],
  "outputs": [
    "intake: object; state valid|provisional|rejected|cancelled, reason, sourceVersion, caseRevision, requestId, artifactId optional"
  ],
  "whyCode": "Code checks scope, current access, command and version before exposing evidence.",
  "approvalRule": "No operational write authority. Staff review the exact version before any action in their own system."
}
```


Sources:

- context / user-brief: Read invoice documents, explain PO mismatches and prepare an AP analyst review packet. No posting, payment or supplier-master updates.

- hypothesis / H1: Read supplied invoices and read-only PO snapshots. Explain line differences for analyst review. Exclude posting, payment, supplier changes, tax advice and approval of invoices.

### C2 · Build trusted evidence view

Parse signed decimal amounts using currency precision from an approved manifest; no float arithmetic. Match unique SKU and explicit PO line reference; ambiguous many-to-one matches abstain. Compare quantity, unit price and line total separately; preserve credits as signed values. No model-generated money enters comparison. OCR creates candidates only; source text and deterministic parsing or analyst verification produce trusted numeric fields. Revisions and document hashes are frozen per packet.

Reasoning: Bound the work and make the result reviewable.

Data:

```json
{
  "group": "Code: tools",
  "taskIds": [
    "T2"
  ],
  "inputs": [
    "intake: validated envelope",
    "bundle: immutable supplied source collection"
  ],
  "outputs": [
    "evidence: object; status ready|missing|stale|conflict|unavailable, source IDs, exact passages, trusted typed facts, reason"
  ],
  "whyCode": "Read-only scoped source access; deterministic numeric/date parsing; timeout 10 seconds with one read retry, then unavailable.",
  "approvalRule": "No operational write authority. Staff review the exact version before any action in their own system."
}
```


Sources:

- context / user-brief: Read invoice documents, explain PO mismatches and prepare an AP analyst review packet. No posting, payment or supplier-master updates.

- hypothesis / H1: Read supplied invoices and read-only PO snapshots. Explain line differences for analyst review. Exclude posting, payment, supplier changes, tax advice and approval of invoices.

## Workflow rules

### W1 · Check request

{"state": "W1", "transitions": [{"to": "W2", "when": "intake.state == valid", "mode": "exclusive"}, {"to": "W5", "when": "intake.state in {provisional,rejected,cancelled}", "mode": "exclusive"}], "failureDisposition": "Local error receipt; owner retries a new revision after checking source problem. Never claim business success.", "timeout": "30 seconds for draft; 10 seconds per read; all others 5 seconds. Handoff returned in caller session.", "retryPolicy": "One read retry only. One model attempt; invalid or timeout becomes a needs_human packet. No automatic draft regeneration.", "terminalDisposition": "", "bindings": {"intake": "C1.intake; command and authenticated scope set on request", "evidence": "C2.evidence; frozen bundle read result", "draft": "C3.draft; schema validation adds invalid or timeout", "checked": "C4.checked; recheck before ready output", "handoffInput": "C1.intake exception at W1, C2.evidence plus intake exception at W2, or C4.checked at W4; tag selected by predecessor."}, "precedence": "Cancellation then invalid authority then missing evidence then draft. Replacement uses expectedRevision; concurrent stale revision is rejected. Outputs are session artifacts, never a sent reply or approved transaction."}

Reasoning: Bound the work and make the result reviewable.

Data:

```json
{
  "componentId": "C1",
  "taskIds": [
    "T1"
  ],
  "next": [
    "W2",
    "W5"
  ],
  "decision": true,
  "example": "Valid scope → frozen evidence → draft → check → local staff packet; source error skips draft and produces an exception packet."
}
```


Sources:

- context / user-brief: Read invoice documents, explain PO mismatches and prepare an AP analyst review packet. No posting, payment or supplier-master updates.

- hypothesis / H1: Read supplied invoices and read-only PO snapshots. Explain line differences for analyst review. Exclude posting, payment, supplier changes, tax advice and approval of invoices.

### W2 · Prepare evidence

{"state": "W2", "transitions": [{"to": "W3", "when": "evidence.status == ready", "mode": "exclusive"}, {"to": "W5", "when": "evidence.status in {missing,stale,conflict,unavailable}", "mode": "exclusive"}], "failureDisposition": "Local error receipt; owner retries a new revision after checking source problem. Never claim business success.", "timeout": "30 seconds for draft; 10 seconds per read; all others 5 seconds. Handoff returned in caller session.", "retryPolicy": "One read retry only. One model attempt; invalid or timeout becomes a needs_human packet. No automatic draft regeneration.", "terminalDisposition": "", "bindings": {"intake": "C1.intake; command and authenticated scope set on request", "evidence": "C2.evidence; frozen bundle read result", "draft": "C3.draft; schema validation adds invalid or timeout", "checked": "C4.checked; recheck before ready output", "handoffInput": "C1.intake exception at W1, C2.evidence plus intake exception at W2, or C4.checked at W4; tag selected by predecessor."}, "precedence": "Cancellation then invalid authority then missing evidence then draft. Replacement uses expectedRevision; concurrent stale revision is rejected. Outputs are session artifacts, never a sent reply or approved transaction."}

Reasoning: Bound the work and make the result reviewable.

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
  "example": "Valid scope → frozen evidence → draft → check → local staff packet; source error skips draft and produces an exception packet."
}
```


Sources:

- context / user-brief: Read invoice documents, explain PO mismatches and prepare an AP analyst review packet. No posting, payment or supplier-master updates.

- hypothesis / H1: Read supplied invoices and read-only PO snapshots. Explain line differences for analyst review. Exclude posting, payment, supplier changes, tax advice and approval of invoices.

## Required tests

For each ID below, load ../eval-set.json items[id].data.input, .expected and .passRule. These are the full fixture, expected result and exact assertions; no inherited test context is assumed.

- EV1: Useful bounded packet
- EV2: Currency differs
- EV3: Ambiguous OCR digit
- EV4: Wrong supplier PO
- EV5: Revoked source access
- EV7: Stale concurrent replacement
- EV9: Cancellation
- EV11: Held-out staff usefulness and evidence audit
- EV12: Review-only operating monitor
- EV13: Release gate for all specified branches
- EV14: Exact duplicate request
- EV15: Conflicting supplied evidence
- EV16: Missing supplied evidence
## Acceptance criteria

- Reject wrong scope before model context; preserve source and revision.
