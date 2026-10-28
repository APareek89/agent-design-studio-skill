"""Focused stdlib tests for artifact contracts,not execution of business controls."""

import copy
import csv
import importlib.util
import io
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/agent-design-studio/scripts/design_io.py"
spec = importlib.util.spec_from_file_location("design_io", SCRIPT)
design_io = importlib.util.module_from_spec(spec)
spec.loader.exec_module(design_io)


def make_design(llm=True):
    brief = "Design an internal request triage aid; humans own decisions."
    source = {"type": "context", "file": "user-brief", "passage": brief}

    def item(id, kind, title, data, description=None):
        return {
            "id": id,
            "kind": kind,
            "title": title,
            "description": description or title + " design responsibility.",
            "reasoning": "Keeps evidence and actual human authority distinct.",
            "assumptions": [],
            "sources": [copy.deepcopy(source)],
            "data": data,
        }

    taskdata = {
        "parentId": "",
        "mode": "sequence",
        "basis": ["Authenticated request and explicit rules"],
        "examples": ["New request", "Missing subject"],
        "autonomy": "Human decides; code validates; LLM may explain only.",
        "frequency": "Per request",
        "risk": "medium",
    }
    root = item("T0", "task", "Prepare owned triage", taskdata)
    leaf = item(
        "T1",
        "task",
        "Recommend or abstain",
        dict(taskdata, parentId="T0", mode="leaf", risk="high"),
    )
    contract = {
        "state": "TRIAGE",
        "transitions": [],
        "bindings": {},
        "failureDisposition": "Owned analyst queue",
        "timeout": "20 seconds then analyst",
        "retryPolicy": "One schema retry; no business write",
        "terminalDisposition": "RECOMMENDED or owned ABSTAIN; never actual decision",
    }
    component = item(
        "C1",
        "component",
        "Bounded recommendation",
        {
            "group": "Agents (LLM)" if llm else "Code: validation",
            "taskIds": ["T1"],
            "inputs": ["requestId:string!", "text:string!"],
            "outputs": ["disposition:RECOMMEND|ABSTAIN!", "evidenceRefs:string[]!"],
            "whyCode": ""
            if llm
            else "Exact required-field checks must be deterministic.",
            "approvalRule": "Read-only; no actual business action authority.",
        },
    )
    framework = item(
        "F1",
        "framework",
        "Bounded assist pattern",
        {
            "category": "fit",
            "taskIds": ["T1"],
            "choice": "One bounded read-only step with human decision owner.",
            "alternatives": ["Reject autonomous decision agent: no human authority."],
            "tradeoffs": "Lower autonomy; actual owner retains decision.",
            "permission": "none",
            "blastRadius": "Internal recommendation only.",
            "approvalRule": "No write tool.",
            "leastPrivilege": "No business credentials.",
            "aws": "Unverified candidate only; no cloud selected.",
            "gcp": "Unverified candidate only; no cloud selected.",
            "azure": "Unverified candidate only; no cloud selected.",
            "openSource": "Unverified local candidate; no deployment claim.",
        },
    )
    model = item(
        "M1",
        "model",
        "Illustrative model budget",
        {
            "componentId": "C1",
            "tier": "small",
            "rationale": "One W1 invocation plus at most one retry; unavailable->human; prices unknown/unpriced,not free.",
            "fineTuneWhen": "Only after labelled recurring failures and heldout safety evidence.",
            "callsPerCase": 1,
            "inputTokens": 1000,
            "outputTokens": 100,
            "inputPrice": 0,
            "outputPrice": 0,
        },
    )
    failure = item(
        "FM1",
        "fmea",
        "Missing subject assigned as confirmed",
        {
            "taskIds": ["T1"],
            "componentIds": ["C1"],
            "effect": "Wrong owner and unresolved queue.",
            "cause": "Missing subject interpreted as known.",
            "severity": 8,
            "occurrence": 3,
            "detection": 5,
            "control": "Abstain with evidence and actual human fallback.",
            "detectionMethod": "EV1 isolated missing-subject fixture.",
            "action": "Operations owner requires EV1 all assertions pass before assist release.",
            "metric": "Unsupported subject count",
            "kpi": "Unowned requests per weekly intake cohort",
            "evalIds": ["EV1", "EV2", "EV3", "EV4"],
            "acceptedRisk": False,
            "commonToAll": True,
        },
    )
    evals = []
    for i, category in enumerate(("golden", "offline", "online", "release"), 1):
        evals.append(
            item(
                "EV" + str(i),
                "eval",
                category + " evidence check",
                {
                    "category": category,
                    "taskIds": ["T1"],
                    "componentIds": ["C1"],
                    "failureModeIds": ["FM1"],
                    "input": json.dumps(
                        {"requestId": "REQ1", "text": "Need help", "subject": None}
                    ),
                    "expected": json.dumps({"disposition": "ABSTAIN", "writes": 0}),
                    "passRule": json.dumps(
                        {"equals": {"disposition": "ABSTAIN", "writes": 0}}
                    ),
                    "metric": "Unsupported subject count",
                    "kpi": "Unowned requests per weekly intake cohort",
                    "target": "Zero unsupported subjects in synthetic test suite; real rate unknown.",
                    "testSet": "REQ1 incomplete plus complete positive counterpart.",
                    "labelling": "Operations labels; control owner adjudicates.",
                    "cadence": "Each change; online monitor continuous.",
                    "alertThreshold": "Any unsupported subject routes to operations owner.",
                },
            )
        )
    rollout = []
    for i, category in enumerate(("kpi", "phase", "experiment", "owner"), 1):
        rollout.append(
            item(
                "R" + str(i),
                "rollout",
                category + " plan",
                {
                    "category": category,
                    "businessKpi": "Unowned request count / all admitted requests,weekly; baseline unknown.",
                    "aiMetrics": [
                        "Abstention protects unknown-subject boundary; queue age is service guardrail."
                    ],
                    "phase": "Shadow then human assist",
                    "gate": "Entry: synthetic tests; exit: operations reviews labels; no measured efficacy claim.",
                    "owner": "Operations owner proposed; confirm staffing before launch.",
                    "experiment": "Team-week assignment; collect baseline variance before power calculation; no sufficient sample claim.",
                },
            )
        )
    stages = {key: {"items": [], "assumptions": []} for key in design_io.STAGES}
    stages["context"]["items"] = [
        item(
            "CTX1",
            "context",
            "Bounded brief",
            {"field": "useCase", "value": brief, "question": ""},
        )
    ]
    stages["tasks"]["items"] = [
        root,
        leaf,
        item(
            "A1",
            "attribute",
            "Authenticated request",
            {
                "taskIds": ["T1"],
                "sourceSystem": "Request registry proposed by H1",
                "loaded": "on demand",
            },
        ),
    ]
    stages["components"]["items"] = [component]
    stages["workflow"]["items"] = [
        item(
            "W1",
            "workflow",
            "Recommend or abstain",
            {
                "componentId": "C1",
                "taskIds": ["T1"],
                "next": [],
                "decision": False,
                "example": "Unknown subject stays owned for human review.",
            },
            json.dumps(contract),
        )
    ]
    stages["framework"]["items"] = [framework]
    stages["models"]["items"] = [model] if llm else []
    stages["fmea"]["items"] = [failure]
    stages["evals"]["items"] = evals
    stages["rollout"]["items"] = rollout
    stages["export"]["items"] = [
        item(
            "X1",
            "export",
            "Build bounded triage",
            {
                "acceptanceCriteria": [
                    "EV1 missing subject yields ABSTAIN and zero writes."
                ],
                "buildInstructions": "Implement C1/W1 read-only inputs and preserve actual human decision owner; do not add authority.",
            },
        )
    ]
    return {
        "schemaVersion": "1.0",
        "title": "Synthetic triage design",
        "brief": brief,
        "assumptions": [
            {
                "id": "H1",
                "statement": "A scoped request registry exists.",
                "why": "Needed to identify request evidence.",
                "owner": "Operations owner",
                "validation": "Confirm read contract and access scope.",
                "launchBlocker": True,
            }
        ],
        "stages": stages,
    }


