# Telecom complaint and service credit assistant

> PASS · DESIGN ONLY. Review is a design judgement; no business controls or provider reliability were executed.

Review method: independent-agent; round 2.

Review dimensions (supplied scores):

- D1: 3/4 — CTX1–CTX3 and T0/T3 define the authenticated complaint boundary, sequential investigation and exclusive automatic/human/no-credit outcomes. Speed, billing, cash refunds and invoice correction have explicit owned limits; C1/W1 now specify selection clarification and resumption.
- D2: 3/4 — Current T1/T2/T3.1/T3.2/T3.3/T4 reach C1–C11, W1–W14 and EV1–EV26. FM1–FM9 risk links are reciprocal; H1–H5 distinguish proposed facts. Actual eval-set equals canonical evals; all23 semantic golden fixtures equal decoded input/expected with consistent integer write assertions. Revised EV13 names C9/C11, and selected milestones now include the correction.
- D3: 3/4 — W1 establishes entry; W13 proves credit and W14 shows proved case outcomes. W6 persists 1h acknowledgement and original 48h deadline, with ENTRY/H24 notice sequence. W9 uncertain outcomes must enter W10; DEFINITIVELY_ABSENT permits at most one W8 revalidation and same-operation retry. C9 freezes unresolved event keys across logout and worker failure.
- D4: 3/4 — C1–C11 separate scoped reads, bounded explanation, amount calculation, approval, internal portal notice, fresh validation, financial write, readback and two proof guards. CreditPlan enumerates financial/version fields; C8 provides typed write/error outcomes; C5 specifies queue, owner and timing. H2/H4 explicitly block use until real adapters, privacy and atomic preconditions are verified.
- D5: 3/4 — C3 has no tools or money/date/identity outputs. C4 computes integer credit; C7/C8 reconstruct and atomically validate exact signed or policy plan and invoice entitlement version. C10 requires direct committed postingId, C11 cannot claim credit from case proof. F3/H4 bound least privilege, tenant scope and retention. EV24 exercises monthly cumulative balance, EV25 selection and EV26 amount-bound approval.
- D6: 3/4 — CTX3 explicitly says no company policy, API support, staffing or savings is verified. H1–H4 are live-launch blockers; H5 cost/traffic is illustrative. Missing/conflicting evidence routes to supervisor without invented entitlement. F4 names provider candidates without live capability/compliance claims.
- D7: 3/4 — F1 selects one durable code state machine and transactional outbox for timers/recovery, rejecting free-running planner and synchronous handler. F2/F3 specify financial truth and permission separation. F4 lists AWS/GCP/Azure/open-source data/secret candidates against common retention/residency/audit/restore/operator criteria, with provider decision explicitly deferred to H4 verification. Quantified provider comparison is a non-blocking follow-up for this bounded provider-neutral design.
- D8: 3/4 — C3 has exactly one plan M1. Independently recomputed $0.0032/call at2000 input/300 output and $1/$4 per million; 1.1 expected calls gives $0.00352/case and $35.20/10000; worst2 calls=$0.0064. Max2 attempts and20s budget, deterministic fallback, excluded costs and held-out fine-tuning criteria are explicit.
- D9: 3/4 — FM1–FM9 cover wrong scope, stale entitlement/authority, duplicates, uncertain commit, injection, false completion, stalled queue, conflicting evidence and reordered cancellation/approval. Each names affected tasks/components, hypothetical S/O/D, owner, prevention/detection and specific linked cases. EV24–EV26 substantively extend invoice race, selection and approval tamper coverage.
- D10: 3/4 — Current23 goldens inspected and exact fixture/write assertions checked. EV1/EV2 compute1000/2000; EV18 caps at500; EV24 two distinct500 incident plans consume one500 invoice balance atomically; EV25 blocks ambiguous selection and EV26 isolates submitted2100 vs signed2000. EV9/EV10/EV11 cover committed, definitively absent and unresolved recovery.; EV13 now supplies malformed C8 response, three explicit C9 UNRESOLVED results at5/30/120s and C11 PROVEN_CASE. C8 normalization mandates W9→W10; unresolved leads W12→W14 PENDING_RECONCILIATION with Billing Operations, zero actual commits, one attempt, no C10/W13. Hidden no-commit remains harness-only. Exact expected fields equal passRule.equals; semantic fixture is identical. Prior IR1 is resolved.; EV21–EV23 specify strata, double labelling, component/end-to-end checks, continuous safety and queue monitoring, and mandatory exact goldens. Business harness remains future work and is not claimed executed.
- D11: 3/4 — R1 defines seven-day reopen denominator and elapsed decision metrics, safety separately. R2–R5 specify shadow/assist/pilot/scale, H1–H4 gates and disabling new writes while preserving readback. R6 defines sticky account randomization, strata, contamination controls, baseline-dependent power/design effect, four-week observation plus7d follow-up and immediate safety stop. R7 assigns queue and reconciliation owners.
- D12: 3/4 — Current PRD/architecture/eval-set/build00–03 compared with canonical component and workflow IDs. EV13 correction is preserved in eval-set and C11 milestone selection; X1 retains explicit build/launch blockers and design-only scope. No new business scope or authority introduced. Review/export status is independent round2 design-pass, never production certification.

