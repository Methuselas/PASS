"""Tests for safe PASS project-snapshot import."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "workspace/tools/import_project_snapshot.py"
SPEC = importlib.util.spec_from_file_location("import_project_snapshot", TOOL)
assert SPEC and SPEC.loader
snapshot_import = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = snapshot_import
SPEC.loader.exec_module(snapshot_import)


def entry(path: str) -> snapshot_import.ArchiveEntry:
    info = zipfile.ZipInfo("PASS-project-art/" + path)
    return snapshot_import.ArchiveEntry(PurePosixPath(path), info)


class SnapshotArchiveInspectionTests(unittest.TestCase):
    def test_archive_requires_one_safe_stable_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            archive_path = Path(temp_dir) / "project.zip"
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr("PASS-project-art/PASS/SKILL.md", "skill")
                archive.writestr("PASS-project-art/library/metaskills/INDEX.md", "index")
                archive.writestr("PASS-project-art/library/art/card.md", "card")

            inspected = snapshot_import.inspect_archive(
                archive_path,
                max_file_bytes=1024,
                max_total_bytes=4096,
            )

            self.assertEqual(inspected.root_name, "PASS-project-art")
            self.assertEqual(snapshot_import.snapshot_domains(inspected), ["art"])

    def test_archive_rejects_parent_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            archive_path = Path(temp_dir) / "project.zip"
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr("PASS-project-art/../outside.txt", "no")

            with self.assertRaises(snapshot_import.SnapshotImportError):
                snapshot_import.inspect_archive(
                    archive_path,
                    max_file_bytes=1024,
                    max_total_bytes=4096,
                )


class SnapshotImportScopeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.repo = Path(self.temporary.name)
        skill = self.repo / ".agents/skills/visual-art/SKILL.md"
        skill.parent.mkdir(parents=True)
        skill.write_text("Use library/art/ cards.\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def make_snapshot(self) -> snapshot_import.SnapshotArchive:
        paths = (
            "CHANGELOG.md",
            "PASS/SKILL.md",
            "LICENSES/AGPL-3.0.txt",
            "README.md",
            "VERSION",
            "library/metaskills/INDEX.md",
            "library/art/card.md",
            "memory/art/skill_memory.yaml",
            "workspace/tools/helper.py",
            "workspace/release-recipes/SkillForge_Art.yaml",
            "workspace/release-recipes/SkillForge_Writing.yaml",
            "workspace/release-recipes/Legacy.yaml",
            "workspace/handoffs/ART_TRAINING_ENTRY.md",
            "workspace/handoffs/WRITING_TRAINING_ENTRY.md",
            ".agents/skills/visual-art/SKILL.md",
            ".agents/skills/writing/SKILL.md",
            "tests/test_example.py",
            "SOURCE_INPUT/unit.txt",
        )
        return snapshot_import.SnapshotArchive(
            "PASS-project-art", tuple(entry(path) for path in paths)
        )

    def test_default_scope_includes_domain_library_memory_handoffs_and_recipe(self) -> None:
        selected = snapshot_import.select_entries(
            self.make_snapshot(),
            self.repo,
            ["art"],
            all_project_files=False,
        )
        paths = {item.relative.as_posix() for item in selected}

        self.assertEqual(
            paths,
            {
                "library/art/card.md",
                "memory/art/skill_memory.yaml",
                "workspace/handoffs/ART_TRAINING_ENTRY.md",
                "workspace/release-recipes/SkillForge_Art.yaml",
            },
        )

    def test_all_project_scope_remains_bounded(self) -> None:
        selected = snapshot_import.select_entries(
            self.make_snapshot(),
            self.repo,
            ["art"],
            all_project_files=True,
        )
        paths = {item.relative.as_posix() for item in selected}

        self.assertIn("README.md", paths)
        self.assertIn("CHANGELOG.md", paths)
        self.assertIn("VERSION", paths)
        self.assertIn("LICENSES/AGPL-3.0.txt", paths)
        self.assertIn("PASS/SKILL.md", paths)
        self.assertIn("library/metaskills/INDEX.md", paths)
        self.assertIn("workspace/tools/helper.py", paths)
        self.assertIn("workspace/release-recipes/SkillForge_Art.yaml", paths)
        self.assertIn(".agents/skills/visual-art/SKILL.md", paths)
        self.assertIn("tests/test_example.py", paths)
        self.assertNotIn("workspace/release-recipes/Legacy.yaml", paths)
        self.assertNotIn(".agents/skills/writing/SKILL.md", paths)
        self.assertNotIn("workspace/handoffs/WRITING_TRAINING_ENTRY.md", paths)
        self.assertNotIn("SOURCE_INPUT/unit.txt", paths)


class SnapshotApplyTests(unittest.TestCase):
    def test_apply_adds_and_updates_without_deleting_other_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            repo = (temp / "repo").resolve()
            extracted = temp / "extracted"
            existing = repo / "library/art/existing.md"
            unrelated = repo / "library/art/local-only.md"
            incoming_existing = extracted / "library/art/existing.md"
            incoming_new = extracted / "library/art/new.md"
            for path, content in (
                (existing, "old\n"),
                (unrelated, "keep\n"),
                (incoming_existing, "updated\n"),
                (incoming_new, "new\n"),
            ):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
            entries = (
                entry("library/art/existing.md"),
                entry("library/art/new.md"),
            )

            plan = snapshot_import.plan_changes(extracted, repo, entries)
            snapshot_import.apply_changes(repo, plan)

            self.assertEqual([change.kind for change in plan.changes], ["UPDATE", "ADD"])
            self.assertEqual(existing.read_text(encoding="utf-8"), "updated\n")
            self.assertEqual(
                (repo / "library/art/new.md").read_text(encoding="utf-8"),
                "new\n",
            )
            self.assertEqual(unrelated.read_text(encoding="utf-8"), "keep\n")


if __name__ == "__main__":
    unittest.main()
