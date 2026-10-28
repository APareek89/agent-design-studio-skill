#!/usr/bin/env python3
"""Validate and export design artifacts using Python's standard library only.

This is deliberately a small JSON Schema interpreter, NOT a general draft2020-12
implementation. Supported assertion keywords: type, required, properties,
additionalProperties (boolean or supported schema), items, min/maxItems,
min/maxLength, minimum/maximum, const, enum, pattern, anyOf. Boolean schemas and
union type lists are supported. Annotation keywords are ignored explicitly.
Every other schema keyword is rejected, including $ref/format/oneOf, so bundled
schema evolution cannot silently weaken validation. Structural and ID-based
coverage checks do not execute fixtures, verify policy truth, prove authority,
judge evidence quality, or certify implementation/production safety.
"""

from __future__ import annotations
import argparse
import copy
import csv
import hashlib
import html
import io
import json
import math
import os
from pathlib import Path
import re
import sys
import tempfile

STAGES = (
    "context",
    "tasks",
    "components",
    "workflow",
    "framework",
    "models",
    "fmea",
    "evals",
    "rollout",
    "export",
)
SCHEMA_PATH = Path(__file__).resolve().parents[1] / "references" / "stage-schemas.json"
GENERATOR = "agent-design-studio.design_io/1.0"
OUTPUT_FILES = (
    "PRD.md",
    "architecture.md",
    "build-prompt.md",
    "eval-set.json",
    "fmea-register.csv",
    "assumptions.md",
    "validation.json",
)
LIMITATIONS = [
    "Design-only tooling: this helper makes no provider, network or business API calls and executes no business assertions; optional host-assistant research is outside this statement.",
    "Schema, reference, graph and ID-coverage checks do not establish semantic completeness, source truth, actual human authorization or production safety.",
    "Review scores and evidence are supplied by the reviewing agent; the helper checks their shape and declared pass conditions, not their truth.",
    "FMEA action/control text is required where specified; the helper does not verify ownership, release authority, regulatory compliance or risk acceptance.",
]
ANNOTATIONS = {
    "$schema",
    "$id",
    "$comment",
    "title",
    "description",
    "default",
    "examples",
    "deprecated",
    "readOnly",
    "writeOnly",
}
ASSERTIONS = {
    "type",
    "required",
    "properties",
    "additionalProperties",
    "items",
    "minItems",
    "maxItems",
    "minLength",
    "maxLength",
    "minimum",
    "maximum",
    "const",
    "enum",
    "pattern",
    "anyOf",
}
TYPES = {"object", "array", "string", "integer", "number", "boolean", "null"}


def _issue(errors, path, message):
    errors.append({"path": path, "message": message})


def _nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def _json_equal(a, b):
    if isinstance(a, bool) or isinstance(b, bool):
        return type(a) is type(b) and a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return a == b
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(_json_equal(a[k], b[k]) for k in a)
    if isinstance(a, list):
        return len(a) == len(b) and all(_json_equal(x, y) for x, y in zip(a, b))
    return a == b


def _type_ok(value, name):
    if name == "object":
        return isinstance(value, dict)
    if name == "array":
        return isinstance(value, list)
    if name == "string":
        return isinstance(value, str)
    if name == "boolean":
        return isinstance(value, bool)
    if name == "null":
        return value is None
    if name == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if name == "number":
        return (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            and (isinstance(value, int) or math.isfinite(value))
        )
    return False


def audit_schema(schema, path="$schema", errors=None):
    """Reject unsupported keywords and malformed schema definitions recursively."""
    errors = [] if errors is None else errors
    if isinstance(schema, bool):
        return errors
    if not isinstance(schema, dict):
        _issue(errors, path, "Schema must be an object or boolean.")
        return errors
    for key in schema:
        if key not in ASSERTIONS | ANNOTATIONS:
            _issue(
                errors,
                path + "." + key,
                "Unsupported schema keyword; validation refuses a silent gap.",
            )
    typ = schema.get("type")
    if typ is not None:
        ts = typ if isinstance(typ, list) else [typ]
        if not ts or any(not isinstance(t, str) or t not in TYPES for t in ts):
            _issue(errors, path + ".type", "Unsupported JSON type declaration.")
    for key in ("minItems", "maxItems", "minLength", "maxLength"):
        if key in schema and (type(schema[key]) is not int or schema[key] < 0):
            _issue(
                errors, path + "." + key, "Schema bound must be a nonnegative integer."
            )
    for key in ("minimum", "maximum"):
        if key in schema and not _type_ok(schema[key], "number"):
            _issue(errors, path + "." + key, "Schema bound must be a finite number.")
    if "pattern" in schema:
        try:
            re.compile(schema["pattern"])
        except (TypeError, re.error):
            _issue(errors, path + ".pattern", "Invalid schema regex.")
    if "required" in schema and (
        not isinstance(schema["required"], list)
        or any(not isinstance(k, str) for k in schema["required"])
    ):
        _issue(
            errors, path + ".required", "required must be an array of property names."
        )
    if "enum" in schema and (
        not isinstance(schema["enum"], list) or not schema["enum"]
    ):
        _issue(errors, path + ".enum", "enum must be a nonempty array.")
    if "properties" in schema:
        if not isinstance(schema["properties"], dict):
            _issue(errors, path + ".properties", "properties must be an object.")
        else:
            for key, child in schema["properties"].items():
                audit_schema(child, path + ".properties." + key, errors)
    for key in ("items", "additionalProperties"):
        if key in schema:
            audit_schema(schema[key], path + "." + key, errors)
    if "anyOf" in schema:
        if not isinstance(schema["anyOf"], list) or not schema["anyOf"]:
            _issue(errors, path + ".anyOf", "anyOf must be a nonempty array.")
        else:
            for i, child in enumerate(schema["anyOf"]):
                audit_schema(child, f"{path}.anyOf[{i}]", errors)
    return errors


