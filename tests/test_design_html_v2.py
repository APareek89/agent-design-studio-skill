"""v1.2 HTML view tests on the two seed designs and synthetic graphs.

Checks structure the html-design-spec requires: every view renders in every
mode, one tree box per task and one SVG node per workflow item, a condition
label on every edge whose source has several successors, no reader-text
ellipsis, no external asset, balanced markup, and the exporter writing
DESIGN.html alongside the PDF companions.
"""

import copy
from html.parser import HTMLParser
import importlib.util
import json
from pathlib import Path
import re
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills/agent-design-studio/scripts"


def module(name):
    spec = importlib.util.spec_from_file_location("v2_" + name, SCRIPTS / (name + ".py"))
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


design_html = module("design_html")
design_io = module("design_io")
fixture_spec = importlib.util.spec_from_file_location("v2_fixtures", ROOT / "tests/test_design_io.py")
fixtures = importlib.util.module_from_spec(fixture_spec)
fixture_spec.loader.exec_module(fixtures)

SEEDS = ("telecom", "health-claims")
VOID = {"br", "meta", "input", "hr", "path", "circle", "line", "rect", "use", "col", "wbr"}


class Balance(HTMLParser):
    """Counts mismatched close tags; a zero count is the 'zero parser errors' bar."""

    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.errors = 0
        self.text = []
        self.in_style_or_script = False
        self.feed(source)
        self.errors += len(self.stack)

    def handle_starttag(self, tag, attrs):
        if tag in ("style", "script"):
            self.in_style_or_script = True
        if tag not in VOID:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        return

    def handle_endtag(self, tag):
        if tag in ("style", "script"):
            self.in_style_or_script = False
        if tag in VOID:
            return
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()
        else:
            self.errors += 1

    def handle_data(self, data):
        if not self.in_style_or_script:
            self.text.append(data)


def seed(name):
    folder = ROOT / "examples" / name
    return design_io.load_json(folder / "design.json"), design_io.load_json(folder / "review.json")


def section(document, key):
    match = re.search(r'<section data-view="%s".*?</section>' % re.escape(key), document, re.S)
    return match.group(0) if match else ""


