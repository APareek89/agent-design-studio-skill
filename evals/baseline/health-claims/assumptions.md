# Inpatient claim evidence and adjudication assistance

> PASS · DESIGN ONLY. Review is a design judgement; no business controls or provider reliability were executed.

Review method: self-review; round 3.

Review dimensions (supplied scores):

- D1: 3/4 — CTX1–CTX6/T0–T4.3 completely bound supported intake through review/hold/cancel; all final insurer decisions remain human.
- D2: 3/4 — Every high-risk leaf has reachable W coverage and substantive golden. FM/EV reciprocal links derived once; EV26 is included in FM10 and EV25 manifest.
- D3: 3/4 — W1–W13 enumerate ready/hold/cancel/reject and commit/error/unknown paths. Cancellation precedence, CAS and digest readback prevent conflicting resubmission; W11 retains recovery owner.
- D4: 3/4 — C1–C7 declare typed inputs/outputs, read and internal write logical contracts, temporal parser, human-event reentry and SLA roles. Real adapters remain verification dependencies.
- D5: 3/4 — C4 owns integer arithmetic/dates/limits; C6 checks identity/resource/version/full payload at API. C3 has no tools; F3/F4 isolate medical evidence and redacted inference.
- D6: 4/4 — H1–H9 identify every unprovided policy/volume/price/threshold/owner as hypothesis. Sources preserve brief and exact H statements; no clinical/legal claims.
- D7: 3/4 — F1–F5 choose code state machine and bounded single judgement over multi-agent/open-ended adjudication; data candidates labelled unverified against common criteria.
- D8: 3/4 — M1 cost formula .84*$0.0384=$0.032256/case and 2-call worst budget reproducible. Input overflow holds; tier selection requires held-out evidence and fine-tune gates.
- D9: 3/4 — FM1–FM10 contain concrete inpatient-specific effects, causes, S/O/D rationale, owner release gates, control and reciprocal golden coverage. No risk accepted.
- D10: 3/4 — 23 self-contained golden fixtures (EV1–EV22,EV26) plus EV23 offline/EV24 online/EV25 release. Exact payload hashes locally checked; EV17 intentionally fails. Actual citation mutation, room cap controls, stale policy, cancellation and callback fixtures inspected. Planned harness remains unexecuted.
- D11: 3/4 — R1–R6 specify unknown-baseline collection, proposed quality/time targets, causal measures, cluster experiment and noncircular shadow/assist/scale gates. Safety event overrides benefits.
- D12: 3/4 — X1 follows canonical C/W/EV IDs; exports generated from same canonical design after frozen validation. Launch blockers remain explicit, no business control execution claimed.

Review findings:

- ISSUE5 [major, resolved] evals/EV7: Citation validity was only mocked false although actual model span remained valid; must corrupt a concrete span to isolate guard. Repaired in final canonical version and re-inspected.
- ISSUE6 [major, resolved] evals/EV26: Generic fixture augmentation cited last document (policy clause) for admission dates. Correct dates to discharge span and include actual line trace in persist packet. Repaired in final canonical version and re-inspected.
- ISSUE7 [major, resolved] evals/EV18: Timer fixture runs at 48h without a clear preexisting committed review record; make event action and prior receipt explicit. Repaired in final canonical version and re-inspected.

## Proposed assumption ledger

### H1

Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.

Why: Unknown authority and policy interpretation require a bounded useful release.

Proposed owner: Claims product owner

Validation: Approve assist-only scope and identify adjudicator roles.

Launch blocker: true

### H2

A tenant policy registry provides legally reviewed immutable policy/endorsement versions, effective intervals, member binding and explicit claim-date selection rules.

Why: Upload text alone cannot establish governing coverage.

Proposed owner: Insurance policy lead

Validation: Approve temporal rule packs, member coverage lookup and retrospective amendment handling.

Launch blocker: true

### H3

Synthetic rule pack HC1 uses admission-date selection, inclusive discharge day, INR minor units, room-rent cap only on room lines, no proportional deduction, zero deductible and zero coinsurance.

Why: A concrete executable illustration is needed; none of these are verified insurer rules.

Proposed owner: Insurance policy lead

Validation: Replace or approve every rule; validate day count, benefit sublimits, exclusions, coordination, remaining sum insured, rounding and temporal basis per product.

Launch blocker: true

### H4

Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.

Why: Recovery and audit require durable state.

Proposed owner: Platform owner

Validation: Contract spike proving version CAS, transactional events, idempotency and readback with access controls.

Launch blocker: true

### H5

Use restricted medical evidence storage, encrypted transport and storage, tenant keys, no provider training, no raw content in logs; proposed 30-day working-copy deletion after case close subject to insurer approved retention/legal holds.

Why: Medical data needs explicit minimization and a verified retention basis.

Proposed owner: Privacy owner

Validation: Approve lawful basis, residency, model processing contract, access matrix, retention and legal-hold policy before real data.

Launch blocker: true

### H6

Human queues are staffed by claims operations: acknowledge in 4 elapsed hours, review in 2 elapsed days; overdue goes to duty manager at 4h and head of claims at 48h. Timers run UTC 24x7.

Why: Missing information and exceptions need an owned end state.

Proposed owner: Claims operations lead

Validation: Confirm staffing, escalation channels, queue capacity and elapsed-time SLA.

Launch blocker: true

### H7

