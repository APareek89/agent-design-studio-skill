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


def _report_schemas():
    text = {"type": "string", "minLength": 1}
    ids = {"type": "array", "items": text}
    call = {"type": "object", "required": ["choice", "rejected", "why"], "properties": {key: text for key in ("choice", "rejected", "why")}, "additionalProperties": False}
    autonomy = {"type": "object", "required": ["action", "level"], "properties": {"action": text, "level": {"enum": ["acts alone", "suggests", "human decides"]}, "note": text}, "additionalProperties": False}
    presentation = {"type": "object", "required": ["systemSentence", "designCalls", "autonomy"], "properties": {
        "systemSentence": text, "designCalls": {"type": "array", "minItems": 3, "maxItems": 5, "items": call},
        "autonomy": {"type": "array", "minItems": 1, "items": autonomy}, "scopeSummary": text,
        "taskLabels": {"type": "object", "additionalProperties": text},
        "workflowLabels": {"type": "object", "additionalProperties": text}}, "additionalProperties": False}
    milestone = {"type": "object", "required": ["id", "title", "taskIds", "componentIds", "evalIds", "acceptanceCriteria"], "properties": {
        "id": text, "title": text, "taskIds": ids, "componentIds": ids, "evalIds": ids, "workflowIds": ids,
        "acceptanceCriteria": {"type": "array", "minItems": 1, "items": text}}, "additionalProperties": False}
    return {"presentation": presentation,
            "runOptions": {"type": "object", "required": ["mode", "interactive"], "properties": {"mode": {"enum": ["lite", "standard", "full"]}, "interactive": {"type": "boolean"}}, "additionalProperties": False},
            "milestones": {"type": "array", "minItems": 1, "items": milestone}}


def _research_schema():
    text = {"type": "string", "minLength": 1}
    finding = {
        "type": "object",
        "required": ["id", "topic", "url", "title", "retrievedAt", "summary", "usedBy"],
        "properties": {
            "id": {"type": "string", "pattern": r"^RS[1-9]\d*$"},
            "topic": {"type": "string", "minLength": 1, "maxLength": 120},
            "url": {"type": "string", "pattern": r"^https?://\S+$", "maxLength": 2000},
            "title": {"type": "string", "minLength": 1, "maxLength": 300},
            "retrievedAt": {"type": "string", "pattern": r"^\d{4}-\d{2}-\d{2}$"},
            "summary": {"type": "string", "minLength": 1, "maxLength": 1200},
            "usedBy": {"type": "array", "items": text, "maxItems": 60},
        },
        "additionalProperties": False,
    }
    return {
        "type": "object",
        "required": ["performed", "tool", "unavailableReason", "queries", "findings"],
        "properties": {
            "performed": {"type": "boolean"},
            "tool": {"type": "string", "maxLength": 200},
            "unavailableReason": {"type": "string", "maxLength": 600},
            "queries": {"type": "array", "items": {"type": "string", "minLength": 1, "maxLength": 300}, "maxItems": 60},
            "findings": {"type": "array", "items": finding, "maxItems": 60},
        },
        "additionalProperties": False,
    }


