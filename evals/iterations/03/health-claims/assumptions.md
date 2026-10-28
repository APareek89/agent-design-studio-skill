# Inpatient claim review assistant

> PASS · DESIGN ONLY. Review is a design judgement; no business controls or provider reliability were executed.

Review method: self-review; round 3.

Review dimensions (supplied scores):

- D1: 3/4 — CTX1-CTX4, T0-T7 bound intake through proven staff-facing draft or owned exception. H1 excludes payments, final rejection, appeals and clinical judgement; W1/W5 cover missing, unsupported and cancel commands.
- D2: 3/4 — T1-T7 map through C1-C9 and W1-W11 to substantive goldens. FM1-FM8 links are reciprocal for golden/offline/online/release tests. Exact brief preserved; H1-H6 distinguish every proposed operating condition.
- D3: 3/4 — W1-W11 enumerate exclusive component output paths, durable 24h review clock, explicit one-hour notice, bounded model/read retries and one reconciled write retry. W8 found/absence/unresolved predicates are disjoint; W11 owns failure without false completion.
- D4: 3/4 — C1-C9 name typed fields, resource scopes, input/output enums, API deadline/readback and staff signed event requirements. C7 stores immutable payload bytes and SHA256; C8 retains independent reconciliation scope after caller expiry. H2 is explicit adapter verification dependency.
- D5: 3/4 — C1 gates medical reads; C2 admits visible verified source only; C4 owns service dates, integer money and caps. C7 fresh RBAC/CAS binds tenant/member/claim/version/operation/full bytes; no payment credentials. W9 guards durable proof before W10. H3 blocks PHI processing pending approval.
- D6: 3/4 — H1-H6 carry proposed role/threshold/retention/cost/volume assumptions and validation owners. Unknown/contradictory rules, unverified OCR, model unavailability and service-period splits withhold authoritative totals and route staff.
- D7: 3/4 — F1 chooses durable database-backed code plus a stateless explanation call over autonomous adjudication. F2-F4 compare cloud/self-host categories on identical residency, timer, key and deletion criteria, explicitly unverified; retrieval is separate from authoritative rules/ledger.
- D8: 3/4 — One M1 plan for the only model C3; 0.8*1.1=0.88 expected calls, max two W3 calls. Token arithmetic gives USD0.024/call, 0.02112/case, 211.20/10000 cases, excluding OCR/storage/humans. Tier alternatives and fine-tune gates explicit.
- D9: 3/4 — FM1-FM8 cover subject/privacy, dated room rules, prompt/citation/OCR conflict, exact/semantic/race duplicates, unknown saves/cancellation/session expiry, false proof, revoked authority and human queue clocks. Hypothetical S/O/D and owner-specific release gates are declared; none accepted.
- D10: 3/4 — EV1-EV18 and EV22-EV31 contain self-contained JSON inputs/expected/pass assertions; full payload byte hashes and ordered mocks are explicit. Positive room-only/proration/rounding/remaining-cap cases, three isolated citation mutations, two-operation CAS, time-of-revocation, cancellation and queue deadlines are covered. EV21 names every golden; EV19/EV20 define heldout/monitor evidence.
- D11: 3/4 — R1 defines units/denominators, baseline and hypothetical impact target. R2 ends at assist-only with separate shadow/assist entry/exit and immediate safety stop. R3 defines team-cluster randomization, strata, contamination controls, variance/power/ICC method and minimum cycle; R4 names veto/signoff and unresolved-save owners.
- D12: 3/4 — X1 and four milestones select actual C contracts and all linked tests; full source/effective goldens remain machine companions. H1-H4 clearly identify launch dependencies; handoff preserves no settlement scope and opt-in HTML instruction. Failed review rounds 1 and 2 are retained unchanged; final validator has zero errors with verified declarations.

Review findings:

- ISSUE1 [major, resolved] workflow/W8: Resolved recovery predicate overlap; found is disjoint from absence fallback.
- ISSUE2 [major, resolved] evals/EV15: Resolved fixture provenance: full operation bytes/hashes, save-time revocation, date/cap/copay/OCR/rounding and review command tests added.
- ISSUE3 [major, resolved] export/X1: Resolved schema field types; final structural validation passes.
- ISSUE4 [major, resolved] workflow/W6: Declared requester_notice role for actual one-hour notice branch.
- ISSUE5 [major, resolved] components/C5: Added T7 owned terminal responsibility and explicit lifecycle handling.

## Proposed assumption ledger

### H1

First release publishes staff-facing recommendations only; all settlement, denial notices and appeals stay outside this assistant.

Why: Coverage rules and write authority are unspecified.

Proposed owner: Claims director

Validation: Approve scope and human operating procedure.

Launch blocker: true

### H2

Insurer supplies signed, effective-dated policy rule packs, member linkage, authority and case APIs with version checks and operation readback.

Why: Uploaded policy text cannot establish operative coverage or authority.

Proposed owner: Insurance rules owner

Validation: Reconcile a sample of policy endorsements and claims with authoritative records; certify adapter contracts.

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

- Self-review, not an independent agent verdict. Scores assess a bounded proposed assist-only design, not production certification.
- No provider, business or network calls were made; policy correctness, real API support, medical suitability and human capacity remain unverified.
- Golden cases EV1-EV31 are specifications. The validator checks structure, references and declared semantics; no business harness ran them.
- H1-H4 block any PHI launch until proposed owners verify scope, rule/API contracts, privacy/deletion/residency and queue staffing. Model cost/volume and impact targets H5-H6 are illustrative.
- Core PDF generation and visual inspection are delegated to the parent run; no PDF exists yet in this worker output.
- Design-only tooling: this helper makes no provider, network or business API calls and executes no business assertions; optional host-assistant research is outside this statement.
- Schema, reference, graph and ID-coverage checks do not establish semantic completeness, source truth, actual human authorization or production safety.
- Review scores and evidence are supplied by the reviewing agent; the helper checks their shape and declared pass conditions, not their truth.
- FMEA action/control text is required where specified; the helper does not verify ownership, release authority, regulatory compliance or risk acceptance.
