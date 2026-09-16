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

    def prepare(
        self, name: str = "study", evidence_role: str = "held-out-validation"
    ) -> Path:
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
            evidence_role,
            "C++20",
        )
        return out

    def write_discovery(self, run: Path) -> None:
        (run / "student" / "answer" / "discovery.md").write_text(
            "# Purpose and contract\n\nThe function returns the value 42.\n\n"
            "# Ownership and constraints\n\nThe scalar has no ownership.\n\n"
            "# Evidence and uncertainty\n\nBoth implementation and caller were inspected.\n",
            encoding="utf-8",
        )
        (run / "student" / "answer" / "discovery.json").write_text(
            json.dumps({
                "schema_version": study.SCHEMA_VERSION,
                "source_facts": [{
                    "fact_id": "return_signature",
                    "claim": "answer is declared with a top-level const int return.",
                    "fact_kind": "signature",
                    "evidence": [{
                        "area": "source",
                        "path": "src/value.cpp",
                        "start_line": 1,
                        "end_line": 1,
                        "kind": "declaration",
                    }],
                }, {
                    "fact_id": "caller_contract",
                    "claim": "The caller observes the returned scalar value 42.",
                    "fact_kind": "contract",
                    "evidence": [{
                        "area": "source",
                        "path": "tests/value_test.cpp",
                        "start_line": 1,
                        "end_line": 2,
                        "kind": "test",
                    }],
                }],
                "unresolved_context": [],
            }),
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
        self.complete_audit(run)
        study.accept_audit(run)
        return run

    def complete_audit(self, run: Path) -> dict:
        path = run / "grader" / "audit.json"
        audit = json.loads(path.read_text(encoding="utf-8"))
        metadata = study.load_run(run)[1]
        source_locator = {
            "area": "source", "path": "src/value.cpp",
            "start_line": 1, "end_line": 1, "kind": "declaration",
        }
        human_locator = {
            "area": "source", "path": "src/value.cpp",
            "start_line": 1, "end_line": 1, "kind": "implementation",
        }
        alternative_locator = {
            "area": "work", "path": "improved.cpp",
            "start_line": 1, "end_line": 1, "kind": "implementation",
        }
        machine_locator = {
            "area": "answer", "path": "machine_evidence.md",
            "start_line": 1, "end_line": 1, "kind": "machine-output",
        }
        audit.update({
            "validity": "valid",
            "invalid_reason": "",
            "blocker_attribution": "none",
            "auditor_relation": "separate",
            "card_if_status": "established",
            "card_if_fact_ids": ["return_signature"],
            "comparison_fact_ids": ["return_signature", "caller_contract"],
            "context_resolutions": [],
            "reproduction_map": [{
                "source_fact_id": "return_signature",
                "preservation": "preserved",
                "explanation": "The fixture keeps the scalar int return.",
                "fixture_evidence": [alternative_locator],
            }, {
                "source_fact_id": "caller_contract",
                "preservation": "preserved",
                "explanation": "The fixture returns the same value to the caller.",
                "fixture_evidence": [alternative_locator],
            }],
            "human_implementation_evidence": [human_locator],
            "alternative_implementation_evidence": [alternative_locator],
            "improvement_property": "interface-clarity",
            "improvement_target": "remove a misleading top-level qualifier",
            "improvement_checks": [{
                "check_id": "same_caller_contract",
                "property": "interface-clarity",
                "capable_of_distinguishing": True,
                "observed_difference": True,
                "result": "Both forms return 42; only the alternative matches the callable type.",
                "evidence": [machine_locator],
            }],
            "metadata": {
                "revision": metadata["revision"],
                "source_snapshot_sha256": metadata["source_snapshot_sha256"],
                "language": metadata["language"],
                "language_standard": metadata["language_standard"],
                "project_toolchain": metadata["project_toolchain"],
                "fixture_toolchain": "MSVC 19.50",
                "commands": ["cl /std:c++20 improved.cpp && improved.exe"],
                "evidence": [machine_locator],
            },
        })
        for gate in audit["gates"]:
            gate["result"] = "pass"
            gate["evidence"] = "Structured evidence above satisfies this gate."
        path.write_text(json.dumps(audit), encoding="utf-8")
        return audit

    def complete_grade(self, run: Path, passing: bool = True) -> dict:
        path = run / "grader" / "grade.json"
        grade = json.loads(path.read_text(encoding="utf-8"))
        grade.update({
            "qualification_result": "pass" if passing else "fail",
            "improvement_outcome": "improved",
            "next_action": "project-trial" if passing else "card-repair",
            "attribution": "none" if passing else "skillcard",
            "attributed_object_id": None if passing else PRIMARY,
            "artifact_quality": "strong",
            "process_validity": "strong",
            "skill_attribution": "unproven",
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

    def test_type_fact_requires_declaration_evidence(self) -> None:
        run = self.prepare()
        self.write_discovery(run)
        path = run / "student" / "answer" / "discovery.json"
        discovery = json.loads(path.read_text(encoding="utf-8"))
        discovery["source_facts"][0]["fact_kind"] = "type"
        discovery["source_facts"][0]["evidence"][0]["kind"] = "implementation"
        path.write_text(json.dumps(discovery), encoding="utf-8")
        with self.assertRaisesRegex(study.StudyError, "requires declaration evidence"):
            study.freeze_discovery(run)

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
        self.assertTrue((run / "grader" / "audit_guidance.md").is_file())
        self.assertTrue((run / "grader" / "grade_guidance.md").is_file())
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
        with self.assertRaisesRegex(study.StudyError, "result must be pass or fail"):
            study.finalize(run, "SE_EV_9997", "Qualify a Pattern.")

        grade["criteria"][0]["result"] = "fail"
        path.write_text(json.dumps(grade), encoding="utf-8")
        with self.assertRaisesRegex(study.StudyError, "qualification_result must be fail"):
            study.finalize(run, "SE_EV_9997", "Qualify a Pattern.")

    def test_equivalent_cannot_hide_an_observed_property_difference(self) -> None:
        run = self.reveal_complete_run()
        grade = self.complete_grade(run)
        grade["improvement_outcome"] = "equivalent"
        path = run / "grader" / "grade.json"
        path.write_text(json.dumps(grade), encoding="utf-8")
        with self.assertRaisesRegex(study.StudyError, "equivalent conflicts"):
            study.finalize(run, "SE_EV_9992", "Qualify a Pattern.")

    def test_evidence_audit_rejects_unsupported_gates(self) -> None:
        cases = (
            (
                lambda audit: audit.update({"card_if_fact_ids": ["missing_fact"]}),
                "unknown card IF fact IDs",
            ),
            (
                lambda audit: audit["reproduction_map"].pop(),
                "cover exactly the comparison_fact_ids",
            ),
            (
                lambda audit: audit["improvement_checks"][0].update(
                    {"capable_of_distinguishing": False}
                ),
                "capable of distinguishing",
            ),
            (
                lambda audit: audit["metadata"].update({"fixture_toolchain": ""}),
                "fixture_toolchain is required",
            ),
            (
                lambda audit: audit.update({"auditor_relation": "same-reader"}),
                "separate evidence auditor",
            ),
        )
        for index, (mutate, message) in enumerate(cases):
            with self.subTest(case=index):
                run = self.prepare(f"audit-{index}")
                self.write_discovery(run)
                study.freeze_discovery(run)
                study.open_guidance(run)
                self.write_guided_work(run)
                study.freeze_work(run)
                study.reveal(run)
                audit = self.complete_audit(run)
                mutate(audit)
                (run / "grader" / "audit.json").write_text(
                    json.dumps(audit), encoding="utf-8"
                )
                with self.assertRaisesRegex(study.StudyError, message):
                    study.accept_audit(run)

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
        run = self.prepare()
        self.write_discovery(run)
        discovery_path = run / "student" / "answer" / "discovery.json"
        discovery = json.loads(discovery_path.read_text(encoding="utf-8"))
        discovery["unresolved_context"] = [{
            "context_id": "missing_declaration",
            "question": "What declaration decides the card condition?",
            "potentially_deciding": True,
        }]
        discovery_path.write_text(json.dumps(discovery), encoding="utf-8")
        study.freeze_discovery(run)
        study.open_guidance(run)
        self.write_guided_work(run)
        study.freeze_work(run)
        study.reveal(run)
        path = run / "grader" / "audit.json"
        audit = json.loads(path.read_text(encoding="utf-8"))
        audit.update({
            "validity": "invalid",
            "invalid_reason": "The declaration that decides the card IF is absent.",
            "blocker_attribution": "source-context",
        })
        path.write_text(json.dumps(audit), encoding="utf-8")
        study.accept_audit(run)
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

    def test_motivating_example_cannot_export_habit_candidate(self) -> None:
        run = self.prepare("regression", "motivating-example-regression")
        self.write_discovery(run)
        study.freeze_discovery(run)
        study.open_guidance(run)
        self.write_guided_work(run)
        study.freeze_work(run)
        study.reveal(run)
        self.complete_audit(run)
        study.accept_audit(run)
        grade = self.complete_grade(run)
        path = run / "grader" / "grade.json"
        with self.assertRaisesRegex(study.StudyError, "non-held-out"):
            study.finalize(run, "SE_EV_9995", "Attempt a Pattern field test.")
        grade["habit_candidates"] = []
        path.write_text(json.dumps(grade), encoding="utf-8")
        result = study.finalize(run, "SE_EV_9995", "Run a regression study.")
        self.assertEqual(result["evidence_role"], "motivating-example-regression")
        self.assertFalse((run / "candidate_training_event.json").exists())

    def test_source_paths_cannot_escape_the_bounded_slice(self) -> None:
        with self.assertRaisesRegex(study.StudyError, "relative and bounded"):
            study.prepare(
                LIBRARY, PRIMARY, (), self.source, ("../outside.cpp",),
                "project-relevant-reference", "Example", "abc", "C++20", "MSVC",
                "Review one decision.", self.root / "escape",
            )

    def test_schema_two_studies_are_status_only(self) -> None:
        run = self.prepare()
        run_path = run / "controller" / "run.json"
        metadata = json.loads(run_path.read_text(encoding="utf-8"))
        metadata["schema_version"] = 2
        run_path.write_text(json.dumps(metadata), encoding="utf-8")
        self.assertEqual(study.load_run(run)[1]["schema_version"], 2)
        with self.assertRaisesRegex(study.StudyError, "read-only"):
            study.freeze_discovery(run)

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