def check_schema(value, schema, path="$", errors=None):
    """Validate an already-audited schema. Returns precise actionable paths."""
    errors = [] if errors is None else errors
    if schema is True:
        return errors
    if schema is False:
        _issue(errors, path, "Value is forbidden by schema.")
        return errors
    if "anyOf" in schema:
        candidates = [check_schema(value, branch, path) for branch in schema["anyOf"]]
        if not any(not candidate for candidate in candidates):
            _issue(errors, path, "Does not match any allowed schema variant.")
            errors.extend(min(candidates, key=len))
    if "type" in schema:
        ts = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        if not any(_type_ok(value, t) for t in ts):
            _issue(errors, path, "Expected " + "|".join(ts) + ".")
            return errors
    if "const" in schema and not _json_equal(value, schema["const"]):
        _issue(errors, path, "Must equal const " + repr(schema["const"]) + ".")
    if "enum" in schema and not any(_json_equal(value, z) for z in schema["enum"]):
        _issue(errors, path, "Value is not in the allowed enum.")
    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                _issue(errors, path + "." + key, "Required field is missing.")
        props = schema.get("properties", {})
        for key, child in value.items():
            if key in props:
                check_schema(child, props[key], path + "." + key, errors)
            elif schema.get("additionalProperties", True) is False:
                _issue(errors, path + "." + key, "Unexpected field is not allowed.")
            elif isinstance(schema.get("additionalProperties"), dict):
                check_schema(
                    child, schema["additionalProperties"], path + "." + key, errors
                )
    if isinstance(value, list):
        for key, op, msg in [
            ("minItems", lambda x, y: x < y, "Too few items"),
            ("maxItems", lambda x, y: x > y, "Too many items"),
        ]:
            if key in schema and op(len(value), schema[key]):
                _issue(errors, path, f"{msg}; {key}={schema[key]}.")
        if "items" in schema:
            for i, child in enumerate(value):
                check_schema(child, schema["items"], f"{path}[{i}]", errors)
    if isinstance(value, str):
        if "minLength" in schema and len(value) < schema["minLength"]:
            _issue(errors, path, f"String shorter than {schema['minLength']}.")
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            _issue(errors, path, f"String longer than {schema['maxLength']}.")
        if "pattern" in schema and re.search(schema["pattern"], value) is None:
            _issue(errors, path, "String does not match required pattern.")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if isinstance(value, float) and not math.isfinite(value):
            _issue(errors, path, "Nonfinite numbers are not valid JSON numbers.")
        if "minimum" in schema and value < schema["minimum"]:
            _issue(errors, path, f"Number is below {schema['minimum']}.")
        if "maximum" in schema and value > schema["maximum"]:
            _issue(errors, path, f"Number is above {schema['maximum']}.")
    return errors


