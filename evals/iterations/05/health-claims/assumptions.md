# Inpatient claim review assistant

> PASS · DESIGN ONLY. Review is a design judgement; no business controls or provider reliability were executed.

Review method: independent-agent; round 2.

Review dimensions (supplied scores):

- D1: 3/4 — CTX1-CTX4/T1-T7 define authenticated inpatient draft scope, terminal proof or owned exception; H1 rejects automated settlement.
- D2: 3/4 — T1-T7/C1-C9/W1-W11 retain stable links; FM2/EV32/EV33 and EV21 propagate accumulator guard coverage. C2 authenticated snapshot and receipt establish trusted source separately from operation outputs. Exact eval-set data equals canonical.
- D3: 3/4 — W1-W11 define exclusive predicates, 24h durable wait, one-hour notice, bounded readback and retry, cancellation/expiry and owned unresolved terminal.
- D4: 3/4 — C1-C9 retain typed bounded contracts; C2 adds accumulator scope/version/receipt response; C4 exact source guards and C7 fresh writer version recheck prevent source-state inference. H2 is explicit external API verification dependency.
- D5: 3/4 — C1 gates PHI; C2 excludes hidden layers; C4 owns arithmetic/dates; C7 enforces RBAC/CAS/immutable bytes; C8 independent readback; C9 gates saved display. No payment/denial scope.
- D6: 4/4 — H1-H6 label authority, policy/privacy/staffing launch gaps and illustrative cost/targets. Unknown rules/clinical necessity/copay/currency/date splits abstain.
- D7: 3/4 — F1 durable code workflow fits 11 nodes; F2 separates vault/rules/ledger; F3 least privilege; F4 uses equivalent candidate residency/deletion/timer tests and rejects multi-cloud expansion.
- D8: 4/4 — M1 exactly covers C3: 0.8*1.1=.88 calls, .024 USD/call, .02112/case, 211.20/10k; retry/worst-case/context/staff exclusions and rejected tiers are explicit.
- D9: 3/4 — FM1-FM8 give scored case-specific causes, controls, owners and reciprocal tests for PHI, rules, forged sources, races, uncertain save, proof, revocation and queue stalls.
- D10: 3/4 — 30 self-contained golden fixtures: EV1/EV4/EV9/EV23/EV30 now carry C2 source snapshot, same-request receipt and clock. EV32 missing accumulatorVersion and EV33 mismatched receipt version each assert zero writes/no authoritative total. EV10 has independently authorized OP-A and OP-B payloads with matching recomputed hashes and exact CAS schedule/winner/loser/no-overwrite assertions. EV6-EV8 remain isolated page/clause/quote negatives. EV25 sole intentional payload-hash mismatch.
- D11: 3/4 — R1-R4 define denominators, baseline/assist gates, team randomization/ICC power method, safety vetoes and stop/reconciliation ownership; no unapproved scale claim.
- D12: 3/4 — Actual PRD/architecture/build milestones include repaired accumulator contracts and concurrency handoff; exported eval-set data equal canonical. EV21 release set names all 30 goldens including EV32/EV33. Real H2 adapters and business harness remain clear launch dependencies.

Review findings:

- IR1 [major, resolved] evals/EV1: Resolved by C2 typed authoritative accumulatorSnapshot, C4 scope/same-request version/timestamp guards, positive fixture source/clock payloads, C7 fresh writer-version query, and isolated missing/stale negatives EV32/EV33. Independently inspected actual fixture objects and their API mock responses.
- IR2 [major, resolved] evals/EV10: Resolved by two complete independently authorized OP-A/OP-B payloads and matching request paths/IDs/hashes/source versions, explicit expectedVersion=3 CAS schedule and one-winner/no-overwrite assertions. Both SHA256 values independently recomputed from actual payloads.

## Proposed assumption ledger

### H1

First release publishes staff-facing recommendations only; all settlement, denial notices and appeals stay outside this assistant.

Why: Coverage rules and write authority are unspecified.

Proposed owner: Claims director

Validation: Approve scope and human operating procedure.

Launch blocker: true

### H2

