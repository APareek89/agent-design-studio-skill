# Weekly evidence brief assistant

> NEEDS-WORK | DESIGN ONLY. independent-agent; round 1.

## Original brief

Help a product team find evidence in its supplied research notes and draft a weekly decision brief. Cite evidence and state disagreement.

## Context

- **CTX1 Decision and boundary**: Use source-grounded synthesis while keeping contested conclusions visible.
- **CTX2 Inputs, outputs and stop conditions**: Inputs, outputs and stop conditions
- **CTX3 Ownership and privacy**: Ownership and privacy

## Tasks

- **T0 Weekly evidence brief assistant**: Weekly evidence brief assistant
- **T1 Freeze authorized note collection**: Freeze authorized note collection
- **T2 Find relevant and contrary passages**: Find relevant and contrary passages
- **T3 Draft decision options with citations**: Draft decision options with citations
- **T4 Check evidence and hand off weekly brief**: Check evidence and hand off weekly brief
- **A1 Frozen source and authority context**: Frozen source and authority context

## Components

- **C1 Check case envelope**: Code checks scope, current access, command and version before exposing evidence. Exact duplicate requestId/revision and same frozen source manifest yields intake.state valid with reusedArtifact. W2 supplies existing checked source view; W3 skips model and returns saved draft; W4 rechecks scope/source freshness and receipt. Replacement with changed inputs requires next revision; semantic duplicates are candidates only.
- **C2 Build trusted evidence view**: First select question and frozen collection, then retrieve both supporting and contrary passages. No relevant evidence yields an explicit gap, never a fabricated recommendation. Distinguish observed quote, inference and recommendation per claim. No participant names in output; use approved aliases. Date/week comes from staff selection, never model inference. Silence is not consensus.
- **C3 Draft bounded recommendation**: First select question and frozen collection, then retrieve both supporting and contrary passages. No relevant evidence yields an explicit gap, never a fabricated recommendation. Distinguish observed quote, inference and recommendation per claim. No participant names in output; use approved aliases. Date/week comes from staff selection, never model inference. Silence is not consensus.
- **C4 Check claims and output proof**: First select question and frozen collection, then retrieve both supporting and contrary passages. No relevant evidence yields an explicit gap, never a fabricated recommendation. Distinguish observed quote, inference and recommendation per claim. No participant names in output; use approved aliases. Date/week comes from staff selection, never model inference. Silence is not consensus. A forged or absent citation yields reason INVALID_CITATION, status needs_human. Frozen source conflict yields EVIDENCE_CONFLICT; missing source yields EVIDENCE_MISSING. Local draftId derives from requestId/revision and source manifest; do not export ready before all required source IDs and artifact receipt exist.
- **C5 Prepare human handoff**: Accept exactly one tagged handoffInput. W1 exceptions carry intake, W2 exceptions carry evidence plus intake, W4 carries checked plus intake. Create a local receipt even for exceptions; if receipt generation fails, return unconfirmed error in current caller session. No operational success claim. First select question and frozen collection, then retrieve both supporting and contrary passages. No relevant evidence yields an explicit gap, never a fabricated recommendation. Distinguish observed quote, inference and recommendation per claim. No participant names in output; use approved aliases. Date/week comes from staff selection, never model inference. Silence is not consensus.

## Workflow

