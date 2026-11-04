# Changelog

## 1.2.0 — unreleased review candidate (4 November 2026)

- `DESIGN.html` is a default deliverable. `design_io.py export` writes it in every mode (lite: Decision brief, Task map, Flow, Risks; standard and full: all twelve views) and `--no-html` skips it only for hosts that cannot write it. The opt-in question is gone from SKILL.md, the personas, the references, the build files and the PDF.
- `design_html.py` was rewritten to the HTML design spec (`docs/html-design-spec.md`, references in `evals/target/`): Decision brief from `presentation`; CSS task tree with leaf cards, detail panel and key-attribute grid; inline SVG flow with layered layout, condition plates, handoff and uncertain-exit notes, task filter, node detail and coverage table; interpretation inventory and grouped component cards; stack cards; model table and cost calculator; risk heat table, act-now rule and expandable register; test coverage, golden cards and monitoring table; KPI cards and phases; handoff file list and milestones; assumption and review tables; chevron rail and read-only status bar. Standard library only, no network asset, no design data in script, nothing truncated.
- One table of step names, groups and captions (`report_v2.STEPS`) now drives the HTML navigation and the PDF section headings ("3. Building blocks" with the group as a running line). Stage keys are unchanged.
- Standard and full exports write `README.md` and keep `PRD.md`, `architecture.md`, `eval-set.json`, `fmea-register.csv` and `assumptions.md` under `_evidence/`; build files link there. `validation.json` tracks every generated file, including `DESIGN.html`, so re-export replaces only unchanged generated files.
- `scripts/score_run.py` adds S13: `DESIGN.html` present, renders in every mode without a renderer refusal, and an independent visual grade of at least 3 for every view bound to the hashes of `design.json` and `DESIGN.html` (`html-grader.json`). The v1.2 prompt called this S23; the repository scorer has S1–S12, so the new target is S13.
- `scripts/html_qa.js` (Playwright) screenshots every view at 1440 px and 400 px offline and fails on console errors, external requests or page-level horizontal scroll. Captures, reference captures and the grader report are in `evals/html-qa/2026-11-04/`. The independent grader scored 26 of 26 views at 3 or above for the telecom and health-claims examples (Flow at 3 on both, every other view 4); the scorecards there show S1–S10, S12 and S13 passing, with S11 still unmeasured.
- Research and tools. The skill now runs a bounded web-research pass when the host offers search: the industry and use case first, then current options for each capability the brief needs, starting from the new `references/tool-catalog.md` (voice and telephony, speech, guardrails and PII, web search, embeddings and reranking, vector stores, knowledge graphs, document AI, orchestration, LLM gateways, observability, channels, identity, human review). Findings are recorded in a top-level `research` object with URL, title and retrieval date and cited through a new `research` source type; a `tooling` framework card per capability lists candidates with their verification status. The validator checks citation consistency and that a `verified` candidate cites a finding; the HTML shows a Research used table and a Tools by capability table; `_evidence/assumptions.md` and the full PDF list the findings. Without a web tool the record says so and every candidate stays unverified. Examples predate these fields and are unchanged.
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
