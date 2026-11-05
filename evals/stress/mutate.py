"""Stress harness: mutate the skill's telecom example and run validate / html / pdf on each variant."""
import json, copy, subprocess, sys, os, shutil
from pathlib import Path

SK = Path(sys.argv[1])            # skill dir (scripts under SK/scripts)
EX = Path(sys.argv[2])            # examples/telecom dir
OUT = Path(sys.argv[3]); OUT.mkdir(parents=True, exist_ok=True)
base = json.loads((EX / "design.json").read_text())
review = (EX / "review.json").read_text()

def run(cmd, timeout=180):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, (p.stdout + p.stderr)
    except subprocess.TimeoutExpired:
        return 124, "TIMEOUT"

def items(d, stage): return d["stages"][stage]["items"]

VARIANTS = {}
def variant(name):
    def deco(fn): VARIANTS[name] = fn; return fn
    return deco

@variant("01_xss_strings")
def _(d):
    bad = '<script>alert(1)</script><img src=x onerror=alert(2)> " onmouseover="alert(3)'
    d["title"] = "Telecom " + bad
    d["brief"] += " " + bad
    for it in items(d, "tasks")[:3]:
        it["title"] += bad; it["description"] += bad
        if "examples" in it["data"]: it["data"]["examples"] = [bad]
    items(d, "fmea")[0]["data"]["control"] += bad
    d["presentation"]["systemSentence"] += bad
    d["presentation"]["designCalls"][0]["choice"] += bad
    return d

@variant("02_unicode_scripts")
def _(d):
    u = " हिंदी शिकायत · العربية · 中文 · emoji 🚀✅ · Ωmega"
    d["title"] += u; d["presentation"]["systemSentence"] += u
    for it in items(d, "tasks")[:4]: it["title"] += u
    for it in items(d, "workflow")[:3]: it["title"] += u
    items(d, "fmea")[0]["title"] += u
    return d

@variant("03_very_long_labels")
def _(d):
    long = " " + ("verylongtokenwithoutanybreaks" * 12) + " " + ("a long predicate that keeps going, " * 20)
    w = items(d, "workflow")[1]; w["title"] += long
    c = json.loads(w["description"])
    for t in c.get("transitions", []): t["when"] = t["when"] + long
    w["description"] = json.dumps(c)
    # keep semantics in sync for exact 'when'
    for t in d["semantics"]["transitions"]:
        if t["from"] == w["id"]: t["when"] = t["when"] + long
    items(d, "tasks")[2]["title"] += long
    return d

@variant("04_twelve_design_calls")
def _(d):
    c = d["presentation"]["designCalls"][0]
    d["presentation"]["designCalls"] = [dict(c, choice=f"Call {i}: " + c["choice"]) for i in range(12)]
    d["presentation"]["autonomy"] = d["presentation"]["autonomy"] * 6
    return d

@variant("05_zero_fmea")
def _(d):
    items(d, "fmea").clear()
    for e in items(d, "evals"): e["data"]["failureModeIds"] = []
    return d

@variant("06_zero_models_all_code")
def _(d):
    items(d, "models").clear()
    return d

@variant("07_duplicate_ids")
def _(d):
    items(d, "tasks")[2]["id"] = items(d, "tasks")[1]["id"]
    return d

@variant("08_cycle_back_edge")
def _(d):
    w = items(d, "workflow")
    last, first = w[-1], w[1]
    c = json.loads(last["description"]); c.setdefault("transitions", []).append({"to": first["id"], "when": "retry whole case", "mode": "exclusive"}); last["description"] = json.dumps(c)
    last["data"]["next"] = list(dict.fromkeys(last["data"].get("next", []) + [first["id"]]))
    d["semantics"]["transitions"].append({"from": last["id"], "to": first["id"], "when": "retry whole case", "outcome": "repeat"})
    return d

@variant("09_rpn_extremes")
def _(d):
    f = items(d, "fmea")
    f[0]["data"].update(severity=10, occurrence=10, detection=10)
    f[1]["data"].update(severity=0, occurrence=-1, detection=11)
    return d

