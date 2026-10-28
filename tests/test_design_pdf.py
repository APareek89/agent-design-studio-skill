"""Actual PDF coverage tests; no provider/network/business controls execute."""

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock
import test_design_io

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "skills/agent-design-studio/scripts/design_pdf.py"
)
spec = importlib.util.spec_from_file_location("design_pdf", SCRIPT)
design_pdf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(design_pdf)
try:
    import reportlab
    from pypdf import PdfReader

    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


class DependencyTests(unittest.TestCase):
    def test_reportlab_is_optional_and_error_is_actionable(self):
        real_import = __import__

        def missing(name, *args, **kwargs):
            if name == "reportlab" or name.startswith("reportlab."):
                raise ImportError("test missing reportlab")
            return real_import(name, *args, **kwargs)

        with mock.patch("builtins.__import__", side_effect=missing):
            with self.assertRaisesRegex(ValueError, "pip install"):
                design_pdf._libraries()
        self.assertTrue(
            test_design_io.design_io.validate_design(test_design_io.make_design(False))[
                "valid"
            ]
        )

    def test_fixture_summary_avoids_large_raw_mock_dump(self):
        value = json.dumps(
            {
                "command": {"kind": "CREATE", "subject": "S1"},
                "orderedMocks": {"long": "x" * 100000},
                "files": {"private": "x" * 100000},
            }
        )
        summary = design_pdf._fixture_summary(value)
        self.assertIn("CREATE", summary)
        self.assertNotIn("xxxxx", summary)
        self.assertLessEqual(len(summary), 330)


