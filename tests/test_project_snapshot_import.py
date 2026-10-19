"""Tests for safe PASS project-snapshot import."""

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path, PurePosixPath

import yaml


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "workspace/tools/import_project_snapshot.py"
SPEC = importlib.util.spec_from_file_location("import_project_snapshot", TOOL)
assert SPEC and SPEC.loader
snapshot_import = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = snapshot_import
SPEC.loader.exec_module(snapshot_import)

BUILD_TOOL = ROOT / "workspace/tools/build_project_snapshot.py"
BUILD_SPEC = importlib.util.spec_from_file_location("build_project_snapshot", BUILD_TOOL)
assert BUILD_SPEC and BUILD_SPEC.loader
snapshot_build = importlib.util.module_from_spec(BUILD_SPEC)
sys.modules[BUILD_SPEC.name] = snapshot_build
BUILD_SPEC.loader.exec_module(snapshot_build)


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


def write_v3_game_design_memory(memory_root: Path) -> bytes:
    """A schema-3 game-design store plus its History; returns the store bytes.

    The claims mirror the projection fixture's faces (one cited event, one
    claim with no evidence key, a `canon` reference) so the round trip proves
    every projected-away field survives a snapshot export and import intact.
    """
    def claim_id(n: int) -> str:
        return "GD_MEM_" + str(n).rjust(26, "0")

    claims = [
        {
            "id": claim_id(1),
            "claim": (
                "A countdown timer changes player decision quality only when the "
                "cost of waiting is visible."
            ),
            "claim_class": "conduct",
            "claim_kind": "deterministic",
            "confidence": "repeated",
            "delta": {
                "kinds": ["action"],
                "statement": "Show the cost of waiting beside the timer.",
            },
            "envelope": {
                "holds_in": ["timed resource decisions"],
                "not_shown_in": ["real-time action beats"],
            },
            "provenance": ["runtime_self_audit"],
            "scope": "timer_cost_legibility",
            "retrieval_cues": ["countdown timer cost"],
            "last_verified": "2026-10-18",
            "evidence": ["GAMEDESIGN_EV_0001"],
        },
        {
            "id": claim_id(2),
            "claim": (
                "Telegraphing an adversary's next action through posture gives "
                "the player a fair read."
            ),
            "claim_class": "conduct",
            "claim_kind": "stochastic",
            "confidence": "provisional",
            "delta": {
                "kinds": ["judgment"],
                "statement": "Telegraph intent in posture before the action.",
            },
            "envelope": {
                "holds_in": ["human-readable adversaries"],
                "not_shown_in": ["stealth detection meters"],
            },
            "provenance": ["human_teaching"],
            "scope": "adversary_telegraphing",
            "retrieval_cues": ["telegraph adversary intent"],
            "last_verified": "2026-10-15",
            "canon": ["PAT_build_gesture_into_clear_masses"],
        },
    ]
    store = {
        "memory_schema_version": 3,
        "skillset": "game-design",
        "memory_version": 1,
        "claims": claims,
    }
    events = [
        {
            "event_id": "GAMEDESIGN_EV_0001",
            "date": "2026-10-18",
            "task": "Playtest a countdown-timer resource decision",
            "validity": "valid",
        },
    ]
    domain = memory_root / "game-design"
    domain.mkdir(parents=True, exist_ok=True)
    store_bytes = yaml.safe_dump(
        store, sort_keys=False, allow_unicode=True, width=88
    ).encode("utf-8")
    (domain / "skill_memory.yaml").write_bytes(store_bytes)
    with (domain / "training_history.jsonl").open("w", encoding="utf-8", newline="\n") as handle:
        for event in events:
            handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
    return store_bytes


class V3MemoryRoundTripTests(unittest.TestCase):
    """T09: a project snapshot is NOT a projection.

    A SkillForge *release* projects a v3 store to current state; a *project
    snapshot* round-trips the full writable store — `training_history.jsonl`
    and claim-level `evidence` included — and its import gate validates
    exactly those shipped bytes (R2.5 §8.5).
    """

    def test_a_v3_memory_store_round_trips_and_validates(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            source = temp / "source"
            (source / "PASS").mkdir(parents=True)
            (source / "PASS/SKILL.md").write_text("# Skill\n", encoding="utf-8")
            shutil.copytree(ROOT / "library/metaskills", source / "library/metaskills")
            shutil.copytree(ROOT / "library/game-design", source / "library/game-design")
            (source / "workspace/release-recipes").mkdir(parents=True)
            shutil.copy2(
                ROOT / "workspace/release-recipes/SkillForge_Game_Design.yaml",
                source / "workspace/release-recipes/SkillForge_Game_Design.yaml",
            )
            store_bytes = write_v3_game_design_memory(source / "memory")

            files = snapshot_build.collect_snapshot_files(source, ["game-design"])
            archive = temp / "PASS-project-game-design.zip"
            snapshot_build.write_snapshot_archive(
                archive, source, "PASS-project-game-design", files, []
            )

            # Export is not a projection: the archive carries the full store.
            with zipfile.ZipFile(archive) as zipped:
                self.assertEqual(
                    zipped.read(
                        "PASS-project-game-design/memory/game-design/skill_memory.yaml"
                    ),
                    store_bytes,
                )
                history = zipped.read(
                    "PASS-project-game-design/memory/game-design/training_history.jsonl"
                )
            self.assertIn(b"GAMEDESIGN_EV_0001", history)

            # Destination repo: PASS tools plus the same two packages, no memory yet.
            dest = temp / "dest"
            shutil.copytree(
                ROOT / "PASS",
                dest / "PASS",
                ignore=shutil.ignore_patterns("__pycache__"),
            )
            (dest / "library").mkdir(parents=True)
            shutil.copytree(ROOT / "library/metaskills", dest / "library/metaskills")
            shutil.copytree(ROOT / "library/game-design", dest / "library/game-design")

            result = subprocess.run(
                [
                    sys.executable, str(TOOL), str(archive),
                    "--repo", str(dest), "--apply",
                ],
                text=True, encoding="utf-8", capture_output=True, cwd=temp,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("validated skillset memory", result.stdout)
            self.assertIn("ADD    memory/game-design/skill_memory.yaml", result.stdout)
            landed = dest / "memory/game-design/skill_memory.yaml"
            self.assertEqual(landed.read_bytes(), store_bytes)
            landed_history = dest / "memory/game-design/training_history.jsonl"
            self.assertTrue(landed_history.is_file())
            self.assertEqual(landed_history.read_bytes(), history)


if __name__ == "__main__":
    unittest.main()