Insurer supplies signed, effective-dated policy rule packs, member linkage, authority and case APIs with version checks and operation readback. This proposed integration also exposes a tenant/member/policy-bound benefit accumulator snapshot and a same-request current-version receipt; its real support and currency/freshness semantics require insurer verification.

Why: Uploaded policy text cannot establish operative coverage or authority.

Proposed owner: Insurance rules owner

Validation: Reconcile a sample of policy endorsements and claims with authoritative records; certify adapter contracts. Verify accumulator GET response fields, current-version receipt, source authentication, version-race behavior and writer freshness check with insurer.

Launch blocker: true

### H3

Privacy owner selects deployment region, role access, lawful processing basis, document retention and model contract; proposed documents TTL 30 days, minimal audit 365 days, legal hold overrides deletion.

Why: Medical records need deliberate processing and deletion controls.

Proposed owner: Privacy officer

Validation: Approve data map, permitted model processing, encryption, residency and tested deletion/hold procedure.

Launch blocker: true

### H4

Claims team covers a 24-hour elapsed-time review deadline, four-hour acknowledgement and a one-hour visible waiting status.

Why: A stalled queue must retain an accountable next step.

Proposed owner: Claims operations lead

Validation: Capacity test staff queue; approve calendar, backup and escalation rules.

Launch blocker: true

### H5

Synthetic budget: one standard model call per supported complete claim, at most one retry; 10% retry, 80% complete inputs; 8000 input and 1000 output tokens, USD 2/8 per million, 10000 cases/month.

Why: Enable transparent planning without provider facts.

Proposed owner: Product owner

Validation: Benchmark actual models, document lengths and traffic before procurement.

Launch blocker: false

### H6

Illustrative pilot targets are zero unauthorized disclosures and zero unsupported monetary calculations; 20% lower median handling time with no quality regression.

Why: Baseline and business targets are unknown.

Proposed owner: Product analytics lead

Validation: Collect baseline then approve measurable targets and power analysis.

Launch blocker: false

