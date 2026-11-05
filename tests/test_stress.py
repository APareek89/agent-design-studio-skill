"""The stress harness as a test: fifteen mutations, each with an expected outcome.

`evals/stress/mutate.py` bends the telecom example fifteen ways and was run by
hand. The outcomes are now pinned here, so a change that silently turns a
rejection into a render, or a render into a rejection, fails the suite.

Each mutation is listed in OUTCOMES with the behaviour v1.3 commits to. A
mutation with no entry fails the suite too: an outcome nobody wrote down is
not a decision, and docs/decisions.md records the ones that were judgement
calls rather than obvious.
"""

import copy
import importlib.util
import json
from pathlib import Path
import re
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills/agent-design-studio/scripts"
OUT = ROOT / "evals/stress/out"
REVIEW = ROOT / "examples/telecom/review.json"


def module(name, prefix="st_"):
    spec = importlib.util.spec_from_file_location(prefix + name, SCRIPTS / (name + ".py"))
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


design_io = module("design_io")
design_html = module("design_html")


def has_pdf_tools():
    try:
        import reportlab  # noqa: F401
        import pypdf  # noqa: F401
    except ImportError:
        return False
    return True


# verdict: "renders" or "rejected".
# says: text the rejection message must contain, or the render must not drop.
OUTCOMES = {
    "01_xss_strings": {
        "verdict": "renders",
        "why": "Script tags and event handlers in a brief are content, and are escaped.",
    },
    "02_unicode_scripts": {
        "verdict": "renders",
        "why": "Devanagari and Arabic render in HTML and PDF with the text intact.",
    },
    "03_very_long_labels": {
        "verdict": "renders",
        "why": "A 350-character edge predicate wraps; no plate overlaps another plate or a node.",
    },
    "04_twelve_design_calls": {
        "verdict": "rejected",
        "says": "maxItems=5",
        "why": "The Decision brief holds at most five design calls; twelve is not a reader layer.",
    },
    "05_zero_fmea": {
        "verdict": "rejected",
        "says": "minItems=1",
        "why": "A design with no risk register has not been through the risk step.",
    },
    "06_zero_models_all_code": {
        "verdict": "rejected",
        "says": "model",
        "why": ("Not listed in the v1.3 brief. Emptying the model stage leaves components that declare "
                "a model with nothing to bind to, which is a real error; recorded in docs/decisions.md."),
    },
    "07_duplicate_ids": {
        "verdict": "rejected",
        "says": "Duplicate item ID",
        "why": "Two items with one ID make every cross-reference ambiguous.",
    },
    "08_cycle_back_edge": {
        "verdict": "renders",
        "why": "A retry loop is a legitimate workflow; the router draws it as a back edge on a rail.",
    },
    "09_rpn_extremes": {
        "verdict": "rejected",
        "says": "below 1",
        "why": "Severity, occurrence and detection are 1 to 10; 0 and -1 are not scores.",
    },
    "10_deep_task_tree": {
        "verdict": "rejected",
        "says": "exceeds the limit of 3 levels",
        "why": "The message names the depth limit, so an author knows what to flatten to.",
    },
    "11_twelve_top_tasks": {
        "verdict": "rejected",
        "says": "Leaf task has no serving component",
        "why": "A leaf nothing implements is a gap in the design, not a layout problem.",
    },
    "12_fan_out_eight": {
        "verdict": "renders",
        "why": "Eight exits from one node route through one gutter with no plate collisions.",
    },
    "13_no_presentation_1_1": {
        "verdict": "renders",
        "why": "The reader layer is derived from the ten stages, with nothing cut mid-sentence.",
    },
    "14_huge_brief": {
        "verdict": "renders",
        "why": "A 60 KB brief is quoted in the build overview, so the standard export passes.",
    },
    "15_empty_strings": {
        "verdict": "rejected",
        "says": "Does not match any allowed schema",
        "why": "An empty task title is not a task.",
    },
}


def load(name):
    return design_io.load_json(OUT / name / "design.json")


class EveryMutationIsAccountedFor(unittest.TestCase):
    def test_the_harness_and_the_expectations_agree(self):
        on_disk = {p.name for p in OUT.iterdir() if p.is_dir() and (p / "design.json").is_file()}
        self.assertEqual(on_disk, set(OUTCOMES),
                         "every mutation needs a recorded expected outcome, and every expectation a mutation")
        self.assertEqual(len(OUTCOMES), 15)

    def test_every_expectation_says_why(self):
        for name, row in OUTCOMES.items():
            with self.subTest(mutation=name):
                self.assertIn(row["verdict"], ("renders", "rejected"))
                self.assertGreater(len(row["why"].split()), 6, "an expectation states its reason")

    def test_the_mutator_still_produces_these_fifteen(self):
        source = (ROOT / "evals/stress/mutate.py").read_text(encoding="utf-8")
        declared = set(re.findall(r'@variant\("([^"]+)"\)', source))
        self.assertEqual(declared, set(OUTCOMES),
                         "a new mutation must be given an expected outcome here")


