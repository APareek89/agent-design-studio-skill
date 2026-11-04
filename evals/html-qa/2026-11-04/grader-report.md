# HTML visual grader report, 2026-11-04

Grader: independent agent `html-visual-grader-2026-11-04`. Inputs: rendered captures in `evals/html-qa/2026-11-04/telecom` and `evals/html-qa/2026-11-04/health-claims` (13 views at 1440 px and 400 px each), reference captures in `evals/html-qa/2026-11-04/reference/telecom-target` (13 views) and `reference/claim-adjudication` (10 views). Rubric from `docs/html-design-spec.md`: 4 same blocks, order and interactions; 3 same blocks and order with minor spacing or label differences; 2 a block missing or out of order; 1 a table where a diagram or cards are required; 0 view missing. Pass threshold 3 per view. Scores and per-view evidence are in `examples/telecom/html-grader.json` and `examples/health-claims/html-grader.json`.

Mapping: rendered `rollout` was compared with reference `measure`. Health-claims used the claim-adjudication reference for context through export and the telecom-target reference for brief, assumptions and review. Reference approval, regenerate, upload and checkbox controls were ignored because the rendered page is read-only by rule.

## Scores

| View | Telecom score | Health-claims score |
| --- | --- | --- |
| Decision brief (`brief`) | 4 | 4 |
| Brief and scope (`context`) | 4 | 4 |
| Task map (`tasks`) | 4 | 4 |
| Building blocks (`components`) | 4 | 4 |
| Flow (`workflow`) | 3 | 3 |
| Stack and permissions (`framework`) | 4 | 4 |
| Models and cost (`models`) | 4 | 4 |
| Risks (`fmea`) | 4 | 4 |
| Tests (`evals`) | 4 | 4 |
| Measure and roll out (`rollout`) | 4 | 4 |
| Handoff (`export`) | 4 | 4 |
| Assumptions (`assumptions`) | 4 | 4 |
| Review (`review`) | 4 | 4 |

Result: 26 of 26 view scores are at or above the pass threshold of 3. No view scored below 3.

## Views scoring 3 (nothing below 3)

- Telecom `workflow` (3): all required blocks are present in order (filter bar, legend, SVG, detail panel, coverage table) and the interactions are visible, but the nodes carry no muted one-line example under the title, and the diagram is a single horizontal row filling only the top third of its panel, with a large empty dotted area below and W4 onward hidden behind an in-panel scroll where the reference's branching layout fits in view.
- Health-claims `workflow` (3): same block set, order and interactions; the diagram again occupies the top third of its panel with empty space beneath and needs in-panel scrolling past W4, and the W2 handoff note wraps mid-word (`unavai` / `lable`).

## Differences from the references that did not cost points

- Both renders add the chevron step rail, a `READ THIS FIRST` / `STEP n` caption line, a sticky status chip (`DESIGN ONLY . PASS`) and a footer sentence; none displaces a required block.
- Decision brief KPI block shows one KPI with `see definition` instead of the reference's four `baseline -> target` lines, because neither design's KPI text states a baseline or target (permitted by the spec).
- Brief and scope rows show one line of design reading; the telecom reference adds a muted second line per row that the data does not carry.
- Task map leaves show one example bullet (data has one) where the reference shows two; health-claims' seven top-level leaf tasks overflow the tree panel to the right exactly as the reference tree does.
- Building blocks: the interpretation inventory has one row (one LLM component per design); code cards show the `Why code` callout in place of a separate description when the two texts coincide, and the C3 agent card repeats its description as the Authority line (data duplication). Health-claims C4 carries a multi-thousand-character why-code text that makes its row very tall; nothing is truncated.
- Risks heat table only draws the severity and occurrence values present; for health-claims every cell is red because all eight risks have S >= 8.
- Tests golden cards all carry FM chips (no `positive` chip appears because no positive control exists in the data); each adds the spec's collapsible `Fixture and expected result` that the telecom reference omits.
- Measure and roll out: health-claims has a single phase panel (`Shadow then assist`) because the design defines one phase; KPI cards have no `baseline -> target` for the same reason as the brief.
- Handoff adds `DESIGN.html` in the file list and a collapsed `Build instructions` row, both required by the spec but absent from the telecom reference; the claim reference's download cards were not expected on a read-only page.
- Assumptions: no stage or item notes block appears; `design.json` contains no notes for either design.
- Health-claims brief design calls print a double full stop (`Automatic settlement.. Payment authority is unknown.`) because the rejected option already ends in a period; a copy nit, not a block or label change.

## Narrow-screen (400 px) observations

- All 26 captures stack to one column: the left step list becomes a horizontal strip that wraps to two rows, the chevron rail is hidden, the brief's right column, the cost calculator, the rollout phase panels, the experiment/owner boxes and every card grid stack vertically, and the status bar stacks its button under the text. `qa.json` reports `pageScrollWidth` 400 and no horizontal page scroll for every view of both designs.
- Containers that scroll inside themselves are clipped at the panel edge in the capture rather than cut off the page: the task tree (only T1 and part of T2 visible), the flow diagram (only W1 and the first edge visible), and wide tables (key attributes, models, risk register with the RPN pill half visible, assumptions, review dimensions and issues, the eval layer table, the flow detail's Next steps table).
- Two views are hard to read at this width without scrolling the table: Review, where the Evidence column is entirely off-screen so each dimension row is a tall near-empty band, and Assumptions, where the statement column is squeezed to two or three words per line. Nothing is truncated with an ellipsis, and no text overlaps.

## Limits of this grading

- Interactions (clickable task leaves and flow nodes, the task filter bar, expandable risk rows, collapsible inputs/outputs, fixtures and build instructions, the editable volume field) were judged from the controls and populated detail panels visible in the captures; nothing was clicked, so hover, focus, keyboard activation and dimming behaviour were not verified.
- Full-page JPEG captures show only the default state of each view (first leaf, first node, no filter, no expanded row), so the content of a second node's detail, an expanded FMEA strip or an opened fixture was not seen.
- The 400 px captures cannot show whether a table or diagram that is clipped at its panel edge actually scrolls inside its container; that was inferred from the spec and from qa.json reporting pageScrollWidth 400 with no horizontal page scroll.
