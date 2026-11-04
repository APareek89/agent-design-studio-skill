# HTML and PDF together

Every run delivers two readable artifacts from the same `design.json` and `review.json`: `DESIGN.html`, a clickable read-only view, and `DESIGN.pdf`, a printable report. `design_io.py export` writes `DESIGN.html` in every mode; pass `--no-html` only when the host cannot write it, and say so. Neither artifact is an approval tool.

## DESIGN.html

The renderer is `scripts/design_html.py` (standard library only). It renders the Decision brief, the ten steps under their reader names (Brief and scope, Task map, Building blocks, Flow, Stack and permissions, Models and cost, Risks, Tests, Measure and roll out, Handoff) and an Evidence group (Assumptions, Review). Lite mode renders the Decision brief, Task map, Flow and Risks only. The full view-by-view contract is `docs/html-design-spec.md` in the repository; the reference files are `evals/target/`.

What the page must do:

- Build the task tree and the flow from `design.json`: every task box and every workflow node is present; edges carry their condition; handoff and uncertain-exit notes come from the edges. Large graphs split into bands or scroll; nodes are never dropped and text never shrinks below 11 px.
- Read the reader layer (`presentation`, `milestones`, `runOptions`) for the brief, labels and handoff; say in one line when it had to derive the brief from a schema 1.0 input.
- Stay self-contained: embedded styles and script, no fonts, images, scripts or styles from the network, every design and review string HTML-escaped, no design data inside the script. Keyboard access for every clickable node, leaf and row. No approval, regenerate, upload or edit control; the status bar says the design is proposed and not approved.
- Never truncate with an ellipsis. Keep exact IDs clickable: task IDs open the leaf, FM IDs open and flash the risk row, W IDs open the node.

Check it before delivery when a browser is available: `node scripts/html_qa.js <out>/DESIGN.html <qa-folder> --jpeg` opens the page offline, screenshots every view at 1440 px and 400 px, and fails on console errors, external requests or page-level horizontal scroll. Do not claim visual browser testing from source checks alone. An independent grader scoring each view 0 to 4 against the reference captures is recorded as `html-grader.json`; `score_run.py` reads it as S13.

## DESIGN.pdf

Use the PDF renderer with the canonical design and actual review. Prefer the host's existing ReportLab runtime; otherwise install `requirements-pdf.txt` in an isolated environment if permitted. No additional model credential or business-system access is needed.

Keep PDF content readable: a concise first-page decision brief, section headings in the same step names and numbers as the HTML, wrapped long fields, page numbers and legible risk and coverage tables. Centralize assumption and source ledgers. Show concrete fixture outcome and assertion summaries and point to `_evidence/eval-set.json` for complete machine inputs. Do not repeat every source packet or the whole canonical JSON inside the PDF.

Render pages with an available PDF tool (for example `pdftoppm`) and inspect the latest output, especially dense contracts and tables. Check for clipped text, broken rows, replacement glyphs and headings without body content. Do not describe a PDF as verified if only its text was extracted. State a concrete runtime or rendering limitation when it cannot be resolved.
