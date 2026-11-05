"""Read-only, real-time and multi-tenant systems get different rules.

`intake.briefProfile` says what kind of system the brief describes. Three
kinds change what the design must contain:

  read-only   the ten stages stay, but the risk families, goldens, authority
              wording and coverage are about answers rather than writes;
  real-time   nodes may carry a latency budget and a streaming flag, any node
              that speaks needs a barge-in branch, and a speech component must
              report its confidence;
  multi-tenant every identity binding carries a trusted tenant, and a
              component that reads by record ID is scoped to one.

A design with no profile keeps the v1.2 rules exactly, which the seed examples
check.
"""

import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills/agent-design-studio/scripts"


def module(name, prefix="bp_"):
    spec = importlib.util.spec_from_file_location(prefix + name, SCRIPTS / (name + ".py"))
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


design_io = module("design_io")
design_html = module("design_html")
semantic_checks = module("semantic_checks")
fixture_spec = importlib.util.spec_from_file_location("bp_fixtures", ROOT / "tests/test_design_io.py")
fixtures = importlib.util.module_from_spec(fixture_spec)
fixture_spec.loader.exec_module(fixtures)

TELECOM = ROOT / "examples/telecom"


def profile(**fields):
    base = {
        "language": {"code": "en", "name": "English"},
        "words": 120, "length": "ok", "isAgentSystem": True,
        "writes": True, "realtime": False, "multiTenant": False,
    }
    base.update(fields)
    return base


def with_profile(design, **fields):
    design = copy.deepcopy(design)
    design["intake"] = {"asked": False, "tool": "", "questions": [], "briefProfile": profile(**fields)}
    return design


def read_component(design):
    """A component the design declares as a reader."""
    reads = {e["componentId"] for e in design["semantics"]["componentEffects"] if e["effect"] == "read"}
    return next(c for c in design["stages"]["components"]["items"] if c["id"] in reads)


def answer_golden(design, eval_id, polarity, citations):
    """An answer golden plus the eval it asserts on, wired to a read component."""
    template = next(e for e in design["stages"]["evals"]["items"] if e["data"]["category"] == "golden")
    reader = read_component(design)
    item = copy.deepcopy(template)
    item["id"] = eval_id
    item["title"] = ("Answers with a verifiable citation" if polarity == "positive"
                     else "Declines when the corpus is silent")
    payload = {"question": "What does the policy say?", "corpus": "reports-v1"}
    expected = {"citations": citations, "answered": polarity == "positive"}
    item["data"]["input"] = json.dumps(payload)
    item["data"]["expected"] = json.dumps(expected)
    item["data"]["passRule"] = json.dumps({"equals": {"citations": citations}})
    item["data"]["componentIds"] = [reader["id"]]
    # Reciprocal FMEA links are checked across every eval category; a new
    # golden links to no failure mode rather than claiming one it does not test.
    item["data"]["failureModeIds"] = []
    design["stages"]["evals"]["items"].append(item)
    design["semantics"]["goldens"].append({
        "evalId": eval_id, "actionClass": "answer", "polarity": polarity,
        "citationField": "sources",
        "fixture": {"input": payload, "expected": expected},
    })


def read_only_design():
    """The telecom design given a read-only profile and the goldens that profile needs."""
    design = with_profile(design_io.load_json(TELECOM / "design.json"), writes=False)
    answer_golden(design, "EV91", "positive", 2)
    answer_golden(design, "EV92", "negative", 0)
    return design


def multi_tenant_design():
    """The telecom design given a multi-tenant profile and the tenant scope it needs."""
    design = with_profile(design_io.load_json(TELECOM / "design.json"), multiTenant=True)
    effects = {e["componentId"]: e["effect"] for e in design["semantics"]["componentEffects"]}
    for component in design["stages"]["components"]["items"]:
        if effects.get(component["id"]) in ("read", "write"):
            component["data"]["inputs"] = ["tenantId:string"] + list(component["data"]["inputs"])
    for node in design["semantics"]["nodes"]:
        bindings = node.get("bindings")
        if isinstance(bindings, list) and any(b.get("category") == "identity" for b in bindings):
            node["bindings"] = [{"field": "tenantId", "category": "identity", "source": "trusted"}] + bindings
    return design


