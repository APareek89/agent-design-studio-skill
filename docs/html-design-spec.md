# HTML design specification (DESIGN.html, v1.2)

`DESIGN.html` is the default visual deliverable of Agent Design Studio, written by `design_io.py export` in every mode next to `DESIGN.pdf`. It is a read-only view of one `design.json` and `review.json`. It must look and behave like `evals/target/claim-adjudication-design.html` from the Task map step onward and like `evals/target/telecom-target.html` for the Decision brief. Where this document and the reference files differ, the reference files win; where a reference shows an approval control, the read-only rule below wins.

The renderer is `skills/agent-design-studio/scripts/design_html.py`. It uses only the Python standard library, embeds its own CSS and JavaScript, loads nothing from the network, holds no design data in script, escapes every design and review string, and offers no approve, regenerate, upload or edit control. The optional visual check is `scripts/html_qa.js` (Playwright).

## Shell and tokens

- **Layout.** Sticky top bar: product name, design title, mode chip, status chip (`DESIGN ONLY · PASS` or `NEEDS-WORK`), `read-only` chip. Left column 236 px with the step list; main column at most 1180 px. Under the title bar in the main column: a horizontal chevron rail of the ten steps grouped under three thin labels. Below 900 px the left list becomes a horizontal scroll strip and the rail is hidden; below 620 px grids stack to one column. No horizontal page scroll; only tables, the task tree and the flow diagram scroll inside their own container.
- **Type.** Display face IBM Plex Sans Condensed, body IBM Plex Sans, data and IDs IBM Plex Mono, each declared first in its stack with system fallbacks (`system-ui, -apple-system, "Segoe UI", sans-serif`; `ui-monospace, Menlo, Consolas, monospace`). No font is loaded from the network. Nothing in the SVG is smaller than 11 px.
- **Colour tokens** (light; dark values in the reference file): background `#eef1f0`, surface `#ffffff`, text `#16202a`, muted `#5a6570`, line `#d3dad7`, accent `#0b6d66`, accent-soft `#d5ebe7`. Component types: LLM `#6a4bd6`, code validation `#365a7d`, read tool `#2c8549`, write tool `#c25a14`, human `#b52f4b`, retrieval `#0b7c8a`, decision `#946f00`. Semantic: ok `#2c8549`, warn `#946f00`, critical `#b52f4b`. Both themes through `prefers-color-scheme` and `data-theme`.
- **Chips.** Every type, basis and risk value is a pill with a 7 px dot in its type colour. IDs (T1.2, C14, FM3, EV7, W9) are mono, muted, and clickable wherever they appear: a task ID opens that leaf in Task map; an FM ID opens that row in Risks and flashes it; a W ID opens that node in Flow.
- **Status bar** at the bottom of every view: "Proposed design", review method, round and status, "Read-only view. Not approved by stakeholders." and a `Next → <number> <step>` button. Never an approve button.

## Step names, groups and captions

Stage keys in `design.json` do not change. The reader-facing number, group, name and caption live in one table, `report_v2.STEPS`, read by the HTML and PDF renderers.

| Group | # | Key | Name | Caption |
| --- | --- | --- | --- | --- |
| Understand | 1 | context | Brief and scope | What problem, for whom, with what limits? |
|  | 2 | tasks | Task map | What must the system get done? |
| Design | 3 | components | Building blocks | Which parts are code, which are a model, which are people? |
|  | 4 | workflow | Flow | In what order, with what checks and exits? |
|  | 5 | framework | Stack and permissions | What runs it, and what may it touch? |
|  | 6 | models | Models and cost | Which model where, at what price? |
| Prove | 7 | fmea | Risks | What goes wrong, how bad, how do we catch it? |
|  | 8 | evals | Tests | How do we know each risk is covered? |
|  | 9 | rollout | Measure and roll out | How do we prove value and grow autonomy safely? |
|  | 10 | export | Handoff | What does the builder receive? |

Read-only outputs add **0 Decision brief** ("Read this first") before step 1 and an **Evidence** group after step 10 with **Assumptions** and **Review**. The PDF uses "3. Building blocks" style headings with the group and caption as a running line above each section.

### The rail