- context/CTX1: H1
- context/CTX1: H2
- context/CTX1: H3
- context/CTX2: H1
- context/CTX2: H2
- context/CTX2: H3
- context/CTX3: H1
- context/CTX3: H2
- context/CTX3: H3
- context/CTX4: H1
- context/CTX4: H2
- context/CTX4: H3
- tasks/T0: H1
- tasks/T0: H2
- tasks/T0: H4
- tasks/T1: H1
- tasks/T1: H2
- tasks/T1: H4
- tasks/T2: H1
- tasks/T2: H2
- tasks/T2: H4
- tasks/T3: H1
- tasks/T3: H2
- tasks/T3: H4
- tasks/T4: H1
- tasks/T4: H2
- tasks/T4: H4
- tasks/T5: H1
- tasks/T5: H2
- tasks/T5: H4
- tasks/T6: H1
- tasks/T6: H2
- tasks/T6: H4
- tasks/T7: H1
- tasks/T7: H2
- tasks/T7: H4
- tasks/A1: H2
- tasks/A2: H2
- tasks/A3: H2
- components/C1: H1
- components/C1: H2
- components/C1: H3
- components/C1: H4
- components/C2: H1
- components/C2: H2
- components/C2: H3
- components/C2: H4
- components/C3: H1
- components/C3: H2
- components/C3: H3
- components/C3: H4
- components/C4: H1
- components/C4: H2
- components/C4: H3
- components/C4: H4
- components/C5: H1
- components/C5: H2
- components/C5: H3
- components/C5: H4
- components/C6: H1
- components/C6: H2
- components/C6: H3
- components/C6: H4
- components/C7: H1
- components/C7: H2
- components/C7: H3
- components/C7: H4
- components/C8: H1
- components/C8: H2
- components/C8: H3
- components/C8: H4
- components/C9: H1
- components/C9: H2
- components/C9: H3
- components/C9: H4
- workflow/W1: H1
- workflow/W1: H2
- workflow/W1: H4
- workflow/W2: H1
- workflow/W2: H2
- workflow/W2: H4
- workflow/W3: H1
- workflow/W3: H2
- workflow/W3: H4
- workflow/W4: H1
- workflow/W4: H2
- workflow/W4: H4
- workflow/W5: H1
- workflow/W5: H2
- workflow/W5: H4
- workflow/W6: H1
- workflow/W6: H2
- workflow/W6: H4
- workflow/W7: H1
- workflow/W7: H2
- workflow/W7: H4
- workflow/W8: H1
- workflow/W8: H2
- workflow/W8: H4
- workflow/W9: H1
- workflow/W9: H2
- workflow/W9: H4
- workflow/W10: H1
- workflow/W10: H2
- workflow/W10: H4
- workflow/W11: H1
- workflow/W11: H2
- workflow/W11: H4
- framework/F1: H1
- framework/F1: H2
- framework/F1: H3
- framework/F2: H1
- framework/F2: H2
- framework/F2: H3
- framework/F3: H1
- framework/F3: H2
- framework/F3: H3
- framework/F4: H1
- framework/F4: H2
- framework/F4: H3
- models/M1: H5
- fmea/FM1: H1
- fmea/FM1: H2
- fmea/FM1: H4
- fmea/FM2: H1
- fmea/FM2: H2
- fmea/FM2: H4
- fmea/FM3: H1
- fmea/FM3: H2
- fmea/FM3: H4
- fmea/FM4: H1
- fmea/FM4: H2
- fmea/FM4: H4
- fmea/FM5: H1
- fmea/FM5: H2
- fmea/FM5: H4
- fmea/FM6: H1
- fmea/FM6: H2
- fmea/FM6: H4
- fmea/FM7: H1
- fmea/FM7: H2
- fmea/FM7: H4
- fmea/FM8: H1
- fmea/FM8: H2
- fmea/FM8: H4
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
- evals/EV18: H2
- evals/EV19: H2
- evals/EV19: H3
- evals/EV19: H4
- evals/EV20: H2
- evals/EV20: H3
- evals/EV20: H4
- evals/EV21: H2
- evals/EV21: H3
- evals/EV21: H4
- evals/EV22: H2
- evals/EV23: H2
- evals/EV24: H2
- evals/EV25: H2
- evals/EV26: H2
- evals/EV27: H2
- evals/EV28: H2
- evals/EV29: H2
- evals/EV30: H2
- evals/EV31: H2
- evals/EV32: H2
- evals/EV33: H2
- rollout/R1: H1
- rollout/R1: H2
- rollout/R1: H3
- rollout/R1: H4
- rollout/R1: H6
- rollout/R2: H1
- rollout/R2: H2
- rollout/R2: H3
- rollout/R2: H4
- rollout/R2: H6
- rollout/R3: H1
- rollout/R3: H2
- rollout/R3: H3
- rollout/R3: H4
- rollout/R3: H6
- rollout/R4: H1
- rollout/R4: H2
- rollout/R4: H3
- rollout/R4: H4
- rollout/R4: H6
- export/X1: H1
- export/X1: H2
- export/X1: H3
- export/X1: H4

## Review and tooling limitations

- Independent second-round AI design review; pass means bounded proposed-design readiness, not insurance/medical/legal certification or production correctness.
- Business golden harness and live API/PHI controls were not executed. Structural validation and independent fixture arithmetic/hash checks do not establish those controls work in production.
- H1-H4 remain launch blockers: real rule registry/accumulator and authorization contracts, policy applicability, privacy/deletion/residency and staffed queues require accountable evidence.
- The staff-assist design explicitly excludes claim payment, final rejection and straight-through settlement, so no STP QA sample is claimed.
- Reviewed revised canonical design, actual eval-set and PRD/architecture/build exports against D1-D12 and prior independent findings; did not rely on author reviews, repair scripts or self-reported repair checks.
- Design-only tooling: this helper makes no provider, network or business API calls and executes no business assertions; optional host-assistant research is outside this statement.
- Schema, reference, graph and ID-coverage checks do not establish semantic completeness, source truth, actual human authorization or production safety.
- Review scores and evidence are supplied by the reviewing agent; the helper checks their shape and declared pass conditions, not their truth.
- FMEA action/control text is required where specified; the helper does not verify ownership, release authority, regulatory compliance or risk acceptance.
