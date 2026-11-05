#!/usr/bin/env python3
"""Unicode fonts for the PDF renderers.

ReportLab's base fonts are Latin-1 only, so Devanagari, Arabic, Chinese and
emoji came out as black squares. This module registers the Noto Sans family
that ships under `fonts/` and picks a font per character, so a brief written in
Hindi renders as Hindi rather than as boxes.

A character no registered font can draw is written as `?` and recorded in
`warnings`, which the renderers add to `validation.json`. A silent box is never
acceptable: either the text renders or the reader is told it did not.

Shipped (SIL Open Font License, see fonts/OFL.txt):
    NotoSans-Regular, NotoSans-Bold   Latin, Greek, Cyrillic, Devanagari
    NotoSansMono-Regular              monospace
    NotoSansDevanagari-Regular        Devanagari, preferred for that script
    NotoSansArabic-Regular            Arabic

Not shipped, used when dropped into `fonts/`: NotoSansCJK-Regular.ttf (its
~16 MB is more than this repository should carry) and any other
`NotoSans<Script>-Regular.ttf`.
"""

from __future__ import annotations

import html
from pathlib import Path

FONT_DIR = Path(__file__).resolve().parent.parent / "fonts"

# Registered name -> file name. The first three are required for the studio
# look; the rest are per-script fallbacks used only when present.
CORE_FONTS = (
    ("StudioBody", "NotoSans-Regular.ttf"),
    ("StudioBold", "NotoSans-Bold.ttf"),
    ("StudioMono", "NotoSansMono-Regular.ttf"),
)
SCRIPT_FONTS = (
    ("StudioDevanagari", "NotoSansDevanagari-Regular.ttf"),
    ("StudioArabic", "NotoSansArabic-Regular.ttf"),
    ("StudioCJK", "NotoSansCJK-Regular.ttf"),
    ("StudioBengali", "NotoSansBengali-Regular.ttf"),
    ("StudioTamil", "NotoSansTamil-Regular.ttf"),
    ("StudioThai", "NotoSansThai-Regular.ttf"),
    ("StudioHebrew", "NotoSansHebrew-Regular.ttf"),
)

# Which font to try first for a character, by Unicode block. Falls through to
# the body font, then to any other registered font, then to `?`.
BLOCK_PREFERENCE = (
    (0x0900, 0x097F, "StudioDevanagari"),
    (0x0980, 0x09FF, "StudioBengali"),
    (0x0B80, 0x0BFF, "StudioTamil"),
    (0x0590, 0x05FF, "StudioHebrew"),
    (0x0600, 0x06FF, "StudioArabic"),
    (0x0750, 0x077F, "StudioArabic"),
    (0x08A0, 0x08FF, "StudioArabic"),
    (0xFB50, 0xFDFF, "StudioArabic"),
    (0xFE70, 0xFEFF, "StudioArabic"),
    (0x0E00, 0x0E7F, "StudioThai"),
    (0x3000, 0x30FF, "StudioCJK"),
    (0x3400, 0x4DBF, "StudioCJK"),
    (0x4E00, 0x9FFF, "StudioCJK"),
    (0xAC00, 0xD7AF, "StudioCJK"),
    (0xF900, 0xFAFF, "StudioCJK"),
)

_REGISTERED = {}