def _intake_schema():
    question = {
        "type": "object",
        "required": ["id", "topic", "question", "answer", "source"],
        "properties": {
            "id": {"type": "string", "pattern": r"^Q[1-9]\d*$"},
            "topic": {"type": "string", "minLength": 1, "maxLength": 80},
            "question": {"type": "string", "minLength": 1, "maxLength": 400},
            "answer": {"type": "string", "maxLength": 2000},
            "source": {"enum": ["user", "skipped", "unavailable"]},
        },
        "additionalProperties": False,
    }
    # What `design_intake.py classify` read from the brief before the questions
    # were shaped. Heuristic: the host confirms it and may override it, and both
    # the profile and the override are kept.
    conflict = {
        "type": "object",
        "required": ["id", "rule", "briefAsks", "designKeeps"],
        "properties": {
            "id": {"type": "string", "minLength": 1, "maxLength": 20},
            "rule": {"type": "string", "minLength": 1, "maxLength": 120},
            "briefAsks": {"type": "string", "minLength": 1, "maxLength": 400},
            "designKeeps": {"type": "string", "minLength": 1, "maxLength": 400},
            "message": {"type": "string", "maxLength": 800},
        },
        "additionalProperties": False,
    }
    profile = {
        "type": "object",
        "required": ["language", "words", "length", "isAgentSystem", "writes", "realtime", "multiTenant"],
        "properties": {
            "language": {
                "type": "object",
                "required": ["code", "name"],
                "properties": {
                    "code": {"type": "string", "minLength": 2, "maxLength": 8},
                    "name": {"type": "string", "minLength": 1, "maxLength": 40},
                    "script": {"type": "string", "maxLength": 40},
                    "confidence": {"enum": ["high", "medium", "low"]},
                    "evidence": {"type": "string", "maxLength": 300},
                },
                "additionalProperties": False,
            },
            "words": {"type": "integer", "minimum": 0},
            "length": {"enum": ["empty", "thin", "ok", "long"]},
            "isAgentSystem": {"type": "boolean"},
            "notAgentHints": {"type": "array", "items": {"type": "string", "maxLength": 80}, "maxItems": 10},
            "writes": {"type": "boolean"},
            "realtime": {"type": "boolean"},
            "multiTenant": {"type": "boolean"},
            "briefConflicts": {"type": "array", "items": conflict, "maxItems": 10},
            "signals": {
                "type": "array",
                "maxItems": 12,
                "items": {
                    "type": "object",
                    "required": ["id", "title", "detail"],
                    "properties": {
                        "id": {"type": "string", "minLength": 1, "maxLength": 40},
                        "title": {"type": "string", "minLength": 1, "maxLength": 80},
                        "detail": {"type": "string", "minLength": 1, "maxLength": 1200},
                    },
                    "additionalProperties": False,
                },
            },
            "messages": {"type": "array", "items": {"type": "string", "maxLength": 1200}, "maxItems": 12},
            "suggestedMode": {"enum": ["lite", "standard", "full"]},
            "gapCheckLanguage": {"type": "string", "maxLength": 40},
            "shapeSignalsReliable": {"type": "boolean"},
            "confirmed": {"type": "boolean"},
            "overriddenBy": {"type": "string", "maxLength": 400},
            "note": {"type": "string", "maxLength": 600},
        },
        "additionalProperties": False,
    }
    return {
        "type": "object",
        "required": ["asked", "tool", "questions"],
        "properties": {
            "asked": {"type": "boolean"},
            "tool": {"type": "string", "maxLength": 120},
            "questions": {"type": "array", "items": question, "maxItems": 12},
            "briefProfile": profile,
        },
        "additionalProperties": False,
    }


# ---------------------------------------------------------------------------
# Brief profiles. `intake.briefProfile` says what kind of system the brief
# describes; three kinds change what the design must contain. A design with no
# profile keeps the v1.2 rules exactly.
# ---------------------------------------------------------------------------

# A read-only assistant cannot go wrong in the ways a writing one can, so the
# write risk families are replaced rather than added to. Each entry is a family
# name and the words that show a risk card covers it.
READ_ONLY_RISK_FAMILIES = (
    ("wrong or stale source", r"stale|out[- ]of[- ]date|outdated|superseded|wrong (?:source|document|version)|old version"),
    ("missing citation", r"missing citation|uncited|no citation|without a citation|unattributed"),
    ("answer outside the corpus", r"outside the corpus|out of scope|not in the (?:corpus|documents)|beyond the corpus|unsupported claim|hallucinat"),
    ("prompt injection through documents", r"prompt injection|injected instruction|instruction in a document|poisoned document|indirect injection"),
    ("leaking content the user may not see", r"leak\w*|not permitted to see|unauthorised (?:content|access)|unauthorized (?:content|access)|permission\w* (?:breach|leak)|access control"),
    ("confident answer when the corpus is silent", r"corpus is silent|no evidence|nothing found|silent corpus|confident(?:ly)? (?:answer|wrong)|over[- ]confiden|abstain|decline"),
)
READ_ONLY_AUTONOMY = ("answers with citation", "answers with caveat", "declines")
# A voice system's own failure surface.
REALTIME_REQUIRED_CAPABILITIES = ("speech", "voice")


def brief_profile(design):
    """The recorded brief profile, or an empty dict when the design has none."""
    intake = design.get("intake")
    if not isinstance(intake, dict):
        return {}
    profile = intake.get("briefProfile")
    return profile if isinstance(profile, dict) else {}


def profile_says(design, key, default=None):
    """One profile field, honouring a host override recorded alongside it."""
    profile = brief_profile(design)
    return profile.get(key, default) if profile else default


def is_read_only(design):
    profile = brief_profile(design)
    return bool(profile) and profile.get("writes") is False


def is_realtime(design):
    return bool(profile_says(design, "realtime", False))


def is_multi_tenant(design):
    return bool(profile_says(design, "multiTenant", False))


def _risk_text(design):
    return " ".join(
        item["title"] + " " + item["description"] + " " + item["data"].get("control", "")
        + " " + item["data"].get("action", "")
        for item in design["stages"]["fmea"]["items"]
    ).lower()


