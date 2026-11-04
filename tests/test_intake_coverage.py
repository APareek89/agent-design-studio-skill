"""Intake questions, expected-information coverage and the install script.

Synthetic fixtures only. The intake analyzer never asks a question itself; the
coverage report looks for expected information and never judges its quality.
"""

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills/agent-design-studio/scripts"


def module(name):
    spec = importlib.util.spec_from_file_location("ic_" + name, SCRIPTS / (name + ".py"))
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


design_io = module("design_io")
design_html = module("design_html")
intake = module("design_intake")
fixture_spec = importlib.util.spec_from_file_location("ic_fixtures", ROOT / "tests/test_design_io.py")
fixtures = importlib.util.module_from_spec(fixture_spec)
fixture_spec.loader.exec_module(fixtures)

TELECOM_BRIEF = design_io.load_json(ROOT / "examples/telecom/design.json")["brief"]
FULL_BRIEF = (
    "Design a complaint assistant for an Indian telecom provider under TRAI rules and the DPDP Act. Customers write in English and Hinglish through app chat "
    "and WhatsApp. About 10,000 complaints per month. Staff approve every refund; the assistant may explain and raise tickets alone. "
    "Facts come from the billing API and the CRM. Target: first-contact resolution from 45% to 70%. Run it on AWS."
)


class IntakeTests(unittest.TestCase):
    def test_minimal_brief_asks_autonomy_first_and_at_most_four(self):
        result = intake.analyze("Help staff triage support requests and draft replies.")
        self.assertFalse(result["complete"])
        self.assertLessEqual(len(result["ask"]), 4)
        self.assertEqual(result["ask"][0]["topic"], "autonomy")
        self.assertEqual(result["ask"][0]["id"], "Q1")
        for q in result["ask"]:
            self.assertEqual(q["options"][-1], intake.ASSUME)
            self.assertTrue(q["why"])
        self.assertIn("optional", result["note"])
        self.assertEqual(len(intake.analyze("x", limit=2)["ask"]), 2)

    def test_detailed_briefs_ask_less_and_complete_briefs_ask_nothing(self):
        telecom = intake.analyze(TELECOM_BRIEF)
        self.assertNotIn("autonomy", [g["topic"] for g in telecom["gaps"]])
        self.assertNotIn("users", [g["topic"] for g in telecom["gaps"]])
        self.assertIn("volume", [g["topic"] for g in telecom["gaps"]])
        full = intake.analyze(FULL_BRIEF)
        self.assertTrue(full["complete"], full["gaps"])
        self.assertEqual(full["ask"], [])

    def test_cli_reads_stdin_and_rejects_empty_brief(self):
        done = subprocess.run([sys.executable, str(SCRIPTS / "design_intake.py"), "questions", "-"], input="Route invoices to approvers.", capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stderr)
        payload = json.loads(done.stdout)
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["ask"])
        empty = subprocess.run([sys.executable, str(SCRIPTS / "design_intake.py"), "questions", "-"], input="   ", capture_output=True, text=True)
        self.assertEqual(empty.returncode, 1)
        self.assertIn("ask only for the brief", empty.stderr)


def with_intake(design):
    design = copy.deepcopy(design)
    design["intake"] = {
        "asked": True,
        "tool": "AskUserQuestion",
        "questions": [
            {"id": "Q1", "topic": "autonomy", "question": "Which actions may the system complete on its own?", "answer": "Explain only; staff do every action.", "source": "user"},
            {"id": "Q2", "topic": "volume", "question": "Roughly how many cases per month?", "answer": "", "source": "skipped"},
        ],
    }
    design["stages"]["context"]["items"][0]["sources"].append({"type": "context", "file": "user-intake", "passage": "Explain only; staff do every action."})
    return design


class IntakeValidationTests(unittest.TestCase):
    def errors(self, design):
        return [e["path"] + ": " + e["message"] for e in design_io.validate_design(design)["errors"]]

    def test_user_answers_are_citable_facts(self):
        design = with_intake(fixtures.make_design())
        self.assertEqual(self.errors(design), [])
        design["stages"]["context"]["items"][0]["sources"][-1]["passage"] = "A paraphrase."
        self.assertTrue(any("exact user answer" in e for e in self.errors(design)))
        design = with_intake(fixtures.make_design())
        design["intake"]["questions"][0]["answer"] = ""
        self.assertTrue(any("user's words" in e for e in self.errors(design)))
        design = with_intake(fixtures.make_design())
        design["intake"]["tool"] = ""
        self.assertTrue(any("question dialog" in e for e in self.errors(design)))
        design = with_intake(fixtures.make_design())
        design["intake"]["questions"][0]["source"] = "guessed"
        self.assertTrue(any("intake.questions[0].source" in e for e in self.errors(design)))

    def test_html_and_assumptions_show_what_the_user_added(self):
        design = with_intake(fixtures.make_design())
        document = design_html.render_html(design, fixtures.make_review())
        self.assertIn("What the user added", document)
        self.assertIn("Explain only; staff do every action.", document)
        self.assertIn("skipped; became an assumption", document)
        self.assertNotIn("What the user added", design_html.render_html(fixtures.make_design(), fixtures.make_review()))
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            (folder / "design.json").write_text(json.dumps(design))
            (folder / "review.json").write_text(json.dumps(fixtures.make_review()))
            self.assertTrue(design_io.export_design(folder / "design.json", folder / "out", folder / "review.json", mode="standard")["ok"])
            text = (folder / "out/_evidence/assumptions.md").read_text()
            self.assertIn("## What the user added", text)
            self.assertIn("Q2 Roughly how many cases per month? — skipped", text)
            readme = (folder / "out/README.md").read_text()
            self.assertIn("## Expected information", readme)
            self.assertIn("required items covered", readme)


