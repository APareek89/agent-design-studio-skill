"""Research record, research sources and tooling cards: validation, rendering and export.

Synthetic fixtures only. The validator checks that citations are consistent with
the recorded findings; it cannot verify that a web page says what the summary
claims, and these tests do not fetch anything.
"""

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills/agent-design-studio/scripts"


def module(name):
    spec = importlib.util.spec_from_file_location("rt_" + name, SCRIPTS / (name + ".py"))
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


design_io = module("design_io")
design_html = module("design_html")
fixture_spec = importlib.util.spec_from_file_location("rt_fixtures", ROOT / "tests/test_design_io.py")
fixtures = importlib.util.module_from_spec(fixture_spec)
fixture_spec.loader.exec_module(fixtures)

FINDING = {
    "id": "RS1",
    "topic": "tool: guardrails and PII",
    "url": "https://example.test/docs/pii-detection",
    "title": "Example PII detection service documentation",
    "retrievedAt": "2026-11-04",
    "summary": "The documented service detects names, phone numbers and account identifiers in text and returns spans with confidence.",
    "usedBy": ["F2", "H1"],
}


def researched_design():
    design = fixtures.make_design()
    design["research"] = {
        "performed": True,
        "tool": "host web search",
        "unavailableReason": "",
        "queries": ["PII detection service text spans confidence", "internal request triage practice"],
        "findings": [copy.deepcopy(FINDING)],
    }
    base = design["stages"]["framework"]["items"][0]
    card = copy.deepcopy(base)
    card["id"] = "F2"
    card["title"] = "PII detection before the model"
    card["description"] = "A detection service runs on every request before the model sees it."
    card["sources"] = [{"type": "research", "file": "RS1", "passage": FINDING["summary"]}]
    card["data"].update(
        category="tooling",
        capability="guardrails and PII detection",
        choice="Managed detection service, chosen for span-level output with confidence.",
        alternatives=["Regex-only scrubbing: rejected, misses free-text identifiers."],
        candidates=[
            {"name": "Example detection service", "kind": "managed", "note": "Returns spans with confidence; checked against RS1.", "verified": True, "sourceIds": ["RS1"]},
            {"name": "Open-source analyzer", "kind": "open-source", "note": "Self-hosted option; not checked in this run.", "verified": False, "sourceIds": []},
        ],
    )
    design["stages"]["framework"]["items"].append(card)
    return design


class ValidationTests(unittest.TestCase):
    def errors(self, design):
        return [e["path"] + ": " + e["message"] for e in design_io.validate_design(design)["errors"]]

    def test_researched_design_is_valid_and_legacy_examples_still_validate(self):
        self.assertEqual(self.errors(researched_design()), [])
        for name in ("telecom", "health-claims", "civic", "csv-report"):
            design = design_io.load_json(ROOT / "examples" / name / "design.json")
            self.assertTrue(design_io.validate_design(design)["valid"], name)

    def test_research_citations_must_match_recorded_findings(self):
        design = researched_design()
        design["stages"]["framework"]["items"][1]["sources"][0]["passage"] = "A paraphrase that is not the recorded summary."
        self.assertTrue(any("exact summary" in e for e in self.errors(design)))
        design = researched_design()
        design["stages"]["framework"]["items"][1]["sources"][0]["file"] = "RS9"
        self.assertTrue(any("RS ID" in e for e in self.errors(design)))
        design = researched_design()
        design["research"]["findings"][0]["usedBy"] = ["F2", "T404"]
        self.assertTrue(any("missing item or assumption ID T404" in e for e in self.errors(design)))
        design = researched_design()
        design["research"]["findings"][0]["url"] = "ftp://example.test/x"
        self.assertTrue(any("research.findings[0].url" in e for e in self.errors(design)))
        design = researched_design()
        design["research"]["findings"].append(dict(FINDING))
        self.assertTrue(any("Duplicate research finding" in e for e in self.errors(design)))

    def test_unperformed_research_is_honest(self):
        design = researched_design()
        design["research"].update(performed=False, unavailableReason="")
        errs = self.errors(design)
        self.assertTrue(any("cannot carry findings" in e for e in errs))
        self.assertTrue(any("why no web research" in e for e in errs))
        design = fixtures.make_design()
        design["research"] = {"performed": False, "tool": "", "unavailableReason": "The host offered no web search tool in this session.", "queries": [], "findings": []}
        self.assertEqual(self.errors(design), [])
        design["research"]["performed"] = True
        self.assertTrue(any("Name the web search" in e for e in self.errors(design)))

    def test_tooling_cards_need_capability_candidates_and_backed_verification(self):
        design = researched_design()
        card = design["stages"]["framework"]["items"][1]["data"]
        card["capability"] = ""
        self.assertTrue(any("names the capability" in e for e in self.errors(design)))
        design = researched_design()
        design["stages"]["framework"]["items"][1]["data"]["candidates"] = []
        self.assertTrue(any("at least one candidate" in e for e in self.errors(design)))
        design = researched_design()
        design["stages"]["framework"]["items"][1]["data"]["candidates"][1]["verified"] = True
        self.assertTrue(any("verified candidate cites" in e for e in self.errors(design)))
        design = researched_design()
        design["stages"]["framework"]["items"][1]["data"]["candidates"][0]["sourceIds"] = ["RS7"]
        self.assertTrue(any("missing research finding RS7" in e for e in self.errors(design)))
        design = researched_design()
        design["stages"]["framework"]["items"][1]["data"]["candidates"][0]["kind"] = "vendor"
        self.assertTrue(any("candidates[0].kind" in e for e in self.errors(design)))