- **W1 Check request**: {"state": "W1", "transitions": [{"to": "W2", "when": "intake.state == valid", "mode": "exclusive"}, {"to": "W5", "when": "intake.state in {provisional,rejected,cancelled}", "mode": "exclusive"}], "failureDisposition": "Local error receipt; owner retries a new revision after checking source problem. Never claim business success.", "timeout": "30 seconds for draft; 10 seconds per read; all others 5 seconds. Handoff returned in caller session.", "retryPolicy": "One read retry only. One model attempt; invalid or timeout becomes a needs_human packet. No automatic draft regeneration.", "terminalDisposition": "", "bindings": {"intake": "C1.intake; command and authenticated scope set on request", "evidence": "C2.evidence; frozen bundle read result", "draft": "C3.draft; schema validation adds invalid or timeout", "checked": "C4.checked; recheck before ready output", "handoffInput": "C1.intake exception at W1, C2.evidence plus intake exception at W2, or C4.checked at W4; tag selected by predecessor."}, "precedence": "Cancellation then invalid authority then missing evidence then draft. Replacement uses expectedRevision; concurrent stale revision is rejected. Outputs are session artifacts, never a sent reply or approved transaction."}
- **W2 Prepare evidence**: {"state": "W2", "transitions": [{"to": "W3", "when": "evidence.status == ready", "mode": "exclusive"}, {"to": "W5", "when": "evidence.status in {missing,stale,conflict,unavailable}", "mode": "exclusive"}], "failureDisposition": "Local error receipt; owner retries a new revision after checking source problem. Never claim business success.", "timeout": "30 seconds for draft; 10 seconds per read; all others 5 seconds. Handoff returned in caller session.", "retryPolicy": "One read retry only. One model attempt; invalid or timeout becomes a needs_human packet. No automatic draft regeneration.", "terminalDisposition": "", "bindings": {"intake": "C1.intake; command and authenticated scope set on request", "evidence": "C2.evidence; frozen bundle read result", "draft": "C3.draft; schema validation adds invalid or timeout", "checked": "C4.checked; recheck before ready output", "handoffInput": "C1.intake exception at W1, C2.evidence plus intake exception at W2, or C4.checked at W4; tag selected by predecessor."}, "precedence": "Cancellation then invalid authority then missing evidence then draft. Replacement uses expectedRevision; concurrent stale revision is rejected. Outputs are session artifacts, never a sent reply or approved transaction."}
- **W3 Draft with sources**: {"state": "W3", "transitions": [{"to": "W4", "when": "draft returned valid or abstain or invalid or timeout", "mode": "exclusive"}], "failureDisposition": "Local error receipt; owner retries a new revision after checking source problem. Never claim business success.", "timeout": "30 seconds for draft; 10 seconds per read; all others 5 seconds. Handoff returned in caller session.", "retryPolicy": "One read retry only. One model attempt; invalid or timeout becomes a needs_human packet. No automatic draft regeneration.", "terminalDisposition": "", "bindings": {"intake": "C1.intake; command and authenticated scope set on request", "evidence": "C2.evidence; frozen bundle read result", "draft": "C3.draft; schema validation adds invalid or timeout", "checked": "C4.checked; recheck before ready output", "handoffInput": "C1.intake exception at W1, C2.evidence plus intake exception at W2, or C4.checked at W4; tag selected by predecessor."}, "precedence": "Cancellation then invalid authority then missing evidence then draft. Replacement uses expectedRevision; concurrent stale revision is rejected. Outputs are session artifacts, never a sent reply or approved transaction."}
- **W4 Check draft**: {"state": "W4", "transitions": [{"to": "W5", "when": "checked produced for every draft outcome", "mode": "exclusive"}], "failureDisposition": "Local error receipt; owner retries a new revision after checking source problem. Never claim business success.", "timeout": "30 seconds for draft; 10 seconds per read; all others 5 seconds. Handoff returned in caller session.", "retryPolicy": "One read retry only. One model attempt; invalid or timeout becomes a needs_human packet. No automatic draft regeneration.", "terminalDisposition": "", "bindings": {"intake": "C1.intake; command and authenticated scope set on request", "evidence": "C2.evidence; frozen bundle read result", "draft": "C3.draft; schema validation adds invalid or timeout", "checked": "C4.checked; recheck before ready output", "handoffInput": "C1.intake exception at W1, C2.evidence plus intake exception at W2, or C4.checked at W4; tag selected by predecessor."}, "precedence": "Cancellation then invalid authority then missing evidence then draft. Replacement uses expectedRevision; concurrent stale revision is rejected. Outputs are session artifacts, never a sent reply or approved transaction."}
- **W5 Hand off with next step**: {"state": "W5", "transitions": [], "failureDisposition": "Local exception in current caller session; receiving staff owns recovery. No remote write or unknown external commit exists.", "timeout": "30 seconds for draft; 10 seconds per read; all others 5 seconds. Handoff returned in caller session.", "retryPolicy": "One read retry only. One model attempt; invalid or timeout becomes a needs_human packet. No automatic draft regeneration.", "terminalDisposition": "Return local review_ready, provisional, needs_human, rejected or cancelled packet, with owner and nextStep; if artifact receipt unavailable return ARTIFACT_UNCONFIRMED in caller session. No operational completion. Receiving staff review/acknowledge in existing tools; the assistant does not wait for a decision.", "bindings": {"intake": "C1.intake; command and authenticated scope set on request", "evidence": "C2.evidence; frozen bundle read result", "draft": "C3.draft; schema validation adds invalid or timeout", "checked": "C4.checked; recheck before ready output", "handoffInput": "C1.intake exception at W1, C2.evidence plus intake exception at W2, or C4.checked at W4; tag selected by predecessor."}, "precedence": "Cancellation then invalid authority then missing evidence then draft. Replacement uses expectedRevision; concurrent stale revision is rejected. Outputs are session artifacts, never a sent reply or approved transaction."}