def _pairs(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError("Duplicate JSON key " + repr(key) + ".")
        out[key] = value
    return out


def _constant(value):
    raise ValueError("Nonfinite JSON constant " + value + " is forbidden.")


def parse_json(text):
    return json.loads(text, object_pairs_hook=_pairs, parse_constant=_constant)


def load_json(path):
    try:
        return parse_json(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        raise ValueError(f"{path}: {exc}") from exc


def _object_json(text, path, errors):
    try:
        value = parse_json(text)
    except (TypeError, ValueError) as exc:
        _issue(errors, path, "Expected a JSON object string: " + str(exc))
        return None
    if not isinstance(value, dict) or not value:
        _issue(errors, path, "Expected a nonempty JSON object.")
        return None
    return value


def _finite_walk(value, path, errors):
    if isinstance(value, float) and not math.isfinite(value):
        _issue(errors, path, "Nonfinite number is forbidden.")
    elif isinstance(value, dict):
        for k, v in value.items():
            _finite_walk(v, path + "." + str(k), errors)
    elif isinstance(value, list):
        for i, v in enumerate(value):
            _finite_walk(v, f"{path}[{i}]", errors)


def validate_design(design, schemas=None):
    errors, warnings = [], []
    schemas = load_json(SCHEMA_PATH) if schemas is None else schemas
    if not isinstance(schemas, dict) or set(schemas) != set(STAGES):
        return {
            "valid": False,
            "status": "structural-errors",
            "errors": [
                {
                    "path": "$schema",
                    "message": "Bundled stage schemas must contain exactly the ten canonical stages.",
                }
            ],
            "warnings": [],
            "limitations": LIMITATIONS,
        }
    for key in STAGES:
        audit_schema(schemas[key], "$schema." + key, errors)
    if errors:
        return {
            "valid": False,
            "status": "structural-errors",
            "errors": errors,
            "warnings": warnings,
            "limitations": LIMITATIONS,
        }
    ledger_schema = {
        "type": "array",
        "items": {
            "type": "object",
            "required": [
                "id",
                "statement",
                "why",
                "owner",
                "validation",
                "launchBlocker",
            ],
            "properties": {
                "id": {"type": "string", "pattern": r"^H[1-9]\d*$"},
                "statement": {"type": "string", "minLength": 1},
                "why": {"type": "string", "minLength": 1},
                "owner": {"type": "string", "minLength": 1},
                "validation": {"type": "string", "minLength": 1},
                "launchBlocker": {"type": "boolean"},
            },
            "additionalProperties": False,
        },
    }
    top_schema = {
        "type": "object",
        "required": ["schemaVersion", "title", "brief", "assumptions", "stages"],
        "properties": {
            "schemaVersion": {"enum": ["1.0", "1.1"]},
            "semantics": {"type": "object"},
            "presentation": {"type": "object"},
            "runOptions": {"type": "object"},
            "milestones": {"type": "array"},
            "title": {"type": "string", "minLength": 1},
            "brief": {"type": "string", "minLength": 1},
            "assumptions": ledger_schema,
            "stages": {
                "type": "object",
                "required": list(STAGES),
                "properties": schemas,
                "additionalProperties": False,
            },
        },
        "additionalProperties": False,
    }
    check_schema(design, top_schema, "$", errors)
    _finite_walk(design, "$", errors)
    if errors:
        return {
            "valid": False,
            "status": "structural-errors",
            "errors": errors,
            "warnings": warnings,
            "limitations": LIMITATIONS,
        }
    for field in ("title", "brief"):
        if not _nonempty(design[field]):
            _issue(errors, "$." + field, "Must contain meaningful non-whitespace text.")
    ledger = {}
    for i, h in enumerate(design["assumptions"]):
        p = f"$.assumptions[{i}]"
        if h["id"] in ledger:
            _issue(errors, p + ".id", "Duplicate hypothesis ID " + h["id"] + ".")
        ledger[h["id"]] = h
        for field in ("statement", "why", "owner", "validation"):
            if not _nonempty(h[field]):
                _issue(errors, p + "." + field, "Must contain meaningful text.")
    packets = design["stages"]
    all_items = []
    by_stage = {}
    global_ids = {}
    for key in STAGES:
        by_stage[key] = {}
        for i, item in enumerate(packets[key]["items"]):
            p = f"$.stages.{key}.items[{i}]"
            ident = item["id"]
            all_items.append((key, p, item))
            if ident in global_ids:
                _issue(
                    errors,
                    p + ".id",
                    "Duplicate item ID "
                    + ident
                    + "; first seen at "
                    + global_ids[ident]
                    + ".",
                )
            global_ids[ident] = p
            by_stage[key][ident] = item
            for field in ("title", "description", "reasoning"):
                if not _nonempty(item[field]):
                    _issue(
                        errors,
                        p + "." + field,
                        "A real design card needs nonempty " + field + ".",
                    )
            for j, source in enumerate(item["sources"]):
                sp = f"{p}.sources[{j}]"
                if source["type"] == "context":
                    if (
                        source["file"] != "user-brief"
                        or not _nonempty(source["passage"])
                        or source["passage"] not in design["brief"]
                    ):
                        _issue(
                            errors,
                            sp,
                            "Context source must name user-brief and quote an exact nonempty passage from brief.",
                        )
                elif source["type"] == "hypothesis":
                    h = ledger.get(source["file"])
                    if h is None or source["passage"] != h["statement"]:
                        _issue(
                            errors,
                            sp,
                            "Hypothesis source must name an existing H ID and its exact statement.",
                        )
                else:
                    _issue(
                        errors,
                        sp,
                        "Unbacked upload sources are not supported by this brief-only contract.",
                    )
    tasks = {k: v for k, v in by_stage["tasks"].items() if v["kind"] == "task"}
    comps = by_stage["components"]
    nodes = by_stage["workflow"]
    failures = by_stage["fmea"]
    evals = by_stage["evals"]
    for key, p, item in all_items:
        d = item["data"]
        for field, target in [
            ("taskIds", tasks),
            ("componentIds", comps),
            ("evalIds", evals),
            ("failureModeIds", failures),
        ]:
            for j, ident in enumerate(d.get(field, [])):
                if ident not in target:
                    _issue(
                        errors,
                        f"{p}.data.{field}[{j}]",
                        "References missing " + field + " ID " + ident + ".",
                    )
        if key in ("components", "workflow") and not d["taskIds"]:
            _issue(
                errors,
                p + ".data.taskIds",
                "Responsibility must serve at least one real task.",
            )
        if key == "context":
            if d["question"]:
                _issue(
                    errors,
                    p + ".data.question",
                    "Resolve unknowns as labelled assumptions/dependencies; question must be empty.",
                )
            if not _nonempty(d["value"]):
                _issue(
                    errors,
                    p + ".data.value",
                    "Context value cannot be an unanswered gate.",
                )
        if key == "components":
            if d["group"] != "Agents (LLM)" and not _nonempty(d["whyCode"]):
                _issue(
                    errors,
                    p + ".data.whyCode",
                    "Deterministic component must explain why code owns this responsibility.",
                )
            for field in ("inputs", "outputs"):
                if not d[field] or any(not _nonempty(z) for z in d[field]):
                    _issue(
                        errors,
                        p + ".data." + field,
                        "Provide actual typed input/output fields.",
                    )
            if not _nonempty(d["approvalRule"]):
                _issue(
                    errors,
                    p + ".data.approvalRule",
                    "State a concrete authorization rule or explicit read-only/no-action boundary.",
                )
        if key == "framework":
            for field in (
                "choice",
                "tradeoffs",
                "blastRadius",
                "approvalRule",
                "leastPrivilege",
            ):
                if not _nonempty(d[field]):
                    _issue(
                        errors,
                        p + ".data." + field,
                        "Architecture card needs an actual " + field + ".",
                    )
            if not d["alternatives"]:
                _issue(
                    errors,
                    p + ".data.alternatives",
                    "Record the rejected alternative and rationale.",
                )
        if key == "fmea":
            for field in (
                "effect",
                "cause",
                "control",
                "detectionMethod",
                "action",
                "metric",
                "kpi",
            ):
                if not _nonempty(d[field]):
                    _issue(
                        errors,
                        p + ".data." + field,
                        "Failure mode needs a concrete " + field + ".",
                    )
            # Scores/owners/acceptedRisk are author/user assertions, never certified by parsing.
        if key == "evals":
            for field in (
                "metric",
                "kpi",
                "target",
                "testSet",
                "labelling",
                "cadence",
                "alertThreshold",
            ):
                if not _nonempty(d[field]):
                    _issue(
                        errors,
                        p + ".data." + field,
                        "Evaluation needs an actual " + field + ".",
                    )
            if d["category"] == "golden":
                for field in ("input", "expected", "passRule"):
                    _object_json(d[field], p + ".data." + field, errors)
        if key == "rollout":
            for field in ("businessKpi", "phase", "gate", "owner"):
                if not _nonempty(d[field]):
                    _issue(
                        errors,
                        p + ".data." + field,
                        "Rollout card needs an actual " + field + ".",
                    )
            if d["category"] == "experiment" and not _nonempty(d["experiment"]):
                _issue(
                    errors,
                    p + ".data.experiment",
                    "Experiment card needs an actual experiment design.",
                )
            if not d["aiMetrics"]:
                _issue(
                    errors,
                    p + ".data.aiMetrics",
                    "Record metric mechanisms or explicit guardrails.",
                )
        if key == "export":
            if not d["acceptanceCriteria"] or any(
                not _nonempty(z) for z in d["acceptanceCriteria"]
            ):
                _issue(
                    errors,
                    p + ".data.acceptanceCriteria",
                    "Provide observable acceptance criteria.",
                )
            if not _nonempty(d["buildInstructions"]):
                _issue(
                    errors,
                    p + ".data.buildInstructions",
                    "Provide a real canonical handoff.",
                )
    roots = [t for t in tasks.values() if not t["data"]["parentId"]]
    if len(roots) != 1:
        _issue(
            errors, "$.stages.tasks", "Task tree needs exactly one overall-job root."
        )
    leaves = [t for t in tasks.values() if t["data"]["mode"] == "leaf"]
    for ident, t in tasks.items():
        p = global_ids[ident]
        parent = t["data"]["parentId"]
        children = [z for z in tasks.values() if z["data"]["parentId"] == ident]
        if parent and parent not in tasks:
            _issue(errors, p + ".data.parentId", "Parent task is missing.")
        if t["data"]["mode"] == "leaf" and children:
            _issue(errors, p, "Leaf task cannot have children.")
        if t["data"]["mode"] != "leaf" and not children:
            _issue(errors, p, "Parent task needs a real child.")
        cursor = ident
        seen = set()
        depth = 0
        while cursor in tasks and tasks[cursor]["data"]["parentId"]:
            if cursor in seen:
                _issue(errors, p, "Task hierarchy contains a cycle.")
                break
            seen.add(cursor)
            cursor = tasks[cursor]["data"]["parentId"]
            depth += 1
            if depth > 2:
                _issue(errors, p, "Task depth exceeds overall job -> task -> subtask.")
                break
    for leaf in leaves:
        if not any(leaf["id"] in c["data"]["taskIds"] for c in comps.values()):
            _issue(
                errors, global_ids[leaf["id"]], "Leaf task has no serving component."
            )
    incoming = set()
    transitions = {}
    for ident, node in nodes.items():
        p = global_ids[ident]
        d = node["data"]
        c = comps.get(d["componentId"])
        if c is None:
            _issue(errors, p + ".data.componentId", "Workflow component is missing.")
        elif not set(d["taskIds"]).issubset(c["data"]["taskIds"]):
            _issue(
                errors,
                p + ".data.taskIds",
                "Workflow claims tasks not served by its component.",
            )
        for target in d["next"]:
            if target not in nodes:
                _issue(
                    errors,
                    p + ".data.next",
                    "Missing workflow successor " + target + ".",
                )
            incoming.add(target)
        contract = _object_json(node["description"], p + ".description", errors)
        if contract is None:
            continue
        for field in ("state", "failureDisposition", "timeout", "retryPolicy"):
            value = contract.get(field)
            if not (_nonempty(value) or isinstance(value, dict) and value):
                _issue(
                    errors,
                    p + ".description." + field,
                    "Workflow contract requires a nonempty " + field + ".",
                )
        if "terminalDisposition" not in contract:
            _issue(
                errors,
                p + ".description.terminalDisposition",
                "Workflow contract requires the terminalDisposition field; nonterminals may use null or an empty string.",
            )
        if not isinstance(contract.get("state"), str):
            _issue(errors, p + ".description.state", "State must be a string.")
        ts = contract.get("transitions")
        if not isinstance(ts, list):
            _issue(
                errors, p + ".description.transitions", "Transitions must be an array."
            )
            continue
        targets = []
        for j, tr in enumerate(ts):
            tp = f"{p}.description.transitions[{j}]"
            if not isinstance(tr, dict):
                _issue(errors, tp, "Transition must be an object.")
                continue
            for field in ("to", "when", "mode"):
                if not _nonempty(tr.get(field)):
                    _issue(
                        errors,
                        tp + "." + field,
                        "Transition needs a nonempty " + field + ".",
                    )
            if isinstance(tr.get("to"), str):
                targets.append(tr["to"])
        if len(set(d["next"])) != len(d["next"]) or set(targets) != set(d["next"]):
            _issue(
                errors,
                p + ".description.transitions",
                "Transition target set must match unique next IDs exactly; multiple predicates may share a successor.",
            )
        if not d["next"] and str(
            contract.get("terminalDisposition", "")
        ).strip().lower() in ("", "none", "null"):
            _issue(
                errors,
                p + ".description.terminalDisposition",
                "Terminal node needs a durable terminal disposition.",
            )
        if len(d["next"]) > 1 and not d["decision"]:
            _issue(
                errors,
                p + ".data.decision",
                "Multiple successors require an explicit decision/fan-out declaration.",
            )
        transitions[ident] = d["next"]
    entry = [ident for ident in nodes if ident not in incoming]
    reachable = set()
    pending = list(entry)
    if nodes and not entry:
        _issue(
            errors,
            "$.stages.workflow",
            "Flow needs at least one entry node outside all cycles.",
        )
    while pending:
        ident = pending.pop()
        if ident in reachable or ident not in nodes:
            continue
        reachable.add(ident)
        pending.extend(nodes[ident]["data"]["next"])
    for ident in nodes:
        if ident not in reachable:
            _issue(
                errors, global_ids[ident], "Workflow node is unreachable from an entry."
            )
    for leaf in leaves:
        if not any(leaf["id"] in nodes[n]["data"]["taskIds"] for n in reachable):
            _issue(
                errors,
                global_ids[leaf["id"]],
                "Leaf task has no reachable workflow path.",
            )
    for ident in comps:
        if not any(n["data"]["componentId"] == ident for n in nodes.values()):
            _issue(
                errors, global_ids[ident], "Inventory component has no workflow node."
            )
    agents = {
        ident for ident, c in comps.items() if c["data"]["group"] == "Agents (LLM)"
    }
    for ident in agents:
        plans = [
            m for m in by_stage["models"].values() if m["data"]["componentId"] == ident
        ]
        if len(plans) != 1:
            _issue(
                errors,
                global_ids[ident],
                "Exactly one active model plan is required per LLM component.",
            )
    for ident, m in by_stage["models"].items():
        if m["data"]["componentId"] not in agents:
            _issue(
                errors,
                global_ids[ident] + ".data.componentId",
                "Model plan must refer to an LLM component,never code or a missing component.",
            )
        for field in ("rationale", "fineTuneWhen"):
            if not _nonempty(m["data"][field]):
                _issue(
                    errors,
                    global_ids[ident] + ".data." + field,
                    "State a concrete " + field + ".",
                )
    golden = [e for e in evals.values() if e["data"]["category"] == "golden"]
    for fid, f in failures.items():
        for eid in f["data"]["evalIds"]:
            if eid in evals and fid not in evals[eid]["data"]["failureModeIds"]:
                _issue(
                    errors,
                    global_ids[fid] + ".data.evalIds",
                    "Link to " + eid + " is not reciprocal.",
                )
        if not f["data"]["acceptedRisk"] and not any(
            fid in e["data"]["failureModeIds"] for e in golden
        ):
            _issue(
                errors,
                global_ids[fid],
                "Unaccepted failure needs an included golden evaluation.",
            )
    for eid, e in evals.items():
        for fid in e["data"]["failureModeIds"]:
            if fid in failures and eid not in failures[fid]["data"]["evalIds"]:
                _issue(
                    errors,
                    global_ids[eid] + ".data.failureModeIds",
                    "Link to "
                    + fid
                    + " is not reciprocal across all evaluation categories.",
                )
    for leaf in leaves:
        if leaf["data"]["risk"] == "high" and not any(
            leaf["id"] in e["data"]["taskIds"] for e in golden
        ):
            _issue(
                errors,
                global_ids[leaf["id"]],
                "High-risk leaf needs an included golden evaluation.",
            )
    for category in ("golden", "offline", "online", "release"):
        if not any(e["data"]["category"] == category for e in evals.values()):
            _issue(
                errors,
                "$.stages.evals",
                "Missing actual " + category + " evaluation layer.",
            )
    for category in ("kpi", "phase", "experiment", "owner"):
        if not any(
            x["data"]["category"] == category for x in by_stage["rollout"].values()
        ):
            _issue(
                errors,
                "$.stages.rollout",
                "Missing actual " + category + " rollout card.",
            )
    semantic_coverage = "unverified"
    if design["schemaVersion"] == "1.1" or "semantics" in design:
        # File-local loading also supports callers importing design_io by path.
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "agent_design_semantic_checks", Path(__file__).with_name("semantic_checks.py")
        )
        semantic_checks = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(semantic_checks)
        semantic_errors = semantic_checks.validate_semantics(design)
        errors.extend(semantic_errors)
        semantic_coverage = "failed" if semantic_errors else "verified-declarations"
    else:
        warnings.append({"path": "$.semantics", "message": "Legacy schema 1.0: semantic coverage unverified; author new designs as schema 1.1 with complete semantic metadata."})
    return {
        "semanticCoverage": semantic_coverage,
        "valid": not errors,
        "status": "structural-pass" if not errors else "structural-errors",
        "errors": errors,
        "warnings": warnings,
        "counts": {k: len(packets[k]["items"]) for k in STAGES},
        "limitations": LIMITATIONS,
    }


def validate_review(review, structural_valid=True):
    errors = []
    schema = {
        "type": "object",
        "required": [
            "method",
            "round",
            "status",
            "dimensions",
            "issues",
            "limitations",
        ],
        "additionalProperties": False,
        "properties": {
            "method": {"enum": ["self-review", "independent-agent"]},
            "round": {"type": "integer", "minimum": 1},
            "status": {"enum": ["pass", "needs-work"]},
            "dimensions": {
                "type": "array",
                "minItems": 12,
                "maxItems": 12,
                "items": {
                    "type": "object",
                    "required": ["id", "score", "evidence"],
                    "additionalProperties": False,
                    "properties": {
                        "id": {"type": "string", "pattern": r"^D(?:[1-9]|1[0-2])$"},
                        "score": {"type": "integer", "minimum": 0, "maximum": 4},
                        "evidence": {
                            "type": "array",
                            "minItems": 1,
                            "items": {"type": "string", "minLength": 1},
                        },
                    },
                },
            },
            "issues": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": [
                        "id",
                        "severity",
                        "stage",
                        "itemId",
                        "message",
                        "resolved",
                    ],
                    "additionalProperties": False,
                    "properties": {
                        "id": {"type": "string", "minLength": 1},
                        "severity": {
                            "enum": [
                                "critical",
                                "major",
                                "minor",
                                "warning",
                                "observation",
                            ]
                        },
                        "stage": {"type": "string", "enum": list(STAGES)},
                        "itemId": {"type": "string"},
                        "message": {"type": "string", "minLength": 1},
                        "resolved": {"type": "boolean"},
                    },
                },
            },
            "limitations": {
                "type": "array",
                "minItems": 1,
                "items": {"type": "string", "minLength": 1},
            },
        },
    }
    check_schema(review, schema, "$.review", errors)
    if errors:
        return {
            "valid": False,
            "status": "needs-work",
            "computedStatus": "needs-work",
            "errors": errors,
            "limitations": LIMITATIONS,
        }
    ids = [d["id"] for d in review["dimensions"]]
    if set(ids) != {"D" + str(i) for i in range(1, 13)} or len(set(ids)) != 12:
        _issue(errors, "$.review.dimensions", "Provide D1 through D12 exactly once.")
    for i, d in enumerate(review["dimensions"]):
        if any(not _nonempty(z) for z in d["evidence"]):
            _issue(
                errors,
                f"$.review.dimensions[{i}].evidence",
                "Every dimension needs real non-whitespace evidence.",
            )
    issue_ids = set()
    for i, q in enumerate(review["issues"]):
        if q["id"] in issue_ids:
            _issue(errors, f"$.review.issues[{i}].id", "Issue IDs must be unique.")
        issue_ids.add(q["id"])
        if not _nonempty(q["message"]):
            _issue(
                errors,
                f"$.review.issues[{i}].message",
                "Issue must state concrete evidence/consequence/fix.",
            )
    if any(not _nonempty(z) for z in review["limitations"]):
        _issue(
            errors,
            "$.review.limitations",
            "Limitations must contain actual non-whitespace text.",
        )
    blockers = [
        q["id"]
        for q in review["issues"]
        if not q["resolved"] and q["severity"] in ("critical", "major")
    ]
    computed = (
        "pass"
        if structural_valid
        and all(d["score"] >= 3 for d in review["dimensions"])
        and not blockers
        and not errors
        else "needs-work"
    )
    if review["status"] == "pass" and computed != "pass":
        _issue(
            errors,
            "$.review.status",
            "Claimed pass is unsupported: structural validity,all D1-D12 >=3,no unresolved critical/major,and limitations are required.",
        )
    status = (
        "needs-work"
        if review["status"] == "needs-work" or computed != "pass"
        else "pass"
    )
    return {
        "valid": not errors,
        "status": status,
        "computedStatus": computed,
        "errors": errors,
        "blockerIds": blockers,
        "method": review["method"],
        "round": review["round"],
        "scores": {d["id"]: d["score"] for d in review["dimensions"]},
        "limitations": LIMITATIONS,
    }