def make_review(status="pass"):
    return {
        "method": "self-review",
        "round": 1,
        "status": status,
        "dimensions": [
            {
                "id": "D" + str(i),
                "score": 3,
                "evidence": [
                    "C1/W1: bounded read-only contract; remaining evidence is a design judgement."
                ],
            }
            for i in range(1, 13)
        ],
        "issues": [],
        "limitations": [
            "Synthetic design review only; business fixtures and provider reliability were not executed."
        ],
    }


class DesignTests(unittest.TestCase):
    def setUp(self):
        self.design = make_design()

    def messages(self, d=None):
        return "\n".join(
            x["path"] + " " + x["message"]
            for x in design_io.validate_design(self.design if d is None else d)[
                "errors"
            ]
        )

    def test_complete_fixture_and_no_llm(self):
        self.assertTrue(
            design_io.validate_design(self.design)["valid"], self.messages()
        )
        self.assertTrue(design_io.validate_design(make_design(False))["valid"])

    def test_required_and_strict_fields_have_paths(self):
        del self.design["stages"]["components"]["items"][0]["data"]["outputs"]
        self.assertIn(".data.outputs", self.messages())
        self.design = make_design()
        self.design["stages"]["context"]["items"][0]["approved"] = True
        self.assertIn(".approved", self.messages())

    def test_schema_bounds_types_and_unknown_keywords(self):
        self.design["stages"]["models"]["items"][0]["data"]["callsPerCase"] = True
        self.assertIn("Expected number", self.messages())
        schema = {
            "type": "object",
            "properties": {"x": {"type": "string", "format": "email"}},
        }
        self.assertIn("Unsupported schema keyword", str(design_io.audit_schema(schema)))
        self.assertTrue(
            design_io.check_schema("XX", {"type": "string", "pattern": "^A"})
        )
        self.assertTrue(
            design_io.check_schema(
                [1, 2], {"type": "array", "maxItems": 1, "items": {"type": "integer"}}
            )
        )
        self.assertTrue(
            design_io.check_schema("abc", {"type": "string", "maxLength": 2})
        )
        self.assertTrue(design_io.check_schema(True, {"enum": [1]}))
        self.assertFalse(
            design_io.check_schema(10**1000, {"type": "integer", "minimum": 0})
        )

    def test_nonfinite_and_duplicate_json_rejected(self):
        for text in ('{"x":NaN}', '{"x":Infinity}', '{"x":1,"x":2}'):
            with self.assertRaises(ValueError):
                design_io.parse_json(text)
        self.design["stages"]["models"]["items"][0]["data"]["inputPrice"] = math.inf
        self.assertIn("number", self.messages())

    def test_hypothesis_and_exact_brief_sources(self):
        item = self.design["stages"]["components"]["items"][0]
        item["sources"] = [
            {
                "type": "hypothesis",
                "file": "H1",
                "passage": self.design["assumptions"][0]["statement"],
            }
        ]
        self.assertTrue(design_io.validate_design(self.design)["valid"])
        item["sources"][0]["passage"] = "Not the actual statement"
        self.assertIn("existing H ID", self.messages())
        item["sources"] = [
            {"type": "context", "file": "user-brief", "passage": "Invented brief quote"}
        ]
        self.assertIn("exact nonempty passage", self.messages())
        item["sources"] = [
            {"type": "upload", "file": "missing.pdf", "passage": "Unverified"}
        ]
        self.assertIn("Unbacked upload", self.messages())

    def test_duplicate_ids_and_hypotheses(self):
        self.design["stages"]["tasks"]["items"].append(
            copy.deepcopy(self.design["stages"]["tasks"]["items"][1])
        )
        self.assertIn("Duplicate item ID", self.messages())
        self.design = make_design()
        self.design["assumptions"].append(copy.deepcopy(self.design["assumptions"][0]))
        self.assertIn("Duplicate hypothesis", self.messages())

    def test_one_root_cycles_and_depth(self):
        self.design["stages"]["tasks"]["items"][1]["data"]["parentId"] = ""
        self.assertIn("exactly one", self.messages())
        self.design = make_design()
        self.design["stages"]["tasks"]["items"][0]["data"]["parentId"] = "T1"
        self.assertIn("cycle", self.messages())
        self.design = make_design()
        tasks = self.design["stages"]["tasks"]["items"]
        leaf = tasks[1]
        leaf["data"]["mode"] = "sequence"
        a = copy.deepcopy(leaf)
        a["id"] = "T1.1"
        a["data"].update(parentId="T1", mode="sequence")
        b = copy.deepcopy(a)
        b["id"] = "T1.1.1"
        b["data"].update(parentId="T1.1", mode="leaf")
        tasks.extend([a, b])
        self.assertIn("depth exceeds", self.messages())

    def test_missing_links_component_coverage_and_canonical_task_consistency(self):
        self.design["stages"]["components"]["items"][0]["data"]["taskIds"] = ["NO_TASK"]
        self.assertIn("References missing taskIds", self.messages())
        self.assertIn("Leaf task has no", self.messages())
        self.assertIn("not served by its component", self.messages())
        self.design = make_design()
        self.design["stages"]["workflow"]["items"][0]["data"]["componentId"] = "C404"
        self.assertIn("component is missing", self.messages())

    def test_workflow_guard_mode_terminal_and_unreachable(self):
        node = self.design["stages"]["workflow"]["items"][0]
        contract = json.loads(node["description"])
        node["data"]["next"] = ["W1"]
        node["data"]["decision"] = True
        contract["transitions"] = [{"to": "W1", "when": "", "mode": ""}]
        node["description"] = json.dumps(contract)
        msgs = self.messages()
        self.assertIn("nonempty when", msgs)
        self.assertIn("nonempty mode", msgs)
        self.assertIn("entry node", msgs)
        self.design = make_design()
        node = self.design["stages"]["workflow"]["items"][0]
        contract = json.loads(node["description"])
        contract["terminalDisposition"] = "none"
        node["description"] = json.dumps(contract)
        self.assertIn("durable terminal", self.messages())

    def test_exact_transition_targets(self):
        node = self.design["stages"]["workflow"]["items"][0]
        contract = json.loads(node["description"])
        contract["transitions"] = [
            {"to": "W404", "when": "always", "mode": "exclusive"}
        ]
        node["description"] = json.dumps(contract)
        self.assertIn("match unique next IDs", self.messages())

    def test_nonterminal_null_and_shared_successor_predicates(self):
        for terminal_value in (None, ""):
            d = make_design()
            first = d["stages"]["workflow"]["items"][0]
            second = copy.deepcopy(first)
            second["id"] = "W2"
            d["stages"]["workflow"]["items"].append(second)
            c = json.loads(first["description"])
            c["terminalDisposition"] = terminal_value
            c["transitions"] = [
                {"to": "W2", "when": "request.kind == A", "mode": "exclusive"},
                {"to": "W2", "when": "request.kind == B", "mode": "exclusive"},
            ]
            first["description"] = json.dumps(c)
            first["data"].update(next=["W2"], decision=True)
            result = design_io.validate_design(d)
            self.assertTrue(result["valid"], result["errors"])

    def test_malformed_transition_target_reports_error_not_crash(self):
        node = self.design["stages"]["workflow"]["items"][0]
        c = json.loads(node["description"])
        c["transitions"] = [
            {"to": {"bad": "shape"}, "when": "always", "mode": "exclusive"}
        ]
        node["description"] = json.dumps(c)
        self.assertIn("nonempty to", self.messages())

    def test_all_category_reciprocity_and_golden_coverage(self):
        self.design["stages"]["fmea"]["items"][0]["data"]["evalIds"].remove("EV3")
        self.assertIn("reciprocal across all", self.messages())
        self.design = make_design()
        self.design["stages"]["evals"]["items"][0]["data"]["category"] = "offline"
        msgs = self.messages()
        self.assertIn("Unaccepted failure needs", msgs)
        self.assertIn("High-risk leaf needs", msgs)

    def test_golden_objects_not_arrays_empty_or_prose(self):
        for value in ("[]", "{}", "not json", '{"v":NaN}'):
            d = make_design()
            d["stages"]["evals"]["items"][0]["data"]["passRule"] = value
            self.assertIn(".passRule", self.messages(d))

    def test_model_cardinality_and_code_plans(self):
        self.design["stages"]["models"]["items"] = []
        self.assertIn("Exactly one active model", self.messages())
        self.design = make_design(False)
        model = make_design()["stages"]["models"]["items"][0]
        self.design["stages"]["models"]["items"] = [model]
        self.assertIn("never code", self.messages())

    def test_experiment_text_can_be_empty_on_nonexperiment_rollout_cards(self):
        for item in self.design["stages"]["rollout"]["items"]:
            if item["data"]["category"] != "experiment":
                item["data"]["experiment"] = ""
        result = design_io.validate_design(self.design)
        self.assertTrue(result["valid"], result["errors"])
        card = next(
            x
            for x in self.design["stages"]["rollout"]["items"]
            if x["data"]["category"] == "experiment"
        )
        card["data"]["experiment"] = ""
        self.assertIn("Experiment card needs", self.messages())

    def test_real_risk_and_rollout_cards(self):
        self.design["stages"]["fmea"]["items"][0]["data"]["action"] = " "
        self.assertIn("concrete action", self.messages())
        self.design = make_design()
        self.design["stages"]["rollout"]["items"] = [
            x
            for x in self.design["stages"]["rollout"]["items"]
            if x["data"]["category"] != "owner"
        ]
        self.assertIn("owner rollout", self.messages())


