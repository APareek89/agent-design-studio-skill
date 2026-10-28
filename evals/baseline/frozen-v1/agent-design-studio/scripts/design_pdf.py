#!/usr/bin/env python3
"""Render a validated canonical design as a readable,design-only PDF.

Optional runtime dependency: ReportLab>=4,<5. The stdlib validator/exporter does
not import this module or require ReportLab. This renderer summarizes canonical
contracts and test expectations; full fixtures remain in design.json and the
companion eval-set.json. It never calls a model,network or business system.
"""

from __future__ import annotations
import argparse
from collections import OrderedDict
import hashlib
import html
import importlib.util
import io
import json
from pathlib import Path
import re
import sys
from types import SimpleNamespace

HTML_QUESTION = "Would you also like a visual HTML version in the same ten-stage structure as the app?"
SECTIONS = (
    ("context", "Context"),
    ("tasks", "Task map"),
    ("components", "Components"),
    ("workflow", "Workflow map"),
    ("framework", "Framework, tools and data"),
    ("models", "Models and cost"),
    ("fmea", "Failure modes"),
    ("evals", "Evaluations"),
    ("rollout", "Measurement and rollout"),
    ("export", "Coding handoff"),
)


def _io_module():
    path = Path(__file__).with_name("design_io.py")
    spec = importlib.util.spec_from_file_location("agent_design_studio_pdf_io", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _libraries():
    try:
        import reportlab
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_LEFT
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.platypus import (
            SimpleDocTemplate,
            Paragraph,
            Spacer,
            LongTable,
            TableStyle,
            CondPageBreak,
            KeepTogether,
        )
    except ImportError as exc:
        raise ValueError(
            'Missing optional PDF dependency ReportLab. Run `python3 -m pip install "reportlab>=4,<5"` in the Python environment used for design_pdf.py. The stdlib design_io.py commands remain available without it.'
        ) from exc
    return SimpleNamespace(**locals())


def _text(value):
    text = (
        str(value)
        .replace("\u2011", "-")
        .replace("\u2013", "-")
        .replace("\u2014", " - ")
        .replace("\u2192", " -> ")
    )
    return "".join(c if c in "\n\t" or ord(c) >= 32 else " " for c in text)


def _clip(value, limit=600):
    text = _text(value)
    if limit is None or len(text) <= limit:
        return text
    return text[: limit - 3].rsplit(" ", 1)[0] + "..."


def _parse(value):
    if not isinstance(value, str):
        return value
    try:
        return json.loads(value)
    except (ValueError, TypeError):
        return value


def _readable(value, limit=600, depth=0):
    """Render field values as terse readable facts,not indented raw JSON."""
    value = _parse(value)
    if value is None:
        return "none"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, dict):
        text = "; ".join(
            str(k)
            + ": "
            + _readable(
                v, None if limit is None else (160 if depth else 260), depth + 1
            )
            for k, v in value.items()
        )
        return _clip(text, limit)
    if isinstance(value, list):
        return _clip(
            " | ".join(
                _readable(v, None if limit is None else 180, depth + 1) for v in value
            ),
            limit,
        )
    return _clip(value, limit)


def _fixture_summary(data):
    obj = _parse(data)
    if not isinstance(obj, dict):
        return _readable(obj, 250)
    run = obj.get("run", obj)
    if isinstance(run, dict) and "inherit" in run:
        ref = run["inherit"]
        parts = ["Base " + _readable(ref, 110)]
        variants = run.get("variants", [])
        if variants:
            parts.append(
                "Variants: "
                + ", ".join(
                    str(v.get("id", v.get("name", "case")))
                    for v in variants
                    if isinstance(v, dict)
                )
            )
        return _clip("; ".join(parts), 300)
    preferred = (
        "command",
        "event",
        "request",
        "mutation",
        "override",
        "overrides",
        "patch",
        "variants",
        "cases",
        "scenario",
        "config",
        "clock",
        "clock_utc",
    )
    selected = {key: obj[key] for key in preferred if key in obj}
    if not selected:
        selected = {
            k: v
            for k, v in obj.items()
            if k
            not in (
                "registry",
                "base",
                "fixtures",
                "files",
                "ordered_mocks",
                "orderedMocks",
            )
        }
    return _readable(selected, 330)


