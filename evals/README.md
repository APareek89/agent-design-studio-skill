# Behavioral evaluation

`briefs.json` contains six synthetic briefs for repeatable manual/agent forward-testing. A brief is the only user input; do not provide an intended design answer. Generate outputs outside this repository and review the actual artifacts.

The first release was forward-tested on municipal repair intake and deterministic CSV reporting. Both produced complete canonical designs, passed structural validation and exported their companion packages. Actual counts, author self-review methods and limitations are in `results.json`. The other four briefs are additional regression cases, not claimed completed runs. The PDF-first presentation was added afterward: both PDFs were rendered and visually checked, and all 58 unit tests passed with the PDF runtime. The optional HTML renderer passed 14 source/render/output-safety tests; browser visual QA was unavailable. No user HTML deliverable was generated.

Useful behavior checks: no follow-up questionnaire or extra API key; all ten stages and nine named files; explicit missing-fact assumptions; code-only scope can have zero model plans; coherent typed commands/recovery; substantive evaluation fixtures; honest self-review versus independent review; no business-system execution or publishing inferred from a design brief.

Structural unit tests and AI forward-tests are complementary. Neither establishes live provider accuracy, business-control correctness or production readiness. App-era review scores are not scores for this new skill.

Synthetic worked examples, including PDFs, are in `examples/civic/` and `examples/csv-report/`. Their review records say self-review; independent forward-test authorship is not independent grading of their own designs.
