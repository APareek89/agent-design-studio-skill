# Draft checks and human packet

> PASS | DESIGN ONLY. self-review; round 2.

Depends on earlier milestones where their outputs are inputs below. Cross-milestone shared types are read by ID from ../design.json, not copied.

## Selected contracts

### C3 · Draft bounded recommendation

Parse signed decimal amounts using currency precision from an approved manifest; no float arithmetic. Match unique SKU and explicit PO line reference; ambiguous many-to-one matches abstain. Compare quantity, unit price and line total separately; preserve credits as signed values. No model-generated money enters comparison. OCR creates candidates only; source text and deterministic parsing or analyst verification produce trusted numeric fields. Revisions and document hashes are frozen per packet.

Reasoning: Bound the work and make the result reviewable.

Data:

```json
{
  "group": "Agents (LLM)",
  "taskIds": [
    "T3"
  ],
  "inputs": [
    "evidence: validated minimized source view",
    "scope: approved instructions and output schema"
  ],
  "outputs": [
    "draft: object; text, claim citations, disagreement, disposition ready|abstain"
  ],
  "whyCode": "",
  "approvalRule": "No operational write authority. Staff review the exact version before any action in their own system."
}
```


Sources:

- context / user-brief: Read invoice documents, explain PO mismatches and prepare an AP analyst review packet. No posting, payment or supplier-master updates.

- hypothesis / H1: Read supplied invoices and read-only PO snapshots. Explain line differences for analyst review. Exclude posting, payment, supplier changes, tax advice and approval of invoices.

### C4 · Check claims and output proof

Parse signed decimal amounts using currency precision from an approved manifest; no float arithmetic. Match unique SKU and explicit PO line reference; ambiguous many-to-one matches abstain. Compare quantity, unit price and line total separately; preserve credits as signed values. No model-generated money enters comparison. OCR creates candidates only; source text and deterministic parsing or analyst verification produce trusted numeric fields. Revisions and document hashes are frozen per packet. A forged or absent citation yields reason INVALID_CITATION, status needs_human. Frozen source conflict yields EVIDENCE_CONFLICT; missing source yields EVIDENCE_MISSING. Local draftId derives from requestId/revision and source manifest; do not export ready before all required source IDs and artifact receipt exist.

Reasoning: Bound the work and make the result reviewable.

Data:

```json
{
  "group": "Code: validation",
  "taskIds": [
    "T3",
    "T4"
  ],
  "inputs": [
    "draft: candidate or null",
    "evidence: frozen authoritative view",
    "intake: envelope plus fresh scope and revision check"
  ],
  "outputs": [
    "checked: object; status ready|needs_human|rejected|cancelled, artifactId, sourceIds, reason"
  ],
  "whyCode": "Verify exact citations, allowed claims, required fields, freshness and no forbidden action claim. Local artifact receipt is required; no business mutation.",
  "approvalRule": "No operational write authority. Staff review the exact version before any action in their own system."
}
```


Sources:

- context / user-brief: Read invoice documents, explain PO mismatches and prepare an AP analyst review packet. No posting, payment or supplier-master updates.

- hypothesis / H1: Read supplied invoices and read-only PO snapshots. Explain line differences for analyst review. Exclude posting, payment, supplier changes, tax advice and approval of invoices.

### C5 · Prepare human handoff

Accept exactly one tagged handoffInput. W1 exceptions carry intake, W2 exceptions carry evidence plus intake, W4 carries checked plus intake. Create a local receipt even for exceptions; if receipt generation fails, return unconfirmed error in current caller session. No operational success claim. Parse signed decimal amounts using currency precision from an approved manifest; no float arithmetic. Match unique SKU and explicit PO line reference; ambiguous many-to-one matches abstain. Compare quantity, unit price and line total separately; preserve credits as signed values. No model-generated money enters comparison. OCR creates candidates only; source text and deterministic parsing or analyst verification produce trusted numeric fields. Revisions and document hashes are frozen per packet.

Reasoning: Bound the work and make the result reviewable.

Data:

```json
{
  "group": "Code: human triggers",
  "taskIds": [
    "T4"
  ],
  "inputs": [
    "handoffInput: union; checked when W4 ran, otherwise intake exception or evidence exception with requestId, caseRevision, reason, sourceIds and status",
    "owner: proposed role and approved working calendar"
  ],
  "outputs": [
    "handoff: object; owner, status review_ready|provisional|needs_human|needs_staff|needs_analyst|needs_researcher|needs_coordinator|needs_revision|cancelled|rejected, nextStep, reason, artifactId nullable, deadline nullable"
  ],
  "whyCode": "Produce a local review packet and explicit owned next step; no automatic queue message or sending. Human acknowledgement occurs outside this tool.",
  "approvalRule": "No operational write authority. Staff review the exact version before any action in their own system."
}
```


Sources:

- context / user-brief: Read invoice documents, explain PO mismatches and prepare an AP analyst review packet. No posting, payment or supplier-master updates.

- hypothesis / H1: Read supplied invoices and read-only PO snapshots. Explain line differences for analyst review. Exclude posting, payment, supplier changes, tax advice and approval of invoices.

## Workflow rules

### W3 · Draft with sources

