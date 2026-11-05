"""The read-only seed example: a worked design from a brief that never writes.

The telecom and health-claims examples both write, so until v1.3 nothing
exercised the read-only profile end to end. This seed does, and these tests
hold it to the same bar as the other two: it validates, it passes strict
coverage, its semantic contract verifies, and its review is honestly a
self-review.

They also prove the profile rules are doing work rather than passing
vacuously: removing the answer goldens must make SEM008 fire, and removing the
read-only risk families must make COV17 fail.
"""

import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills/agent-design-studio/scripts"
SEED = ROOT / "evals/seeds/read-only-qa"


def module(name, prefix="ro_"):
    spec = importlib.util.spec_from_file_location(prefix + name, SCRIPTS / (name + ".py"))
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


design_io = module("design_io")
design_html = module("design_html")
semantic_checks = module("semantic_checks")


class SeedIsValid(unittest.TestCase):
    def setUp(self):
        self.design = design_io.load_json(SEED / "design.json")
        self.review = design_io.load_json(SEED / "review.json")

    def test_it_validates_with_a_verified_semantic_contract(self):
        result = design_io.validate_design(self.design)
        self.assertTrue(result["valid"], result["errors"][:3])
        self.assertEqual(result["semanticCoverage"], "verified-declarations")
        self.assertEqual(result["warnings"], [])

    def test_it_has_no_missing_required_coverage(self):
        coverage = design_io.validate_design(self.design)["coverage"]
        self.assertEqual(coverage["missingRequired"], [])
        self.assertEqual(coverage["missingRecommended"], [])

    def test_its_review_is_valid_and_passes(self):
        structural = design_io.validate_design(self.design)["valid"]
        result = design_io.validate_review(self.review, structural)
        self.assertTrue(result["valid"], result["errors"][:3])
        self.assertEqual(result["status"], "pass")

    def test_the_review_is_honestly_a_self_review(self):
        self.assertEqual(self.review["method"], "self-review")
        text = " ".join(self.review["limitations"])
        self.assertNotIn("independent", text.lower())
        self.assertIn("self-review", text)
        self.assertIn("No separate reviewing agent", text)

    def test_the_review_keeps_its_unresolved_issues(self):
        unresolved = [i for i in self.review["issues"] if not i["resolved"]]
        self.assertTrue(unresolved, "a review with nothing left open is not a review")
        self.assertTrue(all(i["severity"] == "minor" for i in unresolved),
                        "an unresolved major would make the pass unsupported")


class SeedIsReadOnly(unittest.TestCase):
    def setUp(self):
        self.design = design_io.load_json(SEED / "design.json")

    def test_the_profile_says_it_writes_nothing(self):
        self.assertTrue(design_io.is_read_only(self.design))
        self.assertFalse(design_io.is_realtime(self.design))
        self.assertFalse(design_io.is_multi_tenant(self.design))

    def test_there_is_no_write_node_and_no_write_action(self):
        semantics = self.design["semantics"]
        self.assertEqual([n for n in semantics["nodes"] if n["kind"] == "write"], [])
        self.assertEqual(semantics["writeActions"], [])
        effects = {e["componentId"]: e["effect"] for e in semantics["componentEffects"]}
        self.assertNotIn("write", effects.values())
        self.assertIn("read", effects.values(), "something must read the library")

    def test_it_carries_the_answer_golden_pair(self):
        answers = [g for g in self.design["semantics"]["goldens"] if g["actionClass"] == "answer"]
        self.assertEqual({g["polarity"] for g in answers}, {"positive", "negative"})
        for golden in answers:
            self.assertTrue(golden["citationField"])
            self.assertIsInstance(golden["fixture"]["expected"]["citations"], int)

    def test_every_read_only_risk_family_is_in_the_register(self):
        self.assertEqual(design_io.read_only_risk_gaps(self.design), [])

    def test_the_decision_brief_reads_as_answers_not_actions(self):
        review = design_io.load_json(SEED / "review.json")
        document = design_html.render_html(self.design, review)
        brief = document[document.find('data-view="brief"'):]
        brief = brief[: brief.find("</section>")]
        self.assertIn("Answers with citation", brief)
        self.assertNotIn("Acts alone", brief)


class TheRulesAreDoingWork(unittest.TestCase):
    """Remove what the profile requires, and the profile must notice."""

    def setUp(self):
        self.design = design_io.load_json(SEED / "design.json")

    def test_removing_the_answer_goldens_fires_sem008(self):
        broken = copy.deepcopy(self.design)
        answers = {g["evalId"] for g in broken["semantics"]["goldens"] if g["actionClass"] == "answer"}
        broken["semantics"]["goldens"] = [g for g in broken["semantics"]["goldens"]
                                          if g["actionClass"] != "answer"]
        broken["stages"]["evals"]["items"] = [e for e in broken["stages"]["evals"]["items"]
                                              if e["id"] not in answers]
        errors = [e for e in semantic_checks.validate_semantics(broken) if e.get("ruleId") == "SEM008"]
        self.assertTrue(errors, "SEM008 must fire when the answer goldens go")

    def test_removing_the_risk_families_fails_cov17(self):
        broken = copy.deepcopy(self.design)
        for card in broken["stages"]["fmea"]["items"]:
            card["description"] = "A risk."
            card["title"] = "A risk"
            card["data"]["control"] = "A control."
            card["data"]["action"] = "An action."
        gaps = design_io.read_only_risk_gaps(broken)
        self.assertEqual(len(gaps), 6, "every read-only family should be reported missing")

    def test_a_golden_without_a_read_source_fires_sem008(self):
        broken = copy.deepcopy(self.design)
        broken["semantics"]["componentEffects"] = [
            dict(e, effect="none") for e in broken["semantics"]["componentEffects"]]
        errors = [e for e in semantic_checks.validate_semantics(broken) if e.get("ruleId") == "SEM008"]
        self.assertTrue(any("effect is read" in e["message"] for e in errors), errors)


class SeedIsReproducible(unittest.TestCase):
    def test_the_author_script_is_committed_beside_the_design(self):
        script = SEED / "author_design.py"
        self.assertTrue(script.is_file())
        self.assertIn("def build_semantics", script.read_text(encoding="utf-8"))

    def test_the_run_report_records_a_degraded_host(self):
        report = json.loads((SEED / "run-report.json").read_text(encoding="utf-8"))
        self.assertFalse(report["hostCapabilities"]["subAgent"])
        self.assertFalse(report["hostCapabilities"]["webSearch"])
        self.assertIn("self-review (no separate agent available)", report["runConditions"])

    def test_the_research_record_says_no_tool_was_offered(self):
        design = design_io.load_json(SEED / "design.json")
        self.assertFalse(design["research"]["performed"])
        self.assertIn("No web search tool", design["research"]["unavailableReason"])
        self.assertTrue(all(
            not c["verified"]
            for f in design["stages"]["framework"]["items"]
            for c in f["data"].get("candidates", [])),
            "with no research, no candidate may be marked verified")


if __name__ == "__main__":
    unittest.main()
