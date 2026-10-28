# Inpatient claim review assistant

> PASS · DESIGN ONLY. Review is a design judgement; no business controls or provider reliability were executed.

Review method: self-review; round 2.

Review dimensions (supplied scores):

- D1: 3/4 — CTX1/CTX3 and T1-T5 bound draft-only inpatient review and owned pending outcomes.
- D2: 3/4 — T1-T5 link C1-C7/W1-W8 and EV1-EV20; FM links derived in both directions.
- D3: 3/4 — W4 timeout/unknown to W5; W5 bounded reads; W6 proof before W7; W8 owns unresolved outcomes.
- D4: 3/4 — C1-C7 typed contracts separate read, draft-write and readback; H3 marks adapter capability unverified.
- D5: 3/4 — C3 uses approved policy and human-verified facts; C4 cannot pay/deny; C6 durable assignment proof.
- D6: 3/4 — H1-H6 mark proposed scope, rules, ownership, privacy and budgets; no clinical/legal claims.
- D7: 3/4 — F1-F4 select code worker; reject in-memory and unconstrained agents; candidates explicitly unverified.
- D8: 3/4 — M1 gives W2-only calls 1.05 expected/2 maximum, USD .0378 illustrative and fallback.
- D9: 3/4 — FM1-FM7 specific subject, policy, room-cap, injection, duplicate, uncertainty and queue risks, owner gates.
- D10: 3/4 — EV1-EV17 self-contained synthetic fixtures, EV18 held-out, EV19 operations and EV20 inclusion assertions.
- D11: 3/4 — R1-R7 define denominators, baseline, mean-test power plan, cluster assignment and assist-only scale.
- D12: 3/4 — X1 and milestones select exact contracts; no final claim writes or fabricated launch evidence.

Review findings:

- ISSUE1 [major, resolved] context/CTX1: Initial artifact left descriptions empty on many cards; validator rejects incomplete cards. Fill specific summaries and revalidate. Repaired and inspected in current design; validator now passes.
- ISSUE2 [major, resolved] workflow/W8: W8 lists T1/T4 but C7 serves only T5. Align display responsibility with T5. Repaired and inspected in current design; validator now passes.
- ISSUE3 [major, resolved] evals/EV9: Missing-proof fixture says start after prior operation but includes a POST in mocks. Explicitly start proof stage and remove POST to isolate guard. Repaired and inspected in current design; validator now passes.

## Proposed assumption ledger

### H1

First release creates review packets only. Claims staff approve all eligible recommendations, exceptions and rejection candidates; no settlement, denial notice or payment is automated.

Why: Bounds harm while rules and evidence are verified.

Proposed owner: Claims lead

Validation: Approve scope, queue and final decision process.

Launch blocker: true

### H2

Insurer supplies immutable policy editions, endorsements, precedence rules and effective-date selection plus verified structured bill facts. Room-rent proration applies only when the approved policy rule explicitly names affected charge classes.

Why: No insurance interpretation is established by the brief.

Proposed owner: Policy owner

Validation: Sign versioned rule fixtures including dates, caps, deductible, coinsurance, rounding and exclusions.

Launch blocker: true

### H3

Adapters support tenant-scoped reads and an atomic, conditional review-packet insert with unique submission key, immutable body, assigned reviewer and durable record lookup.

Why: Recovery and audit depend on real API support.

Proposed owner: Platform owner

Validation: Contract spike proves conditional create, conflict, revoked access, timeout and lookup consistency.

Launch blocker: true

### H4

Medical documents stay in an approved regional encrypted store. Only minimum redacted pages reach an approved zero-training model endpoint; raw content is excluded from logs. Proposed packet retention is 90 days, subject to insurer approval and legal hold.

Why: The brief provides no jurisdiction, consent, residency or retention policy.

Proposed owner: Privacy owner

Validation: Approve lawful access, region, model terms, retention, deletion and incident response.

Launch blocker: true

### H5

Review queue acknowledges assignment within 4 business hours and alerts its supervisor after 1 business day; claims remain pending throughout. UTC timers use a versioned insurer business calendar.

Why: Prevents stalled exceptions being reported as resolved.

Proposed owner: Claims lead

Validation: Approve calendar, staffing, notice templates, SLA and escalation ownership.

Launch blocker: true

### H6

Illustrative budget is 1000 cases/month; one standard model call costs assumed USD 2/M input tokens and USD 8/M output tokens, with 5% single retry.

Why: Prices and traffic have not been measured or verified.

Proposed owner: Product owner

Validation: Replace with approved quote and measured branch mix; no launch dependency.

Launch blocker: false

- context/CTX1: H1
- context/CTX2: H2
- context/CTX3: H1
- tasks/T0: H1
- tasks/T1: H1
- tasks/T2: H1
- tasks/T3: H1
- tasks/T4: H1
- tasks/T5: H1
- tasks/A1: H1
- tasks/A2: H1
- tasks/A3: H1
- components/C1: H3
- components/C2: H4
- components/C3: H2
- components/C4: H3
- components/C5: H3
- components/C6: H3
- components/C7: H3
- workflow/W1: H1
- workflow/W2: H1
- workflow/W3: H1
- workflow/W4: H1
- workflow/W5: H1
- workflow/W6: H1
- workflow/W7: H1
- workflow/W8: H1
- framework/F1: H3
- framework/F2: H3
- framework/F3: H3
- framework/F4: H4
- models/M1: H6
- fmea/FM1: H1
- fmea/FM2: H1
- fmea/FM3: H1
- fmea/FM4: H1
- fmea/FM5: H1
- fmea/FM6: H1
- fmea/FM7: H1
- evals/EV1: H2
- evals/EV2: H2
- evals/EV3: H2
- evals/EV4: H2
- evals/EV5: H2
- evals/EV6: H2
- evals/EV7: H2
- evals/EV8: H2
- evals/EV9: H2
- evals/EV10: H2
- evals/EV11: H2
- evals/EV12: H2
- evals/EV13: H2
- evals/EV14: H2
- evals/EV15: H2
- evals/EV16: H2
- evals/EV17: H2
- evals/EV18: H1
- evals/EV19: H1
- evals/EV20: H1
- rollout/R1: H1
- rollout/R2: H1
- rollout/R3: H1
- rollout/R4: H1
- rollout/R5: H1
- rollout/R6: H1
- rollout/R7: H1
- export/X1: H1

## Review and tooling limitations

- Self-review by design author; independent reviewer has not evaluated these files.
- Schema and semantic declarations do not execute business controls or establish provenance truth.
- Synthetic policy, proposed API support, privacy rules and human queue SLA require H1-H5 owner evidence.
- No live claim, medical advice, final decision, cost quote or measured savings is represented.
- Human review resolution is outside the first-release workflow; the existing insurer queue must prove H5 assignment, acknowledgement and overdue alerts. Packet-ready is not claim approved.
- Design-only tooling: this helper makes no provider, network or business API calls and executes no business assertions; optional host-assistant research is outside this statement.
- Schema, reference, graph and ID-coverage checks do not establish semantic completeness, source truth, actual human authorization or production safety.
- Review scores and evidence are supplied by the reviewing agent; the helper checks their shape and declared pass conditions, not their truth.
- FMEA action/control text is required where specified; the helper does not verify ownership, release authority, regulatory compliance or risk acceptance.