{"state": "W3", "transitions": [{"to": "W4", "when": "draft returned valid or abstain or invalid or timeout", "mode": "exclusive"}], "failureDisposition": "Local error receipt; owner retries a new revision after checking source problem. Never claim business success.", "timeout": "30 seconds for draft; 10 seconds per read; all others 5 seconds. Handoff returned in caller session.", "retryPolicy": "One read retry only. One model attempt; invalid or timeout becomes a needs_human packet. No automatic draft regeneration.", "terminalDisposition": "", "bindings": {"intake": "C1.intake; command and authenticated scope set on request", "evidence": "C2.evidence; frozen bundle read result", "draft": "C3.draft; schema validation adds invalid or timeout", "checked": "C4.checked; recheck before ready output", "handoffInput": "C1.intake exception at W1, C2.evidence plus intake exception at W2, or C4.checked at W4; tag selected by predecessor."}, "precedence": "Cancellation then invalid authority then missing evidence then draft. Replacement uses expectedRevision; concurrent stale revision is rejected. Outputs are session artifacts, never a sent reply or approved transaction."}

Reasoning: Bound the work and make the result reviewable.

Data:

```json
{
  "componentId": "C3",
  "taskIds": [
    "T3"
  ],
  "next": [
    "W4"
  ],
  "decision": false,
  "example": "Valid scope → frozen evidence → draft → check → local staff packet; source error skips draft and produces an exception packet."
}
```


Sources:

- context / user-brief: Read invoice documents, explain PO mismatches and prepare an AP analyst review packet. No posting, payment or supplier-master updates.

- hypothesis / H1: Read supplied invoices and read-only PO snapshots. Explain line differences for analyst review. Exclude posting, payment, supplier changes, tax advice and approval of invoices.

### W4 · Check draft

{"state": "W4", "transitions": [{"to": "W5", "when": "checked produced for every draft outcome", "mode": "exclusive"}], "failureDisposition": "Local error receipt; owner retries a new revision after checking source problem. Never claim business success.", "timeout": "30 seconds for draft; 10 seconds per read; all others 5 seconds. Handoff returned in caller session.", "retryPolicy": "One read retry only. One model attempt; invalid or timeout becomes a needs_human packet. No automatic draft regeneration.", "terminalDisposition": "", "bindings": {"intake": "C1.intake; command and authenticated scope set on request", "evidence": "C2.evidence; frozen bundle read result", "draft": "C3.draft; schema validation adds invalid or timeout", "checked": "C4.checked; recheck before ready output", "handoffInput": "C1.intake exception at W1, C2.evidence plus intake exception at W2, or C4.checked at W4; tag selected by predecessor."}, "precedence": "Cancellation then invalid authority then missing evidence then draft. Replacement uses expectedRevision; concurrent stale revision is rejected. Outputs are session artifacts, never a sent reply or approved transaction."}

Reasoning: Bound the work and make the result reviewable.

Data:

```json
{
  "componentId": "C4",
  "taskIds": [
    "T3",
    "T4"
  ],
  "next": [
    "W5"
  ],
  "decision": false,
  "example": "Valid scope → frozen evidence → draft → check → local staff packet; source error skips draft and produces an exception packet."
}
```


Sources:

- context / user-brief: Read invoice documents, explain PO mismatches and prepare an AP analyst review packet. No posting, payment or supplier-master updates.

- hypothesis / H1: Read supplied invoices and read-only PO snapshots. Explain line differences for analyst review. Exclude posting, payment, supplier changes, tax advice and approval of invoices.

### W5 · Hand off with next step

{"state": "W5", "transitions": [], "failureDisposition": "Local exception in current caller session; receiving staff owns recovery. No remote write or unknown external commit exists.", "timeout": "30 seconds for draft; 10 seconds per read; all others 5 seconds. Handoff returned in caller session.", "retryPolicy": "One read retry only. One model attempt; invalid or timeout becomes a needs_human packet. No automatic draft regeneration.", "terminalDisposition": "Return local review_ready, provisional, needs_human, rejected or cancelled packet, with owner and nextStep; if artifact receipt unavailable return ARTIFACT_UNCONFIRMED in caller session. No operational completion. Receiving staff review/acknowledge in existing tools; the assistant does not wait for a decision.", "bindings": {"intake": "C1.intake; command and authenticated scope set on request", "evidence": "C2.evidence; frozen bundle read result", "draft": "C3.draft; schema validation adds invalid or timeout", "checked": "C4.checked; recheck before ready output", "handoffInput": "C1.intake exception at W1, C2.evidence plus intake exception at W2, or C4.checked at W4; tag selected by predecessor."}, "precedence": "Cancellation then invalid authority then missing evidence then draft. Replacement uses expectedRevision; concurrent stale revision is rejected. Outputs are session artifacts, never a sent reply or approved transaction."}

Reasoning: Bound the work and make the result reviewable.

Data:

```json
{
  "componentId": "C5",
  "taskIds": [
    "T4"
  ],
  "next": [],
  "decision": false,
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
- EV6: Model output unavailable
- EV7: Stale concurrent replacement
- EV8: Missing receipt
- EV9: Cancellation
- EV10: Overdue human review
- EV11: Held-out staff usefulness and evidence audit
- EV12: Review-only operating monitor
- EV13: Release gate for all specified branches
- EV14: Exact duplicate request
- EV15: Conflicting supplied evidence
- EV16: Missing supplied evidence
- EV17: Forged citation
## Acceptance criteria

- Check every claim; return owned exception on missing evidence or failure; no business write.