A flex row of ten chevrons (`clip-path: polygon(0 0, calc(100% - 14px) 0, 100% 50%, calc(100% - 14px) 100%, 0 100%, 14px 50%)`, 8 px negative margin so the points nest, first item without the left notch, minimum tap target 40 px). Each chevron shows number, name and a state mark: done ✓ (accent-soft fill), current ● (surface fill, accent border, bold). A read-only view has no locked or stale state; the app uses locked ○ (muted, "Approve step N first") and stale ⚠ (amber, "Changed upstream; review again"). The rail is `<nav aria-label="Steps">` with an ordered list; the current step has `aria-current="step"`. On narrow screens the rail scrolls sideways and the current step is centred. The left column keeps the vertical list with the same names, a 2 px connector and a small down-arrow glyph between steps.

## Views

Each view must contain the blocks below in this order. Nothing is truncated with an ellipsis; long text wraps; long ID lists wrap as chips.

| View | Must contain, in this order |
| --- | --- |
| 0 Decision brief | One-sentence system description (`presentation.systemSentence`) and the scope summary. 3 to 5 design calls as numbered cards: full sentence, then "Rejected: X. Why." Autonomy table (action, level). Right column: KPI block (name, baseline → target when the KPI text states one, definition), top 5 risks by RPN with an RPN pill and one-line control, launch blockers with owner, cost per case and per month with the volume assumption and its source, review status in one line. |
| 1 Brief and scope | The verbatim brief in a box; then a two-column table of context fields and the design reading, with the scope summary as the first row. When the design carries a `research` record: a **Research used** table (ID, topic, source title with the URL as plain text, retrieval date, what it says, used-by chips), or one line saying no web research was performed and why. |
| 2 Task map | Risk-rule callout with the count of high-risk leaves. A top-down tree: root box (dark, with mode and task count), a horizontal connector, one column per task with a bordered task box (ID, name, mode chip: "sequence: all run" or "choose one per case") and below it the leaf cards joined by a left rail. A top-level task that is itself a leaf renders as a bordered leaf card in its column. Each leaf card: ID and name, basis chips (or basis lines when the basis is a sentence), two examples as bullets, autonomy line, risk with the reason in brackets for high. Clicking a leaf fills the detail panel: breadcrumb, name, what it does, resolved by, all examples as quote boxes, autonomy, frequency and risk, component chips, failure-mode chips, "Show in flow". Then the **Key attributes** grid: attribute rows × task columns with ticks, plus Source and Loaded. |
| 3 Building blocks | First the **interpretation inventory** table (input, why it is hard, handled by, signal, fallback), one row per LLM component. Then four groups with a heading chip: Agents (LLM), Code: tools, Code: validation, Code: human triggers. Cards: ID, name, write or retrieval chip where relevant, description, "Why code" callout with a blue left rule, Authority line, collapsible inputs and outputs in mono, task ID chips. |
| 4 Flow | Task filter bar (All, then one chip per top-level task) that dims unrelated nodes and edges. Legend of type chips plus "rounded box = decision step". SVG diagram: lane captions in mono caps derived from the dominant top-level task per column; nodes 180 × (66 or taller when a label wraps) with 6 px radius, filled 13 % of the type colour with a 1.5 px type-colour border; header line "W9 · C8 · decides" where applicable, bold title, muted one-line example; decision nodes use a 14 px radius. Edges are direct curves with an arrowhead and the condition on a small surface-coloured plate drawn above the nodes; loop-back edges run orthogonally above the nodes; no shared bus lines. Below each node that can leave the happy path, a mono note: red "↳ handoff: condition" when an edge enters a human-trigger step, amber "↳ uncertain exit: condition" for TIMEOUT or unknown-commit outcomes. Clicking a node fills a detail panel: type chip, IDs, task chips, name, example, what the part does, a Next steps table (go to, when, parallel marker), failure disposition, timeout and retry, failure-mode chips, collapsible state contract. Then the **Coverage** table: every leaf, the steps that serve it, Covered or Gap. |
| 5 Stack and permissions | When the design has `tooling` cards, first a **Tools by capability** table (capability, chosen option, candidate count, Checked or Unverified). Then one card per framework item: breadcrumb with ID, category, capability and permission, title, then Choice, Rejected, Trade-off; tooling cards add a Candidates table (candidate, kind, note, evidence as RS chips or "unverified"); permission cards add Blast radius, Approval, Least privilege; cards with cloud options add a small table AWS / Google Cloud / Azure / Open source. |
| 6 Models and cost | Table: part, tier, why and rejected tier, fine-tune only when, calls per case, USD per case. Below: a cost calculator with an editable volume field, cost per case in large mono, the per-month figure, the formula, the volume source and exclusions as notes. A code-only design states that no model is used. |
| 7 Risks | Two boxes side by side: severity × occurrence heat table with FM IDs in the cells (red, amber, green bands), and the act-now rule with the count of qualifying risks. Then the register sorted by RPN: ID and name, "all tasks" tag where common, effect in muted text, subtask ID chips, S, O, D, RPN pill coloured by band, control, test IDs. Clicking a row expands a three-column strip: cause, detection and metric → KPI, owner and gate. |
| 8 Tests | **Coverage** table first: each failure mode and each high-risk leaf, number of tests, key test name, Covered in green or Gap in red. Then golden cases as cards: ID and name, linked FM chip or "positive", a "Must hold" block listing the assertions, collapsible fixture and expected result. Then one table for offline, online and release tests: layer, metric, target, cadence, alert. |
| 9 Measure and roll out | KPI cards: name, baseline → target in mono when stated, definition, the AI metrics that move it, the mechanism in one line. Phases as joined panels: name, what happens, gate, owner. Then boxes for experiments and owners. |
| 10 Handoff | File list (name, one-line purpose) for the user folder: DESIGN.html, DESIGN.pdf, build/, design.json, README.md, review and validation records, `_evidence/`. Numbered build milestones. Acceptance criteria as a list. Build instructions collapsed below. |
| Assumptions | Table: ID, assumption, owner, how to verify, blocks launch (Yes in red). Stage and item notes below. |
| Review | Method, round, status line. Dimension table with name, score and evidence. Issues table with status. Limits list. Earlier rounds listed by file name. |

