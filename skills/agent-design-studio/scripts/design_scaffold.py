#!/usr/bin/env python3
"""Draft the `semantics` block for a validated tasks and components stage.

SEM000 is where weaker and smaller-context models lose rounds: the semantic
contract has to cover every node, every component and every transition
exactly, and getting that shape right by hand is bookkeeping, not design. This
script does the bookkeeping and leaves the design decisions blank.

    python3 design_scaffold.py design.json                 # JSON to stdout
    python3 design_scaffold.py design.json --out scaffold.json
    python3 design_scaffold.py design.json --merge          # write into design.json

What it fills from the design: one `nodes` row per workflow node with a kind
guessed from its component group, one `componentEffects` row per component,
one `transitions` row per declared `data.next` edge with `when` copied from
the contract, one `modelOutputs` row per LLM output field, and the field names
every write binding needs, taken from the component's declared inputs.

What it never invents: a transition's `outcome`, a model output's `category`,
a binding's `source`, a write's `actionClass`, a human wait's `waitHours`, or
any golden. Those are judgements about the business, and a guess there is
worse than a blank. Every blank is the string "TODO" or null, and a scaffold
with a blank left in it fails validation, so an unfinished contract cannot
reach a reader.

Standard library only.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

TODO = "TODO"

# A component group suggests what its node does. The author confirms it: a
# "Code: tools" component may read or write, and only the design says which.
GROUP_KIND = {
    "Agents (LLM)": "other",
    "Code: validation": "validation",
    "Code: human triggers": "human_wait",
    "Code: tools": TODO,
}
GROUP_EFFECT = {
    "Agents (LLM)": "none",
    "Code: validation": "none",
    "Code: human triggers": "none",
    "Code: tools": TODO,
}
KINDS = ("start", "validation", "approval", "write", "human_wait", "requester_notice",
         "reconcile", "record_id_guard", "completion", "other")
CATEGORIES = ("money", "date", "identity", "other")
OUTCOMES = ("normal", "TIMEOUT", "unknown_commit", "repeat", "notice")
SOURCES = ("llm", "trusted", "literal")


def field_name(declaration):
    """'amount: C4.plan.amount, required' -> 'amount'."""
    return str(declaration).split(":", 1)[0].rstrip("!").strip()


def contract_of(node):
    try:
        value = json.loads(node["description"])
    except (TypeError, ValueError):
        return {}
    return value if isinstance(value, dict) else {}


def scaffold(design):
    """The semantics skeleton for this design, plus the checklist to finish it."""
    workflow = design["stages"]["workflow"]["items"]
    components = {c["id"]: c for c in design["stages"]["components"]["items"]}
    by_id = {w["id"]: w for w in workflow}

    incoming = {w["id"]: 0 for w in workflow}
    for node in workflow:
        for nxt in node["data"]["next"]:
            if nxt in incoming:
                incoming[nxt] += 1
    entrypoints = [i for i in incoming if incoming[i] == 0]

    nodes, todo = [], []
    for node in workflow:
        component = components.get(node["data"]["componentId"], {})
        group = component.get("data", {}).get("group", "")
        kind = "start" if node["id"] in entrypoints and len(workflow) > 1 else GROUP_KIND.get(group, TODO)
        row = {"id": node["id"], "kind": kind}
        if kind == TODO:
            todo.append(f"{node['id']}: choose a kind from {', '.join(KINDS)}; "
                        f"its component {component.get('id', '?')} is a tool, which may read or write.")
        if kind == "human_wait":
            row["waitHours"] = None
            todo.append(f"{node['id']}: set waitHours, and add a requester-notice branch if it is over one hour.")
        nodes.append(row)

    effects = []
    for cid, component in components.items():
        effect = GROUP_EFFECT.get(component["data"]["group"], TODO)
        effects.append({"componentId": cid, "effect": effect})
        if effect == TODO:
            todo.append(f"{cid}: declare its effect as read, write or none.")

    transitions = []
    for node in workflow:
        declared = {t.get("to"): t for t in contract_of(node).get("transitions", []) if isinstance(t, dict)}
        for nxt in node["data"]["next"]:
            if nxt not in by_id:
                continue
            when = str(declared.get(nxt, {}).get("when", TODO))
            transitions.append({"from": node["id"], "to": nxt, "when": when, "outcome": TODO})
            if when == TODO:
                todo.append(f"{node['id']} -> {nxt}: the contract states no condition; copy the exact predicate.")
    if transitions:
        todo.append(f"Set an outcome for each of the {len(transitions)} transitions, from "
                    f"{', '.join(OUTCOMES)}.")

    model_outputs = []
    for cid, component in components.items():
        if component["data"]["group"] != "Agents (LLM)":
            continue
        for declaration in component["data"]["outputs"]:
            model_outputs.append({"componentId": cid, "field": field_name(declaration), "category": TODO})
    if model_outputs:
        todo.append(f"Categorise each of the {len(model_outputs)} model outputs as "
                    f"{', '.join(CATEGORIES)}. A money, date or identity output may not reach a write.")

    # Write bindings: the field names come from the component's declared
    # inputs, which is bookkeeping. Where each value comes from is not.
    for row in nodes:
        component = components.get(by_id[row["id"]]["data"]["componentId"], {})
        if not component:
            continue
        if GROUP_EFFECT.get(component["data"]["group"]) == TODO or row["kind"] == TODO:
            row["bindings"] = [
                {"field": field_name(d), "category": TODO, "source": TODO}
                for d in component["data"]["inputs"]
            ]
            if row["bindings"]:
                todo.append(f"{row['id']}: if this node writes, give every binding a category "
                            f"({', '.join(CATEGORIES)}) and a source ({', '.join(SOURCES)}); "
                            f"money, dates and identity are never sourced from the model.")
            row["actionClass"] = TODO
            todo.append(f"{row['id']}: if this node writes, name its actionClass and list it in writeActions.")

    todo.append("Add goldens: a positive and a negative case for every write action class, or, for a "
                "read-only design, a cited answer and a refusal when the corpus is silent.")

    return {
        "semantics": {
            "version": "1.1",
            "entrypoints": entrypoints,
            "nodes": nodes,
            "transitions": transitions,
            "componentEffects": effects,
            "modelOutputs": model_outputs,
            "writeActions": [],
            "goldens": [],
        },
        "todo": todo,
        "filled": {
            "nodes": len(nodes),
            "transitions": len(transitions),
            "componentEffects": len(effects),
            "modelOutputs": len(model_outputs),
        },
        "note": ("Every TODO and null is a decision about the business that this script will not guess. "
                 "A scaffold with one left in it fails validation, so an unfinished contract cannot be "
                 "delivered as a finished one."),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("design", help="Path to a design.json with tasks and components filled in.")
    parser.add_argument("--out", help="Write the scaffold here instead of stdout.")
    parser.add_argument("--merge", action="store_true",
                        help="Write the semantics block into the design file. Refuses to overwrite an existing one.")
    args = parser.parse_args(argv)
    try:
        design = json.loads(Path(args.design).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 1
    for stage in ("workflow", "components"):
        if not design.get("stages", {}).get(stage, {}).get("items"):
            print(json.dumps({"ok": False, "error": f"Fill the {stage} stage before scaffolding semantics."}),
                  file=sys.stderr)
            return 1
    result = scaffold(design)
    result["ok"] = True
    if args.merge:
        if design.get("semantics"):
            print(json.dumps({"ok": False, "error": "This design already has a semantics block; "
                                                    "scaffolding would discard the author's work."}), file=sys.stderr)
            return 1
        design["semantics"] = result["semantics"]
        Path(args.design).write_text(json.dumps(design, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        result["merged"] = args.design
    if args.out:
        Path(args.out).write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        result["written"] = args.out
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