def _dump(value):
    return json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n"


def _fence(text, lang=""):
    runs = [len(x) for x in re.findall(r"`+", text)]
    f = "`" * max(3, max(runs, default=0) + 1)
    return f + lang + "\n" + text.rstrip("\n") + "\n" + f + "\n"


def _value(value):
    if isinstance(value, str):
        return value
    return _dump(value).rstrip()


def _item_md(item):
    parts = [
        f"### {item['id']} · {item['title']}",
        item["description"],
        "Reasoning: " + item["reasoning"],
    ]
    if item["assumptions"]:
        parts += ["Assumptions:"] + ["- " + s for s in item["assumptions"]]
    parts += ["Data:", _fence(_dump(item["data"]), "json"), "Sources:"]
    parts += [
        "- " + s["type"] + " / " + s["file"] + ": " + s["passage"]
        for s in item["sources"]
    ]
    return "\n\n".join(parts) + "\n"


def _stage_md(design, key):
    p = design["stages"][key]
    return (
        "## "
        + key
        + "\n\n"
        + "".join(_item_md(x) + "\n" for x in p["items"])
        + (
            "Stage assumptions:\n\n"
            + "\n".join("- " + z for z in p["assumptions"])
            + "\n"
            if p["assumptions"]
            else ""
        )
    )