def _contracts(values):
    lines = []
    for value in values:
        parsed = _parse(value)
        if isinstance(parsed, dict):
            lines.extend(str(k) + ": " + _readable(v, None) for k, v in parsed.items())
        else:
            lines.append(_text(value))
    return lines


def _assumptions(design):
    ledger = design["assumptions"]
    known_ids = {h["id"] for h in ledger}
    seen = {" ".join(h["statement"].split()) for h in ledger}
    extra = OrderedDict()
    for key, packet in design["stages"].items():
        for statement in packet["assumptions"]:
            norm = " ".join(statement.split())
            if (
                norm
                and norm not in seen
                and not (known_ids & set(re.findall(r"\bH[1-9]\d*\b", statement)))
            ):
                extra.setdefault(norm, []).append(key)
        for item in packet["items"]:
            for statement in item["assumptions"]:
                norm = " ".join(statement.split())
                if (
                    norm
                    and norm not in seen
                    and not (known_ids & set(re.findall(r"\bH[1-9]\d*\b", statement)))
                ):
                    extra.setdefault(norm, []).append(item["id"])
    return ledger, extra


def create_pdf(design_path, review_path, out):
    D = _io_module()
    design_path = Path(design_path)
    review_path = Path(review_path)
    out = Path(out)
    design = D.load_json(design_path)
    validation = D.validate_design(design)
    if not validation["valid"]:
        return {
            "ok": False,
            "status": "structural-errors",
            "errors": validation["errors"],
        }
    review = D.load_json(review_path)
    rv = D.validate_review(review, True)
    if not rv["valid"]:
        return {"ok": False, "status": "invalid-review", "errors": rv["errors"]}
    if out.suffix.lower() != ".pdf":
        raise ValueError("PDF output must use a .pdf filename.")
    if out.resolve() in (design_path.resolve(), review_path.resolve()):
        raise ValueError(
            "Refusing to overwrite design or review input; choose a new PDF filename."
        )
    if out.exists() or out.is_symlink():
        raise ValueError(
            f"{out}: existing files are never overwritten. Choose a new PDF filename or explicitly remove a known generated prior PDF."
        )
    R = _libraries()
    colors = R.colors
    body_font, bold_font, mono_font = "Helvetica", "Helvetica-Bold", "Courier"
    fontdir = Path(R.reportlab.__file__).parent / "fonts"
    if (fontdir / "Vera.ttf").is_file() and (fontdir / "VeraBd.ttf").is_file():
        R.pdfmetrics.registerFont(R.TTFont("StudioBody", str(fontdir / "Vera.ttf")))
        R.pdfmetrics.registerFont(R.TTFont("StudioBold", str(fontdir / "VeraBd.ttf")))
        R.pdfmetrics.registerFontFamily(
            "StudioBody",
            normal="StudioBody",
            bold="StudioBold",
            italic="StudioBody",
            boldItalic="StudioBold",
        )
        body_font, bold_font = "StudioBody", "StudioBold"
    navy = colors.HexColor("#18324A")
    teal = colors.HexColor("#087F8C")
    muted = colors.HexColor("#566879")
    line = colors.HexColor("#D9E3EB")
    pale = colors.HexColor("#F3F7FA")
    styles = {
        "body": R.ParagraphStyle(
            "Body",
            fontName=body_font,
            fontSize=9,
            leading=12.7,
            textColor=navy,
            spaceAfter=5,
            splitLongWords=True,
        ),
        "small": R.ParagraphStyle(
            "Small",
            fontName=body_font,
            fontSize=7.6,
            leading=10.4,
            textColor=muted,
            spaceAfter=4,
            splitLongWords=True,
        ),
        "mono": R.ParagraphStyle(
            "Mono",
            fontName=body_font,
            fontSize=8,
            leading=10.8,
            textColor=navy,
            spaceAfter=3,
            splitLongWords=True,
        ),
        "title": R.ParagraphStyle(
            "Title",
            fontName=bold_font,
            fontSize=23,
            leading=29,
            textColor=navy,
            spaceAfter=12,
            splitLongWords=True,
        ),
        "section": R.ParagraphStyle(
            "Section",
            fontName=bold_font,
            fontSize=15,
            leading=19,
            textColor=navy,
            spaceBefore=13,
            spaceAfter=8,
            keepWithNext=True,
            splitLongWords=True,
        ),
        "card": R.ParagraphStyle(
            "Card",
            fontName=bold_font,
            fontSize=10.2,
            leading=13.5,
            textColor=teal,
            spaceBefore=8,
            spaceAfter=5,
            keepWithNext=True,
            splitLongWords=True,
        ),
        "head": R.ParagraphStyle(
            "Head",
            fontName=bold_font,
            fontSize=8,
            leading=10.6,
            textColor=colors.white,
            splitLongWords=True,
        ),
    }
    story = []

    def p(text, style="body"):
        # Only renderer-owned markup is interpreted. Every brief/card is escaped.
        escaped = html.escape(_text(text), quote=False).replace("\n", "<br/>")
        return R.Paragraph(escaped, styles[style])

    def add(text, style="body"):
        story.append(p(text, style))

    def label(name, value, limit=700, style="body"):
        if value is None or value == "" or value == []:
            return
        escaped_name = html.escape(name, quote=False)
        escaped = html.escape(_readable(value, limit), quote=False).replace(
            "\n", "<br/>"
        )
        story.append(
            R.Paragraph("<b>" + escaped_name + ":</b> " + escaped, styles[style])
        )

    def table(headers, rows, widths):
        cells = [[p(x, "head") for x in headers]] + [
            [p(_text(x), "small") for x in row] for row in rows
        ]
        t = R.LongTable(
            cells,
            colWidths=widths,
            repeatRows=1,
            splitByRow=1,
            splitInRow=1,
            hAlign="LEFT",
        )
        t.setStyle(
            R.TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), navy),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ("LINEBELOW", (0, 0), (-1, 0), 0.5, navy),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, pale]),
                    ("LINEBELOW", (0, 1), (-1, -1), 0.25, line),
                ]
            )
        )
        story.extend([t, R.Spacer(1, 7)])

    def card(item):
        story.append(R.CondPageBreak(62))
        add(item["id"] + " - " + item["title"], "card")

    def section(n, title):
        story.append(R.CondPageBreak(110))
        add(str(n) + "  " + title, "section")

    add("AGENT DESIGN STUDIO", "small")
    add(design["title"], "title")
    status = rv["status"].upper()
    add(status + " | DESIGN ONLY", "card")
    add(
        "A reviewed system-design specification,not an implemented system or executed business test. Scores below are supplied design judgements.",
        "body",
    )
    add(
        "Review: "
        + review["method"]
        + " / round "
        + str(review["round"])
        + " | "
        + str(sum(len(s["items"]) for s in design["stages"].values()))
        + " canonical cards across ten stages.",
        "small",
    )
    add(
        "This report prioritizes design calls,contracts and review evidence. Full fixtures and exact canonical wording remain in design.json; eval-set.json contains the complete machine-readable evaluation set.",
        "small",
    )
    table(
        ["Design dimension", "Score", "Design dimension", "Score"],
        [
            [
                review["dimensions"][i]["id"],
                str(review["dimensions"][i]["score"]) + "/4",
                review["dimensions"][i + 6]["id"],
                str(review["dimensions"][i + 6]["score"]) + "/4",
            ]
            for i in range(6)
        ],
        [184, 72, 184, 71],
    )
    stages = design["stages"]
    for number, (key, title) in enumerate(SECTIONS, 1):
        section(number, title)
        items = stages[key]["items"]
        if key == "context":
            add("Original brief", "card")
            add(design["brief"])
            printed = {" ".join(design["brief"].split())}
            for item in items:
                value = item["data"]["value"]
                norm = " ".join(value.split())
                if norm in printed:
                    continue
                printed.add(norm)
                card(item)
                label(item["data"]["field"], value, 1800)
            add(
                "Evidence boundary: brief quotes and proposed H assumptions are separate. Validation checks source form; it does not establish policy truth or permissions.",
                "small",
            )
        elif key == "tasks":
            tasks = [x for x in items if x["kind"] == "task"]
            lookup = {x["id"]: x for x in tasks}
            for item in tasks:
                depth = 0
                cursor = item
                while cursor["data"]["parentId"] in lookup:
                    depth += 1
                    cursor = lookup[cursor["data"]["parentId"]]
                card(item)
                label(
                    "Tree position",
                    ("  " * depth)
                    + (
                        "Overall job"
                        if depth == 0
                        else "Child of " + item["data"]["parentId"]
                    )
                    + " / "
                    + item["data"]["mode"]
                    + " / risk "
                    + item["data"]["risk"],
                    250,
                    "small",
                )
                add(_clip(item["description"], 650))
                label("Resolution basis", item["data"]["basis"], 440)
                label("Autonomy", item["data"]["autonomy"], 400)
                label(
                    "Frequency / examples",
                    item["data"]["frequency"]
                    + " / "
                    + "; ".join(item["data"]["examples"]),
                    330,
                    "small",
                )
            attrs = [x for x in items if x["kind"] == "attribute"]
            if attrs:
                table(
                    ["Attribute", "Tasks", "Authority / loading"],
                    [
                        [
                            a["id"] + " " + a["title"],
                            ", ".join(a["data"]["taskIds"]),
                            a["data"]["sourceSystem"] + " / " + a["data"]["loaded"],
                        ]
                        for a in attrs
                    ],
                    [151, 82, 278],
                )
        elif key == "components":
            add(
                "Contracts below retain field names and action boundaries. Long values are compacted; canonical design.json remains authoritative.",
                "small",
            )
            for item in items:
                d = item["data"]
                card(item)
                label(
                    "Group / tasks",
                    d["group"] + " / " + ", ".join(d["taskIds"]),
                    350,
                    "small",
                )
                add(_clip(item["description"], 850))
                for name, values in [
                    ("Inputs", d["inputs"]),
                    ("Outputs", d["outputs"]),
                ]:
                    add(name, "small")
                    for text in _contracts(values):
                        add(text, "mono")
                label("Why code", d["whyCode"], 270, "small")
                label("Authorization / approval boundary", d["approvalRule"], None)
        elif key == "workflow":
            rows = []
            controls = OrderedDict()
            bindings = OrderedDict()
            for item in items:
                d = item["data"]
                c = _parse(item["description"])
                prefix = item["id"] + " / " + d["componentId"]
                if c["transitions"]:
                    for tr in c["transitions"]:
                        rows.append(
                            [
                                prefix,
                                tr["to"],
                                _text(tr["when"]) + " [" + str(tr["mode"]) + "]",
                            ]
                        )
                else:
                    rows.append(
                        [prefix, "TERMINAL", _readable(c["terminalDisposition"], None)]
                    )
                for name in (
                    "failureDisposition",
                    "timeout",
                    "retryPolicy",
                    "cancellation",
                    "reconciliationIdentity",
                ):
                    value = c.get(name)
                    if value:
                        controls.setdefault((name, _readable(value, None)), []).append(
                            item["id"]
                        )
                for field, binding in c.get("bindings", {}).items():
                    bindings.setdefault((field, _readable(binding, None)), []).append(
                        item["id"]
                    )
            table(
                ["Node / component", "To", "Guard or terminal disposition"],
                rows,
                [105, 62, 344],
            )
            add("Failure,retry and human controls", "card")
            for (name, value), node_ids in controls.items():
                label(name + " [" + ", ".join(node_ids) + "]", value, None)
            if bindings:
                table(
                    ["Guard field", "Producer / type / update"],
                    [
                        [field, value + " [" + ", ".join(ids) + "]"]
                        for (field, value), ids in bindings.items()
                    ],
                    [135, 376],
                )
        elif key == "framework":
            seen_cloud = {}
            for item in items:
                d = item["data"]
                card(item)
                label(
                    "Category / permission",
                    d["category"] + " / " + d["permission"],
                    160,
                    "small",
                )
                label("Chosen design", d["choice"], None)
                label("Rejected alternatives", d["alternatives"], None)
                label("Tradeoffs / verification", d["tradeoffs"], None)
                label("Blast radius", d["blastRadius"], None)
                label("Authority", d["approvalRule"], None)
                label("Least privilege", d["leastPrivilege"], None)
                cloud = tuple(d[k] for k in ("aws", "gcp", "azure", "openSource"))
                if any(cloud) and cloud not in seen_cloud:
                    seen_cloud[cloud] = item["id"]
                    for name in ("aws", "gcp", "azure", "openSource"):
                        label(name, d[name], None, "small")
                elif any(cloud):
                    add(
                        "Cloud candidate details match " + seen_cloud[cloud] + ".",
                        "small",
                    )
        elif key == "models":
            if not items:
                add(
                    "No LLM components are included. No model plan or provider cost is required.",
                    "body",
                )
            else:
                table(
                    [
                        "Plan / component",
                        "Tier / calls",
                        "Input / output tokens",
                        "USD per million tokens",
                    ],
                    [
                        [
                            m["id"] + " / " + m["data"]["componentId"],
                            m["data"]["tier"] + " / " + str(m["data"]["callsPerCase"]),
                            str(m["data"]["inputTokens"])
                            + " / "
                            + str(m["data"]["outputTokens"]),
                            str(m["data"]["inputPrice"])
                            + " input / "
                            + str(m["data"]["outputPrice"])
                            + " output",
                        ]
                        for m in items
                    ],
                    [115, 99, 128, 169],
                )
                add(
                    "Zero prices mean unpriced,not free. Numeric budgets and branch frequencies are hypotheses unless evidence states otherwise.",
                    "small",
                )
                for item in items:
                    card(item)
                    label(
                        "Budget rationale and fallback", item["data"]["rationale"], None
                    )
                    label("Fine-tuning condition", item["data"]["fineTuneWhen"], None)
        elif key == "fmea":
            table(
                ["Risk", "Specific failure", "S / O / D", "RPN", "Linked evaluations"],
                [
                    [
                        x["id"],
                        _clip(x["title"], 150),
                        f"{x['data']['severity']} / {x['data']['occurrence']} / {x['data']['detection']}",
                        str(
                            x["data"]["severity"]
                            * x["data"]["occurrence"]
                            * x["data"]["detection"]
                        ),
                        ", ".join(x["data"]["evalIds"]),
                    ]
                    for x in items
                ],
                [42, 193, 63, 40, 173],
            )
            add(
                "Scores and RPN are author-supplied prioritization estimates,not incident probabilities or verified risk acceptance.",
                "small",
            )
            for item in items:
                d = item["data"]
                card(item)
                label("Effect / cause", d["effect"] + " / " + d["cause"], 520)
                label(
                    "Prevent / detect",
                    d["control"] + " / " + d["detectionMethod"],
                    None,
                )
                label("Owned action / gate", d["action"], None)
                label(
                    "Metric / business KPI",
                    d["metric"] + " / " + d["kpi"],
                    350,
                    "small",
                )
        elif key == "evals":
            add(
                "These are test specifications,not executed results. Full self-contained fixtures,ordered mocks and inheritance rules are in eval-set.json and design.json. This report shows concrete outcomes and assertion summaries.",
                "small",
            )
            for item in items:
                d = item["data"]
                card(item)
                label(
                    "Layer / links",
                    d["category"]
                    + " / tasks "
                    + ", ".join(d["taskIds"])
                    + " / risks "
                    + ", ".join(d["failureModeIds"]),
                    300,
                    "small",
                )
                label("Fixture", _fixture_summary(d["input"]), 330)
                label("Expected summary", _readable(d["expected"], 500), 500)
                label("Assertion summary", _readable(d["passRule"], 520), 520)
                label(
                    "Metric / target", d["metric"] + " / " + d["target"], 300, "small"
                )
                label(
                    "Labels / cadence / alert",
                    d["labelling"] + " / " + d["cadence"] + " / " + d["alertThreshold"],
                    360,
                    "small",
                )
        elif key == "rollout":
            for item in items:
                d = item["data"]
                card(item)
                label(
                    "Category / phase / owner",
                    d["category"] + " / " + d["phase"] + " / " + d["owner"],
                    340,
                    "small",
                )
                label("Business outcome", d["businessKpi"], None)
                label("AI mechanisms / guardrails", d["aiMetrics"], None)
                label("Entry / exit / stop and rollback", d["gate"], None)
                if d["experiment"]:
                    label("Experiment", d["experiment"], None)
        elif key == "export":
            for item in items:
                d = item["data"]
                card(item)
                for i, criterion in enumerate(d["acceptanceCriteria"], 1):
                    label("Acceptance " + str(i), criterion, None)
                label("Build instructions", d["buildInstructions"], None)
            add(
                "After delivering DESIGN.pdf, ask the user: "
                + HTML_QUESTION
                + " Generate HTML only after opt-in, unless already requested.",
                "card",
            )
    section("A", "Assumptions and launch dependencies")
    ledger, extra = _assumptions(design)
    if not ledger and not extra:
        add(
            "No proposed assumptions were recorded; that does not prove there are no unknowns.",
            "small",
        )
    for h in ledger:
        add(
            h["id"]
            + " - "
            + ("LAUNCH BLOCKER" if h["launchBlocker"] else "PROPOSED ASSUMPTION"),
            "card",
        )
        add(h["statement"])
        label("Why", h["why"], None)
        label("Proposed owner", h["owner"], None)
        label("Required validation", h["validation"], None)
    if extra:
        add("Other unique recorded assumptions", "card")
        for statement, refs in extra.items():
            label(_clip(", ".join(dict.fromkeys(refs)), 150), statement, None, "small")
    section("B", "Review evidence and limits")
    add(
        "Review method: "
        + review["method"]
        + "; round "
        + str(review["round"])
        + "; supplied status "
        + review["status"]
        + ".",
        "small",
    )
    table(
        ["Dimension", "Score", "Supplied evidence"],
        [
            [d["id"], str(d["score"]) + "/4", _clip("; ".join(d["evidence"]), 600)]
            for d in review["dimensions"]
        ],
        [57, 40, 414],
    )
    if review["issues"]:
        for issue in review["issues"]:
            add(
                issue["id"]
                + " / "
                + issue["severity"]
                + " / "
                + ("resolved" if issue["resolved"] else "OPEN")
                + " / "
                + issue["stage"]
                + "/"
                + issue["itemId"],
                "card",
            )
            add(issue["message"])
    else:
        add(
            "No issues were recorded by the reviewer. This is not proof of completeness or operational correctness.",
            "small",
        )
    for text in dict.fromkeys(review["limitations"] + D.LIMITATIONS):
        add(text, "small")
    add(
        "Canonical design SHA256: "
        + hashlib.sha256(design_path.read_bytes()).hexdigest(),
        "small",
    )
    buffer = io.BytesIO()
    doc = R.SimpleDocTemplate(
        buffer,
        pagesize=R.A4,
        rightMargin=42,
        leftMargin=42,
        topMargin=49,
        bottomMargin=43,
        title=design["title"],
        author="Agent Design Studio",
        subject=status + " / design-only specification",
        creator="Agent Design Studio design_pdf.py",
    )
    width, height = R.A4

    def page(canvas, document):
        canvas.saveState()
        canvas.setStrokeColor(line)
        canvas.setLineWidth(0.5)
        canvas.line(42, height - 34, width - 42, height - 34)
        canvas.setFillColor(muted)
        canvas.setFont(body_font, 7)
        canvas.drawString(42, height - 25, _clip(design["title"], 90))
        canvas.line(42, 32, width - 42, 32)
        canvas.drawString(42, 21, "Agent Design Studio | " + status + " | DESIGN ONLY")
        canvas.drawRightString(width - 42, 21, str(document.page))
        canvas.restoreState()

    doc.build(story, onFirstPage=page, onLaterPages=page)
    out.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation also protects against a file appearing after preflight.
    with out.open("xb") as handle:
        handle.write(buffer.getvalue())
    return {
        "ok": True,
        "status": rv["status"],
        "designOnly": True,
        "file": str(out.resolve()),
        "pages": doc.page,
        "bytes": len(buffer.getvalue()),
        "limitations": [
            "Readable summary; exact contracts and full machine fixtures remain canonical design.json/eval-set.json.",
            "This renderer executes no model,network or business controls.",
        ],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("design")
    parser.add_argument("--review", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    try:
        result = create_pdf(args.design, args.review, args.out)
        code = 0 if result["ok"] else 1
    except (ValueError, OSError, UnicodeError) as exc:
        result = {
            "ok": False,
            "status": "pdf-error",
            "errors": [{"path": "$", "message": str(exc)}],
        }
        code = 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
