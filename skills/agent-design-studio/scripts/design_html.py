#!/usr/bin/env python3
"""Read-only, self-contained HTML view of a validated design (schema 1.0 or 1.1).

Standard library only. Renders twelve views: the Decision brief, the ten design
steps and an Evidence group (Assumptions, Review). The task tree is a CSS grid and
the flow is inline SVG, both built in Python from design.json; nothing is drawn
from the reference files' data. The page loads no network asset, calls no model,
executes no workflow and offers no approval control. All design and review text
is HTML-escaped; the embedded script holds no design data.
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


def _load(name):
    spec = importlib.util.spec_from_file_location(
        "_agent_design_html_" + name, Path(__file__).with_name(name + ".py")
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


design_io = _load("design_io")
report = _load("report_v2")

STAGES = design_io.STAGES
STEPS = report.STEPS
BRIEF_STEP = report.BRIEF_STEP
EVIDENCE_STEPS = report.EVIDENCE_STEPS
STEP_BY_KEY = {row[0]: row for row in STEPS + (BRIEF_STEP,) + EVIDENCE_STEPS}
VIEW_ORDER = ("brief",) + tuple(row[0] for row in STEPS) + ("assumptions", "review")
LITE_VIEWS = ("brief", "tasks", "workflow", "fmea")
MODES = ("lite", "standard", "full")
RUBRIC_PATH = Path(__file__).resolve().parents[1] / "references" / "quality-rubric.json"
GROUP_TYPE = {
    "Agents (LLM)": "llm",
    "Code: tools": "read",
    "Code: validation": "code",
    "Code: human triggers": "human",
}
TYPE_NAME = {
    "llm": "LLM agent",
    "code": "Code: validation",
    "read": "Code: tool",
    "write": "Code: write tool",
    "rag": "Retrieval",
    "human": "Human trigger",
    "decision": "Decision",
}
MODE_TEXT = {"sequence": "sequence: all run", "choose one": "choose one per case", "leaf": "leaf"}
LEVEL_TEXT = {"acts alone": "Acts alone", "suggests": "Suggests", "human decides": "Human decides"}
VOLUME_WORDS = r"(?:text\s+)?(?:cases|claims|requests|complaints|reports|tickets|conversations|runs|jobs|orders|interactions|messages|applications)"
VOLUME_RE = re.compile(
    r"(\d{1,3}(?:[, ]\d{3})+|\d+)\s*" + VOLUME_WORDS + r"\s*(?:/|per|a|each|every)\s*month", re.I
)
RANGE_RE = re.compile(r"(?<![\w.])([^;:\n]{1,32}?)\s*(?:→|->)\s*([^;:\n(]{1,32}?)(?=[\s;,.(]|$)")


# ---------------------------------------------------------------- text helpers
def esc(value):
    """All design/review text passes through HTML escaping, never JS source."""
    if value is None:
        return "—"
    if isinstance(value, bool):
        value = "true" if value else "false"
    return html.escape(str(value), quote=True)


def plain(value):
    """Reader-facing glossary substitution; contracts are never rewritten."""
    return report.plain(str(value))


def _pieces(word, width):
    """Split an over-long token after punctuation where possible, never dropping text."""
    out = []
    while len(word) > width:
        cut = max(word.rfind(ch, 1, width) for ch in ",;|/)}]")
        if cut < width // 3:
            cut = width - 1
        out.append(word[: cut + 1])
        word = word[cut + 1 :]
    out.append(word)
    return out


def wrap(text, width):
    """Word-wrap into lines of at most `width` characters; nothing is dropped."""
    lines, current = [], ""
    for word in str(text).split():
        for part in _pieces(word, width):
            if not current:
                current = part
            elif len(current) + 1 + len(part) <= width:
                current += " " + part
            else:
                lines.append(current)
                current = part
    if current:
        lines.append(current)
    return lines or [""]


def chip(label, kind=None, mono=False, attrs=""):
    cls = "chip"
    dot = ""
    if kind:
        cls += " ty tag-" + kind
        dot = '<span class="d"></span>'
    if mono:
        cls += " mono"
    return f'<span class="{cls}"{attrs}>{dot}{esc(label)}</span>'


def type_chip(kind):
    return chip(TYPE_NAME.get(kind, kind), kind)


def money(value):
    if value == 0:
        return "0"
    if value < 0.01:
        return f"{value:.4f}"
    if value < 1:
        return f"{value:.3f}"
    return f"{value:,.2f}"


def kv_rows(pairs):
    body = ""
    for label, value in pairs:
        if value in ("", None, []):
            continue
        body += f"<dt>{esc(label)}</dt><dd>{value}</dd>"
    return f'<dl class="kv">{body}</dl>' if body else ""


def bullet_list(values, cls=""):
    if not values:
        return '<span class="mini">None</span>'
    return (
        f'<ul class="{cls}">'
        + "".join(f"<li>{esc(v)}</li>" for v in values)
        + "</ul>"
    )


def pretty_json(value):
    try:
        parsed = design_io.parse_json(value) if isinstance(value, str) else value
        return json.dumps(parsed, ensure_ascii=False, indent=2, allow_nan=False)
    except (ValueError, TypeError):
        return str(value)


# ---------------------------------------------------------------------- model
class Model:
    """Precomputed lookups over one validated design, review and mode."""

    def __init__(self, design, review, mode, rounds=()):
        self.d = design
        self.review = review
        self.mode = mode
        self.rounds = [r for r in rounds if r]
        st = design["stages"]
        self.tasks = [i for i in st["tasks"]["items"] if i["kind"] == "task"]
        self.attrs = [i for i in st["tasks"]["items"] if i["kind"] == "attribute"]
        self.task = {t["id"]: t for t in self.tasks}
        self.children = {}
        for t in self.tasks:
            self.children.setdefault(t["data"]["parentId"], []).append(t)
        roots = self.children.get("", [])
        self.root = roots[0] if roots else None
        self.tops = self.children.get(self.root["id"], []) if self.root else []
        self.leaves = [t for t in self.tasks if t["data"]["mode"] == "leaf"]
        self.comps = st["components"]["items"]
        self.comp = {c["id"]: c for c in self.comps}
        self.nodes = st["workflow"]["items"]
        self.node = {w["id"]: w for w in self.nodes}
        self.contract = {w["id"]: self._contract(w) for w in self.nodes}
        self.fmea = st["fmea"]["items"]
        self.fm = {f["id"]: f for f in self.fmea}
        self.evals = st["evals"]["items"]
        self.framework = st["framework"]["items"]
        self.models = st["models"]["items"]
        self.rollout = st["rollout"]["items"]
        self.export = st["export"]["items"]
        self.ctx = st["context"]["items"]
        sem = design.get("semantics") if isinstance(design.get("semantics"), dict) else {}
        self.has_semantics = bool(sem)
        self.effects = {
            e.get("componentId"): e.get("effect")
            for e in sem.get("componentEffects", [])
            if isinstance(e, dict)
        }
        self.node_kind = {n.get("id"): n.get("kind") for n in sem.get("nodes", []) if isinstance(n, dict)}
        self.outcome = {
            (t.get("from"), t.get("to"), t.get("when")): t.get("outcome")
            for t in sem.get("transitions", [])
            if isinstance(t, dict)
        }
        research = design.get("research")
        self.research = research if isinstance(research, dict) else None
        self.finding = {f["id"]: f for f in (self.research or {}).get("findings", []) if isinstance(f, dict)}
        pres = design.get("presentation")
        self.derived = not isinstance(pres, dict)
        self.pres = pres if isinstance(pres, dict) else {}
        self.brief = report.brief_data(design)
        self.task_labels = self.pres.get("taskLabels", {}) or {}
        self.node_labels = self.pres.get("workflowLabels", {}) or {}
        self.index = {item["id"]: key for key in STAGES for item in st[key]["items"]}
        self.top_cache = {}
        self.rubric_names = self._rubric_names()
        self.volume, self.volume_note = self._volume()
        self.result = design_io.validate_review(review, True)

    @staticmethod
    def _contract(node):
        try:
            value = design_io.parse_json(node["description"])
        except (ValueError, TypeError):
            value = {}
        return value if isinstance(value, dict) else {}

    @staticmethod
    def _rubric_names():
        try:
            rubric = design_io.load_json(RUBRIC_PATH)
            return {d["id"]: d["name"] for d in rubric["dimensions"]}
        except (OSError, ValueError, KeyError, TypeError):
            return {}

    def _volume(self):
        texts = [(h["id"], h["statement"]) for h in self.d["assumptions"]]
        texts += [(c["id"], c["data"]["value"]) for c in self.ctx]
        texts += [(m["id"], m["data"]["rationale"]) for m in self.models]
        for ident, text in texts:
            match = VOLUME_RE.search(text)
            if match:
                number = int(re.sub(r"[^\d]", "", match.group(1)))
                if number > 0:
                    return number, f"Volume {number:,} per month comes from {ident}; it is an assumption, not a measurement."
        return 10000, "Volume 10,000 per month is an illustrative default; no monthly volume was stated in the design."

    # --- labels and links
    def task_label(self, tid):
        return self.task_labels.get(tid) or self.task[tid]["title"]

    def node_label(self, wid):
        return self.node_labels.get(wid) or self.node[wid]["title"]

    def top_of(self, tid):
        if tid in self.top_cache:
            return self.top_cache[tid]
        cursor = tid
        seen = set()
        while cursor in self.task and self.task[cursor]["data"]["parentId"] not in ("", None):
            parent = self.task[cursor]["data"]["parentId"]
            if self.root and parent == self.root["id"]:
                break
            if cursor in seen or parent not in self.task:
                break
            seen.add(cursor)
            cursor = parent
        self.top_cache[tid] = cursor
        return cursor

    def descendants(self, tid):
        out = []
        stack = [tid]
        while stack:
            current = stack.pop()
            out.append(current)
            stack.extend(c["id"] for c in self.children.get(current, []))
        return out

    def comp_type(self, cid):
        comp = self.comp.get(cid)
        if comp is None:
            return "code"
        group = comp["data"]["group"]
        base = GROUP_TYPE.get(group, "code")
        if base != "read":
            return base
        effect = self.effects.get(cid)
        if effect == "write":
            return "write"
        if effect is None and not self.has_semantics:
            text = comp["title"] + " " + comp["description"]
            if re.search(r"\b(write|writer|post|posts|save|saves|send|sends|create|creates|persist|publish|record)\b", text, re.I):
                return "write"
        if re.search(r"\b(retriev|search|clause|knowledge|lookup|index)", comp["title"] + " " + comp["description"], re.I):
            return "rag"
        return "read"

    def rpn(self, item):
        d = item["data"]
        return d["severity"] * d["occurrence"] * d["detection"]

    @staticmethod
    def band(rpn, severity):
        if rpn >= 150 or severity >= 8:
            return "hi"
        if rpn >= 100:
            return "md"
        return "lo"

    def act_now(self, item):
        return self.rpn(item) >= 150 or item["data"]["severity"] >= 8

    def serving_comps(self, tid):
        return [c for c in self.comps if tid in c["data"]["taskIds"]]

    def serving_nodes(self, tid):
        return [w for w in self.nodes if tid in w["data"]["taskIds"]]

    def risk_reason(self, task):
        if task["data"]["risk"] != "high":
            return ""
        ids = set(self.descendants(task["id"]))
        comps = [c for c in self.comps if ids & set(c["data"]["taskIds"])]
        if any(self.comp_type(c["id"]) == "write" for c in comps):
            return "writes records or money"
        if any(c["data"]["group"] == "Code: human triggers" for c in comps):
            return "owns a human decision"
        for attr in self.attrs:
            if ids & set(attr["data"]["taskIds"]) and re.search(
                r"identit|customer|account|auth|subject|member|claimant", attr["title"] + " " + attr["data"]["sourceSystem"], re.I
            ):
                return "acts on identity"
        return "author-rated"

    def link(self, ident):
        """Clickable ID chip that opens the owning view; unknown IDs stay plain."""
        stage = self.index.get(ident)
        if stage == "tasks" and ident in self.task:
            return f'<button type="button" class="chip mono" data-goleaf="{esc(ident)}">{esc(ident)}</button>'
        if stage == "fmea":
            return f'<button type="button" class="chip" data-gofm="{esc(ident)}"><b class="mono">{esc(ident)}</b> {esc(self.fm[ident]["title"])}</button>'
        if stage == "workflow":
            return f'<button type="button" class="chip mono" data-gonode="{esc(ident)}">{esc(ident)}</button>'
        if stage == "components":
            return chip(ident + " " + self.comp[ident]["title"], self.comp_type(ident))
        return chip(ident, mono=True)

    def links(self, ids):
        return '<div class="inline-list">' + ("".join(self.link(i) for i in ids) or '<span class="mini">None</span>') + "</div>"

    def status_line(self):
        r = self.review
        return f'{r["method"]}, round {r["round"]}: {self.result["status"]}. Read-only view. Not approved by stakeholders.'

    def views(self):
        return LITE_VIEWS if self.mode == "lite" else VIEW_ORDER

    def next_view(self, key):
        order = self.views()
        if key in order and order.index(key) + 1 < len(order):
            return order[order.index(key) + 1]
        return None


# ----------------------------------------------------------------- fragments
def head(title, lead):
    return f'<div class="phead"><h2>{esc(title)}</h2></div><p class="lead">{esc(lead)}</p>'


def status_bar(m, key):
    nxt = m.next_view(key)
    button = ""
    if nxt:
        row = STEP_BY_KEY[nxt]
        number = f"{row[1]} " if row[1] is not None and row[1] > 0 else ""
        button = f'<button class="btn small primary" type="button" data-step="{nxt}">Next → {number}{esc(row[3])}</button>'
    return (
        '<div class="statusbar" role="status"><span class="st">Proposed design</span><span class="cnt">'
        + esc(m.status_line())
        + '</span><span class="sp"></span>'
        + button
        + "</div>"
    )


def parse_range(text):
    match = RANGE_RE.search(text or "")
    if not match:
        return None
    baseline, target = match.group(1).strip(" ,;"), match.group(2).strip(" ,;")
    if not baseline or not target or len(baseline) > 32 or len(target) > 32:
        return None
    return baseline, target


def must_hold(pass_rule):
    """Assertions from a golden pass rule; prose rules stay whole."""
    try:
        parsed = design_io.parse_json(pass_rule)
    except (ValueError, TypeError):
        parsed = None
    if not isinstance(parsed, dict):
        return [str(pass_rule)]
    lines = []
    for key, value in parsed.items():
        if isinstance(value, list) and all(isinstance(v, str) for v in value):
            prefix = "Must not: " if key.lower() in ("forbidden", "never", "mustnot", "must_not") else ""
            lines.extend(prefix + v for v in value)
        elif isinstance(value, dict):
            lines.extend(f"{key}.{k} == {json.dumps(v, ensure_ascii=False)}" for k, v in value.items())
        else:
            lines.append(f"{key}: {json.dumps(value, ensure_ascii=False)}")
    return lines or [str(pass_rule)]


# --------------------------------------------------------------------- views
def view_brief(m):
    b = m.brief
    p = m.pres
    calls = "".join(
        f'<li class="panel"><span class="n">{i}</span><div>{esc(plain(c["choice"]))}'
        f'<div class="rej"><b>Rejected:</b> {esc(plain(c["rejected"]).rstrip(". "))}. {esc(plain(c["why"]))}</div></div></li>'
        for i, c in enumerate(b["calls"], 1)
    )
    autonomy = "".join(
        f"<tr><td>{esc(plain(a['action']))}</td><td>{esc(LEVEL_TEXT.get(a['level'], a['level']))}</td></tr>"
        for a in b["autonomy"]
    )
    kpis = ""
    for r in [x for x in m.rollout if x["data"]["category"] == "kpi"]:
        span = parse_range(r["data"]["businessKpi"])
        value = f'{esc(span[0])} → <b>{esc(span[1])}</b>' if span else '<span class="mini">see definition</span>'
        kpis += f'<div class="kpimini"><span>{esc(plain(r["title"]))}</span><span class="v">{value}</span><span class="df">{esc(plain(r["data"]["businessKpi"]))}</span></div>'
    if not kpis:
        kpis = '<p class="mini">No KPI card in the rollout stage.</p>'
    top = sorted(m.fmea, key=m.rpn, reverse=True)[:5]
    risks = "".join(
        f'<div class="blk"><span class="rpn {m.band(m.rpn(f), f["data"]["severity"])} tiny">{m.rpn(f)}</span>'
        f'<span><button type="button" class="chip link" data-gofm="{esc(f["id"])}"><b class="mono">{esc(f["id"])}</b></button> {esc(plain(f["title"]))}'
        f'<span class="o">{esc(plain(f["data"]["control"]))}</span></span></div>'
        for f in top
    )
    blockers = "".join(
        f'<div class="blk"><span class="mono">{esc(h["id"])}</span><span>{esc(plain(h["statement"]))}<span class="o">Owner: {esc(h["owner"])} (proposed)</span></span></div>'
        for h in b["blockers"]
    ) or '<p class="mini">No launch blocker recorded. Confirm missing facts before launch.</p>'
    cost = b["cost"]
    note = "Provider prices are unknown; zero prices mean unpriced, not free." if not b["priced"] else "An estimate from the model budget, not a provider quote."
    if not m.models:
        cost_text = "No model calls: the model budget is zero. Hosting, tools and staff time still cost money."
    else:
        cost_text = f"USD {money(cost)} per case in model calls; about USD {round(cost * m.volume):,} per month at {m.volume:,} cases. {note} {m.volume_note}"
    scope = f'<p class="mini">{esc(plain(p["scopeSummary"]))}</p>' if p.get("scopeSummary") else ""
    derived = (
        '<p class="mini derived">Reader layer derived from the ten stages because this design has no presentation block (schema 1.0 input).</p>'
        if m.derived
        else ""
    )
    return (
        head(m.d["title"], "Page 1 of the report. Everything below is a proposal built from one brief.")
        + f'<p class="sentence">{esc(plain(b["sentence"]))}</p>'
        + scope
        + derived
        + '<div class="brief-grid"><div>'
        + '<h3 class="h3">Key design calls</h3><ol class="calls">'
        + calls
        + "</ol>"
        + '<div class="sec"><h3>Who acts and who decides</h3><div class="tw"><table><thead><tr><th>Action</th><th>Autonomy</th></tr></thead><tbody>'
        + autonomy
        + "</tbody></table></div></div></div>"
        + '<div class="stack">'
        + '<div class="panel box"><h3>How we will know it works</h3>'
        + kpis
        + "</div>"
        + '<div class="panel box"><h3>Top 5 risks</h3>'
        + risks
        + "</div>"
        + '<div class="panel box"><h3>Launch blockers</h3>'
        + blockers
        + "</div>"
        + f'<div class="panel box"><h3>Cost</h3><div class="small">{esc(cost_text)}</div></div>'
        + f'<div class="panel box"><h3>Review</h3><div class="small">{esc(m.status_line())}</div></div>'
        + "</div></div>"
    )


def view_context(m):
    rows = ""
    if m.pres.get("scopeSummary"):
        rows += f'<tr><td class="nowrap"><span class="fm-id">Scope</span> First release</td><td>{esc(plain(m.pres["scopeSummary"]))}</td></tr>'
    for c in m.ctx:
        reading = ""
        if " ".join(c["description"].split()) != " ".join(c["data"]["value"].split()):
            reading = f'<div class="mini">{esc(c["description"])}</div>'
        rows += f'<tr><td class="nowrap"><span class="fm-id">{esc(c["id"])}</span> {esc(c["data"]["field"])}</td><td>{esc(c["data"]["value"])}{reading}</td></tr>'
    return (
        head(STEP_BY_KEY["context"][3], "The brief as given, and how this design reads it. Facts the brief did not give are assumptions with owners.")
        + f'<div class="panel box"><div class="lb">Brief (verbatim)</div><div class="brief-text">{esc(m.d["brief"])}</div></div>'
        + '<div class="sec"><div class="tw"><table><thead><tr><th>Field</th><th>Design reading</th></tr></thead><tbody>'
        + rows
        + "</tbody></table></div></div>"
        + research_section(m)
    )


def research_section(m):
    """Web research the author used, when the design carries a research record."""
    r = m.research
    if r is None:
        return ""
    if not r["performed"]:
        return (
            '<div class="sec"><h3>Research used</h3><div class="panel box"><p class="small">No web research was performed: '
            + esc(r["unavailableReason"])
            + ' Industry facts rest on the author\'s own knowledge and tool candidates are unverified.</p></div></div>'
        )
    rows = "".join(
        f'<tr><td class="mono nowrap">{esc(f["id"])}</td><td>{esc(f["topic"])}</td><td>{esc(f["title"])}<div class="mono tiny" style="color:var(--muted);overflow-wrap:anywhere">{esc(f["url"])}</div></td>'
        f'<td class="mono small nowrap">{esc(f["retrievedAt"])}</td><td>{esc(f["summary"])}</td><td>{m.links(f["usedBy"])}</td></tr>'
        for f in r["findings"]
    ) or '<tr><td colspan="6" class="mini">Research was run but no finding was kept.</td></tr>'
    return (
        f'<div class="sec"><h3>Research used</h3><p class="sub">Web research with {esc(r["tool"])}: {len(r["queries"])} queries, {len(r["findings"])} findings kept. '
        "Findings are the author's summaries of public pages with a retrieval date; they inform the design and do not verify this organisation's own policies, contracts or systems.</p>"
        '<div class="tw"><table><thead><tr><th>ID</th><th>Topic</th><th>Source</th><th>Retrieved</th><th>What it says</th><th>Used by</th></tr></thead><tbody>'
        + rows
        + "</tbody></table></div></div>"
    )


def basis_kind(text):
    if re.search(r"\b(llm|model|judg|draft|explain)", text, re.I):
        return "llm"
    if re.search(r"human|supervisor|staff|approv|operator|reviewer|officer", text, re.I):
        return "human"
    if re.search(r"policy|lookup|search|retriev|clause", text, re.I):
        return "rag"
    return "code"


def leaf_card(m, task, selected, top_box=False):
    d = task["data"]
    reason = m.risk_reason(task)
    basis = d["basis"]
    short = all(len(b) <= 40 for b in basis)
    basis_html = (
        '<div class="bs">' + "".join(chip(b, basis_kind(b)) for b in basis) + "</div>"
        if short
        else '<div class="exs basis">' + "".join(f"<div>{esc(b)}</div>" for b in basis) + "</div>"
    )
    examples = "".join(f"<div>{esc(e)}</div>" for e in d["examples"][:2])
    risk = f'<span class="risk-{d["risk"]}">{esc(d["risk"])} risk</span>' + (f' <span class="why-r">({esc(reason)})</span>' if reason else "")
    cls = "leaf top-leaf" if top_box else "leaf"
    return (
        f'<div role="button" tabindex="0" class="{cls}" data-leaf="{esc(task["id"])}" aria-selected="{"true" if selected else "false"}">'
        + (f'<div class="id">{esc(task["id"])}</div><div class="nm">{esc(m.task_label(task["id"]))}</div><span class="mode">leaf</span>' if top_box else f'<div><span class="fm-id">{esc(task["id"])}</span> <span class="ln">{esc(m.task_label(task["id"]))}</span></div>')
        + basis_html
        + (f'<div class="exs">{examples}</div>' if examples else "")
        + f'<div class="meta">{esc(d["autonomy"])}</div><div class="meta">{risk}</div></div>'
    )


def leaf_detail(m, task, hidden):
    d = task["data"]
    parent = m.task.get(d["parentId"])
    crumb = (f'{esc(parent["id"])} {esc(m.task_label(parent["id"]))} › ' if parent else "") + esc(task["id"])
    comps = m.serving_comps(task["id"])
    fms = [f for f in m.fmea if task["id"] in f["data"]["taskIds"]]
    risk = f'<span class="risk-{d["risk"]}">{esc(d["risk"])}</span>' + (f" ({esc(m.risk_reason(task))})" if m.risk_reason(task) else "")
    return (
        f'<div class="panel detail" data-leaf-detail="{esc(task["id"])}"{" hidden" if hidden else ""}>'
        + f'<div class="crumb">{crumb}</div><h3>{esc(m.task_label(task["id"]))}</h3>'
        + kv_rows(
            [
                ("What it does", esc(task["description"])),
                ("Resolved by", '<div class="inline-list">' + "".join(chip(b, basis_kind(b)) for b in d["basis"]) + "</div>"),
                ("Examples", '<div class="quotes">' + "".join(f'<div class="q">{esc(e)}</div>' for e in d["examples"]) + "</div>"),
                ("Autonomy", esc(d["autonomy"])),
                ("Frequency · risk", esc(d["frequency"]) + " · " + risk),
                ("Components", '<div class="inline-list">' + ("".join(chip(c["id"] + " " + c["title"], m.comp_type(c["id"])) for c in comps) or '<span class="mini">None</span>') + "</div>"),
                ("Failure modes", m.links([f["id"] for f in fms])),
            ]
        )
        + f'<div class="dtools"><button class="btn small" type="button" data-showwf="{esc(m.top_of(task["id"]))}">Show in flow</button></div></div>'
    )


def view_tasks(m):
    leaves = m.leaves
    high = [t for t in leaves if t["data"]["risk"] == "high"]
    first = leaves[0]["id"] if leaves else ""
    root = m.root
    root_html = (
        f'<div class="root">{esc(m.task_label(root["id"]))}<small>{esc(MODE_TEXT.get(root["data"]["mode"], root["data"]["mode"]))} · {len(m.tops)} tasks</small></div><div class="stem"></div>'
        if root
        else ""
    )
    columns = ""
    for top in m.tops:
        kids = m.children.get(top["id"], [])
        if top["data"]["mode"] == "leaf" and not kids:
            box = leaf_card(m, top, top["id"] == first, top_box=True)
            subs = ""
        else:
            box = f'<div class="tbox"><div class="id">{esc(top["id"])}</div><div class="nm">{esc(m.task_label(top["id"]))}</div><span class="mode">{esc(MODE_TEXT.get(top["data"]["mode"], top["data"]["mode"]))}</span></div>'
            subs = '<div class="subs">' + "".join(leaf_card(m, k, k["id"] == first) for k in kids) + "</div>"
        columns += f'<div class="tcol">{box}{subs}</div>'
    n = max(1, len(m.tops))
    tree = (
        f'<div class="tree-wrap panel"><div class="tree2" style="min-width:{max(720, n * 210)}px">'
        + root_html
        + f'<div class="trow" style="--n:{n};grid-template-columns:repeat({n},minmax(0,1fr))">'
        + columns
        + "</div></div></div>"
    )
    details = "".join(leaf_detail(m, t, t["id"] != first) for t in leaves)
    attr_rows = ""
    for a in m.attrs:
        ticks = ""
        linked = set(a["data"]["taskIds"])
        for top in m.tops:
            ticks += f'<td class="ck">{"✓" if linked & set(m.descendants(top["id"])) else ""}</td>'
        attr_rows += f'<tr><td>{esc(a["title"])}</td>{ticks}<td>{esc(a["data"]["sourceSystem"])}</td><td class="mono small">{esc(a["data"]["loaded"])}</td></tr>'
    attrs = (
        '<div class="sec"><h3>Key attributes</h3><p class="sub">Facts the tasks rely on, where they come from and when they load.</p>'
        + '<div class="tw attr"><table><thead><tr><th>Attribute</th>'
        + "".join(f'<th title="{esc(m.task_label(t["id"]))}">{esc(t["id"])}</th>' for t in m.tops)
        + "<th>Source</th><th>Loaded</th></tr></thead><tbody>"
        + (attr_rows or f'<tr><td colspan="{len(m.tops) + 3}" class="mini">No key attributes recorded.</td></tr>')
        + "</tbody></table></div></div>"
    )
    rule = (
        "How to read risk: high = moves money, acts on identity, or makes a regulated decision; "
        "medium = a wrong answer causes rework or a repeat contact; low = read-only. "
        f"Result: {len(high)} of {len(leaves)} subtasks are high risk. Labels are the author's estimates."
    )
    return (
        head(STEP_BY_KEY["tasks"][3], f"The overall job, its {len(m.tops)} tasks and their real subtasks. Under each box: how it is resolved, examples, autonomy and risk.")
        + f'<div class="callout fit"><b>Risk rule</b><p>{esc(rule)}</p></div>'
        + tree
        + details
        + attrs
    )


def view_components(m):
    llms = [c for c in m.comps if c["data"]["group"] == "Agents (LLM)"]
    rows = ""
    for c in llms:
        fallbacks = [m.contract[w["id"]].get("failureDisposition", "") for w in m.nodes if w["data"]["componentId"] == c["id"]]
        fallbacks = [f for f in dict.fromkeys(fallbacks) if f]
        rows += (
            f"<tr><td>{bullet_list(c['data']['inputs'], 'plainlist mono small')}</td><td>{esc(c['description'])}</td>"
            f"<td>{chip(c['id'] + ' ' + c['title'], 'llm')}</td><td>{bullet_list(c['data']['outputs'], 'plainlist mono small')}</td>"
            f"<td>{esc(c['data']['approvalRule'])}{('<div class=' + chr(34) + 'mini' + chr(34) + '>' + esc('; '.join(fallbacks)) + '</div>') if fallbacks else ''}</td></tr>"
        )
    interp = (
        '<div class="sec first"><h3>Where input needs interpreting</h3><p class="sub">Every point where free text or documents become structured data, with the signal the part emits and the fallback when it cannot.</p>'
        + '<div class="tw"><table><thead><tr><th>Input</th><th>Why it is hard</th><th>Handled by</th><th>Signal</th><th>Fallback</th></tr></thead><tbody>'
        + (rows or '<tr><td colspan="5">No model component: this design interprets no free text. Every part is code or a person.</td></tr>')
        + "</tbody></table></div></div>"
    )
    groups = ""
    for group, kind in GROUP_TYPE.items():
        members = [c for c in m.comps if c["data"]["group"] == group]
        if not members:
            continue
        cards = ""
        for c in members:
            d = c["data"]
            ctype = m.comp_type(c["id"])
            extra = type_chip(ctype) if ctype in ("write", "rag") else ""
            why = f'<div class="why">Why code: {esc(d["whyCode"])}</div>' if d["whyCode"].strip() else ""
            same = " ".join(d["whyCode"].split()) == " ".join(c["description"].split())
            description = "" if same else f'<div class="small">{esc(c["description"])}</div>'
            cards += (
                f'<div class="panel cc" id="comp-{esc(c["id"])}"><div><span class="fm-id">{esc(c["id"])}</span> <span class="nm">{esc(c["title"])}</span> {extra}</div>'
                f'{description}{why}'
                f'<div class="small"><b>Authority:</b> {esc(d["approvalRule"])}</div>'
                f'<details><summary class="mini">Inputs and outputs</summary><div class="io"><b>In</b>{bullet_list(d["inputs"], "mono tiny")}<b>Out</b>{bullet_list(d["outputs"], "mono tiny")}</div></details>'
                f'<div class="tk">{"".join(m.link(t) for t in d["taskIds"])}</div></div>'
            )
        groups += f'<div class="ctype"><h3>{type_chip(kind)} {esc(group)}</h3><div class="ccards">{cards}</div></div>'
    return (
        head(STEP_BY_KEY["components"][3], "Everything the design needs, before it is wired into a flow. Each code part says why it is code, not a model.")
        + interp
        + groups
    )


# ------------------------------------------------------------------ flow SVG
NODE_W = 180
GAP_X = 170
LAYERS_PER_BAND = 16


def layout_flow(m):
    ids = [w["id"] for w in m.nodes]
    succ = {w["id"]: [t for t in dict.fromkeys(w["data"]["next"]) if t in m.node] for w in m.nodes}
    incoming = {i: 0 for i in ids}
    for s in ids:
        for t in succ[s]:
            incoming[t] += 1
    entries = [i for i in ids if incoming[i] == 0] or ids[:1]
    state, back = {}, set()

    def dfs(start):
        stack = [(start, iter(succ[start]))]
        state[start] = 1
        while stack:
            node, it = stack[-1]
            for nxt in it:
                if state.get(nxt) == 1:
                    back.add((node, nxt))
                elif nxt not in state:
                    state[nxt] = 1
                    stack.append((nxt, iter(succ[nxt])))
                    break
            else:
                state[node] = 2
                stack.pop()

    for e in entries:
        if e not in state:
            dfs(e)
    for i in ids:
        if i not in state:
            dfs(i)
    fwd = {u: [v for v in succ[u] if (u, v) not in back] for u in ids}
    indeg = {i: 0 for i in ids}
    for u in ids:
        for v in fwd[u]:
            indeg[v] += 1
    layer = {i: 0 for i in ids}
    queue = [i for i in ids if indeg[i] == 0]
    while queue:
        u = queue.pop(0)
        for v in fwd[u]:
            layer[v] = max(layer[v], layer[u] + 1)
            indeg[v] -= 1
            if indeg[v] == 0:
                queue.append(v)
    nlayers = (max(layer.values()) + 1) if ids else 0
    cols = [[] for _ in range(nlayers)]
    for i in ids:
        cols[layer[i]].append(i)
    pos = {i: k for col in cols for k, i in enumerate(col)}
    preds = {i: [] for i in ids}
    for u in ids:
        for v in fwd[u]:
            preds[v].append(u)
    for _ in range(3):
        for L in range(1, nlayers):
            cols[L].sort(key=lambda i: (sum(pos[p] for p in preds[i]) / len(preds[i]) if preds[i] else pos[i], pos[i]))
            for k, i in enumerate(cols[L]):
                pos[i] = k
        for L in range(nlayers - 2, -1, -1):
            cols[L].sort(key=lambda i: (sum(pos[s] for s in fwd[i]) / len(fwd[i]) if fwd[i] else pos[i], pos[i]))
            for k, i in enumerate(cols[L]):
                pos[i] = k
    return layer, cols, back, succ


def node_tags(m, wid):
    """Red handoff / amber uncertain-exit notes under a node, derived from its edges."""
    node = m.node[wid]
    red, amber = [], []
    for tr in m.contract[wid].get("transitions", []):
        if not isinstance(tr, dict):
            continue
        target = m.node.get(tr.get("to"))
        when = str(tr.get("when", ""))
        if target is None:
            continue
        if m.comp[target["data"]["componentId"]]["data"]["group"] == "Code: human triggers" and target["id"] != wid:
            red.append(when)
        outcome = m.outcome.get((wid, target["id"], when))
        if outcome in ("TIMEOUT", "unknown_commit") or (outcome is None and not m.has_semantics and re.search(r"timeout|unknown", when, re.I)):
            amber.append(when)
    tags = []
    if red:
        tags.append(("handoff", "↳ handoff: " + " / ".join(dict.fromkeys(red))))
    if amber:
        tags.append(("exit", "↳ uncertain exit: " + " / ".join(dict.fromkeys(amber))))
    return tags


def bezier_point(p0, p1, p2, p3, t):
    u = 1 - t
    return (
        u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0],
        u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1],
    )


def label_plate(lines, cx, cy, cls="wf-elbl"):
    width = max(len(line) for line in lines) * 6.7 + 12
    height = 15 * len(lines) + 4
    text = "".join(
        f'<tspan x="{cx:.1f}" dy="{"0" if i == 0 else "15"}">{esc(line)}</tspan>' for i, line in enumerate(lines)
    )
    y0 = cy - height / 2
    return (
        f'<rect class="wf-elbl-bg" x="{cx - width / 2:.1f}" y="{y0:.1f}" width="{width:.1f}" height="{height:.1f}" rx="3"/>'
        f'<text class="{cls}" x="{cx:.1f}" y="{y0 + 12:.1f}" text-anchor="middle">{text}</text>'
    )


def flow_svg(m):
    if not m.nodes:
        return '<p class="mini">This design has no workflow node.</p>', {}
    layer, cols, back, succ = layout_flow(m)
    # Text per node
    info = {}
    for w in m.nodes:
        wid = w["id"]
        comp = m.comp[w["data"]["componentId"]]
        label = m.node_label(wid)
        example = w["data"]["example"]
        if " ".join(example.split()).lower() in (" ".join(label.split()).lower(), " ".join(w["title"].split()).lower()):
            example = ""
        info[wid] = {
            "header": f'{wid} · {comp["id"]}' + (" · decides" if w["data"]["decision"] else ""),
            "title": wrap(label, 23),
            "example": wrap(example, 27) if example and len(wrap(example, 27)) <= 2 else [],
            "tags": [(kind, wrap(text, 32)) for kind, text in node_tags(m, wid)],
            "type": m.comp_type(comp["id"]),
            "decision": bool(w["data"]["decision"]),
            "tops": sorted({m.top_of(t) for t in w["data"]["taskIds"]}),
        }
    node_h = max(26 + 14 * len(i["title"]) + 13 * len(i["example"]) + 8 for i in info.values())
    tag_lines = max([sum(len(lines) for _, lines in i["tags"]) for i in info.values()] + [0])
    pitch_y = node_h + 14 * tag_lines + 30
    nlayers = len(cols)
    bands = [list(range(s, min(s + LAYERS_PER_BAND, nlayers))) for s in range(0, nlayers, LAYERS_PER_BAND)]
    band_of = {L: b for b, layers in enumerate(bands) for L in layers}
    # Edges grouped by (source, target), labels joined
    edges = {}
    for w in m.nodes:
        for tr in m.contract[w["id"]].get("transitions", []):
            if isinstance(tr, dict) and tr.get("to") in m.node:
                edges.setdefault((w["id"], tr["to"]), []).append((str(tr.get("when", "")), str(tr.get("mode", ""))))
    for s, targets in succ.items():
        for t in targets:
            edges.setdefault((s, t), [])
    out_count = {s: len({t for (a, t) in edges if a == s}) for s in m.node}
    # Positions
    xy = {}
    band_tops = []
    svg_h = 0
    width = 20 + LAYERS_PER_BAND * (NODE_W + GAP_X) - GAP_X + 20 if nlayers > LAYERS_PER_BAND else 20 + nlayers * (NODE_W + GAP_X) - GAP_X + 20
    cross_notes = {}
    for b, layers in enumerate(bands):
        back_in_band = [(s, t) for (s, t) in back if band_of[layer[s]] == b and band_of[layer[t]] == b]
        rails = len(back_in_band)
        top = svg_h
        caption_h = 34
        y0 = top + caption_h + rails * 16 + 12
        maxrows = max(len(cols[L]) for L in layers)
        for L in layers:
            col = cols[L]
            offset = ((maxrows - len(col)) // 2) * pitch_y
            for k, wid in enumerate(col):
                xy[wid] = (20 + (L - layers[0]) * (NODE_W + GAP_X), y0 + offset + k * pitch_y)
        band_tops.append((top, y0, rails, back_in_band))
        svg_h = y0 + maxrows * pitch_y + 10
    # Cross-band edges become notes under the nodes
    for (s, t), whens in edges.items():
        if band_of[layer[s]] != band_of[layer[t]]:
            cross_notes.setdefault(s, []).append(("continue", f"→ continues at {t} (band {band_of[layer[t]] + 1})"))
            cross_notes.setdefault(t, []).append(("continue", f"← from {s} (band {band_of[layer[s]] + 1})"))
    parts = []
    # Lane captions per band: dominant top-level task per layer, grouped
    for b, layers in enumerate(bands):
        top, y0, rails, back_in_band = band_tops[b]
        if b:
            parts.append(f'<line class="wf-band" x1="0" y1="{top + 2}" x2="{width}" y2="{top + 2}"/>')
        groups = []
        for L in layers:
            counts = {}
            for wid in cols[L]:
                for tid in info[wid]["tops"]:
                    counts[tid] = counts.get(tid, 0) + 1
            dominant = max(counts, key=lambda k: (counts[k], -list(counts).index(k))) if counts else ""
            if groups and groups[-1][0] == dominant:
                groups[-1][2] = L
            else:
                groups.append([dominant, L, L])
        for dominant, start, end in groups:
            if not dominant or dominant not in m.task:
                continue
            caption = f"{dominant} {m.task_label(dominant)}".upper()
            chars = max(12, int(((end - start + 1) * (NODE_W + GAP_X) - 20) / 6.9))
            lines = wrap(caption, chars)[:2]
            x = 20 + (start - layers[0]) * (NODE_W + GAP_X)
            parts.append(
                f'<text class="wf-lane" x="{x}" y="{top + 16}">'
                + "".join(f'<tspan x="{x}" dy="{0 if i == 0 else 13}">{esc(line)}</tspan>' for i, line in enumerate(lines))
                + "</text>"
            )
    # Edges
    rail_index = {}
    for b, (top, y0, rails, back_in_band) in enumerate(band_tops):
        for k, edge in enumerate(sorted(back_in_band)):
            rail_index[edge] = top + 34 + 8 + k * 16
    plates = []
    per_source = {}
    for (s, t) in edges:
        per_source.setdefault(s, []).append(t)
    for (s, t), whens in sorted(edges.items(), key=lambda e: (layer[e[0][0]], e[0])):
        if band_of[layer[s]] != band_of[layer[t]]:
            continue
        sx, sy = xy[s]
        tx, ty = xy[t]
        tasks = " ".join(sorted(set(info[s]["tops"]) | set(info[t]["tops"])))
        label_lines = []
        text_whens = [w for w, _ in whens if w]
        if out_count[s] > 1 or (text_whens and len(text_whens[0]) <= 48):
            for w, mode in whens:
                if not w:
                    continue
                suffix = " (parallel)" if mode == "fan-out" else ""
                label_lines.extend(wrap(w + suffix, 20))
        if out_count[s] > 1 and not label_lines:
            label_lines = ["(no condition stated)"]
        siblings = per_source[s]
        j = siblings.index(t)
        n_out = len(siblings)
        if (s, t) in back:
            rail = rail_index[(s, t)]
            k = sorted(band_tops[band_of[layer[s]]][3]).index((s, t))
            gx1 = sx + NODE_W + 14 + k * 7
            gx2 = tx - 14 - k * 7
            path = f"M{sx + NODE_W},{sy + node_h / 2} L{gx1},{sy + node_h / 2} L{gx1},{rail} L{gx2},{rail} L{gx2},{ty + node_h / 2} L{tx},{ty + node_h / 2}"
            lx, ly = (gx1 + gx2) / 2, rail
            cls = "wf-edge back"
        elif layer[t] == layer[s]:
            reach = NODE_W + 34 + j * 10
            p0 = (sx + NODE_W, sy + node_h / 2)
            p3 = (tx + NODE_W, ty + node_h / 2)
            p1 = (sx + reach + 30, sy + node_h / 2)
            p2 = (tx + reach + 30, ty + node_h / 2)
            path = f"M{p0[0]},{p0[1]} C{p1[0]},{p1[1]} {p2[0]},{p2[1]} {p3[0]},{p3[1]}"
            lx, ly = bezier_point(p0, p1, p2, p3, 0.5)
            cls = "wf-edge"
        else:
            p0 = (sx + NODE_W, sy + node_h / 2)
            p3 = (tx, ty + node_h / 2)
            mid = (p0[0] + p3[0]) / 2
            p1 = (mid, p0[1])
            p2 = (mid, p3[1])
            path = f"M{p0[0]},{p0[1]} C{p1[0]},{p1[1]} {p2[0]},{p2[1]} {p3[0]},{p3[1]}"
            span = layer[t] - layer[s]
            gap_index = (span - 1) // 2
            target_x = p0[0] + GAP_X / 2 + gap_index * (NODE_W + GAP_X)
            lo, hi = 0.0, 1.0
            for _ in range(40):  # bisection on the monotone x(t) of the curve
                mid_t = (lo + hi) / 2
                if bezier_point(p0, p1, p2, p3, mid_t)[0] < target_x:
                    lo = mid_t
                else:
                    hi = mid_t
            lx, ly = bezier_point(p0, p1, p2, p3, (lo + hi) / 2)
            cls = "wf-edge"
        parts.append(
            f'<g class="wf-edgeg" data-edge="{esc(s)}-{esc(t)}" data-tasks="{esc(tasks)}"><path class="{cls}" d="{path}" marker-end="url(#ah)"/></g>'
        )
        if label_lines:
            plates.append(f'<g class="wf-edgeg" data-tasks="{esc(tasks)}">{label_plate(label_lines, lx, ly)}</g>')
    # Nodes
    for w in m.nodes:
        wid = w["id"]
        i = info[wid]
        x, y = xy[wid]
        texts = f'<text class="ty" x="{x + 9}" y="{y + 14}">{esc(i["header"])}</text>'
        yy = y + 30
        for line in i["title"]:
            texts += f'<text class="tt" x="{x + 9}" y="{yy}">{esc(line)}</text>'
            yy += 14
        for line in i["example"]:
            texts += f'<text class="ex" x="{x + 9}" y="{yy}">{esc(line)}</text>'
            yy += 13
        tag_y = y + node_h + 14
        tags = ""
        for kind, lines in i["tags"] + [(k, wrap(t, 32)) for k, t in cross_notes.get(wid, [])]:
            for line in lines:
                tags += f'<text class="wf-tag {kind}" x="{x + 2}" y="{tag_y}">{esc(line)}</text>'
                tag_y += 14
        parts.append(
            f'<g class="wf-node n-{i["type"]}{" decision" if i["decision"] else ""}" data-node="{esc(wid)}" data-tasks="{esc(" ".join(i["tops"]))}" tabindex="0" role="button" aria-label="{esc(wid + " " + m.node_label(wid))}">'
            f'<rect x="{x}" y="{y}" width="{NODE_W}" height="{node_h}" rx="{14 if i["decision"] else 6}"/>{texts}</g>{tags}'
        )
    parts.extend(plates)  # condition plates sit above nodes so they stay legible
    svg = (
        f'<svg viewBox="0 0 {width} {svg_h}" width="{width}" height="{svg_h}" role="img" aria-label="Workflow of {esc(m.d["title"])}">'
        '<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path class="arrowhead" d="M0,0 L10,5 L0,10 z"/></marker></defs>'
        + "".join(parts)
        + "</svg>"
    )
    return svg, info


def node_detail(m, w, hidden):
    wid = w["id"]
    c = m.contract[wid]
    comp = m.comp[w["data"]["componentId"]]
    rows = ""
    for tr in c.get("transitions", []):
        if not isinstance(tr, dict):
            continue
        target = m.node.get(tr.get("to"))
        name = f'{esc(tr.get("to"))} {esc(m.node_label(target["id"]))}' if target else esc(tr.get("to"))
        fan = ' <span class="chip">runs in parallel</span>' if tr.get("mode") == "fan-out" else ""
        rows += f'<tr><td class="mono nowrap"><button type="button" class="chip mono" data-gonode="{esc(tr.get("to"))}">{name}</button></td><td>{esc(tr.get("when"))}{fan}</td></tr>'
    nxt = (
        f'<div class="tw"><table><thead><tr><th>Go to</th><th>When</th></tr></thead><tbody>{rows}</tbody></table></div>'
        if rows
        else f'<b>Ends here.</b> {esc(c.get("terminalDisposition") or "")}'
    )
    bindings = c.get("bindings")
    binding_rows = ""
    if isinstance(bindings, dict) and bindings:
        binding_rows = "".join(
            f'<tr><td class="mono">{esc(k)}</td><td class="mono small">{esc(pretty_json(json.dumps(v)) if not isinstance(v, str) else v)}</td></tr>'
            for k, v in bindings.items()
        )
    extras = ""
    for key, value in c.items():
        if key in ("state", "transitions", "failureDisposition", "timeout", "retryPolicy", "terminalDisposition", "bindings"):
            continue
        extras += f"<dt>{esc(key)}</dt><dd class=\"small\">{esc(value if isinstance(value, str) else pretty_json(json.dumps(value)))}</dd>"
    fms = [f for f in m.fmea if comp["id"] in f["data"]["componentIds"]]
    tasks = '<div class="inline-list">' + "".join(m.link(t) for t in w["data"]["taskIds"]) + "</div>"
    return (
        f'<div class="panel wf-detail" data-node-detail="{esc(wid)}"{" hidden" if hidden else ""}>'
        f'<div class="inline-list">{type_chip(m.comp_type(comp["id"]))}<span class="fm-id">{esc(wid)} · {esc(comp["id"])}</span>{"".join(m.link(t) for t in w["data"]["taskIds"])}</div>'
        f'<h3>{esc(m.node_label(wid))}</h3>'
        + kv_rows(
            [
                ("Example", esc(w["data"]["example"])),
                ("What the part does", esc(comp["description"])),
                ("Next steps", nxt),
                ("If it fails", esc(c.get("failureDisposition", ""))),
                ("Timeout · retry", esc(c.get("timeout", "")) + " · " + esc(c.get("retryPolicy", ""))),
                ("Failure modes", m.links([f["id"] for f in fms])),
            ]
        )
        + f'<details class="contract"><summary class="mini">State contract</summary><div class="small"><b>State:</b> {esc(c.get("state", ""))}</div>'
        + (f'<div class="tw"><table><thead><tr><th>Guard field</th><th>Producer</th></tr></thead><tbody>{binding_rows}</tbody></table></div>' if binding_rows else "")
        + (f'<dl class="kv">{extras}</dl>' if extras else "")
        + "</details></div>"
    )


def view_workflow(m):
    svg, info = flow_svg(m)
    first = m.nodes[0]["id"] if m.nodes else ""
    filters = '<button type="button" class="fbtn" data-task="all" aria-pressed="true">All tasks</button>' + "".join(
        f'<button type="button" class="fbtn" data-task="{esc(t["id"])}" aria-pressed="false">{esc(t["id"])} {esc(m.task_label(t["id"]))}</button>'
        for t in m.tops
    )
    kinds = []
    for w in m.nodes:
        k = m.comp_type(w["data"]["componentId"])
        if k not in kinds:
            kinds.append(k)
    legend = "".join(type_chip(k) for k in ("llm", "read", "write", "rag", "code", "human") if k in kinds) + '<span class="chip">rounded box = decision step</span>'
    details = "".join(node_detail(m, w, w["id"] != first) for w in m.nodes)
    cov = ""
    for leaf in m.leaves:
        steps = m.serving_nodes(leaf["id"])
        cov += (
            f'<tr><td><span class="fm-id">{esc(leaf["id"])}</span> {esc(m.task_label(leaf["id"]))}</td>'
            f'<td>{", ".join(esc(w["id"] + " " + m.node_label(w["id"])) for w in steps) or "—"}</td>'
            f'<td class="{"ok" if steps else "gap"}">{"Covered" if steps else "Gap"}</td></tr>'
        )
    return (
        head(STEP_BY_KEY["workflow"][3], "Components wired into a flow. Edges carry their condition. Red notes show where a step hands the case to a person; amber notes show uncertain exits.")
        + f'<div class="taskbar">{filters}</div><div class="legend">{legend}</div>'
        + f'<div class="wf-wrap">{svg}</div>'
        + details
        + '<div class="sec"><h3>Coverage</h3><p class="sub">Every subtask reaches at least one step.</p><div class="tw cov"><table><thead><tr><th>Subtask</th><th>Steps</th><th>Status</th></tr></thead><tbody>'
        + cov
        + "</tbody></table></div></div>"
    )


def view_framework(m):
    names = {"fit": "Fit and autonomy", "architecture": "Architecture", "orchestration": "Orchestration", "permission": "Permissions", "data": "Data", "tooling": "Tooling"}
    cards = ""
    tooling = [f for f in m.framework if f["data"]["category"] == "tooling"]
    if tooling:
        summary = "".join(
            f'<tr><td>{esc(f["data"].get("capability", ""))}</td><td>{esc(f["title"])}</td><td class="num">{len(f["data"].get("candidates", []))}</td>'
            f'<td>{"Checked" if any(c["verified"] for c in f["data"].get("candidates", [])) else "Unverified"}</td></tr>'
            for f in tooling
        )
        cards += (
            '<div class="sec first"><h3>Tools by capability</h3><p class="sub">One card per capability the design needs beyond the model. A checked candidate cites a research finding; an unverified one is a name to confirm before build.</p>'
            '<div class="tw"><table><thead><tr><th>Capability</th><th>Chosen</th><th>Candidates</th><th>Status</th></tr></thead><tbody>'
            + summary
            + "</tbody></table></div></div>"
        )
    for f in m.framework:
        d = f["data"]
        crumb = f'{f["id"]} · {names.get(d["category"], d["category"])}' + (f' · {d["capability"]}' if d.get("capability") else "") + (f' · {d["permission"]}' if d["permission"] != "none" else "")
        pairs = [
            ("Choice", esc(d["choice"])),
            ("Rejected", "<br>".join(esc(a) for a in d["alternatives"])),
            ("Trade-off", esc(d["tradeoffs"])),
        ]
        if d.get("candidates"):
            crows = ""
            for c in d["candidates"]:
                evidence = (
                    " ".join(f'<span class="chip mono" title="{esc(m.finding[rs]["title"]) if rs in m.finding else ""}">{esc(rs)}</span>' for rs in c["sourceIds"])
                    if c["verified"] and c["sourceIds"]
                    else '<span class="warn">unverified</span>'
                )
                crows += f'<tr><td>{esc(c["name"])}</td><td>{esc(c["kind"])}</td><td>{esc(c["note"])}</td><td>{evidence}</td></tr>'
            pairs.append(("Candidates", '<div class="tw"><table><thead><tr><th>Candidate</th><th>Kind</th><th>Note</th><th>Evidence</th></tr></thead><tbody>' + crows + "</tbody></table></div>"))
        if d["category"] == "permission" or d["permission"] != "none":
            pairs += [("Blast radius", esc(d["blastRadius"])), ("Approval", esc(d["approvalRule"])), ("Least privilege", esc(d["leastPrivilege"]))]
        cloud = [(label, d[key]) for key, label in (("aws", "AWS"), ("gcp", "Google Cloud"), ("azure", "Azure"), ("openSource", "Open source"))]
        if any(v for _, v in cloud):
            pairs.append(("Options", '<div class="tw"><table><tbody>' + "".join(f"<tr><td>{esc(k)}</td><td>{esc(v)}</td></tr>" for k, v in cloud if v) + "</tbody></table></div>"))
        cards += f'<div class="panel box card"><div class="crumb">{esc(crumb)}</div><h3 class="card-title">{esc(f["title"])}</h3>{kv_rows(pairs)}</div>'
    lead = "Each choice names the option it rejected. Vendor features are candidates to verify, not claims."
    if tooling:
        lead += " A checked candidate cites the research finding behind it."
    return head(STEP_BY_KEY["framework"][3], lead) + cards


def view_models(m):
    if not m.models:
        body = (
            '<div class="panel box"><h3>No LLM component</h3><p class="small">No model calls or model token spend are allocated. The chosen workflow is code-only. '
            "This does not imply zero hosting, storage or human operating cost.</p></div>"
        )
        return head(STEP_BY_KEY["models"][3], "One plan per LLM part. Money, limits and identity use no model at all.") + body
    rows = ""
    total = 0.0
    terms = []
    for x in m.models:
        d = x["data"]
        per = d["callsPerCase"] * (d["inputTokens"] * d["inputPrice"] + d["outputTokens"] * d["outputPrice"]) / 1e6
        total += per
        terms.append(f'{d["callsPerCase"]} × ({d["inputTokens"]} × {d["inputPrice"]} + {d["outputTokens"]} × {d["outputPrice"]}) / 1e6 = {money(per)}')
        comp = m.comp.get(d["componentId"])
        rows += (
            f'<tr><td><span class="fm-id">{esc(d["componentId"])}</span> {esc(comp["title"] if comp else "")}</td><td>{esc(d["tier"])}</td>'
            f'<td>{esc(d["rationale"])}</td><td>{esc(d["fineTuneWhen"])}</td><td class="num">{esc(d["callsPerCase"])}</td><td class="num">{money(per)}</td></tr>'
        )
    priced = all(x["data"]["inputPrice"] > 0 and x["data"]["outputPrice"] > 0 for x in m.models)
    notes = [
        "Per case = sum over model plans of calls × (input tokens × input price + output tokens × output price) / 1e6.",
        *terms,
        m.volume_note,
        "Model calls only. Hosting, tools, retrieval, storage, network and staff time are not in this figure.",
        "Prices and tokens are illustrative placeholders unless a model card says measured." if priced else "A zero price means unpriced, not free.",
    ]
    return (
        head(STEP_BY_KEY["models"][3], "One plan per LLM part. Money, limits and identity use no model at all. Prices are placeholders.")
        + '<div class="tw"><table><thead><tr><th>Part</th><th>Tier</th><th>Why, and what was rejected</th><th>Fine-tune only when</th><th>Calls / case</th><th>USD / case</th></tr></thead><tbody>'
        + rows
        + "</tbody></table></div>"
        + '<div class="sec"><h3>Cost</h3><div class="calc"><div class="panel"><div class="in-grid"><div class="field"><label for="vol">Cases per month</label>'
        + f'<input id="vol" data-calc="volume" type="number" min="0" step="1" value="{m.volume}"></div></div>'
        + '<ul class="mini notes">' + "".join(f"<li>{esc(n)}</li>" for n in notes) + "</ul></div>"
        + f'<div class="panel out"><div class="mini">Model cost per case</div><div class="big tnum">USD {money(total)}</div>'
        + f'<div class="month">Per month: <b class="mono tnum" data-month-cost="{total!r}">USD {round(total * m.volume):,}</b></div></div></div></div>'
    )


def view_fmea(m):
    ordered = sorted(m.fmea, key=m.rpn, reverse=True)
    sev = sorted({f["data"]["severity"] for f in m.fmea}, reverse=True)
    occ = sorted({f["data"]["occurrence"] for f in m.fmea})
    s_hi, s_lo = (sev[0], sev[-1]) if sev else (10, 8)
    o_lo, o_hi = (occ[0], occ[-1]) if occ else (1, 3)
    while s_hi - s_lo < 2:
        if s_lo > 1:
            s_lo -= 1
        elif s_hi < 10:
            s_hi += 1
        else:
            break
    while o_hi - o_lo < 2:
        if o_hi < 10:
            o_hi += 1
        elif o_lo > 1:
            o_lo -= 1
        else:
            break
    cells = ""
    for s in range(s_hi, s_lo - 1, -1):
        row = ""
        for o in range(o_lo, o_hi + 1):
            ids = [f["id"] for f in m.fmea if f["data"]["severity"] == s and f["data"]["occurrence"] == o]
            score = s * o
            cls = "h-hi" if score >= 40 or s >= 8 else "h-md" if score >= 25 else "h-lo"
            row += f'<td class="{cls}">{esc(" ".join(ids)) if ids else "&nbsp;"}</td>'
        cells += f"<tr><th>{s}</th>{row}</tr>"
    heat = (
        '<div class="panel box"><h3>Severity × occurrence</h3><div class="scroll"><table class="heat"><thead><tr><th>S \\ O</th>'
        + "".join(f"<th>{o}</th>" for o in range(o_lo, o_hi + 1))
        + f"</tr></thead><tbody>{cells}</tbody></table></div></div>"
    )
    acting = [f for f in ordered if m.act_now(f)]
    common = [f for f in ordered if f["data"]["commonToAll"]]
    act = (
        f"RPN ≥ 150 or severity ≥ 8 needs an owner and a release gate. {len(acting)} of {len(ordered)} risks qualify."
        + (f' {len(common)} apply to every task: {", ".join(f["id"] + " " + f["title"] for f in common)}.' if common else "")
    )
    rows = ""
    for f in ordered:
        d = f["data"]
        r = m.rpn(f)
        rows += (
            f'<tr class="fm-row" data-fmrow="{esc(f["id"])}" id="row-{esc(f["id"])}" tabindex="0" aria-expanded="false">'
            f'<td><span class="fm-id">{esc(f["id"])}</span> <span class="fm-name">{esc(f["title"])}</span>{"<br><span class=" + chr(34) + "common" + chr(34) + ">all tasks</span>" if d["commonToAll"] else ""}<br><span class="mini">{esc(d["effect"])}</span></td>'
            f'<td>{m.links(d["taskIds"])}</td><td class="num">{d["severity"]}</td><td class="num">{d["occurrence"]}</td><td class="num">{d["detection"]}</td>'
            f'<td><span class="rpn {m.band(r, d["severity"])}">{r}</span></td><td class="control">{esc(d["control"])}</td><td class="mono small">{esc(", ".join(d["evalIds"]))}</td></tr>'
            f'<tr class="fm-open" data-fm-detail="{esc(f["id"])}" hidden><td colspan="8"><div class="fm-x"><div><h4>Cause</h4><p>{esc(d["cause"])}</p></div>'
            f'<div><h4>Detection</h4><p>{esc(d["detectionMethod"])}</p><h4 class="gap-top">Metric → KPI</h4><p>{esc(d["metric"])} → <b>{esc(d["kpi"])}</b></p></div>'
            f'<div><h4>Owner and gate</h4><p>{esc(d["action"])}</p>{"<p class=" + chr(34) + "mini" + chr(34) + ">Accepted risk: yes (user-supplied acceptance recorded).</p>" if d["acceptedRisk"] else ""}</div></div></td></tr>'
        )
    return (
        head(STEP_BY_KEY["fmea"][3], "Severity, occurrence and detection on 1–10; RPN = S × O × D. Scores rank what to fix first; they are estimates, not measurements.")
        + f'<div class="two">{heat}<div class="panel box"><h3>Act-now rule</h3><p class="small">{esc(act)}</p></div></div>'
        + '<div class="sec"><div class="tw"><table class="fm-table"><thead><tr><th>Risk</th><th>Subtasks</th><th>S</th><th>O</th><th>D</th><th>RPN</th><th>Control</th><th>Tests</th></tr></thead><tbody>'
        + rows
        + '</tbody></table></div><p class="mini gap-top">Click a row for cause, detection, metric and owner.</p></div>'
    )


def view_evals(m):
    golden = [e for e in m.evals if e["data"]["category"] == "golden"]
    cov = ""
    for f in m.fmea:
        g = [e for e in golden if f["id"] in e["data"]["failureModeIds"]]
        cov += (
            f'<tr><td><span class="fm-id">{esc(f["id"])}</span> {esc(f["title"])}</td><td class="num">{len(f["data"]["evalIds"])}</td>'
            f'<td>{esc(g[0]["id"] + " " + g[0]["title"]) if g else "—"}</td><td class="{"ok" if g else "gap"}">{"Covered" if g else "Gap"}</td></tr>'
        )
    for leaf in [t for t in m.leaves if t["data"]["risk"] == "high"]:
        g = [e for e in golden if leaf["id"] in e["data"]["taskIds"]]
        cov += (
            f'<tr><td><span class="fm-id">{esc(leaf["id"])}</span> {esc(m.task_label(leaf["id"]))} <span class="why-r">high risk</span></td><td class="num">{len(g)}</td>'
            f'<td>{esc(g[0]["id"] + " " + g[0]["title"]) if g else "—"}</td><td class="{"ok" if g else "gap"}">{"Covered" if g else "Gap"}</td></tr>'
        )
    cards = ""
    for e in golden:
        d = e["data"]
        linked = d["failureModeIds"][0] if d["failureModeIds"] else "positive"
        cards += (
            f'<div class="panel tc"><div class="h"><span class="fm-id">{esc(e["id"])} · {esc(e["title"])}</span>{chip(linked, mono=True)}</div>'
            f'<div class="lb">Must hold</div><div class="pass">{"<br>".join(esc(x) for x in must_hold(d["passRule"]))}</div>'
            f'<details><summary class="mini">Fixture and expected result</summary><div class="lb">Input</div><pre>{esc(pretty_json(d["input"]))}</pre><div class="lb">Expected</div><pre>{esc(pretty_json(d["expected"]))}</pre></details></div>'
        )
    others = "".join(
        f'<tr><td><span class="fm-id">{esc(e["id"])}</span> {esc(e["title"])}</td><td>{esc(e["data"]["category"])}</td><td>{esc(e["data"]["metric"])}</td>'
        f'<td class="mono small">{esc(e["data"]["target"])}</td><td>{esc(e["data"]["cadence"])}</td><td>{esc(e["data"]["alertThreshold"])}</td></tr>'
        for e in m.evals
        if e["data"]["category"] != "golden"
    )
    return (
        head(STEP_BY_KEY["evals"][3], "What must be tested before release. These are test plans; nothing here has been run yet.")
        + '<div class="sec first"><h3>Coverage</h3><p class="sub">Each risk and each high-risk subtask, with its tests. A row with no test would block export.</p>'
        + '<div class="tw cov"><table><thead><tr><th>Risk or subtask</th><th>Tests</th><th>Key test</th><th>Status</th></tr></thead><tbody>'
        + cov
        + "</tbody></table></div></div>"
        + '<div class="sec"><h3>Golden cases</h3><p class="sub">Full fixtures and mocks are in eval-set.json.</p><div class="cards">'
        + cards
        + "</div></div>"
        + '<div class="sec"><h3>Offline, online and release</h3><div class="tw"><table><thead><tr><th>Test</th><th>Layer</th><th>Metric</th><th>Target</th><th>Cadence</th><th>Alert</th></tr></thead><tbody>'
        + others
        + "</tbody></table></div></div>"
    )


def view_rollout(m):
    by = lambda cat: [r for r in m.rollout if r["data"]["category"] == cat]
    kpis = ""
    for k in by("kpi"):
        d = k["data"]
        span = parse_range(d["businessKpi"])
        bt = f'<div class="bt tnum"><span class="b">{esc(span[0])}</span><span>→</span><span class="tg">{esc(span[1])}</span></div>' if span else ""
        kpis += (
            f'<div class="panel kpi"><div class="k">{esc(k["title"])}</div>{bt}<div class="mini">{esc(d["businessKpi"])}</div>'
            f'<ul>{"".join(f"<li>{esc(x)}</li>" for x in d["aiMetrics"])}</ul><div class="mini">{esc(k["description"])}</div></div>'
        )
    phases = "".join(
        f'<div class="ph"><div class="nm">{esc(p["title"])}</div><div class="small">{esc(p["data"]["phase"])}</div><div class="gate"><b>Gate:</b> {esc(p["data"]["gate"])}</div><div class="w">{esc(p["data"]["owner"])}</div></div>'
        for p in by("phase")
    )
    boxes = "".join(
        f'<div class="panel box"><h3>{esc(x["title"])}</h3><p class="small">{esc(x["data"]["gate"])}</p><p class="mini">{esc(x["data"]["experiment"])}</p></div>'
        for x in by("experiment")
    ) + "".join(
        f'<div class="panel box"><h3>{esc(o["title"])}</h3><p class="small">{esc(o["data"]["owner"])}</p><p class="mini">{esc(o["data"]["gate"])}</p></div>'
        for o in by("owner")
    )
    return (
        head(STEP_BY_KEY["rollout"][3], "How value is proven, and how autonomy grows only with evidence.")
        + f'<div class="sec first"><h3>KPI tree</h3><div class="kpis">{kpis}</div></div>'
        + f'<div class="sec"><h3>Rollout</h3><div class="phases" style="--n:{max(1, len(by("phase")))}">{phases}</div></div>'
        + f'<div class="sec two">{boxes}</div>'
    )


def view_export(m):
    milestones = m.d.get("milestones") or []
    if not milestones:
        milestones = [
            {"id": f"{i:02d}", "title": c["title"], "componentIds": [c["id"]]}
            for i, c in enumerate(m.comps, 1)
        ]
    n = len(milestones)
    if m.mode == "lite":
        files = [
            ("DESIGN.html", "This read-only view: decision brief, task map, flow and risks."),
            ("DESIGN.pdf", "The four-page report: decision brief, task tree, workflow and top risks."),
            ("design.json", "The single source for every ID, contract and fixture."),
            ("review.json", "The review record; earlier rounds stay as review-round-N.json."),
            ("validation.json, run-report.json", "Structural checks, generated-file hashes, timing and sizes."),
        ]
    else:
        files = [
            ("DESIGN.html", "This read-only view: the decision brief, the ten steps and the evidence group."),
            ("DESIGN.pdf", "The readable report: decision brief on page 1, then the steps" + (", at most 12 pages." if m.mode == "standard" else " and appendices.")),
            ("build/", f"00-overview.md plus {n} milestone file{'s' if n != 1 else ''}, each under 25 KB, with only the contracts, tests and acceptance criteria that milestone needs."),
            ("design.json", "The single source for every ID, contract and fixture."),
            ("README.md", "What each file is and what to open first."),
            ("review.json, validation.json, run-report.json", "Review record with earlier rounds kept as review-round-N.json, structural checks and run measurements."),
            ("_evidence/", "eval-set.json, fmea-register.csv, assumptions.md, PRD.md and architecture.md: the full fixtures, scored risks, owners and exact contracts."),
        ]
    file_list = "".join(f'<div class="fl"><span class="fn">{esc(name)}</span><span>{esc(text)}</span></div>' for name, text in files)
    steps = "".join(
        f'<li class="panel"><span>{esc(ms["id"])} {esc(ms["title"])}</span><span class="mini">{esc(", ".join(ms.get("componentIds", [])))}</span></li>'
        for ms in milestones
    )
    criteria = "".join(f"<li>{esc(a)}</li>" for x in m.export for a in x["data"]["acceptanceCriteria"])
    instructions = "".join(
        f'<details class="panel box"><summary><b>{esc(x["id"])} {esc(x["title"])}</b> · build instructions</summary><p class="small pre">{esc(x["data"]["buildInstructions"])}</p></details>'
        for x in m.export
    )
    return (
        head(STEP_BY_KEY["export"][3], "What the user receives. A short top level; the detailed companions sit in _evidence/.")
        + f'<div class="filelist">{file_list}</div>'
        + f'<div class="sec"><h3>Build milestones</h3><ol class="gates">{steps}</ol></div>'
        + f'<div class="sec"><h3>Acceptance criteria</h3><div class="panel box"><ul class="small">{criteria}</ul></div></div>'
        + f'<div class="sec"><h3>Build instructions</h3>{instructions}</div>'
    )


def view_assumptions(m):
    rows = "".join(
        f'<tr><td class="mono">{esc(h["id"])}</td><td>{esc(h["statement"])}</td><td>{esc(h["owner"])}</td><td>{esc(h["validation"])}</td>'
        f'<td class="{"blocks" if h["launchBlocker"] else "mini"}">{"Yes" if h["launchBlocker"] else "No"}</td></tr>'
        for h in m.d["assumptions"]
    ) or '<tr><td colspan="5">No top-level assumption was recorded. That is not a claim that no unknowns exist.</td></tr>'
    stage_notes = ""
    for key in STAGES:
        for note in m.d["stages"][key]["assumptions"]:
            stage_notes += f"<li><span class='mono'>{esc(key)}</span> {esc(note)}</li>"
        for item in m.d["stages"][key]["items"]:
            for note in item["assumptions"]:
                if re.fullmatch(r"H[1-9]\d*", note.strip()):
                    continue  # a bare ledger ID; the ledger row above carries the statement
                stage_notes += f"<li><span class='mono'>{esc(item['id'])}</span> {esc(note)}</li>"
    blockers = sum(1 for h in m.d["assumptions"] if h["launchBlocker"])
    return (
        head("Assumptions", f"Facts the brief did not give. Each has an owner and a way to verify it. {blockers} block launch and must be cleared before the first live phase.")
        + '<div class="tw"><table><thead><tr><th>ID</th><th>Assumption</th><th>Owner (proposed)</th><th>How to verify</th><th>Blocks launch</th></tr></thead><tbody>'
        + rows
        + "</tbody></table></div>"
        + (f'<div class="sec"><h3>Stage notes</h3><ul class="small">{stage_notes}</ul></div>' if stage_notes else "")
    )


def view_review(m):
    r = m.review
    dims = "".join(
        f'<tr><td class="nowrap">{esc(d["id"])} {esc(m.rubric_names.get(d["id"], ""))}</td><td class="mono">{d["score"]}/4</td><td>{"<br>".join(esc(x) for x in d["evidence"])}</td></tr>'
        for d in r["dimensions"]
    )
    issues = "".join(
        f'<tr><td class="mono">{esc(q["id"])}</td><td>{esc(q["severity"])}</td><td class="mono">{esc(q["stage"])} / {esc(q["itemId"])}</td><td>{esc(q["message"])}</td>'
        f'<td class="{"ok" if q["resolved"] else "warn"}">{"Resolved" if q["resolved"] else "Open"}</td></tr>'
        for q in r["issues"]
    ) or '<tr><td colspan="5">No issue was recorded by this reviewer. That is not proof of completeness.</td></tr>'
    limits = "".join(f"<li>{esc(x)}</li>" for x in dict.fromkeys(list(r["limitations"]) + design_io.LIMITATIONS))
    rounds = "".join(f'<li class="mono">{esc(x)}</li>' for x in m.rounds)
    failed = f'<div class="sec"><h3>Earlier rounds kept</h3><ul class="small">{rounds}</ul></div>' if rounds else '<p class="mini gap-top">No earlier review round file was supplied to the renderer.</p>'
    status = m.result["status"]
    return (
        head("Review", f'Method: {r["method"]}, round {r["round"]}, status {status}. Scores are bounded design judgements, not measured accuracy or stakeholder approval.')
        + '<div class="tw"><table><thead><tr><th>Dimension</th><th>Score</th><th>Evidence</th></tr></thead><tbody>'
        + dims
        + "</tbody></table></div>"
        + '<div class="sec"><h3>Issues</h3><div class="tw"><table><thead><tr><th>Issue</th><th>Severity</th><th>Item</th><th>Note</th><th>Status</th></tr></thead><tbody>'
        + issues
        + "</tbody></table></div></div>"
        + f'<div class="sec"><h3>Limits</h3><ul class="small">{limits}</ul></div>'
        + failed
    )


VIEWS = {
    "brief": view_brief,
    "context": view_context,
    "tasks": view_tasks,
    "components": view_components,
    "workflow": view_workflow,
    "framework": view_framework,
    "models": view_models,
    "fmea": view_fmea,
    "evals": view_evals,
    "rollout": view_rollout,
    "export": view_export,
    "assumptions": view_assumptions,
    "review": view_review,
}


# --------------------------------------------------------------------- shell
def nav_item(row, key, extra_cls=""):
    number = row[1]
    marker = "•" if number is None else str(number)
    return (
        f'<li class="{extra_cls}"><button class="step" type="button" data-step="{key}"><span class="n">{marker}</span>'
        f'<span><span class="t">{esc(row[3])}</span><br><span class="s">{esc(row[4])}</span></span></button></li>'
    )


def side_nav(m):
    views = m.views()
    items = ""
    if "brief" in views:
        items += nav_item(BRIEF_STEP, "brief")
    last_group = None
    for row in STEPS:
        if row[0] not in views:
            continue
        if row[2] != last_group:
            items += f'<li class="grp-lbl" aria-hidden="true">{esc(row[2])}</li>'
            last_group = row[2]
        items += nav_item(row, row[0])
    evidence = "".join(nav_item(row, row[0]) for row in EVIDENCE_STEPS if row[0] in views)
    blockers = sum(1 for h in m.d["assumptions"] if h["launchBlocker"])
    total = len(m.d["assumptions"])
    note = (
        f"Proposed design from one brief. Facts the brief did not give are labelled assumptions (H1–H{total}) with owners; {blockers} block launch."
        if total
        else "Proposed design from one brief. No top-level assumption was recorded."
    )
    return (
        '<nav class="side" aria-label="Design steps"><div class="lbl">Design</div><ol class="steps">'
        + items
        + "</ol>"
        + (f'<div class="grp">Evidence</div><ol class="steps">{evidence}</ol>' if evidence else "")
        + f'<p class="note">{esc(note)}</p></nav>'
    )


def rail(m):
    views = m.views()
    rows = [row for row in STEPS if row[0] in views]
    if len(rows) < 2:
        return ""
    groups = []
    for row in rows:
        if groups and groups[-1][0] == row[2]:
            groups[-1][1] += 1
        else:
            groups.append([row[2], 1])
    labels = "".join(f'<span style="flex:{count} 1 0">{esc(name)}</span>' for name, count in groups)
    chevrons = "".join(
        f'<li><button class="chev done" type="button" data-step="{row[0]}"><span class="num">{row[1]}</span><span class="nm">{esc(row[3])}</span><span class="state" aria-hidden="true"></span></button></li>'
        for row in rows
    )
    return f'<nav class="rail" aria-label="Steps"><div class="rg">{labels}</div><ol>{chevrons}</ol></nav>'


def render_html(design, review, mode="standard", review_rounds=()):
    if mode not in MODES:
        raise ValueError("HTML mode must be lite, standard or full.")
    structural = design_io.validate_design(design)
    checked_review = design_io.validate_review(review, structural["valid"])
    if not structural["valid"] or not checked_review["valid"]:
        raise ValueError(
            "HTML requires valid canonical design and review: "
            + json.dumps(structural["errors"] + checked_review["errors"], ensure_ascii=False)
        )
    m = Model(design, review, mode, review_rounds)
    sections = ""
    first_leaf = m.leaves[0]["id"] if m.leaves else ""
    first_node = m.nodes[0]["id"] if m.nodes else ""
    for key in m.views():
        row = STEP_BY_KEY[key]
        number = f"Step {row[1]} · {row[2]}" if row[1] else row[2]
        sections += (
            f'<section data-view="{key}" aria-labelledby="h-{key}" hidden><div class="eyebrow">{esc(number)}</div>'
            + VIEWS[key](m).replace("<h2>", f'<h2 id="h-{key}">', 1)
            + status_bar(m, key)
            + "</section>"
        )
    status = checked_review["status"]
    title = design["title"]
    # No design JSON is embedded in executable JS, so </script>, U+2028 and
    # U+2029 from inputs are inert escaped HTML text, not script delimiters.
    return (
        '<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
        '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; script-src \'unsafe-inline\'; style-src \'unsafe-inline\'; img-src \'none\'; connect-src \'none\'; font-src \'none\'; base-uri \'none\'; form-action \'none\'">'
        f"<title>{esc(title)} · Design view</title><style>{CSS}</style></head>"
        f'<body data-default-leaf="{esc(first_leaf)}" data-default-node="{esc(first_node)}">'
        '<header class="top"><div class="brand"><div class="mark" aria-hidden="true"><svg viewBox="0 0 16 16"><circle cx="3" cy="8" r="2" fill="#fff"/><circle cx="13" cy="3.5" r="2" fill="#fff"/><circle cx="13" cy="12.5" r="2" fill="#fff"/><path d="M5 8 L11 4 M5 8 L11 12" stroke="#fff" stroke-width="1.4"/></svg></div><h1>Agent Design Studio</h1></div>'
        f'<div class="proj"><span>Design</span><b>{esc(title)}</b><span class="chip">{esc(mode)}</span></div><div class="sp"></div>'
        f'<span class="chip status-{esc(status)}">DESIGN ONLY · {esc(status.upper())}</span>'
        '<span class="chip" title="This view is read-only. It shows a proposed design, not an approved one.">read-only</span></header>'
        '<div class="shell">'
        + side_nav(m)
        + '<main class="main"><div class="main-in">'
        + rail(m)
        + sections
        + "</div></main></div>"
        '<footer>Self-contained local HTML · no network assets, model calls or action controls. design.json and review.json remain the source of truth.</footer>'
        f"<script>{JS}</script></body></html>\n"
    )


CSS = r"""
:root{--bg:#eef1f0;--surface:#ffffff;--surface-2:#f6f8f7;--sunk:#e4e9e7;--fg:#16202a;--muted:#5a6570;--line:#d3dad7;--accent:#0b6d66;--accent-soft:#d5ebe7;--accent-fg:#ffffff;--t-llm:#6a4bd6;--t-code:#365a7d;--t-read:#2c8549;--t-write:#c25a14;--t-human:#b52f4b;--t-rag:#0b7c8a;--t-decision:#946f00;--crit:#b52f4b;--warn:#946f00;--ok:#2c8549;--f-display:"IBM Plex Sans Condensed","Arial Narrow",system-ui,sans-serif;--f-body:"IBM Plex Sans",system-ui,-apple-system,"Segoe UI",sans-serif;--f-mono:"IBM Plex Mono",ui-monospace,Menlo,Consolas,monospace;color-scheme:light}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0f1418;--surface:#161d23;--surface-2:#1b242b;--sunk:#222c34;--fg:#e3e9ed;--muted:#9aa6af;--line:#2c3740;--accent:#4cc3b7;--accent-soft:#16332f;--accent-fg:#0b1513;--t-llm:#a48fff;--t-code:#8fb2d6;--t-read:#6cc68b;--t-write:#f09a5b;--t-human:#f37b90;--t-rag:#56c7d4;--t-decision:#e0b64a;--crit:#f37b90;--warn:#e0b64a;--ok:#6cc68b;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#0f1418;--surface:#161d23;--surface-2:#1b242b;--sunk:#222c34;--fg:#e3e9ed;--muted:#9aa6af;--line:#2c3740;--accent:#4cc3b7;--accent-soft:#16332f;--accent-fg:#0b1513;--t-llm:#a48fff;--t-code:#8fb2d6;--t-read:#6cc68b;--t-write:#f09a5b;--t-human:#f37b90;--t-rag:#56c7d4;--t-decision:#e0b64a;--crit:#f37b90;--warn:#e0b64a;--ok:#6cc68b;color-scheme:dark}
*{box-sizing:border-box}html{overflow-x:hidden}body{margin:0;background:var(--bg);color:var(--fg);font-family:var(--f-body);font-size:14px;line-height:1.5;overflow-wrap:break-word}
button{font:inherit;color:inherit}:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
h1,h2,h3{font-family:var(--f-display);margin:0;letter-spacing:.005em}.mono{font-family:var(--f-mono)}.tnum{font-variant-numeric:tabular-nums}
.small{font-size:13px}.mini{font-size:12.5px;color:var(--muted)}.tiny{font-size:11.5px}.nowrap{white-space:nowrap}.gap-top{margin-top:10px}.pre{white-space:pre-wrap}
.top{position:sticky;top:0;z-index:5;background:var(--surface);border-bottom:1px solid var(--line);padding:10px 16px;display:flex;align-items:center;gap:14px;flex-wrap:wrap}
.brand{display:flex;align-items:center;gap:10px;min-width:0}.mark{width:26px;height:26px;border-radius:6px;background:var(--accent);display:grid;place-items:center;flex:none}.mark svg{width:16px;height:16px}.brand h1{font-size:17px;font-weight:700}
.proj{display:flex;align-items:center;gap:8px;color:var(--muted);font-size:13px;min-width:0;flex-wrap:wrap}.proj b{color:var(--fg);font-weight:600}.top .sp,.statusbar .sp{flex:1}
.btn{border:1px solid var(--line);background:var(--surface);border-radius:6px;padding:6px 11px;cursor:pointer;font-size:13px;display:inline-flex;align-items:center;gap:6px}.btn:hover{border-color:var(--accent)}.btn.primary{background:var(--accent);border-color:var(--accent);color:var(--accent-fg);font-weight:600}.btn.small{padding:4px 9px;font-size:12px;min-height:32px}
.shell{display:grid;grid-template-columns:236px minmax(0,1fr);min-height:calc(100vh - 52px)}
.side{border-right:1px solid var(--line);background:var(--surface-2);padding:18px 14px}.side .lbl,.side .grp{font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);margin:0 8px 8px}.side .grp{margin-top:16px}
.steps{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:2px}.steps li{position:relative}
.steps li.grp-lbl{font-family:var(--f-mono);font-size:10.5px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);padding:10px 8px 2px}
.steps li+li:not(.grp-lbl)::before{content:"";position:absolute;left:19px;top:-6px;width:2px;height:8px;background:var(--line)}
.steps li+li:not(.grp-lbl)::after{content:"↓";position:absolute;left:15px;top:-11px;font-size:9px;color:var(--muted);line-height:1}
.step{display:grid;grid-template-columns:24px 1fr;gap:8px;align-items:start;padding:8px;border-radius:7px;cursor:pointer;border:1px solid transparent;text-align:left;background:none;width:100%;min-height:40px}
.step:hover{background:var(--sunk)}.step[aria-current="step"]{background:var(--surface);border-color:var(--line);box-shadow:0 1px 0 var(--line)}
.step .n{width:22px;height:22px;border-radius:50%;display:grid;place-items:center;font-size:11px;font-family:var(--f-mono);border:1.5px solid var(--line);color:var(--muted);background:var(--surface)}
.step[aria-current="step"] .n{background:var(--accent);border-color:var(--accent);color:var(--accent-fg)}.step .t{font-weight:600;font-size:13.5px;line-height:1.25}.step .s{font-size:11.5px;color:var(--muted)}
.side .note{margin:18px 8px 0;font-size:12px;color:var(--muted);border-top:1px solid var(--line);padding-top:12px}
.main{padding:22px 16px 60px 24px;min-width:0}.main-in{max-width:1180px}
.rail{margin:0 0 20px;overflow-x:auto;padding-bottom:4px}.rail .rg{display:flex;min-width:1120px;font:11px/1 var(--f-mono);text-transform:uppercase;letter-spacing:.08em;color:var(--muted);margin:0 0 4px}.rail .rg span{padding-left:14px;min-width:0}
.rail ol{list-style:none;margin:0;padding:0;display:flex;min-width:1120px}.rail li{flex:1 1 0;min-width:0}.rail li+li{margin-left:-8px}
.chev{display:flex;align-items:center;gap:6px;width:100%;min-height:44px;padding:6px 16px 6px 22px;border:0;background:var(--sunk);color:var(--fg);cursor:pointer;text-align:left;font-size:12px;line-height:1.2;clip-path:polygon(0 0,calc(100% - 14px) 0,100% 50%,calc(100% - 14px) 100%,0 100%,14px 50%)}.chev .nm{overflow-wrap:normal;word-break:normal}
.rail li:first-child .chev{padding-left:12px;clip-path:polygon(0 0,calc(100% - 14px) 0,100% 50%,calc(100% - 14px) 100%,0 100%)}
.chev .num{font-family:var(--f-mono);font-size:11px;color:var(--muted)}.chev .nm{font-weight:600;min-width:0}.chev .state::before{content:"✓";color:var(--accent);font-size:11px;margin-left:auto}
.chev.done{background:var(--accent-soft)}.chev[aria-current="step"]{background:var(--surface);box-shadow:inset 0 -2px 0 var(--accent),inset 0 2px 0 var(--accent);font-weight:700}.chev[aria-current="step"] .state::before{content:"●"}
.eyebrow{font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);margin-bottom:4px;font-family:var(--f-mono)}
.phead{display:flex;align-items:flex-end;gap:12px;flex-wrap:wrap;margin-bottom:6px}.phead h2{font-size:26px;font-weight:700}
.lead{color:var(--muted);max-width:72ch;margin:4px 0 18px}.sec{margin-top:26px}.sec.first{margin-top:0}.sec>h3,.h3{font-size:17px;font-weight:600;margin-bottom:4px}.sec>.sub{color:var(--muted);font-size:13px;margin:0 0 10px;max-width:80ch}
.panel{background:var(--surface);border:1px solid var(--line);border-radius:9px;min-width:0}.cc,.tc,.kpi,.ph,.calls li{min-width:0}
.tw{overflow-x:auto;border:1px solid var(--line);border-radius:9px;background:var(--surface)}table{border-collapse:collapse;width:100%;font-size:13px}th,td{text-align:left;padding:9px 11px;border-bottom:1px solid var(--line);vertical-align:top}
th{font-size:11.5px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);font-weight:600;background:var(--surface-2);white-space:nowrap}tr:last-child td{border-bottom:0}td.num{font-variant-numeric:tabular-nums;text-align:right;white-space:nowrap}td.ok,.ok{color:var(--ok);font-weight:600;white-space:nowrap}td.gap,.gap{color:var(--crit);font-weight:600;white-space:nowrap}td.warn,.warn{color:var(--warn);font-weight:600;white-space:nowrap}td.blocks{color:var(--crit);font-weight:600;white-space:nowrap}pre,.q,.io,.io *,.fn,.in,.pass{overflow-wrap:anywhere}
.chip{display:inline-flex;align-items:center;gap:5px;font-size:11.5px;padding:1px 8px;border-radius:999px;border:1px solid var(--line);background:var(--surface-2);line-height:1.6;max-width:100%}.chip .d{width:7px;height:7px;border-radius:50%;flex:none}
button.chip{cursor:pointer;font-family:inherit}button.chip:hover{border-color:var(--accent)}button.chip.link{border:0;background:none;padding:0}
.tag-llm{--c:var(--t-llm)}.tag-code{--c:var(--t-code)}.tag-read{--c:var(--t-read)}.tag-write{--c:var(--t-write)}.tag-human{--c:var(--t-human)}.tag-rag{--c:var(--t-rag)}.tag-decision{--c:var(--t-decision)}
.chip.ty{border-color:color-mix(in srgb,var(--c) 45%,var(--line));background:color-mix(in srgb,var(--c) 10%,var(--surface));color:var(--fg)}.chip.ty .d{background:var(--c)}
.status-pass{color:var(--ok);font-weight:600}.status-needs-work{color:var(--warn);font-weight:600}
.risk-high{color:var(--crit);font-weight:600}.risk-medium{color:var(--warn);font-weight:600}.risk-low{color:var(--ok);font-weight:600}.why-r{font-size:10.5px;color:var(--crit);font-family:var(--f-mono)}
.inline-list{display:flex;flex-wrap:wrap;gap:6px}.fm-id{font-family:var(--f-mono);font-size:11.5px;color:var(--muted)}.fm-name{font-weight:600}.common{font-size:10.5px;text-transform:uppercase;letter-spacing:.06em;color:var(--accent);font-weight:600}
.kv{display:grid;grid-template-columns:150px minmax(0,1fr);gap:10px 16px;margin:12px 0 0}.kv dt{font-size:12px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);font-weight:600;padding-top:2px}.kv dd{margin:0;min-width:0}
.quotes{display:flex;flex-direction:column;gap:6px}.q{font-family:var(--f-mono);font-size:12.5px;background:var(--surface-2);border:1px solid var(--line);border-radius:6px;padding:6px 9px}
.callout{padding:14px 16px;border-left:3px solid var(--accent);background:var(--accent-soft);border-radius:0 8px 8px 0}.callout p{margin:4px 0 0}.fit{margin-bottom:16px}
.box{padding:14px 16px}.box h3{font-size:15px;margin:0 0 8px}.card{margin-bottom:12px}.card-title{font-size:17px;margin:2px 0 8px}.crumb{font-size:12px;color:var(--muted);font-family:var(--f-mono)}
.two{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.stack{display:grid;gap:12px;align-content:start}
.brief-grid{display:grid;grid-template-columns:minmax(0,1.25fr) minmax(0,1fr);gap:16px;align-items:start}.sentence{font-size:17px;line-height:1.45;max-width:70ch;margin:0 0 12px}.derived{border-left:3px solid var(--warn);padding-left:8px}
.calls{list-style:none;margin:0;padding:0;display:grid;gap:10px}.calls li{padding:12px 14px;display:grid;grid-template-columns:26px minmax(0,1fr);gap:8px}.calls .n{font-family:var(--f-mono);color:var(--accent);font-weight:600}.calls .rej{font-size:12.5px;color:var(--muted);margin-top:4px}.calls .rej b{color:var(--fg);font-weight:600}
.kpimini{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:4px 12px;font-size:13px;padding:7px 0;border-bottom:1px solid var(--line)}.kpimini:last-child{border-bottom:0}.kpimini .v{font-family:var(--f-mono);white-space:nowrap}.kpimini .v b{color:var(--accent)}.kpimini .df{grid-column:1/-1;color:var(--muted);font-size:12px}
.blk{font-size:13px;padding:6px 0;border-bottom:1px solid var(--line);display:grid;grid-template-columns:44px minmax(0,1fr);gap:8px}.blk:last-child{border-bottom:0}.blk .o{display:block;color:var(--muted);font-size:12px}
.lb{font-size:11.5px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);font-weight:600;margin-bottom:6px}.brief-text{font-size:13.5px;max-width:90ch;white-space:pre-wrap}
.tree-wrap{overflow-x:auto;padding:16px}.tree2{display:flex;flex-direction:column;align-items:center}.root{background:var(--fg);color:var(--bg);border-radius:9px;padding:10px 18px;font-family:var(--f-display);font-weight:700;font-size:16px;text-align:center}.root small{display:block;font-family:var(--f-mono);font-weight:400;font-size:11px;opacity:.75}
.stem{width:2px;height:16px;background:var(--line)}.trow{display:grid;gap:12px;width:100%;position:relative;padding-top:16px}.trow::before{content:"";position:absolute;top:0;left:calc(100% / (var(--n) * 2));right:calc(100% / (var(--n) * 2));height:2px;background:var(--line)}
.tcol{position:relative;display:flex;flex-direction:column;gap:8px;min-width:0}.tcol::before{content:"";position:absolute;top:-16px;left:50%;width:2px;height:16px;background:var(--line)}
.tbox,.top-leaf{background:var(--surface);border:1.5px solid var(--fg);border-radius:8px;padding:8px 10px}.tbox .id,.top-leaf .id{font-family:var(--f-mono);font-size:11px;color:var(--muted)}.tbox .nm,.top-leaf .nm{font-weight:600;font-size:14px;line-height:1.25}
.mode{display:inline-block;margin-top:4px;font-family:var(--f-mono);font-size:10.5px;padding:0 6px;border-radius:4px;background:var(--sunk);color:var(--muted)}
.subs{display:flex;flex-direction:column;gap:8px;padding-left:12px;border-left:2px solid var(--line);margin-left:10px}
.leaf{background:var(--surface);border:1px solid var(--line);border-radius:7px;padding:8px 9px;cursor:pointer;text-align:left;width:100%;display:block}.leaf:hover{border-color:var(--accent)}.leaf[aria-selected="true"]{border-color:var(--accent);box-shadow:0 0 0 2px var(--accent-soft)}.top-leaf[aria-selected="true"]{border-color:var(--accent)}
.leaf .ln{font-weight:600;font-size:12.5px;line-height:1.3}.leaf .bs{display:flex;flex-wrap:wrap;gap:4px;margin:5px 0}.leaf .bs .chip{font-size:10.5px;padding:0 6px}.leaf .exs{font-size:11.5px;color:var(--muted);line-height:1.35}.leaf .exs div::before{content:"• "}.leaf .exs.basis div::before{content:"basis: ";font-family:var(--f-mono);font-size:10px}.leaf .meta{font-size:10.5px;font-family:var(--f-mono);color:var(--muted);margin-top:4px}
.detail{padding:18px 20px;margin-top:14px}.detail h3{font-size:20px;font-weight:700;margin:2px 0 10px}.dtools{display:flex;gap:8px;flex-wrap:wrap;margin-top:18px;padding-top:14px;border-top:1px solid var(--line)}
.attr td.ck{text-align:center;color:var(--accent);font-weight:700}
.ctype{margin-top:20px}.ctype>h3{font-size:16px;display:flex;align-items:center;gap:8px;margin-bottom:8px}.ccards{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:10px}.cc{padding:12px 14px;display:flex;flex-direction:column;gap:6px}.cc .nm{font-weight:600}.cc .why{font-size:12px;border-left:3px solid var(--t-code);padding-left:8px;color:var(--muted)}.cc .tk{display:flex;flex-wrap:wrap;gap:4px}
.io{font-size:12px;margin-top:6px}.io ul{margin:2px 0 6px;padding-left:16px}.plainlist{margin:0;padding-left:16px}ul.mono li,ul.tiny li{font-family:var(--f-mono);font-size:11.5px}
.taskbar,.legend{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:10px;align-items:center}.fbtn{border:1px solid var(--line);background:var(--surface);border-radius:999px;padding:3px 11px;font-size:12.5px;cursor:pointer;min-height:32px}.fbtn[aria-pressed="true"]{background:var(--fg);color:var(--bg);border-color:var(--fg)}
.wf-wrap{overflow-x:auto;border:1px solid var(--line);border-radius:9px;background:var(--surface);background-image:radial-gradient(var(--line) 1px,transparent 1px);background-size:18px 18px}.wf-wrap svg{display:block}
.wf-node{cursor:pointer}.wf-node rect{stroke-width:1.5}.wf-node text{font-family:var(--f-body);fill:var(--fg);font-size:12.5px}.wf-node .tt{font-weight:600}.wf-node .ty{font-family:var(--f-mono);font-size:11px;fill:var(--muted);letter-spacing:.03em}.wf-node .ex{font-size:11px;fill:var(--muted);font-style:italic}
.wf-node:hover rect{stroke-width:2.5}.wf-node.sel rect{stroke-width:3}.wf-node.dim,.wf-edgeg.dim,.wf-tag.dim{opacity:.15}
.n-llm rect{fill:color-mix(in srgb,var(--t-llm) 13%,var(--surface));stroke:var(--t-llm)}.n-code rect{fill:color-mix(in srgb,var(--t-code) 13%,var(--surface));stroke:var(--t-code)}.n-read rect{fill:color-mix(in srgb,var(--t-read) 13%,var(--surface));stroke:var(--t-read)}.n-write rect{fill:color-mix(in srgb,var(--t-write) 13%,var(--surface));stroke:var(--t-write)}.n-human rect{fill:color-mix(in srgb,var(--t-human) 13%,var(--surface));stroke:var(--t-human)}.n-rag rect{fill:color-mix(in srgb,var(--t-rag) 13%,var(--surface));stroke:var(--t-rag)}
.wf-edge{fill:none;stroke:var(--muted);stroke-width:1.4}.wf-elbl{font-family:var(--f-mono);font-size:11px;fill:var(--muted)}.wf-elbl-bg{fill:var(--surface);stroke:var(--line);stroke-width:.5}.arrowhead{fill:var(--muted)}.wf-lane{font-family:var(--f-mono);font-size:11px;fill:var(--muted);letter-spacing:.06em}.wf-band{stroke:var(--line);stroke-dasharray:6 4}
.wf-tag{font-family:var(--f-mono);font-size:11px;fill:var(--crit)}.wf-tag.exit{fill:var(--warn)}.wf-tag.continue{fill:var(--muted)}
.wf-detail{margin-top:14px;padding:16px 18px}.wf-detail h3{font-size:18px;margin:6px 0}
.formula{display:flex;flex-wrap:wrap;gap:10px}.rpn{font-family:var(--f-mono);font-weight:600;padding:2px 8px;border-radius:5px;display:inline-block;min-width:42px;text-align:center}.rpn.tiny{min-width:0;padding:0 4px;font-size:11px}.rpn.hi{background:color-mix(in srgb,var(--crit) 16%,var(--surface));color:var(--crit)}.rpn.md{background:color-mix(in srgb,var(--warn) 16%,var(--surface));color:var(--warn)}.rpn.lo{background:color-mix(in srgb,var(--ok) 14%,var(--surface));color:var(--ok)}
.fm-row{cursor:pointer}.fm-row:hover td{background:var(--surface-2)}.fm-row.flash td{background:var(--accent-soft)}.fm-open td{background:var(--surface-2)}.fm-table td.control{min-width:220px}
.fm-x{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;padding:6px 2px}.fm-x h4{margin:0 0 4px;font-size:11.5px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted)}.fm-x p{margin:0}
.scroll{overflow-x:auto}.heat{border-collapse:separate;border-spacing:3px;font-size:11.5px;width:auto}.heat td,.heat th{text-align:center;padding:4px 6px;border:0;border-radius:4px;min-width:38px}.heat th{background:none}.h-hi{background:color-mix(in srgb,var(--crit) 20%,var(--surface))}.h-md{background:color-mix(in srgb,var(--warn) 20%,var(--surface))}.h-lo{background:color-mix(in srgb,var(--ok) 16%,var(--surface))}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:12px}.tc{padding:14px;display:flex;flex-direction:column;gap:8px}.tc .h{display:flex;justify-content:space-between;gap:8px;align-items:flex-start}.tc .pass{font-size:12.5px;border-left:3px solid var(--ok);padding-left:8px}.tc pre{font-family:var(--f-mono);font-size:11px;white-space:pre-wrap;background:var(--surface-2);border:1px solid var(--line);border-radius:6px;padding:8px;margin:0 0 8px;max-height:360px;overflow:auto}
.gates{counter-reset:g;list-style:none;padding:0;margin:0;display:grid;gap:8px}.gates li{padding:10px 14px;display:flex;gap:10px;flex-wrap:wrap;align-items:baseline}.gates li::before{counter-increment:g;content:counter(g);font-family:var(--f-mono);color:var(--accent);font-weight:600}
.kpis{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:12px}.kpi{padding:14px 16px}.kpi .k{font-weight:600}.kpi .bt{display:flex;align-items:baseline;gap:8px;margin:6px 0 10px;font-family:var(--f-mono)}.kpi .bt .b{color:var(--muted);text-decoration:line-through}.kpi .bt .tg{font-size:20px;font-weight:600;color:var(--accent)}.kpi ul{margin:6px 0;padding-left:16px;font-size:13px}
.phases{display:grid;grid-template-columns:repeat(var(--n),minmax(0,1fr));border:1px solid var(--line);border-radius:9px;overflow:hidden;background:var(--surface)}.ph{padding:14px;border-right:1px solid var(--line)}.ph:last-child{border-right:0}.ph .w{font-family:var(--f-mono);font-size:11.5px;color:var(--muted);margin-top:6px}.ph .nm{font-family:var(--f-display);font-weight:700;font-size:16px;margin:2px 0 6px}.ph .gate{margin-top:10px;font-size:12px;border-top:1px dashed var(--line);padding-top:8px}.ph .gate b{color:var(--accent)}
.calc{display:grid;grid-template-columns:minmax(0,1.1fr) minmax(0,1fr);gap:16px;align-items:start}.in-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;padding:14px}.field{display:flex;flex-direction:column;gap:5px}.field label{font-size:12px;font-weight:600;color:var(--muted);text-transform:uppercase;letter-spacing:.06em}.field input{font:inherit;font-family:var(--f-mono);color:var(--fg);background:var(--surface);border:1px solid var(--line);border-radius:7px;padding:8px 10px;width:100%}
.notes{padding:0 14px 14px 30px;margin:0}.out{padding:16px}.big{font-family:var(--f-mono);font-size:28px;font-weight:600;color:var(--accent)}.month{margin-top:8px}
.filelist{display:grid;gap:6px;margin-top:8px}.fl{display:grid;grid-template-columns:200px minmax(0,1fr);gap:10px;font-size:13px;padding:8px 12px;border:1px solid var(--line);border-radius:8px;background:var(--surface)}.fl .fn{font-family:var(--f-mono);font-weight:500}
details.panel{margin-bottom:10px}details summary{cursor:pointer}
.statusbar{margin-top:26px;display:flex;align-items:center;gap:10px;flex-wrap:wrap;padding:10px 14px;background:var(--surface);border:1px solid var(--line);border-radius:10px}.statusbar .st{font-weight:600;color:var(--ok)}.statusbar .cnt{color:var(--muted);font-size:13px}
footer{padding:14px 24px 30px;font-size:12px;color:var(--muted)}
[hidden]{display:none!important}
@media (max-width:900px){.shell{grid-template-columns:1fr}.side{border-right:0;border-bottom:1px solid var(--line);padding:8px 16px;overflow-x:auto}.side .lbl,.side .grp,.side .note{display:none}.steps{flex-direction:row;gap:4px;width:max-content}.steps li+li::before,.steps li+li::after{display:none}.steps li.grp-lbl{padding:8px 4px}.step{width:auto;grid-template-columns:22px auto;white-space:nowrap}.step .s{display:none}.main{padding:16px}.rail{display:none}.two,.calc,.brief-grid{grid-template-columns:1fr}.phases{grid-template-columns:1fr 1fr}.ph{border-bottom:1px solid var(--line)}}
@media (max-width:620px){.kv{grid-template-columns:1fr;gap:2px 0}.kv dd{margin-bottom:10px}.fm-x,.ccards,.cards,.kpis,.phases,.in-grid{grid-template-columns:1fr}.ph{border-right:0}.fl{grid-template-columns:1fr}.phead h2{font-size:22px}.tree-wrap{padding:10px}}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
@media print{.side,.rail,.statusbar button{display:none}.shell{display:block}section[data-view][hidden]{display:block!important}.wf-wrap,.tw,.tree-wrap{overflow:visible}body{background:#fff}}
"""

JS = r"""
(() => {
  "use strict";
  const views = Array.from(document.querySelectorAll("section[data-view]"));
  const order = views.map(v => v.dataset.view);
  const navButtons = Array.from(document.querySelectorAll("nav [data-step]"));
  function byAttr(attr, value) {
    return Array.from(document.querySelectorAll("[" + attr + "]")).filter(el => el.getAttribute(attr) === value);
  }
  function show(key) {
    if (!order.includes(key)) return false;
    views.forEach(v => { v.hidden = v.dataset.view !== key; });
    navButtons.forEach(b => {
      if (b.dataset.step === key) {
        b.setAttribute("aria-current", "step");
        if (b.classList.contains("chev") && b.scrollIntoView) b.scrollIntoView({ block: "nearest", inline: "center" });
      } else b.removeAttribute("aria-current");
    });
    try { history.replaceState(null, "", "#" + key); } catch (_) {}
    try { localStorage.setItem("agent-design-studio.lastView", key); } catch (_) {}
    return true;
  }
  function select(attr, id, detailAttr) {
    document.querySelectorAll("[" + attr + "]").forEach(el => {
      const on = el.getAttribute(attr) === id;
      el.setAttribute("aria-selected", on ? "true" : "false");
      el.classList.toggle("sel", on);
    });
    document.querySelectorAll("[" + detailAttr + "]").forEach(el => { el.hidden = el.getAttribute(detailAttr) !== id; });
  }
  function filterTasks(task) {
    document.querySelectorAll("[data-task]").forEach(b => b.setAttribute("aria-pressed", b.dataset.task === task ? "true" : "false"));
    document.querySelectorAll("[data-tasks]").forEach(el => {
      const list = (el.getAttribute("data-tasks") || "").split(" ").filter(Boolean);
      el.classList.toggle("dim", task !== "all" && !list.includes(task));
    });
  }
  function openRisk(id, flash) {
    document.querySelectorAll("[data-fmrow]").forEach(r => {
      const on = r.getAttribute("data-fmrow") === id;
      r.classList.toggle("fm-open", on);
      r.setAttribute("aria-expanded", on ? "true" : "false");
    });
    document.querySelectorAll("[data-fm-detail]").forEach(r => { r.hidden = r.getAttribute("data-fm-detail") !== id; });
    const row = byAttr("data-fmrow", id)[0];
    if (row && flash) {
      row.scrollIntoView({ block: "center" });
      row.classList.add("flash");
      setTimeout(() => row.classList.remove("flash"), 1200);
    }
  }
  function recalc(input) {
    const out = document.querySelector("[data-month-cost]");
    if (!out) return;
    const per = parseFloat(out.getAttribute("data-month-cost")) || 0;
    const volume = parseFloat(input.value) || 0;
    out.textContent = "USD " + Math.round(per * volume).toLocaleString("en-US");
  }
  document.addEventListener("click", event => {
    const t = event.target;
    const step = t.closest("[data-step]"); if (step) { show(step.getAttribute("data-step")); window.scrollTo({ top: 0 }); return; }
    const leaf = t.closest("[data-leaf]"); if (leaf) { select("data-leaf", leaf.getAttribute("data-leaf"), "data-leaf-detail"); return; }
    const goleaf = t.closest("[data-goleaf]"); if (goleaf) {
      const id = goleaf.getAttribute("data-goleaf");
      select("data-leaf", id, "data-leaf-detail"); show("tasks");
      const target = byAttr("data-leaf", id)[0]; if (target) target.scrollIntoView({ block: "center" });
      return;
    }
    const showwf = t.closest("[data-showwf]"); if (showwf) { filterTasks(showwf.getAttribute("data-showwf")); show("workflow"); window.scrollTo({ top: 0 }); return; }
    const task = t.closest("[data-task]"); if (task) { filterTasks(task.getAttribute("data-task")); return; }
    const node = t.closest("[data-node]"); if (node) { select("data-node", node.getAttribute("data-node"), "data-node-detail"); return; }
    const gonode = t.closest("[data-gonode]"); if (gonode) {
      const id = gonode.getAttribute("data-gonode");
      select("data-node", id, "data-node-detail"); show("workflow");
      const target = byAttr("data-node", id)[0]; if (target && target.scrollIntoView) target.scrollIntoView({ block: "center", inline: "center" });
      return;
    }
    const gofm = t.closest("[data-gofm]"); if (gofm) { const id = gofm.getAttribute("data-gofm"); show("fmea"); openRisk(id, true); return; }
    const row = t.closest("[data-fmrow]"); if (row) {
      const id = row.getAttribute("data-fmrow");
      openRisk(row.classList.contains("fm-open") ? "" : id, false);
    }
  });
  document.addEventListener("keydown", event => {
    if (event.key !== "Enter" && event.key !== " ") return;
    if (!event.target.closest) return;
    if (event.target.matches("input, button, a, summary, textarea")) return;
    const el = event.target.closest("[data-node], [data-leaf], [data-fmrow]");
    if (!el) return;
    event.preventDefault();
    el.click();
  });
  document.addEventListener("input", event => { if (event.target.matches("[data-calc]")) recalc(event.target); });
  function initial() {
    let hash = "";
    try { hash = decodeURIComponent(location.hash.slice(1)); } catch (_) {}
    if (order.includes(hash)) return hash;
    let last = "";
    try { last = localStorage.getItem("agent-design-studio.lastView") || ""; } catch (_) {}
    return order.includes(last) ? last : order[0];
  }
  window.addEventListener("hashchange", () => { let h = ""; try { h = decodeURIComponent(location.hash.slice(1)); } catch (_) {} if (order.includes(h)) show(h); });
  window.addEventListener("beforeprint", () => views.forEach(v => { v.hidden = false; }));
  window.addEventListener("afterprint", () => show(initial()));
  select("data-leaf", document.body.getAttribute("data-default-leaf") || "", "data-leaf-detail");
  select("data-node", document.body.getAttribute("data-default-node") || "", "data-node-detail");
  filterTasks("all");
  show(initial());
})();
"""


# ------------------------------------------------------------------- output
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


def review_rounds_near(review_path):
    """Names of kept earlier review rounds next to review.json, if any."""
    folder = Path(review_path).parent
    try:
        return sorted(p.name for p in folder.glob("review-round-*.json") if p.is_file())
    except OSError:
        return []


def export_html(design_path, review_path, out, mode="standard", review_rounds=None):
    design = design_io.load_json(design_path)
    review = design_io.load_json(review_path)
    rounds = review_rounds_near(review_path) if review_rounds is None else review_rounds
    document = render_html(design, review, mode, rounds)
    path = _write_new(out, document, (design_path, review_path))
    return {
        "ok": True,
        "designOnly": True,
        "readOnlyView": True,
        "mode": mode,
        "views": list(LITE_VIEWS if mode == "lite" else VIEW_ORDER),
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
    parser.add_argument("--mode", choices=MODES, default="standard")
    args = parser.parse_args(argv)
    try:
        result = export_html(args.design, args.review, args.out, args.mode)
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
