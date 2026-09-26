"""Contracts for CRQ execution evidence and evaluation.

Covers `open-execution` (result templates, frozen arm bundles, held-out cases
revealed only now), `freeze-execution` (all-or-nothing verdicts, evidence
manifests, evaluator relations, contamination) and `evaluate` (arm symmetry,
per-case deltas, the final gate, a frozen result that never edits canon). The
end-to-end runs reproduce design fixtures A (qualified) and B (two targets fixed,
one protection regressed). The synthetic library and memory store come from the
candidate-freeze suite.
"""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_candidate_qualification_candidate import (  # noqa: E402
    CONTROLLER, HELD_OUT_TASK, STRESS_TASK, TARGET, CandidateFixture, crq, default_plan_entries,
    plan_entry, write_text,
)


PASS_ALL = "pass"


class ExecutionFixture(CandidateFixture):
    def frozen_run(self, run_id: str = "SE_CRQ_0001", entries: list[dict] | None = None,
                   gap: str | None = None) -> Path:
        out = self.make_run(run_id)
        self.write_plan(out, entries, gap)
        crq.freeze_plan(out)
        crq.stage_candidate(out)
        self.author(out)
        crq.freeze_candidate(out)
        return out

    def open_run(self, run_id: str = "SE_CRQ_0001", **options) -> Path:
        out = self.frozen_run(run_id, **options)
        crq.open_execution(out)
        return out

    def result_path(self, out: Path, case_id: str, arm: str) -> Path:
        return out / "cases" / case_id / arm / "result.json"

    def fill(self, out: Path, case_id: str, arm: str, verdict: str, **changes) -> dict:
        """Grade one arm with real evidence; `changes` override result fields."""
        path = self.result_path(out, case_id, arm)
        result = json.loads(path.read_text(encoding="utf-8"))
        evidence = path.parent / "evidence" / "output.txt"
        write_text(evidence, f"{case_id} {arm} artifact\n")
        failing = verdict == "fail"
        result.update({
            "verdict": verdict,
            "executor": {"kind": "ai", "runtime": "synthetic-host", "model": "synthetic-model"},
            "environment": {"toolchain": "same"},
            "criteria": [
                {"criterion": item["criterion"], "result": "fail" if failing else "pass",
                 "evidence": "evidence/output.txt"}
                for item in result["criteria"]
            ],
            "evidence_manifest": [{"path": "evidence/output.txt", "sha256": crq.digest_file(evidence),
                                   "kind": "arm-output"}],
        })
        if verdict == "invalid":
            result.update(invalid_reason="the fixture could not be built", criteria=[])
        result.update(changes)
        crq.write_json_atomic(path, result)
        return result

    def grade(self, out: Path, verdicts: dict[str, tuple[str, str]]) -> None:
        for case_id, (baseline, candidate) in verdicts.items():
            self.fill(out, case_id, "baseline", baseline)
            self.fill(out, case_id, "candidate", candidate)

    def result(self, out: Path) -> dict:
        return json.loads((out / "qualification_result.json").read_text(encoding="utf-8"))


GOOD = {"TARGET_001": ("fail", "pass"), "PROTECT_001": ("pass", "pass"),
        "STRESS_001": ("pass", "pass"), "DET_001": ("fail", "pass")}


class OpenExecutionTests(ExecutionFixture):
    def test_templates_bundles_and_revealed_brief(self) -> None:
        out = self.open_run()
        run = crq.load_run(out)[1]
        self.assertEqual(run["state"], "execution-open")
        for entry in default_plan_entries():
            for arm in crq.ARMS:
                result = json.loads(self.result_path(out, entry["case_id"], arm).read_text(encoding="utf-8"))
                self.assertIsNone(result["verdict"])
                self.assertEqual(result["case_sha256"], crq.digest_file(out / "cases" / entry["case_id"] / "case.json"))
                self.assertEqual([c["criterion"] for c in result["criteria"]], ["The owner outlives every view."])
        baseline = out / "arms" / "baseline" / "cards" / TARGET
        candidate = out / "arms" / "candidate" / "cards" / TARGET
        self.assertEqual(baseline.read_bytes(), (out / "baseline" / "cards" / TARGET).read_bytes())
        self.assertEqual(candidate.read_bytes(), (out / "candidate" / "cards" / TARGET).read_bytes())
        self.assertNotEqual(baseline.read_bytes(), candidate.read_bytes())
        self.assertIn("arms", run["freezes"])
        brief = (out / "README.md").read_text(encoding="utf-8")
        for revealed in (HELD_OUT_TASK, STRESS_TASK, "PROTECT_001", "fresh context"):
            self.assertIn(revealed, brief)
        status = crq.status_report(out)
        self.assertEqual(len(status["missing_results"]), 8)

    def test_tampered_arm_bundle_blocks_the_freeze(self) -> None:
        out = self.open_run()
        self.grade(out, GOOD)
        write_text(out / "arms" / "baseline" / "cards" / TARGET, "tampered\n")
        with self.assertRaisesRegex(crq.CandidateQualificationError, "arms: .* changed after it was frozen"):
            crq.freeze_execution(out)

    def test_open_refuses_a_premature_arm_bundle(self) -> None:
        out = self.frozen_run()
        (out / "arms").mkdir()
        with self.assertRaisesRegex(crq.CandidateQualificationError, "already exists"):
            crq.open_execution(out)
        self.assertEqual(crq.load_run(out)[1]["state"], "candidate-frozen")