def _node_id(stage, ident):
    return stage + "_" + re.sub(r"[^A-Za-z0-9_]", "_", ident)


def _label(text):
    return json.dumps(
        html.escape(str(text).replace("\n", " "), quote=True), ensure_ascii=False
    )


def _graphs(design):
    task_lines = ["flowchart TD"]
    workflow_lines = ["flowchart TD"]
    for t in design["stages"]["tasks"]["items"]:
        if t["kind"] != "task":
            continue
        ident = _node_id("task", t["id"])
        task_lines.append(f"  {ident}[{_label(t['id'] + ': ' + t['title'])}]")
        if t["data"]["parentId"]:
            task_lines.append(
                f"  {_node_id('task', t['data']['parentId'])} --> {ident}"
            )
    for w in design["stages"]["workflow"]["items"]:
        ident = _node_id("flow", w["id"])
        workflow_lines.append(
            f"  {ident}[{_label(w['id'] + ' / ' + w['data']['componentId'] + ': ' + w['title'])}]"
        )
        for tr in parse_json(w["description"])["transitions"]:
            workflow_lines.append(
                f"  {ident} -->|{_label(tr['when'])}| {_node_id('flow', tr['to'])}"
            )
    return "\n".join(task_lines), "\n".join(workflow_lines)


def _csv_safe(value):
    text = (
        value
        if isinstance(value, str)
        else json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    )
    stripped = text.lstrip(" \t\r\n\ufeff")
    if text.startswith(("\t", "\r", "\n")) or stripped.startswith(("=", "+", "-", "@")):
        return "'" + text
    return text