class SeedViewTests(unittest.TestCase):
    def test_every_view_renders_for_both_seeds_in_every_mode(self):
        for name in SEEDS:
            design, review = seed(name)
            for mode in design_html.MODES:
                document = design_html.render_html(design, review, mode)
                expected = design_html.LITE_VIEWS if mode == "lite" else design_html.VIEW_ORDER
                for key in expected:
                    self.assertTrue(section(document, key), (name, mode, key))
                page = Balance(document)
                self.assertEqual(page.errors, 0, (name, mode))
                text = "".join(page.text)
                self.assertNotIn("…", text, (name, mode))
                for pattern in ('src="', 'href="http', "@import", "https://", "http://"):
                    self.assertNotIn(pattern, document, (name, mode, pattern))
                self.assertIsNone(re.search(r"url\((?!#)", document), (name, mode))
                self.assertNotIn("Approve and continue", document)

    def test_one_tree_box_per_task_and_one_svg_node_per_workflow_item(self):
        for name in SEEDS:
            design, review = seed(name)
            document = design_html.render_html(design, review)
            tasks = [t for t in design["stages"]["tasks"]["items"] if t["kind"] == "task"]
            tree = section(document, "tasks")
            for task in tasks:
                if task["data"]["parentId"] == "":
                    self.assertIn('<div class="root">', tree)
                elif task["data"]["mode"] == "leaf":
                    self.assertEqual(tree.count('data-leaf="%s"' % task["id"]), 1, (name, task["id"]))
                    self.assertEqual(tree.count('data-leaf-detail="%s"' % task["id"]), 1, (name, task["id"]))
                else:
                    self.assertIn('<div class="id">%s</div>' % task["id"], tree, (name, task["id"]))
            flow = section(document, "workflow")
            svg = re.search(r"<svg.*?</svg>", flow, re.S).group(0)
            for node in design["stages"]["workflow"]["items"]:
                self.assertEqual(svg.count('data-node="%s"' % node["id"]), 1, (name, node["id"]))
                self.assertEqual(flow.count('data-node-detail="%s"' % node["id"]), 1, (name, node["id"]))
            self.assertNotIn("(no condition stated)", svg)

    def test_every_edge_from_a_branching_node_carries_its_condition(self):
        for name in SEEDS:
            design, review = seed(name)
            document = design_html.render_html(design, review)
            svg = re.search(r"<svg.*?</svg>", section(document, "workflow"), re.S).group(0)
            plain = re.sub(r"<[^>]+>", " ", svg)
            plain = re.sub(r"\s+", " ", plain)
            for node in design["stages"]["workflow"]["items"]:
                if len(set(node["data"]["next"])) < 2:
                    continue
                for tr in json.loads(node["description"])["transitions"]:
                    first_line = design_html.wrap(tr["when"], 20)[0]
                    self.assertIn(design_html.esc(first_line), plain.replace("&amp;", "&amp;"), (name, node["id"], tr["to"]))
                    self.assertIn('data-edge="%s-%s"' % (node["id"], tr["to"]), svg)

    def test_reader_layer_uses_presentation_and_has_no_truncation(self):
        for name in SEEDS:
            design, review = seed(name)
            document = design_html.render_html(design, review)
            brief = section(document, "brief")
            p = design["presentation"]
            self.assertIn(design_html.esc(design_html.plain(p["systemSentence"])), brief)
            for call in p["designCalls"]:
                self.assertIn(design_html.esc(design_html.plain(call["choice"])), brief)
            for row in p["autonomy"]:
                self.assertIn(design_html.esc(design_html.plain(row["action"])), brief)
            self.assertNotIn("...", re.sub(r"<[^>]+>", "", brief))
            self.assertNotIn("Reader layer derived", brief)
            for wid, label in p.get("workflowLabels", {}).items():
                self.assertIn(design_html.esc(design_html.wrap(label, 23)[0]), section(document, "workflow"))
            for h in design["assumptions"]:
                self.assertIn(design_html.esc(h["statement"]), section(document, "assumptions"))

    def test_clickable_ids_focusable_and_status_bar_read_only(self):
        design, review = seed("telecom")
        document = design_html.render_html(design, review)
        self.assertIn('data-gofm="FM1"', document)
        self.assertIn('data-goleaf="T3.1"', document)
        self.assertIn('data-gonode="W2"', document)
        self.assertIn('class="fm-row" data-fmrow="FM1" id="row-FM1" tabindex="0"', document)
        self.assertRegex(document, r'<g class="wf-node[^"]*" data-node="W1"[^>]*tabindex="0" role="button"')
        self.assertIn("Next → 1 Brief and scope", section(document, "brief"))
        self.assertNotIn("Next →", section(document, "review"))
        self.assertEqual(document.count('class="statusbar"'), len(design_html.VIEW_ORDER))
        self.assertIn('data-month-cost="', document)


class WrapTests(unittest.TestCase):
    def test_long_tokens_break_after_punctuation_and_keep_every_character(self):
        token = "documentStatus in {missing,conflict,invalid,unavailable}"
        lines = design_html.wrap(token, 32)
        self.assertTrue(all(len(line) <= 32 for line in lines), lines)
        self.assertEqual(lines[0], "documentStatus in")
        self.assertTrue(lines[1].endswith(","), lines)
        self.assertEqual("".join(lines).replace(" ", ""), token.replace(" ", ""))
        self.assertEqual(design_html.wrap("x" * 70, 20), ["x" * 20, "x" * 20, "x" * 20, "x" * 10])
        self.assertEqual(design_html.wrap("", 10), [""])


