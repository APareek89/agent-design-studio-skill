# Shop support draft desk

> PASS | DESIGN ONLY. self-review; round 2.

## Original brief

Help a small shop triage customer support and draft useful replies. Staff review every reply before sending.

## Context

- **CTX1 Decision and boundary**: Route urgent complaints to staff while drafting grounded answers to routine questions.
- **CTX2 Inputs, outputs and stop conditions**: Inputs, outputs and stop conditions
- **CTX3 Ownership and privacy**: Ownership and privacy

## Tasks

- **T0 Shop support draft desk**: Shop support draft desk
- **T1 Check request and shop context**: Check request and shop context
- **T2 Find approved shop facts**: Find approved shop facts
- **T3 Sort and draft a reply**: Sort and draft a reply
- **T4 Check claims and prepare staff review**: Check claims and prepare staff review
- **A1 Frozen source and authority context**: Frozen source and authority context

## Components

- **C1 Check case envelope**: Code checks scope, current access, command and version before exposing evidence. Exact duplicate requestId/revision and same frozen source manifest yields intake.state valid with reusedArtifact. W2 supplies existing checked source view; W3 skips model and returns saved draft; W4 rechecks scope/source freshness and receipt. Replacement with changed inputs requires next revision; semantic duplicates are candidates only.
- **C2 Build trusted evidence view**: Classification enum product|delivery|complaint|other; urgent safety or legal complaints are needs_staff. Duplicate message IDs return the earlier draft; semantic duplicates are shown as candidates only. Every draft prominently says Staff review required. Edits invalidate earlier claim checks. No send credential or send API exists.
- **C3 Draft bounded recommendation**: Classification enum product|delivery|complaint|other; urgent safety or legal complaints are needs_staff. Duplicate message IDs return the earlier draft; semantic duplicates are shown as candidates only. Every draft prominently says Staff review required. Edits invalidate earlier claim checks. No send credential or send API exists.
- **C4 Check claims and output proof**: Classification enum product|delivery|complaint|other; urgent safety or legal complaints are needs_staff. Duplicate message IDs return the earlier draft; semantic duplicates are shown as candidates only. Every draft prominently says Staff review required. Edits invalidate earlier claim checks. No send credential or send API exists. A forged or absent citation yields reason INVALID_CITATION, status needs_human. Frozen source conflict yields EVIDENCE_CONFLICT; missing source yields EVIDENCE_MISSING. Local draftId derives from requestId/revision and source manifest; do not export ready before all required source IDs and artifact receipt exist.
- **C5 Prepare human handoff**: Accept exactly one tagged handoffInput. W1 exceptions carry intake, W2 exceptions carry evidence plus intake, W4 carries checked plus intake. Create a local receipt even for exceptions; if receipt generation fails, return unconfirmed error in current caller session. No operational success claim. Classification enum product|delivery|complaint|other; urgent safety or legal complaints are needs_staff. Duplicate message IDs return the earlier draft; semantic duplicates are shown as candidates only. Every draft prominently says Staff review required. Edits invalidate earlier claim checks. No send credential or send API exists.

## Workflow

