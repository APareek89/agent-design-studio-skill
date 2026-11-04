"""HTML artifact tests on the synthetic fixture; no business execution."""

import copy
from html.parser import HTMLParser
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/agent-design-studio/scripts/design_html.py"
spec = importlib.util.spec_from_file_location("design_html", SCRIPT)
design_html = importlib.util.module_from_spec(spec)
spec.loader.exec_module(design_html)
fixture_spec = importlib.util.spec_from_file_location(
    "html_test_fixtures", ROOT / "tests/test_design_io.py"
)
fixtures = importlib.util.module_from_spec(fixture_spec)
fixture_spec.loader.exec_module(fixtures)


class Page(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.elements = []
        self.scripts = []
        self.in_script = False
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))
        if tag == "script":
            self.in_script = True
            self.scripts.append("")

    def handle_endtag(self, tag):
        if tag == "script":
            self.in_script = False

    def handle_data(self, value):
        if self.in_script:
            self.scripts[-1] += value


class RenderTests(unittest.TestCase):
    def setUp(self):
        self.design = fixtures.make_design()
        self.review = fixtures.make_review()

    def render(self, mode="standard"):
        return design_html.render_html(self.design, self.review, mode)

    def test_twelve_views_in_order_and_self_contained_layout(self):
        document = self.render()
        page = Page(document)
        views = [a["data-view"] for t, a in page.elements if t == "section" and "data-view" in a]
        self.assertEqual(views, list(design_html.VIEW_ORDER))
        self.assertEqual(len(views), 13)  # brief + ten steps + assumptions + review
        side = [a["data-step"] for t, a in page.elements if "data-step" in a and "step" in a.get("class", "")]
        self.assertEqual(side, list(design_html.VIEW_ORDER))
        self.assertIn("@media (max-width:900px)", document)
        self.assertIn("overflow-x:auto", document)
        self.assertIn('aria-label="Design steps"', document)
        self.assertIn('aria-label="Steps"', document)
        self.assertEqual(len(page.scripts), 1)
        for tag, attrs in page.elements:
            self.assertNotIn(tag, ("iframe", "img", "form", "link", "object", "embed"))
            self.assertNotIn("src", attrs)
            if tag == "input":
                self.assertEqual(attrs.get("type"), "number")
                self.assertIn("data-calc", attrs)
            for name, value in attrs.items():
                self.assertFalse(name.startswith("on"))
                if name == "href":
                    self.assertTrue(value.startswith("#"))
        self.assertIn("connect-src &#x27;none&#x27;", design_html.esc("connect-src 'none'"))
        self.assertIn("connect-src 'none'", document)
        for forbidden in ("fetch(", "XMLHttpRequest", "new WebSocket", "eval(", "innerHTML", "document.write", "http://", "https://"):
            self.assertNotIn(forbidden, page.scripts[0])
        self.assertNotIn("@import", document)
        self.assertIsNone(re.search(r"url\((?!#)", document))  # only the in-page SVG marker reference

    def test_untrusted_text_never_becomes_markup_or_script(self):
        payload = "</script><script>window.PWNED=true</script><img src=x onerror=alert(1)>  &\"'"
        self.design["title"] = payload
        self.design["assumptions"][0]["statement"] = payload
        self.design["stages"]["components"]["items"][0]["data"]["inputs"] = [payload]
        self.design["stages"]["components"]["items"][0]["description"] = payload
        self.design["stages"]["evals"]["items"][0]["data"]["input"] = json.dumps({"payload": payload})
        self.design["stages"]["workflow"]["items"][0]["data"]["example"] = payload
        self.review["limitations"] = [payload]
        self.review["dimensions"][0]["evidence"] = [payload]
        self.review["issues"] = [
            {
                "id": payload,
                "severity": "observation",
                "stage": "context",
                "itemId": payload,
                "message": payload,
                "resolved": False,
            }
        ]
        document = self.render()
        page = Page(document)
        self.assertEqual(len(page.scripts), 1)
        self.assertNotIn("PWNED", page.scripts[0])
        self.assertNotIn("<img src=x", document)
        self.assertIn("&lt;/script&gt;", document)
        self.assertIn("&#x27;", document)
        self.assertNotIn("img", [t for t, _ in page.elements])

    def test_code_only_is_explicit_and_no_model_claims_are_fabricated(self):
        self.design = fixtures.make_design(False)
        document = self.render()
        self.assertIn("No LLM component", document)
        self.assertIn("No model calls or model token spend", document)
        self.assertIn("does not imply zero hosting", document)
        self.assertIn("No model calls: the model budget is zero", document)
        self.assertNotIn('data-month-cost="', document)
        self.assertIn("Read-only view. Not approved by stakeholders", document)

    def test_tree_contracts_rpn_coverage_and_reader_layer_note(self):
        document = self.render()
        self.assertIn('data-leaf="T1"', document)
        self.assertIn('data-leaf-detail="T1"', document)
        self.assertIn("Prepare owned triage", document)
        self.assertIn("Inputs and outputs", document)
        self.assertIn("<li>requestId:string!</li>", document)
        self.assertIn('class="rpn hi">120<', document)
        self.assertIn("Act-now rule", document)
        self.assertIn("Must hold", document)
        self.assertIn("equals.disposition == &quot;ABSTAIN&quot;", document)
        self.assertIn(">Covered<", document)
        self.assertIn("Reader layer derived from the ten stages", document)
        self.assertIn("zero prices mean unpriced, not free", document)
        self.assertNotIn("application/json", document)
        self.assertIn('data-calc="volume"', document)
        self.assertIn("data-month-cost", document)

    def test_guarded_workflow_terminal_and_labels_are_readable(self):
        node = self.design["stages"]["workflow"]["items"][0]
        terminal = copy.deepcopy(node)
        terminal["id"] = "W2"
        self.design["stages"]["workflow"]["items"].append(terminal)
        contract = json.loads(node["description"])
        contract["transitions"] = [
            {"to": "W2", "when": "subject is present & verified", "mode": "exclusive"}
        ]
        contract["terminalDisposition"] = ""
        node["description"] = json.dumps(contract)
        node["data"].update(next=["W2"], decision=True)
        document = self.render()
        self.assertIn('data-node="W1"', document)
        self.assertIn('data-node="W2"', document)
        self.assertIn('data-edge="W1-W2"', document)
        self.assertIn("subject is present &amp;", document)
        self.assertIn("Ends here.", document)
        self.assertIn("State contract", document)
        self.assertIn("· decides", document)
        self.assertIn('rx="14"', document)

    def test_assumptions_view_keeps_item_notes_and_full_text(self):
        statement = self.design["assumptions"][0]["statement"]
        item = self.design["stages"]["components"]["items"][0]
        item["sources"] = [{"type": "hypothesis", "file": "H1", "passage": statement}]
        item["assumptions"] = ["H1", "Keep this custom item assumption."]
        item["description"] = "LONG_FIELD_" * 150
        document = self.render()
        self.assertIn('data-view="assumptions"', document)
        self.assertIn("Keep this custom item assumption.", document)
        self.assertIn("LONG_FIELD_" * 150, document)
        self.assertNotIn("Read full text", document)
        self.assertNotIn("…", document)
        self.assertIn("Blocks launch", document)

    def test_needs_work_view_is_honest_and_false_pass_refused(self):
        self.review["status"] = "needs-work"
        self.review["dimensions"][0]["score"] = 2
        document = self.render()
        self.assertIn("DESIGN ONLY · NEEDS-WORK", document)
        self.assertIn("round 1: needs-work. Read-only view", document)
        self.review["status"] = "pass"
        with self.assertRaises(ValueError):
            self.render()
        self.review = fixtures.make_review()
        self.design["stages"]["components"]["items"][0]["data"]["taskIds"] = ["MISSING"]
        with self.assertRaises(ValueError):
            self.render()

    def test_lite_mode_renders_four_views_and_no_approval_controls(self):
        document = self.render("lite")
        page = Page(document)
        views = [a["data-view"] for t, a in page.elements if t == "section" and "data-view" in a]
        self.assertEqual(views, list(design_html.LITE_VIEWS))
        self.assertNotIn("Approve", document)
        self.assertNotIn("Regenerate", document)
        self.assertIn("read-only", document)
        with self.assertRaises(ValueError):
            self.render("tiny")


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.design_path = self.root / "design.json"
        self.review_path = self.root / "review.json"
        self.output = self.root / "DESIGN.html"
        self.design_path.write_text(json.dumps(fixtures.make_design(False)), encoding="utf-8")
        self.review_path.write_text(json.dumps(fixtures.make_review()), encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def export(self, out=None, **kwargs):
        return design_html.export_html(self.design_path, self.review_path, out or self.output, **kwargs)

    def test_actual_cli_export_and_input_preservation(self):
        (self.root / "review-round-1.json").write_text(json.dumps(fixtures.make_review("needs-work")))
        before = (self.design_path.read_bytes(), self.review_path.read_bytes())
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(self.design_path), "--review", str(self.review_path), "--out", str(self.output), "--mode", "lite"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        status = json.loads(result.stdout)
        self.assertTrue(status["ok"])
        self.assertTrue(status["readOnlyView"])
        self.assertTrue(status["designOnly"])
        self.assertEqual(status["mode"], "lite")
        self.assertEqual(status["views"], list(design_html.LITE_VIEWS))
        self.assertGreater(self.output.stat().st_size, 1000)
        self.assertEqual(before, (self.design_path.read_bytes(), self.review_path.read_bytes()))
        standard = self.root / "standard.html"
        self.assertTrue(self.export(standard)["ok"])
        self.assertIn("review-round-1.json", standard.read_text(encoding="utf-8"))

    def test_existing_output_and_both_input_aliases_refused(self):
        self.output.write_text("existing private document")
        with self.assertRaises(ValueError):
            self.export()
        self.assertEqual(self.output.read_text(), "existing private document")
        for path in (self.design_path, self.review_path):
            with self.assertRaises(ValueError):
                self.export(path)

    def test_final_symlinks_refused_and_parent_alias_still_cannot_overwrite(self):
        self.output.symlink_to(self.design_path)
        with self.assertRaises(ValueError):
            self.export()
        self.output.unlink()
        self.output.symlink_to(self.root / "missing")
        with self.assertRaises(ValueError):
            self.export()
        self.output.unlink()
        actual = self.root / "actual"
        actual.mkdir()
        alias = self.root / "alias"
        alias.symlink_to(actual, target_is_directory=True)
        self.assertTrue(self.export(alias / "report.html")["ok"])
        self.assertTrue((actual / "report.html").is_file())
        with self.assertRaises(ValueError):
            self.export(alias / "report.html")

    def test_hardlink_to_either_input_or_unrelated_file_refused(self):
        unrelated = self.root / "notes.txt"
        unrelated.write_text("preserve")
        for target in (self.design_path, self.review_path, unrelated):
            os.link(target, self.output)
            original = target.read_bytes()
            with self.assertRaises(ValueError):
                self.export()
            self.assertEqual(target.read_bytes(), original)
            self.output.unlink()

    def test_invalid_design_review_or_duplicate_json_writes_nothing(self):
        initial = self.design_path.read_text()
        for bad in ('{"x":1,"x":2}', '{"schemaVersion":"1.0"}'):
            self.design_path.write_text(bad)
            with self.assertRaises(ValueError):
                self.export()
            self.assertFalse(self.output.exists())
        self.design_path.write_text(initial)
        review = fixtures.make_review()
        review["dimensions"][0]["score"] = 1
        self.review_path.write_text(json.dumps(review))
        with self.assertRaises(ValueError):
            self.export()
        self.assertFalse(self.output.exists())

    def test_failed_write_removes_only_own_partial_output(self):
        with mock.patch.object(design_html.os, "fsync", side_effect=OSError("synthetic disk failure")):
            with self.assertRaises(OSError):
                self.export()
        self.assertFalse(self.output.exists())
        self.assertTrue(self.design_path.is_file())

    def test_cli_failure_nonzero_and_no_implicit_directories(self):
        missing = self.root / "missing" / "DESIGN.html"
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(self.design_path), "--review", str(self.review_path), "--out", str(missing)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 1)
        self.assertFalse(json.loads(result.stderr)["ok"])
        self.assertFalse(missing.parent.exists())


if __name__ == "__main__":
    unittest.main()