## Framework

### F1 · Workflow choice

Workflow choice

Reasoning: Bound the work and make the result reviewable.

Data:

```json
{
  "category": "orchestration",
  "taskIds": [
    "T1",
    "T2",
    "T3",
    "T4"
  ],
  "choice": "A small deterministic state machine with one bounded drafting call.",
  "alternatives": [
    "Free tool-using agent; multi-agent chain."
  ],
  "tradeoffs": "Few states and no operational writes favor a simple flow; more agents add disagreement and latency.",
  "permission": "none",
  "blastRadius": "One scoped case; no operational system changes.",
  "approvalRule": "Staff review output; scope and adapter approval H1-H3 block pilot.",
  "leastPrivilege": "Separate source read principal from model; source allowlist enforced before retrieval; minimize, redact, expire per approved policy.",
  "aws": "Unverified pattern: object storage and relational run index.",
  "gcp": "Unverified pattern: object storage and relational run index.",
  "azure": "Unverified pattern: object storage and relational run index.",
  "openSource": "Unverified pattern: self-hosted object storage and PostgreSQL."
}
```


Sources:

- context / user-brief: Help a product team find evidence in its supplied research notes and draft a weekly decision brief. Cite evidence and state disagreement.

- hypothesis / H1: Use only the team-supplied, authorized note collection for the selected week and question. Draft a brief with citations, contrary evidence and gaps. Exclude web search, roadmap updates and automatic distribution.

### F2 · Permissions and data

Permissions and data

Reasoning: Bound the work and make the result reviewable.

Data:

```json
{
  "category": "permission",
  "taskIds": [
    "T1",
    "T2",
    "T3",
    "T4"
  ],
  "choice": "Read-only supplied evidence and local artifact export; no business write credentials.",
  "alternatives": [
    "Connect full operational accounts."
  ],
  "tradeoffs": "A wider connection adds exposure without helping this review-only release.",
  "permission": "read",
  "blastRadius": "One scoped case; no operational system changes.",
  "approvalRule": "Staff review output; scope and adapter approval H1-H3 block pilot.",
  "leastPrivilege": "Separate source read principal from model; source allowlist enforced before retrieval; minimize, redact, expire per approved policy.",
  "aws": "Unverified pattern: object storage and relational run index.",
  "gcp": "Unverified pattern: object storage and relational run index.",
  "azure": "Unverified pattern: object storage and relational run index.",
  "openSource": "Unverified pattern: self-hosted object storage and PostgreSQL."
}
```


Sources:

- context / user-brief: Help a product team find evidence in its supplied research notes and draft a weekly decision brief. Cite evidence and state disagreement.

- hypothesis / H1: Use only the team-supplied, authorized note collection for the selected week and question. Draft a brief with citations, contrary evidence and gaps. Exclude web search, roadmap updates and automatic distribution.

### F3 · Storage and deployment options

Storage and deployment options

Reasoning: Bound the work and make the result reviewable.

Data:

```json
{
  "category": "data",
  "taskIds": [
    "T1",
    "T2",
    "T3",
    "T4"
  ],
  "choice": "Choose encrypted existing team storage with access checks and a relational run manifest; verify environment before purchase.",
  "alternatives": [
    "AWS object store plus relational ledger; GCP object store plus relational ledger; Azure object store plus relational ledger; self-hosted object storage plus PostgreSQL. All are unverified candidate patterns."
  ],
  "tradeoffs": "Compare same criteria: scoped reads, region, retention, audit, operations effort and price. Existing team storage wins provisionally; self-hosting adds operational burden. Retrieval indexes never override original sources.",
  "permission": "read",
  "blastRadius": "One scoped case; no operational system changes.",
  "approvalRule": "Staff review output; scope and adapter approval H1-H3 block pilot.",
  "leastPrivilege": "Separate source read principal from model; source allowlist enforced before retrieval; minimize, redact, expire per approved policy.",
  "aws": "Unverified pattern: object storage and relational run index.",
  "gcp": "Unverified pattern: object storage and relational run index.",
  "azure": "Unverified pattern: object storage and relational run index.",
  "openSource": "Unverified pattern: self-hosted object storage and PostgreSQL."
}
```


Sources:

- context / user-brief: Help a product team find evidence in its supplied research notes and draft a weekly decision brief. Cite evidence and state disagreement.

- hypothesis / H1: Use only the team-supplied, authorized note collection for the selected week and question. Draft a brief with citations, contrary evidence and gaps. Exclude web search, roadmap updates and automatic distribution.