def render_exports(
    design, review, structural, review_result, design_hash="", review_hash=""
):
    status = review_result["status"]
    banner = f"> {status.upper()} · DESIGN ONLY. Review is a design judgement; no business controls or provider reliability were executed.\n"
    overview = (
        "# "
        + design["title"]
        + "\n\n"
        + banner
        + "\nReview method: "
        + review["method"]
        + "; round "
        + str(review["round"])
        + ".\n\n"
    )
    overview += (
        "Review dimensions (supplied scores):\n\n"
        + "\n".join(
            "- " + d["id"] + ": " + str(d["score"]) + "/4 — " + "; ".join(d["evidence"])
            for d in review["dimensions"]
        )
        + "\n\n"
    )
    if review["issues"]:
        overview += (
            "Review findings:\n\n"
            + "\n".join(
                "- "
                + q["id"]
                + " ["
                + q["severity"]
                + ", "
                + ("resolved" if q["resolved"] else "OPEN")
                + "] "
                + q["stage"]
                + "/"
                + q["itemId"]
                + ": "
                + q["message"]
                for q in review["issues"]
            )
            + "\n\n"
        )
    prd = (
        overview
        + "## Original brief\n\n"
        + _fence(design["brief"])
        + "\n"
        + "".join(_stage_md(design, k) + "\n" for k in STAGES)
    )
    tasks, flow = _graphs(design)
    architecture = (
        overview
        + "## Task tree\n\n"
        + _fence(tasks, "mermaid")
        + "\n## Workflow\n\n"
        + _fence(flow, "mermaid")
        + "\n"
        + "".join(
            _stage_md(design, k) + "\n"
            for k in ("tasks", "components", "workflow", "framework", "models")
        )
    )
    build = (
        overview
        + "## Coding-agent handoff\n\nTreat unresolved issues and launch dependencies as blockers. Do not infer authority,acceptance or completed execution from this design. Preserve record proof,source boundaries and the defined deterministic controls.\n\nAfter delivering DESIGN.pdf, ask the user: Would you also like a visual HTML version in the same ten-stage structure as the app? Generate HTML only after opt-in, unless already requested.\n\n"
        + _stage_md(design, "export")
        + "\n## Complete canonical design\n\n"
        + _fence(_dump(design), "json")
    )
    ev = {
        "schemaVersion": "1.0",
        "title": design["title"],
        "designOnly": True,
        "reviewStatus": status,
        "items": copy.deepcopy(design["stages"]["evals"]["items"]),
        "assumptions": design["stages"]["evals"]["assumptions"],
        "limitations": review["limitations"] + LIMITATIONS,
    }
    csv_out = io.StringIO(newline="")
    writer = csv.writer(csv_out)
    fields = [
        "id",
        "title",
        "taskIds",
        "componentIds",
        "effect",
        "cause",
        "severity",
        "occurrence",
        "detection",
        "rpn",
        "control",
        "detectionMethod",
        "action",
        "metric",
        "kpi",
        "evalIds",
        "acceptedRisk",
        "commonToAll",
        "description",
        "reasoning",
        "assumptions",
        "sources",
    ]
    writer.writerow(fields)
    for item in design["stages"]["fmea"]["items"]:
        row = dict(
            item["data"],
            id=item["id"],
            title=item["title"],
            description=item["description"],
            reasoning=item["reasoning"],
            assumptions=item["assumptions"],
            sources=item["sources"],
        )
        row["rpn"] = row["severity"] * row["occurrence"] * row["detection"]
        writer.writerow([_csv_safe(row[k]) for k in fields])
    assumptions = overview + "## Proposed assumption ledger\n\n"
    if not design["assumptions"]:
        assumptions += "No proposed assumptions were recorded. This is not a claim that no unknowns exist.\n\n"
    for h in design["assumptions"]:
        assumptions += f"### {h['id']}\n\n{h['statement']}\n\nWhy: {h['why']}\n\nProposed owner: {h['owner']}\n\nValidation: {h['validation']}\n\nLaunch blocker: {str(h['launchBlocker']).lower()}\n\n"
    for key in STAGES:
        for text in design["stages"][key]["assumptions"]:
            assumptions += "- " + key + ": " + text + "\n"
        for item in design["stages"][key]["items"]:
            for text in item["assumptions"]:
                assumptions += "- " + key + "/" + item["id"] + ": " + text + "\n"
    assumptions += (
        "\n## Review and tooling limitations\n\n"
        + "\n".join("- " + s for s in review["limitations"] + LIMITATIONS)
        + "\n"
    )
    validation = {
        "generator": GENERATOR,
        "generatedFiles": list(OUTPUT_FILES),
        "designOnly": True,
        "status": status,
        "designSha256": design_hash,
        "reviewSha256": review_hash,
        "structuralValidation": structural,
        "reviewValidation": review_result,
        "review": copy.deepcopy(review),
        "limitations": LIMITATIONS,
    }
    return {
        "PRD.md": prd,
        "architecture.md": architecture,
        "build-prompt.md": build,
        "eval-set.json": _dump(ev),
        "fmea-register.csv": csv_out.getvalue(),
        "assumptions.md": assumptions,
        "validation.json": _dump(validation),
    }


