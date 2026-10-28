import importlib.util
import json
from pathlib import Path
import re
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/agent-design-studio"


class PackageTests(unittest.TestCase):
    def test_manifests_agree_and_require_no_connection(self):
        root = json.loads((ROOT / "plugin.json").read_text())
        compat = json.loads((ROOT / ".codex-plugin/plugin.json").read_text())
        for field in ["name", "version", "repository", "license"]:
            self.assertEqual(root[field], compat[field])
        self.assertEqual(compat["skills"], "./skills/")
        self.assertEqual(
            compat["interface"], root["extensions"]["com.openai"]["interface"]
        )
        self.assertNotIn("mcpServers", compat)
        self.assertFalse((ROOT / "mcp.json").exists())
        self.assertFalse((ROOT / ".mcp.json").exists())

    def test_skill_links_resolve_inside_package(self):
        content = (SKILL / "SKILL.md").read_text()
        self.assertTrue(content.startswith("---\nname: agent-design-studio\n"))
        for target in re.findall(r"\]\(([^)]+)\)", content):
            if "://" in target:
                continue
            resource = (SKILL / target).resolve()
            self.assertTrue(resource.is_relative_to(SKILL))
            self.assertTrue(resource.is_file(), target)

    def test_all_ten_stage_schemas_are_self_contained(self):
        schemas = json.loads((SKILL / "references/stage-schemas.json").read_text())
        self.assertEqual(
            set(schemas),
            {
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
            },
        )
        self.assertNotIn('"$ref"', json.dumps(schemas))
        self.assertEqual(schemas["models"]["properties"]["items"].get("minItems", 0), 0)
        self.assertEqual(schemas["tasks"]["properties"]["items"]["minItems"], 1)

    def test_distribution_is_self_contained_and_excludes_generated_work(self):
        spec = importlib.util.spec_from_file_location(
            "package_plugin", ROOT / "scripts/package_plugin.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as temp:
            archive = module.package(temp)
            with zipfile.ZipFile(archive) as z:
                names = z.namelist()
                prefix = "agent-design-studio/"
                for file in [
                    "plugin.json",
                    ".codex-plugin/plugin.json",
                    "LICENSE",
                    "README.md",
                    "skills/agent-design-studio/SKILL.md",
                    "skills/agent-design-studio/scripts/design_io.py",
                    "skills/agent-design-studio/scripts/design_pdf.py",
                    "skills/agent-design-studio/scripts/design_html.py",
                    "skills/agent-design-studio/requirements-pdf.txt",
                    "skills/agent-design-studio/references/stage-schemas.json",
                ]:
                    self.assertIn(prefix + file, names)
                self.assertFalse(
                    any(
                        ".." in Path(n).parts
                        or "__pycache__" in n
                        or "/evals/" in n
                        or "/tests/" in n
                        for n in names
                    )
                )
                self.assertTrue(Path(str(archive) + ".sha256").is_file())


if __name__ == "__main__":
    unittest.main()