- **W1 Check request**: {"state": "W1", "transitions": [{"to": "W2", "when": "intake.state == valid", "mode": "exclusive"}, {"to": "W5", "when": "intake.state in {provisional,rejected,cancelled}", "mode": "exclusive"}], "failureDisposition": "Local error receipt; owner retries a new revision after checking source problem. Never claim business success.", "timeout": "30 seconds for draft; 10 seconds per read; all others 5 seconds. Handoff returned in caller session.", "retryPolicy": "One read retry only. One model attempt; invalid or timeout becomes a needs_human packet. No automatic draft regeneration.", "terminalDisposition": "", "bindings": {"intake": "C1.intake; command and authenticated scope set on request", "evidence": "C2.evidence; frozen bundle read result", "draft": "C3.draft; schema validation adds invalid or timeout", "checked": "C4.checked; recheck before ready output", "handoffInput": "C1.intake exception at W1, C2.evidence plus intake exception at W2, or C4.checked at W4; tag selected by predecessor."}, "precedence": "Cancellation then invalid authority then missing evidence then draft. Replacement uses expectedRevision; concurrent stale revision is rejected. Outputs are session artifacts, never a sent reply or approved transaction."}
- **W2 Prepare evidence**: {"state": "W2", "transitions": [{"to": "W3", "when": "evidence.status == ready", "mode": "exclusive"}, {"to": "W5", "when": "evidence.status in {missing,stale,conflict,unavailable}", "mode": "exclusive"}], "failureDisposition": "Local error receipt; owner retries a new revision after checking source problem. Never claim business success.", "timeout": "30 seconds for draft; 10 seconds per read; all others 5 seconds. Handoff returned in caller session.", "retryPolicy": "One read retry only. One model attempt; invalid or timeout becomes a needs_human packet. No automatic draft regeneration.", "terminalDisposition": "", "bindings": {"intake": "C1.intake; command and authenticated scope set on request", "evidence": "C2.evidence; frozen bundle read result", "draft": "C3.draft; schema validation adds invalid or timeout", "checked": "C4.checked; recheck before ready output", "handoffInput": "C1.intake exception at W1, C2.evidence plus intake exception at W2, or C4.checked at W4; tag selected by predecessor."}, "precedence": "Cancellation then invalid authority then missing evidence then draft. Replacement uses expectedRevision; concurrent stale revision is rejected. Outputs are session artifacts, never a sent reply or approved transaction."}
- **W3 Draft with sources**: {"state": "W3", "transitions": [{"to": "W4", "when": "draft returned valid or abstain or invalid or timeout", "mode": "exclusive"}], "failureDisposition": "Local error receipt; owner retries a new revision after checking source problem. Never claim business success.", "timeout": "30 seconds for draft; 10 seconds per read; all others 5 seconds. Handoff returned in caller session.", "retryPolicy": "One read retry only. One model attempt; invalid or timeout becomes a needs_human packet. No automatic draft regeneration.", "terminalDisposition": "", "bindings": {"intake": "C1.intake; command and authenticated scope set on request", "evidence": "C2.evidence; frozen bundle read result", "draft": "C3.draft; schema validation adds invalid or timeout", "checked": "C4.checked; recheck before ready output", "handoffInput": "C1.intake exception at W1, C2.evidence plus intake exception at W2, or C4.checked at W4; tag selected by predecessor."}, "precedence": "Cancellation then invalid authority then missing evidence then draft. Replacement uses expectedRevision; concurrent stale revision is rejected. Outputs are session artifacts, never a sent reply or approved transaction."}
- **W4 Check draft**: {"state": "W4", "transitions": [{"to": "W5", "when": "checked produced for every draft outcome", "mode": "exclusive"}], "failureDisposition": "Local error receipt; owner retries a new revision after checking source problem. Never claim business success.", "timeout": "30 seconds for draft; 10 seconds per read; all others 5 seconds. Handoff returned in caller session.", "retryPolicy": "One read retry only. One model attempt; invalid or timeout becomes a needs_human packet. No automatic draft regeneration.", "terminalDisposition": "", "bindings": {"intake": "C1.intake; command and authenticated scope set on request", "evidence": "C2.evidence; frozen bundle read result", "draft": "C3.draft; schema validation adds invalid or timeout", "checked": "C4.checked; recheck before ready output", "handoffInput": "C1.intake exception at W1, C2.evidence plus intake exception at W2, or C4.checked at W4; tag selected by predecessor."}, "precedence": "Cancellation then invalid authority then missing evidence then draft. Replacement uses expectedRevision; concurrent stale revision is rejected. Outputs are session artifacts, never a sent reply or approved transaction."}
- **W5 Hand off with next step**: {"state": "W5", "transitions": [], "failureDisposition": "Local exception in current caller session; receiving staff owns recovery. No remote write or unknown external commit exists.", "timeout": "30 seconds for draft; 10 seconds per read; all others 5 seconds. Handoff returned in caller session.", "retryPolicy": "One read retry only. One model attempt; invalid or timeout becomes a needs_human packet. No automatic draft regeneration.", "terminalDisposition": "Return local review_ready, provisional, needs_human, rejected or cancelled packet, with owner and nextStep; if artifact receipt unavailable return ARTIFACT_UNCONFIRMED in caller session. No operational completion. Receiving staff review/acknowledge in existing tools; the assistant does not wait for a decision.", "bindings": {"intake": "C1.intake; command and authenticated scope set on request", "evidence": "C2.evidence; frozen bundle read result", "draft": "C3.draft; schema validation adds invalid or timeout", "checked": "C4.checked; recheck before ready output", "handoffInput": "C1.intake exception at W1, C2.evidence plus intake exception at W2, or C4.checked at W4; tag selected by predecessor."}, "precedence": "Cancellation then invalid authority then missing evidence then draft. Replacement uses expectedRevision; concurrent stale revision is rejected. Outputs are session artifacts, never a sent reply or approved transaction."}

