"""Geometry of the workflow SVG: plates, nodes and the viewBox.

Before v1.3 the router drew long bezier curves and dropped each condition
plate wherever the curve happened to pass at a chosen x. With a fan-out of
eight, or an edge spanning several columns, plates landed on other plates and
on nodes, and edges crossed the whole picture.

These tests read the rendered SVG and check the geometry itself rather than
the markup around it:
  * no two condition plates overlap;
  * no plate overlaps a node box;
  * every edge that states a condition carries either its text or a legend
    number, so no condition is lost to the layout;
  * every node is inside the viewBox.
"""

import copy
import importlib.util
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills/agent-design-studio/scripts"


def module(name, prefix="fl_"):
    spec = importlib.util.spec_from_file_location(prefix + name, SCRIPTS / (name + ".py"))
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


design_html = module("design_html")
design_io = module("design_io")
fixture_spec = importlib.util.spec_from_file_location("fl_fixtures", ROOT / "tests/test_design_io.py")
fixtures = importlib.util.module_from_spec(fixture_spec)
fixture_spec.loader.exec_module(fixtures)

STRESS_FAN_OUT = ROOT / "evals/stress/out/12_fan_out_eight/design.json"
RECT_RE = re.compile(r'<rect class="wf-elbl-bg" x="(-?[\d.]+)" y="(-?[\d.]+)" '
                     r'width="([\d.]+)" height="([\d.]+)"')
NODE_RE = re.compile(r'<g class="wf-node[^"]*" data-node="([^"]+)"[^>]*>'
                     r'<rect x="(-?[\d.]+)" y="(-?[\d.]+)" width="([\d.]+)" height="([\d.]+)"')
VIEWBOX_RE = re.compile(r'viewBox="0 0 ([\d.]+) ([\d.]+)"')


def workflow_svg(design, review=None):
    document = design_html.render_html(design, review or fixtures.make_review())
    match = re.search(r"<svg.*?</svg>", design_html_section(document, "workflow"), re.S)
    assert match, "the workflow view must contain an SVG"
    return match.group(0)


def design_html_section(document, key):
    match = re.search(r'<section data-view="%s".*?</section>' % re.escape(key), document, re.S)
    return match.group(0) if match else ""


def plates(svg):
    return [tuple(float(v) for v in m.groups()) for m in RECT_RE.finditer(svg)]


def nodes(svg):
    return {m.group(1): tuple(float(v) for v in m.groups()[1:]) for m in NODE_RE.finditer(svg)}


def overlap_area(a, b):
    dx = min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0])
    dy = min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1])
    return dx * dy if dx > 0 and dy > 0 else 0.0


def chain(length, fan_out_at=None, fan_out=4):
    """A synthetic workflow: a chain of `length` nodes, optionally fanning out."""
    design = fixtures.make_design()
    base = design["stages"]["workflow"]["items"][0]
    items = []
    for i in range(1, length + 1):
        node = copy.deepcopy(base)
        node["id"] = "W%d" % i
        node["title"] = "Step %d with a fairly long label to wrap" % i
        contract = json.loads(node["description"])
        nxt = []
        if i < length:
            nxt.append("W%d" % (i + 1))
        if fan_out_at == i:
            nxt += ["W%d" % j for j in range(i + 2, min(length, i + 1 + fan_out) + 1)]
        contract["transitions"] = [
            {"to": t, "when": "intent == case_%s" % t.lower(), "mode": "exclusive"} for t in nxt
        ]
        contract["terminalDisposition"] = "" if nxt else "DONE"
        node["description"] = json.dumps(contract)
        node["data"].update(next=nxt, decision=len(nxt) > 1)
        items.append(node)
    design["stages"]["workflow"]["items"] = items
    return design


class PlateCollisions(unittest.TestCase):
    """No plate may sit on another plate or on a node."""

    def assert_clean(self, svg, label):
        boxes = plates(svg)
        self.assertTrue(boxes, label + ": the flow must carry condition plates")
        for i, a in enumerate(boxes):
            for b in boxes[i + 1:]:
                self.assertEqual(overlap_area(a, b), 0.0, "%s: two plates overlap at %s / %s" % (label, a, b))
        for name, box in nodes(svg).items():
            for plate in boxes:
                self.assertEqual(overlap_area(plate, box), 0.0,
                                 "%s: a plate overlaps node %s" % (label, name))

    def test_fan_out_of_eight_has_no_plate_collisions(self):
        self.assert_clean(workflow_svg(chain(12, fan_out_at=2, fan_out=8)), "fan-out 8")

    def test_the_fan_out_eight_stress_design_has_no_plate_collisions(self):
        design = design_io.load_json(STRESS_FAN_OUT)
        review = design_io.load_json(ROOT / "examples/telecom/review.json")
        self.assert_clean(workflow_svg(design, review), "12_fan_out_eight")

    def test_a_twenty_layer_chain_has_no_plate_collisions(self):
        self.assert_clean(workflow_svg(chain(20)), "20-layer chain")

    def test_the_seed_designs_have_no_plate_collisions(self):
        for name in ("telecom", "health-claims"):
            folder = ROOT / "examples" / name
            design = design_io.load_json(folder / "design.json")
            review = design_io.load_json(folder / "review.json")
            with self.subTest(seed=name):
                self.assert_clean(workflow_svg(design, review), name)


