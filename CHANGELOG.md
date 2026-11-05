# Changelog

## 1.3.0 — unreleased review candidate (5 November 2026)

A stress harness (`evals/stress/mutate.py`, fifteen mutations of the telecom
example plus seven edge briefs) found the cases where 1.2.0 failed, fitted
badly or said something wrong. This release fixes them. No validator rule,
rubric threshold or seeded defect was weakened, and the "code owns money,
identity, dates and limits" rule is untouched. Decisions are recorded in
`docs/decisions.md`, one section per fix.

- **The brief is classified before it is designed from.**
  `scripts/design_intake.py classify` runs before `questions` and writes a
  `briefProfile` into `intake`: the language by Unicode block and then by
  distinctive function words; whether the brief is too short or vague, or over
  6,000 words; whether it describes an agent system at all; whether it writes
  to a system of record; whether it is real-time or voice; whether it is
  multi-tenant; and whether it asks the design to drop a control the skill
  keeps. Every signal carries a plain-language message, the host confirms the
  profile in one line and may override it, and both are recorded. A recorded
  `briefConflicts` entry must be answered on the Context card "Trigger and
  first-release scope" and on the Decision brief, or validation fails: the
  design never silently redesigns around the brief. `evals/briefs/edge/` holds
  the seven briefs with their expected profiles.
- **Non-Latin text renders as text.** The skill ships Noto Sans, Noto Sans
  Bold, Noto Sans Mono, Noto Sans Devanagari and Noto Sans Arabic (SIL Open
  Font License) under `skills/agent-design-studio/fonts/`, and both PDF
  renderers pick a font per character. Devanagari and Arabic used to come out
  as black squares. A character no registered font can draw is written as `?`
  and adds one warning line to `validation.json` naming the code points and
  the font to drop into `fonts/`; a silent box is never acceptable.
- **The derived reader layer is readable.** `report_v2.derive_presentation()`
  builds the Decision brief for a design with no `presentation` block. Design
  calls come whole from the framework cards that record a decision
  (`architecture`, `orchestration`, `permission`) instead of being cut
  mid-sentence; autonomy rows are action classes derived from the workflow
  graph and `semantics.writeActions` instead of one row per component (six
  rows for telecom, not eighteen); an owner is labelled "(proposed)" once; a
  KPI with no target says "see definition" instead of drawing an arrow from a
  baseline it does not have; and the title is printed once.
- **A long brief no longer breaks the standard export.**
  `build/00-overview.md` quotes at most the first 2 KB of the brief and points
  at `design.json`, so a 60 KB brief exports. The size error names each
  oversize file with its byte count and the field that dominates it, instead
  of advising a milestone split that could not have helped. Nothing is hidden
  to fit a limit: the HTML collapses a long brief behind a "show full brief"
  control with the whole text still in the page, and the full PDF carries it
  as appendix D.
- **The flow is routed, not drawn with long curves.** Edges are orthogonal
  with one gutter per source: out of the node sideways into its own lane, down
  that lane, across a corridor between node rows when the span crosses several
  columns, and into the target from the left. Condition plates are anchored at
  the target end and slid along that line until they touch no other plate and
  no node. Over six exits from one node become a numbered legend under the
  node, with the number on the edge and the full text still in the node detail
  table. A cross-band edge says "continues at" at both ends. Measured over
  both seeds and six stress variants: 0 of 43 plates overlap a plate or a
  node, and every node is inside the viewBox. This removes the two collisions
  recorded under 1.2.0's known limits.
- **Three brief profiles change what a design must contain.** With
  `briefProfile.writes = false` the ten stages stay, but COV17 names the
  read-only risk families a register is missing (stale source, missing
  citation, answer outside the corpus, prompt injection through documents,
  leaking content the reader may not see, confident answer when the corpus is
  silent), the money-trigger check becomes "n/a" with its reason, COV16
  requires a citation golden, a refusal golden and a statement of who may see
  which documents, the new **SEM008** checks answer goldens the way SEM003
  checks writes, and the authority table reads "answers with citation",
  "answers with caveat", "declines". With `realtime = true` nodes may carry
  `latencyBudgetMs` and `streaming` (both optional, so every earlier design
  stays valid), a node the design says speaks must have a barge-in branch, a
  speech component must output a confidence value, and a path over the brief's
  stated reply target warns. With `multiTenant = true` the new **SEM009**
  fails a read or write component whose inputs name a record ID with no tenant
  in scope, and an identity binding with no tenant or with a tenant the model
  supplied; the key attributes grid puts the tenant rows first. A design with
  no `briefProfile` keeps the 1.2.0 rules exactly, which is covered by a test.
