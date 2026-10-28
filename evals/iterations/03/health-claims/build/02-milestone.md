# Explanation and rule engine

> PASS | DESIGN ONLY. self-review; round 3.

Depends on earlier milestones where their outputs are inputs below. Cross-milestone shared types are read by ID from ../design.json, not copied.

## Selected contracts

### C3 · Explain evidence

No authority. Context maximum 8000 tokens; longer files route to staff rather than silent truncation. Structured output validation and a single retry; 30s each; no tools or memory.

Reasoning: Bounded responsibility with an owned safe outcome.

Assumptions:

- H1

- H2

- H3

- H4

Data:

```json
{
  "group": "Agents (LLM)",
  "taskIds": [
    "T3"
  ],
  "inputs": [
    "evidence: authorized verified visible text only",
    "ruleSummary: trusted clause descriptions"
  ],
  "outputs": [
    "explanation: structured {claims:[{documentHash,page,clause,quote,interpretation}],disposition: supported|abstain}",
    "draftStatus: enum valid|abstain|unavailable"
  ],
  "whyCode": "",
  "approvalRule": "Draft publication only; no insurer adjudication or settlement authority. Fresh caller role required; staff event bound to exact snapshot where review is needed."
}
```


Sources:

- context / user-brief: Policies can change over time and bills may include room-rent limits.

- hypothesis / H1: First release publishes staff-facing recommendations only; all settlement, denial notices and appeals stay outside this assistant.

- hypothesis / H2: Insurer supplies signed, effective-dated policy rule packs, member linkage, authority and case APIs with version checks and operation readback.

- hypothesis / H3: Privacy owner selects deployment region, role access, lawful processing basis, document retention and model contract; proposed documents TTL 30 days, minimal audit 365 days, legal hold overrides deletion.

- hypothesis / H4: Claims team covers a 24-hour elapsed-time review deadline, four-hour acknowledgement and a one-hour visible waiting status.

### C4 · Validate policy and calculate

