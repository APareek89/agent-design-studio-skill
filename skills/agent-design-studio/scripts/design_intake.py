#!/usr/bin/env python3
"""Find key information a brief leaves out and shape at most four questions.

Standard library only. The host assistant shows the questions once through its
own question dialog (Claude Code: AskUserQuestion; Codex: request_user_input;
other hosts: a single chat message with numbered options). Every question is
optional: a skipped question becomes a labelled assumption, and a host that
cannot ask proceeds without asking. This script never asks anything itself.

    python3 design_intake.py questions brief.txt          # JSON question set
    python3 design_intake.py questions - < brief.txt
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

ASSUME = "Not sure; propose an assumption with an owner"

# Topics in priority order. `present` is a regex that marks the topic as already
# covered by the brief; `question` is what the host asks when it is not.
TOPICS = (
    {
        "id": "autonomy",
        "topic": "Which actions may run without a person",
        "present": r"\b(approv\w*|human|supervisor|reviewer|staff (?:must|review|decide)|sign[- ]?off|autonom\w*|automatic\w*|without (?:a )?human|read[- ]only|never (?:send|pay|change))\b",
        "question": "Which actions may the system complete on its own, and which need a person to approve?",
        "why": "Autonomy decides where code checks, approvals and human queues go; guessing it wrong changes most of the design.",
        "options": [
            "Read and explain only; a person does every action",
            "Low-risk actions alone (tickets, replies); money, identity and policy changes need approval",
            "Most actions alone within stated limits; a person handles exceptions",
        ],
    },
    {
        "id": "systems",
        "topic": "Systems of record and their interfaces",
        "present": r"\b(crm|erp|billing system|database|api|apis|system of record|ticketing|salesforce|sap|servicenow|zendesk|workday|records?|ledger|data warehouse|spreadsheet)\b",
        "question": "Which systems hold the facts the assistant needs, and do they have an API the assistant may call?",
        "why": "Every read and write in the design binds to a real system; without it the stack step can only name placeholders.",
        "options": [
            "Named systems with usable APIs",
            "Named systems but no API yet (exports, screens or files)",
            "Not decided; the design should propose the adapters",
        ],
    },
    {
        "id": "volume",
        "topic": "Expected volume",
        "present": r"\b\d[\d,.]*\s*(?:k|thousand|million|m)?\s*(?:cases|claims|requests|complaints|reports|tickets|conversations|calls|messages|orders|applications|documents|users|customers)\b.{0,30}\b(?:per|a|each|/)\s*(?:day|week|month|year|hour)\b|\b(?:per|a)\s*(?:day|week|month)\b.{0,20}\d",
        "question": "Roughly how many cases per month should the first release handle?",
        "why": "Volume sets the model budget, the human-queue size and whether an automatic path is worth building.",
        "options": ["Under 1,000 a month", "1,000 to 10,000 a month", "10,000 to 100,000 a month", "Over 100,000 a month"],
    },
    {
        "id": "constraints",
        "topic": "Regulation, privacy and data limits",
        "present": r"\b(gdpr|hipaa|pci|dpdp|ccpa|sox|regulat\w*|complian\w*|privacy|pii|personal data|data residen\w*|retention|audit\w*|consent|legal)\b",
        "question": "Which regulations, privacy rules or data-location limits apply?",
        "why": "They decide what the model may see, where data may live and which records must be kept.",
        "options": [
            "None beyond ordinary data protection",
            "Sector rules apply (finance, health, telecom, public sector)",
            "Strict: regulated data, residency or audit duties",
        ],
    },
    {
        "id": "users",
        "topic": "Who uses it and who owns decisions",
        "present": r"\b(customer\w*|staff|employee\w*|agent\w*|citizen\w*|patient\w*|operator\w*|analyst\w*|clinician\w*|assessor\w*|officer\w*|team|users?|clients?|members?)\b",
        "question": "Who uses the system day to day, and which role owns the final decision?",
        "why": "Actors shape the task map, the handoff queue and who signs off on risk.",
        "options": ["Internal staff only", "Customers or the public, with staff behind them", "Both, in different steps"],
    },
    {
        "id": "channels",
        "topic": "Channels",
        "present": r"\b(chat|email|voice|phone|call\w*|whatsapp|sms|web|app|api|portal|slack|teams|in[- ]person|counter|letter)\b",
        "question": "Through which channels do requests arrive, and where should replies go?",
        "why": "Voice needs speech tools and latency budgets; messaging channels have template and consent rules.",
        "options": ["Text channels only (chat, email, web form)", "Voice calls included", "Documents or files are the main input"],
    },
    {
        "id": "kpis",
        "topic": "Success measures and baselines",
        "present": r"\b(kpi\w*|target\w*|reduce|increase|improve|%|percent|minutes|hours|days|cost per|turnaround|sla|first[- ]contact|accuracy|baseline)\b",
        "question": "How will success be measured, and is there a current baseline?",
        "why": "Measurable targets make the rollout gates and the experiment real instead of placeholders.",
        "options": ["Time or cost per case", "Quality or error rate", "Customer or user outcome (resolution, satisfaction)", "Not measured today"],
    },
    {
        "id": "domain",
        "topic": "Industry and region",
        "present": r"\b(telecom\w*|bank\w*|insur\w*|health\w*|hospital|clinic|retail\w*|logistic\w*|government|public sector|municipal\w*|city|education|school|universit\w*|energy|utilit\w*|legal|law firm|hr\b|manufactur\w*|airline|hotel|travel|saas|software|e-?commerce|pharma\w*|india|uk|united kingdom|eu\b|europe|us\b|united states|usa|australia|canada|singapore|uae|germany|france)\b",
        "question": "Which industry and country or region is this for?",
        "why": "Industry fixes the vocabulary and typical process; the region fixes the regulator and the data rules.",
        "options": ["Financial services or insurance", "Healthcare", "Telecom or utilities", "Public sector or education", "Other commercial"],
    },
    {
        "id": "platform",
        "topic": "Platform and vendor preferences",
        "present": r"\b(aws|amazon web services|gcp|google cloud|azure|microsoft|on[- ]prem\w*|self[- ]host\w*|openai|anthropic|claude|gemini|mistral|llama|langgraph|temporal|vertex|bedrock|open[- ]source only)\b",
        "question": "Is there a required cloud, model provider or open-source preference?",
        "why": "It narrows the stack cards to options the team can actually run.",
        "options": ["AWS", "Google Cloud", "Azure", "No preference or self-hosted"],
    },
    {
        "id": "languages",
        "topic": "Languages",
        "present": r"\b(language\w*|multilingual|english|hindi|hinglish|spanish|french|german|arabic|portuguese|mandarin|chinese|japanese|tamil|bengali)\b",
        "question": "Which languages must the system handle?",
        "why": "Mixed or non-English input changes the model choice and the evaluation set.",
        "options": ["English only", "Two or three named languages", "Many languages, including mixed-language text"],
    },
)


def analyze(brief, limit=4):
    """Return the gaps in a brief and the questions worth asking, most useful first."""
    text = " ".join(str(brief).split())
    lowered = text.lower()
    detected, gaps = {}, []
    for topic in TOPICS:
        found = re.search(topic["present"], lowered, re.I) is not None
        detected[topic["id"]] = found
        if not found:
            gaps.append(
                {
                    "id": "Q" + str(len(gaps) + 1),
                    "topic": topic["id"],
                    "title": topic["topic"],
                    "question": topic["question"],
                    "why": topic["why"],
                    "options": list(topic["options"]) + [ASSUME],
                }
            )
    return {
        "briefWords": len(text.split()),
        "detected": detected,
        "gaps": gaps,
        "ask": gaps[:limit],
        "complete": not gaps,
        "note": (
            "Ask the first questions once, through the host's question dialog, with the options shown plus the host's free-text choice. "
            "Every question is optional: a skipped question becomes a labelled assumption with an owner. A host that cannot ask proceeds without asking and records that in design.json intake."
        ),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    questions = sub.add_parser("questions", help="List missing key information and the questions to ask, as JSON.")
    questions.add_argument("brief", help="Path to the brief text, or - for stdin.")
    questions.add_argument("--max", type=int, default=4, help="Most questions to ask at once (default 4).")
    args = parser.parse_args(argv)
    try:
        text = sys.stdin.read() if args.brief == "-" else Path(args.brief).read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 1
    if not text.strip():
        print(json.dumps({"ok": False, "error": "The brief is empty; ask only for the brief."}), file=sys.stderr)
        return 1
    result = analyze(text, max(0, args.max))
    result["ok"] = True
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