def read_only_risk_gaps(design):
    """Read-only risk families with no card covering them."""
    text = _risk_text(design)
    return [name for name, pattern in READ_ONLY_RISK_FAMILIES if not re.search(pattern, text)]


CONTEXT_EXPECTATIONS = (
    ("COV1", "Business decision and boundary", r"decision|boundar|goal|purpose|objective|problem"),
    ("COV2", "Actors and decision owners", r"actor|owner|people|role|user|customer|staff|who |stakeholder"),
    ("COV3", "Trigger, first-release scope and non-goals", r"scope|trigger|non-goal|first release|exclu|out of scope|boundar"),
    ("COV4", "Success measures or end conditions", r"kpi|success|measure|metric|outcome|end condition|value"),
    ("COV5", "Constraints, regulation and privacy", r"constraint|regulat|compliance|privacy|retention|residen|limit|law|policy|consent"),
    ("COV6", "Evidence limits and unknowns", r"evidence|assumption|unknown|unverified|limit|hypothes"),
)
CAPABILITY_HINTS = (
    ("voice and telephony", r"\b(voice|phone|telephon\w*|ivr|call cent(?:re|er)|phone calls?)\b", r"voice|telephon|speech|call"),
    ("guardrails and PII detection", r"\b(pii|personal data|sensitive data|redact\w*|gdpr|hipaa|dpdp|pci)\b", r"guardrail|pii|redact|privacy|sensitive"),
    ("web search", r"\b(web search|search the web|internet|latest (?:news|information)|online sources)\b", r"web search|search api|internet"),
    ("retrieval and embeddings", r"\b(knowledge base|policy wording|manuals?|faq|documentation|retriev\w*|rag)\b", r"retriev|embedding|vector|knowledge base|rag"),
    ("knowledge graph", r"\b(knowledge graph|graph database|ontology)\b", r"graph"),
    ("document AI and OCR", r"\b(pdfs?|scans?|scanned|ocr|handwrit\w*|uploaded documents?|attachments?)\b", r"document|ocr|extraction"),
    ("messaging channels", r"\b(whatsapp|sms|e-?mail|slack|microsoft teams|push notification)\b", r"channel|messag|whatsapp|sms|e-?mail|notification"),
)
WRITE_HINTS = r"\b(refunds?|credits?|payments?|pay|payout\w*|invoices?|transfers?|disburs\w*|approve claims?|settle\w*|reimburs\w*)\b"


