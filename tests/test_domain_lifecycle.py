"""A new domain originates in a project and enters only by explicit authorization;
a module may ship a declared, tested runtime and nothing else executable."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "workspace/tools/build_project_snapshot.py"
IMPORT = ROOT / "workspace/tools/import_project_snapshot.py"
sys.path.insert(0, str(ROOT / "PASS" / "tools"))
from module_runtime import runtime_problems  # noqa: E402

DOMAIN = "lifecycle-probe"


def run(*args: object) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, *map(str, args)], capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def zip_tree(tree: Path, output: Path, root_name: str) -> None:
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(tree.rglob("*")):
            if path.is_file():
                archive.write(path, (Path(root_name) / path.relative_to(tree)).as_posix())


class NewDomainLifecycleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.temp = Path(self.temporary.name)
        self.project = self.temp / f"PASS-project-{DOMAIN}"
        built = run(BUILD, self.project, "--new-domain", DOMAIN)
        self.assertEqual(built.returncode, 0, built.stderr)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def finish_domain(self) -> None:
        for path in [self.project / f"workspace/release-recipes/SkillForge_Lifecycle_Probe.yaml",
                     *(self.project / host / "skills" / DOMAIN / "SKILL.md" for host in (".claude", ".agents"))]:
            path.write_text(path.read_text(encoding="utf-8").replace("before import", "when probing"),
                            encoding="utf-8")

    def archive(self) -> Path:
        output = self.temp / f"PASS-project-{DOMAIN}.zip"
        output.unlink(missing_ok=True)
        zip_tree(self.project, output, self.project.name)
        return output

    def test_bootstrap_is_a_valid_project_for_a_domain_that_does_not_exist(self) -> None:
        for relative in (f"library/{DOMAIN}/foundations/MODULE.yaml",
                         f".claude/skills/{DOMAIN}/SKILL.md", f".agents/skills/{DOMAIN}/SKILL.md",
                         "workspace/release-recipes/SkillForge_Lifecycle_Probe.yaml",
                         "workspace/handoffs/LIFECYCLE_PROBE_NEW_DOMAIN.md", "PASS/SKILL.md"):
            self.assertTrue((self.project / relative).is_file(), relative)
        self.assertFalse((self.project / "library/writing").exists())
        checked = run(ROOT / "PASS/tools/validate.py", "--library", self.project / "library")
        self.assertEqual(checked.returncode, 0, checked.stdout)
        self.assertNotEqual(run(BUILD, self.temp / "again", "--new-domain", "writing").returncode, 0)
        self.assertNotEqual(run(BUILD, self.temp / "bad", "--new-domain", "Bad_Name").returncode, 0)

    def test_an_archive_cannot_create_a_domain_without_explicit_authorization(self) -> None:
        self.finish_domain()
        archive = self.archive()
        refused = run(IMPORT, archive)
        self.assertEqual(refused.returncode, 1)
        self.assertIn("--create-domain", refused.stderr)
        self.assertIn("already exists", run(IMPORT, archive, "--create-domain", "writing").stderr)
        planned = run(IMPORT, archive, "--create-domain", DOMAIN)  # dry run: writes nothing
        self.assertEqual(planned.returncode, 0, planned.stderr)
        self.assertIn(f"ADD    .claude/skills/{DOMAIN}/SKILL.md", planned.stdout)
        self.assertIn(f"ADD    library/{DOMAIN}/foundations/MODULE.yaml", planned.stdout)
        self.assertFalse((ROOT / "library" / DOMAIN).exists())

    def test_placeholders_and_foreign_card_ids_are_refused(self) -> None:
        self.assertIn("placeholder", run(IMPORT, self.archive(), "--create-domain", DOMAIN).stderr)
        self.finish_domain()
        existing = next((ROOT / "library/writing").rglob("PAT_*.md"))
        copy = self.project / f"library/{DOMAIN}/foundations" / existing.name
        copy.write_text(existing.read_text(encoding="utf-8"), encoding="utf-8")
        refused = run(IMPORT, self.archive(), "--create-domain", DOMAIN)
        self.assertEqual(refused.returncode, 1)
        self.assertIn("duplicates", refused.stderr)


class ModuleRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.library = Path(self.temporary.name) / "library"
        self.module = self.library / "probe" / "tools"
        (self.module / "runtime" / "tests").mkdir(parents=True)
        (self.module / "runtime" / "tool.py").write_text("import json\nimport helper\n", encoding="utf-8")
        (self.module / "runtime" / "helper.py").write_text("import os\n", encoding="utf-8")
        (self.module / "runtime" / "tests" / "test_tool.py").write_text("import unittest\n", encoding="utf-8")
        self.manifest("runtime:\n  entrypoints:\n    - runtime/tool.py\n  tests: runtime/tests\n")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def manifest(self, runtime: str) -> None:
        (self.module / "MODULE.yaml").write_text(f"name: probe/tools\nrequires: []\n{runtime}", encoding="utf-8")

    def problems(self) -> list[str]:
        return [text for _module, text in runtime_problems(self.library)]

    def test_declared_standard_library_runtime_passes(self) -> None:
        self.assertEqual(self.problems(), [])

    def test_undeclared_or_misplaced_code_fails(self) -> None:
        (self.library / "probe" / "stray.py").write_text("", encoding="utf-8")
        self.assertTrue(any("stray.py" in p for p in self.problems()))
        self.manifest("")
        self.assertTrue(any("runtime/tool.py" in p for p in self.problems()))

    def test_runtime_contract_is_enforced(self) -> None:
        (self.module / "runtime" / "tool.py").write_text("import requests\n", encoding="utf-8")
        (self.module / "runtime" / "GUIDE.md").write_text("# not a card\n", encoding="utf-8")
        found = self.problems()
        self.assertTrue(any("requests" in p for p in found))
        self.assertTrue(any("GUIDE.md" in p for p in found))
        self.manifest("runtime:\n  entrypoints:\n    - runtime/tool.py\n")
        self.assertTrue(any("must declare its tests" in p for p in self.problems()))
        self.manifest("runtime:\n  entrypoints:\n    - ../escape.py\n  tests: runtime/tests\n")
        self.assertTrue(any("under runtime/" in p for p in self.problems()))


if __name__ == "__main__":
    unittest.main()