class CoverageTests(unittest.TestCase):
    def test_fixture_gaps_are_findings_not_errors_and_can_be_justified(self):
        design = fixtures.make_design()
        result = design_io.validate_design(design)
        self.assertTrue(result["valid"])
        cov = result["coverage"]
        self.assertIn("COV9", cov["missingRequired"])
        self.assertIn("COV7", cov["missingRequired"])
        self.assertTrue(any(w["path"] == "$.coverage.COV9" for w in result["warnings"]))
        design["stages"]["context"]["assumptions"].append("COV9: the host offered no web search tool in this session.")
        cov = design_io.validate_design(design)["coverage"]
        self.assertNotIn("COV9", cov["missingRequired"])
        self.assertIn("COV9", cov["justified"])
        self.assertEqual([c for c in cov["checks"] if c["id"] == "COV9"][0]["evidence"], "the host offered no web search tool in this session.")
        ids = [c["id"] for c in cov["checks"]]
        self.assertEqual(ids, ["COV" + str(i) for i in range(1, 16)])

    def test_capability_and_write_hints_from_the_brief(self):
        design = fixtures.make_design()
        design["brief"] = "Design a voice assistant that answers calls about refunds using our knowledge base."
        for packet in design["stages"].values():
            for item in packet["items"]:
                for source in item["sources"]:
                    if source["type"] == "context":
                        source["passage"] = design["brief"]
        design["stages"]["context"]["items"][0]["data"]["value"] = design["brief"]
        cov = design_io.validate_design(design)["coverage"]
        cov10 = [c for c in cov["checks"] if c["id"] == "COV10"][0]
        self.assertEqual(cov10["status"], "missing")
        self.assertIn("voice and telephony", cov10["evidence"])
        self.assertIn("retrieval and embeddings", cov10["evidence"])
        cov11 = [c for c in cov["checks"] if c["id"] == "COV11"][0]
        self.assertEqual(cov11["status"], "missing")
        card = copy.deepcopy(design["stages"]["framework"]["items"][0])
        card["id"] = "F2"
        card["data"].update(category="tooling", capability="voice and telephony", candidates=[{"name": "Candidate A", "kind": "managed", "note": "not checked", "verified": False, "sourceIds": []}])
        design["stages"]["framework"]["items"].append(card)
        cov = design_io.validate_design(design)["coverage"]
        cov10 = [c for c in cov["checks"] if c["id"] == "COV10"][0]
        self.assertIn("Covered: voice and telephony", cov10["evidence"])
        self.assertIn("retrieval and embeddings", cov10["evidence"])
        self.assertEqual([c for c in cov["checks"] if c["id"] == "COV15"][0]["status"], "missing")

    def test_examples_report_coverage_and_strict_flag_exits_one(self):
        telecom = design_io.validate_design(design_io.load_json(ROOT / "examples/telecom/design.json"))
        self.assertTrue(telecom["valid"])
        self.assertEqual(telecom["coverage"]["missingRequired"], ["COV9"])
        self.assertEqual([c for c in telecom["coverage"]["checks"] if c["id"] == "COV11"][0]["status"], "covered")
        strict = subprocess.run([sys.executable, str(SCRIPTS / "design_io.py"), "validate", str(ROOT / "examples/telecom/design.json"), "--strict-coverage"], capture_output=True, text=True)
        self.assertEqual(strict.returncode, 1)
        self.assertEqual(json.loads(strict.stdout)["status"], "coverage-gaps")
        plain = subprocess.run([sys.executable, str(SCRIPTS / "design_io.py"), "validate", str(ROOT / "examples/telecom/design.json")], capture_output=True, text=True)
        self.assertEqual(plain.returncode, 0)
        report = subprocess.run([sys.executable, str(SCRIPTS / "design_io.py"), "coverage", str(ROOT / "examples/telecom/design.json")], capture_output=True, text=True)
        self.assertEqual(report.returncode, 1)
        self.assertFalse(json.loads(report.stdout)["ok"])


class InstallScriptTests(unittest.TestCase):
    def test_install_copies_skill_and_backs_up_previous_copy(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "skills"
            first = subprocess.run(["sh", str(ROOT / "scripts/install_skill.sh"), "--dir", str(target)], capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertTrue((target / "agent-design-studio/SKILL.md").is_file())
            self.assertTrue((target / "agent-design-studio/scripts/design_intake.py").is_file())
            second = subprocess.run(["sh", str(ROOT / "scripts/install_skill.sh"), "--dir", str(target)], capture_output=True, text=True)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertIn("Backed up", second.stdout)
            self.assertEqual(len(list(target.glob("agent-design-studio.bak-*"))), 1)
            listing = subprocess.run(["sh", str(ROOT / "scripts/install_skill.sh"), "--list"], capture_output=True, text=True)
            self.assertEqual(listing.returncode, 0)
            self.assertIn(".claude/skills", listing.stdout)
            bad = subprocess.run(["sh", str(ROOT / "scripts/install_skill.sh"), "nosuchhost"], capture_output=True, text=True)
            self.assertNotEqual(bad.returncode, 0)


if __name__ == "__main__":
    unittest.main()
