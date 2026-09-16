"""Contracts for the software Code Apprenticeship controller."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_PATH = ROOT / "PASS" / "runtime" / "skillforge_code_study.py"
SPEC = importlib.util.spec_from_file_location("skillforge_code_study", RUNTIME_PATH)
assert SPEC and SPEC.loader
study = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = study
SPEC.loader.exec_module(study)

TOOLS = ROOT / "PASS" / "tools"
sys.path.insert(0, str(TOOLS))
MEMORY_SPEC = importlib.util.spec_from_file_location("skillforge_memory_study", TOOLS / "memory.py")
assert MEMORY_SPEC and MEMORY_SPEC.loader
memory = importlib.util.module_from_spec(MEMORY_SPEC)
sys.modules[MEMORY_SPEC.name] = memory
MEMORY_SPEC.loader.exec_module(memory)

LIBRARY = ROOT / "library"
PRIMARY = "PAT_return_values_without_top_level_const"
SUPPORTING = "AP_review_code_you_did_not_write"


class SkillForgeCodeStudyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.source = self.root / "human-project"
        (self.source / "src").mkdir(parents=True)
        (self.source / "tests").mkdir()
        (self.source / "src" / "value.cpp").write_text(
            "const int answer() { return 42; }\n", encoding="utf-8"
        )
        (self.source / "tests" / "value_test.cpp").write_text(
            "int answer();\nint main() { return answer() == 42 ? 0 : 1; }\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def prepare(self, name: str = "study") -> Path:
        out = self.root / name
        study.prepare(
            LIBRARY,
            PRIMARY,
            (SUPPORTING,),
            self.source,
            ("src/value.cpp", "tests/value_test.cpp"),
            "project-relevant-reference",
            "Example human project",
            "abc123",
            "C++20",
            "MSVC 19.50",
            "Decide whether a scalar return type should carry top-level const.",
            out,
        )
        return out

    def write_discovery(self, run: Path) -> None:
        (run / "student" / "answer" / "discovery.md").write_text(
            "# Purpose and contract\n\nThe function returns the value 42.\n\n"
            "# Ownership and constraints\n\nThe scalar has no ownership.\n\n"
            "# Evidence and uncertainty\n\nBoth implementation and caller were inspected.\n",
            encoding="utf-8",
        )

    def write_guided_work(self, run: Path) -> None:
        answer = run / "student" / "answer"
        (answer / "card_analysis.md").write_text(
            "The Pattern applies to a scalar value return.\n", encoding="utf-8"
        )
        (answer / "improvement.md").write_text(
            "Target: interface clarity. Remove top-level const while preserving behavior.\n",
            encoding="utf-8",
        )
        (answer / "machine_evidence.md").write_text(
            "Both forms compiled and the test returned zero.\n", encoding="utf-8"
        )
        (run / "student" / "work" / "improved.cpp").write_text(
            "int answer() { return 42; }\n", encoding="utf-8"
        )

    def reveal_complete_run(self, name: str = "study") -> Path:
        run = self.prepare(name)
        self.write_discovery(run)
        study.freeze_discovery(run)
        study.open_guidance(run)
        self.write_guided_work(run)
        study.freeze_work(run)
        study.reveal(run)
        return run

    def complete_grade(self, run: Path, passing: bool = True) -> dict:
        path = run / "grader" / "grade.json"
        grade = json.loads(path.read_text(encoding="utf-8"))
        grade.update({
            "validity": "valid",
            "invalid_reason": "",
            "qualification_result": "pass" if passing else "fail",
            "improvement_outcome": "improved",
            "improvement_target": "interface clarity",
            "next_action": "project-trial" if passing else "card-repair",
            "attribution": "none" if passing else "skillcard",
            "attributed_object_id": None if passing else PRIMARY,
            "artifact_quality": "strong",
            "process_validity": "strong",
            "skill_attribution": "unproven",
            "card_if_status": "established",
            "card_if_evidence": (
                "src/value.cpp:1 declares the top-level const scalar return; "
                "tests/value_test.cpp:1 declares and calls the same interface."
            ),
            "source_context_complete": True,
            "reproduction_fidelity": "verified",
            "reproduction_fidelity_evidence": (
                "The work preserves the int return type, value, and caller contract."
            ),
            "improvement_claim_exercised": True,
            "improvement_claim_evidence": (
                "Both declarations compiled against the same caller and returned 42."
            ),
            "metadata_consistent": True,
            "metadata_evidence": (
                "The abc123 source slice and MSVC 19.50 evidence match the run metadata."
            ),
            "observations": [
                "The alternative preserved behavior and removed a misleading qualifier."
            ],
            "habit_candidates": [{
                "observation": "A top-level const scalar return changed no caller behavior.",
                "habit": "Avoid top-level const on returned scalar values.",
                "verification": "Compile equivalent declarations and run the same caller test.",
                "disposition": "memory-candidate",
                "owner_object_id": PRIMARY,
            }],
        })
        for item in grade["criteria"]:
            item["result"] = "pass"
            item["evidence"] = "Recorded in the frozen study artifacts."
        if not passing:
            grade["criteria"][-1]["result"] = "fail"
            grade["criteria"][-1]["evidence"] = "The primary card omitted a required constraint."
        path.write_text(json.dumps(grade), encoding="utf-8")
        return grade

    def test_prepare_exposes_source_but_hides_skillcards(self) -> None:
        run = self.prepare()
        self.assertTrue((run / "student" / "source" / "src" / "value.cpp").is_file())
        self.assertFalse((run / "student" / "skillcards").exists())
        brief = (run / "student" / "brief.md").read_text(encoding="utf-8")
        self.assertIn("before any PASS card is opened", brief)
        self.assertIn("answer/discovery.md", brief)
        metadata = study.load_run(run)[1]
        self.assertEqual(metadata["exposed_card_ids"], [])

    def test_guidance_opens_only_after_frozen_discovery(self) -> None:
        run = self.prepare()
        with self.assertRaisesRegex(study.StudyError, "discovery-frozen"):
            study.open_guidance(run)
        self.write_discovery(run)
        frozen = study.freeze_discovery(run)
        self.assertEqual(frozen["state"], "discovery-frozen")
        opened = study.open_guidance(run)
        self.assertEqual(opened["exposed_card_ids"], [PRIMARY, SUPPORTING])
        self.assertTrue((run / "student" / "skillcards").is_dir())
        guidance = (run / "student" / "guidance.md").read_text(encoding="utf-8")
        self.assertIn("implemented, not merely described", guidance)
        self.assertIn("A name, cast, comment, or use is not declaration evidence", guidance)
        self.assertIn("the run is INVALID", guidance)

    def test_mutating_discovery_or_source_after_freeze_fails_closed(self) -> None:
        run = self.prepare()
        self.write_discovery(run)
        study.freeze_discovery(run)
        discovery = run / "student" / "answer" / "discovery.md"
        discovery.write_text("changed", encoding="utf-8")
        with self.assertRaisesRegex(study.StudyError, "discovery changed"):
            study.open_guidance(run)

        run = self.prepare("source-change")
        self.write_discovery(run)
        study.freeze_discovery(run)
        (run / "student" / "source" / "extra.cpp").write_text("int x;\n", encoding="utf-8")
        with self.assertRaisesRegex(study.StudyError, "human source changed"):
            study.open_guidance(run)

    def test_freeze_requires_analysis_evidence_and_implemented_work(self) -> None:
        run = self.prepare()
        self.write_discovery(run)
        study.freeze_discovery(run)
        study.open_guidance(run)
        with self.assertRaisesRegex(study.StudyError, "card_analysis.md"):
            study.freeze_work(run)
        self.write_guided_work(run)
        (run / "student" / "work" / "improved.cpp").unlink()
        with self.assertRaisesRegex(study.StudyError, "implemented alternative"):
            study.freeze_work(run)

    def test_valid_grade_is_binary_and_exports_memory_candidate(self) -> None:
        run = self.reveal_complete_run()
        self.complete_grade(run)
        event = study.finalize(
            run,
            "SE_EV_9999",
            "Qualify a software Pattern against human code and test an improvement.",
            "2026-09-15",
        )
        self.assertEqual(event["run_type"], "software-card-field-test")
        self.assertEqual(event["validity"], "valid")
        self.assertEqual(event["scope_id"], PRIMARY)
        self.assertTrue(any("Habit candidate" in item for item in event["observations"]))
        self.assertTrue((run / "candidate_training_event.json").is_file())
        errors: list[str] = []
        memory.validate_event(event, 0, errors)
        self.assertEqual(errors, [])

    def test_failed_card_qualification_requires_exposed_card_attribution(self) -> None:
        run = self.reveal_complete_run()
        grade = self.complete_grade(run, passing=False)
        grade["attributed_object_id"] = "PAT_not_exposed"
        path = run / "grader" / "grade.json"
        path.write_text(json.dumps(grade), encoding="utf-8")
        with self.assertRaisesRegex(study.StudyError, "exposed Pattern/AP"):
            study.finalize(run, "SE_EV_9998", "Qualify a Pattern.")

        grade["attributed_object_id"] = PRIMARY
        path.write_text(json.dumps(grade), encoding="utf-8")
        event = study.finalize(run, "SE_EV_9998", "Qualify a Pattern.")
        self.assertEqual(event["validity"], "valid")
        self.assertIn("qualification=fail", event["notes"])

    def test_partial_or_inconsistent_qualification_is_rejected(self) -> None:
        run = self.reveal_complete_run()
        grade = self.complete_grade(run)
        grade["criteria"][0]["result"] = "partial"
        path = run / "grader" / "grade.json"
        path.write_text(json.dumps(grade), encoding="utf-8")
        with self.assertRaisesRegex(study.StudyError, "invalid result"):
            study.finalize(run, "SE_EV_9997", "Qualify a Pattern.")

        grade["criteria"][0]["result"] = "fail"
        path.write_text(json.dumps(grade), encoding="utf-8")
        with self.assertRaisesRegex(study.StudyError, "qualification_result must be fail"):
            study.finalize(run, "SE_EV_9997", "Qualify a Pattern.")

    def test_valid_grade_requires_explicit_evidence_gates(self) -> None:
        run = self.reveal_complete_run()
        grade = self.complete_grade(run)
        path = run / "grader" / "grade.json"
        cases = (
            ("card_if_status", "not-established", "card IF to be established"),
            ("source_context_complete", False, "complete deciding source context"),
            ("reproduction_fidelity", "not-verified", "reproduction fidelity"),
            ("improvement_claim_exercised", False, "exercise the named improvement"),
            ("metadata_consistent", False, "consistent revision, language, and toolchain"),
        )
        for key, value, message in cases:
            with self.subTest(key=key):
                candidate = dict(grade)
                candidate[key] = value
                path.write_text(json.dumps(candidate), encoding="utf-8")
                with self.assertRaisesRegex(study.StudyError, message):
                    study.finalize(run, "SE_EV_9994", "Qualify a Pattern.")

    def test_neutral_corpus_rejects_floating_revision(self) -> None:
        with self.assertRaisesRegex(study.StudyError, "immutable revision"):
            study.prepare(
                LIBRARY, PRIMARY, (), self.source, ("src/value.cpp",),
                "neutral-external-corpus", "Example", "master", "C++20", "MSVC",
                "Review one decision.", self.root / "floating-revision",
            )

    def test_explicit_invalidation_is_not_craft_evidence(self) -> None:
        run = self.prepare()
        study.invalidate(run, "source context was incomplete")
        event = study.finalize(
            run, "SE_EV_9996", "Attempt a software card field test.", "2026-09-15"
        )
        self.assertEqual(event["validity"], "invalid")
        self.assertEqual(event["invalid_reason"], "source context was incomplete")
        errors: list[str] = []
        memory.validate_event(event, 0, errors)
        self.assertEqual(errors, [])

    def test_grader_can_invalidate_missing_deciding_source_context(self) -> None:
        run = self.reveal_complete_run()
        path = run / "grader" / "grade.json"
        grade = json.loads(path.read_text(encoding="utf-8"))
        grade.update({
            "validity": "invalid",
            "invalid_reason": "The declaration that decides the card IF is absent.",
            "qualification_result": "not_tested",
            "improvement_outcome": "not_tested",
            "next_action": "source-context-review",
            "attribution": "source-context",
            "artifact_quality": "unproven",
            "process_validity": "failed",
            "skill_attribution": "unproven",
            "card_if_status": "not-established",
            "card_if_evidence": "",
            "source_context_complete": False,
            "reproduction_fidelity": "not-verified",
            "reproduction_fidelity_evidence": "",
            "improvement_claim_exercised": False,
            "improvement_claim_evidence": "",
            "metadata_consistent": True,
            "metadata_evidence": "Run metadata matches the available evidence.",
            "observations": [],
            "habit_candidates": [],
        })
        path.write_text(json.dumps(grade), encoding="utf-8")
        event = study.finalize(
            run, "SE_EV_9993", "Attempt a Pattern field test.", "2026-09-15"
        )
        self.assertEqual(event["validity"], "invalid")
        self.assertEqual(
            event["invalid_reason"],
            "The declaration that decides the card IF is absent.",
        )
        errors: list[str] = []
        memory.validate_event(event, 0, errors)
        self.assertEqual(errors, [])

    def test_invalid_grade_cannot_retain_habit_candidates(self) -> None:
        run = self.reveal_complete_run()
        path = run / "grader" / "grade.json"
        grade = json.loads(path.read_text(encoding="utf-8"))
        grade.update({
            "validity": "invalid",
            "invalid_reason": "compiler unavailable",
            "attribution": "runtime-tool",
            "artifact_quality": "unproven",
            "process_validity": "failed",
            "skill_attribution": "unproven",
            "habit_candidates": [{
                "observation": "The run stopped before compilation.",
                "habit": "Use a different compiler.",
                "verification": "Compile the probe.",
                "disposition": "memory-candidate",
            }],
        })
        path.write_text(json.dumps(grade), encoding="utf-8")
        with self.assertRaisesRegex(study.StudyError, "cannot retain coding-habit"):
            study.finalize(run, "SE_EV_9995", "Attempt a Pattern field test.")

    def test_source_paths_cannot_escape_the_bounded_slice(self) -> None:
        with self.assertRaisesRegex(study.StudyError, "relative and bounded"):
            study.prepare(
                LIBRARY, PRIMARY, (), self.source, ("../outside.cpp",),
                "project-relevant-reference", "Example", "abc", "C++20", "MSVC",
                "Review one decision.", self.root / "escape",
            )

    def test_software_release_vendors_the_code_apprenticeship_runner(self) -> None:
        release = self.root / "release"
        recipe = (
            ROOT
            / "workspace"
            / "release-recipes"
            / "SkillForge_Software_Engineering.yaml"
        )
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
            encoding="utf-8",
            capture_output=True,
            cwd=ROOT,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        runner = release / "scripts" / "skillforge_code_study.py"
        self.assertTrue(runner.is_file())
        help_result = subprocess.run(
            [sys.executable, str(runner), "--help"],
            text=True,
            encoding="utf-8",
            capture_output=True,
            cwd=release,
        )
        self.assertEqual(help_result.returncode, 0, help_result.stdout + help_result.stderr)
        manifest = json.loads(
            (release / "RELEASE_MANIFEST.json").read_text(encoding="utf-8")
        )
        self.assertTrue(manifest["code_study_runner"])
        skill = (release / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Software Code Apprenticeship", skill)


if __name__ == "__main__":
    unittest.main()