def rule_ids(errors):
    return {e.get("ruleId") for e in errors}


class ProfileIsOptional(unittest.TestCase):
    def test_a_design_with_no_profile_keeps_the_existing_rules(self):
        design = design_io.load_json(TELECOM / "design.json")
        self.assertEqual(design_io.brief_profile(design), {})
        self.assertFalse(design_io.is_read_only(design))
        self.assertFalse(design_io.is_realtime(design))
        self.assertFalse(design_io.is_multi_tenant(design))
        self.assertTrue(design_io.validate_design(design)["valid"])

    def test_a_writing_profile_changes_nothing_for_the_seed(self):
        design = with_profile(design_io.load_json(TELECOM / "design.json"), writes=True)
        self.assertTrue(design_io.validate_design(design)["valid"])


class ReadOnlyProfile(unittest.TestCase):
    def setUp(self):
        self.design = with_profile(design_io.load_json(TELECOM / "design.json"), writes=False)

    def test_the_money_trigger_check_does_not_apply(self):
        report = design_io.coverage_report(self.design)
        cov11 = next(c for c in report["checks"] if c["id"] == "COV11")
        self.assertEqual(cov11["status"], "n/a")
        self.assertIn("Read-only", cov11["evidence"])

    def test_cov16_requires_citation_goldens_and_an_access_statement(self):
        report = design_io.coverage_report(self.design)
        cov16 = next(c for c in report["checks"] if c["id"] == "COV16")
        self.assertIn(cov16["status"], ("covered", "missing"))
        self.assertIn("citation", cov16["title"].lower())

    def test_cov17_names_the_read_only_risk_families_that_are_missing(self):
        report = design_io.coverage_report(self.design)
        cov17 = next(c for c in report["checks"] if c["id"] == "COV17")
        # The telecom register is about money writes, so it covers none of them.
        self.assertEqual(cov17["status"], "missing")
        for family in ("prompt injection", "missing citation"):
            self.assertIn(family, cov17["evidence"])

    def test_every_read_only_risk_family_is_detected_when_present(self):
        design = copy.deepcopy(self.design)
        card = design["stages"]["fmea"]["items"][0]
        card["description"] += (
            " Stale source or superseded policy wording. Missing citation on an answer. "
            "An answer outside the corpus. Prompt injection through an uploaded document. "
            "Leaking content the reader has no permission to see. "
            "A confident answer when the corpus is silent, where the system must decline."
        )
        self.assertEqual(design_io.read_only_risk_gaps(design), [])

    def test_the_read_only_rules_are_satisfiable(self):
        design = read_only_design()
        errors = [e for e in semantic_checks.validate_semantics(design) if e.get("ruleId") == "SEM008"]
        self.assertEqual(errors, [], "a design with answer goldens must pass SEM008")

    def test_the_authority_table_says_answers_not_acts(self):
        review = design_io.load_json(TELECOM / "review.json")
        document = design_html.render_html(read_only_design(), review)
        brief = document[document.find('data-view="brief"'):]
        brief = brief[: brief.find("</section>")]
        self.assertIn("Answers with citation", brief)
        self.assertNotIn("Acts alone", brief)

    def test_sem008_demands_answer_goldens_when_there_are_none(self):
        errors = semantic_checks.validate_semantics(self.design)
        self.assertIn("SEM008", rule_ids(errors))
        message = next(e["message"] for e in errors if e.get("ruleId") == "SEM008")
        self.assertIn("answer", message)
        self.assertIn("citation", message)

    def test_sem008_checks_polarity_citation_count_and_a_read_source(self):
        design = copy.deepcopy(self.design)
        evals = design["stages"]["evals"]["items"]
        golden = next(e for e in evals if e["data"]["category"] == "golden")
        positive = copy.deepcopy(golden)
        positive["id"] = "EV90"
        positive["data"]["expected"] = json.dumps({"citations": 0})
        design["stages"]["evals"]["items"].append(positive)
        design["semantics"]["goldens"].append({
            "evalId": "EV90", "actionClass": "answer", "polarity": "positive",
            "citationField": "sources", "fixture": {"input": {}, "expected": {}},
        })
        errors = [e for e in semantic_checks.validate_semantics(design) if e.get("ruleId") == "SEM008"]
        self.assertTrue(any("at least one citation" in e["message"] for e in errors), errors)

    def test_sem008_is_silent_for_a_writing_design(self):
        design = with_profile(design_io.load_json(TELECOM / "design.json"), writes=True)
        self.assertNotIn("SEM008", rule_ids(semantic_checks.validate_semantics(design)))