class ReviewTests(unittest.TestCase):
    def test_pass_and_honest_needs_work(self):
        self.assertTrue(design_io.validate_review(make_review())["valid"])
        r = make_review("needs-work")
        r["dimensions"][0]["score"] = 2
        r["issues"] = [
            {
                "id": "I1",
                "severity": "major",
                "stage": "workflow",
                "itemId": "W1",
                "message": "W1 missing source binding; ambiguity requires typed producer before release.",
                "resolved": False,
            }
        ]
        result = design_io.validate_review(r)
        self.assertTrue(result["valid"])
        self.assertEqual(result["status"], "needs-work")

    def test_fabricated_pass_duplicate_dims_bool_and_missing_evidence(self):
        r = make_review()
        r["dimensions"][0]["score"] = 2
        self.assertFalse(design_io.validate_review(r)["valid"])
        r = make_review()
        r["dimensions"][-1]["id"] = "D1"
        self.assertFalse(design_io.validate_review(r)["valid"])
        r = make_review()
        r["dimensions"][0]["score"] = True
        self.assertFalse(design_io.validate_review(r)["valid"])
        r = make_review()
        r["dimensions"][0]["evidence"] = [" "]
        self.assertFalse(design_io.validate_review(r)["valid"])

    def test_observations_and_warnings_are_valid_nonblocking_review_notes(self):
        for severity in ("observation", "warning"):
            r = make_review()
            r["issues"] = [
                {
                    "id": "NOTE1",
                    "severity": severity,
                    "stage": "context",
                    "itemId": "CTX1",
                    "message": "CTX1 bounded brief remains an author-supplied design assumption.",
                    "resolved": False,
                }
            ]
            result = design_io.validate_review(r)
            self.assertTrue(result["valid"])
            self.assertEqual(result["status"], "pass")
        self.assertIn("this helper makes no provider", design_io.LIMITATIONS[0])

    def test_major_issue_and_structural_errors_block_pass(self):
        r = make_review()
        r["issues"] = [
            {
                "id": "I1",
                "severity": "major",
                "stage": "workflow",
                "itemId": "W1",
                "message": "Concrete omission needs correction.",
                "resolved": False,
            }
        ]
        self.assertFalse(design_io.validate_review(r)["valid"])
        self.assertFalse(design_io.validate_review(make_review(), False)["valid"])
        r = make_review()
        r["limitations"] = []
        self.assertFalse(design_io.validate_review(r)["valid"])


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.design_path = self.root / "design.json"
        self.review_path = self.root / "review.json"
        self.out = self.root / "export"
        self.design = make_design()
        self.review = make_review()
        self.write_inputs()

    def tearDown(self):
        self.temp.cleanup()

    def write_inputs(self):
        self.design_path.write_text(json.dumps(self.design))
        self.review_path.write_text(json.dumps(self.review))

    def test_export_files_and_canonical_consistency(self):
        self.design["stages"]["components"]["items"][0]["description"] = (
            "CANONICAL-UPDATED-C1"
        )
        self.write_inputs()
        result = design_io.export_design(self.design_path, self.out, self.review_path)
        self.assertTrue(result["ok"])
        self.assertEqual(
            set(p.name for p in self.out.iterdir()), set(design_io.OUTPUT_FILES)
        )
        for name in ("PRD.md", "architecture.md", "build-prompt.md"):
            text = (self.out / name).read_text()
            self.assertIn("CANONICAL-UPDATED-C1", text)
            self.assertIn("DESIGN ONLY", text)
        self.assertIn(
            "Would you also like a visual HTML version in the same ten-stage structure as the app?",
            (self.out / "build-prompt.md").read_text(),
        )
        self.assertIn(
            "After delivering DESIGN.pdf, ask the user:",
            (self.out / "build-prompt.md").read_text(),
        )
        self.assertIn(
            "Generate HTML only after opt-in, unless already requested.",
            (self.out / "build-prompt.md").read_text(),
        )
        architecture = (self.out / "architecture.md").read_text()
        self.assertIn("flowchart TD", architecture)
        self.assertIn("task_T0 --> task_T1", architecture)
        ev = json.loads((self.out / "eval-set.json").read_text())
        self.assertEqual(ev["items"], self.design["stages"]["evals"]["items"])
        manifest = json.loads((self.out / "validation.json").read_text())
        self.assertEqual(manifest["review"]["dimensions"], self.review["dimensions"])
        self.assertTrue(manifest["designOnly"])
        self.assertEqual(json.loads(self.design_path.read_text()), self.design)

    def test_needs_work_is_exportable_with_banner(self):
        self.review["status"] = "needs-work"
        self.review["dimensions"][0]["score"] = 2
        self.write_inputs()
        r = design_io.export_design(self.design_path, self.out, self.review_path)
        self.assertTrue(r["ok"])
        self.assertEqual(r["status"], "needs-work")
        self.assertIn("NEEDS-WORK", (self.out / "PRD.md").read_text())

    def test_false_pass_or_invalid_design_writes_nothing(self):
        self.review["dimensions"][0]["score"] = 2
        self.write_inputs()
        self.assertFalse(
            design_io.export_design(self.design_path, self.out, self.review_path)["ok"]
        )
        self.assertFalse(self.out.exists())
        self.design["stages"]["evals"]["items"][0]["data"]["input"] = "prose"
        self.write_inputs()
        self.assertFalse(
            design_io.export_design(self.design_path, self.out, self.review_path)["ok"]
        )
        self.assertFalse(self.out.exists())

    def test_csv_formula_escaping(self):
        self.design["stages"]["fmea"]["items"][0]["title"] = "=CMD()"
        self.design["stages"]["fmea"]["items"][0]["data"]["cause"] = "\t=CMD()"
        self.write_inputs()
        design_io.export_design(self.design_path, self.out, self.review_path)
        row = list(
            csv.DictReader(io.StringIO((self.out / "fmea-register.csv").read_text()))
        )[0]
        self.assertEqual(row["title"], "'=CMD()")
        self.assertTrue(row["cause"].startswith("'\t"))
        self.assertEqual(row["rpn"], "120")
        for text in ("+SUM(1)", "-1+2", "@IMPORT", "  =x", "\ttext"):
            self.assertTrue(design_io._csv_safe(text).startswith("'"))

    def test_no_input_or_unrelated_overwrite_and_safe_regeneration(self):
        before = self.design_path.read_bytes()
        self.out.mkdir()
        (self.out / "PRD.md").write_text("Unrelated document")
        with self.assertRaises(ValueError):
            design_io.export_design(self.design_path, self.out, self.review_path)
        self.assertEqual((self.out / "PRD.md").read_text(), "Unrelated document")
        self.assertEqual(self.design_path.read_bytes(), before)
        (self.out / "PRD.md").unlink()
        design_io.export_design(self.design_path, self.out, self.review_path)
        self.assertTrue(
            design_io.export_design(self.design_path, self.out, self.review_path)["ok"]
        )

    def test_same_folder_inputs_history_and_unrelated_files_preserved(self):
        history = self.root / "review-round-1.json"
        history.write_text("original failed round")
        work = self.root / ".work"
        work.mkdir()
        (work / "notes.txt").write_text("private local notes")
        unrelated = self.root / "brief.txt"
        unrelated.write_text("Original brief source")
        before = {
            p: p.read_bytes()
            for p in (
                self.design_path,
                self.review_path,
                history,
                unrelated,
                work / "notes.txt",
            )
        }
        result = design_io.export_design(self.design_path, self.root, self.review_path)
        self.assertTrue(result["ok"])
        self.assertTrue(
            design_io.export_design(self.design_path, self.root, self.review_path)["ok"]
        )
        for path, data in before.items():
            self.assertEqual(path.read_bytes(), data)

    def test_exact_input_filename_and_hardlink_collision_refused(self):
        collision = self.root / "PRD.md"
        collision.write_text(json.dumps(self.design))
        before = collision.read_bytes()
        with self.assertRaises(ValueError):
            design_io.export_design(collision, self.root, self.review_path)
        self.assertEqual(collision.read_bytes(), before)
        collision.unlink()
        design_io.export_design(self.design_path, self.out, self.review_path)
        target = self.out / "PRD.md"
        target.unlink()
        try:
            target.hardlink_to(self.design_path)
        except AttributeError:
            import os

            os.link(self.design_path, target)
        with self.assertRaises(ValueError):
            design_io.export_design(self.design_path, self.out, self.review_path)

    def test_generated_folder_can_keep_unrelated_files(self):
        design_io.export_design(self.design_path, self.out, self.review_path)
        extra = self.out / "README-user.md"
        extra.write_text("Keep me")
        self.assertTrue(
            design_io.export_design(self.design_path, self.out, self.review_path)["ok"]
        )
        self.assertEqual(extra.read_text(), "Keep me")

    def test_symlink_outputs_refused(self):
        design_io.export_design(self.design_path, self.out, self.review_path)
        target = self.out / "PRD.md"
        target.unlink()
        target.symlink_to(self.design_path)
        with self.assertRaises(ValueError):
            design_io.export_design(self.design_path, self.out, self.review_path)

    def test_cli_json_exit_codes_and_required_review(self):
        run = subprocess.run(
            [sys.executable, str(SCRIPT), "validate", str(self.design_path)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertTrue(json.loads(run.stdout)["valid"])
        self.design_path.write_text("{invalid")
        run = subprocess.run(
            [sys.executable, str(SCRIPT), "validate", str(self.design_path)],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(run.returncode, 0)
        self.assertEqual(json.loads(run.stdout)["status"], "input-or-output-error")
        self.assertNotIn("Traceback", run.stderr)
        run = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "export",
                str(self.design_path),
                "--out",
                str(self.out),
            ],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("--review", run.stderr)


if __name__ == "__main__":
    unittest.main()
