#!/usr/bin/env python3
"""Optional, read-only, self-contained HTML view of a validated design.

Uses only Python's standard library. This renders design evidence; it does not
execute the designed workflow, fetch assets, call models, or grant authority.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import importlib.util
import json
import os
from pathlib import Path
import re
import sys

_spec = importlib.util.spec_from_file_location(
    "_agent_design_html_io", Path(__file__).with_name("design_io.py")
)
design_io = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(design_io)

STAGES = design_io.STAGES
LABELS = (
    "Context",
    "Task map",
    "Components",
    "Workflow",
    "Framework",
    "Models",
    "FMEA",
    "Evaluations",
    "Rollout",
    "Build handoff",
)
INTROS = (
    "The decision, audience, boundary and evidence behind the design.",
    "Outcomes, their order and the information each leaf requires.",
    "Bounded responsibilities with typed inputs, outputs and authority.",
    "States, guarded edges, recovery and explicit terminal outcomes.",
    "Architecture choices, rejected alternatives and data permissions.",
    "Model responsibilities and illustrative budgets, where applicable.",
    "Failure causes, controls, ownership and planned verification.",
    "Concrete fixtures and planned offline, online and release evidence.",
    "Measures, phase gates, experiment and accountable proposed roles.",
    "Observable acceptance criteria and coding-agent instructions.",
)


def esc(value):
    """All design/review text passes through HTML escaping, never JS source."""
    if value is None:
        return "—"
    if isinstance(value, bool):
        value = "true" if value else "false"
    return html.escape(str(value), quote=True)


def text(value, tag="p", cls=""):
    return (
        f"<{tag}" + (f' class="{cls}"' if cls else "") + ">" + esc(value) + f"</{tag}>"
    )


def badge(value, cls=""):
    return '<span class="badge ' + cls + '">' + esc(value) + "</span>"


def prose(value):
    value = str(value)
    if len(value) <= 800:
        return text(value)
    return (
        text(value[:420] + "…")
        + "<details><summary>Read full text</summary>"
        + text(value)
        + "</details>"
    )


def listing(values, code=False):
    if not values:
        return '<p class="muted">None specified.</p>'
    return (
        "<ul>"
        + "".join(
            "<li>" + ("<code>" + esc(v) + "</code>" if code else esc(v)) + "</li>"
            for v in values
        )
        + "</ul>"
    )


def field(label, value):
    if value in ("", [], None):
        return ""
    body = listing(value) if isinstance(value, list) else prose(value)
    return '<div class="field">' + text(label, "h4") + body + "</div>"


def json_detail(label, value):
    try:
        parsed = design_io.parse_json(value)
        shown = json.dumps(parsed, ensure_ascii=False, indent=2, allow_nan=False)
    except (ValueError, TypeError):
        shown = value
    # JSON is displayed as escaped text in <pre>, never interpolated in a script.
    return (
        '<details class="contract"><summary>'
        + esc(label)
        + "</summary><pre>"
        + esc(shown)
        + "</pre></details>"
    )


def links(ids, index):
    result = []
    for ident in ids:
        stage = index.get(ident)
        if stage:
            result.append(
                '<a class="ref" href="#item-'
                + esc(ident)
                + '" data-open-stage="'
                + stage
                + '">'
                + esc(ident)
                + "</a>"
            )
        else:
            result.append(esc(ident))
    return " ".join(result)


def metadata(item):
    hypotheses = sorted(
        {s["file"] for s in item["sources"] if s["type"] == "hypothesis"}
    )
    custom = []
    for note in item["assumptions"]:
        match = re.match(r"^(H[1-9]\d*)(?::|\b)", note)
        if not match or match.group(1) not in hypotheses:
            custom.append(note)
    body = field("Reasoning", item["reasoning"])
    if hypotheses:
        body += (
            "<h4>Assumption ledger</h4><p>"
            + "".join(
                '<a class="ref" href="#assumption-'
                + esc(h)
                + '" data-central="assumptions">'
                + esc(h)
                + "</a> "
                for h in hypotheses
            )
            + "</p>"
        )
    body += field("Item assumptions", custom)
    context = [s for s in item["sources"] if s["type"] != "hypothesis"]
    body += "<h4>Sources</h4>" + listing(
        [s["type"] + " / " + s["file"] + ": " + s["passage"] for s in context]
    )
    return (
        '<details class="metadata"><summary>Reasoning &amp; provenance</summary>'
        + body
        + "</details>"
    )


def task_tree(items):
    tasks = [i for i in items if i["kind"] == "task"]
    children = {}
    for item in tasks:
        children.setdefault(item["data"]["parentId"], []).append(item)

    def branch(parent):
        return (
            "<ul>"
            + "".join(
                '<li><a href="#item-'
                + esc(i["id"])
                + '">'
                + esc(i["id"])
                + " · "
                + esc(i["title"])
                + "</a> "
                + badge(i["data"]["mode"])
                + branch(i["id"])
                + "</li>"
                for i in children.get(parent, [])
            )
            + "</ul>"
            if parent in children
            else ""
        )

    return '<div class="overview tree"><h3>Outcome tree</h3>' + branch("") + "</div>"


def workflow_edges(items):
    rows = []
    for item in items:
        state = design_io.parse_json(item["description"])
        for edge in state["transitions"]:
            rows.append(
                "<tr><td>"
                + esc(item["id"])
                + " → "
                + esc(edge["to"])
                + "</td><td>"
                + esc(edge["when"])
                + "</td><td>"
                + esc(edge["mode"])
                + "</td></tr>"
            )
    if not rows:
        return '<div class="overview"><h3>Workflow</h3><p>This workflow has a terminal entry state and no outgoing edges.</p></div>'
    return (
        '<div class="overview"><h3>Guarded edges</h3><div class="table-scroll"><table><thead><tr><th>Edge</th><th>Predicate</th><th>Mode</th></tr></thead><tbody>'
        + "".join(rows)
        + "</tbody></table></div></div>"
    )


def fmea_overview(items):
    rows = []
    for item in items:
        d = item["data"]
        rpn = d["severity"] * d["occurrence"] * d["detection"]
        rows.append(
            '<tr><td><a href="#item-'
            + esc(item["id"])
            + '">'
            + esc(item["id"])
            + "</a></td><td>"
            + esc(item["title"])
            + "</td><td>"
            + str(d["severity"])
            + "</td><td>"
            + str(d["occurrence"])
            + "</td><td>"
            + str(d["detection"])
            + "</td><td><strong>"
            + str(rpn)
            + "</strong></td></tr>"
        )
    return (
        '<div class="overview"><h3>Risk register</h3><p class="muted">RPN = severity × occurrence × detection. Scores prioritize proposed risks; they are not measured probabilities or accepted risk.</p><div class="table-scroll"><table><thead><tr><th>ID</th><th>Failure</th><th>S</th><th>O</th><th>D</th><th>RPN</th></tr></thead><tbody>'
        + "".join(rows)
        + "</tbody></table></div></div>"
    )


def coverage(design):
    evals = design["stages"]["evals"]["items"]
    risks = design["stages"]["fmea"]["items"]
    categories = ("golden", "offline", "online", "release")
    counts = {c: sum(e["data"]["category"] == c for e in evals) for c in categories}
    chips = "".join(badge(c + ": " + str(counts[c])) for c in categories)
    rows = []
    for risk in risks:
        matched = [e for e in evals if risk["id"] in e["data"]["failureModeIds"]]
        rows.append(
            "<tr><td>"
            + esc(risk["id"])
            + "</td>"
            + "".join(
                "<td>"
                + esc(
                    ", ".join(e["id"] for e in matched if e["data"]["category"] == c)
                    or "—"
                )
                + "</td>"
                for c in categories
            )
            + "</tr>"
        )
    high = [
        i
        for i in design["stages"]["tasks"]["items"]
        if i["kind"] == "task"
        and i["data"]["mode"] == "leaf"
        and i["data"]["risk"] == "high"
    ]
    high_rows = "".join(
        "<li>"
        + esc(t["id"])
        + ": "
        + esc(
            ", ".join(
                e["id"]
                for e in evals
                if e["data"]["category"] == "golden" and t["id"] in e["data"]["taskIds"]
            )
            or "No linked golden"
        )
        + "</li>"
        for t in high
    )
    return (
        '<div class="overview"><h3>Planned evaluation coverage</h3><p>'
        + chips
        + '</p><p class="muted">Links describe planned coverage. They do not prove that fixtures or business controls have been executed.</p><div class="table-scroll"><table><thead><tr><th>Failure</th>'
        + "".join("<th>" + c.title() + "</th>" for c in categories)
        + "</tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table></div>"
        + (
            "<h4>High-risk leaves → golden cases</h4><ul>" + high_rows + "</ul>"
            if high
            else ""
        )
        + "</div>"
    )


def render_item(item, stage, index):
    d = item["data"]
    top = badge(item["id"]) + badge(item["kind"])
    for key in ("category", "group", "mode", "risk", "tier"):
        if d.get(key):
            top += badge(d[key])
    body = (
        '<article class="card" id="item-'
        + esc(item["id"])
        + '"><div class="chips">'
        + top
        + "</div>"
        + text(item["title"], "h3")
    )
    if stage != "workflow":
        body += prose(item["description"])
    if d.get("taskIds"):
        body += (
            '<p class="refs"><span>Tasks</span> ' + links(d["taskIds"], index) + "</p>"
        )
    if stage == "context":
        if d["value"] != item["description"]:
            body += field(d["field"], d["value"])
    elif stage == "tasks":
        if item["kind"] == "attribute":
            body += field("Source system", d["sourceSystem"]) + field(
                "Loaded", d["loaded"]
            )
        else:
            body += field("Autonomy", d["autonomy"])
            body += (
                "<details><summary>Basis, examples &amp; frequency</summary>"
                + field("Parent", d["parentId"])
                + field("Basis", d["basis"])
                + field("Examples", d["examples"])
                + field("Frequency", d["frequency"])
                + "</details>"
            )
    elif stage == "components":
        for key in ("inputs", "outputs"):
            compact = len(d[key]) <= 6 and sum(map(len, d[key])) < 900
            body += (
                '<details class="contract"'
                + (" open" if compact else "")
                + "><summary>"
                + key.title()
                + " · typed contract</summary>"
                + listing(d[key], code=True)
                + "</details>"
            )
        body += field("Why code / bounded judgement", d["whyCode"]) + field(
            "Approval rule", d["approvalRule"]
        )
    elif stage == "workflow":
        w = design_io.parse_json(item["description"])
        body += (
            field("State", w["state"])
            + "<p>Component "
            + links([d["componentId"]], index)
            + "</p>"
        )
        if not w["transitions"]:
            body += badge("Terminal") + field(
                "Terminal disposition", w["terminalDisposition"]
            )
        body += '<details class="contract"><summary>Recovery, guards &amp; state contract</summary>'
        for key, value in w.items():
            if key == "transitions":
                continue
            if isinstance(value, (dict, list)):
                body += json_detail(
                    key, json.dumps(value, ensure_ascii=False, allow_nan=False)
                )
            else:
                body += field(
                    re.sub(r"([a-z])([A-Z])", r"\1 \2", key).capitalize(), value
                )
        body += field("Concrete trace", d["example"]) + "</details>"
    elif stage == "framework":
        for key, label in [
            ("choice", "Chosen pattern"),
            ("alternatives", "Rejected alternatives"),
            ("tradeoffs", "Tradeoffs"),
            ("permission", "Permission"),
            ("blastRadius", "Blast radius"),
            ("approvalRule", "Approval rule"),
            ("leastPrivilege", "Least privilege"),
        ]:
            body += field(label, d[key])
        body += (
            "<details><summary>Deployment and data alternatives</summary>"
            + "".join(
                field(label, d[key])
                for key, label in [
                    ("aws", "AWS"),
                    ("gcp", "GCP"),
                    ("azure", "Azure"),
                    ("openSource", "Open source / local"),
                ]
            )
            + "</details>"
        )
    elif stage == "models":
        body += "<p>Component " + links([d["componentId"]], index) + "</p>"
        for key, label in [
            ("rationale", "Allocation rationale"),
            ("callsPerCase", "Calls per case"),
            ("inputTokens", "Input tokens / call"),
            ("outputTokens", "Output tokens / call"),
            ("inputPrice", "Input USD / million tokens"),
            ("outputPrice", "Output USD / million tokens"),
            ("fineTuneWhen", "Fine-tuning gate"),
        ]:
            body += field(label, d[key])
        body += '<p class="muted">Budgets are illustrative unless source evidence says measured. Zero prices mean unpriced, not free; hosting and human costs may be excluded.</p>'
    elif stage == "fmea":
        body += (
            '<div class="chips">'
            + badge("RPN " + str(d["severity"] * d["occurrence"] * d["detection"]))
            + badge("Accepted risk: " + str(d["acceptedRisk"]).lower())
            + "</div>"
        )
        for key, label in [
            ("effect", "Effect"),
            ("cause", "Cause"),
            ("control", "Control"),
            ("detectionMethod", "Detection"),
            ("action", "Owner / action / release gate"),
            ("metric", "Metric"),
            ("kpi", "Protected KPI"),
        ]:
            body += field(label, d[key])
        body += (
            "<p>Components "
            + links(d["componentIds"], index)
            + "</p><p>Evaluations "
            + links(d["evalIds"], index)
            + "</p>"
        )
    elif stage == "evals":
        body += field("Target / pass threshold", d["target"]) + field(
            "Metric", d["metric"]
        )
        body += (
            "<p>Failures "
            + links(d["failureModeIds"], index)
            + "</p><p>Components "
            + links(d["componentIds"], index)
            + "</p>"
        )
        body += (
            json_detail("Input fixture / specification", d["input"])
            + json_detail("Expected outcome", d["expected"])
            + json_detail("Pass assertions", d["passRule"])
        )
        body += (
            "<details><summary>Dataset, labels &amp; operating signal</summary>"
            + "".join(
                field(label, d[key])
                for key, label in [
                    ("kpi", "Business KPI"),
                    ("testSet", "Test set"),
                    ("labelling", "Labelling"),
                    ("cadence", "Cadence"),
                    ("alertThreshold", "Alert threshold"),
                ]
            )
            + "</details>"
        )
    elif stage == "rollout":
        for key, label in [
            ("businessKpi", "Business KPI"),
            ("aiMetrics", "AI / operating metrics"),
            ("phase", "Phase"),
            ("gate", "Entry / exit / stop gates"),
            ("owner", "Proposed owner"),
            ("experiment", "Experiment"),
        ]:
            body += field(label, d[key])
    elif stage == "export":
        body += field("Acceptance criteria", d["acceptanceCriteria"]) + field(
            "Build instructions", d["buildInstructions"]
        )
    return body + metadata(item) + "</article>"


def central_assumptions(design):
    entries = design["assumptions"]
    content = ""
    for a in entries:
        content += (
            '<article class="ledger-entry" id="assumption-'
            + esc(a["id"])
            + '">'
            + badge(a["id"])
            + badge("Launch blocker" if a["launchBlocker"] else "Proposed default")
            + text(a["statement"], "h3")
        )
        content += (
            field("Why", a["why"])
            + field("Proposed owner", a["owner"])
            + field("Verify before use", a["validation"])
            + "</article>"
        )
    if not content:
        content = "<p>No top-level assumptions were recorded.</p>"
    return (
        '<details class="central" id="assumptions"><summary>Assumptions &amp; launch dependencies <span>'
        + str(len(entries))
        + " recorded</span></summary>"
        + content
        + "</details>"
    )


def central_review(review, result):
    content = text(
        "Method: "
        + review["method"]
        + " · round "
        + str(review["round"])
        + ". Scores are supplied design judgements, not measured accuracy or operational approval."
    )
    content += (
        '<div class="score-grid">'
        + "".join(
            "<div>"
            + badge(d["id"] + " · " + str(d["score"]) + "/4")
            + listing(d["evidence"])
            + "</div>"
            for d in review["dimensions"]
        )
        + "</div>"
    )
    content += "<h3>Findings</h3>"
    if not review["issues"]:
        content += "<p>No findings were recorded by this reviewer.</p>"
    for issue in review["issues"]:
        content += (
            '<div class="ledger-entry">'
            + badge(issue["id"])
            + badge(issue["severity"])
            + badge("Resolved" if issue["resolved"] else "Open")
            + text(issue["stage"] + " / " + issue["itemId"])
            + text(issue["message"])
            + "</div>"
        )
    content += "<h3>Limitations</h3>" + listing(
        list(dict.fromkeys(review["limitations"] + design_io.LIMITATIONS))
    )
    return (
        '<details class="central" id="review"'
        + (" open" if result["status"] != "pass" else "")
        + "><summary>Review &amp; limitations <span>"
        + esc(result["status"])
        + "</span></summary>"
        + content
        + "</details>"
    )


CSS = r"""
:root{color-scheme:light;--bg:#f3f7f1;--paper:#fff;--ink:#20362a;--muted:#62746a;--line:#dce6da;--green:#2e6543;--tint:#e5efdf}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.6 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}a{color:var(--green);text-underline-offset:3px}a:focus-visible,summary:focus-visible{outline:3px solid #82ac71;outline-offset:4px}header{max-width:1530px;margin:auto;padding:38px 38px 24px}h1{font-size:clamp(26px,3.1vw,40px);line-height:1.18;letter-spacing:-.035em;margin:14px 0}h2{font-size:27px;line-height:1.25;margin:0 0 8px}h3{font-size:18px;line-height:1.4;margin:10px 0}h4{font-size:13px;letter-spacing:.03em;color:var(--muted);margin:18px 0 5px}p{white-space:pre-wrap;margin:8px 0;overflow-wrap:anywhere}ul{padding-left:22px}li{margin:5px 0;overflow-wrap:anywhere}.eyebrow{font-size:12px;text-transform:uppercase;letter-spacing:.12em;color:var(--green);font-weight:700}.notice{border-left:3px solid #88aa72;padding:8px 14px;background:var(--tint);border-radius:0 12px 12px 0}.layout{display:grid;grid-template-columns:228px minmax(0,1fr);gap:28px;max-width:1530px;margin:auto;padding:0 38px 50px}nav{position:sticky;top:20px;align-self:start;display:flex;flex-direction:column;gap:5px;padding:12px;background:#eaf1e5;border:1px solid var(--line);border-radius:20px}nav a{display:flex;gap:10px;align-items:center;text-decoration:none;padding:10px;border-radius:12px;color:var(--muted);font-size:14px}nav a[aria-current="step"]{background:var(--paper);color:var(--green);box-shadow:0 1px 4px #213b2510;font-weight:650}.nav-num{font-size:11px;min-width:22px;opacity:.7}.nav-count{margin-left:auto;font-size:11px}main{min-width:0}.stage-head{margin:10px 0 22px}.stage-head p,.muted{color:var(--muted)}.card,.overview{padding:26px 30px;background:var(--paper);border:1px solid var(--line);border-radius:22px;margin:16px 0;min-width:0}.overview{background:#edf4e8}.chips{display:flex;flex-wrap:wrap;gap:5px}.badge{display:inline-block;font-size:11px;line-height:1.45;font-weight:650;padding:4px 8px;border-radius:7px;background:var(--tint);color:var(--green);margin:0 5px 5px 0;overflow-wrap:anywhere}.refs span{color:var(--muted);font-size:12px}.ref{display:inline-block;font-size:12px;margin:3px 5px 3px 0}details{margin:15px 0;border-top:1px solid var(--line);padding-top:12px}summary{cursor:pointer;font-size:13px;font-weight:650;color:var(--green);overflow-wrap:anywhere}details[open]>summary{margin-bottom:12px}.central{background:var(--paper);padding:15px 22px;border:1px solid var(--line);border-radius:16px;margin:12px 0}.central>summary{font-size:14px}.central>summary span{font-size:11px;float:right;color:var(--muted)}.ledger-entry{border-top:1px solid var(--line);padding:18px 0}.ledger-entry:first-of-type{margin-top:16px}.score-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}.score-grid>div{padding:14px;background:var(--bg);border-radius:12px;font-size:13px}.contract code{white-space:pre-wrap;overflow-wrap:anywhere;font-size:12px}.contract ul{padding-left:18px}pre{margin:10px 0;background:#f2f5ef;border-radius:12px;padding:18px;white-space:pre-wrap;overflow-wrap:anywhere;font-size:12px;max-height:560px;overflow:auto}.table-scroll{max-width:100%;overflow-x:auto}table{width:100%;border-collapse:collapse;font-size:13px}th,td{text-align:left;padding:11px 10px;border-bottom:1px solid var(--line);vertical-align:top;overflow-wrap:anywhere}th{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.04em}.tree ul{list-style:none;border-left:1px solid #b7cdb0;margin:10px 0;padding-left:18px}.tree a{text-decoration:none}.tree>ul{border:0;padding:0}.stage-footer{font-size:12px;color:var(--muted);padding:20px 0}footer{max-width:1530px;margin:auto;padding:0 38px 35px;font-size:12px;color:var(--muted)}[hidden]{display:none!important}:target{scroll-margin-top:28px}@media(min-width:1500px){.card{padding:30px 38px}}@media(max-width:820px){header{padding:24px 20px 12px}.layout{display:block;padding:0 20px 30px}nav{position:sticky;top:0;z-index:5;flex-direction:row;overflow-x:auto;gap:4px;border-radius:14px;padding:7px;margin-bottom:22px;backdrop-filter:blur(12px)}nav a{flex-shrink:0;padding:8px 10px;gap:5px}.nav-count{display:none}.card,.overview{padding:20px;border-radius:17px}.score-grid{grid-template-columns:1fr}h2{font-size:24px}.central{padding:13px 16px}footer{padding:0 20px 25px}.central>summary span{float:none;margin-left:8px}:target{scroll-margin-top:80px}}@media print{nav{display:none}.layout{display:block;padding:0}header,footer{padding:10px}.card,.overview,.central{break-inside:avoid;border-radius:0}.table-scroll,pre{overflow:visible;max-height:none}section[hidden]{display:block!important}body{background:#fff}a{color:inherit}}
"""

JS = r"""
(() => {
  "use strict";
  const panels = Array.from(document.querySelectorAll("[data-stage-panel]"));
  const navigation = Array.from(document.querySelectorAll("nav [data-stage]"));
  function activate(key) {
    if (!panels.some(panel => panel.dataset.stagePanel === key)) return;
    panels.forEach(panel => { panel.hidden = panel.dataset.stagePanel !== key; });
    navigation.forEach(link => {
      if (link.dataset.stage === key) link.setAttribute("aria-current", "step");
      else link.removeAttribute("aria-current");
    });
  }
  function revealHash() {
    let id;
    try { id = decodeURIComponent(location.hash.slice(1)); } catch (_) { return; }
    const target = document.getElementById(id);
    if (!target) return;
    const panel = target.closest("[data-stage-panel]");
    if (panel) activate(panel.dataset.stagePanel);
    const details = target.closest("details");
    if (details) details.open = true;
  }
  document.addEventListener("click", event => {
    const link = event.target.closest("a[data-stage], a[data-open-stage], a[data-central]");
    if (!link) return;
    if (link.dataset.stage) activate(link.dataset.stage);
    if (link.dataset.openStage) activate(link.dataset.openStage);
    if (link.dataset.central) {
      const details = document.getElementById(link.dataset.central);
      if (details) details.open = true;
    }
  });
  window.addEventListener("hashchange", revealHash);
  window.addEventListener("beforeprint", () => panels.forEach(panel => { panel.hidden = false; }));
  window.addEventListener("afterprint", () => { activate("context"); revealHash(); });
  activate("context");
  revealHash();
})();
"""


def render_html(design, review):
    structural = design_io.validate_design(design)
    checked_review = design_io.validate_review(review, structural["valid"])
    if not structural["valid"] or not checked_review["valid"]:
        raise ValueError(
            "HTML requires valid canonical design and review: "
            + json.dumps(
                structural["errors"] + checked_review["errors"], ensure_ascii=False
            )
        )
    index = {
        item["id"]: stage
        for stage in STAGES
        for item in design["stages"][stage]["items"]
    }
    nav = "".join(
        '<a href="#stage-'
        + key
        + '" data-stage="'
        + key
        + '"><span class="nav-num">'
        + f"{i + 1:02d}"
        + "</span>"
        + label
        + '<span class="nav-count">'
        + str(len(design["stages"][key]["items"]))
        + "</span></a>"
        for i, (key, label) in enumerate(zip(STAGES, LABELS))
    )
    panels = []
    for number, (key, label, intro) in enumerate(zip(STAGES, LABELS, INTROS), 1):
        packet = design["stages"][key]
        content = ""
        if key == "tasks":
            content += task_tree(packet["items"])
        if key == "workflow":
            content += workflow_edges(packet["items"])
        if key == "fmea":
            content += fmea_overview(packet["items"])
        if key == "evals":
            content += coverage(design)
        if key == "models" and not packet["items"]:
            content += '<div class="overview"><h3>Zero LLM components</h3><p>No model calls or model token spend are allocated. The chosen workflow is code-only. This does not imply zero hosting, storage or human operating cost.</p></div>'
        content += "".join(render_item(i, key, index) for i in packet["items"])
        if packet["assumptions"]:
            content += (
                '<details class="central"><summary>Stage assumptions</summary>'
                + listing(packet["assumptions"])
                + "</details>"
            )
        panels.append(
            '<section id="stage-'
            + key
            + '" data-stage-panel="'
            + key
            + '" aria-labelledby="heading-'
            + key
            + '"><div class="stage-head"><div class="eyebrow">Stage '
            + str(number)
            + ' / 10</div><h2 id="heading-'
            + key
            + '">'
            + label
            + "</h2>"
            + text(intro)
            + "</div>"
            + content
            + '<div class="stage-footer">Read-only proposed design · '
            + str(len(packet["items"]))
            + " cards · no workflow execution</div></section>"
        )
    # No design JSON is embedded in executable JS, so </script>, U+2028 and
    # U+2029 from inputs are inert escaped HTML text, not script delimiters.
    return (
        "<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"><meta http-equiv=\"Content-Security-Policy\" content=\"default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src 'none'; connect-src 'none'; font-src 'none'; base-uri 'none'; form-action 'none'\"><title>"
        + esc(design["title"])
        + " · Design view</title><style>"
        + CSS
        + '</style></head><body><header><div class="eyebrow">Agent Design Studio · optional visual handoff</div><h1>'
        + esc(design["title"])
        + '</h1><p class="notice"><strong>DESIGN ONLY · '
        + esc(checked_review["status"].upper())
        + '</strong> · Read-only generated view. Review scores and planned tests are not operational approval or proof of executed business controls.</p><details class="central"><summary>Original brief</summary>'
        + text(design["brief"])
        + "</details>"
        + central_assumptions(design)
        + central_review(review, checked_review)
        + '</header><div class="layout"><nav aria-label="Design stages">'
        + nav
        + "</nav><main>"
        + "".join(panels)
        + "</main></div><footer>Self-contained local HTML · no network assets, model calls or action controls. Canonical design.json and review.json remain the source of truth.</footer><script>"
        + JS
        + "</script></body></html>\n"
    )


def _write_new(path, content, inputs):
    """Exclusive-create only; never replace an input, alias or existing file."""
    path = Path(path).absolute()
    if path.suffix.lower() not in (".html", ".htm"):
        raise ValueError("Output must have an .html or .htm suffix.")
    if path.is_symlink():
        raise ValueError("Output must not be a symlink: " + str(path))
    if path.resolve() in {Path(p).resolve() for p in inputs}:
        raise ValueError("Output must not alias a canonical input.")
    if path.exists():
        raise ValueError(
            "Refusing to overwrite an existing output, including hardlink aliases: "
            + str(path)
        )
    if not path.parent.is_dir():
        raise ValueError(
            "Output parent directory must already exist: " + str(path.parent)
        )
    # Resolve the existing parent once: system temp aliases such as macOS /var
    # are valid destinations. The final component remains exclusive-create, so
    # neither a parent alias nor a racing final symlink can replace input data.
    path = path.parent.resolve(strict=True) / path.name
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    fd = None
    created = None
    done = False
    try:
        fd = os.open(path, flags, 0o600)
        created = os.fstat(fd)
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            fd = None
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        done = True
    finally:
        if fd is not None:
            os.close(fd)
        if created is not None and not done:
            try:
                current = path.lstat()
                if (
                    current.st_dev == created.st_dev
                    and current.st_ino == created.st_ino
                ):
                    path.unlink()
            except OSError:
                pass
    return path


def export_html(design_path, review_path, out):
    design = design_io.load_json(design_path)
    review = design_io.load_json(review_path)
    document = render_html(design, review)
    path = _write_new(out, document, (design_path, review_path))
    return {
        "ok": True,
        "designOnly": True,
        "optionalVisualView": True,
        "status": design_io.validate_review(review)["status"],
        "output": str(path),
        "bytes": len(document.encode("utf-8")),
        "sha256": hashlib.sha256(document.encode("utf-8")).hexdigest(),
        "limitations": design_io.LIMITATIONS,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("design", type=Path)
    parser.add_argument("--review", type=Path, required=True)
    parser.add_argument(
        "--out",
        type=Path,
        required=True,
        help="New HTML file; existing files and final symlinks are refused.",
    )
    args = parser.parse_args(argv)
    try:
        result = export_html(args.design, args.review, args.out)
    except (OSError, ValueError, UnicodeError) as exc:
        print(
            json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False),
            file=sys.stderr,
        )
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