class RealtimeProfile(unittest.TestCase):
    def setUp(self):
        self.design = with_profile(design_io.load_json(TELECOM / "design.json"), realtime=True)
        self.review = design_io.load_json(TELECOM / "review.json")

    def test_a_node_may_carry_a_latency_budget_and_a_streaming_flag(self):
        design = copy.deepcopy(self.design)
        node = design["stages"]["workflow"]["items"][0]
        node["data"]["latencyBudgetMs"] = 800
        node["data"]["streaming"] = True
        result = design_io.validate_design(design)
        self.assertTrue(result["valid"], result["errors"][:3])

    def test_the_budget_shows_on_the_node_and_in_its_detail(self):
        design = copy.deepcopy(self.design)
        node = design["stages"]["workflow"]["items"][0]
        node["data"]["latencyBudgetMs"] = 800
        node["data"]["streaming"] = True
        document = design_html.render_html(design, self.review)
        self.assertIn("800ms", document)
        self.assertIn("Latency budget", document)
        self.assertIn("streams its reply", document)

    def test_a_design_with_no_budget_shows_no_latency_row(self):
        document = design_html.render_html(self.design, self.review)
        self.assertNotIn("Latency budget", document)

    def test_a_node_that_speaks_needs_a_barge_in_branch(self):
        design = copy.deepcopy(self.design)
        node = design["stages"]["workflow"]["items"][1]
        node["description"] = node["description"]
        node["title"] = "Speak the explanation to the caller"
        errors = design_io._profile_errors(design)
        self.assertTrue(any("barge-in" in e["message"] for e in errors), errors)
        self.assertTrue(any(node["id"] in e["message"] for e in errors))

    def test_a_barge_in_branch_satisfies_the_rule(self):
        design = copy.deepcopy(self.design)
        node = design["stages"]["workflow"]["items"][1]
        node["title"] = "Speak the explanation to the caller"
        contract = json.loads(node["description"])
        contract["transitions"] = list(contract.get("transitions", [])) + [
            {"to": node["data"]["next"][0], "when": "caller barges in: cancel the sentence, keep the case state",
             "mode": "exclusive"}
        ]
        node["description"] = json.dumps(contract)
        self.assertEqual([e for e in design_io._profile_errors(design) if "barge-in" in e["message"]], [])

    def test_a_speech_component_must_report_confidence(self):
        design = copy.deepcopy(self.design)
        component = copy.deepcopy(design["stages"]["components"]["items"][0])
        component["id"] = "C90"
        component["title"] = "Speech to text"
        component["description"] = "Transcribes the caller's speech."
        component["data"]["outputs"] = ["transcript:string"]
        design["stages"]["components"]["items"].append(component)
        errors = design_io._profile_errors(design)
        self.assertTrue(any("confidence" in e["message"] for e in errors), errors)
        component["data"]["outputs"] = ["transcript:string", "confidence:number"]
        self.assertEqual([e for e in design_io._profile_errors(design) if "confidence" in e["message"]], [])

    def test_a_path_over_the_briefs_latency_target_warns(self):
        design = copy.deepcopy(self.design)
        design["brief"] = design["brief"] + " The caller must hear a first reply under 800 ms."
        for node in design["stages"]["workflow"]["items"]:
            node["data"]["latencyBudgetMs"] = 500
        design["stages"]["workflow"]["items"][-1]["title"] = "Speak the outcome to the caller"
        warnings = design_io._profile_warnings(design)
        self.assertTrue(any("over the brief's stated 800 ms" in w["message"] for w in warnings), warnings)

    def test_a_stated_target_with_no_budget_anywhere_says_so(self):
        design = copy.deepcopy(self.design)
        design["brief"] += " The caller must hear a first reply under 800 ms."
        warnings = design_io._profile_warnings(design)
        self.assertTrue(any("no node carries a latencyBudgetMs" in w["message"] for w in warnings), warnings)

    def test_the_target_is_read_from_milliseconds_or_seconds(self):
        self.assertEqual(design_io._latency_target({"brief": "reply within 900 ms"}), 900)
        self.assertEqual(design_io._latency_target({"brief": "reply under 2 seconds"}), 2000)
        self.assertIsNone(design_io._latency_target({"brief": "reply quickly"}))