def _within(path, directory):
    return path == directory or directory in path.parents


def _preflight_output(out, inputs):
    """Allow input/output co-location; protect files,never replace whole folders.

    Only the seven named targets can change. Existing targets require the prior
    generator manifest; unrelated files,design/review/round history and .work
    are left untouched. Symlink and hardlink aliases of inputs are forbidden.
    """
    if out.is_symlink():
        raise ValueError(f"{out}: output directory may not be a symlink.")
    resolved = out.resolve()
    protected = [p.resolve() for p in inputs]
    if out.exists() and not out.is_dir():
        raise ValueError(f"{out}: output must be a directory.")
    existing_targets = []
    for name in OUTPUT_FILES:
        dest = out / name
        if dest.resolve() in protected:
            raise ValueError(
                f"{dest}: refusing to overwrite an input; choose another output folder or input filename."
            )
        if dest.is_symlink() or dest.exists() and not dest.is_file():
            raise ValueError(f"{dest}: refusing a symlink/directory output target.")
        for inp in inputs:
            if dest.exists() and inp.exists() and os.path.samefile(dest, inp):
                raise ValueError(f"{dest}: output aliases a protected input.")
        if dest.exists():
            existing_targets.append(dest)
    if existing_targets:
        manifest = out / "validation.json"
        if not manifest.is_file():
            raise ValueError(
                f"{out}: existing output target is not a prior generated export; choose a fresh target folder."
            )
        previous = load_json(manifest)
        if (
            not isinstance(previous, dict)
            or previous.get("generator") != GENERATOR
            or previous.get("generatedFiles") != list(OUTPUT_FILES)
        ):
            raise ValueError(
                f"{manifest}: refusing to overwrite output targets without a matching generated-export manifest."
            )
    return resolved


