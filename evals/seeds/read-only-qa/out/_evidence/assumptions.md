# Analyst research assistant for the internal report library

> PASS · DESIGN ONLY. Review is a design judgement; no business controls or provider reliability were executed.

Review method: self-review; round 1.

Review dimensions (supplied scores):

- D1: 3/4 — CTX1 states the decision and the boundary; CTX2 names the fifty analysts and Research Operations as the library owner; CTX3 gives the trigger, the in-scope corpus and four explicitly excluded actions.; CTX4 states both end conditions: an answer with a citation per claim, or a decline naming what was searched. A decline is defined as a finished case, not a failure, which is what makes the sufficiency gate meaningful.; The tree partitions the job without overlap: understand (T1), find (T2 with retrieval and sufficiency as separate leaves), answer (T3), decline (T4). Sequence and leaf modes are coherent and the tree is three levels deep.; Held at 3 rather than 4: the first release scope is stated but the design does not say what happens when the library grows a new report type, such as the client decks that are not in the 4,000 PDFs.
- D2: 3/4 — Every leaf reaches a component, a workflow node and at least one evaluation; the validator reports no broken trace and no orphan component.; The failure-mode to evaluation relation is generated from one COVERAGE table in author_design.py and read in both directions, so FM.evalIds and eval.failureModeIds cannot disagree.; Each of the six failure modes carries at least one golden, one offline or online check and the release suite EV11.; Held at 3: the trace is complete but the milestone-to-evaluation mapping repeats EV11 in all three milestones, which is correct and slightly redundant to read.
- D3: 3/4 — W1 is the only entry and the only semantic root; W8 and W9 are explicit terminals with nonempty terminal dispositions and no outgoing edges.; Every edge carries a predicate and all three decision nodes (W3, W5, W7) have mutually exclusive outcomes. The graph is acyclic, so there is no loop needing a bounded exit.; Every node states a timeout and a failure disposition, and each failure disposition returns a decline rather than a partial answer.; Held at 3: recovery is uniform by design because nothing is written, so there is no retry, reconciliation or cancellation path to specify. That is defensible here and is stated on every node, but it means the workflow has had less recovery design than a writing system would need.
- D4: 3/4 — All eight components carry typed input and output declarations; C2 names its status enum and a required errorDetail, so INDEX_UNAVAILABLE is distinguishable from an honestly empty result.; Each of the five deterministic components states a whyCode explaining why the responsibility is code rather than judgement; C5's reason, that a model checking its own citations will agree with itself, is the load-bearing one.; Abstention is a first-class contract: C6 outputs a boolean and a reason, and C7 renders either an answer or a decline through one typed outcome enum.; Held at 3: no component declares a record proof, because the design has no write to prove. The read-only case is the reason, not an omission.
- D5: 4/4 — There is no write node, no write action class and no write component. The service holds one read-only credential and F3 states the write scope is not configured rather than merely unused.; Entitlement is enforced twice by independent deterministic components: C2 filters inside the search query so a restricted passage is never retrieved, and C3 re-checks every returned passage against the directory and drops any that fails.; Every LLM output is categorised in semantics.modelOutputs, and none supplies money, a date or an identity to anything; no model output reaches an action because no action exists.; Identity comes from the corporate directory at session start (H5) and is never taken from the request or inferred by the model, which is what the second check is checking against.; Objective evidence exists for both halves: EV6 asserts the cross-team drop on a fixture and EV8 is a 60-case adversarial entitlement set with a zero tolerance.
- D6: 4/4 — Six H assumptions carry a why, a named owner role, the evidence that would confirm them and a launch-blocker flag; H1, H2 and H5 block launch and the handoff repeats that.; No vendor fact is asserted: research.performed is false with the reason, and every one of the nine tool candidates is verified:false with a note saying it is a name to check rather than a recommendation.; The volume is labelled illustrative (H4) and the twenty-minute baseline is labelled as taken from the brief and not yet measured (H6); R1's gate requires measuring it before the shadow phase, so no target is claimed against an unmeasured baseline.; CTX6 collects the unverified inputs in one place rather than leaving the reader to assemble them from the ledger.
- D7: 3/4 — F1 states plainly that most of the value is better search rather than the model, and rejects both a plain search box and a fine-tuned model, with the reason fine-tuning is rejected outright: it makes citation impossible and staleness invisible.; F2 chooses a fixed four-stage pipeline over a single model call and over a free agent loop, and gives the reason each is rejected rather than asserting the choice.; No orchestration framework is proposed, which the rubric permits for a simple deterministic system; F2 says a plain service is enough and names the cloud options per provider.; Held at 3: the cloud rows name plausible services per provider but none is checked, so the stack cards are a starting point for a build decision rather than a decision.
- D8: 3/4 — Exactly two model plans for exactly two LLM components, each with a bounded role, a tier rationale and a named rejected tier with the reason.; M2's rejected-tier reasoning is specific rather than generic: a small tier merged claims across passages, which the citation check then rejected, raising the failure rate rather than lowering cost.; Calls, tokens and prices are explicitly illustrative, and the design states that hosting, the index, extraction and analyst time are excluded from the per-case figure.; Held at 3: the token counts are estimates from the passage budget rather than measurements, and no price is bound to a dated quote.
- D9: 3/4 — All six read-only failure families are present with concrete causes tied to real component IDs: superseded source (FM1), uncited claim (FM2), answer from outside the corpus (FM3), prompt injection carried in a report (FM4), out-of-entitlement leak (FM5) and a confident answer when the corpus is silent (FM6).; The write-shaped families are justified as inapplicable in the fmea stage assumptions rather than silently absent: there is no write to duplicate, leave uncertain or falsely confirm, and no queue for work to age in.; Every failure scoring severity 8 or above, or RPN 150 or above, names an owner role and an objective release gate in its action; FM5's gate stops the service on a single live occurrence.; acceptedRisk is false throughout; no user acceptance is claimed.; Held at 3: occurrence scores are the author's estimates with no incident history behind them, which the S/O/D note says explicitly.
- D10: 3/4 — Six goldens carry concrete JSON fixtures with real passage IDs, report IDs and page numbers, and mechanically checkable pass rules; EV4 is an exact mutation of EV1 that changes one passage ID to one that was never retrieved.; The read-only pair SEM008 requires is present and checked: EV1 answers with two citations and EV2 declines with zero, each naming C2 as a read source and citationList as the asserted field.; Both high-risk leaves have substantive goldens: T2.1 through EV6 and T3 through EV1 and EV4. Every unaccepted failure mode has at least one golden.; Offline layers state their strata, size and labelling; online checks state cadence, threshold and a response owner; EV11 requires a new golden to be added to the release suite in the same change that adds it.; Held at 3: these are specifications. Nothing here has been executed, which every testSet field says.
- D11: 3/4 — R1 and R2 both state their definition and their baseline status honestly: R1's baseline is the brief's twenty minutes, marked unmeasured, and R2 has no baseline because no system exists today, so it is collected in the first shadow week.; R3 and R4 state entry and exit evidence that does not require the results of the phase being gated; shadow exists to collect the baselines that the pilot comparison later needs.; Each gate names an accountable role, and R6 collects all four owners against what they own.; R5 tests a genuine open question rather than a foregone one, and its hedged arm still carries a citation per claim, so the experiment cannot be read as permission to answer without evidence.; Held at 3: the acceptance targets of 85 and 70 per cent are chosen by the author, not derived from anything measured.
- D12: 3/4 — X1's six acceptance criteria each name the evaluation that proves them, and the last one is about configuration rather than code: the write scope is not configured, not merely unused.; The three milestones cover all eight components and every evaluation linked to them, and each carries acceptance criteria drawn from the stage decisions rather than restating the brief.; The build instructions add no capability: they name the four stages, repeat which assumptions block launch, and list three things not to add, each of which this design does not authorise.; Held at 3: the handoff does not specify the index schema or the re-indexing trigger beyond F4's description, so the builder has one real design decision left to make.

