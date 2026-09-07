"""Contracts for the generic SkillForge Drill administrator."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_PATH = ROOT / "PASS" / "runtime" / "skillforge_drill.py"
SPEC = importlib.util.spec_from_file_location("skillforge_drill", RUNTIME_PATH)
assert SPEC and SPEC.loader
drill = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = drill
SPEC.loader.exec_module(drill)

TOOLS = ROOT / "PASS" / "tools"
sys.path.insert(0, str(TOOLS))
MEMORY_SPEC = importlib.util.spec_from_file_location("skillforge_memory", TOOLS / "memory.py")
assert MEMORY_SPEC and MEMORY_SPEC.loader
memory = importlib.util.module_from_spec(MEMORY_SPEC)
sys.modules[MEMORY_SPEC.name] = memory
MEMORY_SPEC.loader.exec_module(memory)

LIBRARY = ROOT / "library"
GD_DRILL = "DRILL_stress_test_the_core_resolution_grammar"
SE_DRILL = "DRILL_fix_templatized_base_class_name_access"


class SkillForgeDrillTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.scenario = self.root / "scenario.md"
        self.scenario.write_text(
            "# Novel case\n\nResolve the supplied concrete case and record the evidence.\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def prepare(self, cut: str = "before-instructions", *ids: str) -> Path:
        run = self.root / f"run-{len(list(self.root.glob('run-*')))}"
        drill.prepare(LIBRARY, ids or (GD_DRILL,), cut, self.scenario, run)
        return run

    def complete_grade(self, run: Path) -> None:
        grade_path = run / "grader" / "grade.json"
        grade = json.loads(grade_path.read_text(encoding="utf-8"))
        grade.update(
            {
                "validity": "valid",
                "grader_relation": "separate",
                "artifact_quality": "adequate",
                "process_validity": "strong",
                "skill_attribution": "adequate",
                "observations": ["The frozen answer exercised the target capability."],
            }
        )
        for item in grade["drills"]:
            item["overall"] = "pass"
            for criterion in item["criteria"]:
                criterion["result"] = "pass"
                criterion["evidence"] = "Present in the frozen answer."
        grade_path.write_text(json.dumps(grade), encoding="utf-8")

    def test_discovers_current_game_design_and_software_drills(self) -> None:
        self.assertEqual(len(drill.discover(LIBRARY, "game-design")), 14)
        self.assertEqual(len(drill.discover(LIBRARY, "software-engineering")), 71)

    def test_before_instructions_cut_hides_all_answer_bearing_sections(self) -> None:
        run = self.prepare()
        task = (run / "student" / "task.md").read_text(encoding="utf-8")
        key = (run / "controller" / "key.md").read_text(encoding="utf-8")
        self.assertNotIn("## Instructions", task)
        self.assertNotIn("## Success Check", task)
        self.assertNotIn("## Common Failures", task)
        self.assertIn("## Instructions", key)
        self.assertIn("## Success Check", key)
        self.assertFalse((run / "grader").exists())

    def test_before_success_check_cut_exposes_instructions_only(self) -> None:
        run = self.prepare("before-success-check")
        task = (run / "student" / "task.md").read_text(encoding="utf-8")
        self.assertIn("## Instructions", task)
        self.assertNotIn("## Success Check", task)
        self.assertNotIn("## Common Failures", task)

    def test_reveal_before_freeze_fails_closed(self) -> None:
        run = self.prepare()
        with self.assertRaises(drill.DrillError):
            drill.reveal(run)
        self.assertFalse((run / "grader").exists())

    def test_freeze_then_reveal_materializes_complete_grader_template(self) -> None:
        run = self.prepare()
        (run / "student" / "answer.md").write_text("Produced evidence.", encoding="utf-8")
        drill.freeze(run)
        drill.reveal(run)
        grade = json.loads((run / "grader" / "grade.json").read_text(encoding="utf-8"))
        rubric = json.loads(
            (run / "controller" / "rubric.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            [item["criterion"] for item in grade["drills"][0]["criteria"]],
            rubric["drills"][0]["criteria"],
        )
        self.assertEqual(drill.load_run(run)[1]["state"], "revealed")

    def test_answer_mutation_after_freeze_invalidates_the_run(self) -> None:
        run = self.prepare()
        answer = run / "student" / "answer.md"
        answer.write_text("Frozen evidence.", encoding="utf-8")
        drill.freeze(run)
        answer.write_text("Changed after freeze.", encoding="utf-8")
        with self.assertRaises(drill.DrillError):
            drill.reveal(run)
        state = drill.load_run(run)[1]
        self.assertEqual(state["state"], "invalidated")
        self.assertIn("changed after freeze", state["invalid_reason"])
        self.assertFalse((run / "grader").exists())

    def test_chain_preserves_independent_rubrics(self) -> None:
        second = "DRILL_profile_a_randomizer_before_committing_to_it"
        run = self.prepare("before-success-check", GD_DRILL, second)
        rubric = json.loads(
            (run / "controller" / "rubric.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            [item["drill_id"] for item in rubric["drills"]], [GD_DRILL, second]
        )
        self.assertTrue(all(item["criteria"] for item in rubric["drills"]))

    def test_finalize_exports_valid_candidate_without_writing_memory(self) -> None:
        run = self.prepare()
        answer = run / "student" / "answer.md"
        answer.write_text("Produced evidence.", encoding="utf-8")
        drill.freeze(run)
        drill.reveal(run)
        self.complete_grade(run)
        event = drill.finalize(
            run,
            "GAMEDESIGN_EV_9999",
            "Execute a novel core-resolution-grammar case.",
            "2026-09-07",
        )
        self.assertEqual(event["validity"], "valid")
        self.assertNotIn("hash", json.dumps(event).lower())
        self.assertNotIn("run-", json.dumps(event).lower())
        self.assertTrue((run / "candidate_training_event.json").is_file())
        self.assertEqual(drill.load_run(run)[1]["state"], "finalized")
        errors: list[str] = []
        memory.validate_event(event, 0, errors)
        self.assertEqual(errors, [])

    def test_software_engineering_uses_the_identical_lifecycle(self) -> None:
        run = self.prepare("before-success-check", SE_DRILL)
        (run / "student" / "answer.md").write_text(
            "Produced source, compiler transcript, and negative-case evidence.",
            encoding="utf-8",
        )
        drill.freeze(run)
        drill.reveal(run)
        self.complete_grade(run)
        event = drill.finalize(
            run,
            "SOFTWAREENGINEERING_EV_9999",
            "Resolve a dependent base-class name and exercise a negative case.",
            "2026-09-07",
        )
        self.assertEqual(event["validity"], "valid")
        self.assertEqual(drill.load_run(run)[1]["domain"], "software-engineering")

    def test_freeze_rejects_the_student_packet_itself(self) -> None:
        run = self.prepare()
        (run / "student" / "answer.md").write_text("Evidence.", encoding="utf-8")
        with self.assertRaises(drill.DrillError):
            drill.freeze(run, run / "student")

    def test_incomplete_grade_cannot_finalize(self) -> None:
        run = self.prepare()
        (run / "student" / "answer.md").write_text("Evidence.", encoding="utf-8")
        drill.freeze(run)
        drill.reveal(run)
        with self.assertRaises(drill.DrillError):
            drill.finalize(run, "GAMEDESIGN_EV_9999", "Execute a novel case.")

    def test_explicit_invalidation_exports_invalid_history_candidate(self) -> None:
        run = self.prepare()
        drill.invalidate(run, "controller exposed the answer key")
        event = drill.finalize(
            run, "GAMEDESIGN_EV_9999", "Attempt a novel case.", "2026-09-07"
        )
        self.assertEqual(event["validity"], "invalid")
        self.assertEqual(event["invalid_reason"], "controller exposed the answer key")

    def test_cross_domain_chain_is_rejected(self) -> None:
        with self.assertRaises(drill.DrillError):
            drill.prepare(
                LIBRARY,
                (GD_DRILL, SE_DRILL),
                "before-instructions",
                self.scenario,
                self.root / "cross-domain",
            )

    def test_drill_capable_release_vendors_and_runs_the_same_helper(self) -> None:
        release = self.root / "release"
        recipe = ROOT / "workspace" / "release-recipes" / "SkillForge_Game_Design.yaml"
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "PASS" / "tools" / "build_release.py"),
                "build",
                str(recipe),
                str(release),
                "--library",
                str(LIBRARY),
            ],
            text=True,
            capture_output=True,
            cwd=ROOT,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        runner = release / "scripts" / "skillforge_drill.py"
        self.assertTrue(runner.is_file())
        listing = subprocess.run(
            [sys.executable, str(runner), "list", "--domain", "game-design", "--format", "json"],
            text=True,
            capture_output=True,
            cwd=release,
        )
        self.assertEqual(listing.returncode, 0, listing.stdout + listing.stderr)
        self.assertEqual(len(json.loads(listing.stdout)), 14)
        skill = (release / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("model-neutral", skill)
        self.assertIn("candidate_training_event.json", skill)
        released_run = self.root / "released-run"
        commands = [
            [
                sys.executable,
                str(runner),
                "prepare",
                "--drill",
                GD_DRILL,
                "--cut",
                "before-instructions",
                "--scenario",
                str(self.scenario),
                "--out",
                str(released_run),
            ],
            [sys.executable, str(runner), "freeze", "--run", str(released_run)],
            [sys.executable, str(runner), "reveal", "--run", str(released_run)],
        ]
        for command in commands[:1]:
            completed = subprocess.run(command, text=True, capture_output=True, cwd=release)
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        (released_run / "student" / "answer.md").write_text(
            "Produced release-local evidence.", encoding="utf-8"
        )
        for command in commands[1:]:
            completed = subprocess.run(command, text=True, capture_output=True, cwd=release)
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.complete_grade(released_run)
        completed = subprocess.run(
            [
                sys.executable,
                str(runner),
                "finalize",
                "--run",
                str(released_run),
                "--event-id",
                "GAMEDESIGN_EV_9998",
                "--task",
                "Execute a release-local novel game-design case.",
                "--date",
                "2026-09-07",
            ],
            text=True,
            capture_output=True,
            cwd=release,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertTrue((released_run / "candidate_training_event.json").is_file())

    def test_release_without_drills_does_not_carry_the_runner(self) -> None:
        recipe = self.root / "metaskills-only.yaml"
        recipe.write_text(
            "name: Metaskills Only\n"
            "skill_name: metaskills-only\n"
            "description: Test release without Drill objects.\n"
            "modules:\n  - metaskills\n"
            "runtime_profile: generic\n",
            encoding="utf-8",
        )
        with tempfile.TemporaryDirectory() as release_parent:
            release = Path(release_parent) / "metaskills-release"
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "PASS" / "tools" / "build_release.py"),
                    "build",
                    str(recipe),
                    str(release),
                    "--library",
                    str(LIBRARY),
                ],
                text=True,
                capture_output=True,
                cwd=ROOT,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertFalse((release / "scripts" / "skillforge_drill.py").exists())
            manifest = json.loads(
                (release / "RELEASE_MANIFEST.json").read_text(encoding="utf-8")
            )
            self.assertFalse(manifest["drill_runner"])


if __name__ == "__main__":
    unittest.main()