- **A degraded run looks degraded.** `run-report.json` records
  `hostCapabilities` and a `runConditions` line — "Review: self-review (no
  separate agent available). Research: none (no web tool). PDF: skipped.
  Visual QA: not run. Intake: skipped (no question dialog)." — and it appears
  on the HTML status bar of every view and on page 1 of the PDF. A self-review
  that calls itself independent in its method, limitations or issues now fails
  validation.
- **The skill's own examples meet the bar it sets.** Both seeds pass
  `validate --strict-coverage`. They carry a research record stating that no
  search tool was offered when they were authored, so every tool name in them
  is an unverified candidate; health-claims justifies COV4 and COV6 where its
  success measures and evidence limits actually live. `--strict-coverage` is
  now part of the seed tests, so they cannot drift back.
- **`scripts/design_scaffold.py` drafts the schema 1.1 semantic contract.**
  From a filled tasks and components stage it writes every node, component
  effect, transition and model-output row, and the field names each write
  binding needs. It never invents a transition outcome, an output category, a
  binding source, an action class, a wait duration or a golden, and returns a
  checklist. Blanks are `"TODO"` and fail validation with a message that names
  the scaffold rather than "malformed semantic row". SEM000 is where weaker
  and smaller-context models burn rounds; this is the bookkeeping, not the
  design.
- **The task-depth rejection names its limit**: "Task depth 4 exceeds the
  limit of 3 levels (overall job -> task -> subtask)."
- **Tests: 270 pass**, up from 132. New files: `test_brief_classifier.py`,
  `test_pdf_unicode.py`, `test_long_brief.py`, `test_flow_layout.py` (which
  reads the rendered SVG and checks the geometry itself),
  `test_brief_profiles.py`, `test_host_capabilities.py`,
  `test_design_scaffold.py` and `test_stress.py`, which pins an expected
  outcome and a reason for all fifteen mutations and fails on a mutation with
  no recorded outcome. `scripts/score_run.py` gains S14 (classifier accuracy
  on the seven edge briefs: 7 of 7) and S15 (a seed design per brief profile).
  Measurements are in `evals/v1.3-scorecard.md`.

### What it still cannot do

- **The three profile seed designs do not exist, so S15 fails.** The existing
  seeds are 400 to 575 KB with 86 items, full semantic contracts, 23 goldens
  and an independent review. Producing three more to that standard means
  running the skill end to end three times, which is authoring work rather
  than a code fix. The scorecard reports which folder each is missing from
  rather than passing on nothing. The rules those seeds would exercise are
  covered by `tests/test_brief_profiles.py`, which builds satisfiable
  read-only and multi-tenant variants and proves both the failing and the
  passing side of every new rule.
- **S13's visual grade is stale and was not re-run.** Fix 5 rewrote the SVG
  router, so the HTML the independent grader scored no longer exists.
  Re-running it needs that separate agent plus Node, Playwright and a
  launchable Chromium, none of which this host had. The 1.2.0 captures are
  kept under `evals/html-qa/2026-11-04/`. The geometry the grader marked down
  is now checked mechanically, which is a narrower thing than a visual grade.
- **The v1.2 example scorecards no longer bind.** S9, S10 and S12 bind sha256
  hashes to `design.json`, which Fix 10 changed. The checks did not change;
  their evidence needs rebinding by a fresh pipeline run, and rebinding by
  hand would assert evidence this session did not produce. The committed
  `scorecard.json` files are the historical record of the 1.2 run, not a
  current score.
- **Arabic is rendered but not shaped.** ReportLab has no OpenType shaping
  engine, so Arabic letters draw in isolated rather than joined forms, and it
  reverses a right-to-left run so the text layer holds the word in visual
  order. Every character survives and nothing is a box, which was the fix;
  joined Arabic needs a shaping dependency the skill does not have.
- **Noto Sans CJK is not shipped.** At about 16 MB it is more than this
  repository should carry for a script no example uses, so Chinese, Japanese,
  Korean and emoji render as `?` with the warning line. Dropping
  `NotoSansCJK-Regular.ttf` into `skills/agent-design-studio/fonts/` switches
  it on with no code change.
- **A long edge still crosses columns.** It travels in a corridor between node
  rows rather than through a node, but on a very wide span it passes under
  several columns. The node detail table is the readable fallback.
- **The brief classifier is a keyword and script heuristic.** A Latin-script
  brief with no recognised function words is called English with low
  confidence; on a non-English brief the write, real-time and multi-tenant
  signals are marked unreliable rather than suppressed, and the host is told
  to re-run them on a translation. The host confirms the profile, and nothing
  downstream treats it as fact.