## Models

- **M1 One bounded drafting call**: One bounded drafting call

## Fmea

- **FM1 Unsupported prevalence**: Scores are hypothetical priorities: severity 1 negligible to 10 catastrophic; occurrence 1 rare to 10 frequent; detection 1 caught early to 10 unlikely detected. No risk acceptance claimed.
- **FM2 Note injection**: Scores are hypothetical priorities: severity 1 negligible to 10 catastrophic; occurrence 1 rare to 10 frequent; detection 1 caught early to 10 unlikely detected. No risk acceptance claimed.
- **FM3 Repeated observation**: Scores are hypothetical priorities: severity 1 negligible to 10 catastrophic; occurrence 1 rare to 10 frequent; detection 1 caught early to 10 unlikely detected. No risk acceptance claimed.
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
- **EV2 Unsupported prevalence**: Unsupported prevalence
- **EV3 Note injection**: Note injection
- **EV4 Repeated observation**: Repeated observation
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

### R1 · Business measure

Business measure

Reasoning: Bound the work and make the result reviewable.

Data:

```json
{
  "category": "kpi",
  "businessKpi": "Researcher active minutes per approved weekly brief; weekly sum of active minutes / approved briefs. Baseline unknown; proposed improvement goal set after baseline.",
  "aiMetrics": [
    "Fewer unsupported claims reduces rework; usefulness can lower review effort but must be measured.",
    "No private-data leakage is a safety guardrail, not a claimed time saving.",
    "Review age exposes queue capacity; latency p95 guards responsiveness."
  ],
  "phase": "baseline",
  "gate": "Collect manual active-time baseline before setting a numerical savings goal.",
  "owner": "Product research lead",
  "experiment": ""
}
```


Sources:

- context / user-brief: Help a product team find evidence in its supplied research notes and draft a weekly decision brief. Cite evidence and state disagreement.

- hypothesis / H1: Use only the team-supplied, authorized note collection for the selected week and question. Draft a brief with citations, contrary evidence and gaps. Exclude web search, roadmap updates and automatic distribution.

### R2 · Shadow on historical cases

Shadow on historical cases

Reasoning: Bound the work and make the result reviewable.

Data:

```json
{
  "category": "phase",
  "businessKpi": "Researcher active minutes per approved weekly brief; weekly sum of active minutes / approved briefs. Baseline unknown; proposed improvement goal set after baseline.",
  "aiMetrics": [
    "Fewer unsupported claims reduces rework; usefulness can lower review effort but must be measured.",
    "No private-data leakage is a safety guardrail, not a claimed time saving.",
    "Review age exposes queue capacity; latency p95 guards responsiveness."
  ],
  "phase": "shadow",
  "gate": "Entry: approved scope and lawful sample access. Exit: all release goldens and held-out citation/privacy checks pass; domain owner signs evidence.",
  "owner": "Product research lead",
  "experiment": ""
}
```


Sources:

- context / user-brief: Help a product team find evidence in its supplied research notes and draft a weekly decision brief. Cite evidence and state disagreement.

- hypothesis / H1: Use only the team-supplied, authorized note collection for the selected week and question. Draft a brief with citations, contrary evidence and gaps. Exclude web search, roadmap updates and automatic distribution.

### R3 · Assist-only pilot

Assist-only pilot

Reasoning: Bound the work and make the result reviewable.

Data:

```json
{
  "category": "phase",
  "businessKpi": "Researcher active minutes per approved weekly brief; weekly sum of active minutes / approved briefs. Baseline unknown; proposed improvement goal set after baseline.",
  "aiMetrics": [
    "Fewer unsupported claims reduces rework; usefulness can lower review effort but must be measured.",
    "No private-data leakage is a safety guardrail, not a claimed time saving.",
    "Review age exposes queue capacity; latency p95 guards responsiveness."
  ],
  "phase": "assist pilot",
  "gate": "Entry: shadow exit and H1-H3/H5 verified. Review two weekly cycles, staffed capacity confirmed. Exit: no safety failures and useful drafts >=H5; owner may extend review-only usage. Scale keeps human review and all exclusions.",
  "owner": "Product research lead",
  "experiment": ""
}
```


Sources:

- context / user-brief: Help a product team find evidence in its supplied research notes and draft a weekly decision brief. Cite evidence and state disagreement.

- hypothesis / H1: Use only the team-supplied, authorized note collection for the selected week and question. Draft a brief with citations, contrary evidence and gaps. Exclude web search, roadmap updates and automatic distribution.