@variant("10_deep_task_tree")
def _(d):
    t = items(d, "tasks")
    leaf = next(x for x in t if x["kind"] == "task" and x["data"]["mode"] == "leaf")
    leaf["data"]["mode"] = "sequence"
    for i in range(1, 4):
        n = copy.deepcopy(leaf); n["id"] = f"{leaf['id']}.{i}"; n["data"]["parentId"] = leaf["id"]; n["data"]["mode"] = "leaf"; n["title"] = f"Deep leaf {i}"
        t.append(n)
    # go one level deeper
    n2 = copy.deepcopy(t[-1]); n2["id"] = t[-1]["id"] + ".1"; n2["data"]["parentId"] = t[-1]["id"]; t[-1]["data"]["mode"] = "sequence"; t.append(n2)
    return d

@variant("11_twelve_top_tasks")
def _(d):
    t = items(d, "tasks")
    root = next(x for x in t if x["kind"] == "task" and x["data"]["parentId"] == "")
    tops = [x for x in t if x["kind"] == "task" and x["data"]["parentId"] == root["id"]]
    for i in range(12):
        n = copy.deepcopy(tops[0]); n["id"] = f"T9{i}"; n["title"] = f"Extra task {i}"; n["data"]["mode"] = "leaf"; t.append(n)
    return d

@variant("12_fan_out_eight")
def _(d):
    w = items(d, "workflow")
    src = w[1]; c = json.loads(src["description"])
    targets = [x["id"] for x in w[2:10]]
    c["transitions"] = [{"to": t, "when": f"intent == case_{i}", "mode": "exclusive"} for i, t in enumerate(targets)]
    src["description"] = json.dumps(c); src["data"]["next"] = targets
    d["semantics"]["transitions"] = [t for t in d["semantics"]["transitions"] if t["from"] != src["id"]] + [
        {"from": src["id"], "to": t, "when": f"intent == case_{i}", "outcome": "normal"} for i, t in enumerate(targets)]
    return d

@variant("13_no_presentation_1_1")
def _(d):
    d.pop("presentation", None); d.pop("milestones", None)
    return d

@variant("14_huge_brief")
def _(d):
    d["brief"] = d["brief"] + (" More context. " * 4000)
    return d

@variant("15_empty_strings")
def _(d):
    for it in items(d, "tasks")[:2]:
        it["title"] = ""; it["description"] = ""; it["data"]["examples"] = []
    d["presentation"]["systemSentence"] = ""
    return d

results = []
for name, fn in VARIANTS.items():
    d = fn(copy.deepcopy(base))
    vd = OUT / name; shutil.rmtree(vd, ignore_errors=True); vd.mkdir()
    (vd / "design.json").write_text(json.dumps(d, ensure_ascii=False))
    (vd / "review.json").write_text(review)
    rc_v, out_v = run(["python3", "-I", str(SK / "scripts/design_io.py"), "validate", str(vd / "design.json")])
    rc_h, out_h = run(["python3", "-I", str(SK / "scripts/design_html.py"), str(vd / "design.json"), "--review", str(vd / "review.json"), "--out", str(vd / "DESIGN.html")])
    html = (vd / "DESIGN.html").read_text() if (vd / "DESIGN.html").exists() else ""
    notes = []
    if name.startswith("01") and html:
        notes.append("RAW_SCRIPT_TAG" if "<script>alert(1)" in html else "escaped")
        notes.append("RAW_ONERROR" if "onerror=alert" in html.replace("&quot;", '"') and "<img src=x onerror" in html else "img-escaped")
    if html:
        notes.append(f"html {len(html)//1024}KB")
        notes.append("has_ellipsis" if "..." in html.split("<script")[0] else "no_ellipsis")
    err_v = [l for l in out_v.splitlines() if any(k in l for k in ('"code"', "SEM0", "error", "Error", "refus"))][:3]
    err_h = [l for l in out_h.splitlines() if l.strip()][-2:] if rc_h else []
    results.append((name, rc_v, rc_h, notes, err_v, err_h))

for r in results:
    print(f"{r[0]:<24} validate rc={r[1]} html rc={r[2]} {r[3]}")
    for l in r[4]: print("    V:", l.strip()[:160])
    for l in r[5]: print("    H:", l.strip()[:160])