- **Two consecutive all-target passes are still not established**, and were
  not in 1.1 or 1.2 either. S11 stays unmeasured: this host does not report
  total inference usage, and artifact size is not inference usage.
- The known limits of 1.2.0 and 1.1.0 below still apply, except the two flow
  plate collisions and the derived-brief truncation, which are fixed.

## 1.2.0 — unreleased review candidate (4 November 2026)

- `DESIGN.html` is a default deliverable. `design_io.py export` writes it in every mode (lite: Decision brief, Task map, Flow, Risks; standard and full: all twelve views) and `--no-html` skips it only for hosts that cannot write it. The opt-in question is gone from SKILL.md, the personas, the references, the build files and the PDF.
- `design_html.py` was rewritten to the HTML design spec (`docs/html-design-spec.md`, references in `evals/target/`): Decision brief from `presentation`; CSS task tree with leaf cards, detail panel and key-attribute grid; inline SVG flow with layered layout, condition plates, handoff and uncertain-exit notes, task filter, node detail and coverage table; interpretation inventory and grouped component cards; stack cards; model table and cost calculator; risk heat table, act-now rule and expandable register; test coverage, golden cards and monitoring table; KPI cards and phases; handoff file list and milestones; assumption and review tables; chevron rail and read-only status bar. Standard library only, no network asset, no design data in script, nothing truncated.
- One table of step names, groups and captions (`report_v2.STEPS`) now drives the HTML navigation and the PDF section headings ("3. Building blocks" with the group as a running line). Stage keys are unchanged.
- Standard and full exports write `README.md` and keep `PRD.md`, `architecture.md`, `eval-set.json`, `fmea-register.csv` and `assumptions.md` under `_evidence/`; build files link there. `validation.json` tracks every generated file, including `DESIGN.html`, so re-export replaces only unchanged generated files.
- `scripts/score_run.py` adds S13: `DESIGN.html` present, renders in every mode without a renderer refusal, and an independent visual grade of at least 3 for every view bound to the hashes of `design.json` and `DESIGN.html` (`html-grader.json`). The v1.2 prompt called this S23; the repository scorer has S1–S12, so the new target is S13.
- `scripts/html_qa.js` (Playwright) screenshots every view at 1440 px and 400 px offline and fails on console errors, external requests or page-level horizontal scroll. Captures, reference captures and the grader report are in `evals/html-qa/2026-11-04/`. The independent grader scored 26 of 26 views at 3 or above for the telecom and health-claims examples (Flow at 3 on both, every other view 4); the scorecards there show S1–S10, S12 and S13 passing, with S11 still unmeasured.
- Research and tools. The skill now runs a bounded web-research pass when the host offers search: the industry and use case first, then current options for each capability the brief needs, starting from the new `references/tool-catalog.md` (voice and telephony, speech, guardrails and PII, web search, embeddings and reranking, vector stores, knowledge graphs, document AI, orchestration, LLM gateways, observability, channels, identity, human review). Findings are recorded in a top-level `research` object with URL, title and retrieval date and cited through a new `research` source type; a `tooling` framework card per capability lists candidates with their verification status. The validator checks citation consistency and that a `verified` candidate cites a finding; the HTML shows a Research used table and a Tools by capability table; `_evidence/assumptions.md` and the full PDF list the findings. Without a web tool the record says so and every candidate stays unverified. Examples predate these fields and are unchanged.
- Intake. `scripts/design_intake.py questions` reads the brief, lists the key information it leaves out and shapes at most four optional questions with options; SKILL.md tells the host to ask them once through its question dialog (`AskUserQuestion` in Claude Code, `request_user_input` in Codex, a single message elsewhere), never to block, and to record the exchange in a new `intake` object. A user answer is citable as a `user-intake` context source; a skipped question becomes an assumption. The HTML Brief and scope view and `assumptions.md` show what the user added.
- Expected-information coverage. `design_io.py validate --strict-coverage` and `design_io.py coverage` report fifteen COV checks (context cards for decision, actors, scope, measures, constraints and evidence limits; reader layer; milestones; research record; a tooling card per capability the brief implies; a human trigger where the brief implies money writes; recommended volume, KPI baselines, two examples per leaf, checked tool candidates). Required gaps are warnings in `validate`, fail the strict flag, and can be justified with an assumption string starting with the check ID. The export README lists the result. Coverage looks for expected information; it does not judge quality.
- Install. `scripts/install_skill.sh` copies the skill into the skills folder of Claude Code, Codex, GitHub Copilot, Cursor, Gemini CLI, OpenCode or any `--dir`, backing up a previous copy; `.claude-plugin/plugin.json` and `marketplace.json` let Claude Code load the repository as a plugin. README lists the folders and commands.
- Tests: 113 pass (test_design_html.py rewritten; test_design_html_v2.py added for both seed designs, synthetic long and fan-out graphs and the export integration). No validator rule, rubric threshold or seeded defect was changed.
- Example folders gained a rendered `DESIGN.html`; their historical flat companion layout and their PDFs are unchanged, so the example PDFs still carry the 1.1 section titles. Their `grader.json` hashes bind to those PDFs, which is why they were not re-rendered.

