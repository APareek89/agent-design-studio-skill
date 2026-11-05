#!/usr/bin/env python3
"""Find key information a brief leaves out and shape at most four questions.

Standard library only. The host assistant shows the questions once through its
own question dialog (Claude Code: AskUserQuestion; Codex: request_user_input;
other hosts: a single chat message with numbered options). Every question is
optional: a skipped question becomes a labelled assumption, and a host that
cannot ask proceeds without asking. This script never asks anything itself.

    python3 design_intake.py classify brief.txt           # JSON briefProfile
    python3 design_intake.py questions brief.txt          # JSON question set
    python3 design_intake.py questions - < brief.txt

`classify` runs before `questions`. It reads the brief's language, length and
shape and writes a `briefProfile` object that the host records under `intake`.
Every signal is a heuristic: the host confirms the profile in one line before
authoring and may override it. The override is recorded alongside the profile.
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



# ---------------------------------------------------------------------------
# Brief classifier (step 1: classify). Heuristics only; the host confirms.
# ---------------------------------------------------------------------------

# Unicode ranges by script. A brief is attributed to a script when that script
# carries most of its letters, so a Hindi brief with English product names is
# still Hindi.
SCRIPT_RANGES = (
    ("Devanagari", 0x0900, 0x097F),
    ("Bengali", 0x0980, 0x09FF),
    ("Gurmukhi", 0x0A00, 0x0A7F),
    ("Gujarati", 0x0A80, 0x0AFF),
    ("Tamil", 0x0B80, 0x0BFF),
    ("Telugu", 0x0C00, 0x0C7F),
    ("Arabic", 0x0600, 0x06FF),
    ("Arabic", 0x0750, 0x077F),
    ("Hebrew", 0x0590, 0x05FF),
    ("Cyrillic", 0x0400, 0x04FF),
    ("Greek", 0x0370, 0x03FF),
    ("Hangul", 0xAC00, 0xD7AF),
    ("Hiragana", 0x3040, 0x309F),
    ("Katakana", 0x30A0, 0x30FF),
    ("CJK", 0x4E00, 0x9FFF),
    ("Thai", 0x0E00, 0x0E7F),
)

# The script alone names the language when only one language uses it widely;
# where a script is shared, the stop-word list below decides.
SCRIPT_LANGUAGE = {
    "Devanagari": ("hi", "Hindi"),
    "Bengali": ("bn", "Bengali"),
    "Gurmukhi": ("pa", "Punjabi"),
    "Gujarati": ("gu", "Gujarati"),
    "Tamil": ("ta", "Tamil"),
    "Telugu": ("te", "Telugu"),
    "Hebrew": ("he", "Hebrew"),
    "Arabic": ("ar", "Arabic"),
    "Cyrillic": ("ru", "Russian"),
    "Greek": ("el", "Greek"),
    "Hangul": ("ko", "Korean"),
    "Hiragana": ("ja", "Japanese"),
    "Katakana": ("ja", "Japanese"),
    "CJK": ("zh", "Chinese"),
    "Thai": ("th", "Thai"),
}

# Scripts more than one language writes in. SCRIPT_LANGUAGE names the most
# common one; a function word of a sibling listed here overrides it.
SHARED_SCRIPTS = {
    "Cyrillic": (("uk", "Ukrainian"),),
}

# Stop words for the ten most common brief languages. Scored as a share of the
# brief's words, so a long brief is not decided by one borrowed article.
STOP_WORDS = {
    ("en", "English"): "the and for with that this are not from have will each our your must should when which",
    ("es", "Spanish"): "el la los las de que y para con una un por en del se no es su como",
    ("fr", "French"): "le la les des de que et pour avec une un par en du se ne est sur dans",
    ("pt", "Portuguese"): "o a os as de que e para com uma um por em do se nao e sobre",
    ("de", "German"): "der die das und fuer mit dass ein eine von im den auf ist nicht sich werden",
    ("it", "Italian"): "il la i le di che e con una un da del si non sul della sono",
    ("nl", "Dutch"): "de het een en van dat voor met zijn niet op te wordt door",
    ("id", "Indonesian"): "yang dan untuk dengan dari pada ini itu adalah akan tidak dalam",
    ("ru", "Russian"): "\u0438 \u0432 \u043d\u0435 \u043d\u0430 \u044f \u0447\u0442\u043e \u0441 \u043a\u0430\u043a \u0434\u043b\u044f \u044d\u0442\u043e \u043f\u043e \u0438\u0437",
    ("uk", "Ukrainian"): "\u0456 \u0432 \u043d\u0435 \u043d\u0430 \u0449\u043e \u0437 \u044f\u043a \u0434\u043b\u044f \u0446\u0435 \u043f\u043e",
}

# Shape signals. Each is a plain regex over the lowered brief.
NOT_AGENT_HINTS = (
    ("one-off script", r"\b(write|build|create|make) (?:me )?(?:a |an )?(?:python |bash |shell |node |small |simple )*(?:script|cron ?job|one[- ]off|macro|utility)\b"),
    ("scraper or batch job", r"\b(scrape[sr]?|scraping|crawl(?:er|ing)?|nightly (?:job|run)|batch (?:job|process)|etl|data pipeline)\b"),
    ("static report or export", r"\b(emails? me (?:a |the )?(?:csv|report|spreadsheet)|generate (?:a |the )?(?:csv|pdf|spreadsheet|report) (?:file|export)|export (?:to )?(?:csv|excel))\b"),
    ("dashboard only", r"\b(dashboard|bi report|power ?bi|tableau|looker|chart(?:s)? (?:of|showing)|visuali[sz]ation only)\b"),
    ("UI or page only", r"\b(landing page|website|web ?page|mobile app screen|design (?:a |the )?(?:ui|screen|layout|mockup|wireframe))\b"),
)
# A decision step is what makes it an agent system rather than a job.
AGENT_HINTS = r"\b(agent|assistant|copilot|decide[sd]?|decision|triage|classif\w+|route[sd]?|routing|judg\w+|approv\w+|resolve[sd]?|handle[sd]?|respond\w*|reason\w*|autonom\w+|workflow|orchestrat\w+|multi[- ]step|conversat\w+|chatbot|answers? questions)\b"

# Verbs that change a system of record. Their absence makes the brief read-only.
# A write verb only counts when its object is a record, not a deliverable:
# "write a Python script" and "create a dashboard" change no system of record.
WRITE_OBJECT_EXCEPTIONS = r"(?:script|code|program|query|report|csv|spreadsheet|dashboard|document|page|email to me|notebook|function|test|readme|file)\b"
WRITE_VERBS = r"\b(post|posts|posting|create[sd]?|creating|update[sd]?|updating|write[sd]?|writing|send[s]?|sending|sent|refund\w*|approv\w+|close[sd]?|closing|cancel\w+|issue[sd]?|pay|pays|paid|payment\w*|credit\w*|debit\w*|transfer\w*|book[s]?|booking|order[s]?|ordering|submit\w*|file[sd]? a|raise[sd]?|escalat\w+|provision\w*|deactivat\w+|activat\w+|delete[sd]?|modif\w+|change[sd]? the|execut\w+|place[sd]? (?:an )?order|trade[sd]?|buy|sell)\b"
READ_ONLY_HINTS = r"\b(read[- ]only|never takes? any action|takes? no action|no actions?|answers? only|only answers|information only|does not (?:write|change|act)|without (?:writing|acting|changing))\b"

REALTIME_HINTS = r"\b(voice|spoken|speech|call(?:s|er|ing)?|phone|telephon\w+|ivr|sip\b|contact cent(?:re|er)|real[- ]?time|realtime|streaming|stream\w*|latency|barge[- ]?in|interrupt\w*|sub[- ]second|milliseconds?|live (?:audio|conversation))\b"
MULTITENANT_HINTS = r"\b(tenant\w*|multi[- ]?tenant\w*|saas\b|white[- ]?label\w*|per[- ]customer data|multiple (?:clients?|customers?|organi[sz]ations?|companies|brands?)|each (?:client|customer|tenant|organi[sz]ation)|our clients[\u2019\']? (?:own )?data|client[- ]specific)\b"

# A conflict is a brief that asks the design to drop a control the skill keeps.
# Each entry: id, what the brief must ask, the rule it collides with.
CONFLICT_RULES = (
    {
        "id": "BC1",
        "rule": "Code owns money",
        "asks": r"\b(autonomous\w*|automatic\w*|without (?:a )?human|no human|no approval|without approval|unattended)\b",
        "subject": r"\b(trade[sd]?|trading|order[s]?|refund\w*|payment\w*|pay|payout\w*|transfer\w*|disburse\w*|invoice\w*|credit\w*|settle\w*|purchase[sd]?|buy|sell|equit\w+|securit\w+|fund[s]?)\b",
        "keeps": "a limit check in code and a human step above the stated limit",
    },
    {
        "id": "BC2",
        "rule": "Code owns identity",
        "asks": r"\b(autonomous\w*|automatic\w*|without (?:a )?human|no human|no approval|without approval|unattended)\b",
        "subject": r"\b(identity|authenticat\w+|kyc|verif\w+ (?:the )?(?:customer|user|caller)|impersonat\w+|account (?:takeover|recovery)|password reset|grant access|permission\w*|entitlement\w*)\b",
        "keeps": "an identity check in code before any action on an account",
    },
    {
        "id": "BC3",
        "rule": "Code owns regulated decisions",
        "asks": r"\b(autonomous\w*|automatic\w*|without (?:a )?human|no human|no approval|without approval|unattended)\b",
        "subject": r"\b(regulat\w+|complian\w+|medical|clinical|diagnos\w+|credit decision|lending|underwrit\w+|legal advice|adjudicat\w+|eligibilit\w+|benefit\w* decision)\b",
        "keeps": "a human decision step on the regulated outcome",
    },
    {
        "id": "BC4",
        "rule": "Approvals cannot be removed",
        "asks": r"\b(no (?:human )?approval\w*|without approval|never ask (?:for )?approval|skip (?:the )?approval|remove (?:the )?approval|no sign[- ]?off|no human (?:in the loop|step|review))\b",
        "subject": r".",
        "keeps": "an approval step for the actions the rules cover",
    },
)

THIN_WORDS = 40
LONG_WORDS = 6000
# A brief has a subject when it names a domain, a user or a system to act on.
SUBJECT_NOUNS = r"\b(customer\w*|client\w*|patient\w*|citizen\w*|student\w*|employee\w*|analyst\w*|agent\w*|staff|user\w*|member\w*|ticket\w*|claim\w*|complaint\w*|invoice\w*|order\w*|case[s]?|report\w*|document\w*|contract\w*|application\w*|account\w*|policy|policies|loan\w*|refund\w*|crm|erp|billing|telecom\w*|bank\w*|insur\w*|health\w*|hospital|retail\w*|logistic\w*|government|school|universit\w*|energy|legal|hr\b|manufactur\w*|airline|hotel|saas|e-?commerce)\b"


def _distinctive_stop_words():
    """Stop words that tell the Latin-script languages apart.

    Short function words are shared: "a" is English and Portuguese, "e" is
    Portuguese and Italian. Scoring on the raw lists makes a 25-word English
    brief read as Portuguese, so drop any word that more than one language
    claims and any word under three letters.
    """
    seen = {}
    for key, stops in STOP_WORDS.items():
        for word in stops.split():
            seen.setdefault(word, []).append(key)
    distinctive = {}
    for key, stops in STOP_WORDS.items():
        distinctive[key] = {w for w in stops.split() if len(w) >= 3 and len(seen[w]) == 1}
    return distinctive


DISTINCTIVE_STOP_WORDS = _distinctive_stop_words()


def _script_counts(text):
    """How many letters of the brief fall in each named script."""
    counts, latin, letters = {}, 0, 0
    for ch in text:
        if not ch.isalpha():
            continue
        letters += 1
        code = ord(ch)
        for name, low, high in SCRIPT_RANGES:
            if low <= code <= high:
                counts[name] = counts.get(name, 0) + 1
                break
        else:
            if code < 0x0250:
                latin += 1
    if latin:
        counts["Latin"] = latin
    return counts, letters


def detect_language(text):
    """Name the brief's language from its script, then its stop words."""
    counts, letters = _script_counts(text)
    if not letters:
        return {"code": "und", "name": "Undetermined", "script": "none", "confidence": "low",
                "evidence": "The brief has no letters."}
    script, hits = max(counts.items(), key=lambda kv: kv[1])
    share = hits / letters
    words = re.findall(r"[^\W\d_]+", text.lower(), re.UNICODE)
    if script != "Latin":
        code, name = SCRIPT_LANGUAGE.get(script, ("und", "Undetermined"))
        # A shared script names its most common language; a function word of a
        # sibling language overrides it.
        for alt_code, alt_name in SHARED_SCRIPTS.get(script, ()):
            stop_set = DISTINCTIVE_STOP_WORDS.get((alt_code, alt_name), set())
            if any(w in stop_set for w in words):
                code, name = alt_code, alt_name
                break
        return {"code": code, "name": name, "script": script,
                "confidence": "high" if share >= 0.5 else "medium",
                "evidence": f"{round(share * 100)}% of letters are {script}."}
    if not words:
        return {"code": "und", "name": "Undetermined", "script": script, "confidence": "low",
                "evidence": "No words to score."}
    scored = []
    for (code, name), stop_set in DISTINCTIVE_STOP_WORDS.items():
        hits = sum(1 for w in words if w in stop_set)
        scored.append((hits / len(words), hits, code, name))
    scored.sort(reverse=True)
    best, runner = scored[0], scored[1]
    if best[1] < 2:
        # Latin script with no recognised function word: a keyword list, a very
        # short line, or a language outside the ten. English is the safe default
        # for the gap check, flagged low so the host can correct it.
        return {"code": "en", "name": "English", "script": script, "confidence": "low",
                "evidence": ("Latin script with too few function words to tell the language apart "
                             f"(best: {best[1]} for {best[3]}); assuming English. Correct it if wrong.")}
    confidence = "high" if best[0] >= 0.05 and best[0] >= runner[0] * 2 else "medium" if best[0] >= 0.015 else "low"
    return {"code": best[2], "name": best[3], "script": script, "confidence": confidence,
            "evidence": f"{best[1]} of {len(words)} words are {best[3]} function words."}