@unittest.skipUnless(
    PDF_AVAILABLE,
    "Optional PDF tests need ReportLab and pypdf; use the bundled PDF runtime.",
)
class ActualPdfTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="studio-pdf-test-")
        self.root = Path(self.temp.name)
        self.design = test_design_io.make_design()
        self.review = test_design_io.make_review()
        self.dp = self.root / "design.json"
        self.rp = self.root / "review.json"
        self.out = self.root / "DESIGN.pdf"
        self.write()

    def tearDown(self):
        self.temp.cleanup()

    def write(self):
        self.dp.write_text(json.dumps(self.design))
        self.rp.write_text(json.dumps(self.review))

    def text(self):
        return "\n".join(p.extract_text() or "" for p in PdfReader(self.out).pages)

    def test_actual_pdf_covers_ten_stages_and_handoff_question(self):
        result = design_pdf.create_pdf(self.dp, self.rp, self.out)
        self.assertTrue(result["ok"])
        self.assertGreater(result["pages"], 0)
        self.assertTrue(self.out.read_bytes().startswith(b"%PDF-"))
        text = self.text()
        for number, (_, title) in enumerate(design_pdf.SECTIONS, 1):
            self.assertIn(title, text)
        for token in (
            "T0",
            "T1",
            "C1",
            "W1",
            "F1",
            "M1",
            "FM1",
            "EV1",
            "R1",
            "X1",
            "D12",
            "H1",
            "RPN",
            "eval-set.json",
            "DESIGN ONLY",
            "human",
        ):
            self.assertIn(token, text)
        self.assertIn(design_pdf.HTML_QUESTION, text.replace("\n", " "))
        self.assertIn("Generate HTML only after opt-in", text.replace("\n", " "))
        self.assertIn("No issues were recorded", text)

    def test_untrusted_markup_and_long_identifiers_render_as_text(self):
        self.design["brief"] = (
            "User says <b>keep literal</b> & never <script>run()</script>."
        )
        for packet in self.design["stages"].values():
            for item in packet["items"]:
                item["sources"] = [
                    {
                        "type": "context",
                        "file": "user-brief",
                        "passage": self.design["brief"],
                    }
                ]
        self.design["stages"]["components"]["items"][0]["data"]["inputs"] = [
            "identifier_with_no_breaks_" + ("A" * 400) + ":string!"
        ]
        self.write()
        result = design_pdf.create_pdf(self.dp, self.rp, self.out)
        self.assertTrue(result["ok"])
        text = self.text()
        self.assertIn("<b>keep literal</b>", text)
        self.assertIn("<script>run()</script>", text)
        self.assertNotIn("&lt;script&gt;", text)

    def test_needs_work_status_and_zero_llm_pdf(self):
        self.design = test_design_io.make_design(False)
        self.review["status"] = "needs-work"
        self.review["dimensions"][0]["score"] = 2
        self.write()
        result = design_pdf.create_pdf(self.dp, self.rp, self.out)
        self.assertEqual(result["status"], "needs-work")
        text = self.text()
        self.assertIn("NEEDS-WORK", text)
        self.assertIn("No LLM components", text)

    def test_invalid_review_and_structural_error_do_not_write_pdf(self):
        self.review["dimensions"][0]["score"] = 2
        self.write()
        result = design_pdf.create_pdf(self.dp, self.rp, self.out)
        self.assertFalse(result["ok"])
        self.assertFalse(self.out.exists())
        self.design["stages"]["evals"]["items"][0]["data"]["input"] = "notJSON"
        self.write()
        result = design_pdf.create_pdf(self.dp, self.rp, self.out)
        self.assertFalse(result["ok"])
        self.assertFalse(self.out.exists())

    def test_critical_contracts_and_gates_preserve_tail_text(self):
        long = "required_field:string; " * 85
        self.design["stages"]["components"]["items"][0]["data"]["inputs"] = [
            long + " TAIL_TYPED_CONTRACT_PROOF"
        ]
        self.design["stages"]["components"]["items"][0]["data"]["approvalRule"] = (
            long + " TAIL_APPROVAL_PROOF"
        )
        self.design["stages"]["workflow"]["items"][0]["description"] = json.dumps(
            {
                "state": "DONE",
                "transitions": [],
                "failureDisposition": long + " TAIL_FAILURE_CONTROL",
                "timeout": "20s",
                "retryPolicy": "none",
                "terminalDisposition": "Owned recommendation",
            }
        )
        self.design["stages"]["rollout"]["items"][1]["data"]["gate"] = (
            long + " TAIL_ROLLOUT_GATE_PROOF"
        )
        self.design["stages"]["fmea"]["items"][0]["data"]["control"] = (
            long + " TAIL_FMEA_CONTROL_PROOF"
        )
        self.design["stages"]["fmea"]["items"][0]["data"]["action"] = (
            long + " TAIL_FMEA_ACTION_PROOF"
        )
        self.design["stages"]["export"]["items"][0]["data"]["acceptanceCriteria"] = [
            long + " TAIL_ACCEPTANCE_PROOF"
        ]
        self.design["stages"]["export"]["items"][0]["data"]["buildInstructions"] = (
            long + " TAIL_BUILD_PROOF"
        )
        self.write()
        result = design_pdf.create_pdf(self.dp, self.rp, self.out)
        self.assertTrue(result["ok"], result)
        text = self.text()
        for tail in (
            "TAIL_TYPED_CONTRACT_PROOF",
            "TAIL_APPROVAL_PROOF",
            "TAIL_FAILURE_CONTROL",
            "TAIL_ROLLOUT_GATE_PROOF",
            "TAIL_FMEA_CONTROL_PROOF",
            "TAIL_FMEA_ACTION_PROOF",
            "TAIL_ACCEPTANCE_PROOF",
            "TAIL_BUILD_PROOF",
        ):
            self.assertIn(tail, text)

    def test_pdf_never_overwrites_existing_user_files_or_inputs(self):
        self.out.write_text("user file")
        with self.assertRaisesRegex(ValueError, "never overwritten"):
            design_pdf.create_pdf(self.dp, self.rp, self.out)
        self.assertEqual(self.out.read_text(), "user file")
        with self.assertRaises(ValueError):
            design_pdf.create_pdf(self.dp, self.rp, self.dp)
        self.assertEqual(json.loads(self.dp.read_text()), self.design)

    def test_assumptions_deduplicated_and_fixtures_not_dumped(self):
        statement = "UNIQUE_REPEATED_ASSUMPTION_SENTINEL"
        self.design["stages"]["tasks"]["assumptions"] = [statement]
        self.design["stages"]["components"]["items"][0]["assumptions"] = [
            statement,
            "H1: REDUNDANT_HYPOTHESIS_REFERENCE_SENTINEL",
        ]
        item = self.design["stages"]["evals"]["items"][0]
        item["data"]["input"] = json.dumps(
            {
                "command": {"kind": "CREATE"},
                "orderedMocks": {"large": "RAW_FIXTURE_SENTINEL" * 200},
            }
        )
        self.write()
        self.assertTrue(design_pdf.create_pdf(self.dp, self.rp, self.out)["ok"])
        text = self.text()
        self.assertEqual(text.count(statement), 1)
        self.assertNotIn("RAW_FIXTURE_SENTINEL", text)
        self.assertNotIn("REDUNDANT_HYPOTHESIS_REFERENCE_SENTINEL", text)


if __name__ == "__main__":
    unittest.main()