## Framework

- **F1 Workflow choice**: Workflow choice
- **F2 Permissions and data**: Permissions and data
- **F3 Storage and deployment options**: Storage and deployment options

## Models

- **M1 One bounded drafting call**: One bounded drafting call

## Fmea

- **FM1 Wrong customer order**: Scores are hypothetical priorities: severity 1 negligible to 10 catastrophic; occurrence 1 rare to 10 frequent; detection 1 caught early to 10 unlikely detected. No risk acceptance claimed.
- **FM2 Invented refund**: Scores are hypothetical priorities: severity 1 negligible to 10 catastrophic; occurrence 1 rare to 10 frequent; detection 1 caught early to 10 unlikely detected. No risk acceptance claimed.
- **FM3 Expired shop policy**: Scores are hypothetical priorities: severity 1 negligible to 10 catastrophic; occurrence 1 rare to 10 frequent; detection 1 caught early to 10 unlikely detected. No risk acceptance claimed.
- **FM4 Revoked source access**: Scores are hypothetical priorities: severity 1 negligible to 10 catastrophic; occurrence 1 rare to 10 frequent; detection 1 caught early to 10 unlikely detected. No risk acceptance claimed.
- **FM5 Model output unavailable**: Scores are hypothetical priorities: severity 1 negligible to 10 catastrophic; occurrence 1 rare to 10 frequent; detection 1 caught early to 10 unlikely detected. No risk acceptance claimed.
- **FM6 Stale concurrent replacement**: Scores are hypothetical priorities: severity 1 negligible to 10 catastrophic; occurrence 1 rare to 10 frequent; detection 1 caught early to 10 unlikely detected. No risk acceptance claimed.
- **FM7 Missing receipt**: Scores are hypothetical priorities: severity 1 negligible to 10 catastrophic; occurrence 1 rare to 10 frequent; detection 1 caught early to 10 unlikely detected. No risk acceptance claimed.
- **FM8 Cancellation**: Scores are hypothetical priorities: severity 1 negligible to 10 catastrophic; occurrence 1 rare to 10 frequent; detection 1 caught early to 10 unlikely detected. No risk acceptance claimed.
- **FM9 Overdue human review**: Scores are hypothetical priorities: severity 1 negligible to 10 catastrophic; occurrence 1 rare to 10 frequent; detection 1 caught early to 10 unlikely detected. No risk acceptance claimed.
- **FM10 Exact duplicate request**: Hypothetical S/O/D prioritization; no measured probability.
- **FM11 Conflicting supplied evidence**: Hypothetical S/O/D prioritization; no measured probability.
- **FM12 Missing supplied evidence**: Hypothetical S/O/D prioritization; no measured probability.
- **FM13 Forged citation**: Hypothetical S/O/D prioritization; no measured probability.

## Evals

- **EV1 Useful bounded packet**: Useful bounded packet
- **EV2 Wrong customer order**: Wrong customer order
- **EV3 Invented refund**: Invented refund
- **EV4 Expired shop policy**: Expired shop policy
- **EV5 Revoked source access**: Revoked source access
- **EV6 Model output unavailable**: Model output unavailable
- **EV7 Stale concurrent replacement**: Stale concurrent replacement
- **EV8 Missing receipt**: Missing receipt
- **EV9 Cancellation**: Cancellation
- **EV10 Overdue human review**: Overdue human review
- **EV11 Held-out staff usefulness and evidence audit**: Held-out staff usefulness and evidence audit
- **EV12 Review-only operating monitor**: Review-only operating monitor
- **EV13 Release gate for all specified branches**: Release gate for all specified branches
- **EV14 Exact duplicate request**: Return same local artifact for exact request/version; changed revision never reuses a draft.
- **EV15 Conflicting supplied evidence**: Do not pick one conflicting record silently; name both sources and ask staff to resolve.
- **EV16 Missing supplied evidence**: Allow provisional intake, list missing source and owned next step; no invented claim.
- **EV17 Forged citation**: Verify citation ID/version/quote against frozen authorized view, never only syntax.

## Rollout

- **R1 Business measure**: Business measure
- **R2 Shadow on historical cases**: Shadow on historical cases
- **R3 Assist-only pilot**: Assist-only pilot
- **R4 Measure review effort**: Measure review effort
- **R5 Accountable owner and stop plan**: Accountable owner and stop plan

## Export

- **X1 Build a review-only tool**: Build a review-only tool

Full exact data and source evidence: [design.json](design.json). Launch facts and owners: [assumptions.md](assumptions.md).