Illustrative volume is 1000 cases/month; 80% reach the model and 5% of reached cases need one schema repair retry. Synthetic standard model prices are USD 2 input and USD 8 output per million tokens.

Why: Provides reproducible capacity/cost hypotheses, not measured provider prices.

Proposed owner: Engineering lead

Validation: Measure branch mix, token distribution, throughput and approved model quote.

Launch blocker: false

### H8

Proposed release quality gates are zero safety failures in fixed synthetic guard suite, 99% line arithmetic agreement, 98% supported evidence precision and 20% median handling-time reduction.

Why: Explicit hypotheses support go/no-go decisions; do not claim proven benefits.

Proposed owner: Claims product owner

Validation: Baseline measurement, representative held-out evaluation and sign-off on targets.

Launch blocker: false

### H9

Scope is one insurer product, one currency per claim and machine-readable or supported scanned inpatient reimbursement claims. Appeals, fraud decisions, outpatient, multi-currency and medical necessity decisions are human-only.

Why: Limits initial policy complexity and avoids pretending to give medical advice.

Proposed owner: Claims product owner

Validation: Approve product/language/OCR support manifest and exception routing.

Launch blocker: true

- context/CTX1: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- context/CTX2: H2: A tenant policy registry provides legally reviewed immutable policy/endorsement versions, effective intervals, member binding and explicit claim-date selection rules.
- context/CTX3: H9: Scope is one insurer product, one currency per claim and machine-readable or supported scanned inpatient reimbursement claims. Appeals, fraud decisions, outpatient, multi-currency and medical necessity decisions are human-only.
- context/CTX4: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- context/CTX5: H8: Proposed release quality gates are zero safety failures in fixed synthetic guard suite, 99% line arithmetic agreement, 98% supported evidence precision and 20% median handling-time reduction.
- context/CTX6: H5: Use restricted medical evidence storage, encrypted transport and storage, tenant keys, no provider training, no raw content in logs; proposed 30-day working-copy deletion after case close subject to insurer approved retention/legal holds.
- tasks/T0: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- tasks/T0: H9: Scope is one insurer product, one currency per claim and machine-readable or supported scanned inpatient reimbursement claims. Appeals, fraud decisions, outpatient, multi-currency and medical necessity decisions are human-only.
- tasks/T1: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- tasks/T1: H9: Scope is one insurer product, one currency per claim and machine-readable or supported scanned inpatient reimbursement claims. Appeals, fraud decisions, outpatient, multi-currency and medical necessity decisions are human-only.
- tasks/T2: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- tasks/T2: H9: Scope is one insurer product, one currency per claim and machine-readable or supported scanned inpatient reimbursement claims. Appeals, fraud decisions, outpatient, multi-currency and medical necessity decisions are human-only.
- tasks/T3: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- tasks/T3: H9: Scope is one insurer product, one currency per claim and machine-readable or supported scanned inpatient reimbursement claims. Appeals, fraud decisions, outpatient, multi-currency and medical necessity decisions are human-only.
- tasks/T4: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- tasks/T4: H9: Scope is one insurer product, one currency per claim and machine-readable or supported scanned inpatient reimbursement claims. Appeals, fraud decisions, outpatient, multi-currency and medical necessity decisions are human-only.
- tasks/T4.1: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- tasks/T4.1: H9: Scope is one insurer product, one currency per claim and machine-readable or supported scanned inpatient reimbursement claims. Appeals, fraud decisions, outpatient, multi-currency and medical necessity decisions are human-only.
- tasks/T4.2: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- tasks/T4.2: H9: Scope is one insurer product, one currency per claim and machine-readable or supported scanned inpatient reimbursement claims. Appeals, fraud decisions, outpatient, multi-currency and medical necessity decisions are human-only.
- tasks/T4.3: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- tasks/T4.3: H9: Scope is one insurer product, one currency per claim and machine-readable or supported scanned inpatient reimbursement claims. Appeals, fraud decisions, outpatient, multi-currency and medical necessity decisions are human-only.
- tasks/A1: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- tasks/A1: H5: Use restricted medical evidence storage, encrypted transport and storage, tenant keys, no provider training, no raw content in logs; proposed 30-day working-copy deletion after case close subject to insurer approved retention/legal holds.
- tasks/A2: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- tasks/A2: H5: Use restricted medical evidence storage, encrypted transport and storage, tenant keys, no provider training, no raw content in logs; proposed 30-day working-copy deletion after case close subject to insurer approved retention/legal holds.
- tasks/A3: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- tasks/A3: H5: Use restricted medical evidence storage, encrypted transport and storage, tenant keys, no provider training, no raw content in logs; proposed 30-day working-copy deletion after case close subject to insurer approved retention/legal holds.
- tasks/A4: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- tasks/A4: H5: Use restricted medical evidence storage, encrypted transport and storage, tenant keys, no provider training, no raw content in logs; proposed 30-day working-copy deletion after case close subject to insurer approved retention/legal holds.
- components/C1: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- components/C1: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- components/C2: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- components/C2: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- components/C3: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- components/C3: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- components/C4: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- components/C4: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- components/C5: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- components/C5: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- components/C6: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- components/C6: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- components/C7: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- components/C7: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- workflow/W1: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- workflow/W1: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- workflow/W1: H6: Human queues are staffed by claims operations: acknowledge in 4 elapsed hours, review in 2 elapsed days; overdue goes to duty manager at 4h and head of claims at 48h. Timers run UTC 24x7.
- workflow/W2: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- workflow/W2: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- workflow/W2: H6: Human queues are staffed by claims operations: acknowledge in 4 elapsed hours, review in 2 elapsed days; overdue goes to duty manager at 4h and head of claims at 48h. Timers run UTC 24x7.
- workflow/W3: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- workflow/W3: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- workflow/W3: H6: Human queues are staffed by claims operations: acknowledge in 4 elapsed hours, review in 2 elapsed days; overdue goes to duty manager at 4h and head of claims at 48h. Timers run UTC 24x7.
- workflow/W4: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- workflow/W4: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- workflow/W4: H6: Human queues are staffed by claims operations: acknowledge in 4 elapsed hours, review in 2 elapsed days; overdue goes to duty manager at 4h and head of claims at 48h. Timers run UTC 24x7.
- workflow/W5: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- workflow/W5: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- workflow/W5: H6: Human queues are staffed by claims operations: acknowledge in 4 elapsed hours, review in 2 elapsed days; overdue goes to duty manager at 4h and head of claims at 48h. Timers run UTC 24x7.
- workflow/W6: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- workflow/W6: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- workflow/W6: H6: Human queues are staffed by claims operations: acknowledge in 4 elapsed hours, review in 2 elapsed days; overdue goes to duty manager at 4h and head of claims at 48h. Timers run UTC 24x7.
- workflow/W7: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- workflow/W7: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- workflow/W7: H6: Human queues are staffed by claims operations: acknowledge in 4 elapsed hours, review in 2 elapsed days; overdue goes to duty manager at 4h and head of claims at 48h. Timers run UTC 24x7.
- workflow/W8: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- workflow/W8: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- workflow/W8: H6: Human queues are staffed by claims operations: acknowledge in 4 elapsed hours, review in 2 elapsed days; overdue goes to duty manager at 4h and head of claims at 48h. Timers run UTC 24x7.
- workflow/W9: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- workflow/W9: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- workflow/W9: H6: Human queues are staffed by claims operations: acknowledge in 4 elapsed hours, review in 2 elapsed days; overdue goes to duty manager at 4h and head of claims at 48h. Timers run UTC 24x7.
- workflow/W10: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- workflow/W10: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- workflow/W10: H6: Human queues are staffed by claims operations: acknowledge in 4 elapsed hours, review in 2 elapsed days; overdue goes to duty manager at 4h and head of claims at 48h. Timers run UTC 24x7.
- workflow/W11: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- workflow/W11: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- workflow/W11: H6: Human queues are staffed by claims operations: acknowledge in 4 elapsed hours, review in 2 elapsed days; overdue goes to duty manager at 4h and head of claims at 48h. Timers run UTC 24x7.
- workflow/W12: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- workflow/W12: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- workflow/W12: H6: Human queues are staffed by claims operations: acknowledge in 4 elapsed hours, review in 2 elapsed days; overdue goes to duty manager at 4h and head of claims at 48h. Timers run UTC 24x7.
- workflow/W13: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- workflow/W13: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- workflow/W13: H6: Human queues are staffed by claims operations: acknowledge in 4 elapsed hours, review in 2 elapsed days; overdue goes to duty manager at 4h and head of claims at 48h. Timers run UTC 24x7.
- framework/F1: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- framework/F1: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- framework/F1: H5: Use restricted medical evidence storage, encrypted transport and storage, tenant keys, no provider training, no raw content in logs; proposed 30-day working-copy deletion after case close subject to insurer approved retention/legal holds.
- framework/F2: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- framework/F2: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- framework/F2: H5: Use restricted medical evidence storage, encrypted transport and storage, tenant keys, no provider training, no raw content in logs; proposed 30-day working-copy deletion after case close subject to insurer approved retention/legal holds.
- framework/F3: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- framework/F3: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- framework/F3: H5: Use restricted medical evidence storage, encrypted transport and storage, tenant keys, no provider training, no raw content in logs; proposed 30-day working-copy deletion after case close subject to insurer approved retention/legal holds.
- framework/F4: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- framework/F4: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- framework/F4: H5: Use restricted medical evidence storage, encrypted transport and storage, tenant keys, no provider training, no raw content in logs; proposed 30-day working-copy deletion after case close subject to insurer approved retention/legal holds.
- framework/F5: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- framework/F5: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- framework/F5: H5: Use restricted medical evidence storage, encrypted transport and storage, tenant keys, no provider training, no raw content in logs; proposed 30-day working-copy deletion after case close subject to insurer approved retention/legal holds.
- models/M1: H7: Illustrative volume is 1000 cases/month; 80% reach the model and 5% of reached cases need one schema repair retry. Synthetic standard model prices are USD 2 input and USD 8 output per million tokens.
- models/M1: H8: Proposed release quality gates are zero safety failures in fixed synthetic guard suite, 99% line arithmetic agreement, 98% supported evidence precision and 20% median handling-time reduction.
- fmea/FM1: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- fmea/FM1: H2: A tenant policy registry provides legally reviewed immutable policy/endorsement versions, effective intervals, member binding and explicit claim-date selection rules.
- fmea/FM1: H3: Synthetic rule pack HC1 uses admission-date selection, inclusive discharge day, INR minor units, room-rent cap only on room lines, no proportional deduction, zero deductible and zero coinsurance.
- fmea/FM1: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- fmea/FM1: H5: Use restricted medical evidence storage, encrypted transport and storage, tenant keys, no provider training, no raw content in logs; proposed 30-day working-copy deletion after case close subject to insurer approved retention/legal holds.
- fmea/FM1: H6: Human queues are staffed by claims operations: acknowledge in 4 elapsed hours, review in 2 elapsed days; overdue goes to duty manager at 4h and head of claims at 48h. Timers run UTC 24x7.
- fmea/FM2: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- fmea/FM2: H2: A tenant policy registry provides legally reviewed immutable policy/endorsement versions, effective intervals, member binding and explicit claim-date selection rules.
- fmea/FM2: H3: Synthetic rule pack HC1 uses admission-date selection, inclusive discharge day, INR minor units, room-rent cap only on room lines, no proportional deduction, zero deductible and zero coinsurance.
- fmea/FM2: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- fmea/FM2: H5: Use restricted medical evidence storage, encrypted transport and storage, tenant keys, no provider training, no raw content in logs; proposed 30-day working-copy deletion after case close subject to insurer approved retention/legal holds.
- fmea/FM2: H6: Human queues are staffed by claims operations: acknowledge in 4 elapsed hours, review in 2 elapsed days; overdue goes to duty manager at 4h and head of claims at 48h. Timers run UTC 24x7.
- fmea/FM3: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- fmea/FM3: H2: A tenant policy registry provides legally reviewed immutable policy/endorsement versions, effective intervals, member binding and explicit claim-date selection rules.
- fmea/FM3: H3: Synthetic rule pack HC1 uses admission-date selection, inclusive discharge day, INR minor units, room-rent cap only on room lines, no proportional deduction, zero deductible and zero coinsurance.
- fmea/FM3: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- fmea/FM3: H5: Use restricted medical evidence storage, encrypted transport and storage, tenant keys, no provider training, no raw content in logs; proposed 30-day working-copy deletion after case close subject to insurer approved retention/legal holds.
- fmea/FM3: H6: Human queues are staffed by claims operations: acknowledge in 4 elapsed hours, review in 2 elapsed days; overdue goes to duty manager at 4h and head of claims at 48h. Timers run UTC 24x7.
- fmea/FM4: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- fmea/FM4: H2: A tenant policy registry provides legally reviewed immutable policy/endorsement versions, effective intervals, member binding and explicit claim-date selection rules.
- fmea/FM4: H3: Synthetic rule pack HC1 uses admission-date selection, inclusive discharge day, INR minor units, room-rent cap only on room lines, no proportional deduction, zero deductible and zero coinsurance.
- fmea/FM4: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- fmea/FM4: H5: Use restricted medical evidence storage, encrypted transport and storage, tenant keys, no provider training, no raw content in logs; proposed 30-day working-copy deletion after case close subject to insurer approved retention/legal holds.
- fmea/FM4: H6: Human queues are staffed by claims operations: acknowledge in 4 elapsed hours, review in 2 elapsed days; overdue goes to duty manager at 4h and head of claims at 48h. Timers run UTC 24x7.
- fmea/FM5: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- fmea/FM5: H2: A tenant policy registry provides legally reviewed immutable policy/endorsement versions, effective intervals, member binding and explicit claim-date selection rules.
- fmea/FM5: H3: Synthetic rule pack HC1 uses admission-date selection, inclusive discharge day, INR minor units, room-rent cap only on room lines, no proportional deduction, zero deductible and zero coinsurance.
- fmea/FM5: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- fmea/FM5: H5: Use restricted medical evidence storage, encrypted transport and storage, tenant keys, no provider training, no raw content in logs; proposed 30-day working-copy deletion after case close subject to insurer approved retention/legal holds.
- fmea/FM5: H6: Human queues are staffed by claims operations: acknowledge in 4 elapsed hours, review in 2 elapsed days; overdue goes to duty manager at 4h and head of claims at 48h. Timers run UTC 24x7.
- fmea/FM6: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- fmea/FM6: H2: A tenant policy registry provides legally reviewed immutable policy/endorsement versions, effective intervals, member binding and explicit claim-date selection rules.
- fmea/FM6: H3: Synthetic rule pack HC1 uses admission-date selection, inclusive discharge day, INR minor units, room-rent cap only on room lines, no proportional deduction, zero deductible and zero coinsurance.
- fmea/FM6: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- fmea/FM6: H5: Use restricted medical evidence storage, encrypted transport and storage, tenant keys, no provider training, no raw content in logs; proposed 30-day working-copy deletion after case close subject to insurer approved retention/legal holds.
- fmea/FM6: H6: Human queues are staffed by claims operations: acknowledge in 4 elapsed hours, review in 2 elapsed days; overdue goes to duty manager at 4h and head of claims at 48h. Timers run UTC 24x7.
- fmea/FM7: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- fmea/FM7: H2: A tenant policy registry provides legally reviewed immutable policy/endorsement versions, effective intervals, member binding and explicit claim-date selection rules.
- fmea/FM7: H3: Synthetic rule pack HC1 uses admission-date selection, inclusive discharge day, INR minor units, room-rent cap only on room lines, no proportional deduction, zero deductible and zero coinsurance.
- fmea/FM7: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- fmea/FM7: H5: Use restricted medical evidence storage, encrypted transport and storage, tenant keys, no provider training, no raw content in logs; proposed 30-day working-copy deletion after case close subject to insurer approved retention/legal holds.
- fmea/FM7: H6: Human queues are staffed by claims operations: acknowledge in 4 elapsed hours, review in 2 elapsed days; overdue goes to duty manager at 4h and head of claims at 48h. Timers run UTC 24x7.
- fmea/FM8: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- fmea/FM8: H2: A tenant policy registry provides legally reviewed immutable policy/endorsement versions, effective intervals, member binding and explicit claim-date selection rules.
- fmea/FM8: H3: Synthetic rule pack HC1 uses admission-date selection, inclusive discharge day, INR minor units, room-rent cap only on room lines, no proportional deduction, zero deductible and zero coinsurance.
- fmea/FM8: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- fmea/FM8: H5: Use restricted medical evidence storage, encrypted transport and storage, tenant keys, no provider training, no raw content in logs; proposed 30-day working-copy deletion after case close subject to insurer approved retention/legal holds.
- fmea/FM8: H6: Human queues are staffed by claims operations: acknowledge in 4 elapsed hours, review in 2 elapsed days; overdue goes to duty manager at 4h and head of claims at 48h. Timers run UTC 24x7.
- fmea/FM9: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- fmea/FM9: H2: A tenant policy registry provides legally reviewed immutable policy/endorsement versions, effective intervals, member binding and explicit claim-date selection rules.
- fmea/FM9: H3: Synthetic rule pack HC1 uses admission-date selection, inclusive discharge day, INR minor units, room-rent cap only on room lines, no proportional deduction, zero deductible and zero coinsurance.
- fmea/FM9: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- fmea/FM9: H5: Use restricted medical evidence storage, encrypted transport and storage, tenant keys, no provider training, no raw content in logs; proposed 30-day working-copy deletion after case close subject to insurer approved retention/legal holds.
- fmea/FM9: H6: Human queues are staffed by claims operations: acknowledge in 4 elapsed hours, review in 2 elapsed days; overdue goes to duty manager at 4h and head of claims at 48h. Timers run UTC 24x7.
- fmea/FM10: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- fmea/FM10: H2: A tenant policy registry provides legally reviewed immutable policy/endorsement versions, effective intervals, member binding and explicit claim-date selection rules.
- fmea/FM10: H3: Synthetic rule pack HC1 uses admission-date selection, inclusive discharge day, INR minor units, room-rent cap only on room lines, no proportional deduction, zero deductible and zero coinsurance.
- fmea/FM10: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- fmea/FM10: H5: Use restricted medical evidence storage, encrypted transport and storage, tenant keys, no provider training, no raw content in logs; proposed 30-day working-copy deletion after case close subject to insurer approved retention/legal holds.
- fmea/FM10: H6: Human queues are staffed by claims operations: acknowledge in 4 elapsed hours, review in 2 elapsed days; overdue goes to duty manager at 4h and head of claims at 48h. Timers run UTC 24x7.
- evals/EV1: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- evals/EV1: H3: Synthetic rule pack HC1 uses admission-date selection, inclusive discharge day, INR minor units, room-rent cap only on room lines, no proportional deduction, zero deductible and zero coinsurance.
- evals/EV1: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- evals/EV1: H6: Human queues are staffed by claims operations: acknowledge in 4 elapsed hours, review in 2 elapsed days; overdue goes to duty manager at 4h and head of claims at 48h. Timers run UTC 24x7.
- evals/EV2: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- evals/EV2: H3: Synthetic rule pack HC1 uses admission-date selection, inclusive discharge day, INR minor units, room-rent cap only on room lines, no proportional deduction, zero deductible and zero coinsurance.
- evals/EV2: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- evals/EV2: H6: Human queues are staffed by claims operations: acknowledge in 4 elapsed hours, review in 2 elapsed days; overdue goes to duty manager at 4h and head of claims at 48h. Timers run UTC 24x7.
- evals/EV3: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- evals/EV3: H3: Synthetic rule pack HC1 uses admission-date selection, inclusive discharge day, INR minor units, room-rent cap only on room lines, no proportional deduction, zero deductible and zero coinsurance.
- evals/EV3: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- evals/EV3: H6: Human queues are staffed by claims operations: acknowledge in 4 elapsed hours, review in 2 elapsed days; overdue goes to duty manager at 4h and head of claims at 48h. Timers run UTC 24x7.
- evals/EV4: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- evals/EV4: H3: Synthetic rule pack HC1 uses admission-date selection, inclusive discharge day, INR minor units, room-rent cap only on room lines, no proportional deduction, zero deductible and zero coinsurance.
- evals/EV4: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- evals/EV4: H6: Human queues are staffed by claims operations: acknowledge in 4 elapsed hours, review in 2 elapsed days; overdue goes to duty manager at 4h and head of claims at 48h. Timers run UTC 24x7.
- evals/EV5: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- evals/EV5: H3: Synthetic rule pack HC1 uses admission-date selection, inclusive discharge day, INR minor units, room-rent cap only on room lines, no proportional deduction, zero deductible and zero coinsurance.
- evals/EV5: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- evals/EV5: H6: Human queues are staffed by claims operations: acknowledge in 4 elapsed hours, review in 2 elapsed days; overdue goes to duty manager at 4h and head of claims at 48h. Timers run UTC 24x7.
- evals/EV6: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- evals/EV6: H3: Synthetic rule pack HC1 uses admission-date selection, inclusive discharge day, INR minor units, room-rent cap only on room lines, no proportional deduction, zero deductible and zero coinsurance.
- evals/EV6: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- evals/EV6: H6: Human queues are staffed by claims operations: acknowledge in 4 elapsed hours, review in 2 elapsed days; overdue goes to duty manager at 4h and head of claims at 48h. Timers run UTC 24x7.
- evals/EV7: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- evals/EV7: H3: Synthetic rule pack HC1 uses admission-date selection, inclusive discharge day, INR minor units, room-rent cap only on room lines, no proportional deduction, zero deductible and zero coinsurance.
- evals/EV7: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- evals/EV7: H6: Human queues are staffed by claims operations: acknowledge in 4 elapsed hours, review in 2 elapsed days; overdue goes to duty manager at 4h and head of claims at 48h. Timers run UTC 24x7.
- evals/EV8: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- evals/EV8: H3: Synthetic rule pack HC1 uses admission-date selection, inclusive discharge day, INR minor units, room-rent cap only on room lines, no proportional deduction, zero deductible and zero coinsurance.
- evals/EV8: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- evals/EV8: H6: Human queues are staffed by claims operations: acknowledge in 4 elapsed hours, review in 2 elapsed days; overdue goes to duty manager at 4h and head of claims at 48h. Timers run UTC 24x7.
- evals/EV9: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- evals/EV9: H3: Synthetic rule pack HC1 uses admission-date selection, inclusive discharge day, INR minor units, room-rent cap only on room lines, no proportional deduction, zero deductible and zero coinsurance.
- evals/EV9: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- evals/EV9: H6: Human queues are staffed by claims operations: acknowledge in 4 elapsed hours, review in 2 elapsed days; overdue goes to duty manager at 4h and head of claims at 48h. Timers run UTC 24x7.
- evals/EV10: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- evals/EV10: H3: Synthetic rule pack HC1 uses admission-date selection, inclusive discharge day, INR minor units, room-rent cap only on room lines, no proportional deduction, zero deductible and zero coinsurance.
- evals/EV10: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- evals/EV10: H6: Human queues are staffed by claims operations: acknowledge in 4 elapsed hours, review in 2 elapsed days; overdue goes to duty manager at 4h and head of claims at 48h. Timers run UTC 24x7.
- evals/EV11: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- evals/EV11: H3: Synthetic rule pack HC1 uses admission-date selection, inclusive discharge day, INR minor units, room-rent cap only on room lines, no proportional deduction, zero deductible and zero coinsurance.
- evals/EV11: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- evals/EV11: H6: Human queues are staffed by claims operations: acknowledge in 4 elapsed hours, review in 2 elapsed days; overdue goes to duty manager at 4h and head of claims at 48h. Timers run UTC 24x7.
- evals/EV12: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- evals/EV12: H3: Synthetic rule pack HC1 uses admission-date selection, inclusive discharge day, INR minor units, room-rent cap only on room lines, no proportional deduction, zero deductible and zero coinsurance.
- evals/EV12: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- evals/EV12: H6: Human queues are staffed by claims operations: acknowledge in 4 elapsed hours, review in 2 elapsed days; overdue goes to duty manager at 4h and head of claims at 48h. Timers run UTC 24x7.
- evals/EV13: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- evals/EV13: H3: Synthetic rule pack HC1 uses admission-date selection, inclusive discharge day, INR minor units, room-rent cap only on room lines, no proportional deduction, zero deductible and zero coinsurance.
- evals/EV13: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- evals/EV13: H6: Human queues are staffed by claims operations: acknowledge in 4 elapsed hours, review in 2 elapsed days; overdue goes to duty manager at 4h and head of claims at 48h. Timers run UTC 24x7.
- evals/EV14: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- evals/EV14: H3: Synthetic rule pack HC1 uses admission-date selection, inclusive discharge day, INR minor units, room-rent cap only on room lines, no proportional deduction, zero deductible and zero coinsurance.
- evals/EV14: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- evals/EV14: H6: Human queues are staffed by claims operations: acknowledge in 4 elapsed hours, review in 2 elapsed days; overdue goes to duty manager at 4h and head of claims at 48h. Timers run UTC 24x7.
- evals/EV15: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- evals/EV15: H3: Synthetic rule pack HC1 uses admission-date selection, inclusive discharge day, INR minor units, room-rent cap only on room lines, no proportional deduction, zero deductible and zero coinsurance.
- evals/EV15: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- evals/EV15: H6: Human queues are staffed by claims operations: acknowledge in 4 elapsed hours, review in 2 elapsed days; overdue goes to duty manager at 4h and head of claims at 48h. Timers run UTC 24x7.
- evals/EV16: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- evals/EV16: H3: Synthetic rule pack HC1 uses admission-date selection, inclusive discharge day, INR minor units, room-rent cap only on room lines, no proportional deduction, zero deductible and zero coinsurance.
- evals/EV16: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- evals/EV16: H6: Human queues are staffed by claims operations: acknowledge in 4 elapsed hours, review in 2 elapsed days; overdue goes to duty manager at 4h and head of claims at 48h. Timers run UTC 24x7.
- evals/EV17: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- evals/EV17: H3: Synthetic rule pack HC1 uses admission-date selection, inclusive discharge day, INR minor units, room-rent cap only on room lines, no proportional deduction, zero deductible and zero coinsurance.
- evals/EV17: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- evals/EV17: H6: Human queues are staffed by claims operations: acknowledge in 4 elapsed hours, review in 2 elapsed days; overdue goes to duty manager at 4h and head of claims at 48h. Timers run UTC 24x7.
- evals/EV18: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- evals/EV18: H3: Synthetic rule pack HC1 uses admission-date selection, inclusive discharge day, INR minor units, room-rent cap only on room lines, no proportional deduction, zero deductible and zero coinsurance.
- evals/EV18: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- evals/EV18: H6: Human queues are staffed by claims operations: acknowledge in 4 elapsed hours, review in 2 elapsed days; overdue goes to duty manager at 4h and head of claims at 48h. Timers run UTC 24x7.
- evals/EV19: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- evals/EV19: H3: Synthetic rule pack HC1 uses admission-date selection, inclusive discharge day, INR minor units, room-rent cap only on room lines, no proportional deduction, zero deductible and zero coinsurance.
- evals/EV19: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- evals/EV19: H6: Human queues are staffed by claims operations: acknowledge in 4 elapsed hours, review in 2 elapsed days; overdue goes to duty manager at 4h and head of claims at 48h. Timers run UTC 24x7.
- evals/EV20: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- evals/EV20: H3: Synthetic rule pack HC1 uses admission-date selection, inclusive discharge day, INR minor units, room-rent cap only on room lines, no proportional deduction, zero deductible and zero coinsurance.
- evals/EV20: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- evals/EV20: H6: Human queues are staffed by claims operations: acknowledge in 4 elapsed hours, review in 2 elapsed days; overdue goes to duty manager at 4h and head of claims at 48h. Timers run UTC 24x7.
- evals/EV21: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- evals/EV21: H3: Synthetic rule pack HC1 uses admission-date selection, inclusive discharge day, INR minor units, room-rent cap only on room lines, no proportional deduction, zero deductible and zero coinsurance.
- evals/EV21: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- evals/EV21: H6: Human queues are staffed by claims operations: acknowledge in 4 elapsed hours, review in 2 elapsed days; overdue goes to duty manager at 4h and head of claims at 48h. Timers run UTC 24x7.
- evals/EV22: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- evals/EV22: H3: Synthetic rule pack HC1 uses admission-date selection, inclusive discharge day, INR minor units, room-rent cap only on room lines, no proportional deduction, zero deductible and zero coinsurance.
- evals/EV22: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- evals/EV22: H6: Human queues are staffed by claims operations: acknowledge in 4 elapsed hours, review in 2 elapsed days; overdue goes to duty manager at 4h and head of claims at 48h. Timers run UTC 24x7.
- evals/EV26: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- evals/EV26: H3: Synthetic rule pack HC1 uses admission-date selection, inclusive discharge day, INR minor units, room-rent cap only on room lines, no proportional deduction, zero deductible and zero coinsurance.
- evals/EV26: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- evals/EV26: H6: Human queues are staffed by claims operations: acknowledge in 4 elapsed hours, review in 2 elapsed days; overdue goes to duty manager at 4h and head of claims at 48h. Timers run UTC 24x7.
- evals/EV23: H2: A tenant policy registry provides legally reviewed immutable policy/endorsement versions, effective intervals, member binding and explicit claim-date selection rules.
- evals/EV23: H5: Use restricted medical evidence storage, encrypted transport and storage, tenant keys, no provider training, no raw content in logs; proposed 30-day working-copy deletion after case close subject to insurer approved retention/legal holds.
- evals/EV23: H8: Proposed release quality gates are zero safety failures in fixed synthetic guard suite, 99% line arithmetic agreement, 98% supported evidence precision and 20% median handling-time reduction.
- evals/EV24: H5: Use restricted medical evidence storage, encrypted transport and storage, tenant keys, no provider training, no raw content in logs; proposed 30-day working-copy deletion after case close subject to insurer approved retention/legal holds.
- evals/EV24: H6: Human queues are staffed by claims operations: acknowledge in 4 elapsed hours, review in 2 elapsed days; overdue goes to duty manager at 4h and head of claims at 48h. Timers run UTC 24x7.
- evals/EV24: H8: Proposed release quality gates are zero safety failures in fixed synthetic guard suite, 99% line arithmetic agreement, 98% supported evidence precision and 20% median handling-time reduction.
- evals/EV25: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- evals/EV25: H2: A tenant policy registry provides legally reviewed immutable policy/endorsement versions, effective intervals, member binding and explicit claim-date selection rules.
- evals/EV25: H3: Synthetic rule pack HC1 uses admission-date selection, inclusive discharge day, INR minor units, room-rent cap only on room lines, no proportional deduction, zero deductible and zero coinsurance.
- evals/EV25: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- evals/EV25: H5: Use restricted medical evidence storage, encrypted transport and storage, tenant keys, no provider training, no raw content in logs; proposed 30-day working-copy deletion after case close subject to insurer approved retention/legal holds.
- evals/EV25: H6: Human queues are staffed by claims operations: acknowledge in 4 elapsed hours, review in 2 elapsed days; overdue goes to duty manager at 4h and head of claims at 48h. Timers run UTC 24x7.
- evals/EV25: H8: Proposed release quality gates are zero safety failures in fixed synthetic guard suite, 99% line arithmetic agreement, 98% supported evidence precision and 20% median handling-time reduction.
- evals/EV25: H9: Scope is one insurer product, one currency per claim and machine-readable or supported scanned inpatient reimbursement claims. Appeals, fraud decisions, outpatient, multi-currency and medical necessity decisions are human-only.
- rollout/R1: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- rollout/R1: H6: Human queues are staffed by claims operations: acknowledge in 4 elapsed hours, review in 2 elapsed days; overdue goes to duty manager at 4h and head of claims at 48h. Timers run UTC 24x7.
- rollout/R1: H8: Proposed release quality gates are zero safety failures in fixed synthetic guard suite, 99% line arithmetic agreement, 98% supported evidence precision and 20% median handling-time reduction.
- rollout/R2: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- rollout/R2: H6: Human queues are staffed by claims operations: acknowledge in 4 elapsed hours, review in 2 elapsed days; overdue goes to duty manager at 4h and head of claims at 48h. Timers run UTC 24x7.
- rollout/R2: H8: Proposed release quality gates are zero safety failures in fixed synthetic guard suite, 99% line arithmetic agreement, 98% supported evidence precision and 20% median handling-time reduction.
- rollout/R3: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- rollout/R3: H6: Human queues are staffed by claims operations: acknowledge in 4 elapsed hours, review in 2 elapsed days; overdue goes to duty manager at 4h and head of claims at 48h. Timers run UTC 24x7.
- rollout/R3: H8: Proposed release quality gates are zero safety failures in fixed synthetic guard suite, 99% line arithmetic agreement, 98% supported evidence precision and 20% median handling-time reduction.
- rollout/R4: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- rollout/R4: H6: Human queues are staffed by claims operations: acknowledge in 4 elapsed hours, review in 2 elapsed days; overdue goes to duty manager at 4h and head of claims at 48h. Timers run UTC 24x7.
- rollout/R4: H8: Proposed release quality gates are zero safety failures in fixed synthetic guard suite, 99% line arithmetic agreement, 98% supported evidence precision and 20% median handling-time reduction.
- rollout/R5: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- rollout/R5: H6: Human queues are staffed by claims operations: acknowledge in 4 elapsed hours, review in 2 elapsed days; overdue goes to duty manager at 4h and head of claims at 48h. Timers run UTC 24x7.
- rollout/R5: H8: Proposed release quality gates are zero safety failures in fixed synthetic guard suite, 99% line arithmetic agreement, 98% supported evidence precision and 20% median handling-time reduction.
- rollout/R6: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- rollout/R6: H6: Human queues are staffed by claims operations: acknowledge in 4 elapsed hours, review in 2 elapsed days; overdue goes to duty manager at 4h and head of claims at 48h. Timers run UTC 24x7.
- rollout/R6: H8: Proposed release quality gates are zero safety failures in fixed synthetic guard suite, 99% line arithmetic agreement, 98% supported evidence precision and 20% median handling-time reduction.
- export/X1: H1: Release one recommends eligible amounts and routes all decisions to authorized insurer adjudicators; it cannot issue payment, deny coverage or notify claimants.
- export/X1: H2: A tenant policy registry provides legally reviewed immutable policy/endorsement versions, effective intervals, member binding and explicit claim-date selection rules.
- export/X1: H3: Synthetic rule pack HC1 uses admission-date selection, inclusive discharge day, INR minor units, room-rent cap only on room lines, no proportional deduction, zero deductible and zero coinsurance.
- export/X1: H4: Internal case store supports tenant scoped transactions, optimistic versions, immutable evidence hashes, durable outbox and operation lookup. All external adapters remain unverified.
- export/X1: H5: Use restricted medical evidence storage, encrypted transport and storage, tenant keys, no provider training, no raw content in logs; proposed 30-day working-copy deletion after case close subject to insurer approved retention/legal holds.
- export/X1: H6: Human queues are staffed by claims operations: acknowledge in 4 elapsed hours, review in 2 elapsed days; overdue goes to duty manager at 4h and head of claims at 48h. Timers run UTC 24x7.
- export/X1: H9: Scope is one insurer product, one currency per claim and machine-readable or supported scanned inpatient reimbursement claims. Appeals, fraud decisions, outpatient, multi-currency and medical necessity decisions are human-only.

## Review and tooling limitations

- Self-review by host model; no independent evaluator or stakeholder sign-off.
- Frozen v1 validator verifies structure/references only. No business test harness, insurer integration, medical-data processing or production controls executed.
- Synthetic fixtures and illustrative budgets do not prove accuracy, compliance, policy correctness or savings. H1-H6/H9 remain live-use blockers.
- PDF is deferred by explicit parent instruction; this run produces canonical JSON and companion exports only.
- Design-only tooling: this helper makes no provider, network or business API calls and executes no business assertions; optional host-assistant research is outside this statement.
- Schema, reference, graph and ID-coverage checks do not establish semantic completeness, source truth, actual human authorization or production safety.
- Review scores and evidence are supplied by the reviewing agent; the helper checks their shape and declared pass conditions, not their truth.
- FMEA action/control text is required where specified; the helper does not verify ownership, release authority, regulatory compliance or risk acceptance.
