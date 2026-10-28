# Telecom complaint and service credit assistant

> NEEDS-WORK · DESIGN ONLY. Review is a design judgement; no business controls or provider reliability were executed.

Review method: independent-agent; round 1.

Review dimensions (supplied scores):

- D1: 3/4 — CTX1 and T0/T3 bound the outage-credit release, separate speed/billing human work, and state sequence/choice precedence. W1 and W14–W16 retain missing-input/cancellation/owned outcomes. C1 does not explicitly resolve multiple active connections; S8.5 fails.
- D2: 3/4 — Task leaves T1/T2/T3.1/T3.2/T3.3/T4 link through components, workflow and EV1–EV23; FM1–FM9 links are reciprocal. H1–H6 honestly label policy, staffing, privacy and integration hypotheses. Canonical golden data uses serialized JSON while semantic fixture copies are objects; validator accepts this, contrary to literal semantic-contract wording.
- D3: 3/4 — W1 is reachable entry; W15/W16 are explicit terminals. W9/W7/W12 uncertain outcomes reach W10; C8 requires ABSENT_FINAL before a bounded same-key retry. W6 defines UTC queue timers and W8 bounds failed approval correction. C7 uses uniqueness and cycle locking.
- D4: 3/4 — C1–C9 separate identity/evidence, explanation, rule validation, queue, notice, credit, reconciliation and proof. C4 enumerates immutable command fields and C7 specifies target original charge and response/error states. H2/H6 explicitly block live use pending adapter capability verification; these are proposed port contracts, not verified APIs.
- D5: 3/4 — C3 has no write credentials or amount/identity authority; C4 computes money, C7 refreshes authorization and ledger state. C9 requires a matching C7/C8 posting for CREDITED; C1 case proof cannot substitute. F2 and H4 cover least privilege, privacy and retention. C4 caps cumulative cycle credit at remaining original charge, with C7 atomic cycle budget lock; monthly fixtures use October 1–November 1.
- D6: 3/4 — H1–H6 label missing operational facts as assumptions with owners and launch blockers. CTX2/C2 route conflicting and unavailable evidence to owned investigation. H5/M1 explicitly label traffic and prices illustrative; R4 states no approvals actually supplied.
- D7: 2/4 — F1 chooses transactional code workflow and rejects open-ended agent/chat chain for durable 48-hour waits and unknown-write locks. However Temporal/LangGraph are only named as things to compare; F1–F3 repeat identical generic AWS/GCP/Azure candidates without an actual comparative assessment of tools, data and permissions. IR3 remains material under D7.
- D8: 3/4 — Exactly one LLM component C3 has M1. Arithmetic independently checked: 2400*$1/1e6+450*$4/1e6=$0.0042/call; 0.9 calls/case=$0.00378; 10000 cases=$37.80. No model retry; 12-second timeout, excluded infrastructure/human cost, unmeasured peak load and held-out fine-tune gate are explicit.
- D9: 3/4 — FM1–FM9 cover wrong subject, stale authority, duplicate credit, injection/conflict, unknown commit/cancellation, missing proof, queue failure, arithmetic and notice routing. Hypothetical scales, owners, detection metrics and controls are explicit; linked concrete examples exist. Additional boundary tests required by IR1 would strengthen FM2/FM3/FM8 assurance.
- D10: 2/4 — Inspected actual canonical and eval-set fixtures: EV1 yields floor(30000*360/44640)=241; EV12 yields floor(100000*30000/44640)=67204. EV1/EV13 provide positive service-credit effects; EV2/EV3/EV14 forbid writes; EV11 positive and EV10 negative notices; EV6/EV7/EV15/EV16 correctly count only additional writes after prior submissions. Material missing fixtures: exact-cap and remaining-budget boundaries, overlapping interval union inputs, exact approved-amount mutation, multiple connections and ABSENT_FINAL retry path. EV23 names checks but supplies no concrete replacements.
- D11: 3/4 — R1 defines median/P90 resolution time, safe-resolution denominator and separate unresolved aging; baseline unknown. R2 has shadow/assist/pilot/scale and stop action preserving reconciliation. R3 defines account randomization, stratification, incident clustering, contamination control, minimum duration and power method; R4 assigns approval responsibility without claiming sign-off.
- D12: 3/4 — Read PRD.md, architecture.md, eval-set.json and build milestones 00–04 against canonical IDs. Components, workflow and selected tests remain aligned, with H1–H4/H6 launch blockers and design-only limitations explicit. Prior PASS banners reflect author review and are superseded by this independent needs-work result; business assertions remain specifications.

Review findings:

- IR1 [major, OPEN] evals/EV23: D10 lacks substantive boundary and adversarial fixtures for money/authority controls: no automatic-cap equality/overflow pair, remaining cumulative-charge budget case, overlapping outage interval union case, approved amount/currency mutation case, or ABSENT_FINAL safe retry case. EV12 only checks a far-above-cap amount; EV13/EV14 test valid and revoked authority, not command mutation. Add concrete fixtures with exact writes, amounts, tool ordering and forbidden effects before passing D10.
- IR2 [minor, OPEN] components/C1: S8.5: C1 accepts optional selection and rejects wrong/inactive selections, but does not explicitly require clarification when multiple active connections exist and none is selected. Define NEED_INFO with safe choices and zero private reads/writes; add a concrete multi-connection golden.
- IR3 [major, OPEN] framework/F1: D7 comparison is deferred rather than performed: Temporal and LangGraph are listed for a future spike, and AWS/GCP/Azure descriptions are identical generic placeholders. Provide a bounded assessment using the same durability/timer/recovery/permission/data/ownership criteria, separating unknown facts from proposed choices; a minimal custom code choice can remain recommended.
- IR5 [observation, OPEN] evals/EV1: semantic-contract.md describes actual golden input/expected as JSON objects while stage-shaped canonical EV1–EV20/eval-set store serialized JSON and semantics stores parsed object copies. The bundled validator accepts this encoding. Align documentation to clarify the parsing boundary; this is a wording ambiguity, not a structural design defect.

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

- Independent review by final_telecom_review of current telecom canonical design and actual companions; no author review, provenance or earlier cases read to derive findings.
- Scores are bounded AI design judgements, not production, regulatory, API support or measured accuracy evidence. No business control harness or live action executed.
- Bundled structural validation independently returned structural-pass and verified-declarations; it does not execute the golden assertions.
- Actual PDF pages 1–3 were rendered at 72 dpi and inspected at native pixel size. Diagram labels are readable; exact branch predicates are intentionally delegated to architecture.md.
- Design-only tooling: this helper makes no provider, network or business API calls and executes no business assertions; optional host-assistant research is outside this statement.
- Schema, reference, graph and ID-coverage checks do not establish semantic completeness, source truth, actual human authorization or production safety.
- Review scores and evidence are supplied by the reviewing agent; the helper checks their shape and declared pass conditions, not their truth.
- FMEA action/control text is required where specified; the helper does not verify ownership, release authority, regulatory compliance or risk acceptance.