class EveryConditionIsVisible(unittest.TestCase):
    def conditions(self, design):
        found = {}
        for node in design["stages"]["workflow"]["items"]:
            for tr in json.loads(node["description"]).get("transitions", []):
                if tr.get("when"):
                    found[(node["id"], tr["to"])] = tr["when"]
        return found

    def assert_every_edge_speaks(self, design, review=None):
        svg = workflow_svg(design, review)
        text = " ".join(re.findall(r">([^<>]+)<", svg))
        for (source, target), when in self.conditions(design).items():
            edge = re.search(r'data-edge="%s-%s"([^>]*)>' % (re.escape(source), re.escape(target)), svg)
            if edge is None:
                # The two ends sit in different bands, so the edge is drawn as
                # a "continues at" note at both ends rather than as a line.
                self.assertIn("continues at %s" % target, text,
                              "edge %s-%s is neither drawn nor continued" % (source, target))
                self.assertIn("continues at %s" % source, text)
                continue
            numbered = 'data-legend="' in edge.group(1)
            spoken = design_html.wrap(when, 20)[0] in text
            self.assertTrue(numbered or spoken,
                            "edge %s-%s states '%s' but the flow shows neither the text nor a legend number"
                            % (source, target, when))
        return svg

    def test_every_condition_shows_on_a_twenty_layer_chain(self):
        self.assert_every_edge_speaks(chain(20))

    def test_every_condition_shows_under_a_fan_out_of_eight(self):
        svg = self.assert_every_edge_speaks(chain(12, fan_out_at=2, fan_out=8))
        self.assertIn('data-legend="1"', svg, "over six exits become a numbered legend")
        self.assertIn('class="wf-tag legend"', svg, "the legend is printed under the node")

    def test_six_exits_or_fewer_keep_their_text_on_the_edge(self):
        svg = workflow_svg(chain(12, fan_out_at=2, fan_out=4))
        self.assertNotIn("data-legend=", svg)
        self.assertIn("intent == case_w4", " ".join(re.findall(r">([^<>]+)<", svg)))

    def test_the_legend_keeps_the_full_condition_under_the_node(self):
        design = chain(12, fan_out_at=2, fan_out=8)
        document = design_html.render_html(design, fixtures.make_review())
        detail = design_html_section(document, "workflow")
        for target in ("w4", "w5", "w9"):
            self.assertIn("intent == case_%s" % target, detail,
                          "the node detail table keeps every condition in full")


class NodesStayInside(unittest.TestCase):
    def assert_inside(self, svg, label):
        box = VIEWBOX_RE.search(svg)
        self.assertTrue(box, label + ": the SVG must declare a viewBox")
        width, height = float(box.group(1)), float(box.group(2))
        found = nodes(svg)
        self.assertTrue(found, label)
        for name, (x, y, w, h) in found.items():
            self.assertGreaterEqual(x, 0, "%s: %s starts left of the viewBox" % (label, name))
            self.assertGreaterEqual(y, 0, "%s: %s starts above the viewBox" % (label, name))
            self.assertLessEqual(x + w, width, "%s: %s runs past the right edge" % (label, name))
            self.assertLessEqual(y + h, height, "%s: %s runs past the bottom edge" % (label, name))

    def test_nodes_stay_inside_for_a_fan_out_of_eight(self):
        self.assert_inside(workflow_svg(chain(12, fan_out_at=2, fan_out=8)), "fan-out 8")

    def test_nodes_stay_inside_for_a_twenty_layer_chain(self):
        self.assert_inside(workflow_svg(chain(20)), "20-layer chain")

    def test_nodes_stay_inside_for_a_forty_layer_chain_split_into_bands(self):
        svg = workflow_svg(chain(40))
        self.assert_inside(svg, "40-layer chain")
        self.assertIn('class="wf-band"', svg)

    def test_a_cross_band_edge_says_continues_at_on_both_ends(self):
        svg = workflow_svg(chain(40))
        self.assertGreaterEqual(svg.count("continues at"), 2)
        self.assertIn("→ continues at", svg)
        self.assertIn("← continues at", svg)


class OrthogonalRouting(unittest.TestCase):
    def test_edges_are_drawn_as_straight_runs_not_curves(self):
        svg = workflow_svg(chain(12, fan_out_at=2, fan_out=8))
        paths = re.findall(r'<path class="wf-edge[^"]*" d="([^"]+)"', svg)
        self.assertTrue(paths)
        for path in paths:
            self.assertNotIn("C", path, "edges are orthogonal, not bezier curves")
            self.assertRegex(path, r"^M[-\d.]+,[-\d.]+( L[-\d.]+,[-\d.]+)+$")

    def test_edges_from_one_node_share_a_gutter(self):
        svg = workflow_svg(chain(12, fan_out_at=2, fan_out=8))
        gutters = set()
        for match in re.finditer(r'data-edge="W2-W\d+"[^>]*><path class="wf-edge" d="([^"]+)"', svg):
            points = re.findall(r"[ML](-?[\d.]+),(-?[\d.]+)", match.group(1))
            gutters.add(points[1][0])
        self.assertEqual(len(gutters), 1, "one source fans out through one gutter: %s" % gutters)


if __name__ == "__main__":
    unittest.main()
