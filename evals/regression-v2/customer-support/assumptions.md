# Shop support draft desk

> NEEDS-WORK · DESIGN ONLY. Review is a design judgement; no business controls or provider reliability were executed.

Review method: independent-agent; round 1.

Review dimensions (supplied scores):

- D1: 3/4 — CTX1-CTX3 and T0-T4 bound staff-reviewed supplied-evidence work, exclusions and exception/cancellation outputs.
- D2: 3/4 — Stable task/component/workflow/eval IDs are present; independently recomputed FMEA/eval reciprocity has zero discrepancies. No external-source verification is claimed.
- D3: 2/4 — W1-W5 provide exclusive evidence paths and bounded retries, but C4 requires a local receipt before ready while C5 later creates it; no upstream receipt producer/binding is specified.
- D4: 2/4 — C3 draft schema names text/citations; C4.checked and C5.handoff do not carry that draft or a specified retrievable artifact-content contract. EV1 output payload fields lack typed producer bindings.
- D5: 3/4 — F2 excludes business write credentials; C1 checks current scope and C4 rechecks it. H3 bounds retention proposal and logs are minimized/redacted; manual review retains authority.
- D6: 3/4 — H1-H5 distinguish scope, adapter, staffing, retention, budget and target hypotheses from user brief. All fixtures are labelled synthetic and unexecuted.
- D7: 3/4 — F1 chooses simple state machine over free tool agent/multi-agent chain; F3 compares scoped read/region/retention/audit/operations/price for unverified cloud/self-hosted patterns.
- D8: 3/4 — M1 maps solely to C3/W3, max one call/no retry, 30-second deadline; 4000*1/1e6+800*4/1e6=$0.0072 and 100 cases=$0.72. Provider prices and volume explicitly illustrative.
- D9: 3/4 — FM1-FM13 have hypothetical S/O/D scales, owners and release gates; customer subject/policy/refund failures are concrete.
- D10: 2/4 — All 14 complete small golden inputs/expectations inspected. EV5/EV7/EV9/EV14 assert zero model calls yet retain ordered mockSequence with model invocation; EV1/EV17 model outputs are prose rather than exact response payloads. No harness executed.
- D11: 3/4 — R1 defines weekly active-minute denominator; R2-R5 define shadow/pilot entry/exit, owner/manual fallback, randomized source-family strata, contamination control and baseline-driven power method.
- D12: 2/4 — Iteration 6 PDF pages 6/10 now summarize actual architecture and rollout data; IA4 resolved after direct visual inspection. D12 remains 2 because companions/handoff preserve the unresolved C3-C5 content/receipt gaps in IA1/IA2.

Review findings:

- IA1 [major, OPEN] components/C4: C4 requires an artifact receipt before ready but C5 creates the local receipt after C4. Specify the exact upstream producer, persistence contract and binding (or move receipt generation before the check), including unavailable handling; keep W1/W2 exception paths coherent.
- IA2 [major, OPEN] components/C5: Successful handoffInput only carries C4.checked metadata, while checked omits the draft text/claim citations and typed domain result. C5 output also lacks review content. Preserve a fully typed reviewedArtifact payload or specify content storage/retrieval by artifactId, freshness/hash binding and domain fields from producer to terminal output. Declare category enum as an actual produced field; EV1 expects category delivery.
- IA3 [major, OPEN] evals/EV5: EV5, EV7, EV9 and EV14 expect zero/additional-zero model calls yet mockSequence contains model -> source-grounded draft and passRule says verify ordered mocks. EV1/EV17 give prose model responses rather than typed concrete candidates, so a harness must invent payloads. Separate configured responses from expected invocation traces, supply exact candidate outputs and define forbidden calls explicitly.
- IA4 [major, resolved] export/X1: Resolved by final iteration 6 reader export: actual PDF page 6 now displays F1-F3 choices/rejected alternatives/tradeoffs/access; page 10 displays R1-R5 measures, phase owners, gates and experiment summaries. Viewed actual 72 dpi pages; full source fields are present in PRD.md. Remaining contract/eval findings are unaffected.

## Proposed assumption ledger

### H1

Handle product questions, delivery questions and complaints. Staff send replies in their own support tool. Exclude refunds, order changes and automatic sending.

Why: Choose a useful bounded first release from only the brief.

Proposed owner: Shop support lead

Validation: Approve scope and exclusions in a design review before a pilot.

Launch blocker: true

### H2

Authorized staff supply source bundles and approved version manifests; proposed read-only adapter contracts are unverified.

Why: No actual service integration was supplied.

Proposed owner: Integration owner

Validation: Demonstrate scoped read and denial on wrong subject and revoked access.

Launch blocker: true

### H3

One workday response target, coordinator queue and backup owner; 30 day source retention subject to local policy.

Why: Capacity, calendar and privacy policy were not supplied.

Proposed owner: Shop support lead

Validation: Approve working calendar, retention, data location and staffing before pilot.

Launch blocker: true

### H4

Illustrative model budget: one call, 4000 input and 800 output tokens; USD 1 input and USD 4 output per million; 100 cases per month.

Why: Provider and workload unknown; an arithmetic budget is useful.

Proposed owner: Product owner

Validation: Replace with provider quote and measured token/traffic samples.

Launch blocker: false

### H5

Proposed quality target is 95% staff-useful drafts with zero critical evidence or privacy violations.

Why: No baseline or business target supplied.

Proposed owner: Shop support lead

Validation: Collect baseline and approve acceptance threshold.

Launch blocker: true


## Review and tooling limitations

- Independent agent design judgement against canonical source contracts and fixtures; no business assertions, provider, network, integration or deployment executed.
- All operational owners, policies, quality targets and adapters remain proposals or launch blockers as labelled H1-H5.
- Incidental exposure: validation.json contains an embedded author review. Major findings were formed and reported before that read; author reasoning and scripts were not used to derive scores.
- Actual final iteration 6 PDF pages 2, 3, 6 and 10 visually inspected using pdftoppm at 72 dpi/native size; other PDF pages inspected through text.
- Design-only tooling: this helper makes no provider, network or business API calls and executes no business assertions; optional host-assistant research is outside this statement.
- Schema, reference, graph and ID-coverage checks do not establish semantic completeness, source truth, actual human authorization or production safety.
- Review scores and evidence are supplied by the reviewing agent; the helper checks their shape and declared pass conditions, not their truth.
- FMEA action/control text is required where specified; the helper does not verify ownership, release authority, regulatory compliance or risk acceptance.