class FreezeExecutionTests(ExecutionFixture):
    def setUp(self) -> None:
        super().setUp()
        self.out = self.open_run()
        self.grade(self.out, GOOD)

    def assert_refused(self, message: str) -> None:
        before = (self.out / "controller" / "run.json").read_bytes()
        with self.assertRaisesRegex(crq.CandidateQualificationError, message):
            crq.freeze_execution(self.out)
        self.assertEqual((self.out / "controller" / "run.json").read_bytes(), before)

    def test_complete_results_freeze_with_their_evidence(self) -> None:
        run = crq.freeze_execution(self.out)
        self.assertEqual(run["state"], "execution-frozen")
        record = json.loads((self.out / "controller" / "execution.freeze.json").read_text(encoding="utf-8"))
        paths = {item["path"] for item in record["files"]}
        self.assertIn("cases/TARGET_001/candidate/result.json", paths)
        self.assertIn("cases/TARGET_001/candidate/evidence/output.txt", paths)
        self.assertEqual(len(paths), 16)
        self.assertEqual(crq.status_report(self.out)["missing_results"], [])

    def test_ungraded_template_is_refused(self) -> None:
        out = self.open_run("SE_CRQ_0002")
        self.out = out
        self.assert_refused("verdict must be one of")

    def test_partial_verdict_is_refused(self) -> None:
        self.fill(self.out, "TARGET_001", "candidate", "partial")
        self.assert_refused("no partial result")

    def test_pass_and_fail_are_all_or_nothing(self) -> None:
        result = self.fill(self.out, "TARGET_001", "candidate", "pass")
        result["criteria"][0]["result"] = "fail"
        crq.write_json_atomic(self.result_path(self.out, "TARGET_001", "candidate"), result)
        self.assert_refused("a pass needs every criterion to pass")
        result.update(verdict="fail")
        result["criteria"][0]["result"] = "pass"
        crq.write_json_atomic(self.result_path(self.out, "TARGET_001", "candidate"), result)
        self.assert_refused("must name at least one failing criterion")

    def test_criteria_grade_the_frozen_contract(self) -> None:
        self.fill(self.out, "TARGET_001", "candidate", "pass",
                  criteria=[{"criterion": "Something easier.", "result": "pass", "evidence": "evidence/output.txt"}])
        self.assert_refused("frozen success_contract")
        self.fill(self.out, "TARGET_001", "candidate", "pass",
                  criteria=[{"criterion": "The owner outlives every view.", "result": "not-assessed",
                             "evidence": "x"}])
        self.assert_refused("graded pass or fail")

    def test_invalid_needs_a_reason_and_is_never_a_fail(self) -> None:
        self.fill(self.out, "TARGET_001", "candidate", "invalid", invalid_reason=" ")
        self.assert_refused("records invalid_reason")
        self.fill(self.out, "TARGET_001", "candidate", "fail", invalid_reason="tool crashed")
        self.assert_refused("invalid_reason belongs only to an invalid verdict")

    def test_evidence_manifest_is_required_and_verified(self) -> None:
        self.fill(self.out, "TARGET_001", "candidate", "pass", evidence_manifest=[])
        self.assert_refused("needs its evidence listed")
        self.fill(self.out, "TARGET_001", "candidate", "pass")
        write_text(self.out / "cases" / "TARGET_001" / "candidate" / "evidence" / "output.txt", "edited\n")
        self.assert_refused("does not match its sha256")
        self.fill(self.out, "TARGET_001", "candidate", "pass")
        write_text(self.out / "cases" / "TARGET_001" / "candidate" / "evidence" / "extra.txt", "x\n")
        self.assert_refused("not listed in evidence_manifest")

    def test_evidence_paths_are_bounded(self) -> None:
        for path, message in (("../baseline/result.json", "bounded"), ("result.json", "under evidence/")):
            with self.subTest(path=path):
                self.fill(self.out, "TARGET_001", "candidate", "pass",
                          evidence_manifest=[{"path": path, "sha256": "0" * 64, "kind": "x"}])
                self.assert_refused(message)

    def test_required_semantic_case_needs_a_separate_evaluator(self) -> None:
        self.fill(self.out, "PROTECT_001", "candidate", "pass", evaluator_relation="same-reader")
        self.assert_refused("differs from the planned 'separate'")

    def test_deterministic_case_records_a_deterministic_relation(self) -> None:
        self.fill(self.out, "DET_001", "candidate", "pass",
                  executor={"kind": "tool", "runtime": "unittest", "model": None})
        self.assertEqual(crq.freeze_execution(self.out)["state"], "execution-frozen")
        self.assertEqual(
            json.loads(self.result_path(self.out, "DET_001", "candidate").read_text(encoding="utf-8"))["evaluator_relation"],
            "deterministic")

    def test_contamination_rules(self) -> None:
        self.fill(self.out, "TARGET_001", "candidate", "pass", contamination="suspected")
        self.assert_refused("suspected contamination must be resolved")
        self.fill(self.out, "TARGET_001", "candidate", "pass", contamination="confirmed")
        self.assert_refused("confirmed contamination makes the arm invalid")
        self.fill(self.out, "TARGET_001", "candidate", "invalid", contamination="bogus")
        self.assert_refused("contamination must be one of")

    def test_executor_and_shape(self) -> None:
        self.fill(self.out, "TARGET_001", "candidate", "pass",
                  executor={"kind": "ai", "runtime": "host", "model": ""})
        self.assert_refused("names its model")
        self.fill(self.out, "TARGET_001", "candidate", "pass", score=0.9)
        self.assert_refused("must have exactly")
        result = self.fill(self.out, "TARGET_001", "candidate", "pass")
        result.pop("score")
        crq.write_json_atomic(self.result_path(self.out, "TARGET_001", "candidate"), dict(result, arm="baseline"))
        self.assert_refused("different case, arm or schema")

    def test_unexpected_files_in_an_arm_are_refused(self) -> None:
        write_text(self.out / "cases" / "TARGET_001" / "candidate" / "summary.md", "x\n")
        self.assert_refused("unexpected summary.md")