Review findings:

- IR1 [major, resolved] components/C2: The retriever declared its passages and count but no response status, so an index timeout and an honestly empty library were indistinguishable to every downstream component. A silent library is the input to the sufficiency gate, so this could have turned an outage into a confident decline. Resolved in this round: C2 now declares a status enum of OK, NO_MATCH, INDEX_UNAVAILABLE and ENTITLEMENT_UNRESOLVED with a required errorDetail, and W2's failure disposition returns a decline that says the library could not be searched.
- IR2 [major, resolved] fmea/FM1: The register covered the six read-only families but said nothing about the write-shaped families the rubric asks for, leaving a reader unable to tell whether they were considered and dismissed or simply forgotten. Resolved in this round: the fmea stage assumptions justify duplicate and concurrent write, uncertain commit, false completion and human queue failure as inapplicable with the reason, and state where tool timeout is handled instead.
- IR3 [minor, OPEN] models/M1: Token counts are derived from the passage budget rather than measured against a real corpus, so the per-case cost is an order-of-magnitude estimate. Not resolved: it cannot be resolved before the index exists. Recorded so the cost figure is not read as a quote.
- IR4 [minor, OPEN] rollout/R2: The 85 per cent acceptance target is the author's judgement, not a figure derived from a comparable system. Not resolved: it should be revisited once the shadow phase produces a first distribution. Recorded so the gate is not read as externally grounded.

## Proposed assumption ledger

### H1

The report library exposes a read-only search index with per-report entitlement metadata, so the retriever can filter by what the asking analyst may see before any passage is read.

Why: Every control in this design rests on filtering at retrieval rather than after drafting.

Proposed owner: Head of Research Operations

Validation: Confirm the index exposes entitlement fields and that they are maintained with the report.

Launch blocker: true

### H2

Each report carries a version and a superseded-by field, so a superseded edition can be marked rather than quoted as current.

Why: Quoting a withdrawn report as current is the failure analysts said would cost the most trust.

Proposed owner: Head of Research Operations

Validation: Sample fifty reports and check both fields are present and correct.

