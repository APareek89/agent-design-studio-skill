"""The intake brief classifier, checked on the seven edge briefs.

The classifier is a heuristic read of a brief's words. These tests assert only
what each brief settles unambiguously, which is what the host relies on when it
confirms the profile in one line.
"""

import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills/agent-design-studio/scripts"
EDGE = ROOT / "evals/briefs/edge"

spec = importlib.util.spec_from_file_location("bc_intake", SCRIPTS / "design_intake.py")
intake = importlib.util.module_from_spec(spec)
spec.loader.exec_module(intake)

EXPECTED = json.loads((EDGE / "expected.json").read_text(encoding="utf-8"))["briefs"]


def dotted(profile, path):
    value = profile
    for part in path.split("."):
        value = value[part]
    return value


class EdgeBriefClassification(unittest.TestCase):
    def test_every_edge_brief_matches_its_expected_profile(self):
        for name, expectation in EXPECTED.items():
            with self.subTest(brief=name):
                profile = intake.classify((EDGE / name).read_text(encoding="utf-8"))
                for path, want in expectation["expect"].items():
                    self.assertEqual(dotted(profile, path), want, f"{name}: {path} ({expectation['why']})")

    def test_every_edge_brief_raises_its_signal_with_a_message(self):
        for name, expectation in EXPECTED.items():
            with self.subTest(brief=name):
                profile = intake.classify((EDGE / name).read_text(encoding="utf-8"))
                raised = {s["id"] for s in profile["signals"]}
                for signal in expectation["signals"]:
                    self.assertIn(signal, raised, f"{name} should raise {signal}")
                for signal in profile["signals"]:
                    self.assertTrue(signal["detail"].strip(), "every signal carries a plain-language message")
                    self.assertGreater(len(signal["detail"].split()), 5, "a message is a sentence, not a label")
                self.assertEqual(profile["messages"], [s["detail"] for s in profile["signals"]])

    def test_conflicts_are_named_and_say_what_the_design_keeps(self):
        for name, expectation in EXPECTED.items():
            wanted = expectation.get("conflicts", [])
            with self.subTest(brief=name):
                profile = intake.classify((EDGE / name).read_text(encoding="utf-8"))
                self.assertEqual([c["id"] for c in profile["briefConflicts"]], wanted)
                for conflict in profile["briefConflicts"]:
                    self.assertTrue(conflict["designKeeps"].strip())
                    self.assertIn("Override needs a named owner", conflict["message"])

    def test_all_seven_briefs_are_covered(self):
        on_disk = {p.name for p in EDGE.glob("*.md")}
        self.assertEqual(on_disk, set(EXPECTED), "every edge brief has an expected profile")
        self.assertEqual(len(on_disk), 7)


class LanguageDetection(unittest.TestCase):
    def test_script_decides_a_non_latin_brief(self):
        cases = {
            "हमारे अस्पताल में शिकायतें": ("hi", "Devanagari"),
            "نظام لمعالجة شكاوى العملاء": ("ar", "Arabic"),
            "客户投诉处理系统设计": ("zh", "CJK"),
            "система обработки жалоб клиентов": ("ru", "Cyrillic"),
        }
        for text, (code, script) in cases.items():
            with self.subTest(script=script):
                found = intake.detect_language(text)
                self.assertEqual(found["code"], code)
                self.assertEqual(found["script"], script)

    def test_a_short_english_brief_is_not_mistaken_for_another_latin_language(self):
        # Shared function words ("a", "per", "e") used to flip short English
        # briefs to Portuguese or Italian.
        for text in (
            "Design a trading agent that executes equity orders autonomously up to USD 1M per order.",
            "An assistant that answers questions from our internal reports and cites the page.",
            "Build an agent to triage support tickets per team and route each one to an owner.",
        ):
            with self.subTest(text=text[:40]):
                self.assertEqual(intake.detect_language(text)["code"], "en")

    def test_a_brief_with_no_letters_is_undetermined(self):
        found = intake.detect_language("")
        self.assertEqual(found["code"], "und")
        self.assertEqual(found["confidence"], "low")


class ShapeSignals(unittest.TestCase):
    def test_a_deliverable_is_not_a_write_to_a_system_of_record(self):
        for text in (
            "Write a Python script that scrapes competitor prices nightly and emails me a CSV.",
            "Create a weekly sales report for the team.",
        ):
            with self.subTest(text=text[:30]):
                self.assertFalse(intake.classify(text)["writes"])

    def test_a_real_write_is_detected(self):
        self.assertTrue(intake.classify(
            "An agent that issues refunds to customers up to 500 rupees and closes the ticket.")["writes"])

    def test_realtime_and_multitenant_are_detected(self):
        profile = intake.classify(
            "A voice agent on our IVR for each tenant of our white-label SaaS; latency under 800ms.")
        self.assertTrue(profile["realtime"])
        self.assertTrue(profile["multiTenant"])

    def test_a_thin_brief_names_the_lite_fallback(self):
        profile = intake.classify("build me an agent")
        thin = next(s for s in profile["signals"] if s["id"] == "thin")
        self.assertIn("lite", thin["detail"])
        self.assertIn("thin brief", thin["detail"])

    def test_profile_starts_unconfirmed(self):
        profile = intake.classify("An agent that triages support tickets for 2000 customers a day.")
        self.assertFalse(profile["confirmed"])
        self.assertEqual(profile["overriddenBy"], "")


if __name__ == "__main__":
    unittest.main()