### What the HTML still cannot do

- It is a view, not a session: no editing, approval, ticking items out of scope, regenerate or upload. Nothing a reader does changes `design.json`, and only the last opened view is remembered in the browser.
- The task tree is a CSS grid like the reference, not SVG; only the flow is SVG. Flows over 16 layers continue in a second band with "continues at" notes rather than a single picture.
- Edge conditions are shown verbatim on plates; long predicates wrap to several lines and can crowd a dense gap. The node's detail table is the readable fallback.
- Edge-condition plates of edges that span several columns can land on another edge's plate (seen at two positions in the health-claims flow); the node detail table lists every condition in full.
- The flow is laid out automatically in layers and scrolls inside its panel; a long chain with a few multi-row layers leaves empty space in the panel and puts later nodes behind the in-panel scroll, where a hand-placed reference fits its branches in view. The task filter and node detail do not need the whole picture on screen.
- Lane captions, handoff and exit notes, high-risk reasons and the per-month volume are derived from the design's edges, effects and text, not authored; a design can override only task and node names through `presentation`.
- The cost calculator multiplies the per-case model budget by a volume; it prices no hosting, tools, retrieval or staff time.
- Visual grading is a separate agent's structure judgement from screenshots against hand-made reference pages that use different content and manual positions. It is not accessibility certification, user testing or proof that every interaction works in every browser.
- The browser check needs Node, Playwright and a launchable Chromium; without them the page is checked by parsing only.
- Host skill folders in the install script follow each tool's documentation as of November 2026 and were not exercised against every tool from this environment; `--dir` covers any other location.
- Intake and coverage are keyword heuristics: a brief that states a fact in unusual words may still be asked about it, and a design can satisfy a COV check with thin content. The review rubric, not the coverage check, judges quality.
- Research is only as good as the host's search tool and the author's summaries; the validator checks that citations match recorded findings, not that a page says what the summary claims, and the tool catalog is a list of names to verify, not an endorsement.
- The legacy Python export API (`export_design` with no mode) still writes the v1 flat layout without HTML.
- The known limits of 1.1.0 below still apply, including unmeasured total host token usage.

## 1.1.0 — unreleased review candidate (28 October 2026)

- Added lite/standard/full PDF modes; standard is now the default.
- Put a plain-language decision brief first; moved review scores to the back.
- Rendered vector task/workflow diagrams, a risk heat table and evaluation matrix.
- Split build context into bounded milestones and removed stale, unchanged generated files on re-export.
- Added explicit semantic declarations and seven rule families, with stronger writer-linked assertions and trusted record-input guards after independent code review.
- Added opt-in task/component checkpoints, dependency invalidation, run reports and S1–S12 scoring.
- Preserved failed reviews, historical seeds and unmeasured token usage; added independently reviewed synthetic designs and fresh repeat evaluations.

### Known limits

- Total host inference usage is unavailable in this environment. S11 token savings is unmeasured and must not pass on artifact size alone.
- Four additional support/AP/research/onboarding drafts remain explicitly `needs-work` after independent review (handoff content/receipt contracts and incomplete fixtures). Their reviews are preserved; only the telecom and health examples reached an independent pass.
- The fresh-repeat runs surfaced real domain/fixture regressions. Final feedback-repaired examples are not an untouched transfer benchmark. Two consecutive all-target passes have not been established.
- Fresh authors were run for the baseline and iterations01/03; not every intermediate code change received two fresh author sessions. Other iterations are explicitly recorded repairs, reviews or rerenders.
- Civic and CSV worked designs retain legacy schema1.0; their semantic coverage is unverified rather than falsely upgraded.
- Current automatic diagram layout explicitly stops above its readable node/capacity limits; larger graphs require a layout extension or embedded SVG before delivery.
- Semantic checks verify declared contracts and graph paths; they do not execute business assertions, verify external policy truth or certify runtime safety. Typed source labels can still be false; a reviewer must inspect evidence.
- No release tag, publication or push is part of this change. The original public v1 release remains unchanged until review.