**Lite mode** renders the Decision brief, Task map, Flow and Risks only. Standard and full render all twelve views.

## Behaviour

- One view on screen at a time; the URL hash holds the view (`#tasks`, `#workflow`); the step list and the rail show the current step.
- Selections (current leaf, node, task filter, expanded risk) live in page state; nothing is written to storage except an optional last view in `localStorage` inside try/catch.
- Keyboard: every clickable node, leaf and row is focusable and activates on Enter or Space.
- Nothing is truncated with an ellipsis. Long text wraps. Long ID lists wrap as chips.
- Zero external requests: no fonts, images, scripts or styles from the network. Inline SVG only. The script never uses `innerHTML`, `eval`, `fetch` or `XMLHttpRequest`.
- Printing shows every view in order.

## Capacity

If a flow has more than 16 layers the diagram continues in a second band below the first, with a dashed separator; cross-band edges become "→ continues at W12 (band 2)" and "← from W4 (band 1)" notes under the nodes. Nodes are never dropped, text is never shrunk below 11 px, and no diagram falls back to a table. Wide diagrams and trees scroll inside their panel.

## Where the reader layer comes from

`presentation.systemSentence`, `designCalls`, `autonomy`, `scopeSummary`, `taskLabels`, `workflowLabels` and `milestones` feed the brief, the tree and node labels and the handoff. When `presentation` is absent (schema 1.0), the brief is derived from the stages by `report_v2.brief_data` and the view says so in one line. Derived rows that the data does not state directly are labelled: the volume assumption names its H-ID or says it is an illustrative default; risk reasons come from the serving components' declared effects; handoff and exit notes come from the workflow edges and semantic outcomes.

## Acceptance (visual grader rubric, 0 to 4 per view)

4 = same blocks in the same order with the same interactions as the reference; 3 = same blocks and order, minor spacing or label differences; 2 = a block missing or out of order; 1 = view present but a table where a diagram or card layout is required; 0 = view missing. Pass at 3 or above for every view on both seed designs. A separate grader agent scores from the screenshots in `evals/html-qa/<date>/` against the reference captures in `evals/html-qa/<date>/reference/` and writes `html-grader.json` next to each scored design; `scripts/score_run.py` reads it as S13.

## Known limits of the HTML

- The task tree is a CSS grid like the reference, not SVG; the flow is SVG.
- Edge conditions longer than one plate line wrap to several lines; very long predicates are easier to read in the node's detail table.
- The lane captions and handoff notes are derived, not authored; a design can override node and task names only through `presentation`.
- The cost calculator multiplies the per-case model budget by a volume; it does not price hosting, tools, retrieval or staff time.
- The page is a view, not a session: nothing a reader clicks changes `design.json`.