class MultiTenantProfile(unittest.TestCase):
    def setUp(self):
        self.design = with_profile(design_io.load_json(TELECOM / "design.json"), multiTenant=True)

    def test_sem009_fails_a_reader_that_takes_a_record_id_with_no_tenant(self):
        design = copy.deepcopy(self.design)
        component = next(c for c in design["stages"]["components"]["items"]
                         if any(e["componentId"] == c["id"] and e["effect"] == "read"
                                for e in design["semantics"]["componentEffects"]))
        component["data"]["inputs"] = ["customerId:string"]
        errors = semantic_checks._tenant_scope(
            design, design["semantics"],
            {c["id"]: c for c in design["stages"]["components"]["items"]},
            {w["id"]: w for w in design["stages"]["workflow"]["items"]})
        self.assertTrue(any(e["ruleId"] == "SEM009" and component["id"] in e["message"] for e in errors), errors)

    def test_a_tenant_input_satisfies_sem009(self):
        design = copy.deepcopy(self.design)
        component = next(c for c in design["stages"]["components"]["items"]
                         if any(e["componentId"] == c["id"] and e["effect"] == "read"
                                for e in design["semantics"]["componentEffects"]))
        component["data"]["inputs"] = ["tenantId:string", "customerId:string"]
        errors = semantic_checks._tenant_scope(
            design, design["semantics"],
            {component["id"]: component},
            {w["id"]: w for w in design["stages"]["workflow"]["items"]})
        self.assertEqual([e for e in errors if component["id"] in e["message"]], [])

    def test_an_identity_binding_must_name_a_trusted_tenant(self):
        design = copy.deepcopy(self.design)
        node = next(n for n in design["semantics"]["nodes"] if n.get("kind") == "write")
        node["bindings"] = [{"field": "customerId", "category": "identity", "source": "trusted"}]
        errors = semantic_checks._tenant_scope(design, design["semantics"], {}, {})
        self.assertTrue(any("names no tenant field" in e["message"] for e in errors), errors)
        node["bindings"] = [{"field": "tenantId", "category": "identity", "source": "llm"}]
        errors = semantic_checks._tenant_scope(design, design["semantics"], {}, {})
        self.assertTrue(any("must be trusted" in e["message"] for e in errors), errors)
        node["bindings"] = [{"field": "tenantId", "category": "identity", "source": "trusted"}]
        self.assertEqual(semantic_checks._tenant_scope(design, design["semantics"], {}, {}), [])

    def test_sem009_is_silent_for_a_single_tenant_design(self):
        design = with_profile(design_io.load_json(TELECOM / "design.json"), multiTenant=False)
        self.assertNotIn("SEM009", rule_ids(semantic_checks.validate_semantics(design)))

    def test_the_multi_tenant_rules_are_satisfiable(self):
        design = multi_tenant_design()
        errors = [e for e in semantic_checks.validate_semantics(design) if e.get("ruleId") == "SEM009"]
        self.assertEqual(errors, [], "a tenant-scoped design must pass SEM009")

    def test_the_key_attributes_grid_puts_the_tenant_first(self):
        design = multi_tenant_design()
        attrs = [t for t in design["stages"]["tasks"]["items"] if t["kind"] != "task"]
        self.assertTrue(attrs, "the telecom design records key attributes")
        attrs[-1]["title"] = "Tenant scope"
        review = design_io.load_json(TELECOM / "review.json")
        document = design_html.render_html(design, review)
        grid = document[document.find("Key attributes"):]
        grid = grid[: grid.find("</table>")]
        rows = [r for r in grid.split("<tr") if "<td>" in r]
        self.assertIn("Tenant scope", rows[0], "the tenant row leads the grid")
        self.assertIn('class="tenant-row"', rows[0])

    def test_a_design_with_no_tenant_context_card_warns(self):
        warnings = design_io._profile_warnings(self.design)
        self.assertTrue(any("tenant" in w["message"] for w in warnings), warnings)


if __name__ == "__main__":
    unittest.main()