Match every quote byte-for-byte after fixed whitespace normalization to admitted document/page/clause; validate policy dates in code. Parse bill quantities into integer minor units via deterministic schema; ambiguous digit or currency needs staff. No model amount accepted. Proposed engine: rule pack explicitly sets admission/service-date applicability, room-day counting, rounding, room-only vs proportional-linked-charge reduction, exclusions, deductibles, copay order and remaining cover. Each must be certified H2. Synthetic rule RV1: 2 counted days, room cap 500000 minor/day; room charge 1200000 => eligible room 1000000. Other eligible charge 2000000 stays whole for room-only rule => 3000000 total. RV2 proportional rule applies 5/6 only to explicitly linked 1800000, unlinked 200000 => 1000000+1500000+200000=2700000. Round each affected line half-up to minor unit; duplicate lines flagged, not dropped silently. Unknown proration, date gaps, endorsements or accumulator freshness => review with no authoritative total. No deductible/copay assumed absent: explicit zero rules required. First release supports only explicit zero deductible and zero copay; nonzero values, mixed currency or service dates spanning rule periods route review. Apply min(calculated eligible, fresh remainingCoverMinor); remaining cover comes from an authoritative accumulator version, not document text. This recommendation reserves no benefits; fresh recheck by insurer is mandatory before settlement. Exclude clinical necessity, fraud and medically coded exclusion judgement from automated calculation; route these to staff. Monetary inputs must be nonnegative signed-64-bit integers in one trusted currency. Reject negative/overflow values. Day count must match certified admission/discharge convention; do not use a model date. Missing accumulator version or staleness => review.

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
    "T3",
    "T4"
  ],
  "inputs": [
    "snapshot: trusted case/service dates and current rule registry",
    "evidence: verified page and clause spans",
    "explanation: untrusted model explanation"
  ],
  "outputs": [
    "assessment: trusted {status: draft|review,eligibleMinor?,currency?,ruleVersion,lines,reasons,sourceRefs}",
    "calcStatus: enum draft|review"
  ],
  "whyCode": "Match every quote byte-for-byte after fixed whitespace normalization to admitted document/page/clause; validate policy dates in code. Parse bill quantities into integer minor units via deterministic schema; ambiguous digit or currency needs staff. No model amount accepted.",
  "approvalRule": "Draft publication only; no insurer adjudication or settlement authority. Fresh caller role required; staff event bound to exact snapshot where review is needed."
}
```


Sources:

- context / user-brief: Policies can change over time and bills may include room-rent limits.

- hypothesis / H1: First release publishes staff-facing recommendations only; all settlement, denial notices and appeals stay outside this assistant.

- hypothesis / H2: Insurer supplies signed, effective-dated policy rule packs, member linkage, authority and case APIs with version checks and operation readback.

- hypothesis / H3: Privacy owner selects deployment region, role access, lawful processing basis, document retention and model contract; proposed documents TTL 30 days, minimal audit 365 days, legal hold overrides deletion.

- hypothesis / H4: Claims team covers a 24-hour elapsed-time review deadline, four-hour acknowledgement and a one-hour visible waiting status.

## Workflow rules

### W3 · Draft explanation

{"state": "Draft explanation", "transitions": [{"to": "W4", "when": "draftStatus=valid", "mode": "exclusive"}, {"to": "W5", "when": "draftStatus in {abstain,unavailable}", "mode": "exclusive"}], "failureDisposition": "Preserve metadata and owned manual-review state; no claim payment or final denial.", "timeout": "30 seconds per call", "retryPolicy": "At most one output/schema retry, total two calls", "terminalDisposition": "", "guardBindings": "Predicates use the named component output enum, updated once on response; precedence follows listed enum cases. No LLM-generated guard is authoritative."}

Reasoning: Bounded responsibility with an owned safe outcome.

Assumptions:

- H1

- H2

- H4

Data:

```json
{
  "componentId": "C3",
  "taskIds": [
    "T3"
  ],
  "next": [
    "W4",
    "W5"
  ],
  "decision": true,
  "example": "HC-1 follows only the matching output enum."
}
```


Sources:

- context / user-brief: Policies can change over time and bills may include room-rent limits.

- hypothesis / H1: First release publishes staff-facing recommendations only; all settlement, denial notices and appeals stay outside this assistant.

- hypothesis / H2: Insurer supplies signed, effective-dated policy rule packs, member linkage, authority and case APIs with version checks and operation readback.

- hypothesis / H4: Claims team covers a 24-hour elapsed-time review deadline, four-hour acknowledgement and a one-hour visible waiting status.

### W4 · Check quotes and calculate

{"state": "Check quotes and calculate", "transitions": [{"to": "W7", "when": "calcStatus=draft", "mode": "exclusive"}, {"to": "W5", "when": "calcStatus=review", "mode": "exclusive"}], "failureDisposition": "Preserve metadata and owned manual-review state; no claim payment or final denial.", "timeout": "10 seconds", "retryPolicy": "No automatic retry", "terminalDisposition": "", "guardBindings": "Predicates use the named component output enum, updated once on response; precedence follows listed enum cases. No LLM-generated guard is authoritative."}

Reasoning: Bounded responsibility with an owned safe outcome.

Assumptions:

- H1

- H2

- H4

Data:

```json
{
  "componentId": "C4",
  "taskIds": [
    "T3",
    "T4"
  ],
  "next": [
    "W7",
    "W5"
  ],
  "decision": true,
  "example": "HC-1 follows only the matching output enum."
}
```


Sources:

- context / user-brief: Policies can change over time and bills may include room-rent limits.

- hypothesis / H1: First release publishes staff-facing recommendations only; all settlement, denial notices and appeals stay outside this assistant.

- hypothesis / H2: Insurer supplies signed, effective-dated policy rule packs, member linkage, authority and case APIs with version checks and operation readback.

- hypothesis / H4: Claims team covers a 24-hour elapsed-time review deadline, four-hour acknowledgement and a one-hour visible waiting status.

## Required tests

For each ID below, load ../eval-set.json items[id].data.input, .expected and .passRule. These are the full fixture, expected result and exact assertions; no inherited test context is assumed.

- EV1: Valid room-only recommendation
- EV3: Stale operative policy withheld
- EV4: Explicit proportional room rule
- EV5: Missing room rule is not invented
- EV6: Isolated citation check page
- EV7: Isolated citation check clause
- EV8: Isolated citation check text
- EV9: Hidden instructions excluded
- EV17: Conflicting source evidence abstains
- EV19: Held-out source and arithmetic validation
- EV21: Release regression gate
- EV22: Policy boundary uses service date, not current date
- EV23: Fresh remaining cover caps the recommendation
- EV24: Nonzero copay stays with staff
- EV26: Unverified OCR has no authoritative total
- EV30: Half-up rounding is visible at a minor unit
- EV31: Negative charge cannot become a draft
## Acceptance criteria

- Implement exact selected contracts and all named tests; complete H1-H4 evidence before live PHI.
- Do not expand settlement authority; preserve failure ownership and source versions.