def coverage_report(design):
    """Does the design cover the information a reader expects? Gaps are findings, not structural errors.

    A gap can be justified by any assumption string that starts with its ID, e.g.
    "COV9: the host offered no web search tool". Required gaps fail
    `validate --strict-coverage`; recommended gaps are advice.
    """
    checks = []
    justified = {}
    texts = [h["statement"] for h in design.get("assumptions", [])]
    for key in STAGES:
        packet = design["stages"][key]
        texts += list(packet.get("assumptions", []))
        for item in packet.get("items", []):
            texts += list(item.get("assumptions", []))
    for text in texts:
        match = re.match(r"^\s*(COV\d+)\s*:\s*(.+)$", str(text), re.S)
        if match:
            justified[match.group(1).upper()] = match.group(2).strip()

    def add(cid, title, covered, evidence, required=True):
        if covered:
            status = "covered"
        elif cid in justified:
            status, evidence = "justified", justified[cid]
        else:
            status = "missing"
        checks.append({"id": cid, "title": title, "status": status, "required": required, "evidence": evidence})

    context_text = " ".join(
        item["title"] + " " + item["data"].get("field", "") + " " + item["data"].get("value", "")
        for item in design["stages"]["context"]["items"]
    ).lower()
    for cid, title, pattern in CONTEXT_EXPECTATIONS:
        hit = re.search(pattern, context_text)
        add(cid, title, bool(hit), ("Context mentions '" + hit.group(0).strip() + "'.") if hit else "No context card covers this; add one or justify.")
    pres = design.get("presentation") if isinstance(design.get("presentation"), dict) else None
    add("COV7", "Reader layer (system sentence, design calls, autonomy, scope summary)",
        bool(pres) and bool(pres.get("systemSentence")) and len(pres.get("designCalls", [])) >= 3 and bool(pres.get("autonomy")) and bool(pres.get("scopeSummary")),
        "presentation present with scope summary." if pres and pres.get("scopeSummary") else "Add presentation with systemSentence, 3-5 designCalls, autonomy and scopeSummary.")
    mode = (design.get("runOptions") or {}).get("mode", "standard") if isinstance(design.get("runOptions"), dict) else "standard"
    if mode == "lite":
        checks.append({"id": "COV8", "title": "Build milestones", "status": "n/a", "required": False, "evidence": "Lite mode has no build files."})
    else:
        add("COV8", "Build milestones", bool(design.get("milestones")), f"{len(design.get('milestones') or [])} milestones." if design.get("milestones") else "Add milestones so the handoff is split into bounded build files.")
    research = design.get("research") if isinstance(design.get("research"), dict) else None
    add("COV9", "Web research record (performed, or why not)", research is not None,
        (f"{len(research['findings'])} findings via {research['tool']}." if research and research["performed"] else "Not performed: " + research["unavailableReason"]) if research else "No research record; run the research pass or record why it was not possible.")
    brief = str(design.get("brief", "")).lower()
    frameworks = design["stages"]["framework"]["items"]
    missing_caps, found_caps = [], []
    for name, hint, card_pattern in CAPABILITY_HINTS:
        if not re.search(hint, brief):
            continue
        matched = any(
            re.search(card_pattern, (f["data"].get("capability", "") + " " + (f["title"] if f["data"].get("category") == "tooling" else "")).lower())
            for f in frameworks
        )
        (found_caps if matched else missing_caps).append(name)
    if found_caps or missing_caps:
        add("COV10", "Tooling card for each capability the brief implies", not missing_caps,
            ("Covered: " + ", ".join(found_caps) + ". " if found_caps else "") + ("Missing tooling card for: " + ", ".join(missing_caps) + "." if missing_caps else ""))
    else:
        checks.append({"id": "COV10", "title": "Tooling card for each capability the brief implies", "status": "n/a", "required": False, "evidence": "The brief names no capability beyond the model."})
    read_only = is_read_only(design)
    if read_only:
        checks.append({"id": "COV11", "title": "Human trigger for money or record writes the brief implies", "status": "n/a", "required": False, "evidence": "Read-only system: the design writes to no system of record, so there is nothing for a human trigger to gate."})
    elif re.search(WRITE_HINTS, brief):
        human = [c["id"] for c in design["stages"]["components"]["items"] if c["data"]["group"] == "Code: human triggers"]
        add("COV11", "Human trigger for money or record writes the brief implies", bool(human), ("Human triggers: " + ", ".join(human) + ".") if human else "The brief implies money or record writes but no component is a human trigger.")
    else:
        checks.append({"id": "COV11", "title": "Human trigger for money or record writes the brief implies", "status": "n/a", "required": False, "evidence": "The brief implies no money or record write."})
    volume_pool = " ".join([brief] + [h["statement"] for h in design["assumptions"]] + [c["data"].get("value", "") for c in design["stages"]["context"]["items"]])
    add("COV12", "Volume stated (cases per period)", bool(re.search(r"\d[\d,]*\s*(?:k|thousand|million)?\s*\w*\s*(?:/|per|a|each|every)\s*(?:day|week|month|year|hour)", volume_pool, re.I)), "A volume per period is stated." if re.search(r"(?:/|per|a|each|every)\s*(?:day|week|month|year|hour)", volume_pool, re.I) else "State an illustrative volume as an assumption; it drives cost and queue sizing.", required=False)
    kpis = [r for r in design["stages"]["rollout"]["items"] if r["data"]["category"] == "kpi"]
    weak = [r["id"] for r in kpis if not re.search(r"baseline|→|->|from .{1,30} to |unknown|collect", r["data"]["businessKpi"] + " " + r["data"]["gate"], re.I)]
    add("COV13", "Each KPI states a baseline and target, or says the baseline is unknown and how it is collected", not weak, ("All KPI cards state baseline handling." if kpis else "No KPI card.") if not weak else "KPI cards without baseline or collection plan: " + ", ".join(weak) + ".", required=False)
    leaves = [t for t in design["stages"]["tasks"]["items"] if t["kind"] == "task" and t["data"]["mode"] == "leaf"]
    thin = [t["id"] for t in leaves if len(t["data"]["examples"]) < 2]
    add("COV14", "Every leaf task has at least two concrete examples", not thin, "All leaves carry two or more examples." if not thin else "Leaves with fewer than two examples: " + ", ".join(thin) + ".", required=False)
    tooling = [f for f in frameworks if f["data"].get("category") == "tooling"]
    unchecked = [f["id"] for f in tooling if not any(c.get("verified") for c in f["data"].get("candidates", []))]
    if tooling:
        add("COV15", "Each tooling card has at least one candidate checked against a cited source", not unchecked, "All tooling cards cite a checked candidate." if not unchecked else "Tooling cards with no checked candidate: " + ", ".join(unchecked) + ".", required=False)
    else:
        checks.append({"id": "COV15", "title": "Each tooling card has at least one candidate checked against a cited source", "status": "n/a", "required": False, "evidence": "No tooling card."})
    if read_only:
        goldens = [e for e in design["stages"]["evals"]["items"] if e["data"]["category"] == "golden"]
        cited = [e["id"] for e in goldens if re.search(r"citation|cite[sd]?|source", e["data"]["expected"] + " " + e["data"]["passRule"], re.I)]
        declines = [e["id"] for e in goldens if re.search(r"declin|refus|abstain|cannot answer|no answer", e["data"]["expected"] + " " + e["data"]["passRule"] + " " + e["title"], re.I)]
        access = " ".join(
            [c["title"] + " " + c["description"] for c in design["stages"]["components"]["items"]]
            + [f["title"] + " " + f["data"].get("choice", "") for f in design["stages"]["framework"]["items"]]
            + [h["statement"] for h in design["assumptions"]]
        )
        has_access = bool(re.search(r"access (?:check|control)|permission\w* check|document[- ]level|entitlement|who may (?:see|read)", access, re.I))
        missing = []
        if not cited:
            missing.append("a golden that requires a verifiable citation")
        if not declines:
            missing.append("a golden that requires a refusal when the corpus is silent")
        if not has_access:
            missing.append("a statement of who may see which documents")
        add("COV16", "Read-only system: citation goldens and a document access statement", not missing,
            ("Citation goldens: " + ", ".join(cited + declines) + "; access control stated.") if not missing
            else "A read-only assistant needs " + ", ".join(missing) + ".")
        gaps = read_only_risk_gaps(design)
        add("COV17", "Read-only risk families in the register", not gaps,
            "All read-only risk families are covered." if not gaps
            else "No risk card covers: " + ", ".join(gaps) + ".")
    required = [c for c in checks if c["required"]]
    return {
        "required": len(required),
        "coveredRequired": sum(1 for c in required if c["status"] in ("covered", "justified")),
        "missingRequired": [c["id"] for c in required if c["status"] == "missing"],
        "justified": [c["id"] for c in checks if c["status"] == "justified"],
        "missingRecommended": [c["id"] for c in checks if not c["required"] and c["status"] == "missing"],
        "checks": checks,
        "note": "Coverage checks look for expected information by field and keyword; they do not judge its quality. Justify a gap with an assumption string that starts with its ID.",
    }


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
            "research": _research_schema(),
            "intake": _intake_schema(),
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
    top_schema["properties"].update(_report_schemas())
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
    intake = design.get("intake")
    intake_answers = set()
    if isinstance(intake, dict):
        if intake["asked"] and not _nonempty(intake["tool"]):
            _issue(errors, "$.intake.tool", "Name the question dialog that was used (for example AskUserQuestion).")
        for i, q in enumerate(intake["questions"]):
            if q["source"] == "user":
                if not _nonempty(q["answer"]):
                    _issue(errors, f"$.intake.questions[{i}].answer", "A user-sourced answer must carry the user's words.")
                else:
                    intake_answers.add(q["answer"])
        # A brief that asks the design to drop a control the skill keeps must be
        # answered in the open, not quietly redesigned around.
        profile = intake.get("briefProfile")
        if isinstance(profile, dict):
            conflicts = profile.get("briefConflicts") or []
            if conflicts:
                scope_text = " ".join(
                    c["title"] + " " + c["data"].get("field", "") + " " + c["data"].get("value", "")
                    for c in design["stages"]["context"]["items"]
                    if re.search(r"trigger|scope", c["title"] + " " + c["data"].get("field", ""), re.I)
                ).lower()
                pres = design.get("presentation") if isinstance(design.get("presentation"), dict) else {}
                brief_text = " ".join(
                    [str(pres.get("systemSentence", "")), str(pres.get("scopeSummary", ""))]
                    + [str(c.get("choice", "")) + " " + str(c.get("because", "")) for c in pres.get("designCalls", [])]
                ).lower()
                for i, conflict in enumerate(conflicts):
                    cid = conflict.get("id", str(i))
                    if "override" not in scope_text:
                        _issue(errors, "$.stages.context",
                               "The brief conflicts with a rule the design keeps (" + cid + ": " + conflict["rule"]
                               + "). The context card 'Trigger and first-release scope' must say what the brief asks, "
                                 "what the design keeps instead and that an override needs a named owner.")
                        break
                if pres and "override" not in brief_text:
                    _issue(errors, "$.presentation",
                           "The brief conflicts with a rule the design keeps; the Decision brief must say what the "
                           "brief asks, what the design keeps instead and that an override needs a named owner.")
    research = design.get("research")
    findings = {}
    if isinstance(research, dict):
        for i, f in enumerate(research["findings"]):
            fp = f"$.research.findings[{i}]"
            if f["id"] in findings:
                _issue(errors, fp + ".id", "Duplicate research finding ID " + f["id"] + ".")
            findings[f["id"]] = f
            for field in ("topic", "title", "summary"):
                if not _nonempty(f[field]):
                    _issue(errors, fp + "." + field, "Research finding needs real " + field + " text.")
        if research["performed"]:
            if not _nonempty(research["tool"]):
                _issue(errors, "$.research.tool", "Name the web search or fetch tool that was used.")
        else:
            if research["findings"]:
                _issue(errors, "$.research.findings", "A research record marked not performed cannot carry findings.")
            if not _nonempty(research["unavailableReason"]):
                _issue(errors, "$.research.unavailableReason", "State why no web research was performed.")
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
                    if source["file"] == "user-intake":
                        if source["passage"] not in intake_answers:
                            _issue(errors, sp, "Intake source must quote an exact user answer recorded in $.intake.questions with source user.")
                    elif (
                        source["file"] != "user-brief"
                        or not _nonempty(source["passage"])
                        or source["passage"] not in design["brief"]
                    ):
                        _issue(
                            errors,
                            sp,
                            "Context source must name user-brief (or user-intake) and quote an exact nonempty passage.",
                        )
                elif source["type"] == "hypothesis":
                    h = ledger.get(source["file"])
                    if h is None or source["passage"] != h["statement"]:
                        _issue(
                            errors,
                            sp,
                            "Hypothesis source must name an existing H ID and its exact statement.",
                        )
                elif source["type"] == "research":
                    f = findings.get(source["file"])
                    if f is None or source["passage"] != f["summary"]:
                        _issue(
                            errors,
                            sp,
                            "Research source must name an existing RS ID in $.research.findings and its exact summary.",
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
            candidates = d.get("candidates", [])
            if d["category"] == "tooling":
                if not _nonempty(d.get("capability", "")):
                    _issue(errors, p + ".data.capability", "A tooling card names the capability it serves.")
                if not candidates:
                    _issue(errors, p + ".data.candidates", "A tooling card lists at least one candidate with its verification status.")
            for j, cand in enumerate(candidates):
                cp = f"{p}.data.candidates[{j}]"
                if cand["verified"] and not cand["sourceIds"]:
                    _issue(errors, cp + ".verified", "A verified candidate cites at least one research finding; otherwise mark it unverified.")
                for rs in cand["sourceIds"]:
                    if rs not in findings:
                        _issue(errors, cp + ".sourceIds", "Candidate cites a missing research finding " + rs + ".")
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
    for i, f in enumerate(findings.values()):
        for j, used in enumerate(f["usedBy"]):
            if used not in global_ids and used not in ledger:
                _issue(errors, f"$.research.findings[{i}].usedBy[{j}]", "Research finding cites a missing item or assumption ID " + used + ".")
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
    errors.extend(_profile_errors(design))
    warnings.extend(_profile_warnings(design))
    coverage = None
    if not errors:
        coverage = coverage_report(design)
        for check in coverage["checks"]:
            if check["required"] and check["status"] == "missing":
                warnings.append({"path": "$.coverage." + check["id"], "message": check["title"] + ": " + check["evidence"]})
    return {
        "semanticCoverage": semantic_coverage,
        "valid": not errors,
        "status": "structural-pass" if not errors else "structural-errors",
        "errors": errors,
        "warnings": warnings,
        "counts": {k: len(packets[k]["items"]) for k in STAGES},
        "coverage": coverage,
        "limitations": LIMITATIONS,
    }



def _speaking_nodes(design):
    """Nodes that say something to a person, so a caller can talk over them."""
    speaking = []
    for node in design["stages"]["workflow"]["items"]:
        text = node["title"] + " " + node["description"] + " " + node["data"].get("example", "")
        if re.search(r"\b(speak\w*|say[s]?|says|prompt\w*|read[s]? (?:out|back)|play\w*|announce\w*|greet\w*|"
                     r"tts|text[- ]to[- ]speech|utterance|voice reply|spoken)\b", text, re.I):
            speaking.append(node)
    return speaking


def _profile_errors(design):
    """Rules that only apply to a design whose brief profile asks for them."""
    errors = []
    if is_realtime(design):
        nodes = design["stages"]["workflow"]["items"]
        by_id = {n["id"]: n for n in nodes}
        # Where the system speaks, the design must say what happens when the
        # user talks over it. Silence here is a design gap, not a detail.
        for node in _speaking_nodes(design):
            targets = [by_id.get(t) for t in node["data"]["next"]]
            transitions = []
            try:
                transitions = parse_json(node["description"]).get("transitions", [])
            except (ValueError, TypeError):
                transitions = []
            barge_in = any(
                re.search(r"barge[sd]?[- ]?in\b|interrupt\w*|user speaks|caller speaks|talks over|cuts in",
                          str(t.get("when", "")) + " " + str((by_id.get(t.get("to")) or {}).get("title", "")), re.I)
                for t in transitions if isinstance(t, dict)
            ) or any(
                target is not None and re.search(r"barge[sd]?[- ]?in\b|interrupt", target["title"], re.I)
                for target in targets
            )
            if not barge_in:
                _issue(errors, "$.stages.workflow." + node["id"],
                       "Real-time system: " + node["id"] + " speaks to the user, so it needs a barge-in branch "
                       "saying what is cancelled and what is kept when the user talks over it.")
        # A transcript the speech component is unsure of must not reach a write
        # without someone confirming it.
        confidence = [
            c for c in design["stages"]["components"]["items"]
            if re.search(r"confidence|score", " ".join(c["data"].get("outputs", [])), re.I)
            and re.search(r"speech|transcri\w*|stt|asr|voice", c["title"] + " " + c["description"], re.I)
        ]
        speech = [
            c for c in design["stages"]["components"]["items"]
            if re.search(r"speech|transcri\w*|\bstt\b|\basr\b|text[- ]to[- ]speech|\btts\b|telephon\w*",
                         c["title"] + " " + c["description"], re.I)
        ]
        if speech and not confidence:
            _issue(errors, "$.stages.components",
                   "Real-time system: a speech component must output a confidence value, so a low-confidence "
                   "transcript can be routed to a confirm step before any write.")
    return errors


def _profile_warnings(design):
    """Profile findings a reader must see but that do not make the design invalid."""
    warnings = []
    if is_realtime(design):
        target = _latency_target(design)
        budgets = [
            n["data"].get("latencyBudgetMs") for n in design["stages"]["workflow"]["items"]
            if isinstance(n["data"].get("latencyBudgetMs"), int)
        ]
        if target is not None and budgets:
            worst = _first_reply_latency(design)
            if worst is not None and worst > target:
                warnings.append({
                    "path": "$.stages.workflow",
                    "message": ("Real-time system: the slowest path from entry to the first reply budgets %d ms, "
                                "over the brief's stated %d ms." % (worst, target)),
                })
        elif target is not None and not budgets:
            warnings.append({
                "path": "$.stages.workflow",
                "message": ("Real-time system: the brief states a %d ms target but no node carries a "
                            "latencyBudgetMs, so the path cannot be checked." % target),
            })
    if is_multi_tenant(design):
        grid = " ".join(c["data"].get("field", "") for c in design["stages"]["context"]["items"]).lower()
        if "tenant" not in grid:
            warnings.append({
                "path": "$.stages.context",
                "message": "Multi-tenant system: no context card names the tenant; the key attributes grid "
                           "shows the tenant column first and needs it.",
            })
    return warnings


def _latency_target(design):
    """The reply-latency target the brief states, in milliseconds."""
    brief = str(design.get("brief", ""))
    match = re.search(r"(\d[\d,.]*)\s*(ms|milliseconds?)\b", brief, re.I)
    if match:
        return int(float(match.group(1).replace(",", "")))
    match = re.search(r"(?:under|below|within|less than|at most|<=?)\s*(\d[\d,.]*)\s*(seconds?|secs?|s)\b",
                      brief, re.I)
    if match:
        return int(float(match.group(1).replace(",", "")) * 1000)
    return None


def _first_reply_latency(design):
    """The slowest budgeted path from an entry node to the first node that speaks."""
    nodes = {n["id"]: n for n in design["stages"]["workflow"]["items"]}
    if not nodes:
        return None
    incoming = {i: 0 for i in nodes}
    for node in nodes.values():
        for nxt in node["data"]["next"]:
            if nxt in incoming:
                incoming[nxt] += 1
    entries = [i for i in nodes if incoming[i] == 0] or list(nodes)[:1]
    speaks = {n["id"] for n in _speaking_nodes(design)}
    if not speaks:
        return None

    def budget(i):
        value = nodes[i]["data"].get("latencyBudgetMs")
        return value if isinstance(value, int) else 0

    worst, stack = None, [(e, budget(e), {e}) for e in entries]
    while stack:
        node, total, seen = stack.pop()
        if node in speaks:
            worst = total if worst is None else max(worst, total)
            continue
        for nxt in nodes[node]["data"]["next"]:
            if nxt in nodes and nxt not in seen:
                stack.append((nxt, total + budget(nxt), seen | {nxt}))
    return worst


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
    # A review the author ran on their own work is not an independent one, and
    # must never read as one anywhere in the record.
    if re.search(r"\bself\b|self[- ]review", review["method"], re.I):
        where = []
        if re.search(r"independent", review["method"], re.I):
            where.append("$.review.method")
        for i, limitation in enumerate(review.get("limitations", [])):
            if re.search(r"independent", str(limitation), re.I):
                where.append(f"$.review.limitations[{i}]")
        for i, issue in enumerate(review.get("issues", [])):
            text = " ".join(str(v) for v in issue.values() if isinstance(v, str))
            if re.search(r"independent", text, re.I):
                where.append(f"$.review.issues[{i}]")
        for path in where:
            _issue(errors, path,
                   "This is a self-review, so it cannot describe itself as independent. "
                   "Say what was actually done, or have a separate agent review it.")
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
        + "## Coding-agent handoff\n\nTreat unresolved issues and launch dependencies as blockers. Do not infer authority,acceptance or completed execution from this design. Preserve record proof,source boundaries and the defined deterministic controls.\n\nDESIGN.html is delivered with DESIGN.pdf in every mode; it is a read-only view of this design, not an approval tool.\n\n"
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
    intake = design.get("intake")
    if isinstance(intake, dict):
        assumptions += "\n## What the user added\n\n"
        if intake["asked"]:
            assumptions += f"Asked once through {intake['tool']}. Skipped questions became assumptions above.\n\n"
        else:
            assumptions += "No intake question was asked" + (": " + intake["tool"] if intake["tool"] else "") + ".\n\n"
        for q in intake["questions"]:
            assumptions += f"- {q['id']} {q['question']} — " + (q["answer"] if q["source"] == "user" else q["source"]) + "\n"
    research = design.get("research")
    if isinstance(research, dict):
        assumptions += "\n## Research used\n\n"
        if research["performed"]:
            assumptions += f"Web research with {research['tool']}; {len(research['queries'])} queries. Findings are the author's summaries of public pages; they do not verify this organisation's policies, contracts or systems.\n\n"
            for f in research["findings"]:
                assumptions += f"- {f['id']} ({f['topic']}, retrieved {f['retrievedAt']}): {f['title']} <{f['url']}> — {f['summary']} Used by: {', '.join(f['usedBy']) or 'none'}\n"
        else:
            assumptions += "No web research was performed: " + research["unavailableReason"] + " Tool candidates are unverified.\n"
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


def export_design(design_path, out, review_path, mode=None, html=True):
    if mode is not None:
        import importlib.util
        spec = importlib.util.spec_from_file_location("studio_export_v2", Path(__file__).with_name("export_v2.py"))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.export_mode(type("ExportNamespace", (), globals()), design_path, out, review_path, mode, html)
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
    val.add_argument(
        "--strict-coverage",
        action="store_true",
        help="Exit 1 when a required expected-information check is missing and not justified.",
    )
    cov = sub.add_parser(
        "coverage",
        help="Report whether the design covers the information a reader expects; exit 1 on unjustified required gaps.",
    )
    cov.add_argument("design")
    exp = sub.add_parser(
        "export",
        help="Validate design and supplied review,then render design-only documents.",
    )
    exp.add_argument("design")
    exp.add_argument("--out", required=True)
    exp.add_argument("--review", required=True)
    exp.add_argument("--mode", choices=("lite", "standard", "full"), default="standard")
    exp.add_argument(
        "--no-html",
        action="store_true",
        help="Skip DESIGN.html for hosts that cannot write it; the PDF and companions are unchanged.",
    )
    args = parser.parse_args(argv)
    try:
        if args.command == "validate":
            result = validate_design(load_json(args.design))
            code = 0 if result["valid"] else 1
            if args.strict_coverage and result["valid"] and result["coverage"]["missingRequired"]:
                result["status"] = "coverage-gaps"
                code = 1
        elif args.command == "coverage":
            design = load_json(args.design)
            structural = validate_design(design)
            if not structural["valid"]:
                result = {"ok": False, "status": "structural-errors", "errors": structural["errors"]}
                code = 1
            else:
                result = dict(structural["coverage"], ok=not structural["coverage"]["missingRequired"])
                code = 0 if result["ok"] else 1
        else:
            result = export_design(args.design, args.out, args.review, args.mode, not args.no_html)
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
