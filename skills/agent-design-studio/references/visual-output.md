# PDF first, optional HTML

The final user-facing artifact is `DESIGN.pdf`, not raw JSON or a Markdown export. Its sequence matches the app: Context, Task map, Components, Workflow, Framework/tools/data, Models/cost, Failure modes, Evals, Measurement/rollout, Export/handoff. Preserve canonical IDs, design choices, controls, measurable tests, uncertainty and review status.

Use the PDF renderer with the canonical design and actual review. Prefer the host's existing ReportLab runtime; otherwise install `requirements-pdf.txt` in an isolated environment if permitted. The validator and optional HTML renderer themselves use the Python standard library. No additional model credential or business-system access is needed.

Keep PDF content readable: a concise first-page decision summary, consistent section hierarchy, wrapped long fields, page numbers and legible risk/coverage tables. Centralize assumption/source ledgers. Show concrete fixture outcome/assertion summaries and point to companion `eval-set.json` for complete machine inputs. Do not repeat every source/assumption packet or the whole canonical JSON inside the PDF. The companion files retain implementation detail.

Render pages with an available PDF tool (for example `pdftoppm`) and inspect the latest output, especially dense contracts and tables. Check for clipped text, broken rows, replacement glyphs and headings without body content. Do not describe a PDF as verified if only its text was extracted. State a concrete runtime or rendering limitation when it cannot be resolved.

After the PDF is delivered, ask: **“Would you also like a visual HTML version in the same ten-stage structure as the app?”** Ask once; prior explicit HTML authorization is sufficient. The coding-agent handoff must carry this instruction too. Do not create HTML merely because the option exists.

If accepted, generate the standalone HTML with the optional renderer. Use the same ten stages, a sidebar or tabs, readable task/workflow structure, categorized component cards, model assumptions, FMEA priorities, evaluation layers and coverage, rollout and handoff. Display assumptions and review as central supporting views. Keep it a read-only visual design artifact; no provider-key panel, approval simulation or business actions.

The HTML must work offline with embedded styling/scripts, no CDN, fonts, analytics or external network calls. Escape all brief/design text, including script-closing sequences, and use safe DOM rendering. Make navigation keyboard accessible and mobile friendly. Verify it using the host's permitted built-in browser when available; do not claim visual browser testing from source checks alone.