class SyntheticGraphTests(unittest.TestCase):
    def chain(self, length, fan_out_at=None):
        design = fixtures.make_design()
        base = design["stages"]["workflow"]["items"][0]
        items = []
        for i in range(1, length + 1):
            node = copy.deepcopy(base)
            node["id"] = f"W{i}"
            node["title"] = f"Step {i} with a fairly long label to wrap"
            contract = json.loads(node["description"])
            nxt = []
            if i < length:
                nxt.append(f"W{i + 1}")
            if fan_out_at == i:
                nxt += [f"W{j}" for j in range(i + 2, min(length, i + 5) + 1)]
            if i == length and length > 3:
                nxt = ["W2"]  # loop back edge
            contract["transitions"] = [{"to": t, "when": f"result == R{t}", "mode": "exclusive"} for t in nxt]
            contract["terminalDisposition"] = "" if nxt else "DONE"
            node["description"] = json.dumps(contract)
            node["data"].update(next=nxt, decision=len(nxt) > 1)
            items.append(node)
        design["stages"]["workflow"]["items"] = items
        return design

    def test_long_chain_splits_into_bands_and_keeps_every_node(self):
        design = self.chain(40)
        document = design_html.render_html(design, fixtures.make_review())
        svg = re.search(r"<svg.*?</svg>", section(document, "workflow"), re.S).group(0)
        for i in range(1, 41):
            self.assertEqual(svg.count('data-node="W%d"' % i), 1)
        self.assertIn('class="wf-band"', svg)
        self.assertIn("continues at", svg)
        self.assertNotIn("font-size:9", svg)

    def test_fan_out_edges_are_all_labelled_and_back_edge_drawn_above(self):
        design = self.chain(8, fan_out_at=2)
        document = design_html.render_html(design, fixtures.make_review())
        svg = re.search(r"<svg.*?</svg>", section(document, "workflow"), re.S).group(0)
        for target in ("W3", "W4", "W5", "W6"):
            self.assertIn('data-edge="W2-%s"' % target, svg)
            self.assertIn("result == R%s" % target, svg)
        self.assertIn('class="wf-edge back"', svg)
        self.assertIn('data-edge="W8-W2"', svg)


class ExportIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.folder = Path(self.tmp.name)
        self.design = fixtures.make_design()
        self.review = fixtures.make_review()
        self.dp = self.folder / "design.json"
        self.rp = self.folder / "review.json"
        self.dp.write_text(json.dumps(self.design))
        self.rp.write_text(json.dumps(self.review))

    def tearDown(self):
        self.tmp.cleanup()

    def test_export_writes_html_in_every_mode_and_no_html_flag_skips_it(self):
        for mode in ("lite", "standard", "full"):
            out = self.folder / mode
            result = design_io.export_design(self.dp, out, self.rp, mode=mode)
            self.assertTrue(result["ok"], result)
            self.assertTrue(result["html"])
            html = (out / "DESIGN.html").read_text(encoding="utf-8")
            expected = design_html.LITE_VIEWS if mode == "lite" else design_html.VIEW_ORDER
            self.assertEqual(html.count("<section data-view="), len(expected))
            manifest = json.loads((out / "validation.json").read_text())
            self.assertIn("DESIGN.html", manifest["generatedFiles"])
            self.assertIn("DESIGN.html", manifest["fileSha256"])
            if mode != "lite":
                self.assertTrue((out / "README.md").is_file())
                self.assertTrue((out / "_evidence" / "eval-set.json").is_file())
                self.assertIn("DESIGN.html", (out / "README.md").read_text())
            # Re-export over its own output is allowed; the tracked HTML is replaced.
            self.assertTrue(design_io.export_design(self.dp, out, self.rp, mode=mode)["ok"])
        skipped = self.folder / "skipped"
        result = design_io.export_design(self.dp, skipped, self.rp, mode="standard", html=False)
        self.assertTrue(result["ok"])
        self.assertFalse(result["html"])
        self.assertFalse((skipped / "DESIGN.html").exists())
        self.assertNotIn("DESIGN.html", json.loads((skipped / "validation.json").read_text())["fileSha256"])

    def test_cli_no_html_flag(self):
        import subprocess
        import sys

        out = self.folder / "cli"
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / "design_io.py"), "export", str(self.dp), "--review", str(self.rp), "--out", str(out), "--mode", "lite", "--no-html"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((out / "DESIGN.html").exists())
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / "design_io.py"), "export", str(self.dp), "--review", str(self.rp), "--out", str(out), "--mode", "lite"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((out / "DESIGN.html").is_file())

    def test_edited_html_blocks_overwrite(self):
        out = self.folder / "edited"
        design_io.export_design(self.dp, out, self.rp, mode="standard")
        (out / "DESIGN.html").write_text("hand edited")
        with self.assertRaisesRegex(ValueError, "unrelated or edited"):
            design_io.export_design(self.dp, out, self.rp, mode="standard")
        self.assertEqual((out / "DESIGN.html").read_text(), "hand edited")


if __name__ == "__main__":
    unittest.main()
