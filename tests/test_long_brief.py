"""A 60 KB brief must not break the standard export.

`build/00-overview.md` used to copy the whole brief, which broke the 25 KB
per-file cap and reported it as "split milestones" - advice that could not
help, because the milestones were not the problem. The overview now quotes the
brief's opening and points at design.json, the HTML collapses a long brief
behind a control, and the full PDF carries it as an appendix. Nothing is ever
dropped to fit a limit.
"""

import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills/agent-design-studio/scripts"
HUGE = ROOT / "evals/stress/out/14_huge_brief/design.json"
REVIEW = ROOT / "examples/telecom/review.json"


def module(name):
    spec = importlib.util.spec_from_file_location("lb_" + name, SCRIPTS / (name + ".py"))
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


design_io = module("design_io")
design_html = module("design_html")
export_v2 = module("export_v2")


def has_reportlab():
    try:
        import reportlab  # noqa: F401
        import pypdf  # noqa: F401
    except ImportError:
        return False
    return True


class HugeBriefExport(unittest.TestCase):
    def setUp(self):
        self.design = design_io.load_json(HUGE)
        self.review = design_io.load_json(REVIEW)
        self.folder = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.folder, True)
        self.assertGreater(len(self.design["brief"]), 50000, "this fixture must carry a long brief")

    def export(self, mode):
        out = self.folder / mode
        (self.folder / "design.json").write_text(json.dumps(self.design), encoding="utf-8")
        (self.folder / "review.json").write_text(json.dumps(self.review), encoding="utf-8")
        return design_io.export_design(
            self.folder / "design.json", out, self.folder / "review.json", mode), out

    def test_standard_export_passes_with_a_sixty_kilobyte_brief(self):
        result, out = self.export("standard")
        self.assertTrue(result["ok"], result.get("errors"))
        self.assertTrue((out / "build/00-overview.md").is_file())

    def test_the_overview_quotes_the_brief_and_points_at_the_source(self):
        _, out = self.export("standard")
        overview = (out / "build/00-overview.md").read_text(encoding="utf-8")
        self.assertLessEqual(len(overview.encode()), export_v2.FILE_LIMIT)
        self.assertIn(self.design["brief"][:200], overview, "the opening is quoted verbatim")
        quote, trimmed = export_v2.quote_brief(self.design["brief"])
        self.assertTrue(trimmed)
        self.assertIn(quote, overview)
        self.assertLess(len(overview), len(self.design["brief"]) / 10, "the brief is quoted, not copied")
        self.assertIn("design.json -> brief", overview)

    def test_an_ordinary_brief_reaches_the_overview_whole(self):
        design = design_io.load_json(ROOT / "examples/telecom/design.json")
        review = design_io.load_json(REVIEW)
        (self.folder / "design.json").write_text(json.dumps(design), encoding="utf-8")
        (self.folder / "review.json").write_text(json.dumps(review), encoding="utf-8")
        out = self.folder / "ordinary"
        result = design_io.export_design(self.folder / "design.json", out, self.folder / "review.json", "standard")
        self.assertTrue(result["ok"], result.get("errors"))
        overview = (out / "build/00-overview.md").read_text(encoding="utf-8")
        self.assertIn(design["brief"], overview)
        self.assertNotIn("[...]", overview)


class SizeErrorMessage(unittest.TestCase):
    def test_the_error_names_the_file_and_the_field_that_caused_it(self):
        design = design_io.load_json(HUGE)
        files = {"build/00-overview.md": "x" * 30000}
        message = export_v2.size_error(files, list(files), 30000, design)
        self.assertIn("build/00-overview.md", message)
        self.assertIn("$.brief", message)
        self.assertIn("30,000 bytes", message)
        self.assertNotIn("Split milestones", message)

    def test_a_total_overrun_is_reported_separately(self):
        design = design_io.load_json(HUGE)
        files = {"build/01-milestone.md": "x" * 20000, "build/02-milestone.md": "y" * 90000}
        message = export_v2.size_error(files, [], 110000, design)
        self.assertIn("110,000 bytes", message)
        self.assertIn("over the 100 KB total", message)


class QuoteBrief(unittest.TestCase):
    def test_a_quote_ends_on_a_word_and_says_it_was_cut(self):
        text = "word " * 2000
        quote, trimmed = export_v2.quote_brief(text)
        self.assertTrue(trimmed)
        self.assertTrue(quote.endswith("[...]"))
        self.assertLessEqual(len(quote), export_v2.BRIEF_QUOTE_BYTES + 10)
        self.assertTrue(text.startswith(quote[: -len(" [...]")]))

    def test_a_short_brief_is_returned_unchanged(self):
        self.assertEqual(export_v2.quote_brief("short brief"), ("short brief", False))


class LongBriefInTheHtml(unittest.TestCase):
    def setUp(self):
        self.design = design_io.load_json(HUGE)
        self.review = design_io.load_json(REVIEW)
        self.document = design_html.render_html(self.design, self.review)

    def test_a_long_brief_is_collapsed_behind_a_control(self):
        self.assertIn("Show full brief", self.document)
        self.assertIn("<details class=\"brief-full\"", self.document)

    def test_the_whole_brief_is_still_in_the_page(self):
        tail = design_html.esc(self.design["brief"][-150:])
        self.assertIn(tail, self.document, "collapsed, not cut")

    def test_a_short_brief_has_no_control(self):
        panel = design_html.brief_panel("A short brief about telecom complaints.")
        self.assertNotIn("Show full brief", panel)
        self.assertIn("A short brief about telecom complaints.", panel)

    def test_the_collapsed_panel_holds_the_text_in_full(self):
        text = "sentence. " * 400
        panel = design_html.brief_panel(text)
        self.assertIn("Show full brief", panel)
        self.assertIn(design_html.esc(text), panel)


@unittest.skipUnless(has_reportlab(), "ReportLab is not installed")
class LongBriefInThePdf(unittest.TestCase):
    def render(self, mode):
        from pypdf import PdfReader

        design_pdf = module("design_pdf")
        folder = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, folder, True)
        out = folder / "DESIGN.pdf"
        result = design_pdf.create_pdf(HUGE, REVIEW, out, mode)
        self.assertTrue(result["ok"], result)
        reader = PdfReader(str(out))
        return "\n".join(page.extract_text() for page in reader.pages)

    def test_the_full_pdf_carries_the_brief_as_an_appendix(self):
        text = self.render("full")
        self.assertIn("The brief in full", text)
        brief = design_io.load_json(HUGE)["brief"]
        self.assertIn(" ".join(brief[-80:].split()), " ".join(text.split()))

    def test_the_standard_pdf_quotes_it_and_has_no_appendix(self):
        text = self.render("standard")
        self.assertNotIn("The brief in full", text)


if __name__ == "__main__":
    unittest.main()
