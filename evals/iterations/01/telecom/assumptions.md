# Telecom complaint and service credit assistant

> PASS · DESIGN ONLY. Review is a design judgement; no business controls or provider reliability were executed.

Review method: self-review; round 2.

Review dimensions (supplied scores):

- D1: 3/4 — CTX1-CTX3 distinguish eligible service credits from manual cash refunds/invoice correction; T0-T4 cover checked scope, investigation, exclusive route and proof.
- D2: 3/4 — All leaf tasks map to components, W nodes and golden evals; FM eval lists derived from actual EV relations including monitoring/release. Exact brief retained; H1-H5 distinguish proposed policies from facts.
- D3: 3/4 — W6 notice branch has bounded ENTRY/H24 sequence and 48h terminal ownership; W9 uncertain outcomes go exclusively to W10; only definitive absence re-enters W8 once with stable operationId.
- D4: 3/4 — C1-C10 declare scope, input/output enums, immutable plan fields, adapter outcomes, proof and human events. H2 makes real provider contracts a prerequisite. C8 malformed success is normalized UNKNOWN_COMMIT per X1.
- D5: 3/4 — C1 scope before C2; C7/C8 active/version/revocation checks and atomic eventKey uniqueness. C3 produces explanation/disposition only. W11 verifies postingId and matching receipt before W13.
- D6: 3/4 — H1-H4 clearly block launch pending policy, API, queue and privacy verification; H5 prices/volume labelled illustrative. C2/C4 abstain on missing/conflicting records.
- D7: 3/4 — F1 chooses durable code workflow versus planner and request handler using wait/recovery needs. F2-F4 assign state, privileges and coherent cloud/open-source candidates with unverified status.
- D8: 3/4 — M1 only for C3: expected1.1/max2 attempts,2000/300 tokens,$1/$4 illustrative prices,$0.00352/case and$35.20/10000. Standard/reasoning and tuning choices tied to evidence.
- D9: 3/4 — FM1-FM9 cover wrong service, stale authority, duplicate/concurrent writes, unknown posting, injection, false proof, waiting failure, contradictions and cancellation. Each has owner/release gate and specific golden coverage.
- D10: 3/4 — EV1-EV20 are self-contained JSON fixtures with exact expected effects and pass assertions, both polarities for service_credit; EV11 now scripts hidden provider absence while preserving visible uncertainty. EV21-EV23 define offline, monitoring and full release execution; no claim they ran.
- D11: 3/4 — R1 denominators/windows and baseline collection precede effect claims. R2-R5 use distinct entry/exit gates. R6 account randomization, strata, follow-up, two-proportion power and cluster correction are explicit. Safety veto separate from averages.
- D12: 3/4 — X1 and milestones01-03 derive scope, selected component/branch/test contracts and launch blockers. Export validated; full fixtures remain in indexed companion. Live execution and HTML excluded until separate authority/opt-in.

Review findings:

- ISSUE1 [major, resolved] framework/F1: Repaired F1-F4 alternatives to arrays; complete validator now passes. M1 nonempty description also repaired after validator finding.
- ISSUE2 [major, resolved] evals/EV11: Fixture now specifies providerHiddenOutcome.committed=false, invisible to assistant; ambiguity still freezes event key and forbids subsequent POST. Actual eval and semantic fixture remain identical.

## Proposed assumption ledger

### H1

Proposed pilot policy P1: verified outage credits equal floor(monthly recurring service charge in minor units × verified outage seconds / billing-period seconds), capped at the remaining recurring charge. Auto cap is 1000 minor units INR per incident; poor speed without a verified service breach and billing errors require supervisor review.

Why: A safe narrow first release needs an explicit rule.

Proposed owner: Billing policy owner

Validation: Approve currency, tax, rounding, eligibility, caps, overlapping incidents and legal treatment.

Launch blocker: true

### H2

Account, service and billing adapters must offer authenticated tenant/subject reads, active connection version checks, scoped credit posting with a unique business-event key and definitive operation readback.

Why: Unknown provider capabilities block safe writes.

Proposed owner: Billing engineering owner

Validation: Sandbox contract tests prove atomic duplicate exclusion, commit proof and readback; otherwise assist-only.

Launch blocker: true

### H3

Proposed supervisor queue is staffed continuously, acknowledges cases within 1 elapsed hour, decides within 48 elapsed hours, and a duty manager owns overdue cases. Portal updates appear on entry and at 24 hours; overdue notice appears at 48 hours.

Why: 48-hour wait requires a real owner and clock.

Proposed owner: Support operations owner

Validation: Staffing, portal access, event schemas and durable scheduler sign-off.

Launch blocker: true

### H4

Proposed retention is 30 days for redacted model traces and 365 days for financial audit; deployment region, deletion exceptions and customer permissions need privacy review.

Why: No jurisdiction or retention rules supplied.

Proposed owner: Privacy and security owner

Validation: Approve data map, roles, residency and retention before real customer data.

Launch blocker: true

### H5