def export_design(design_path, out, review_path, mode=None):
    if mode is not None:
        import importlib.util
        spec = importlib.util.spec_from_file_location("studio_export_v2", Path(__file__).with_name("export_v2.py"))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.export_mode(type("ExportNamespace", (), globals()), design_path, out, review_path, mode)
    design_path = Path(design_path)
    review_path = Path(review_path)
    out = Path(out)
    design = load_json(design_path)
    structural = validate_design(design)
    if not structural["valid"]:
        return {
            "ok": False,
            "status": "structural-errors",
            "errors": structural["errors"],
            "limitations": LIMITATIONS,
        }
    review = load_json(review_path)
    rr = validate_review(review, True)
    if not rr["valid"]:
        return {
            "ok": False,
            "status": "invalid-review",
            "errors": rr["errors"],
            "limitations": LIMITATIONS,
        }
    # The canonical brief is embedded. Protect exact design/review input files;
    # co-location and unrelated round-history/.work files are safe and preserved.
    resolved = _preflight_output(out, [design_path, review_path])
    docs = render_exports(
        design,
        review,
        structural,
        rr,
        hashlib.sha256(design_path.read_bytes()).hexdigest(),
        hashlib.sha256(review_path.read_bytes()).hexdigest(),
    )
    out.mkdir(parents=True, exist_ok=True)
    for name, text in docs.items():
        temp = None
        try:
            with tempfile.NamedTemporaryFile(
                "w",
                encoding="utf-8",
                newline="",
                dir=out,
                prefix=".design-export-",
                delete=False,
            ) as handle:
                temp = Path(handle.name)
                handle.write(text)
            os.replace(temp, out / name)
        finally:
            if temp is not None and temp.exists():
                temp.unlink()
    return {
        "ok": True,
        "status": rr["status"],
        "designOnly": True,
        "outputDirectory": str(resolved),
        "files": [str(resolved / name) for name in OUTPUT_FILES],
        "limitations": LIMITATIONS,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = parser.add_subparsers(dest="command", required=True)
    val = sub.add_parser(
        "validate",
        help="Validate a canonical design; output JSON,exit1 on structural errors.",
    )
    val.add_argument("design")
    exp = sub.add_parser(
        "export",
        help="Validate design and supplied review,then render design-only documents.",
    )
    exp.add_argument("design")
    exp.add_argument("--out", required=True)
    exp.add_argument("--review", required=True)
    exp.add_argument("--mode", choices=("lite", "standard", "full"), default="standard")
    args = parser.parse_args(argv)
    try:
        if args.command == "validate":
            result = validate_design(load_json(args.design))
            code = 0 if result["valid"] else 1
        else:
            result = export_design(args.design, args.out, args.review, args.mode)
            code = 0 if result["ok"] else 1
    except (ValueError, OSError, UnicodeError) as exc:
        result = {
            "ok": False,
            "status": "input-or-output-error",
            "errors": [{"path": "$", "message": str(exc)}],
            "limitations": LIMITATIONS,
        }
        code = 2
    print(_dump(result), end="")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
