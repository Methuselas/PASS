"""Tests for the pruned Project-chat snapshot builder."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "workspace/tools/build_project_snapshot.py"
SPEC = importlib.util.spec_from_file_location("build_project_snapshot", TOOL)
assert SPEC and SPEC.loader
snapshot = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(snapshot)


class SnapshotSelectionTests(unittest.TestCase):
    def test_domain_snapshot_includes_only_selected_canon_and_default_metaskills(self) -> None:
        files = snapshot.collect_snapshot_files(ROOT, ["game-design"])
        relative = {path.relative_to(ROOT).as_posix() for path in files}

        self.assertIn("PASS/SKILL.md", relative)
        self.assertIn("library/metaskills/INDEX.md", relative)
        self.assertIn("library/game-design/INDEX.md", relative)
        self.assertIn("memory/game-design/skill_memory.yaml", relative)
        self.assertIn(".claude/skills/game-design/SKILL.md", relative)
        self.assertIn(".agents/skills/game-design/SKILL.md", relative)
        self.assertFalse(any(path.startswith("library/art/") for path in relative))
        self.assertFalse(any(path.startswith("library/writing/") for path in relative))

    def test_art_snapshot_discovers_visual_art_host_skills(self) -> None:
        files = snapshot.collect_snapshot_files(ROOT, ["art"])
        relative = {path.relative_to(ROOT).as_posix() for path in files}

        self.assertIn(".claude/skills/visual-art/SKILL.md", relative)
        self.assertIn(".agents/skills/visual-art/SKILL.md", relative)
        self.assertIn("docs/ART_HELP.md", relative)
        self.assertNotIn(".claude/skills/game-design/SKILL.md", relative)
        self.assertNotIn(".agents/skills/game-design/SKILL.md", relative)

    def test_snapshot_includes_reusable_workspace_tools_without_cache(self) -> None:
        files = snapshot.collect_snapshot_files(ROOT, ["art"])
        relative = {path.relative_to(ROOT).as_posix() for path in files}

        self.assertIn("workspace/tools/extract_pdf_text.py", relative)
        self.assertIn("workspace/tools/build_project_snapshot.py", relative)
        self.assertIn("workspace/tools/import_project_snapshot.py", relative)
        self.assertFalse(any("/__pycache__/" in path for path in relative))
        self.assertFalse(any(path.casefold().endswith(".pyc") for path in relative))
        self.assertFalse(any(path.startswith("workspace/authoring/") for path in relative))
        self.assertFalse(any(path.startswith("workspace/releases/") for path in relative))

    def test_snapshot_selection_excludes_sources_archives_and_pdf_files(self) -> None:
        files = snapshot.collect_snapshot_files(ROOT, ["software-engineering"])
        relative = {path.relative_to(ROOT).as_posix() for path in files}

        self.assertFalse(any("workspace/sources" in path for path in relative))
        self.assertFalse(any(path.startswith("archive/") for path in relative))
        self.assertFalse(any(path.casefold().endswith((".pdf", ".zip")) for path in relative))

    def test_include_recipes_keeps_only_canonical_skillforge_recipes(self) -> None:
        files = snapshot.collect_snapshot_files(
            ROOT, ["art"], include_recipes=True
        )
        recipes = {
            path.relative_to(ROOT).as_posix()
            for path in files
            if path.relative_to(ROOT).as_posix().startswith(
                "workspace/release-recipes/"
            )
        }

        self.assertIn(
            "workspace/release-recipes/SkillForge_Art.yaml", recipes
        )
        self.assertNotIn(
            "workspace/release-recipes/Animal_Anatomy.yaml", recipes
        )
        self.assertTrue(
            all(
                Path(path).name.startswith("SkillForge_")
                and Path(path).suffix == ".yaml"
                for path in recipes
            )
        )

    def test_written_snapshot_has_one_stable_root_and_no_other_domain(self) -> None:
        files = snapshot.collect_snapshot_files(ROOT, ["game-design"])
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "snapshot.zip"
            root_name = "PASS-project-game-design"
            with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                for path in files:
                    relative = path.relative_to(ROOT)
                    archive.write(path, (Path(root_name) / relative).as_posix())

            with zipfile.ZipFile(output) as archive:
                names = archive.namelist()
            self.assertTrue(names)
            self.assertTrue(all(name.startswith(root_name + "/") for name in names))
            self.assertFalse(any("/library/art/" in name for name in names))

    def test_explicit_source_text_gets_a_flat_visible_archive_path(self) -> None:
        path = Path("C:/outside/a-book.txt")
        self.assertEqual(
            snapshot.source_input_name("PASS-project-writing", path),
            "PASS-project-writing/SOURCE_INPUT/a-book.txt",
        )

    def test_project_directory_is_materialized_as_the_project_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            repo = temp / "repo"
            project = temp / "PASS-project-art"
            source = repo / "library/art/card.md"
            source.parent.mkdir(parents=True)
            source.write_text("card\n", encoding="utf-8")
            source_input = temp / "unit.txt"
            source_input.write_text("source\n", encoding="utf-8")
            expected_bytes = source.stat().st_size + source_input.stat().st_size

            total = snapshot.write_snapshot_directory(
                project, repo, [source], [source_input]
            )

            self.assertEqual(
                (project / "library/art/card.md").read_text(encoding="utf-8"),
                "card\n",
            )
            self.assertEqual(
                (project / "SOURCE_INPUT/unit.txt").read_text(encoding="utf-8"),
                "source\n",
            )
            self.assertEqual(total, expected_bytes)


if __name__ == "__main__":
    unittest.main()