class RenderTests(unittest.TestCase):
    def test_html_shows_research_table_and_tooling_candidates_without_links(self):
        document = design_html.render_html(researched_design(), fixtures.make_review())
        self.assertIn("Research used", document)
        self.assertIn("host web search", document)
        self.assertIn("https://example.test/docs/pii-detection", document)
        self.assertNotIn('href="http', document)
        self.assertIn("Tools by capability", document)
        self.assertIn("guardrails and PII detection", document)
        self.assertIn("Example detection service", document)
        self.assertIn(">unverified<", document)
        self.assertIn(">RS1<", document)
        self.assertIn("Checked", document)

    def test_unperformed_research_and_legacy_designs_render_honestly(self):
        design = fixtures.make_design()
        design["research"] = {"performed": False, "tool": "", "unavailableReason": "No web tool in this host.", "queries": [], "findings": []}
        document = design_html.render_html(design, fixtures.make_review())
        self.assertIn("No web research was performed: No web tool in this host.", document)
        self.assertIn("tool candidates are unverified", document)
        legacy = design_html.render_html(fixtures.make_design(), fixtures.make_review())
        self.assertNotIn("Research used", legacy)
        self.assertNotIn("Tools by capability", legacy)

    def test_committed_example_html_matches_the_renderer(self):
        for name in ("telecom", "health-claims"):
            folder = ROOT / "examples" / name
            design = design_io.load_json(folder / "design.json")
            review = design_io.load_json(folder / "review.json")
            rounds = design_html.review_rounds_near(folder / "review.json")
            rendered = design_html.render_html(design, review, "standard", rounds)
            self.assertEqual(hashlib.sha256(rendered.encode("utf-8")).hexdigest(), hashlib.sha256((folder / "DESIGN.html").read_bytes()).hexdigest(), name)


class ExportTests(unittest.TestCase):
    def test_assumptions_export_lists_research(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            (folder / "design.json").write_text(json.dumps(researched_design()))
            (folder / "review.json").write_text(json.dumps(fixtures.make_review()))
            result = design_io.export_design(folder / "design.json", folder / "out", folder / "review.json", mode="standard")
            self.assertTrue(result["ok"], result)
            text = (folder / "out" / "_evidence" / "assumptions.md").read_text()
            self.assertIn("## Research used", text)
            self.assertIn("RS1 (tool: guardrails and PII, retrieved 2026-11-04)", text)
            self.assertIn("do not verify this organisation", text)


if __name__ == "__main__":
    unittest.main()