class EvaluateTests(ExecutionFixture):
    def evaluated(self, verdicts: dict[str, tuple[str, str]], run_id: str = "SE_CRQ_0001",
                  entries: list[dict] | None = None, gap: str | None = None, **per_arm) -> Path:
        out = self.open_run(run_id, entries=entries, gap=gap)
        self.grade(out, verdicts)
        for (case_id, arm), changes in per_arm.get("changes", {}).items():
            self.fill(out, case_id, arm, verdicts[case_id][0 if arm == "baseline" else 1], **changes)
        crq.freeze_execution(out)
        crq.evaluate(out)
        return out

    def test_fixture_a_clean_repair_qualifies_without_touching_canon(self) -> None:
        library_before = self.library_bytes()
        out = self.evaluated(GOOD)
        result = self.result(out)
        self.assertEqual(result["status"], "qualified-for-synthesis-review")
        self.assertEqual(sorted(result["positive_qualification_cases"]), ["DET_001", "TARGET_001"])
        self.assertEqual(result["synthetic_cases"], ["STRESS_001"])
        self.assertEqual({d["case_id"]: d["delta"] for d in result["case_deltas"]}, {
            "TARGET_001": "improved", "PROTECT_001": "stable", "STRESS_001": "stable", "DET_001": "improved",
        })
        self.assertEqual(result["change_accounting"][0]["accounting"], "accepted-for-synthesis-review")
        self.assertFalse(result["canon_modified"])
        self.assertEqual(self.library_bytes(), library_before)
        run = crq.load_run(out)[1]
        self.assertEqual(run["state"], "evaluated")
        self.assertIn("result", run["freezes"])
        self.assertEqual(crq.status_report(out)["gate"], "qualified-for-synthesis-review")

    def test_fixture_b_regression_vetoes_two_improvements(self) -> None:
        entries = [
            plan_entry("TARGET_001"),
            plan_entry("TARGET_002", purpose="A second demonstrated missing condition."),
            default_plan_entries()[1],
        ]
        out = self.evaluated({"TARGET_001": ("fail", "pass"), "TARGET_002": ("fail", "pass"),
                              "PROTECT_001": ("pass", "fail")}, entries=entries)
        result = self.result(out)
        self.assertEqual(result["status"], "rejected-regression")
        self.assertEqual(result["blocking_cases"], ["PROTECT_001"])
        self.assertEqual(result["positive_qualification_cases"], [])
        self.assertEqual(result["change_accounting"][0]["accounting"], "rejected-by-qualification")

    def test_protection_gap_run(self) -> None:
        target, _protect, stress = default_plan_entries()[:3]
        out = self.evaluated({"TARGET_001": ("fail", "pass"), "STRESS_001": ("pass", "pass")},
                             entries=[target, stress], gap="No independent protected case exists yet.")
        result = self.result(out)
        self.assertEqual(result["status"], "inconclusive-protection-gap")
        self.assertEqual(result["protected_case_gap"], "No independent protected case exists yet.")
        self.assertEqual(result["change_accounting"][0]["accounting"], "applied-to-candidate")

    def test_invalid_arm_is_not_a_candidate_failure(self) -> None:
        out = self.evaluated(dict(GOOD, TARGET_001=("fail", "invalid")))
        result = self.result(out)
        self.assertEqual(result["status"], "invalid")
        self.assertEqual(result["blocking_cases"], ["TARGET_001"])

    def test_case_hash_mismatch_invalidates_the_comparison(self) -> None:
        out = self.evaluated(GOOD, changes={("PROTECT_001", "candidate"): {"case_sha256": "0" * 64}})
        result = self.result(out)
        delta = next(d for d in result["case_deltas"] if d["case_id"] == "PROTECT_001")
        self.assertEqual(delta["delta"], "invalid")
        self.assertIn("different case definition", delta["comparison_problems"][0])
        self.assertEqual(result["status"], "invalid")

    def test_environment_mismatch_invalidates_the_comparison(self) -> None:
        out = self.evaluated(GOOD, changes={("DET_001", "baseline"): {"environment": {"toolchain": "older"}}})
        delta = next(d for d in self.result(out)["case_deltas"] if d["case_id"] == "DET_001")
        self.assertEqual(delta["delta"], "invalid")
        self.assertEqual(delta["comparison_problems"], ["the arms declare different environments"])

    def test_confirmed_contamination_anywhere_invalidates_the_batch(self) -> None:
        entries = [*default_plan_entries(),
                   plan_entry("DIAG_001", role="protected", required=False, evaluator_relation="same-reader",
                              positive_qualification_eligible=False, source_event_ids=["SE_EV_0002"])]
        out = self.evaluated(dict(GOOD, DIAG_001=("pass", "invalid")), entries=entries,
                             changes={("DIAG_001", "candidate"): {"contamination": "confirmed"}})
        result = self.result(out)
        self.assertTrue(result["contamination_confirmed"])
        self.assertEqual(result["status"], "invalid")

    def test_frozen_result_cannot_be_edited_before_finalize(self) -> None:
        out = self.evaluated(GOOD)
        path = out / "qualification_result.json"
        write_text(path, path.read_text(encoding="utf-8").replace("qualified-for-synthesis-review", "invalid"))
        with self.assertRaisesRegex(crq.CandidateQualificationError, "changed after it was frozen"):
            crq.apply_transition(out, "finalize")

    def test_result_document_shape(self) -> None:
        result = self.result(self.evaluated(GOOD))
        self.assertEqual(set(result), set(crq.QUALIFICATION_RESULT_KEYS))
        self.assertEqual(result["candidate_memory_entry"], "SE_MEM_0001")
        self.assertEqual(result["changed_objects"], ["PAT_target"])


class CommandLineTests(ExecutionFixture):
    def cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, str(CONTROLLER), *args],
                              text=True, encoding="utf-8", capture_output=True)

    def test_execution_commands(self) -> None:
        out = self.frozen_run()
        result = self.cli("open-execution", "--run", str(out))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("EXECUTION OPEN", result.stdout)
        failed = self.cli("freeze-execution", "--run", str(out))
        self.assertEqual(failed.returncode, 2)
        self.assertIn("execution cannot be frozen", failed.stderr)
        self.grade(out, GOOD)
        for command, expected in (("freeze-execution", "EXECUTION FROZEN"),
                                  ("evaluate", "qualified-for-synthesis-review; canon was not modified")):
            result = self.cli(command, "--run", str(out))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(expected, result.stdout)


if __name__ == "__main__":
    unittest.main()
