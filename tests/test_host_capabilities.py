"""A degraded run must look degraded.

Without a sub-agent, web search, ReportLab, Node or a question dialog, the
skill quietly produced less and the PASS badge looked exactly the same. The
run report now records what the host actually had, and the Decision brief,
the HTML status bar and page 1 of the PDF carry one line saying so.
"""

import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills/agent-design-studio/scripts"
TELECOM = ROOT / "examples/telecom"


def module(name, prefix="hc_"):
    spec = importlib.util.spec_from_file_location(prefix + name, SCRIPTS / (name + ".py"))
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


run_report = module("run_report")
design_html = module("design_html")
design_io = module("design_io")

NOTHING = {"subAgent": False, "webSearch": False, "reportLab": False, "node": False, "questionDialog": False}
EVERYTHING = {k: True for k in NOTHING}


class RunConditionsLine(unittest.TestCase):
    def test_a_fully_degraded_host_is_spelled_out(self):
        line = run_report.run_conditions(NOTHING)
        self.assertIn("Review: self-review (no separate agent available)", line)
        self.assertIn("Research: none (no web tool)", line)
        self.assertIn("PDF: skipped", line)
        self.assertIn("Visual QA: not run", line)
        self.assertIn("Intake: skipped (no question dialog)", line)

    def test_a_full_host_says_what_it_did(self):
        line = run_report.run_conditions(EVERYTHING)
        self.assertIn("independent agent review", line)
        self.assertIn("PDF: rendered", line)
        self.assertNotIn("skipped", line)

    def test_every_capability_appears_in_the_line(self):
        line = run_report.run_conditions(NOTHING)
        for _, label, _, _ in run_report.HOST_CAPABILITIES:
            self.assertIn(label + ":", line)


class DetectCapabilities(unittest.TestCase):
    def setUp(self):
        self.folder = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.folder, True)

    def test_a_self_review_is_not_a_sub_agent(self):
        found = run_report.detect_capabilities(self.folder, {}, {"method": "self-review"})
        self.assertFalse(found["subAgent"])

    def test_an_independent_review_is(self):
        found = run_report.detect_capabilities(self.folder, {}, {"method": "independent-agent"})
        self.assertTrue(found["subAgent"])

    def test_research_not_performed_counts_as_no_web_tool(self):
        design = {"research": {"performed": False, "tool": "", "unavailableReason": "no tool",
                               "queries": [], "findings": []}}
        self.assertFalse(run_report.detect_capabilities(self.folder, design, {})["webSearch"])
        design["research"]["performed"] = True
        self.assertTrue(run_report.detect_capabilities(self.folder, design, {})["webSearch"])

    def test_a_skipped_intake_counts_as_no_question_dialog(self):
        design = {"intake": {"asked": False, "tool": "", "questions": []}}
        self.assertFalse(run_report.detect_capabilities(self.folder, design, {})["questionDialog"])
        design["intake"]["asked"] = True
        self.assertTrue(run_report.detect_capabilities(self.folder, design, {})["questionDialog"])

    def test_no_pdf_on_disk_means_the_pdf_was_skipped(self):
        self.assertFalse(run_report.detect_capabilities(self.folder, {}, {})["reportLab"])


class RunConditionsReachTheReader(unittest.TestCase):
    def setUp(self):
        self.design = design_io.load_json(TELECOM / "design.json")
        self.review = design_io.load_json(TELECOM / "review.json")
        self.line = run_report.run_conditions(NOTHING)

    def test_the_html_status_bar_carries_the_line(self):
        document = design_html.render_html(self.design, self.review, "standard", (), self.line)
        self.assertIn("Run conditions - ", document)
        self.assertIn("self-review (no separate agent available)", document)

    def test_the_status_bar_repeats_it_on_every_view(self):
        document = design_html.render_html(self.design, self.review, "standard", (), self.line)
        # Once per status bar, plus the Review panel on the Decision brief.
        self.assertGreaterEqual(document.count("Run conditions - "), len(design_html.VIEW_ORDER))

    def test_a_run_with_no_report_shows_no_line(self):
        document = design_html.render_html(self.design, self.review)
        self.assertNotIn("Run conditions - ", document)

    def test_the_line_is_read_from_the_run_report_beside_the_design(self):
        folder = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, folder, True)
        (folder / "run-report.json").write_text(json.dumps({"runConditions": self.line}), encoding="utf-8")
        self.assertEqual(design_html.run_conditions_near(folder / "design.json"), self.line)

    def test_no_run_report_reads_as_no_conditions(self):
        folder = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, folder, True)
        self.assertEqual(design_html.run_conditions_near(folder / "design.json"), "")


class SelfReviewNeverReadsAsIndependent(unittest.TestCase):
    def test_the_method_field_cannot_say_both(self):
        # The schema allows only "self-review" or "independent-agent", so the
        # two can never be claimed at once in that field.
        review = design_io.load_json(TELECOM / "review.json")
        review["method"] = "self-review by the independent authoring agent"
        self.assertFalse(design_io.validate_review(review)["valid"])

    def test_a_self_review_claiming_independence_in_an_issue_is_rejected(self):
        review = design_io.load_json(TELECOM / "review.json")
        review["method"] = "self-review"
        issue = dict(review["issues"][0])
        issue["message"] = "Confirmed by an independent reviewer."
        review["issues"] = [issue] + list(review["issues"][1:])
        result = design_io.validate_review(review)
        self.assertFalse(result["valid"])
        self.assertTrue(any("cannot describe itself as independent" in e["message"] for e in result["errors"]),
                        result["errors"])

    def test_the_word_is_caught_in_limitations_too(self):
        review = design_io.load_json(TELECOM / "review.json")
        review["method"] = "self-review"
        review["limitations"] = list(review["limitations"]) + ["Scored by an independent reviewer."]
        result = design_io.validate_review(review)
        self.assertTrue(any(e["path"].startswith("$.review.limitations") for e in result["errors"]), result["errors"])

    def test_a_genuinely_independent_review_is_untouched(self):
        review = design_io.load_json(TELECOM / "review.json")
        self.assertEqual(review["method"], "independent-agent")
        self.assertTrue(design_io.validate_review(review)["valid"])

    def test_the_telecom_limitations_must_be_rewritten_for_a_self_review(self):
        # They say the review was independent, which a self-review may not.
        review = design_io.load_json(TELECOM / "review.json")
        review["method"] = "self-review"
        result = design_io.validate_review(review)
        self.assertFalse(result["valid"])
        self.assertTrue(all(e["path"].startswith("$.review.limitations") for e in result["errors"]),
                        result["errors"])

    def test_the_html_never_prints_independent_for_a_self_review(self):
        design = design_io.load_json(TELECOM / "design.json")
        review = design_io.load_json(TELECOM / "review.json")
        review["method"] = "self-review"
        review["limitations"] = [
            "Scored by the authoring agent against the rubric; no separate reviewer was available.",
            "Business assertions were not executed.",
        ]
        document = design_html.render_html(design, review, "standard", (), run_report.run_conditions(NOTHING))
        bar = document[document.find('class="statusbar"'):]
        bar = bar[: bar.find("</div>") + 6]
        self.assertNotIn("independent", bar.lower())


if __name__ == "__main__":
    unittest.main()