### R4 · Measure review effort

Measure review effort

Reasoning: Bound the work and make the result reviewable.

Data:

```json
{
  "category": "experiment",
  "businessKpi": "Researcher active minutes per approved weekly brief; weekly sum of active minutes / approved briefs. Baseline unknown; proposed improvement goal set after baseline.",
  "aiMetrics": [
    "Fewer unsupported claims reduces rework; usefulness can lower review effort but must be measured.",
    "No private-data leakage is a safety guardrail, not a claimed time saving.",
    "Review age exposes queue capacity; latency p95 guards responsiveness."
  ],
  "phase": "assist pilot",
  "gate": "Entry uses baseline/power plan, never already-achieved pilot results. Stop for any critical failure.",
  "owner": "Product research lead",
  "experiment": "Randomize eligible case families to manual or assistant draft; stratify routine/exception and operator. Same source family stays in one arm; hide treatment drafts from control. Collect baseline variance of active minutes, choose minimum useful difference with owner, compute two-sample mean power and adjust operator clustering; do not assert sample size before baseline. Observe two weekly cycles or powered sample, whichever later; calendar duration H3 needs approval."
}
```


Sources:

- context / user-brief: Help a product team find evidence in its supplied research notes and draft a weekly decision brief. Cite evidence and state disagreement.

- hypothesis / H1: Use only the team-supplied, authorized note collection for the selected week and question. Draft a brief with citations, contrary evidence and gaps. Exclude web search, roadmap updates and automatic distribution.

### R5 · Accountable owner and stop plan

Accountable owner and stop plan

Reasoning: Bound the work and make the result reviewable.

Data:

```json
{
  "category": "owner",
  "businessKpi": "Researcher active minutes per approved weekly brief; weekly sum of active minutes / approved briefs. Baseline unknown; proposed improvement goal set after baseline.",
  "aiMetrics": [
    "Fewer unsupported claims reduces rework; usefulness can lower review effort but must be measured.",
    "No private-data leakage is a safety guardrail, not a claimed time saving.",
    "Review age exposes queue capacity; latency p95 guards responsiveness."
  ],
  "phase": "all",
  "gate": "Lead owns backlog, privacy incident response and release decision; technical owner owns adapters and evidence receipts. Stop use on safety breach; preserve scoped audit then manual fallback.",
  "owner": "Product research lead",
  "experiment": ""
}
```


Sources:

- context / user-brief: Help a product team find evidence in its supplied research notes and draft a weekly decision brief. Cite evidence and state disagreement.

- hypothesis / H1: Use only the team-supplied, authorized note collection for the selected week and question. Draft a brief with citations, contrary evidence and gaps. Exclude web search, roadmap updates and automatic distribution.


## Export

### X1 · Build a review-only tool

Build a review-only tool

Reasoning: Bound the work and make the result reviewable.

Data:

```json
{
  "acceptanceCriteria": [
    "Every T1-T4 leaf has components, workflow nodes and concrete goldens.",
    "No sending, operational update, payment, identity grant or roadmap write adapter exists.",
    "All listed release suite goldens and reciprocal risk links are maintained.",
    "H1-H3/H5 remain launch blockers until real owners verify them."
  ],
  "buildInstructions": "Implement typed C1-C5 and exclusive W1-W5 contracts, source evidence and version records, schema checks, scoped reads and local artifact receipts. Persist run manifests only under approved retention policy; no business connectors. Use CASE/requestId and expectedRevision to reject concurrent old changes. Implement deterministic domain checks: First select question and frozen collection, then retrieve both supporting and contrary passages. No relevant evidence yields an explicit gap, never a fabricated recommendation. Distinguish observed quote, inference and recommendation per claim. No participant names in output; use approved aliases. Date/week comes from staff selection, never model inference. Silence is not consensus. Build future fixture harness from eval-set.json and keep synthetic versus actual evidence separate. Release uses all goldens in EV release entry and held-out staff labels; review-only stop returns work to staff. Run no provider or operational call from this design. After delivering the PDF ask exactly once: “Would you also like a visual HTML version in the same ten-stage structure as the app?” No HTML before opt-in."
}
```


Sources:

- context / user-brief: Help a product team find evidence in its supplied research notes and draft a weekly decision brief. Cite evidence and state disagreement.

- hypothesis / H1: Use only the team-supplied, authorized note collection for the selected week and question. Draft a brief with citations, contrary evidence and gaps. Exclude web search, roadmap updates and automatic distribution.


Full exact data and source evidence: [design.json](design.json). Launch facts and owners: [assumptions.md](assumptions.md).