Launch blocker: true

### H3

Page numbers in the extracted text match the page numbers an analyst sees when opening the PDF, including for reports scanned from print.

Why: A citation an analyst cannot follow to the right page is not a citation.

Proposed owner: Data Platform Lead

Validation: Spot-check 100 citations across born-digital and scanned reports.

Launch blocker: false

### H4

An illustrative first-release volume of 3,000 questions a month, about 150 a working day, with a peak of three times the mean in the week after a major report lands.

Why: Volume drives the model budget and the size of the review sample.

Proposed owner: Head of Research Operations

Validation: Measure actual question volume during the shadow phase.

Launch blocker: false

### H5

Analyst identity and team membership come from the corporate directory at session start and are not supplied by the analyst or inferred by the model.

Why: Entitlement filtering is only as trustworthy as the identity it filters on.

Proposed owner: IT Security

Validation: Confirm the directory integration and that no identity field is user-editable.

Launch blocker: true

### H6

A baseline of about twenty minutes to find a cited answer by hand, taken from the brief and not yet measured.

Why: The headline KPI compares against it, so it must be measured before any claim is made.

Proposed owner: Head of Research Operations

Validation: Time twenty real questions before the shadow phase starts.

Launch blocker: false

- context: COV15: no web search tool was offered, so every tool candidate on the stack cards is unverified rather than checked against a cited source.
- context/CTX4: H6
- context/CTX5: H1
- context/CTX5: H5
- context/CTX6: H1
- context/CTX6: H2
- context/CTX6: H3
- context/CTX6: H6
- tasks/T0: H4
- tasks/T2.1: H1
- tasks/T2.1: H5
- tasks/A1: H5
- tasks/A2: H1
- tasks/A3: H2
- tasks/A3: H3
- components/C2: H1
- components/C2: H5
- components/C3: H1
- components/C5: H2
- workflow/W2: H1
- workflow/W3: H1
- workflow/W3: H5
- workflow/W7: H2
- framework/F3: H1
- framework/F3: H5
- framework/F6: H2
- framework/F6: H3
- models/M1: H4
- models/M2: H4
- fmea: Duplicate or concurrent write, uncertain commit and false completion are inapplicable: this design has no write node, no write action class and a read-only credential with no write scope configured, so there is no effect to duplicate, leave uncertain or falsely confirm.
- fmea: Human queue and SLA failure are inapplicable: no step waits for a person. A case that cannot be answered declines immediately rather than queueing, so no work can age in a queue.
- fmea: Tool timeout is covered by contract rather than by a register entry: every node states a timeout and a failureDisposition that returns a decline, and an index timeout is an explicit INDEX_UNAVAILABLE status on C2 rather than an empty result that reads as a silent library.
- fmea/FM1: H2
- fmea/FM5: H1
- fmea/FM5: H5
- evals/EV3: H2
- evals/EV6: H1
- evals/EV6: H5
- evals/EV9: H4
- evals/EV10: H4
- rollout/R1: H6
- rollout/R3: H6
- rollout/R4: H4
- export/X1: H1
- export/X1: H2
- export/X1: H5

## What the user added

No intake question was asked: No question dialog was available in this authoring session; the brief was taken as given..

- Q1 Which system holds the reports, and does it expose a search index with entitlement metadata? — unavailable
- Q2 Is the twenty-minute hand-search baseline measured or estimated? — unavailable

## Research used

No web research was performed: No web search tool was offered to the authoring session, so no search tool was used and no finding is recorded. Every tool named in the stack cards is an unverified candidate to check, not a recommendation. Tool candidates are unverified.

## Review and tooling limitations

- This is a self-review: the same agent authored the design and scored it against the rubric. No separate reviewing agent was available in this session, so no second party checked these scores, and they should carry less weight than the ones on the telecom and health-claims examples.
- Nothing here was executed. Every golden, offline set and online check is a specification; no fixture has been run against a built system, and no retrieval index, model or report corpus exists.
- Every fact about the report library is an unverified assumption, including that the index exposes entitlement metadata (H1), that reports carry a superseded-by field (H2) and that extracted page numbers match the printed page (H3). The design does not work if any of the three is false.
- No web research was performed, so all nine tool candidates are unchecked names rather than recommendations, and no claim here rests on a current vendor capability.
- The S/O/D scores are the author's estimates to prioritise review. They are not measured probabilities and there is no incident history behind them.
- The design was not reviewed by anyone at the organisation in the brief. Entitlement rules, the restricted-client policy and the twenty-minute baseline are all taken from the brief's wording rather than confirmed with an owner.
- Design-only tooling: this helper makes no provider, network or business API calls and executes no business assertions; optional host-assistant research is outside this statement.
- Schema, reference, graph and ID-coverage checks do not establish semantic completeness, source truth, actual human authorization or production safety.
- Review scores and evidence are supplied by the reviewing agent; the helper checks their shape and declared pass conditions, not their truth.
- FMEA action/control text is required where specified; the helper does not verify ownership, release authority, regulatory compliance or risk acceptance.
