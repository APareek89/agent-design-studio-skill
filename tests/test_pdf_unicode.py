"""Non-Latin text in the PDF renders as text, never as black squares.

ReportLab's base fonts are Latin-1, so Devanagari, Arabic, Chinese and emoji
used to come out as filled boxes with nothing to tell the reader they had. The
skill now ships the Noto Sans family and picks a font per character.

What these tests hold the renderer to:
  * every character the fonts cover survives into the PDF's text layer;
  * every character no font covers becomes '?' and one warning line, never a
    silent box.
"""

import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills/agent-design-studio/scripts"
FONTS = ROOT / "skills/agent-design-studio/fonts"
STRESS = ROOT / "evals/stress/out/02_unicode_scripts/design.json"
REVIEW = ROOT / "examples/telecom/review.json"

HINDI = "हिंदी"            # हिंदी
HINDI_COMPLAINT = "शिकायत"   # शिकायत
ARABIC = "العربية"      # العربية
CHINESE = "中文"
ROCKET = "\U0001F680"


def module(name):
    spec = importlib.util.spec_from_file_location("pu_" + name, SCRIPTS / (name + ".py"))
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


design_pdf = module("design_pdf")
design_fonts = module("design_fonts")


def has_reportlab():
    try:
        import reportlab  # noqa: F401
        import pypdf  # noqa: F401
    except ImportError:
        return False
    return True


class ShippedFonts(unittest.TestCase):
    def test_the_core_noto_fonts_are_in_the_repository(self):
        for name, filename in design_fonts.CORE_FONTS:
            with self.subTest(font=name):
                self.assertTrue((FONTS / filename).is_file(), f"{filename} must ship with the skill")

    def test_the_licence_ships_with_them(self):
        licence = FONTS / "OFL.txt"
        self.assertTrue(licence.is_file())
        self.assertIn("SIL Open Font License", licence.read_text(encoding="utf-8"))

    @unittest.skipUnless(has_reportlab(), "ReportLab is not installed")
    def test_devanagari_and_arabic_route_to_their_own_font(self):
        fonts = design_fonts.register()
        self.assertTrue(fonts.unicode, "the Noto family must load from fonts/")
        picked = dict((font, chunk) for font, chunk in fonts.runs("x " + HINDI + " " + ARABIC))
        self.assertIn("StudioDevanagari", picked)
        self.assertIn("StudioArabic", picked)

    @unittest.skipUnless(has_reportlab(), "ReportLab is not installed")
    def test_a_glyph_no_font_covers_becomes_a_question_mark_and_a_warning(self):
        fonts = design_fonts.register()
        rendered = "".join(chunk for _, chunk in fonts.runs(CHINESE + ROCKET))
        self.assertEqual(rendered, "???")
        self.assertEqual(len(fonts.warnings), 1, "one warning line, not one per character")
        warning = fonts.warnings[0]
        self.assertIn("U+4E2D", warning)
        self.assertIn("U+1F680", warning)
        self.assertIn("'?'", warning)

    @unittest.skipUnless(has_reportlab(), "ReportLab is not installed")
    def test_a_covered_glyph_raises_no_warning(self):
        fonts = design_fonts.register()
        fonts.runs("Plain English, " + HINDI + ", " + ARABIC)
        self.assertEqual(fonts.warnings, [])


@unittest.skipUnless(has_reportlab(), "ReportLab is not installed")
class UnicodeStressRender(unittest.TestCase):
    """The 02_unicode_scripts stress variant, rendered and read back."""

    def render(self, mode):
        from pypdf import PdfReader

        folder = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, folder, True)
        out = folder / "DESIGN.pdf"
        result = design_pdf.create_pdf(STRESS, REVIEW, out, mode)
        self.assertTrue(result["ok"], result)
        return result, PdfReader(str(out)).pages[0].extract_text(), folder

    def test_standard_mode_keeps_the_hindi_words_on_page_one(self):
        _, text, _ = self.render("standard")
        self.assertIn(HINDI, text)
        self.assertIn(HINDI_COMPLAINT, text)

    def test_standard_mode_keeps_every_arabic_letter_on_page_one(self):
        # ReportLab reverses a right-to-left run so that drawing left to right
        # puts it on the page the right way round, so the text layer holds the
        # word in visual order. Every character survives either way; the
        # renderer does no Arabic shaping (see CHANGELOG).
        _, text, _ = self.render("standard")
        self.assertTrue(ARABIC in text or ARABIC[::-1] in text,
                        "every Arabic letter must reach the text layer")

    def test_full_mode_keeps_the_hindi_words_too(self):
        _, text, _ = self.render("full")
        self.assertIn(HINDI, text)

    def test_uncovered_glyphs_are_reported_not_hidden(self):
        result, text, _ = self.render("standard")
        self.assertEqual(len(result["fontWarnings"]), 1)
        self.assertIn("U+4E2D", result["fontWarnings"][0])
        self.assertNotIn(CHINESE, text, "an uncovered glyph is replaced, not drawn")
        self.assertIn("?", text)

    def test_the_warning_reaches_validation_json_beside_the_pdf(self):
        from pypdf import PdfReader  # noqa: F401

        folder = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, folder, True)
        manifest = folder / "validation.json"
        manifest.write_text(json.dumps({"warnings": ["an earlier warning"]}), encoding="utf-8")
        design_pdf.create_pdf(STRESS, REVIEW, folder / "DESIGN.pdf", "standard")
        warnings = json.loads(manifest.read_text(encoding="utf-8"))["warnings"]
        self.assertIn("an earlier warning", warnings, "existing warnings are kept")
        self.assertEqual(sum(1 for w in warnings if w.startswith("PDF fonts:")), 1)

    def test_re_rendering_does_not_stack_duplicate_font_warnings(self):
        folder = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, folder, True)
        manifest = folder / "validation.json"
        manifest.write_text(json.dumps({"warnings": []}), encoding="utf-8")
        for name in ("one.pdf", "two.pdf"):
            design_pdf.create_pdf(STRESS, REVIEW, folder / name, "standard")
        warnings = json.loads(manifest.read_text(encoding="utf-8"))["warnings"]
        self.assertEqual(sum(1 for w in warnings if w.startswith("PDF fonts:")), 1)


if __name__ == "__main__":
    unittest.main()
