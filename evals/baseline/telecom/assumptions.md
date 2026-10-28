# Telecom complaint investigation and controlled service credits

> PASS · DESIGN ONLY. Review is a design judgement; no business controls or provider reliability were executed.

Review method: self-review; round 2.

Review dimensions (supplied scores):

- D1: 3/4 — CTX1-CTX7 and T0-T5 bound intake, evidence, three resolution outcomes, cancellation and owned holds; scope excludes autonomous cash refund.
- D2: 3/4 — All stage links pass v1 structural validation; H1-H8 distinguish proposals and exact brief quotes; FM/EV links derived reciprocally.
- D3: 3/4 — W18-W19 add signed exact-quote confirmation with 24h bound, deny/expiry/changed-intent owned exits and fresh recheck; W10-W12 reconcile unknowns; W7 retains original 48h deadline.
- D4: 3/4 — C9 typed portal confirm_credit/decline_credit events, proposal/receipt/digest/subject/expiry fields and bounded reminder; C1 remains intake router; C4/C6 repeat exact action checks.
- D5: 3/4 — C4/C6 bind positive integer CREDIT payload, tenant/subject/active connection, policy/approval version, digest, entitlement key and durable proof; C7 read-only recovery survives session loss.
- D6: 3/4 — H1-H8 label policies, APIs, timing, cost and retention; C2/C3 contradiction and unavailable states route human; no live service assertions.
- D7: 3/4 — F1-F5 choose bounded judgement in durable code workflow; compare common persistence/timer/audit/ownership criteria and reject synchronous and autonomous alternatives.
- D8: 3/4 — M1 maps only C3; W3 allows one retry; 0.88 expected calls, 2 worst-case, illustrative price/token arithmetic and excluded costs explicit.
- D9: 3/4 — FM1-FM10 cover subject, staleness, duplicates, unknown commits, injection, queue, cancellation, amount and false completion with owners and release gates.
- D10: 3/4 — EV1-EV28 plus EV32-EV34 are complete self-contained synthetic fixtures; EV3/EV19 explicitly enter prepared W10; EV29/EV31 enumerate new confirmation fixtures. Planned harness has strict unexpected calls; tests not executed.
- D11: 3/4 — R1 metrics have denominators/windows; R2-R5 distinct entry/exit gates; R6 customer clustering, baseline power calculation, spillover and maturation; zero safety tolerance separate.
- D12: 3/4 — X1 propagates C9/W18-W19, quote/confirmation records and distinct business/state revisions. Exports will derive from this canonical version; H1-H8 remain explicit launch blockers.

Review findings:

- ISSUE1 [major, resolved] workflow/W4: Credit path lacks explicit confirmation interaction and timeout even though authority requires consent. Add typed confirmation command/receipt owner, immutable payload binding, bounded wait and fresh recheck; preserve no-write denial/expiry. Repaired in round 2: C9/W18-W19, EV3/EV19, EV32-EV34, H2/C4 and X1 updated; reciprocal links and release manifest propagated.
- ISSUE2 [major, resolved] evals/EV3: Writer-time deactivation and cancellation fixtures can reject earlier at W1 without exercising intended guard. Bind entryState W10 and existing prepared authorized operation; reject unexpected write effects. Add confirmation fixtures. Repaired in round 2: C9/W18-W19, EV3/EV19, EV32-EV34, H2/C4 and X1 updated; reciprocal links and release manifest propagated.
- ISSUE3 [major, resolved] context/CTX2: H2 describes cap while EV22 requires supervisor routing for uncapped amounts above it; state explicitly that larger customer entitlement is not silently reduced and closed automatically. Repaired in round 2: C9/W18-W19, EV3/EV19, EV32-EV34, H2/C4 and X1 updated; reciprocal links and release manifest propagated.

## Proposed assumption ledger

### H1

Proposed v1 serves authenticated consumer postpaid active connections in one tenant and currency; prepaid, enterprise, closed-service and cash-refund execution use an owned supervisor case.

Why: Bound the ledger and eligibility semantics.

Proposed owner: Product owner

Validation: Confirm supported segments, currency and meaning of active with operations.

Launch blocker: true

### H2

Illustrative policy P1 allows outage credits only: verified outage overlap of at least 60 minutes; credit=floor(monthly base fee minor units * affected minutes / billing-cycle minutes), limited by remaining eligible base fee. If the computed entitlement before the 1000-minor-unit automatic cap exceeds that cap, route the whole claim to a supervisor; do not silently cap and close it. Automatic credit is at most 1000 minor units per incident. Billing errors, poor speed without verified outage, larger amounts and uncertainty require supervisor review.

