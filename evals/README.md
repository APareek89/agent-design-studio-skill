# Behavioral evaluation

`briefs.json` contains six synthetic briefs for repeatable manual/agent forward-testing. A brief is the only user input; do not provide an intended design answer. Generate outputs outside this repository and review the actual artifacts.

The first release was forward-tested on municipal repair intake and deterministic CSV reporting. Both produced complete canonical designs, passed structural validation and exported their companion packages. Actual counts, author self-review methods and limitations are in `results.json`. The other four briefs are additional regression cases, not claimed completed runs. The PDF-first presentation was added afterward: both PDFs were rendered and visually checked, and all 58 unit tests passed with the PDF runtime. The optional HTML renderer passed 14 source/render/output-safety tests; browser visual QA was unavailable. No user HTML deliverable was generated.

Useful behavior checks: no follow-up questionnaire or extra API key; all ten stages and nine named files; explicit missing-fact assumptions; code-only scope can have zero model plans; coherent typed commands/recovery; substantive evaluation fixtures; honest self-review versus independent review; no business-system execution or publishing inferred from a design brief.

Structural unit tests and AI forward-tests are complementary. Neither establishes live provider accuracy, business-control correctness or production readiness. App-era review scores are not scores for this new skill.

Synthetic worked examples, including PDFs, are in `examples/civic/` and `examples/csv-report/`. Their review records say self-review; independent forward-test authorship is not independent grading of their own designs.

## HTML visual QA (v1.2)

`target/` holds the two reference pages the HTML renderer must match: `claim-adjudication-design.html` (Task map onward) and `telecom-target.html` (Decision brief). `html-qa/<date>/` holds Playwright captures of every rendered view at 1440 px and 400 px for the telecom and health-claims examples, reference captures at 1440 px, the `qa.json` reports (console errors, blocked external requests, page scroll width) and the independent grader report. The grader scores each view 0 to 4 against the reference; `html-grader.json` next to each example binds the score to the hashes of `design.json` and `DESIGN.html`, and `scripts/score_run.py` reads it as S13. Captures are JPEG to keep the repository small; rerun `node scripts/html_qa.js` for lossless PNGs.
