"""Optional HTML artifact tests; synthetic fixtures, no business execution."""

import copy
from html.parser import HTMLParser
import importlib.util
import json
import os
from pathlib import Path
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

    def render(self):
        return design_html.render_html(self.design, self.review)

    def test_exact_ten_stage_order_and_self_contained_layout(self):
        document = self.render()
        page = Page(document)
        expected = list(design_html.STAGES)
        self.assertEqual(
            [a["data-stage"] for _, a in page.elements if "data-stage" in a], expected
        )
        self.assertEqual(
            [
                a["data-stage-panel"]
                for _, a in page.elements
                if "data-stage-panel" in a
            ],
            expected,
        )
        self.assertIn("@media(max-width:820px)", document)
        self.assertIn("overflow-x:auto", document)
        self.assertIn('aria-label="Design stages"', document)
        self.assertEqual(len(page.scripts), 1)
        for tag, attrs in page.elements:
            self.assertNotIn(tag, ("iframe", "img", "form", "input"))
            self.assertNotIn("src", attrs)
            for name, value in attrs.items():
                self.assertFalse(name.startswith("on"))
                if name == "href":
                    self.assertTrue(value.startswith("#"))
        self.assertIn(
            "connect-src &#x27;none&#x27;", design_html.esc("connect-src 'none'")
        )
        self.assertIn("connect-src 'none'", document)
        for forbidden in (
            "fetch(",
            "XMLHttpRequest",
            "new WebSocket",
            "eval(",
            "innerHTML",
            "document.write",
        ):
            self.assertNotIn(forbidden, page.scripts[0])

    def test_untrusted_text_never_becomes_markup_or_script(self):
        payload = "</script><script>window.PWNED=true</script><img src=x onerror=alert(1)>\u2028\u2029&\"'"
        self.design["title"] = payload
        self.design["assumptions"][0]["statement"] = payload
        self.design["stages"]["components"]["items"][0]["data"]["inputs"] = [payload]
        self.design["stages"]["components"]["items"][0]["description"] = payload
        self.design["stages"]["evals"]["items"][0]["data"]["input"] = json.dumps(
            {"payload": payload}
        )
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
        self.assertIn("Zero LLM components", document)
        self.assertIn("No model calls or model token spend", document)
        self.assertIn("does not imply zero hosting", document)
        self.assertIn("no workflow execution", document)

    def test_task_tree_typed_contracts_rpn_categories_and_coverage(self):
        document = self.render()
        self.assertIn("Outcome tree", document)
        self.assertIn('href="#item-T1"', document)
        self.assertIn("Inputs · typed contract", document)
        self.assertIn("<code>requestId:string!</code>", document)
        self.assertIn("<td><strong>120</strong></td>", document)
        self.assertIn("golden: 1", document)
        self.assertIn("offline: 1", document)
        self.assertIn("online: 1", document)
        self.assertIn("release: 1", document)
        self.assertIn("High-risk leaves", document)
        self.assertIn("Pass assertions", document)
        self.assertNotIn("application/json", document)

    def test_guarded_workflow_and_terminal_are_readable(self):
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
        self.assertIn("Guarded edges", document)
        self.assertIn("W1 → W2", document)
        self.assertIn("subject is present &amp; verified", document)
        self.assertIn("Terminal disposition", document)
        self.assertIn("Recovery, guards", document)

    def test_assumptions_central_and_large_text_collapsed(self):
        statement = self.design["assumptions"][0]["statement"]
        item = self.design["stages"]["components"]["items"][0]
        item["sources"] = [{"type": "hypothesis", "file": "H1", "passage": statement}]
        item["assumptions"] = ["H1: " + statement, "Keep this custom item assumption."]
        item["description"] = "LONG_FIELD_" * 150
        document = self.render()
        self.assertEqual(document.count(statement), 1)
        self.assertIn('data-central="assumptions"', document)
        self.assertIn("Keep this custom item assumption.", document)
        self.assertIn("Read full text", document)
        self.assertIn("Reasoning &amp; provenance", document)

    def test_needs_work_view_is_honest_and_false_pass_refused(self):
        self.review["status"] = "needs-work"
        self.review["dimensions"][0]["score"] = 2
        document = self.render()
        self.assertIn("DESIGN ONLY · NEEDS-WORK", document)
        self.assertIn('id="review" open', document)
        self.review["status"] = "pass"
        with self.assertRaises(ValueError):
            self.render()
        self.review = fixtures.make_review()
        self.design["stages"]["components"]["items"][0]["data"]["taskIds"] = ["MISSING"]
        with self.assertRaises(ValueError):
            self.render()


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.design_path = self.root / "design.json"
        self.review_path = self.root / "review.json"
        self.output = self.root / "DESIGN.html"
        self.design_path.write_text(
            json.dumps(fixtures.make_design(False)), encoding="utf-8"
        )
        self.review_path.write_text(
            json.dumps(fixtures.make_review()), encoding="utf-8"
        )

    def tearDown(self):
        self.temp.cleanup()

    def export(self, out=None):
        return design_html.export_html(
            self.design_path, self.review_path, out or self.output
        )

    def test_actual_cli_export_and_input_preservation(self):
        before = (self.design_path.read_bytes(), self.review_path.read_bytes())
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(self.design_path),
                "--review",
                str(self.review_path),
                "--out",
                str(self.output),
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        status = json.loads(result.stdout)
        self.assertTrue(status["ok"])
        self.assertTrue(status["optionalVisualView"])
        self.assertTrue(status["designOnly"])
        self.assertGreater(self.output.stat().st_size, 1000)
        self.assertEqual(
            before, (self.design_path.read_bytes(), self.review_path.read_bytes())
        )

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
        with mock.patch.object(
            design_html.os, "fsync", side_effect=OSError("synthetic disk failure")
        ):
            with self.assertRaises(OSError):
                self.export()
        self.assertFalse(self.output.exists())
        self.assertTrue(self.design_path.is_file())

    def test_cli_failure_nonzero_and_no_implicit_directories(self):
        missing = self.root / "missing" / "DESIGN.html"
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(self.design_path),
                "--review",
                str(self.review_path),
                "--out",
                str(missing),
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 1)
        self.assertFalse(json.loads(result.stderr)["ok"])
        self.assertFalse(missing.parent.exists())


if __name__ == "__main__":
    unittest.main()