Why: A concrete safe policy is needed to design the action boundary; these are not company rules.

Proposed owner: Billing policy owner

Validation: Approve a versioned eligibility table, rounding, taxes, overlap rules, limits and customer consent requirements before writes.

Launch blocker: true

### H3

Proposed APIs support tenant/customer/connection scoping, active-state versions, immutable policy versions, atomic incident credit uniqueness, durable operation lookup and fresh authorization at the billing writer.

Why: The design cannot establish actual adapter capabilities.

Proposed owner: Billing engineering lead

Validation: Prove these semantics in sandbox including unknown commit, conflicts and revoked permission. No autonomous credits if unavailable.

Launch blocker: true

### H4

Proposed supervisor queue has a 48 elapsed-hour decision deadline from initial referral, acknowledgement within 15 minutes, updates at receipt and every 12 hours, escalation to duty lead at 36 hours and overdue transfer at 48 hours without approval by silence.

Why: Brief supplies 48 hours but no staffing, clock or update cadence.

Proposed owner: Customer operations lead

Validation: Confirm 24/7 staffing, elapsed UTC timer, escalation acceptance and notification channels.

Launch blocker: true

### H5

Proposed privacy defaults keep full case evidence for 30 days and minimized financial audit references for 365 days, encrypted in tenant-resident storage; no raw payment details or entire bills in model prompts.

Why: Retention and residency require company approval.

Proposed owner: Privacy lead

Validation: Verify applicable retention, deletion, residency and model-provider terms before real data.

Launch blocker: true

### H6

Illustrative planning assumptions are 10000 complaints/month, 80% reaching model investigation, 10% of those needing one schema retry; model budget prices are $2/input million and $8/output million tokens, not a vendor quote.

Why: Reproducible capacity and budget without invented measured data.

Proposed owner: AI platform owner

Validation: Measure shadow branch mix, token lengths and contracted prices.

Launch blocker: false

### H7

Proposed credit API posts positive integer minor units as a CREDIT against a named original invoice line and incident; supervisor cannot override active-connection, subject, duplicate or freshness checks. A separate human process owns cash refunds and compensation.

Why: Avoid introducing an unbounded general refund writer.

Proposed owner: Finance operations lead

Validation: Confirm ledger allocation, credit semantics, supervisor authority and cash-refund handoff receipt.

Launch blocker: true

### H8

Proposed authenticated case portal plus consented service notifications use template outbox messages; case status remains accessible if delivery fails.

Why: Keep customers informed without inventing a live messaging integration.

Proposed owner: Customer experience lead

Validation: Verify channel consent, accessible templates, delivery receipts and outbox deduplication.

Launch blocker: true