def classify(brief, language_override=None):
    """Read a brief's language, length and shape. Every field is a heuristic."""
    text = " ".join(str(brief).split())
    lowered = text.lower()
    words = len(text.split()) if text else 0
    language = dict(language_override) if language_override else detect_language(text)
    english = language.get("code") == "en"
    signals, messages = [], []

    def signal(sid, title, detail):
        signals.append({"id": sid, "title": title, "detail": detail})
        messages.append(detail)

    # Language.
    if not text:
        signal("language", "Language", "The brief is empty, so there is no language to read.")
    elif english:
        signal("language", "Language",
               f"The brief reads as English ({language['evidence']}). The keyword gap check runs directly on it.")
    else:
        signal("language", "Language",
               f"The brief reads as {language['name']} ({language['evidence']}). "
               f"Every check below matches English keywords, so the gap check and the write, real-time and "
               f"multi-tenant signals are unreliable here: run them again on an English translation you produce, "
               f"or skip them and say so. "
               f"Write the design in {language['name']} unless the user asks for another language.")

    # Length.
    subject = bool(re.search(SUBJECT_NOUNS, lowered))
    thin = words < THIN_WORDS or not subject
    long_brief = words > LONG_WORDS
    if words == 0:
        length = "empty"
        signal("thin", "Too short or vague",
               "The brief is empty. Ask for a brief before anything else; there is nothing here to design from.")
    elif thin:
        length = "thin"
        missing = "it names no domain, user or system to act on" if not subject else f"it is {words} words"
        signal("thin", "Too short or vague",
               f"This brief is too thin for a reliable design ({missing}); the result will rest on N assumptions. "
               "Ask the four intake questions. If the host cannot ask, deliver in lite mode with a visible "
               "'thin brief' banner on the Decision brief.")
    elif long_brief:
        length = "long"
        signal("long", "Too long",
               f"The brief is {words:,} words, over the {LONG_WORDS:,}-word mark. The overview quotes its first 2 KB "
               "and points at design.json for the rest; the HTML collapses it and the full PDF gets a one-page appendix.")
    else:
        length = "ok"

    # Is it an agent system at all?
    not_agent_hits = [name for name, pattern in NOT_AGENT_HINTS if re.search(pattern, lowered)]
    agent_hit = re.search(AGENT_HINTS, lowered)
    is_agent = bool(text) and (bool(agent_hit) or not not_agent_hits)
    if text and not_agent_hits and not agent_hit:
        is_agent = False
        signal("notAgent", "Not an agent system",
               f"This reads as {not_agent_hits[0]} rather than an agent system with a decision step. "
               "Say so in one sentence and offer to continue anyway; if you continue, set runOptions.mode to lite.")

    # Read-only.
    write_hit = None
    for match in re.finditer(WRITE_VERBS, lowered):
        # Look at the verb's object: the next few words up to a clause break.
        tail = lowered[match.end():match.end() + 60].split(",")[0].split(" that ")[0]
        if re.search(r"\b" + WRITE_OBJECT_EXCEPTIONS, tail):
            continue
        write_hit = match
        break
    declared_read_only = re.search(READ_ONLY_HINTS, lowered)
    writes = bool(write_hit) and not declared_read_only
    if text and not writes:
        signal("readOnly", "Read-only system",
               ("The brief says the system takes no action." if declared_read_only
                else "No verb in the brief changes a system of record.")
               + " Treated as read-only: the risk register, goldens, authority table and coverage switch to the "
                 "read-only profile.")

    # Real time and voice.
    realtime_hit = re.search(REALTIME_HINTS, lowered)
    realtime = bool(realtime_hit)
    if realtime:
        signal("realtime", "Real-time or voice",
               f"The brief mentions '{realtime_hit.group(0)}'. Nodes may carry a latency budget and a streaming flag, "
               "a barge-in branch is required from any node that speaks, and speech components come from the tool catalog.")

    # Multi-tenant.
    tenant_hit = re.search(MULTITENANT_HINTS, lowered)
    multi_tenant = bool(tenant_hit)
    if multi_tenant:
        signal("multiTenant", "Multi-tenant",
               f"The brief mentions '{tenant_hit.group(0)}'. Every identity binding needs a trusted tenant field and "
               "a cross-tenant negative golden is required.")

    # Conflicts with the rules the skill keeps.
    conflicts = []
    for rule in CONFLICT_RULES:
        asks = re.search(rule["asks"], lowered)
        subject_hit = re.search(rule["subject"], lowered)
        if not (asks and subject_hit):
            continue
        conflicts.append({
            "id": rule["id"],
            "rule": rule["rule"],
            "briefAsks": f"'{asks.group(0)}' applied to '{subject_hit.group(0)}'",
            "designKeeps": rule["keeps"],
            "message": (f"The brief asks for {asks.group(0)} handling of {subject_hit.group(0)}. "
                        f"This design keeps {rule['keeps']} because the rule '{rule['rule']}' is not negotiable. "
                        "Override needs a named owner."),
        })
    if conflicts:
        signal("conflict", "Conflict with the rules",
               "The brief asks the design to drop a control it keeps. Do not silently redesign: record the conflict "
               "on the Context card 'Trigger and first-release scope' and on the Decision brief. "
               + " ".join(c["message"] for c in conflicts))

    mode = "lite" if (length in ("empty", "thin") or not is_agent) else "standard"
    return {
        "language": language,
        "words": words,
        "length": length,
        "isAgentSystem": is_agent,
        "notAgentHints": not_agent_hits,
        "writes": writes,
        "realtime": realtime,
        "multiTenant": multi_tenant,
        "briefConflicts": conflicts,
        "signals": signals,
        "messages": messages,
        "suggestedMode": mode,
        "gapCheckLanguage": "en" if english else "translation-required",
        "shapeSignalsReliable": english,
        "confirmed": False,
        "overriddenBy": "",
        "note": ("Every signal here is a heuristic read of the brief's words. Confirm the profile with the user in one "
                 "line before authoring, record it under intake.briefProfile, and set overriddenBy when the user "
                 "corrects it."),
    }


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
    classify_cmd = sub.add_parser("classify", help="Read the brief's language, length and shape, as JSON. Run this before questions.")
    classify_cmd.add_argument("brief", help="Path to the brief text, or - for stdin.")
    questions = sub.add_parser("questions", help="List missing key information and the questions to ask, as JSON.")
    questions.add_argument("brief", help="Path to the brief text, or - for stdin.")
    questions.add_argument("--max", type=int, default=4, help="Most questions to ask at once (default 4).")
    questions.add_argument("--profile", action="store_true", help="Include the briefProfile from classify in the output.")
    args = parser.parse_args(argv)
    try:
        text = sys.stdin.read() if args.brief == "-" else Path(args.brief).read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 1
    if args.command == "classify":
        profile = classify(text)
        profile["ok"] = True
        print(json.dumps(profile, ensure_ascii=False, indent=2))
        return 0
    if not text.strip():
        # An empty brief still gets a profile, so the host has a message to show.
        print(json.dumps({"ok": False, "error": "The brief is empty; ask only for the brief.",
                          "briefProfile": classify(text)}, ensure_ascii=False), file=sys.stderr)
        return 1
    result = analyze(text, max(0, args.max))
    if args.profile:
        result["briefProfile"] = classify(text)
    result["ok"] = True
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