Review findings:

- IR1 [major, resolved] evals/EV13: Resolved in current iteration06: C8 malformed success routes UNKNOWN_COMMIT through W10/C9; explicit5/30/120s unresolved results lead C11-owned PENDING_RECONCILIATION. Expected trace forbids C10/W13, second POST and invented absence. Exact expected fields/write counts, semantic fixture and milestone links agree.
- IR2 [minor, OPEN] framework/F4: Provider families and common comparison criteria are explicit, but no measured or scored tradeoff assessment is supplied. H4 keeps vendor/residency selection unresolved safely; complete the bounded comparison and operational restore/timer evidence before deployment.

## Proposed assumption ledger

### H1

Proposed pilot policy P1: verified outage credits equal floor(monthly recurring service charge in minor units × verified outage seconds / billing-period seconds), capped at the remaining recurring charge. Auto cap is 1000 minor units INR per incident; poor speed without a verified service breach and billing errors require supervisor review.

Why: A safe narrow first release needs an explicit rule.

Proposed owner: Billing policy owner

Validation: Approve currency, tax, rounding, eligibility, caps, overlapping incidents and legal treatment.

Launch blocker: true

### H2

Account, service and billing adapters must offer authenticated tenant/subject reads, active connection version checks, scoped credit posting with a unique business-event key and definitive operation readback. Financial API must also atomically compare and consume invoice entitlement versions across different incident keys.

Why: Unknown provider capabilities block safe writes.

Proposed owner: Billing engineering owner

Validation: Sandbox contract tests prove atomic duplicate exclusion, commit proof and readback; otherwise assist-only. Race two distinct incident credits against the same remaining invoice balance and prove one rejects the stale entitlement version.

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
- evals/EV24: H1
- evals/EV24: H2
- evals/EV24: H3
- evals/EV25: H1
- evals/EV25: H2
- evals/EV25: H3
- evals/EV26: H1
- evals/EV26: H2
- evals/EV26: H3
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

- Independent second-round review of actual iteration06 source; current design differs from05 only in EV13 plus its semantic fixture and milestone links. No author self-review/provenance was used as evaluative evidence.
- Scores are bounded AI design judgement, not production, regulatory, API support or measured accuracy evidence. No live provider or business actions executed.
- Bundled validation independently returns structural-pass/verified-declarations. All23 golden fixture copies, asserted write counts and cited arithmetic were checked; this is not execution of the proposed business harness.
- PDF pages1–3 require inspection at72dpi/100%; completed results and current source hashes are recorded in grader.json.
- Design-only tooling: this helper makes no provider, network or business API calls and executes no business assertions; optional host-assistant research is outside this statement.
- Schema, reference, graph and ID-coverage checks do not establish semantic completeness, source truth, actual human authorization or production safety.
- Review scores and evidence are supplied by the reviewing agent; the helper checks their shape and declared pass conditions, not their truth.
- FMEA action/control text is required where specified; the helper does not verify ownership, release authority, regulatory compliance or risk acceptance.
