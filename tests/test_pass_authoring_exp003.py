"""EXP-003 portable transaction & recovery invariants.

Each test maps to one required invariant of the EXP-003 handoff: degraded
checkpoint outcomes, pre-validation budget failures, the residue gate,
non-destructive repair, explicit recover rollback audit, content-addressed
checkpoint budget headroom, amendment-baseline materialization, close-run
lifecycle, typed import failures, close residue refusal, legacy run migration,
the legacy accepted-files fallback, export/import blob round-trips, and the
present-degraded packet-sha declaration.
"""

import contextlib
import hashlib
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

try:
    import test_pass_authoring_workflow as harness
except ImportError:  # discovery with the repository as top-level directory
    from tests import test_pass_authoring_workflow as harness

card = harness.card

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "PASS"))
from runtime import pass_authoring_workflow as workflow

LONG_CARD = (
    "PAT_choose_a_class_decorator_over_a_metaclass_unless_construction_or_"
    "metaclass_methods_are_needed.md"
)


class Exp003TransactionTests(unittest.TestCase):
    """EXP-003 invariants built on the shared EXP-002 authoring fixture.

    The fixture is composed (not subclassed) so discovery never re-runs the
    inherited EXP-002 suite under a second class.
    """

    def setUp(self):
        self.h = harness.AuthoringWorkflowTests(methodName="runTest")
        self.h.setUp()
        self.addCleanup(self.h.doCleanups)

    # ------------------------------------------------------------ delegation
    @property
    def repo(self):
        return self.h.repo

    @property
    def root(self):
        return self.h.root

    @property
    def pass_run(self):
        return self.h.run

    @property
    def live(self):
        return self.h.live

    @property
    def temporary(self):
        return self.h.temporary

    @property
    def scratch(self):
        path = Path(tempfile.mkdtemp(prefix="exp003-"))
        self.addCleanup(shutil.rmtree, path, ignore_errors=True)
        return path

    def begin(self, *args, **kwargs):
        return self.h.begin(*args, **kwargs)

    def first(self, *args, **kwargs):
        return self.h.first(*args, **kwargs)

    def second(self, *args, **kwargs):
        return self.h.second(*args, **kwargs)

    def third(self, *args, **kwargs):
        return self.h.third(*args, **kwargs)

    def ready(self, *args, **kwargs):
        return self.h.ready(*args, **kwargs)

    def decision(self, *args, **kwargs):
        return self.h.decision(*args, **kwargs)

    def close_source(self):
        return self.h.close_source()

    def complete_pass2_attention(self, record):
        return self.h.complete_pass2_attention(record)

    # -------------------------------------------------------------- helpers
    def two_unit_refine_to_closure(self):
        """Accept two units whose deltas each refine a different live card."""
        second_card = self.live.parent / "PAT_compare_reading_effect.md"
        card(second_card, second_card.stem)
        self.begin(count=2)
        self.first()
        self.second(refine=True)
        self.third()
        self.pass_run.land(self.decision())
        self.first()
        real_live = self.h.live
        self.h.live = second_card
        try:
            self.second(refine=True)
        finally:
            self.h.live = real_live
        self.third()
        self.pass_run.land(self.decision())
        self.assertEqual(self.pass_run.state["phase"], "closure_pass2")
        return second_card

    def materialize_two_card_amendment(self):
        """Two accepted units, then reopen the previous unit's correction."""
        second_card = self.two_unit_refine_to_closure()
        message = self.pass_run.reopen_last_unit("Independent review found a source-fidelity defect.")
        return second_card, message

    # ------------------------------------------------- invariant 1 + repair
    def test_exp003_degraded_checkpoint_is_the_single_outcome_with_complete_facts(self):
        input_path = self.repo / "load-input.json"
        input_path.write_text(json.dumps(self.pass_run.template(), indent=2) + "\n", encoding="utf-8")
        real_rename = Path.rename

        def fail_fresh(path, target):
            if Path(path).name == "checkpoint.new":
                raise PermissionError(13, "injected fault", str(path))
            return real_rename(path, target)

        stdout, stderr = io.StringIO(), io.StringIO()
        with (
            patch.object(Path, "rename", new=fail_fresh),
            contextlib.redirect_stdout(stdout),
            contextlib.redirect_stderr(stderr),
        ):
            code = workflow.main([
                "--repo-root", str(self.repo), "submit",
                "--run", str(self.root), "--phase", "load", "--input", str(input_path),
            ])
        self.assertEqual(code, 2)
        self.assertEqual(stdout.getvalue(), "", "a degraded checkpoint must never print a success outcome")
        lines = [line for line in stderr.getvalue().splitlines() if line.strip()]
        self.assertEqual(len(lines), 1, "exactly one top-level outcome must be printed")
        self.assertTrue(lines[0].startswith("PASS RUN CHECKPOINT DEGRADED: "))
        record = json.loads(lines[0].split("PASS RUN CHECKPOINT DEGRADED: ", 1)[1])
        self.assertEqual(record["outcome"], "authoritative_state_persisted_checkpoint_not_advanced")
        self.assertIs(record["authoritative_state_persisted"], True)
        self.assertIs(record["checkpoint_advanced"], False)
        self.assertEqual(record["newer"], "authoritative")
        self.assertEqual(record["authoritative"]["phase"], "source_prep")
        self.assertIs(record["residue"]["checkpoint_new"], True)
        self.assertIs(record["residue"]["failure_record"], True)
        self.assertIn("injected fault", record["reason"])
        self.assertIn("repair-checkpoint", record["safe_to_continue"])
        self.assertIn("recover --rollback-authoritative", record["recovery"])
        self.assertEqual(record["operation_context"], {"command": "submit"})
        state = json.loads((self.root / "controller/run.json").read_text(encoding="utf-8"))
        self.assertEqual(state["phase"], "source_prep", "authoritative state must persist the completed command")
        self.assertFalse((self.root / "controller/checkpoint").exists())
        diagnostic = json.loads((self.root / "controller/checkpoint-failure.json").read_text(encoding="utf-8"))
        self.assertEqual(diagnostic["outcome"], record["outcome"])
        self.assertEqual(diagnostic["error_type"], "PermissionError")
        self.h.run.reload()
        message = self.h.run.repair_checkpoint()
        self.assertTrue(message.startswith("REPAIRED"))
        self.assertEqual(
            workflow.checkpoint_residue(self.root),
            {"checkpoint_new": False, "checkpoint_old": False, "failure_record": False},
        )
        manifest = self.h.run.checkpoint_manifest()
        self.assertEqual(manifest["state_sha256"], workflow.digest(self.h.run.state_path))

    # --------------------------------------------- invariant 1 (retire edge)
    def test_exp003_retire_edge_fault_keeps_settled_checkpoint_and_reports_complete_facts(self):
        """A PermissionError at the retire rename (checkpoint -> checkpoint.old)
        is a distinct transaction edge from the promote rename: the settled
        checkpoint must remain untouched in place, the fresh build is retained
        as residue, and the degraded record names every fact truthfully."""
        self.ready(refine=True)
        self.pass_run.land(self.decision())
        self.pass_run.checkpoint()
        settled_manifest = self.root / "controller/checkpoint/manifest.json"
        settled_digest = workflow.digest(settled_manifest)
        self.assertTrue(settled_manifest.is_file())

        staged = self.pass_run.staged_tree()
        target_name = next(name for name in staged if name.endswith(".md"))
        staged_path = self.root / target_name
        staged_path.write_bytes(staged_path.read_bytes() + b"\nmutation between checkpoints\n")

        real_rename = Path.rename

        def fail_retire(path, target):
            if Path(path).name == "checkpoint" and Path(target).name == "checkpoint.old":
                raise PermissionError(13, "injected retire fault", str(path))
            return real_rename(path, target)

        state_digest = workflow.digest(self.pass_run.state_path)
        with patch.object(Path, "rename", new=fail_retire):
            with self.assertRaises(workflow.CheckpointPromotionError) as caught:
                self.pass_run.checkpoint()
        record = caught.exception
        self.assertIn("injected retire fault", record.reason)
        self.assertIs(record.previous_checkpoint_restored, False,
                      "the retire never completed, so no restore action was taken")
        self.assertIs(record.fresh_checkpoint_retained, True)
        self.assertEqual(
            record.residue,
            {"checkpoint_new": True, "checkpoint_old": False, "failure_record": True},
        )
        self.assertEqual(record.authoritative["state_sha256"], state_digest)

        self.assertTrue(settled_manifest.is_file(), "the settled checkpoint must stay in place")
        self.assertEqual(workflow.digest(settled_manifest), settled_digest,
                         "the settled checkpoint must not be advanced or disturbed")
        self.assertFalse((self.root / "controller/checkpoint.old").exists())
        self.assertTrue((self.root / "controller/checkpoint.new").exists())
        self.assertEqual(workflow.digest(self.pass_run.state_path), state_digest,
                         "authoritative state must be untouched by the failed transaction")

        diagnostic = json.loads((self.root / "controller/checkpoint-failure.json").read_text(encoding="utf-8"))
        self.assertEqual(diagnostic["outcome"], "authoritative_state_persisted_checkpoint_not_advanced")
        self.assertEqual(diagnostic["error_type"], "PermissionError")
        self.assertIn("injected retire fault", diagnostic["reason"])
        self.assertIs(diagnostic["previous_checkpoint_restored"], False)
        self.assertIs(diagnostic["fresh_checkpoint_retained"], True)
        self.assertIs(diagnostic["checkpoint_present"], True)
        self.assertIs(diagnostic["retired_checkpoint_present"], False)
        self.assertEqual(diagnostic["authoritative"]["state_sha256"], state_digest)

        self.h.run.reload()
        message = self.h.run.repair_checkpoint()
        self.assertTrue(message.startswith("REPAIRED"))
        self.assertEqual(
            workflow.checkpoint_residue(self.root),
            {"checkpoint_new": False, "checkpoint_old": False, "failure_record": False},
        )
        advanced = self.h.run.checkpoint_manifest()
        self.assertEqual(advanced["state_sha256"], workflow.digest(self.h.run.state_path))

    # ------------------------------------------------------- invariant 2
    def test_exp003_budget_failure_leaves_zero_residue_directories(self):
        card(self.root / "drafts/craft/PAT_probe_budget_card.md", "PAT_probe_budget_card")
        real_validator = workflow.validate_windows_path_budget

        def fail_budget(path, label="path"):
            if "checkpoint blob" in label:
                raise workflow.RunError("injected budget failure")
            return real_validator(path, label)

        with patch.object(workflow, "validate_windows_path_budget", new=fail_budget):
            with self.assertRaises(workflow.CheckpointPromotionError) as caught:
                self.pass_run.checkpoint()
        self.assertIn("injected budget failure", caught.exception.reason)
        self.assertEqual(caught.exception.authoritative["phase"], "load")
        self.assertFalse((self.root / "controller/checkpoint.new").exists(), "pre-validation must precede mkdir")
        self.assertFalse((self.root / "controller/checkpoint").exists())
        self.assertEqual(
            workflow.checkpoint_residue(self.root),
            {"checkpoint_new": False, "checkpoint_old": False, "failure_record": True},
        )
        diagnostic = json.loads((self.root / "controller/checkpoint-failure.json").read_text(encoding="utf-8"))
        self.assertEqual(diagnostic["error_type"], "RunError")
        self.assertIn("injected budget failure", diagnostic["reason"])
        message = self.pass_run.repair_checkpoint()
        self.assertTrue(message.startswith("REPAIRED"))

    # ------------------------------------------------------- invariant 3
    def test_exp003_residue_gate_blocks_mutations_before_side_effects(self):
        fresh = self.root / "controller/checkpoint.new"
        fresh.mkdir(parents=True)
        state_before = (self.root / "controller/run.json").read_bytes()
        with self.assertRaises(workflow.ResidueBlockedError) as caught:
            with self.pass_run.locked(action="probe"):
                self.fail("the locked body must never run while residue is unresolved")
        record = caught.exception.as_record()
        self.assertEqual(record["outcome"], "blocked_checkpoint_residue")
        self.assertIs(record["side_effects"], False)
        self.assertIs(record["residue"]["checkpoint_new"], True)
        self.assertEqual(record["action"], "probe")
        self.assertEqual((self.root / "controller/run.json").read_bytes(), state_before)

        self.h.run.reload()
        brief = self.h.run.brief()
        self.assertIs(brief["checkpoint_residue"]["checkpoint_new"], True)
        self.assertTrue(brief["authorized_action"].startswith("UNRESOLVED CHECKPOINT RESIDUE"))

        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = workflow.main(["--repo-root", str(self.repo), "status", "--run", str(self.root)])
        self.assertEqual(code, 0, "status remains read-only under residue")
        payload = json.loads(stdout.getvalue())
        self.assertIs(payload["checkpoint_residue"]["checkpoint_new"], True)
        self.assertTrue(payload["authorized_action"].startswith("UNRESOLVED CHECKPOINT RESIDUE"))
        self.assertEqual(stderr.getvalue(), "")

        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = workflow.main(["--repo-root", str(self.repo), "continue-run", "--run", str(self.root)])
        self.assertEqual(code, 1)
        self.assertTrue(stderr.getvalue().startswith("PASS RUN BLOCKED: "))
        self.assertIn('"side_effects": false', stderr.getvalue())
        self.assertEqual(stdout.getvalue(), "")
        self.assertEqual((self.root / "controller/run.json").read_bytes(), state_before)

        shutil.rmtree(fresh)
        self.assertEqual(
            workflow.checkpoint_residue(self.root),
            {"checkpoint_new": False, "checkpoint_old": False, "failure_record": False},
        )

    # ------------------------------------------------- invariant 3 (present)
    def test_exp003_blocked_present_leaves_no_marker_or_audit_side_effects(self):
        self.ready(refine=True)
        self.assertEqual(self.pass_run.state["phase"], "land", "present would otherwise succeed here")
        marker = self.root / "controller/landing-presentation.json"
        landing_md = self.root / "controller/audit/u01-landing.md"
        self.assertFalse(marker.exists())
        self.assertFalse(landing_md.exists())
        state_before = (self.root / "controller/run.json").read_bytes()
        fresh = self.root / "controller/checkpoint.new"
        fresh.mkdir(parents=True)
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = workflow.main(["--repo-root", str(self.repo), "present", "--run", str(self.root)])
        self.assertEqual(code, 1)
        self.assertTrue(stderr.getvalue().startswith("PASS RUN BLOCKED: "))
        self.assertIn('"side_effects": false', stderr.getvalue())
        self.assertEqual(stdout.getvalue(), "")
        self.assertFalse(marker.exists(), "a residue-blocked present must not write the presentation marker")
        self.assertFalse(landing_md.exists(), "a residue-blocked present must not archive a landing packet")
        self.assertEqual((self.root / "controller/run.json").read_bytes(), state_before)
        shutil.rmtree(fresh)

    # ---------------------------------------------------- invariant 12
    def test_exp003_terminal_run_is_listed_but_never_selected_for_resume(self):
        self.ready(refine=True)
        self.pass_run.land(self.decision())
        self.close_source()
        self.assertEqual(self.pass_run.state["phase"], "finished")
        runs = workflow.list_registered_runs(self.repo, domain="writing")
        listed = [entry for entry in runs if entry["run_id"] == self.root.name]
        self.assertEqual(len(listed), 1, "terminal runs remain discoverable in the store")
        self.assertEqual(listed[0]["current"]["status"], "finished")
        result = workflow.resume(self.repo, domain="writing")
        self.assertEqual(result["outcome"], "no_incomplete_run")
        result = workflow.resume(self.repo, domain="writing", source=self.h.source)
        self.assertEqual(result["outcome"], "no_incomplete_run")
        self.assertNotIn(self.root.name, json.dumps(result))

    # ------------------------------------------------------- invariant 4
    def test_exp003_repair_checkpoint_is_non_destructive(self):
        self.pass_run.checkpoint()
        self.pass_run.state["stop_after"] = "source_prep"
        self.pass_run.save()
        state_sha = workflow.digest(self.pass_run.state_path)
        fresh = self.root / "controller/checkpoint.new"
        fresh.mkdir(parents=True)
        (self.root / "controller/checkpoint-failure.json").write_text(
            json.dumps({"schema_version": 2, "outcome": "authoritative_state_persisted_checkpoint_not_advanced"}) + "\n",
            encoding="utf-8",
        )
        message = self.pass_run.repair_checkpoint()
        self.assertTrue(message.startswith("REPAIRED"))
        self.assertIn("no data was rolled back", message)
        self.assertEqual(workflow.digest(self.pass_run.state_path), state_sha, "repair must not roll back state")
        self.assertEqual(self.pass_run.state["stop_after"], "source_prep")
        self.assertFalse(fresh.exists())
        self.assertFalse((self.root / "controller/checkpoint-failure.json").exists())
        manifest = self.pass_run.checkpoint_manifest()
        self.assertEqual(manifest["state_sha256"], state_sha)

    # ------------------------------------------------------- invariant 5
    def test_exp003_recover_refusal_and_explicit_rollback_leave_audit_evidence(self):
        self.pass_run.checkpoint()
        checkpoint_sha = self.pass_run.checkpoint_manifest()["state_sha256"]
        self.pass_run.state["stop_after"] = "source_prep"
        self.pass_run.save()
        authoritative_sha = workflow.digest(self.pass_run.state_path)
        history = self.root / "controller/action-history"
        with self.assertRaisesRegex(workflow.RunError, "refusing destructive recovery"):
            self.pass_run.recover()
        self.assertEqual(list(history.glob("rollback-authoritative-*.json")) if history.is_dir() else [], [],
                         "refusal must not write rollback evidence")
        self.assertEqual(workflow.digest(self.pass_run.state_path), authoritative_sha)
        message = self.pass_run.recover(rollback_authoritative=True)
        self.assertTrue(message.startswith("RECOVERED"))
        evidence = list(history.glob("rollback-authoritative-*.json"))
        self.assertEqual(len(evidence), 1, "the explicit destructive intent must leave audit evidence")
        record = json.loads(evidence[0].read_text(encoding="utf-8"))
        self.assertEqual(record["intent"], "explicit recover --rollback-authoritative")
        self.assertEqual(record["discarded_authoritative_sha256"], authoritative_sha)
        self.assertEqual(record["restored_checkpoint_sha256"], checkpoint_sha)
        self.assertEqual(workflow.digest(self.pass_run.state_path), checkpoint_sha)
        self.assertEqual(self.pass_run.state["stop_after"], "complete")

    # ------------------------------------------------------- invariant 6
    def test_exp003_long_card_checkpoint_paths_stay_content_addressed_within_budget(self):
        long_path = self.root / "drafts/craft/deep/nested/segments" / LONG_CARD
        card(long_path, Path(LONG_CARD).stem)
        self.pass_run.checkpoint()
        manifest = self.pass_run.checkpoint_manifest()
        staged = f"drafts/craft/deep/nested/segments/{LONG_CARD}"
        self.assertIn(staged, manifest["files"])
        blob_prefix = len("controller/checkpoint/blobs/")
        blob_lengths = set()
        for path in (self.root / "controller/checkpoint").rglob("*"):
            relative = path.relative_to(self.root).as_posix()
            workflow.validate_windows_path_budget(path, "checkpoint path")
            if f"controller/checkpoint/blobs/" in relative and path.is_file():
                blob_lengths.add(len(relative))
                self.assertTrue(all(c in "0123456789abcdef" for c in path.name))
                self.assertEqual(len(path.name), 64)
        self.assertEqual(blob_lengths, {blob_prefix + 64},
                         "blob destinations must be content-addressed and independent of staged depth")
        self.assertGreater(len(staged), blob_prefix + 64, "the long card path must outgrow its blob destination")

        base = Path("C:/") / ("d" * 40) / "workspace" / "runs" / "r_12345678" / "controller" / "checkpoint.new"
        workflow.validate_windows_path_budget(base / "blobs" / ("a" * 64), "content-addressed blob")
        legacy_style = base / "files" / "library" / "software-engineering" / "metaclasses" / LONG_CARD
        with self.assertRaises(workflow.RunError):
            workflow.validate_windows_path_budget(legacy_style, "legacy nested file")

    # ------------------------------------------------------- invariant 7
    def test_exp003_reopen_materializes_accepted_delta_as_amendment_baseline(self):
        second_card, message = self.materialize_two_card_amendment()
        self.assertIn("2 baseline card(s) materialized into drafts from the accepted source delta", message)
        staged = [f"drafts/craft/{self.live.name}", f"drafts/craft/{second_card.name}"]
        amendment = json.loads(
            (self.root / "controller/unit-history/u02/r002/amendment.json").read_text(encoding="utf-8")
        )
        self.assertEqual(amendment["from_revision"], "r001")
        self.assertEqual(set(amendment["materialized_baseline"]), set(staged))
        baseline = json.loads((self.root / "controller/amendment-baseline.json").read_text(encoding="utf-8"))
        self.assertEqual(baseline["schema_version"], 1)
        self.assertEqual(baseline["unit_id"], "u02")
        self.assertEqual(set(baseline["files"]), set(staged))
        for canon, name in (
            (f"library/writing/craft/{self.live.name}", staged[0]),
            (f"library/writing/craft/{second_card.name}", staged[1]),
        ):
            content = self.pass_run.read_accepted(canon)
            self.assertEqual((self.root / name).read_bytes(), content)
            self.assertEqual(baseline["files"][name], hashlib.sha256(content).hexdigest())
        self.assertFalse((self.root / "drafts/INDEX.md").exists(), "generated indexes are never materialized")
        self.assertEqual(self.pass_run.state["phase"], "pass2")
        self.assertEqual(self.pass_run.state["unit_index"], 1)

    # ------------------------------------------------------- invariant 8
    def test_exp003_close_retains_edited_baseline_work_and_discards_untouched_copies(self):
        second_card, _message = self.materialize_two_card_amendment()
        edited = self.root / f"drafts/craft/{self.live.name}"
        untouched = self.root / f"drafts/craft/{second_card.name}"
        baseline = json.loads((self.root / "controller/amendment-baseline.json").read_text(encoding="utf-8"))
        baseline_sha = {
            "edited": baseline["files"][f"drafts/craft/{self.live.name}"],
            "untouched": baseline["files"][f"drafts/craft/{second_card.name}"],
        }
        with edited.open("a", encoding="utf-8") as handle:
            handle.write("\nEdited by the practitioner during amendment.\n")
        self.assertNotEqual(workflow.digest(edited), baseline_sha["edited"])
        self.second(refine=False)
        self.third()
        self.pass_run.land(self.decision())
        self.assertEqual(self.pass_run.state["phase"], "closure_pass2")
        self.close_source()
        self.assertEqual(self.pass_run.state["phase"], "finished")
        hold = self.root / "EVIDENCE_HOLD.md"
        hold.write_text("explicit diagnosis hold; must survive close-run\n", encoding="utf-8")
        fresh = self.root / "controller/checkpoint.new"
        fresh.mkdir(parents=True)
        with self.assertRaisesRegex(workflow.RunError, "checkpoint residue must be resolved before close-run"):
            self.pass_run.close()
        self.assertTrue(hold.exists())
        self.assertTrue(edited.exists())
        self.assertTrue((self.root / "controller/run.json").exists(), "a refused close must not delete anything")
        fresh.rmdir()
        self.pass_run.close()
        self.assertTrue(edited.exists(), "user-edited baseline work is retained")
        self.assertNotEqual(workflow.digest(edited), baseline_sha["edited"])
        self.assertFalse(untouched.exists(), "untouched controller-copied scratch is discarded")
        self.assertFalse((self.root / "controller/amendment-baseline.json").exists())
        self.assertTrue(hold.exists(), "unknown evidence files survive close-run")
        self.assertFalse((self.root / "controller/run.json").exists())

    # ------------------------------------------------------- invariant 9
    def test_exp003_import_failures_are_typed_and_never_register_a_run(self):
        registered_before = json.dumps(workflow.list_registered_runs(self.repo))

        garbage = self.scratch / "garbage.zip"
        garbage.write_bytes(b"this is definitely not a zip archive")
        with self.assertRaises(workflow.RunError) as caught:
            workflow.import_run(self.repo, garbage)
        self.assertIn("corrupt or truncated", str(caught.exception))
        self.assertIn("no run was registered", str(caught.exception))

        missing = self.scratch / "missing-manifest.zip"
        with zipfile.ZipFile(missing, "w") as archive:
            archive.writestr("run/controller/run.json", b"{}")
        with self.assertRaisesRegex(workflow.RunError, "missing PASS_RUN_EXPORT"):
            workflow.import_run(self.repo, missing)

        mismatched = self.scratch / "hash-mismatch.zip"
        export_record = {
            "schema_version": 1,
            "run_id": "r_deadbeef",
            "run_manifest_sha256": hashlib.sha256(b"claimed manifest").hexdigest(),
            "files": {"controller/run.json": hashlib.sha256(b"claimed payload").hexdigest()},
        }
        with zipfile.ZipFile(mismatched, "w") as archive:
            archive.writestr(workflow.RUN_EXPORT_MANIFEST, json.dumps(export_record))
            archive.writestr("run/controller/run.json", b"an entirely different payload")
        with self.assertRaisesRegex(workflow.RunError, "hash mismatch"):
            workflow.import_run(self.repo, mismatched)

        self.assertEqual(json.dumps(workflow.list_registered_runs(self.repo)), registered_before)
        self.assertFalse((self.run_store / "r_deadbeef").exists())

    def test_exp003_hostile_import_structures_are_rejected_without_registration(self):
        """Traversal, absolute, duplicate, and unmanifested members are all refused
        before any extraction or registration; the catalog never changes and no
        files escape the run store."""
        self.ready(refine=True)
        self.pass_run.land(self.decision())
        self.pass_run.checkpoint()
        valid = self.scratch / "valid.zip"
        workflow.export_run(self.repo, self.root, valid)
        with zipfile.ZipFile(valid) as archive:
            base_pairs = [(name, archive.read(name)) for name in archive.namelist()]
        registered_before = json.dumps(workflow.list_registered_runs(self.repo))

        def hostile(name, mutate):
            path = self.scratch / name
            pairs = list(base_pairs)
            pairs = mutate(pairs)
            with zipfile.ZipFile(path, "w") as archive:
                for member, payload in pairs:
                    archive.writestr(member, payload)
            return path

        def add_traversal(pairs):
            return pairs + [("run/../../escape.txt", b"escaped")]

        def add_absolute(pairs):
            return pairs + [("/tmp/absolute.txt", b"escaped")]

        def add_duplicate(pairs):
            return pairs + [("run/controller/run.json", b"{}")]

        def add_extra(pairs):
            return pairs + [("run/extra.txt", b"not in the manifest")]

        cases = [
            (hostile("traversal.zip", add_traversal), "unsafe run import member"),
            (hostile("absolute.zip", add_absolute), "unsafe run import member"),
            (hostile("duplicate.zip", add_duplicate), "duplicate members"),
            (hostile("extra.zip", add_extra), "do not exactly match"),
        ]
        for archive_path, expected in cases:
            with self.subTest(archive=archive_path.name):
                with self.assertRaisesRegex(workflow.RunError, expected):
                    workflow.import_run(self.repo, archive_path)
                self.assertEqual(json.dumps(workflow.list_registered_runs(self.repo)), registered_before)

        self.assertFalse((self.run_store / "escape.txt").exists(), "no member may escape the run store")
        self.assertFalse((self.repo / "escape.txt").exists())
        self.assertTrue((self.run_store / self.root.name).exists(), "the pre-existing run must stay registered")

    @property
    def run_store(self):
        return self.repo / workflow.RUN_STORE

    # ------------------------------------------------------ invariant 10
    def test_exp003_close_refuses_residue_and_retains_unknown_evidence(self):
        self.ready(refine=True)
        self.pass_run.land(self.decision())
        self.close_source()
        self.assertEqual(self.pass_run.state["phase"], "finished")
        hold = self.root / "EVIDENCE_HOLD.md"
        hold.write_text("explicit diagnosis hold; must survive close-run\n", encoding="utf-8")
        fresh = self.root / "controller/checkpoint.new"
        fresh.mkdir(parents=True)
        with self.assertRaisesRegex(workflow.RunError, "checkpoint residue must be resolved before close-run"):
            self.pass_run.close()
        self.assertTrue(hold.exists())
        self.assertTrue((self.root / "controller/run.json").exists(), "the refused close must delete nothing")
        fresh.rmdir()
        self.pass_run.close()
        self.assertTrue(hold.exists())
        self.assertFalse((self.root / "controller/run.json").exists())
        self.assertFalse((self.root / "RUN_NOTE.md").exists())

    # ------------------------------------------------------ invariant 11
    def test_exp003_runs_migrate_copies_legacy_layout_without_touching_source(self):
        legacy = self.repo / "legacy-staging/writing/Python/original-book-run-one"
        legacy.parent.mkdir(parents=True)
        shutil.copytree(self.root, legacy)
        (legacy / workflow.RUN_MANIFEST).unlink()

        def tree_digests(path):
            return {
                item.relative_to(path).as_posix(): workflow.digest(item)
                for item in path.rglob("*") if item.is_file()
            }

        before = tree_digests(legacy)

        with self.assertRaisesRegex(workflow.RunError, "already carries a short-ID"):
            workflow.migrate_run(self.repo, self.root)

        residue_copy = self.repo / "legacy-staging/writing/Python/residue-book-run"
        shutil.copytree(legacy, residue_copy)
        (residue_copy / "controller/checkpoint.new").mkdir(parents=True)
        with self.assertRaisesRegex(workflow.RunError, "checkpoint residue"):
            workflow.migrate_run(self.repo, residue_copy)

        genre_copy = self.repo / "legacy-staging/writing/Python Vintage Edition/genre-book-run"
        shutil.copytree(legacy, genre_copy)
        with self.assertRaisesRegex(workflow.RunError, "could not derive a genre"):
            workflow.migrate_run(self.repo, genre_copy)

        migrated = workflow.migrate_run(self.repo, legacy)
        manifest = workflow.read_run_manifest(migrated, required=True)
        self.assertEqual(manifest["run_id"], migrated.name)
        self.assertEqual(manifest["domain"], "writing")
        self.assertEqual(manifest["genre"], "python")
        self.assertEqual(manifest["display_label"], "original-book-run-one")
        self.assertEqual(manifest["current"], {"phase": "load", "unit": None, "status": "active"})
        self.assertEqual(tree_digests(legacy), before, "the legacy source must never be modified")
        for rel, sha in before.items():
            self.assertEqual(workflow.digest(migrated / rel), sha, f"migration must copy {rel} byte-for-byte")
        self.assertIn(migrated.name, json.dumps(workflow.list_registered_runs(self.repo)))

        migrated_genre = workflow.migrate_run(self.repo, genre_copy, genre="python")
        self.assertEqual(workflow.read_run_manifest(migrated_genre, required=True)["genre"], "python")

    # ------------------------------------------------------ invariant 12
    def test_exp003_legacy_accepted_files_layout_remains_readable(self):
        canon = f"library/writing/craft/{self.live.name}"
        content = b"---\nobject_id: PAT_review_revision_effect\n---\nlegacy accepted bytes\n"
        legacy_path = self.root / "accepted/files" / canon
        legacy_path.parent.mkdir(parents=True, exist_ok=True)
        legacy_path.write_bytes(content)
        self.assertIsNone(self.pass_run.accepted_manifest())
        self.assertEqual(self.pass_run.accepted_file_hashes(), {canon: hashlib.sha256(content).hexdigest()})
        self.assertEqual(self.pass_run.read_accepted(canon), content)
        self.assertEqual(self.pass_run.accepted_content(), {canon: content})
        self.assertTrue(self.pass_run.accepted_fingerprint().startswith("sha256:"))
        with tempfile.TemporaryDirectory(prefix="exp003-apply-") as temporary:
            tree = Path(temporary)
            self.pass_run.apply_accepted(tree)
            self.assertEqual((tree / canon).read_bytes(), content)
        with self.assertRaisesRegex(workflow.RunError, "accepted file is missing"):
            self.pass_run.read_accepted("library/writing/craft/PAT_absent.md")

    # ------------------------------------------------------ invariant 13
    def test_exp003_export_import_round_trip_preserves_blob_stores(self):
        self.ready(refine=True)
        self.pass_run.land(self.decision())
        self.pass_run.checkpoint()
        canon = f"library/writing/craft/{self.live.name}"
        original_hashes = self.pass_run.accepted_file_hashes()
        self.assertIn(canon, original_hashes)
        original_content = self.pass_run.read_accepted(canon)

        archive_path = self.scratch / "roundtrip.zip"
        workflow.export_run(self.repo, self.root, archive_path)
        imported = workflow.import_run(self.repo, archive_path, collision="new-id")
        other = workflow.Run(self.repo, imported)
        self.assertNotEqual(imported.name, self.root.name)
        self.assertEqual(other.accepted_file_hashes(), original_hashes)
        self.assertEqual(other.read_accepted(canon), original_content)
        accepted_manifest = other.accepted_manifest()
        self.assertEqual(accepted_manifest["layout"], "content-addressed-blobs")
        for sha in original_hashes.values():
            blob = imported / "accepted/blobs" / sha
            self.assertTrue(blob.is_file(), f"accepted blob {sha[:12]} must be exported")
            self.assertEqual(workflow.digest(blob), sha)
        checkpoint_manifest = other.checkpoint_manifest()
        self.assertIsNotNone(checkpoint_manifest, "the checkpoint must survive export/import")
        for sha in set(checkpoint_manifest["files"].values()):
            blob = imported / "controller/checkpoint/blobs" / sha
            self.assertTrue(blob.is_file(), f"checkpoint blob {sha[:12]} must be exported")
            self.assertEqual(workflow.digest(blob), sha)

    # ------------------------------------------------------ invariant 14
    def test_exp003_present_degraded_declares_packet_sha_and_success_prints_packet(self):
        self.ready(refine=True)
        self.assertFalse(
            (self.root / "controller/checkpoint").exists(),
            "no checkpoint exists yet, so the first promotion is the fault seam",
        )
        real_rename = Path.rename

        def fail_fresh(path, target):
            if Path(path).name == "checkpoint.new":
                raise PermissionError(13, "injected fault", str(path))
            return real_rename(path, target)

        stdout, stderr = io.StringIO(), io.StringIO()
        with (
            patch.object(Path, "rename", new=fail_fresh),
            contextlib.redirect_stdout(stdout),
            contextlib.redirect_stderr(stderr),
        ):
            code = workflow.main(["--repo-root", str(self.repo), "present", "--run", str(self.root)])
        self.assertEqual(code, 2)
        self.assertEqual(stdout.getvalue(), "", "a degraded present must not print a packet")
        lines = [line for line in stderr.getvalue().splitlines() if line.strip()]
        self.assertEqual(len(lines), 1)
        record = json.loads(lines[0].split("PASS RUN CHECKPOINT DEGRADED: ", 1)[1])
        context = record["operation_context"]
        self.assertEqual(context["command"], "present")
        packet_sha = context.get("presented_packet_sha256")
        self.assertRegex(packet_sha or "", r"^[0-9a-f]{64}$")
        marker = json.loads((self.root / "controller/landing-presentation.json").read_text(encoding="utf-8"))
        self.assertEqual(marker["sha256"], packet_sha, "the declared packet sha must match the archived marker")
        audit_marker = json.loads((self.root / "controller/audit/u01-landing.json").read_text(encoding="utf-8"))
        self.assertEqual(audit_marker["sha256"], packet_sha)
        self.assertEqual(
            workflow.digest(self.root / "controller/audit/u01-landing.md"), packet_sha,
            "the archived packet itself must hash to the declared sha",
        )
        self.assertIs(record["authoritative_state_persisted"], True)
        self.assertIs(record["checkpoint_advanced"], False)

        self.h.run.reload()
        message = self.h.run.repair_checkpoint()
        self.assertTrue(message.startswith("REPAIRED"))
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = workflow.main(["--repo-root", str(self.repo), "present", "--run", str(self.root)])
        self.assertEqual(code, 0, "a promoted checkpoint releases the packet as a clean success")
        self.assertTrue(stdout.getvalue().startswith("# PASS LANDING PACKET"))
        self.assertNotIn("DEGRADED", stderr.getvalue())

    # ------------------------------------------------------- invariant 15
    def test_exp003_closure_land_renders_a_partial_delta_without_crashing_handoff(self):
        self.ready(refine=True)
        self.h.run.land(self.decision())
        self.assertEqual(self.h.run.state["phase"], "closure_pass2")
        record = self.h.run.template()
        record["closure_audits"] = {name: True for name in record["closure_audits"]}
        self.h.run.submit("closure_pass2", record)
        for key in ("flag_resolutions", "claim_regrounding", "omission_sweep", "reinforcement_evidence"):
            self.assertNotIn(key, self.h.run.state["pass2"], "the closure record replaces the unit delta")

        record = self.h.run.template()
        record["card_only_review"] = True
        record["checks"] = {name: True for name in record["checks"]}
        path = Path(self.temporary.name) / "closure-pass3.json"
        path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = workflow.main([
                "--repo-root", str(self.repo), "submit",
                "--run", str(self.root), "--phase", "closure_pass3", "--input", str(path),
            ])
        self.assertEqual(code, 0, f"closure PASS 3 must not crash the checkpoint/handoff path: {stderr.getvalue()}")
        self.assertIn("CLOSURE PASS 3: pass", stdout.getvalue())
        self.assertNotIn("DEGRADED", stderr.getvalue())
        self.h.run.reload()
        self.assertEqual(self.h.run.state["phase"], "closure_land")
        brief = self.h.run.brief()
        self.assertIn("closure_audits", brief["delta"])
        self.assertIn("buckets", brief["delta"])
        self.assertNotIn("flag_resolutions", brief["delta"])
        self.assertTrue(brief["presentation_command"].startswith("python PASS/pass.py present"))
        handoff = (self.root / "HANDOFF.md").read_text(encoding="utf-8")
        self.assertIn("Last safe endpoint", handoff)


if __name__ == "__main__":
    unittest.main()