Illustrative traffic is 10000 cases/month; one explanation call per case, maximum two attempts. Assume 10% retry rate and 2000 input/300 output tokens at $1/$4 per million tokens.

Why: Budget only; no provider selected or measured usage.

Proposed owner: Product and model owner

Validation: Replace with quotes, measured branch mix, token and latency benchmarks.

Launch blocker: false

- components/C2: H2
- components/C7: H2
- components/C8: H2
- components/C9: H2
- framework/F1: H2
- framework/F1: H4
- framework/F2: H2
- framework/F2: H4
- framework/F3: H2
- framework/F3: H4
- framework/F4: H2
- framework/F4: H4
- models/M1: H5
- fmea/FM1: H1
- fmea/FM1: H2
- fmea/FM1: H3
- fmea/FM2: H1
- fmea/FM2: H2
- fmea/FM2: H3
- fmea/FM3: H1
- fmea/FM3: H2
- fmea/FM3: H3
- fmea/FM4: H1
- fmea/FM4: H2
- fmea/FM4: H3
- fmea/FM5: H1
- fmea/FM5: H2
- fmea/FM5: H3
- fmea/FM6: H1
- fmea/FM6: H2
- fmea/FM6: H3
- fmea/FM7: H1
- fmea/FM7: H2
- fmea/FM7: H3
- fmea/FM8: H1
- fmea/FM8: H2
- fmea/FM8: H3
- fmea/FM9: H1
- fmea/FM9: H2
- fmea/FM9: H3
- evals/EV1: H1
- evals/EV1: H2
- evals/EV1: H3
- evals/EV2: H1
- evals/EV2: H2
- evals/EV2: H3
- evals/EV3: H1
- evals/EV3: H2
- evals/EV3: H3
- evals/EV4: H1
- evals/EV4: H2
- evals/EV4: H3
- evals/EV5: H1
- evals/EV5: H2
- evals/EV5: H3
- evals/EV6: H1
- evals/EV6: H2
- evals/EV6: H3
- evals/EV7: H1
- evals/EV7: H2
- evals/EV7: H3
- evals/EV8: H1
- evals/EV8: H2
- evals/EV8: H3
- evals/EV9: H1
- evals/EV9: H2
- evals/EV9: H3
- evals/EV10: H1
- evals/EV10: H2
- evals/EV10: H3
- evals/EV11: H1
- evals/EV11: H2
- evals/EV11: H3
- evals/EV12: H1
- evals/EV12: H2
- evals/EV12: H3
- evals/EV13: H1
- evals/EV13: H2
- evals/EV13: H3
- evals/EV14: H1
- evals/EV14: H2
- evals/EV14: H3
- evals/EV15: H1
- evals/EV15: H2
- evals/EV15: H3
- evals/EV16: H1
- evals/EV16: H2
- evals/EV16: H3
- evals/EV17: H1
- evals/EV17: H2
- evals/EV17: H3
- evals/EV18: H1
- evals/EV18: H2
- evals/EV18: H3
- evals/EV19: H1
- evals/EV19: H2
- evals/EV19: H3
- evals/EV20: H1
- evals/EV20: H2
- evals/EV20: H3
- rollout/R1: H1
- rollout/R1: H2
- rollout/R1: H3
- rollout/R1: H4
- rollout/R1: H5
- rollout/R2: H1
- rollout/R2: H2
- rollout/R2: H3
- rollout/R2: H4
- rollout/R2: H5
- rollout/R3: H1
- rollout/R3: H2
- rollout/R3: H3
- rollout/R3: H4
- rollout/R3: H5
- rollout/R4: H1
- rollout/R4: H2
- rollout/R4: H3
- rollout/R4: H4
- rollout/R4: H5
- rollout/R5: H1
- rollout/R5: H2
- rollout/R5: H3
- rollout/R5: H4
- rollout/R5: H5
- rollout/R6: H1
- rollout/R6: H2
- rollout/R6: H3
- rollout/R6: H4
- rollout/R6: H5
- rollout/R7: H1
- rollout/R7: H2
- rollout/R7: H3
- rollout/R7: H4
- rollout/R7: H5

## Review and tooling limitations

- Self-review is AI judgement, not independent review or stakeholder approval. Root is obtaining a separate review.
- Validator passes schema and declared semantic invariants only; no business assertions, adapters, model behavior, staffing, costs or production reliability have been executed or verified.
- H1-H4 are live-launch blockers. H5 cost and traffic assumptions require measurement. Portal progress requires customers to revisit/poll; no SMS/email connector is included.
- Design-only tooling: this helper makes no provider, network or business API calls and executes no business assertions; optional host-assistant research is outside this statement.
- Schema, reference, graph and ID-coverage checks do not establish semantic completeness, source truth, actual human authorization or production safety.
- Review scores and evidence are supplied by the reviewing agent; the helper checks their shape and declared pass conditions, not their truth.
- FMEA action/control text is required where specified; the helper does not verify ownership, release authority, regulatory compliance or risk acceptance.
