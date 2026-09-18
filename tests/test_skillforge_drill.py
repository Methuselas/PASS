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
        self.learner = self.root / "learner.json"
        self.learner.write_text(
            json.dumps(
                {
                    "learner_id": "local-model-a",
                    "learner": {"kind": "ai"},
                    "model": {"name": "Example 27B", "revision": "r1"},
                    "runtime": {"name": "Manual folder adapter", "version": "1"},
                    "capabilities": {"files": True, "shell": True},
                    "generation": {"temperature": 1.0},
                }
            ),
            encoding="utf-8",
        )
        self.intervention = self.root / "intervention.json"
        self.intervention.write_text(
            json.dumps(
                {
                    "intervention_id": "skillforge-se-beta24",
                    "kind": "guided-drill-plus-skillcards",
                    "description": "Practise with the Drill instructions and bounded cards.",
                    "components": {
                        "drill_instructions": True,
                        "card_ids": [
                            "PAT_access_templatized_base_members_explicitly"
                        ],
                        "external_material": False,
                    },
                }
            ),
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
                "skill_attribution": "unproven",
                "observations": ["The frozen answer exercised the target capability."],
            }
        )
        for item in grade["drills"]:
            item["overall"] = "pass"
            for criterion in item["criteria"]:
                criterion["result"] = "pass"
                criterion["evidence"] = "Present in the frozen answer."
                criterion["failure_owner"] = "none"
                criterion["owner_object_id"] = None
        grade_path.write_text(json.dumps(grade), encoding="utf-8")

    def finalized_baseline(self) -> Path:
        run = self.root / "baseline-prior"
        drill.prepare(
            LIBRARY,
            (SE_DRILL,),
            "before-instructions",
            self.scenario,
            run,
            training_stage="baseline",
            learner_profile_path=self.learner,
        )
        (run / "student" / "answer.md").write_text("Evidence.", encoding="utf-8")
        drill.freeze(run)
        drill.reveal(run)
        self.complete_grade(run)
        grade_path = run / "grader" / "grade.json"
        grade = json.loads(grade_path.read_text(encoding="utf-8"))
        grade["baseline"] = "completed"
        grade_path.write_text(json.dumps(grade), encoding="utf-8")
        drill.finalize(
            run,
            "SOFTWAREENGINEERING_EV_9995",
            "Establish a blind baseline on a novel case.",
            "2026-09-15",
        )
        return run

    def test_discovers_current_game_design_and_software_drills(self) -> None:
        for domain in ("game-design", "software-engineering"):
            with self.subTest(domain=domain):
                expected = {path.stem for path in (LIBRARY / domain).rglob("DRILL_*.md")}
                discovered = [card.object_id for card in drill.discover(LIBRARY, domain)]
                self.assertTrue(expected)
                self.assertEqual(set(discovered), expected)
                self.assertEqual(len(discovered), len(expected))

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
        self.assertTrue((run / "student" / "skillcards").is_dir())

    def test_before_success_check_cut_exposes_instructions_only(self) -> None:
        run = self.prepare("before-success-check")
        task = (run / "student" / "task.md").read_text(encoding="utf-8")
        self.assertIn("## Instructions", task)
        self.assertNotIn("## Success Check", task)
        self.assertNotIn("## Common Failures", task)
        metadata = drill.load_run(run)[1]
        self.assertTrue(metadata["exposed_card_ids"])
        self.assertIn("Declared Qualification Card Bundle", task)

    def test_prepare_records_neutral_learner_profile_without_exposing_it(self) -> None:
        run = self.root / "profiled-run"
        metadata = drill.prepare(
            LIBRARY,
            (SE_DRILL,),
            "before-success-check",
            self.scenario,
            run,
            learner_profile_path=self.learner,
        )
        self.assertEqual(metadata["learner_profile"]["learner_id"], "local-model-a")
        self.assertEqual(metadata["training_stage"], "qualification")
        task = (run / "student" / "task.md").read_text(encoding="utf-8")
        self.assertNotIn("local-model-a", task)

    def test_human_learner_uses_the_same_run_contract_without_model_metadata(self) -> None:
        human = self.root / "human.json"
        human.write_text(
            json.dumps(
                {
                    "learner_id": "participant-01",
                    "learner": {"kind": "human"},
                    "runtime": {"name": "Printed packet and local tools"},
                }
            ),
            encoding="utf-8",
        )
        run = self.root / "human-baseline"
        metadata = drill.prepare(
            LIBRARY,
            (SE_DRILL,),
            "before-instructions",
            self.scenario,
            run,
            training_stage="baseline",
            learner_profile_path=human,
        )
        self.assertEqual(metadata["learner_profile"]["learner"]["kind"], "human")
        self.assertNotIn("model", metadata["learner_profile"])

    def test_ai_learner_does_not_require_model_identity(self) -> None:
        neutral_ai = self.root / "neutral-ai.json"
        neutral_ai.write_text(
            json.dumps(
                {
                    "learner_id": "anonymous-capable-agent",
                    "learner": {"kind": "ai"},
                    "runtime": {"name": "Folder adapter"},
                }
            ),
            encoding="utf-8",
        )
        metadata = drill.prepare(
            LIBRARY,
            (SE_DRILL,),
            "before-instructions",
            self.scenario,
            self.root / "neutral-ai-baseline",
            training_stage="baseline",
            learner_profile_path=neutral_ai,
        )
        self.assertEqual(metadata["learner_profile"]["learner"]["kind"], "ai")
        self.assertNotIn("model", metadata["learner_profile"])

    def test_qualification_run_cannot_claim_isolation_improvement(self) -> None:
        run = self.prepare("before-success-check", SE_DRILL)
        (run / "student" / "answer.md").write_text("Evidence.", encoding="utf-8")
        drill.freeze(run)
        drill.reveal(run)
        self.complete_grade(run)
        grade_path = run / "grader" / "grade.json"
        grade = json.loads(grade_path.read_text(encoding="utf-8"))
        grade["isolation"] = "improved"
        grade_path.write_text(json.dumps(grade), encoding="utf-8")
        with self.assertRaisesRegex(drill.DrillError, "unmeasured isolation"):
            drill.finalize(run, "SOFTWAREENGINEERING_EV_9997", "Qualify a Drill.")

    def test_baseline_exports_stage_and_structured_taker(self) -> None:
        run = self.root / "baseline-run"
        drill.prepare(
            LIBRARY,
            (SE_DRILL,),
            "before-instructions",
            self.scenario,
            run,
            training_stage="baseline",
            learner_profile_path=self.learner,
        )
        (run / "student" / "answer.md").write_text("Evidence.", encoding="utf-8")
        drill.freeze(run)
        drill.reveal(run)
        self.complete_grade(run)
        grade_path = run / "grader" / "grade.json"
        grade = json.loads(grade_path.read_text(encoding="utf-8"))
        grade["baseline"] = "completed"
        grade_path.write_text(json.dumps(grade), encoding="utf-8")
        event = drill.finalize(
            run,
            "SOFTWAREENGINEERING_EV_9996",
            "Establish a blind baseline on a novel case.",
            "2026-09-15",
        )
        self.assertEqual(event["training_stage"], "baseline")
        self.assertEqual(event["program_purpose"], "skillset-improvement")
        self.assertEqual(event["taker"]["model"]["name"], "Example 27B")
        errors: list[str] = []
        memory.validate_event(event, 0, errors)
        self.assertEqual(errors, [])

    def test_practice_requires_prior_run_and_intervention(self) -> None:
        with self.assertRaisesRegex(drill.DrillError, "requires --intervention"):
            drill.prepare(
                LIBRARY,
                (SE_DRILL,),
                "before-success-check",
                self.scenario,
                self.root / "practice-run",
                training_stage="practice",
                learner_profile_path=self.learner,
            )
        with self.assertRaisesRegex(drill.DrillError, "requires --prior-run"):
            drill.prepare(
                LIBRARY,
                (SE_DRILL,),
                "before-success-check",
                self.scenario,
                self.root / "practice-with-intervention",
                training_stage="practice",
                learner_profile_path=self.learner,
                intervention_path=self.intervention,
            )

    def test_retention_links_same_learner_and_requires_novel_scenario(self) -> None:
        baseline = self.finalized_baseline()
        practice = self.root / "practice-prior"
        drill.prepare(
            LIBRARY,
            (SE_DRILL,),
            "before-success-check",
            self.scenario,
            practice,
            training_stage="practice",
            learner_profile_path=self.learner,
            intervention_path=self.intervention,
            prior_run_path=baseline,
        )
        (practice / "student" / "answer.md").write_text("Practice evidence.", encoding="utf-8")
        drill.freeze(practice)
        drill.reveal(practice)
        self.complete_grade(practice)
        practice_event = drill.finalize(
            practice,
            "SOFTWAREENGINEERING_EV_9994",
            "Practise the capability with a bounded skill load.",
            "2026-09-15",
        )
        self.assertEqual(
            practice_event["intervention"]["components"]["card_ids"],
            ["PAT_access_templatized_base_members_explicitly"],
        )
        errors: list[str] = []
        memory.validate_event(practice_event, 0, errors)
        self.assertEqual(errors, [])
        isolation_scenario = self.root / "isolation-scenario.md"
        isolation_scenario.write_text(
            "# Isolation case\n\nResolve a second concrete case.\n", encoding="utf-8"
        )
        isolation = self.root / "isolation-prior"
        drill.prepare(
            LIBRARY,
            (SE_DRILL,),
            "before-instructions",
            isolation_scenario,
            isolation,
            training_stage="isolation",
            learner_profile_path=self.learner,
            prior_run_path=practice,
        )
        (isolation / "student" / "answer.md").write_text("Isolation evidence.", encoding="utf-8")
        drill.freeze(isolation)
        drill.reveal(isolation)
        self.complete_grade(isolation)
        isolation_grade_path = isolation / "grader" / "grade.json"
        isolation_grade = json.loads(isolation_grade_path.read_text(encoding="utf-8"))
        isolation_grade["isolation"] = "improved"
        isolation_grade_path.write_text(json.dumps(isolation_grade), encoding="utf-8")
        drill.finalize(
            isolation,
            "SOFTWAREENGINEERING_EV_9993",
            "Test the capability immediately after practice on a novel case.",
            "2026-09-15",
        )
        with self.assertRaisesRegex(drill.DrillError, "requires a novel scenario"):
            drill.prepare(
                LIBRARY,
                (SE_DRILL,),
                "before-instructions",
                self.scenario,
                self.root / "retention-duplicate",
                training_stage="retention",
                learner_profile_path=self.learner,
                prior_run_path=isolation,
            )
        novel = self.root / "retention-scenario.md"
        novel.write_text("# Transfer case\n\nResolve a different concrete case.\n", encoding="utf-8")
        run = self.root / "retention-run"
        metadata = drill.prepare(
            LIBRARY,
            (SE_DRILL,),
            "before-instructions",
            novel,
            run,
            training_stage="retention",
            learner_profile_path=self.learner,
            prior_run_path=isolation,
        )
        self.assertEqual(metadata["prior_run"]["run_id"], drill.load_run(isolation)[1]["run_id"])

    def test_stage_practice_packages_declared_pattern_and_drill_guidance(self) -> None:
        baseline = self.finalized_baseline()
        practice = self.root / "guided-practice"
        metadata = drill.prepare(
            LIBRARY,
            (SE_DRILL,),
            "before-success-check",
            self.scenario,
            practice,
            training_stage="practice",
            learner_profile_path=self.learner,
            intervention_path=self.intervention,
            prior_run_path=baseline,
        )
        task = (practice / "student" / "task.md").read_text(encoding="utf-8")
        pattern = (
            practice
            / "student"
            / "skillcards"
            / "software-engineering"
            / "languages"
            / "cpp"
            / "templates"
            / "PAT_access_templatized_base_members_explicitly.md"
        )
        self.assertIn("## Instructions", task)
        self.assertIn("Declared Teaching Intervention", task)
        self.assertTrue(pattern.is_file())
        self.assertIn("## Pattern Rule", pattern.read_text(encoding="utf-8"))
        self.assertEqual(
            metadata["exposed_card_ids"],
            ["PAT_access_templatized_base_members_explicitly"],
        )

    def test_skillcard_only_practice_keeps_the_baseline_cut(self) -> None:
        baseline = self.root / "instruction-visible-baseline"
        drill.prepare(
            LIBRARY,
            (SE_DRILL,),
            "before-success-check",
            self.scenario,
            baseline,
            training_stage="baseline",
            learner_profile_path=self.learner,
        )
        (baseline / "student" / "answer.md").write_text("Evidence.", encoding="utf-8")
        drill.freeze(baseline)
        drill.reveal(baseline)
        self.complete_grade(baseline)
        grade_path = baseline / "grader" / "grade.json"
        grade = json.loads(grade_path.read_text(encoding="utf-8"))
        grade["baseline"] = "completed"
        grade_path.write_text(json.dumps(grade), encoding="utf-8")
        drill.finalize(baseline, "SOFTWAREENGINEERING_EV_9989", "Baseline.")

        card_only = self.root / "card-only.json"
        card_only.write_text(
            json.dumps(
                {
                    "intervention_id": "one-pattern",
                    "kind": "skillcards",
                    "description": "Teach one Pattern while holding Drill guidance constant.",
                    "components": {
                        "drill_instructions": False,
                        "card_ids": [
                            "PAT_access_templatized_base_members_explicitly"
                        ],
                        "external_material": False,
                    },
                }
            ),
            encoding="utf-8",
        )
        drill.prepare(
            LIBRARY,
            (SE_DRILL,),
            "before-success-check",
            self.scenario,
            self.root / "card-only-practice",
            training_stage="practice",
            learner_profile_path=self.learner,
            intervention_path=card_only,
            prior_run_path=baseline,
        )
        with self.assertRaisesRegex(drill.DrillError, "may change the administration cut"):
            drill.prepare(
                LIBRARY,
                (SE_DRILL,),
                "before-instructions",
                self.scenario,
                self.root / "confounded-card-practice",
                training_stage="practice",
                learner_profile_path=self.learner,
                intervention_path=card_only,
                prior_run_path=baseline,
            )

    def test_training_sequence_keeps_learner_and_runtime_profile_stable(self) -> None:
        baseline = self.finalized_baseline()
        changed = self.root / "changed-learner.json"
        profile = json.loads(self.learner.read_text(encoding="utf-8"))
        profile["model"]["revision"] = "different checkpoint"
        changed.write_text(json.dumps(profile), encoding="utf-8")
        with self.assertRaisesRegex(
            drill.DrillError, "learner and runtime profile stable"
        ):
            drill.prepare(
                LIBRARY,
                (SE_DRILL,),
                "before-success-check",
                self.scenario,
                self.root / "changed-profile-practice",
                training_stage="practice",
                learner_profile_path=changed,
                intervention_path=self.intervention,
                prior_run_path=baseline,
            )

    def test_nonpass_cannot_blame_a_pattern_that_was_not_exposed(self) -> None:
        run = self.prepare("before-success-check", SE_DRILL)
        (run / "student" / "answer.md").write_text("Evidence.", encoding="utf-8")
        drill.freeze(run)
        drill.reveal(run)
        self.complete_grade(run)
        grade_path = run / "grader" / "grade.json"
        grade = json.loads(grade_path.read_text(encoding="utf-8"))
        criterion = grade["drills"][0]["criteria"][0]
        criterion.update({
            "result": "fail",
            "failure_owner": "skillcard",
            "owner_object_id": "PAT_initialize_members_with_init_list",
            "lesson": {
                "mistake": "The inherited call remained unqualified.",
                "correction": "Qualify lookup with this-> or a using declaration.",
                "prevention": "Check dependent base names before compiling.",
            },
        })
        grade["drills"][0]["overall"] = "fail"
        grade_path.write_text(json.dumps(grade), encoding="utf-8")
        with self.assertRaisesRegex(drill.DrillError, "Pattern/AP exposed"):
            drill.finalize(run, "SOFTWAREENGINEERING_EV_9988", "Qualify a Drill.")

    def test_qualification_can_attribute_failure_to_an_exposed_linked_skillcard(self) -> None:
        run = self.prepare("before-success-check", SE_DRILL)
        (run / "student" / "answer.md").write_text("Evidence.", encoding="utf-8")
        drill.freeze(run)
        drill.reveal(run)
        self.complete_grade(run)
        grade_path = run / "grader" / "grade.json"
        grade = json.loads(grade_path.read_text(encoding="utf-8"))
        criterion = grade["drills"][0]["criteria"][0]
        criterion.update({
            "result": "fail",
            "failure_owner": "skillcard",
            "owner_object_id": "PAT_access_templatized_base_members_explicitly",
            "lesson": {
                "mistake": "The card left the required qualification ambiguous.",
                "correction": "State the qualification mechanism explicitly.",
                "prevention": "Exercise each named mechanism against a negative case.",
            },
        })
        grade["drills"][0]["overall"] = "fail"
        grade_path.write_text(json.dumps(grade), encoding="utf-8")
        event = drill.finalize(
            run,
            "SOFTWAREENGINEERING_EV_9986",
            "Qualify dependent-name cards on a novel case.",
        )
        self.assertEqual(event["lessons"][0]["cause"], "skillcard")
        self.assertIn(
            "PAT_access_templatized_base_members_explicitly",
            event["intervention"]["components"]["card_ids"],
        )

    def test_qualification_rejects_partial_and_derives_binary_overall(self) -> None:
        run = self.prepare("before-success-check", SE_DRILL)
        (run / "student" / "answer.md").write_text("Evidence.", encoding="utf-8")
        drill.freeze(run)
        drill.reveal(run)
        self.complete_grade(run)
        grade_path = run / "grader" / "grade.json"
        grade = json.loads(grade_path.read_text(encoding="utf-8"))
        criterion = grade["drills"][0]["criteria"][0]
        criterion.update({
            "result": "partial",
            "failure_owner": "application",
            "lesson": {
                "mistake": "A required result was incomplete.",
                "correction": "Complete and verify every required result.",
                "prevention": "Check every rubric criterion before finalizing.",
            },
        })
        grade["drills"][0]["overall"] = "partial"
        grade_path.write_text(json.dumps(grade), encoding="utf-8")
        with self.assertRaisesRegex(drill.DrillError, "invalid overall result"):
            drill.finalize(run, "SOFTWAREENGINEERING_EV_9985", "Qualify a Drill.")

        criterion["result"] = "fail"
        grade["drills"][0]["overall"] = "pass"
        grade_path.write_text(json.dumps(grade), encoding="utf-8")
        with self.assertRaisesRegex(drill.DrillError, "overall must be fail"):
            drill.finalize(run, "SOFTWAREENGINEERING_EV_9985", "Qualify a Drill.")

    def test_semantic_writing_object_ids_resolve_by_type_not_prefix(self) -> None:
        library = self.root / "semantic-writing-library"
        card_path = library / "writing" / "practice" / "example.md"
        card_path.parent.mkdir(parents=True)
        text = drill.select_teaching_cards(
            LIBRARY,
            ["PAT_scale_clue_detail_without_gating_forward_motion"],
            "writing",
        )[0].text.replace(
            "object_id: PAT_scale_clue_detail_without_gating_forward_motion",
            "object_id: semantic_clue_detail_pattern",
            1,
        )
        card_path.write_text(text, encoding="utf-8")
        cards = drill.select_teaching_cards(
            library,
            ["semantic_clue_detail_pattern"],
            "writing",
        )
        self.assertEqual(cards[0].object_type, "pattern")

    def test_semantic_drill_ids_resolve_by_frontmatter_type_not_filename(self) -> None:
        library = self.root / "semantic-library"
        card_path = library / "software-engineering" / "practice" / "exercise.md"
        card_path.parent.mkdir(parents=True)
        (library / "software-engineering" / "MODULE.yaml").write_text(
            "module_id: semantic-test\n", encoding="utf-8"
        )
        text = drill.select_drills(LIBRARY, [SE_DRILL])[0].text.replace(
            "object_id: DRILL_fix_templatized_base_class_name_access",
            "object_id: access_templatized_base_members_explicitly_exercise",
            1,
        )
        card_path.write_text(text, encoding="utf-8")
        cards = drill.discover(library, "software-engineering")
        self.assertEqual(
            [card.object_id for card in cards],
            ["access_templatized_base_members_explicitly_exercise"],
        )

    def test_application_failure_exports_a_transferable_lesson_not_a_model_profile(self) -> None:
        run = self.root / "application-miss"
        drill.prepare(
            LIBRARY,
            (SE_DRILL,),
            "before-success-check",
            self.scenario,
            run,
            learner_profile_path=self.learner,
        )
        (run / "student" / "answer.md").write_text("Evidence.", encoding="utf-8")
        drill.freeze(run)
        drill.reveal(run)
        self.complete_grade(run)
        grade_path = run / "grader" / "grade.json"
        grade = json.loads(grade_path.read_text(encoding="utf-8"))
        criterion = grade["drills"][0]["criteria"][0]
        criterion.update({
            "result": "fail",
            "failure_owner": "application",
            "lesson": {
                "mistake": "Example 27B left a dependent base call unqualified.",
                "correction": "Enable dependent lookup explicitly.",
                "prevention": "Inspect inherited names in every derived class template.",
            },
        })
        grade["drills"][0]["overall"] = "fail"
        grade_path.write_text(json.dumps(grade), encoding="utf-8")
        with self.assertRaisesRegex(drill.DrillError, "not name the taker"):
            drill.finalize(run, "SOFTWAREENGINEERING_EV_9987", "Qualify a Drill.")

        criterion["lesson"]["mistake"] = "A dependent base call was left unqualified."
        grade_path.write_text(json.dumps(grade), encoding="utf-8")
        event = drill.finalize(
            run,
            "SOFTWAREENGINEERING_EV_9987",
            "Exercise dependent-name lookup on a novel case.",
        )
        self.assertEqual(event["lessons"][0]["cause"], "application")
        self.assertNotIn("Example 27B", json.dumps(event["lessons"]))
        errors: list[str] = []
        memory.validate_event(event, 0, errors)
        self.assertEqual(errors, [])

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
            text=True, encoding="utf-8",
            capture_output=True,
            cwd=ROOT,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        runner = release / "scripts" / "skillforge_drill.py"
        self.assertTrue(runner.is_file())
        listing = subprocess.run(
            [sys.executable, str(runner), "list", "--domain", "game-design", "--format", "json"],
            text=True, encoding="utf-8",
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
            completed = subprocess.run(command, text=True, encoding="utf-8", capture_output=True, cwd=release)
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        (released_run / "student" / "answer.md").write_text(
            "Produced release-local evidence.", encoding="utf-8"
        )
        for command in commands[1:]:
            completed = subprocess.run(command, text=True, encoding="utf-8", capture_output=True, cwd=release)
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
            text=True, encoding="utf-8",
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
                text=True, encoding="utf-8",
                capture_output=True,
                cwd=ROOT,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertFalse((release / "scripts" / "skillforge_drill.py").exists())
            manifest = json.loads(
                (release / "RELEASE_MANIFEST.json").read_text(encoding="utf-8")
            )
            self.assertFalse(manifest["drill_runner"])
            self.assertFalse(manifest["code_study_runner"])


if __name__ == "__main__":
    unittest.main()