class Verdicts(unittest.TestCase):
    """Does each mutation validate, and does a rejection say the right thing?"""

    def test_each_mutation_matches_its_expected_verdict(self):
        for name, row in OUTCOMES.items():
            with self.subTest(mutation=name):
                result = design_io.validate_design(load(name))
                expected = row["verdict"] == "renders"
                self.assertEqual(result["valid"], expected,
                                 "%s: expected %s (%s). First errors: %s"
                                 % (name, row["verdict"], row["why"], result["errors"][:2]))

    def test_each_rejection_says_what_is_wrong(self):
        for name, row in OUTCOMES.items():
            if row["verdict"] != "rejected":
                continue
            with self.subTest(mutation=name):
                errors = design_io.validate_design(load(name))["errors"]
                text = " ".join(e["message"] for e in errors)
                self.assertIn(row["says"], text, "%s: %s" % (name, row["why"]))


class Renders(unittest.TestCase):
    def setUp(self):
        self.review = design_io.load_json(REVIEW)
        self.rendering = [n for n, r in OUTCOMES.items() if r["verdict"] == "renders"]

    def html(self, name):
        return design_html.render_html(load(name), self.review)

    def test_every_rendering_mutation_produces_html(self):
        for name in self.rendering:
            with self.subTest(mutation=name):
                self.assertIn("<section data-view=", self.html(name))

    def test_script_tags_in_a_brief_are_escaped(self):
        document = self.html("01_xss_strings")
        self.assertNotIn("<script>alert(1)", document)
        self.assertNotIn("<img src=x onerror", document)
        self.assertIn("&lt;script&gt;alert(1)", document)

    def test_the_derived_brief_cuts_nothing(self):
        document = self.html("13_no_presentation_1_1")
        brief = re.search(r'<section data-view="brief".*?</section>', document, re.S).group(0)
        self.assertNotIn("...", re.sub(r"<[^>]+>", "", brief))

    def test_no_rendering_mutation_has_a_plate_collision(self):
        rect = re.compile(r'<rect class="wf-elbl-bg" x="(-?[\d.]+)" y="(-?[\d.]+)" '
                          r'width="([\d.]+)" height="([\d.]+)"')
        node = re.compile(r'<g class="wf-node[^"]*" data-node="([^"]+)"[^>]*>'
                          r'<rect x="(-?[\d.]+)" y="(-?[\d.]+)" width="([\d.]+)" height="([\d.]+)"')

        def area(a, b):
            dx = min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0])
            dy = min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1])
            return dx * dy if dx > 0 and dy > 0 else 0.0

        for name in self.rendering:
            with self.subTest(mutation=name):
                svg = re.search(r"<svg.*?</svg>", self.html(name), re.S).group(0)
                plates = [tuple(float(v) for v in m.groups()) for m in rect.finditer(svg)]
                nodes = [tuple(float(v) for v in m.groups()[1:]) for m in node.finditer(svg)]
                for i, a in enumerate(plates):
                    for b in plates[i + 1:]:
                        self.assertEqual(area(a, b), 0.0, "%s: two plates overlap" % name)
                    for b in nodes:
                        self.assertEqual(area(a, b), 0.0, "%s: a plate overlaps a node" % name)


class HugeBriefExport(unittest.TestCase):
    def test_the_standard_export_passes(self):
        folder = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, folder, True)
        (folder / "design.json").write_text(json.dumps(load("14_huge_brief")), encoding="utf-8")
        (folder / "review.json").write_text((REVIEW).read_text(encoding="utf-8"), encoding="utf-8")
        result = design_io.export_design(folder / "design.json", folder / "out",
                                         folder / "review.json", "standard")
        self.assertTrue(result["ok"], result.get("errors"))


@unittest.skipUnless(has_pdf_tools(), "ReportLab is not installed")
class UnicodePdf(unittest.TestCase):
    def test_the_hindi_text_survives_into_the_pdf(self):
        from pypdf import PdfReader

        design_pdf = module("design_pdf")
        folder = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, folder, True)
        out = folder / "DESIGN.pdf"
        result = design_pdf.create_pdf(OUT / "02_unicode_scripts/design.json", REVIEW, out, "standard")
        self.assertTrue(result["ok"], result)
        text = PdfReader(str(out)).pages[0].extract_text()
        self.assertIn("हिंदी", text)
        self.assertEqual(len(result["fontWarnings"]), 1, "the glyphs with no font are reported once")


if __name__ == "__main__":
    unittest.main()