class FontSet:
    """The fonts available to one render, and what they could not draw."""

    def __init__(self, body, bold, mono, coverage, unicode_ok):
        self.body = body
        self.bold = bold
        self.mono = mono
        self._coverage = coverage          # font name -> set of codepoints
        self._cache = {}
        self.unicode = unicode_ok          # True when the Noto family loaded
        self.missing = {}                  # codepoint -> count

    # -- choosing a font --------------------------------------------------
    def font_for(self, code):
        """The registered font that can draw this character, or None."""
        if code in self._cache:
            return self._cache[code]
        chosen = None
        for low, high, name in BLOCK_PREFERENCE:
            if low <= code <= high and code in self._coverage.get(name, ()):
                chosen = name
                break
        if chosen is None and code in self._coverage.get(self.body, ()):
            chosen = self.body
        if chosen is None:
            for name in self._coverage:
                if code in self._coverage[name]:
                    chosen = name
                    break
        self._cache[code] = chosen
        return chosen

    def runs(self, text, base=None):
        """Split text into (font name, substring) pairs.

        Characters no font can draw become `?` in a run of the base font and
        are counted in `missing`.
        """
        base = base or self.body
        out = []
        for char in str(text):
            if char in "\n\t" or char == " " or ord(char) < 128:
                font = base
                piece = char
            else:
                font = self.font_for(ord(char))
                if font is None:
                    self.missing[ord(char)] = self.missing.get(ord(char), 0) + 1
                    font, piece = base, "?"
                else:
                    piece = char
                    if font == self.body:
                        font = base
            if out and out[-1][0] == font:
                out[-1][1].append(piece)
            else:
                out.append((font, [piece]))
        return [(font, "".join(parts)) for font, parts in out]

    # -- output -----------------------------------------------------------
    def markup(self, text, base=None, newline_br=True):
        """HTML-escape text and tag each run with the font that can draw it.

        Takes raw text, not escaped text: splitting escaped text would cut
        entities like `&amp;` in half.
        """
        base = base or self.body
        parts = []
        for font, chunk in self.runs(text, base):
            escaped = html.escape(chunk, quote=False)
            if newline_br:
                escaped = escaped.replace("\n", "<br/>")
            parts.append(escaped if font == base else '<font face="%s">%s</font>' % (font, escaped))
        return "".join(parts)

    def draw(self, canvas, x, y, text, size, base=None, align="left"):
        """Draw a canvas string run by run, so each script uses its own font.

        `align` is left, right or centre, matching the three canvas methods.
        """
        base = base or self.body
        runs = self.runs(text, base)
        from reportlab.pdfbase import pdfmetrics

        total = sum(pdfmetrics.stringWidth(chunk, font, size) for font, chunk in runs)
        start = x if align == "left" else x - total if align == "right" else x - total / 2
        for font, chunk in runs:
            canvas.setFont(font, size)
            canvas.drawString(start, y, chunk)
            start += pdfmetrics.stringWidth(chunk, font, size)
        canvas.setFont(base, size)
        return total

    @property
    def warnings(self):
        """One line naming what could not be drawn, or nothing."""
        if not self.missing:
            return []
        shown = sorted(self.missing)[:12]
        names = ", ".join("U+%04X" % cp for cp in shown)
        more = "" if len(self.missing) <= 12 else " and %d more" % (len(self.missing) - 12)
        total = sum(self.missing.values())
        return [
            "PDF fonts: %d character%s in %d code point%s had no glyph in any registered font (%s%s) and were "
            "written as '?'. Add the matching Noto font to skills/agent-design-studio/fonts/ "
            "(for example NotoSansCJK-Regular.ttf for Chinese, Japanese and Korean) and render again."
            % (total, "" if total == 1 else "s", len(self.missing), "" if len(self.missing) == 1 else "s", names, more)
        ]


def _coverage_of(name):
    from reportlab.pdfbase import pdfmetrics

    face = pdfmetrics.getFont(name).face
    return set(getattr(face, "charToGlyph", {}) or ())


def register():
    """Register every font found under fonts/ and return the set to draw with.

    Falls back to ReportLab's base fonts when the Noto files are absent, so the
    renderers still work in a checkout without them; `unicode` is then False.
    """
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    coverage = {}
    for name, filename in CORE_FONTS + SCRIPT_FONTS:
        path = FONT_DIR / filename
        if not path.is_file():
            continue
        try:
            if name not in _REGISTERED:
                pdfmetrics.registerFont(TTFont(name, str(path)))
                _REGISTERED[name] = str(path)
            coverage[name] = _coverage_of(name)
        except Exception:                                   # a damaged font file
            continue
    if "StudioBody" in coverage and "StudioBold" in coverage:
        pdfmetrics.registerFontFamily(
            "StudioBody", normal="StudioBody", bold="StudioBold",
            italic="StudioBody", boldItalic="StudioBold",
        )
        mono = "StudioMono" if "StudioMono" in coverage else "Courier"
        return FontSet("StudioBody", "StudioBold", mono, coverage, True)
    # No Noto family: ReportLab's Latin-1 base fonts, and say so.
    base = {}
    for name in ("Helvetica", "Helvetica-Bold", "Courier"):
        base[name] = set(range(32, 256))
    base.update(coverage)
    return FontSet("Helvetica", "Helvetica-Bold", "Courier", base, False)