- context: All content is proposed design. Relevant H IDs are centralized above; no company policy, API capability or operational evidence has been verified.
- context/CTX1: H1
- context/CTX1: H2
- context/CTX2: H1
- context/CTX2: H7
- context/CTX3: H3
- context/CTX3: H4
- context/CTX4: H2
- context/CTX4: H3
- context/CTX5: H4
- context/CTX5: H6
- context/CTX6: H3
- context/CTX6: H7
- context/CTX6: H8
- context/CTX7: H5
- context/CTX7: H8
- tasks: All content is proposed design. Relevant H IDs are centralized above; no company policy, API capability or operational evidence has been verified.
- tasks/T0: H1
- tasks/T0: H2
- tasks/T1: H1
- tasks/T1: H2
- tasks/T2: H1
- tasks/T2: H2
- tasks/T3: H1
- tasks/T3: H2
- tasks/T4: H1
- tasks/T4: H2
- tasks/T4.1: H1
- tasks/T4.1: H2
- tasks/T4.2: H1
- tasks/T4.2: H2
- tasks/T4.3: H1
- tasks/T4.3: H2
- tasks/T5: H1
- tasks/T5: H2
- tasks/A1: H3
- tasks/A1: H4
- tasks/A1: H5
- tasks/A2: H3
- tasks/A2: H4
- tasks/A2: H5
- tasks/A3: H3
- tasks/A3: H4
- tasks/A3: H5
- tasks/A4: H3
- tasks/A4: H4
- tasks/A4: H5
- components: All content is proposed design. Relevant H IDs are centralized above; no company policy, API capability or operational evidence has been verified.
- components/C1: H1
- components/C1: H3
- components/C2: H3
- components/C2: H5
- components/C3: H2
- components/C3: H5
- components/C3: H6
- components/C4: H2
- components/C4: H3
- components/C4: H7
- components/C5: H4
- components/C5: H7
- components/C5: H8
- components/C6: H2
- components/C6: H3
- components/C6: H7
- components/C7: H3
- components/C7: H4
- components/C7: H7
- components/C8: H3
- components/C8: H4
- components/C8: H8
- components/C9: H2
- components/C9: H3
- components/C9: H8
- workflow: All content is proposed design. Relevant H IDs are centralized above; no company policy, API capability or operational evidence has been verified.
- workflow/W1: H3
- workflow/W1: H4
- workflow/W2: H3
- workflow/W2: H4
- workflow/W3: H3
- workflow/W3: H4
- workflow/W4: H3
- workflow/W4: H4
- workflow/W6: H3
- workflow/W6: H4
- workflow/W7: H3
- workflow/W7: H4
- workflow/W8: H3
- workflow/W8: H4
- workflow/W9: H3
- workflow/W9: H4
- workflow/W10: H3
- workflow/W10: H4
- workflow/W11: H3
- workflow/W11: H4
- workflow/W12: H3
- workflow/W12: H4
- workflow/W13: H3
- workflow/W13: H4
- workflow/W14: H3
- workflow/W14: H4
- workflow/W15: H3
- workflow/W15: H4
- workflow/W16: H3
- workflow/W16: H4
- workflow/W17: H3
- workflow/W17: H4
- workflow/W18: H2
- workflow/W18: H3
- workflow/W18: H8
- workflow/W19: H2
- workflow/W19: H3
- workflow/W19: H8
- framework: All content is proposed design. Relevant H IDs are centralized above; no company policy, API capability or operational evidence has been verified.
- framework/F1: H3
- framework/F1: H5
- framework/F2: H3
- framework/F2: H5
- framework/F3: H3
- framework/F3: H5
- framework/F4: H3
- framework/F4: H5
- framework/F5: H3
- framework/F5: H5
- models: All content is proposed design. Relevant H IDs are centralized above; no company policy, API capability or operational evidence has been verified.
- models/M1: H6
- fmea: All content is proposed design. Relevant H IDs are centralized above; no company policy, API capability or operational evidence has been verified.
- fmea/FM1: H2
- fmea/FM1: H3
- fmea/FM1: H4
- fmea/FM2: H2
- fmea/FM2: H3
- fmea/FM2: H4
- fmea/FM3: H2
- fmea/FM3: H3
- fmea/FM3: H4
- fmea/FM4: H2
- fmea/FM4: H3
- fmea/FM4: H4
- fmea/FM5: H2
- fmea/FM5: H3
- fmea/FM5: H4
- fmea/FM6: H2
- fmea/FM6: H3
- fmea/FM6: H4
- fmea/FM7: H2
- fmea/FM7: H3
- fmea/FM7: H4
- fmea/FM8: H2
- fmea/FM8: H3
- fmea/FM8: H4
- fmea/FM9: H2
- fmea/FM9: H3
- fmea/FM9: H4
- fmea/FM10: H2
- fmea/FM10: H3
- fmea/FM10: H4
- evals: All content is proposed design. Relevant H IDs are centralized above; no company policy, API capability or operational evidence has been verified.
- evals/EV1: H2
- evals/EV1: H3
- evals/EV1: H4
- evals/EV1: H7
- evals/EV2: H2
- evals/EV2: H3
- evals/EV2: H4
- evals/EV2: H7
- evals/EV3: H2
- evals/EV3: H3
- evals/EV3: H4
- evals/EV3: H7
- evals/EV4: H2
- evals/EV4: H3
- evals/EV4: H4
- evals/EV4: H7
- evals/EV5: H2
- evals/EV5: H3
- evals/EV5: H4
- evals/EV5: H7
- evals/EV6: H2
- evals/EV6: H3
- evals/EV6: H4
- evals/EV6: H7
- evals/EV7: H2
- evals/EV7: H3
- evals/EV7: H4
- evals/EV7: H7
- evals/EV8: H2
- evals/EV8: H3
- evals/EV8: H4
- evals/EV8: H7
- evals/EV9: H2
- evals/EV9: H3
- evals/EV9: H4
- evals/EV9: H7
- evals/EV10: H2
- evals/EV10: H3
- evals/EV10: H4
- evals/EV10: H7
- evals/EV11: H2
- evals/EV11: H3
- evals/EV11: H4
- evals/EV11: H7
- evals/EV12: H2
- evals/EV12: H3
- evals/EV12: H4
- evals/EV12: H7
- evals/EV13: H2
- evals/EV13: H3
- evals/EV13: H4
- evals/EV13: H7
- evals/EV14: H2
- evals/EV14: H3
- evals/EV14: H4
- evals/EV14: H7
- evals/EV15: H2
- evals/EV15: H3
- evals/EV15: H4
- evals/EV15: H7
- evals/EV16: H2
- evals/EV16: H3
- evals/EV16: H4
- evals/EV16: H7
- evals/EV17: H2
- evals/EV17: H3
- evals/EV17: H4
- evals/EV17: H7
- evals/EV18: H2
- evals/EV18: H3
- evals/EV18: H4
- evals/EV18: H7
- evals/EV19: H2
- evals/EV19: H3
- evals/EV19: H4
- evals/EV19: H7
- evals/EV20: H2
- evals/EV20: H3
- evals/EV20: H4
- evals/EV20: H7
- evals/EV21: H2
- evals/EV21: H3
- evals/EV21: H4
- evals/EV21: H7
- evals/EV22: H2
- evals/EV22: H3
- evals/EV22: H4
- evals/EV22: H7
- evals/EV23: H2
- evals/EV23: H3
- evals/EV23: H4
- evals/EV23: H7
- evals/EV24: H2
- evals/EV24: H3
- evals/EV24: H4
- evals/EV24: H7
- evals/EV25: H2
- evals/EV25: H3
- evals/EV25: H4
- evals/EV25: H7
- evals/EV26: H2
- evals/EV26: H3
- evals/EV26: H4
- evals/EV26: H7
- evals/EV27: H2
- evals/EV27: H3
- evals/EV27: H4
- evals/EV27: H7
- evals/EV28: H2
- evals/EV28: H3
- evals/EV28: H4
- evals/EV28: H7
- evals/EV29: H2
- evals/EV29: H3
- evals/EV29: H4
- evals/EV30: H2
- evals/EV30: H3
- evals/EV30: H4
- evals/EV31: H2
- evals/EV31: H3
- evals/EV31: H4
- evals/EV32: H2
- evals/EV32: H3
- evals/EV32: H4
- evals/EV32: H7
- evals/EV33: H2
- evals/EV33: H3
- evals/EV33: H4
- evals/EV33: H7
- evals/EV34: H2
- evals/EV34: H3
- evals/EV34: H4
- evals/EV34: H7
- rollout: All content is proposed design. Relevant H IDs are centralized above; no company policy, API capability or operational evidence has been verified.
- rollout/R1: H3
- rollout/R1: H4
- rollout/R1: H6
- rollout/R2: H3
- rollout/R2: H4
- rollout/R2: H6
- rollout/R3: H3
- rollout/R3: H4
- rollout/R3: H6
- rollout/R4: H3
- rollout/R4: H4
- rollout/R4: H6
- rollout/R5: H3
- rollout/R5: H4
- rollout/R5: H6
- rollout/R6: H3
- rollout/R6: H4
- rollout/R6: H6
- rollout/R7: H3
- rollout/R7: H4
- rollout/R7: H6
- export: All content is proposed design. Relevant H IDs are centralized above; no company policy, API capability or operational evidence has been verified.
- export/X1: H1
- export/X1: H2
- export/X1: H3
- export/X1: H4
- export/X1: H5
- export/X1: H7
- export/X1: H8

## Review and tooling limitations

- Self-review by the author, not independent review or stakeholder approval.
- Bundled structural validator executed; financial, identity, queue and model assertions are specifications only and have not run against a business implementation.
- Synthetic fixtures, policy P1, volumes, thresholds and costs are proposed assumptions; actual API capability, authority, privacy and policy approval remain H1-H8 launch dependencies.
- PDF rendering and visual QA deliberately deferred to root batch step; no HTML requested or produced.
- Design-only tooling: this helper makes no provider, network or business API calls and executes no business assertions; optional host-assistant research is outside this statement.
- Schema, reference, graph and ID-coverage checks do not establish semantic completeness, source truth, actual human authorization or production safety.
- Review scores and evidence are supplied by the reviewing agent; the helper checks their shape and declared pass conditions, not their truth.
- FMEA action/control text is required where specified; the helper does not verify ownership, release authority, regulatory compliance or risk acceptance.
