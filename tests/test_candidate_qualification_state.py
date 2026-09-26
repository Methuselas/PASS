"""Contracts for the Candidate Refinement & Qualification controller skeleton.

Covers the run state machine, atomic persistence and read-back, the controller
fingerprint, path containment, frozen-file hashes, and baseline drift. The
fixture library is synthetic; no canonical card is read or written.
"""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
CONTROLLER = ROOT / "PASS" / "runtime" / "pass_candidate_qualification.py"


def load_controller(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


crq = load_controller(CONTROLLER, "pass_candidate_qualification")

TARGET = "software-engineering/core/PAT_example.md"
SUPPORT = "software-engineering/core/PAT_support.md"
MODULE = "software-engineering/core/MODULE.yaml"
UNRELATED = "software-engineering/core/PAT_unrelated.md"
LIFECYCLE_COMMANDS = list(crq.TRANSITIONS)


def card(object_id: str) -> str:
    return f"---\nobject_id: {object_id}\nobject_type: pattern\n---\n\n# {object_id}\n"


class CandidateRunFixture(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name)
        self.library = self.base / "library"
        self.memory = self.base / "memory"
        self.memory.mkdir()
        for relative, text in (
            (TARGET, card("PAT_example")),
            (SUPPORT, card("PAT_support")),
            (UNRELATED, card("PAT_unrelated")),
            (MODULE, "module: core\n"),
        ):
            path = self.library / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        self.workspace = self.base / "workspace" / "candidate-qualification"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def populate(self, staging: Path, run: dict) -> None:
        entries = [
            crq.baseline_entry(self.library, TARGET, "PAT_example", "target"),
            crq.baseline_entry(self.library, SUPPORT, "PAT_support", "support"),
            crq.baseline_entry(self.library, MODULE, None, "module-manifest"),
        ]
        for entry in entries:
            destination = staging / "baseline" / "cards" / entry["relative_path"]
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(self.library / entry["relative_path"], destination)
        path = staging / run["files"]["baseline_manifest"]
        crq.write_json_atomic(path, {
            "schema_version": crq.SCHEMA_VERSION,
            "run_id": run["run_id"],
            "entries": entries,
        })
        run["baseline_manifest_sha256"] = crq.digest_file(path)

    def make_run(self, run_id: str = "SE_CRQ_0001") -> Path:
        out = self.workspace / "software-engineering" / run_id
        record = crq.new_run_record(
            run_id=run_id,
            domain="software-engineering",
            memory_entry_id="SE_MEM_0042",
            library_root=self.library,
            memory_root=self.memory,
        )
        crq.initialize_run(out, record, self.populate)
        return out

    def advance_to(self, run_dir: Path, state: str) -> None:
        for command in LIFECYCLE_COMMANDS:
            if crq.load_run(run_dir)[1]["state"] == state:
                return
            crq.apply_transition(run_dir, command)
        self.assertEqual(crq.load_run(run_dir)[1]["state"], state)

    def run_bytes(self, run_dir: Path) -> bytes:
        return (run_dir / "controller" / "run.json").read_bytes()

    def state(self, run_dir: Path) -> str:
        return crq.load_run(run_dir)[1]["state"]


class StateMachineTests(CandidateRunFixture):
    def test_transition_table_is_the_designed_linear_lifecycle(self) -> None:
        self.assertEqual(
            [(command, *crq.TRANSITIONS[command]) for command in crq.TRANSITIONS],
            [
                ("freeze-assessment", "prepared", "assessment-frozen"),
                ("freeze-plan", "assessment-frozen", "plan-frozen"),
                ("stage-candidate", "plan-frozen", "candidate-staged"),
                ("freeze-candidate", "candidate-staged", "candidate-frozen"),
                ("open-execution", "candidate-frozen", "execution-open"),
                ("freeze-execution", "execution-open", "execution-frozen"),
                ("evaluate", "execution-frozen", "evaluated"),
                ("finalize", "evaluated", "finalized"),
            ],
        )
        self.assertEqual(crq.CLOSING_COMMANDS, {"invalidate": "invalidated", "abandon": "abandoned"})
        self.assertEqual(crq.TERMINAL_STATES, {"finalized", "invalidated", "abandoned"})

    def test_prepare_creates_a_prepared_run_with_frozen_baseline(self) -> None:
        run_dir = self.make_run()
        root, run = crq.load_run(run_dir)
        self.assertEqual(run["state"], "prepared")
        self.assertEqual(run["history"][0]["command"], "prepare")
        self.assertEqual(run["scope_limits"], {"max_changed_cards": 3, "max_new_cards": 2})
        self.assertEqual(crq.baseline_drift(root, run), [])
        self.assertTrue((run_dir / "baseline" / "cards" / TARGET).is_file())
        self.assertEqual(
            [path.name for path in run_dir.parent.iterdir()], ["SE_CRQ_0001"],
            "no staging directory may be left beside the run",
        )

    def test_full_lifecycle_walk_records_every_transition_and_leaves_canon(self) -> None:
        before = {path: path.read_bytes() for path in self.library.rglob("*") if path.is_file()}
        run_dir = self.make_run()
        for command in LIFECYCLE_COMMANDS:
            run = crq.apply_transition(run_dir, command)
            self.assertEqual(run["state"], crq.TRANSITIONS[command][1])
            self.assertEqual(crq.load_run(run_dir)[1], run)
        history = crq.load_run(run_dir)[1]["history"]
        self.assertEqual([item["command"] for item in history], ["prepare", *LIFECYCLE_COMMANDS])
        after = {path: path.read_bytes() for path in self.library.rglob("*") if path.is_file()}
        self.assertEqual(before, after)

    def test_wrong_state_command_fails_without_changing_state(self) -> None:
        for state in crq.LIFECYCLE_STATES[:-1]:
            with self.subTest(state=state):
                run_dir = self.make_run(f"SE_CRQ_{crq.LIFECYCLE_STATES.index(state) + 1:04d}")
                self.advance_to(run_dir, state)
                before = self.run_bytes(run_dir)
                for command, (required, _target) in crq.TRANSITIONS.items():
                    if required == state:
                        continue
                    with self.assertRaisesRegex(crq.CandidateQualificationError, "requires state"):
                        crq.apply_transition(run_dir, command)
                    self.assertEqual(self.run_bytes(run_dir), before)

    def test_unknown_command_is_refused(self) -> None:
        run_dir = self.make_run()
        before = self.run_bytes(run_dir)
        for command in ("prepare", "invalidate", "promote", "install"):
            with self.subTest(command=command):
                with self.assertRaises(crq.CandidateQualificationError):
                    crq.apply_transition(run_dir, command)
        self.assertEqual(self.run_bytes(run_dir), before)

    def test_invalidate_and_abandon_from_every_nonterminal_state(self) -> None:
        number = 0
        for state in crq.LIFECYCLE_STATES[:-1]:
            for command, target, key in (
                ("invalidate", "invalidated", "invalid_reason"),
                ("abandon", "abandoned", "abandoned_reason"),
            ):
                number += 1
                with self.subTest(state=state, command=command):
                    run_dir = self.make_run(f"SE_CRQ_{number:04d}")
                    self.advance_to(run_dir, state)
                    run = crq.close_run(run_dir, command, "  stopped for the test  ")
                    self.assertEqual(run["state"], target)
                    self.assertEqual(run[key], "stopped for the test")
                    self.assertEqual(run["history"][-1]["from"], state)

    def test_terminal_runs_are_read_only_except_status(self) -> None:
        finalized = self.make_run("SE_CRQ_0001")
        self.advance_to(finalized, "finalized")
        invalidated = self.make_run("SE_CRQ_0002")
        crq.invalidate(invalidated, "contamination confirmed")
        abandoned = self.make_run("SE_CRQ_0003")
        crq.abandon(abandoned, "no longer needed")
        for run_dir in (finalized, invalidated, abandoned):
            state = self.state(run_dir)
            before = self.run_bytes(run_dir)
            with self.subTest(state=state):
                for command in LIFECYCLE_COMMANDS:
                    with self.assertRaisesRegex(crq.CandidateQualificationError, "read-only"):
                        crq.apply_transition(run_dir, command)
                for command in crq.CLOSING_COMMANDS:
                    with self.assertRaisesRegex(crq.CandidateQualificationError, "read-only"):
                        crq.close_run(run_dir, command, "again")
                self.assertEqual(self.run_bytes(run_dir), before)
                self.assertEqual(crq.status_report(run_dir)["state"], state)
                self.assertTrue(crq.status_report(run_dir)["terminal"])

    def test_closing_requires_a_reason(self) -> None:
        run_dir = self.make_run()
        before = self.run_bytes(run_dir)
        for command in crq.CLOSING_COMMANDS:
            with self.subTest(command=command):
                with self.assertRaisesRegex(crq.CandidateQualificationError, "reason"):
                    crq.close_run(run_dir, command, "   ")
        self.assertEqual(self.run_bytes(run_dir), before)

    def test_failed_command_work_leaves_state_unchanged(self) -> None:
        run_dir = self.make_run()
        before = self.run_bytes(run_dir)

        def failing(root: Path, run: dict) -> None:
            run["memory_entry_id"] = "changed"
            raise crq.CandidateQualificationError("assessment is not ready")

        with self.assertRaisesRegex(crq.CandidateQualificationError, "not ready"):
            crq.apply_transition(run_dir, "freeze-assessment", failing)
        self.assertEqual(self.run_bytes(run_dir), before)

        def sets_state(root: Path, run: dict) -> None:
            run["state"] = "finalized"

        with self.assertRaisesRegex(crq.CandidateQualificationError, "may not set state"):
            crq.apply_transition(run_dir, "freeze-assessment", sets_state)
        self.assertEqual(self.run_bytes(run_dir), before)


class PersistenceTests(CandidateRunFixture):
    def test_resume_reads_back_state_in_a_fresh_process(self) -> None:
        run_dir = self.make_run()
        crq.apply_transition(run_dir, "freeze-assessment")
        result = subprocess.run(
            [sys.executable, str(CONTROLLER), "status", "--run", str(run_dir)],
            text=True, encoding="utf-8", capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        status = json.loads(result.stdout)
        self.assertEqual(status["state"], "assessment-frozen")
        self.assertEqual(status["baseline"]["status"], "clean")
        self.assertTrue(status["controller_matches"])
        self.assertFalse(status["canon_modified"])
        crq.apply_transition(run_dir, "freeze-plan")
        self.assertEqual(self.state(run_dir), "plan-frozen")

    def test_interrupted_atomic_write_leaves_previous_state(self) -> None:
        run_dir = self.make_run()
        before = self.run_bytes(run_dir)
        with mock.patch.object(crq.os, "replace", side_effect=OSError("power lost")):
            with self.assertRaisesRegex(OSError, "power lost"):
                crq.apply_transition(run_dir, "freeze-assessment")
        self.assertEqual(self.run_bytes(run_dir), before)
        self.assertEqual(
            sorted(path.name for path in (run_dir / "controller").iterdir()),
            ["baseline_manifest.json", "run.json"],
            "the interrupted temporary file must be removed",
        )
        self.assertEqual(crq.apply_transition(run_dir, "freeze-assessment")["state"], "assessment-frozen")

    def test_read_back_mismatch_fails_loudly(self) -> None:
        run_dir = self.make_run()
        root, run = crq.load_run(run_dir)
        original = crq.stable_json

        def corrupting(value):
            if isinstance(value, dict) and "run_id" in value and "state" in value:
                value = dict(value, memory_entry_id="SE_MEM_9999")
            return original(value)

        with mock.patch.object(crq, "stable_json", corrupting):
            with self.assertRaisesRegex(crq.CandidateQualificationError, "read-back"):
                crq.save_run(root, run)

    def test_unsupported_schema_is_refused_not_migrated(self) -> None:
        run_dir = self.make_run()
        path = run_dir / "controller" / "run.json"
        run = json.loads(path.read_text(encoding="utf-8"))
        run["schema_version"] = 2
        path.write_text(json.dumps(run), encoding="utf-8")
        before = path.read_bytes()
        with self.assertRaisesRegex(crq.CandidateQualificationError, "does not migrate"):
            crq.apply_transition(run_dir, "freeze-assessment")
        with self.assertRaisesRegex(crq.CandidateQualificationError, "does not migrate"):
            crq.status_report(run_dir)
        self.assertEqual(path.read_bytes(), before)

    def test_malformed_run_records_are_refused(self) -> None:
        run_dir = self.make_run()
        path = run_dir / "controller" / "run.json"
        pristine = json.loads(path.read_text(encoding="utf-8"))
        cases = {
            "unknown key": dict(pristine, promoted=True),
            "missing key": {k: v for k, v in pristine.items() if k != "memory_root"},
            "reason outside its state": dict(pristine, invalid_reason="early"),
            "unknown state": dict(pristine, state="qualified"),
            "history disagrees": dict(pristine, state="plan-frozen"),
            "bad run id": dict(pristine, run_id="crq-1"),
            "escaping file path": dict(pristine, files=dict(pristine["files"], assessment="../a.json")),
        }
        for label, record in cases.items():
            with self.subTest(case=label):
                path.write_text(json.dumps(record), encoding="utf-8")
                with self.assertRaises(crq.CandidateQualificationError):
                    crq.load_run(run_dir)

    def test_scope_ceiling_override_is_recorded_and_bounded(self) -> None:
        common = dict(
            run_id="SE_CRQ_0001", domain="software-engineering",
            memory_entry_id="SE_MEM_0042", library_root=self.library, memory_root=self.memory,
        )
        with self.assertRaisesRegex(crq.CandidateQualificationError, "override_reason"):
            crq.new_run_record(**common, max_changed_cards=5)
        run = crq.new_run_record(**common, max_changed_cards=5, override_reason="one family of cards")
        self.assertEqual(run["scope_limits"]["max_changed_cards"], 5)
        self.assertEqual(run["scope_limits"]["override_reason"], "one family of cards")
        tightened = crq.new_run_record(**common, max_new_cards=0)
        self.assertEqual(tightened["scope_limits"]["max_new_cards"], 0)
        for extra in ("max_deleted_cards", "max_renamed_object_ids", "max_moved_cards"):
            with self.subTest(extra=extra):
                record = dict(run, scope_limits=dict(run["scope_limits"], **{extra: 1}))
                self.assertTrue(
                    any("never enabled" in error for error in crq.validate_run_record(record))
                )

    def test_initialize_requires_baseline_and_refuses_overwrite(self) -> None:
        out = self.workspace / "software-engineering" / "SE_CRQ_0001"
        record = crq.new_run_record(
            run_id="SE_CRQ_0001", domain="software-engineering",
            memory_entry_id="SE_MEM_0042", library_root=self.library, memory_root=self.memory,
        )
        with self.assertRaises(crq.BaselineDriftError):
            crq.initialize_run(out, dict(record))
        self.assertFalse(out.exists())
        self.assertEqual(list(out.parent.iterdir()), [], "failed prepare must leave no staging")
        self.make_run()
        with self.assertRaisesRegex(crq.CandidateQualificationError, "overwrite"):
            crq.initialize_run(out, record, self.populate)


class ControllerFingerprintTests(CandidateRunFixture):
    def test_prepare_records_the_controller_hash(self) -> None:
        run = crq.load_run(self.make_run())[1]
        self.assertEqual(run["controller_sha256"], crq.digest_file(CONTROLLER))

    def test_changed_controller_cannot_continue_or_close_a_run(self) -> None:
        run_dir = self.make_run()
        crq.apply_transition(run_dir, "freeze-assessment")
        changed = self.base / "changed_controller.py"
        changed.write_text(
            CONTROLLER.read_text(encoding="utf-8") + "\n# administration rules changed\n",
            encoding="utf-8",
        )
        other = load_controller(changed, "pass_candidate_qualification_changed")
        before = self.run_bytes(run_dir)
        with self.assertRaises(other.ControllerMismatchError):
            other.apply_transition(run_dir, "freeze-plan")
        with self.assertRaises(other.ControllerMismatchError):
            other.invalidate(run_dir, "controller changed")
        self.assertEqual(self.run_bytes(run_dir), before)
        status = other.status_report(run_dir)
        self.assertFalse(status["controller_matches"])
        self.assertEqual(status["state"], "assessment-frozen")
        self.assertEqual(crq.apply_transition(run_dir, "freeze-plan")["state"], "plan-frozen")


class ContainmentTests(CandidateRunFixture):
    def test_relative_paths_must_be_bounded(self) -> None:
        self.assertEqual(crq.safe_relative("a/b.md", "path").as_posix(), "a/b.md")
        for value in ("", "../x", "a/../../x", "/abs", "C:/x", "C:x", "a\\b", "a/./b", "a//b", "a/", 7):
            with self.subTest(value=value):
                with self.assertRaises(crq.CandidateQualificationError):
                    crq.safe_relative(value, "path")

    def test_symlink_cannot_escape_the_run(self) -> None:
        root = self.base / "run"
        root.mkdir()
        outside = self.base / "outside"
        outside.mkdir()
        try:
            os.symlink(outside, root / "link", target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks are unavailable here")
        with self.assertRaisesRegex(crq.CandidateQualificationError, "escapes"):
            crq.contained(root, "link/evidence.txt", "evidence")

    def test_baseline_manifest_paths_are_bounded(self) -> None:
        manifest = {
            "schema_version": crq.SCHEMA_VERSION,
            "run_id": "SE_CRQ_0001",
            "entries": [
                {"relative_path": "../outside.md", "object_id": "X", "sha256": "0" * 64, "role": "target"},
                {"relative_path": "a.md", "object_id": None, "sha256": "0" * 64, "role": "target"},
                {"relative_path": "b.md", "object_id": "Y", "sha256": "0" * 64, "role": "owner"},
            ],
        }
        errors = crq.validate_baseline_manifest(manifest, "SE_CRQ_0001")
        self.assertTrue(any("bounded" in error for error in errors))
        self.assertTrue(any("requires object_id" in error for error in errors))
        self.assertTrue(any("unknown role" in error for error in errors))


class DriftTests(CandidateRunFixture):
    def assert_blocked(self, run_dir: Path, pattern: str = "baseline") -> None:
        before = self.run_bytes(run_dir)
        with self.assertRaisesRegex(crq.CandidateQualificationError, pattern):
            crq.apply_transition(run_dir, "freeze-assessment")
        self.assertEqual(self.run_bytes(run_dir), before)
        self.assertEqual(self.state(run_dir), "prepared")

    def test_changed_canonical_baseline_file_blocks_continuation(self) -> None:
        for number, relative in enumerate((TARGET, SUPPORT, MODULE), start=1):
            with self.subTest(file=relative):
                run_dir = self.make_run(f"SE_CRQ_{number:04d}")
                path = self.library / relative
                original = path.read_bytes()
                path.write_bytes(original + b"\nedited in canon\n")
                try:
                    self.assert_blocked(run_dir)
                    status = crq.status_report(run_dir)
                    self.assertEqual(status["baseline"]["status"], "drifted")
                    self.assertIn(f"canonical baseline file changed: {relative}", status["baseline"]["problems"])
                finally:
                    path.write_bytes(original)
                self.assertEqual(crq.apply_transition(run_dir, "freeze-assessment")["state"], "assessment-frozen")

    def test_deleted_canonical_baseline_file_blocks_continuation(self) -> None:
        run_dir = self.make_run()
        (self.library / TARGET).unlink()
        self.assert_blocked(run_dir, "missing")

    def test_unrelated_library_change_does_not_block(self) -> None:
        run_dir = self.make_run()
        (self.library / UNRELATED).write_text(card("PAT_unrelated") + "\nrevised\n", encoding="utf-8")
        (self.library / "software-engineering" / "core" / "PAT_new.md").write_text(card("PAT_new"), encoding="utf-8")
        self.assertEqual(crq.apply_transition(run_dir, "freeze-assessment")["state"], "assessment-frozen")

    def test_edited_baseline_snapshot_blocks_continuation(self) -> None:
        run_dir = self.make_run()
        (run_dir / "baseline" / "cards" / TARGET).write_text("tampered\n", encoding="utf-8")
        self.assert_blocked(run_dir, "snapshot baseline file changed")

    def test_edited_baseline_manifest_blocks_continuation(self) -> None:
        run_dir = self.make_run()
        path = run_dir / "controller" / "baseline_manifest.json"
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["entries"] = manifest["entries"][:1]
        path.write_text(json.dumps(manifest), encoding="utf-8")
        self.assert_blocked(run_dir, "manifest changed")

    def test_drifted_run_can_still_be_invalidated(self) -> None:
        run_dir = self.make_run()
        (self.library / TARGET).write_text("rewritten\n", encoding="utf-8")
        run = crq.invalidate(run_dir, "baseline drift in canon")
        self.assertEqual(run["state"], "invalidated")

    def test_frozen_run_files_are_hash_checked(self) -> None:
        run_dir = self.make_run()
        assessment = run_dir / "controller" / "assessment.json"
        crq.write_json_atomic(assessment, {"candidate_disposition": "canon-candidate"})

        def freeze(root: Path, run: dict) -> None:
            crq.record_freeze(root, run, "assessment", ["controller/assessment.json"])

        run = crq.apply_transition(run_dir, "freeze-assessment", freeze)
        self.assertIn("assessment", run["freezes"])
        self.assertEqual(crq.status_report(run_dir)["assessment"], "frozen")

        def refreeze(root: Path, run: dict) -> None:
            crq.record_freeze(root, run, "assessment", ["controller/assessment.json"])

        with self.assertRaisesRegex(crq.CandidateQualificationError, "already frozen"):
            crq.apply_transition(run_dir, "freeze-plan", refreeze)

        original = assessment.read_bytes()
        assessment.write_text('{"candidate_disposition": "memory-only"}\n', encoding="utf-8")
        before = self.run_bytes(run_dir)
        with self.assertRaisesRegex(crq.CandidateQualificationError, "changed after it was frozen"):
            crq.apply_transition(run_dir, "freeze-plan")
        self.assertEqual(self.run_bytes(run_dir), before)
        self.assertEqual(crq.status_report(run_dir)["frozen_files"]["status"], "changed")

        assessment.write_bytes(original)
        record = run_dir / "controller" / "assessment.freeze.json"
        record.write_text(record.read_text(encoding="utf-8").replace('"files"', '"files" ', 1), encoding="utf-8")
        with self.assertRaisesRegex(crq.CandidateQualificationError, "freeze record changed"):
            crq.apply_transition(run_dir, "freeze-plan")

    def test_cannot_freeze_a_missing_file(self) -> None:
        run_dir = self.make_run()

        def freeze(root: Path, run: dict) -> None:
            crq.record_freeze(root, run, "assessment", ["controller/assessment.json"])

        with self.assertRaisesRegex(crq.CandidateQualificationError, "missing file"):
            crq.apply_transition(run_dir, "freeze-assessment", freeze)
        self.assertEqual(self.state(run_dir), "prepared")


class CommandLineTests(CandidateRunFixture):
    def cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(CONTROLLER), *args],
            text=True, encoding="utf-8", capture_output=True,
        )

    def test_invalidate_and_abandon_commands(self) -> None:
        first = self.make_run("SE_CRQ_0001")
        result = self.cli("invalidate", "--run", str(first), "--reason", "fixture was wrong")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("INVALIDATED", result.stdout)
        self.assertEqual(crq.load_run(first)[1]["invalid_reason"], "fixture was wrong")
        again = self.cli("abandon", "--run", str(first), "--reason", "late")
        self.assertEqual(again.returncode, 2)
        self.assertIn("read-only", again.stderr)

        second = self.make_run("SE_CRQ_0002")
        result = self.cli("abandon", "--run", str(second), "--reason", "superseded by a narrower candidate")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.state(second), "abandoned")

    def test_status_of_a_missing_run_fails_cleanly(self) -> None:
        result = self.cli("status", "--run", str(self.base / "nothing"))
        self.assertEqual(result.returncode, 2)
        self.assertIn("not a CRQ run", result.stderr)

    def test_controller_calls_no_model_and_writes_no_canon(self) -> None:
        source = CONTROLLER.read_text(encoding="utf-8")
        for forbidden in ("import anthropic", "import openai", "import requests", "urllib.request", "subprocess"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
