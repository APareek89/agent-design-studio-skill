"""The schema 1.1 authoring scaffold.

SEM000 is where weaker and smaller-context models burn rounds: the semantic
contract must cover every node, component and transition exactly. The
scaffold does that bookkeeping and leaves every business decision blank, and
a blank fails validation so an unfinished contract cannot be delivered as a
finished one.
"""

import copy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills/agent-design-studio/scripts"
TELECOM = ROOT / "examples/telecom/design.json"


def module(name, prefix="sc_"):
    spec = importlib.util.spec_from_file_location(prefix + name, SCRIPTS / (name + ".py"))
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


scaffold = module("design_scaffold")
design_io = module("design_io")
semantic_checks = module("semantic_checks")


def without_semantics():
    design = json.loads(TELECOM.read_text(encoding="utf-8"))
    design.pop("semantics", None)
    return design


class WhatItFills(unittest.TestCase):
    def setUp(self):
        self.design = without_semantics()
        self.result = scaffold.scaffold(self.design)
        self.semantics = self.result["semantics"]
        self.authored = json.loads(TELECOM.read_text(encoding="utf-8"))["semantics"]

    def test_it_covers_every_node_component_and_transition(self):
        workflow = {w["id"] for w in self.design["stages"]["workflow"]["items"]}
        components = {c["id"] for c in self.design["stages"]["components"]["items"]}
        self.assertEqual({n["id"] for n in self.semantics["nodes"]}, workflow)
        self.assertEqual({e["componentId"] for e in self.semantics["componentEffects"]}, components)
        edges = {(w["id"], n) for w in self.design["stages"]["workflow"]["items"]
                 for n in w["data"]["next"] if n in workflow}
        self.assertEqual({(t["from"], t["to"]) for t in self.semantics["transitions"]}, edges)

    def test_it_finds_the_same_entrypoints_as_the_authored_contract(self):
        self.assertEqual(self.semantics["entrypoints"], self.authored["entrypoints"])

    def test_it_copies_transition_conditions_verbatim(self):
        authored = {(t["from"], t["to"]): t["when"] for t in self.authored["transitions"]}
        for row in self.semantics["transitions"]:
            key = (row["from"], row["to"])
            if key in authored:
                self.assertEqual(row["when"], authored[key], key)

    def test_it_lists_every_llm_output_field(self):
        self.assertEqual(
            {(m["componentId"], m["field"]) for m in self.semantics["modelOutputs"]},
            {(m["componentId"], m["field"]) for m in self.authored["modelOutputs"]})

    def test_it_takes_binding_field_names_from_the_components_inputs(self):
        by_id = {n["id"]: n for n in self.semantics["nodes"] if "bindings" in n}
        self.assertTrue(by_id, "tool nodes get a binding skeleton")
        components = {c["id"]: c for c in self.design["stages"]["components"]["items"]}
        workflow = {w["id"]: w for w in self.design["stages"]["workflow"]["items"]}
        for nid, node in by_id.items():
            expected = {scaffold.field_name(d)
                        for d in components[workflow[nid]["data"]["componentId"]]["data"]["inputs"]}
            self.assertEqual({b["field"] for b in node["bindings"]}, expected, nid)


class WhatItRefusesToGuess(unittest.TestCase):
    def setUp(self):
        self.result = scaffold.scaffold(without_semantics())
        self.semantics = self.result["semantics"]

    def test_no_transition_outcome_is_invented(self):
        self.assertTrue(self.semantics["transitions"])
        for row in self.semantics["transitions"]:
            self.assertEqual(row["outcome"], "TODO")

    def test_no_model_output_category_is_invented(self):
        for row in self.semantics["modelOutputs"]:
            self.assertEqual(row["category"], "TODO")

    def test_no_binding_source_or_category_is_invented(self):
        for node in self.semantics["nodes"]:
            for binding in node.get("bindings", []):
                self.assertEqual(binding["source"], "TODO")
                self.assertEqual(binding["category"], "TODO")

    def test_no_write_action_and_no_golden_is_invented(self):
        self.assertEqual(self.semantics["writeActions"], [])
        self.assertEqual(self.semantics["goldens"], [])

    def test_a_human_wait_gets_no_guessed_duration(self):
        waits = [n for n in self.semantics["nodes"] if n["kind"] == "human_wait"]
        self.assertTrue(waits)
        for node in waits:
            self.assertIsNone(node["waitHours"])

    def test_the_checklist_names_every_kind_of_blank(self):
        text = " ".join(self.result["todo"])
        for phrase in ("outcome", "Categorise", "actionClass", "waitHours", "goldens"):
            self.assertIn(phrase, text)


class BlanksFailValidation(unittest.TestCase):
    def test_a_merged_scaffold_does_not_validate(self):
        design = without_semantics()
        design["semantics"] = scaffold.scaffold(design)["semantics"]
        result = design_io.validate_design(design)
        self.assertFalse(result["valid"])
        self.assertEqual(result["semanticCoverage"], "failed")

    def test_the_error_names_the_scaffold_rather_than_a_stray_key(self):
        design = without_semantics()
        design["semantics"] = scaffold.scaffold(design)["semantics"]
        errors = semantic_checks.validate_semantics(design)
        self.assertTrue(any("scaffold blanks" in e["message"] for e in errors), errors)
        self.assertTrue(any("design_scaffold.py" in e["message"] for e in errors))

    def test_a_finished_contract_gets_the_ordinary_message(self):
        design = json.loads(TELECOM.read_text(encoding="utf-8"))
        design["semantics"]["nodes"][0]["kind"] = 42
        errors = semantic_checks.validate_semantics(design)
        self.assertTrue(any("Malformed semantic row" in e["message"] for e in errors), errors)
        self.assertFalse(any("scaffold blanks" in e["message"] for e in errors))


class CommandLine(unittest.TestCase):
    def setUp(self):
        self.folder = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.folder, True)
        self.path = self.folder / "design.json"
        self.path.write_text(json.dumps(without_semantics()), encoding="utf-8")

    def run_it(self, *args):
        return subprocess.run([sys.executable, "-I", str(SCRIPTS / "design_scaffold.py"), str(self.path)] + list(args),
                              capture_output=True, text=True)

    def test_it_prints_a_scaffold(self):
        done = self.run_it()
        self.assertEqual(done.returncode, 0, done.stderr)
        payload = json.loads(done.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["filled"]["nodes"], 13)

    def test_merge_writes_the_block_into_the_design(self):
        self.assertEqual(self.run_it("--merge").returncode, 0)
        self.assertIn("semantics", json.loads(self.path.read_text(encoding="utf-8")))

    def test_merge_refuses_to_discard_an_authored_contract(self):
        self.path.write_text(TELECOM.read_text(encoding="utf-8"), encoding="utf-8")
        done = self.run_it("--merge")
        self.assertEqual(done.returncode, 1)
        self.assertIn("already has a semantics block", done.stderr)

    def test_it_refuses_before_the_components_stage_is_filled(self):
        design = without_semantics()
        design["stages"]["components"]["items"] = []
        self.path.write_text(json.dumps(design), encoding="utf-8")
        done = self.run_it()
        self.assertEqual(done.returncode, 1)
        self.assertIn("Fill the components stage", done.stderr)


if __name__ == "__main__":
    unittest.main()
