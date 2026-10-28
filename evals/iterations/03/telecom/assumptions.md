# Telecom complaint and service credit assistant

> PASS · DESIGN ONLY. Review is a design judgement; no business controls or provider reliability were executed.

Review method: self-review; round 3.

Review dimensions (supplied scores):

- D1: 3/4 — CTX1 and T0/T3 sequence/choice cover active-service investigation, outage credit, supervisor, cancellation and owned unknown outcomes; cash payouts and network repair excluded.
- D2: 3/4 — Every leaf T1,T2,T3.1,T3.2,T3.3,T4 is served by C/W and goldens. FM1-FM9 links derive from EV1-EV23 and are reciprocal. Source brief exact quote; H1-H6 separate proposed policies and adapters.
- D3: 3/4 — W6 durable timers, W5 notice scheduling, W7 actual send, W10 all unknown paths reconcile, same-key one retry after final absence; W14 proof before W15; W16 owned unresolved terminal. EV6 now CREDITED plus cancellation flag.
- D4: 3/4 — C1-C9 define scope/evidence/status fields, required immutable command content, write response enums, 5s adapter deadlines, durable queue acknowledgement/escalation and read-only lookup beyond session.
- D5: 3/4 — C1 and C7 scope/active joins precede private reads and credit. C4 exact approved command, C7 fresh versions/authority and atomic uniqueness; C3 has explanation-only output with citation verification. H4 privacy is explicit launch gate.
- D6: 3/4 — H1-H4/H6 block launch on unverified policy, integration, staffing, privacy and notice evidence. H5/M1 illustrative volume/prices and all fixtures synthetic. Missing/conflicting records yield owned investigation.
- D7: 3/4 — F1 rejects open-ended/synchronous chain for durable code state machine; same comparison criteria persistence/timers/dedup/authority/recovery. F2 scopes principals; F3 compares relational/evidence/audit patterns across cloud/open-source as unverified candidates.
- D8: 3/4 — One M1 matches C3/W3. 2400*1/1e6+450*4/1e6=.0042 USD/call, <=.9 calls gives .00378/case and <=37.80/10000 cases; worst one call. No retries, timeout fallback, fine-tune only after labeled held-out improvement.
- D9: 3/4 — FM1-FM9 are case-specific with hypothetical S/O/D, actionable owners, gates and objective metrics. High severity and high RPN have no invented acceptance; guard failures tie to actual scoped tests.
- D10: 3/4 — EV1 valid arithmetic, EV2 wrong customer, EV3/14 stale/revoked, EV4 two concurrent operations, EV5/20 conflict/invented citation, EV6/16 uncertain/logout/cancel, EV7 proof failure, EV8 48h queue, EV9 missing policy, EV10/11/15 notices, EV12 cap overflow, EV13 signed supervisor, EV17 cancel, EV18 inactive, EV19 speed. Self-contained inputs and expected effects; EV21-EV23 explicitly release all 20 goldens.
- D11: 3/4 — R1 denominators/windows and censored resolution, R2 non-circular Shadow/Assist/Pilot/Scale gates and stop/reconcile policy, R3 account randomization and binary/log-hours sample-size methods, R4 proposed accountable role sign-offs.
- D12: 3/4 — X1 preserves exact C/W boundaries and shared state ownership; four milestones cover all components and linked tests. Full fixtures indexed outside build packets. No claim of executing business controls or receiving policy approval.

Review findings:

- ISS1 [major, resolved] workflow/W10: EV6 expects CREDITED_CANCEL_REQUESTED outside C9 outcome enum. Keep CREDITED with cancellationRequested flag; otherwise client state handling needs invention.
- ISS2 [major, resolved] evals/EV7: A malformed POST response does not prove zero ledger effects. Start fixture after uncertain authorized attempt, assert zero additional writes and UNKNOWN_OWNED with proof lock.
- ISS3 [major, resolved] framework/F1: Structural validator rejects alternatives string and presentation autonomy labels. Use array and allowed levels; rerun.
- ISS4 [major, resolved] workflow/W6: Wait notice edge targets a write node rather than a separate requester_notice role. Add durable notice scheduling node W5, then external delivery W7.
- ISS5 [major, resolved] export/X1: Several descriptions empty and W12 claims T3.3 outside C6 task contract. Populate meaningful descriptions and constrain W12 task claim.

## Proposed assumption ledger

### H1

Proposed policy P1: automatic outage credit only, in INR minor units, floor(monthly recurring service charge × verified outage minutes / billing-cycle minutes), limited to INR 500 and remaining cycle service charge. No automated speed or billing-error credit.

Why: A bounded first release needs a deterministic rule; real policy is unknown.

Proposed owner: Billing policy owner

Validation: Approve a versioned signed rule, tax treatment, rounding, eligible outage sources and customer notice text.

Launch blocker: true

### H2

Account and ledger adapters can enforce tenant/customer/active-connection scope, atomic incident-cycle uniqueness, policy/version checks, stable operation IDs and authoritative commit lookup.

Why: These are required capabilities, not verified API facts.

Proposed owner: Integration owner

Validation: Sandbox contract tests for all listed conditions; disable automatic credits if any capability is absent.

Launch blocker: true

### H3

Supervisor queue is staffed continuously; acknowledge within 2 elapsed hours, remind at 24 hours and escalate at 48 elapsed hours from intake. Approval is valid for 15 minutes and exact immutable command only.

Why: The brief permits a 48-hour wait but gives no staffing or approval rules.

Proposed owner: Support operations owner

Validation: Staffing roster, outage drills, legal approval of notice timing and authority matrix.

Launch blocker: true

### H4

Proposed privacy defaults: minimize to complaint-linked fields, no payment instruments, encrypted case records, tenant-scoped access, 90-day case retention and 365-day audit retention subject to legal approval.

Why: Privacy and retention rules were not supplied.

Proposed owner: Privacy owner

Validation: Approve residency, retention, deletion exceptions and access audits.

Launch blocker: true

### H5

Illustrative budget uses 10000 monthly cases, 90% identity-valid cases, one LLM call per valid case, 2400 input/450 output tokens, USD 1/4 per million input/output tokens; no model retry.

Why: Allows reproducible budgeting without invented provider prices or traffic.

Proposed owner: Product owner

Validation: Replace with measured branch mix, tested model quote and token logs before pilot.

Launch blocker: false

### H6

Notice delivery adapter supports stable notice IDs and lookup after uncertain send; authenticated in-app case status is always available.

Why: Customers need updates across session expiry.

Proposed owner: Messaging integration owner

Validation: Verify opt-in channels, deduplication, callbacks and readback in sandbox.

Launch blocker: true

- models/M1: H5 illustrative, not vendor quote.

## Review and tooling limitations

- Self-review by author, not independent review or stakeholder approval.
- Structural and semantic declarations passed helper; goldens are specifications, no business harness or real API tests ran.
- H1-H4,H6 remain launch blockers; policy legality, API support, continuous staffing and actual vendor performance have not been verified.
- PDF rendering and visual layout inspection are delegated to root and are not claimed complete in this source-only subtask.
- Design-only tooling: this helper makes no provider, network or business API calls and executes no business assertions; optional host-assistant research is outside this statement.
- Schema, reference, graph and ID-coverage checks do not establish semantic completeness, source truth, actual human authorization or production safety.
- Review scores and evidence are supplied by the reviewing agent; the helper checks their shape and declared pass conditions, not their truth.
- FMEA action/control text is required where specified; the helper does not verify ownership, release authority, regulatory compliance or risk acceptance.
