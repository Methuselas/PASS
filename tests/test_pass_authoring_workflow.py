"""Executable authoring gates, actual overlay validation and unit integration."""

import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "PASS"))
from runtime import pass_authoring_workflow as workflow


def card(path, oid, *, links=None, note="Keep only changes with an observable purpose.", placement=None):
    parts = path.parts[path.parts.index("library") + 1:-1] if "library" in path.parts else ("writing", "craft")
    data = dict(object_id=oid, object_type="pattern", name=oid[4:].replace("_", " ").title(),
                library_path=list(placement or parts), stage_binding="3 rough", lane_fit="skill",
                foundation_role="foundation", routing_class="general", specialization_axis="none",
                foundation_object_id="none", tags=["revision"], cross_links=links or [],
                confidence="high", references=[], variants=[])
    body = f"""# {data['name']}

## Pattern Rule
**IF** a revision changes the reader's understanding
**THEN** compare the intended effect with the revised result
**ELSE** preserve the working passage

## Do
- Identify the effect before choosing an edit.

## Don't
- Substitute extra detail for a clear decision.

## Checklist
- Can the intended effect be seen in the result?

## Notes
{note}
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("---\n" + yaml.safe_dump(data, sort_keys=False) + "---\n" + body, encoding="utf-8")


class AuthoringWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.repo = Path(self.temporary.name)
        shutil.copytree(ROOT / "PASS/tools", self.repo / "PASS/tools", ignore=shutil.ignore_patterns("__pycache__"))
        for name in workflow.required_documents(ROOT):
            target = self.repo / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("Fixture canonical instructions\n", encoding="utf-8")
        self.module("writing/craft")
        self.module("metaskills")
        self.live = self.repo / "library/writing/craft/PAT_review_revision_effect.md"
        card(self.live, self.live.stem)
        (self.repo / "workspace/release-recipes").mkdir(parents=True)
        (self.repo / "workspace/release-recipes/SkillForge_Writing.yaml").write_text("modules: [writing/craft]\n", encoding="utf-8")
        self.source = self.repo / "Original Book.txt"
        self.source.write_text("Original user input remains untouched.\n", encoding="utf-8")
        self.root = workflow.start(self.repo, self.source, "writing", "original-book-run-one")
        self.run = workflow.Run(self.repo, self.root)

    def module(self, name):
        target = self.repo / "library" / name / "MODULE.yaml"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(f"name: {name}\nrequires: []\n", encoding="utf-8")

    def begin(self, count=1):
        self.run.submit("load", self.run.template())
        record = self.run.template()
        record.update(title="Original Book", author="Fixture Author", extent="20 pages", text_quality="readable",
                      subject="Revise prose for an observable reader effect.", mode="unit ingestion")
        record["units"] = [dict(unit_id=f"u{i:02d}", material=f"Instructional unit {i}", locator=f"chapter {i}",
                                overlap_object_ids=[self.live.stem], card_potential="medium") for i in range(1, count + 1)]
        record["no_extract"] = []
        self.run.submit("preflight", record)
        self.accept()

    def accept(self):
        packet = self.run.present()
        self.run.accept_preflight(dict(schema_version=1, presentation_sha256=hashlib.sha256(packet.encode("utf-8")).hexdigest(),
                                       subject=self.run.state["plan"]["subject"], basis="user confirmation",
                                       reason="The practitioner confirmed the presented subject and unit plan."))

    def first(self, *, questions=False, flags=False):
        record = self.run.template()
        record["full_read"] = True
        if questions:
            record["questions"] = [{"question_id": "scope", "question": "Which interpretation is authorized?"}]
        if flags:
            record["secondary_subject_flags"] = [{"flag_id": "secondary", "subject": "Revisit a possible embedded revision rule."}]
        self.run.submit("pass1", record)

    def second(self, *, refine=False, approval=False):
        record = self.run.template()
        record.update(full_reread=True, approval_required=approval)
        for flag in record["flag_resolutions"]:
            flag["reason"] = "Instruction does not justify another reusable owner."
        if refine:
            name = "drafts/craft/" + self.live.name
            card(self.run.root / name, self.live.stem, note="Test the change against the declared reader effect before acceptance.")
            record["changes"] = [name]
            record["buckets"]["REFINE"] = [{"object_id": self.live.stem, "reason": "Make the acceptance test explicit."}]
        else:
            record["buckets"]["REINFORCE"] = [{"object_id": self.live.stem, "reason": "The existing owner covers the unit completely."}]
        self.run.submit("pass2", record)
        return record

    def third(self):
        record = self.run.template()
        record["card_only_review"] = True
        record["checks"] = {name: True for name in workflow.SEMANTIC_CHECKS}
        self.run.submit("pass3", record)

    def ready(self, *, count=1, refine=False, approval=False):
        self.begin(count)
        self.first()
        self.second(refine=refine, approval=approval)
        self.third()

    def decision(self, basis="evidence"):
        packet = self.run.present()
        return dict(schema_version=1, unit_id=self.run.unit()["unit_id"], basis=basis,
                    presentation_sha256=hashlib.sha256(packet.encode("utf-8")).hexdigest(),
                    reason="The complete reviewed delta is settled by the source and schema.")

    def test_start_never_infers_or_creates_a_domain(self):
        self.module("art/foundations")
        (self.repo / "library/apa-style").mkdir()
        for domain in (None, "apa-style", "../writing", "missing"):
            with self.subTest(domain=domain), self.assertRaises(workflow.RunError):
                workflow.start(self.repo, self.source, domain, "another-run")
        self.assertFalse((self.repo / "library/missing").exists())
        self.assertFalse((self.repo / "workspace/authoring/apa-style").exists())

    def other_source(self, name="Second Book.txt", text="A different book with different bytes entirely.\n"):
        path = self.repo / name
        path.write_text(text, encoding="utf-8")
        return path

    def files(self):
        return {p.relative_to(self.repo).as_posix(): p.read_bytes() for p in self.repo.rglob("*") if p.is_file() and "__pycache__" not in p.parts}

    def resumed(self, **arguments):
        before = self.files()
        result = workflow.resume(self.repo, **arguments)
        self.assertEqual(self.files(), before, "resume must never write")
        return result

    def test_single_domain_project_defaults_without_reading_source(self):
        second = self.other_source()
        with patch.object(Path, "read_bytes", side_effect=AssertionError("source content must not be read")):
            root = workflow.start(self.repo, second, None, "single-domain-run")
        self.assertEqual(workflow.Run(self.repo, root).domain, "writing")

    def test_staging_is_separate_for_each_book_run(self):
        other = workflow.start(self.repo, self.other_source(), "writing", "original-book-run-two")
        self.assertNotEqual(other, self.root)
        with self.assertRaises(workflow.RunError):
            workflow.start(self.repo, self.other_source("Third Book.txt", "Third.\n"), "writing", self.root.name)

    def test_start_refuses_a_second_run_of_the_same_source(self):
        self.begin()
        copy = self.repo / "moved/Renamed Copy.txt"
        copy.parent.mkdir()
        copy.write_bytes(self.source.read_bytes())
        for source in (self.source, copy):
            with self.subTest(source=source.name), self.assertRaisesRegex(workflow.RunError, "existing incomplete PASS run"):
                workflow.start(self.repo, source, "writing", None)
        self.assertEqual(sorted(p.name for p in (self.repo / "workspace/authoring/writing").iterdir()), [self.root.name])

    def test_same_source_may_start_in_another_domain_or_after_finishing(self):
        self.module("art/foundations")
        self.assertTrue(workflow.start(self.repo, self.source, "art", "art-reading").is_dir())
        self.ready()
        self.run.land(self.decision())
        self.assertEqual(self.run.state["phase"], "finished")
        self.assertTrue(workflow.start(self.repo, self.source, "writing", "second-reading").is_dir())

    def test_abandon_retires_the_run_keeps_its_drafts_and_unblocks_start(self):
        self.begin()
        draft = self.root / "drafts/craft/PAT_kept_draft.md"
        draft.parent.mkdir(parents=True)
        draft.write_text("Partial draft.\n", encoding="utf-8")
        with self.assertRaises(workflow.RunError):
            workflow.abandon(self.repo, self.root, "  ")
        message = workflow.abandon(self.repo, self.root, "The user asked to restart this book from scratch.")
        self.assertIn("RUN ABANDONED", message)
        self.assertTrue(draft.is_file())
        record = json.loads((self.root / workflow.ABANDONED).read_text(encoding="utf-8"))
        self.assertEqual(record["state"]["phase"], "pass1")
        self.assertIn("restart", record["reason"])
        with self.assertRaisesRegex(workflow.RunError, "abandoned"):
            workflow.Run(self.repo, self.root)
        self.assertEqual(self.resumed(domain="writing")["outcome"], "no_incomplete_run")
        self.assertTrue(workflow.start(self.repo, self.source, "writing", "restarted").is_dir())

    def test_finished_run_is_closed_not_abandoned(self):
        self.ready()
        self.run.land(self.decision())
        with self.assertRaisesRegex(workflow.RunError, "close-run"):
            workflow.abandon(self.repo, self.root, "The user asked to abandon it.")

    def test_resume_names_the_controller_next_action_at_every_phase(self):
        def check(last):
            result = self.resumed(domain="writing")
            self.assertEqual(result["outcome"], "resume")
            self.assertEqual(result["run"], str(self.root))
            self.assertEqual(result["phase"], self.run.state["phase"])
            self.assertEqual(result["last_accepted"], last)
            self.assertEqual(result["next_action"], self.run.brief()["authorized_action"])
            self.assertTrue(result["context"]["safe_to_discard"])
            return result

        self.assertIsNone(check(None)["current_unit"])
        self.run.submit("load", self.run.template())
        check("LOAD")
        record = self.run.template()
        record.update(title="Original Book", author="Fixture Author", extent="20 pages", text_quality="readable",
                      subject="Revise prose for an observable reader effect.", mode="unit ingestion", no_extract=[],
                      units=[dict(unit_id=f"u0{i}", material=f"Unit {i}", locator=f"chapter {i}",
                                  overlap_object_ids=[self.live.stem], card_potential="medium") for i in (1, 2)])
        self.run.submit("preflight", record)
        check("preflight validated; acceptance pending")
        self.accept()
        self.assertEqual(check("preflight accepted")["current_unit"], "U01")
        self.first(questions=True)
        check("U01 PASS 1")
        answers = self.run.template()
        answers["answers"][0]["resolution"] = "Practitioner chose the narrower interpretation."
        self.run.submit("checkpoint", answers)
        check("U01 checkpoint")
        self.second(refine=True)
        check("U01 PASS 2")
        self.third()
        self.assertEqual(check("U01 PASS 3")["drafts"], "verified against PASS 3 hashes")
        self.run.land(self.decision())
        result = check("U01 landed")
        self.assertEqual((result["units_completed"], result["current_unit"], result["unit_count"]), (["U01"], "U02", 2))
        self.assertIn("NEXT ACTION", result["statement"])

    def test_resume_by_source_finds_moved_identical_bytes_and_asks_for_rebind(self):
        self.begin()
        moved = self.repo / "moved/Original Book.txt"
        moved.parent.mkdir()
        self.source.replace(moved)
        result = self.resumed(domain="writing", source=moved)
        self.assertEqual((result["outcome"], result["source_identity"]), ("blocked", "moved"))
        self.assertIn("rebind-source", result["next_action"])
        self.assertIn(str(moved.resolve()), result["next_action"])

    def test_resume_blocks_on_changed_source_edited_draft_or_interrupted_operation(self):
        self.ready(refine=True)
        staged = self.root / self.run.state["pass2"]["changes"][0]
        original = staged.read_bytes()
        staged.write_bytes(original + b"\nEdited after review.\n")
        result = self.resumed(domain="writing")
        self.assertEqual(result["outcome"], "blocked")
        self.assertIn("--phase pass3", result["next_action"])
        staged.write_bytes(original)
        self.assertEqual(self.resumed(domain="writing")["outcome"], "resume")

        lock = self.root / "controller/operation.lock"
        lock.write_text('{"pid": 1, "acquired_at": "earlier"}\n', encoding="utf-8")
        result = self.resumed(root=self.root)
        self.assertEqual(result["outcome"], "blocked")
        self.assertFalse(result["context"]["safe_to_discard"])
        self.assertIn("did not finish", result["next_action"])
        lock.unlink()

        self.source.write_text("Different bytes under the same name.\n", encoding="utf-8")
        result = self.resumed(root=self.root)
        self.assertEqual((result["outcome"], result["source_identity"]), ("blocked", "changed"))

    def test_resume_asks_when_several_runs_are_open(self):
        second = self.other_source()
        other = workflow.start(self.repo, second, "writing", "second-book")
        self.assertEqual(self.resumed(domain="writing")["outcome"], "choose_run")
        self.assertEqual(self.resumed(domain="writing", source=second)["run"], str(other))

    def locked(self, operation, *arguments, **keywords):
        with self.run.locked():
            return operation(*arguments, **keywords)

    def test_every_accepted_step_checkpoints_and_rewrites_the_handoff(self):
        self.locked(self.run.submit, "load", self.run.template())
        manifest = self.run.checkpoint_manifest()
        self.assertEqual((manifest["phase"], manifest["last_accepted"]), ("preflight", "LOAD"))
        handoff = (self.root / "HANDOFF.md").read_text(encoding="utf-8")
        self.assertIn(workflow.HANDOFF_MARK, handoff)
        self.assertIn("Last safe endpoint: **LOAD**", handoff)
        self.assertIn("pass.py resume --run", handoff)

    def test_interrupted_pass3_rolls_back_to_the_end_of_pass2(self):
        self.begin()
        self.first()
        self.locked(self.second, refine=True)
        staged = self.root / self.run.state["pass2"]["changes"][0]
        accepted = staged.read_bytes()
        staged.write_bytes(accepted + b"\nHalf-finished PASS 3 repair.\n")
        extra = self.root / "drafts/craft/PAT_half_written.md"
        extra.write_text("Interrupted.\n", encoding="utf-8")
        self.locked(lambda: None)  # an operation that accepts nothing must not move the checkpoint
        result = self.resumed(domain="writing")
        self.assertEqual(result["phase"], "pass3")
        self.assertIn("rollback", result["next_action"])
        self.assertEqual(result["changed_since_checkpoint"], ["drafts/craft/PAT_half_written.md", self.run.state["pass2"]["changes"][0]])
        message = self.locked(self.run.rollback)
        self.assertIn("end of U01 PASS 2", message)
        self.assertEqual(staged.read_bytes(), accepted)
        self.assertFalse(extra.exists())
        self.assertEqual(self.run.state["phase"], "pass3")
        self.assertNotIn("rollback", self.resumed(domain="writing")["next_action"])
        self.third()
        self.assertEqual(self.run.state["phase"], "land")

    def test_rollback_needs_a_substantive_phase_and_a_checkpoint(self):
        self.begin()
        with self.assertRaisesRegex(workflow.RunError, "no checkpoint"):
            self.run.rollback()
        self.first()
        self.second()
        self.third()
        self.locked(lambda: None)
        with self.assertRaisesRegex(workflow.RunError, "has none to restart"):
            self.run.rollback()

    def test_a_hand_written_handoff_is_kept_as_notes(self):
        (self.root / "HANDOFF.md").write_text("Model notes: the figures carry the mechanism.\n", encoding="utf-8")
        self.locked(self.run.submit, "load", self.run.template())
        self.assertIn("the figures carry the mechanism", (self.root / "NOTES.md").read_text(encoding="utf-8"))
        self.assertIn(workflow.HANDOFF_MARK, (self.root / "HANDOFF.md").read_text(encoding="utf-8"))

    def test_run_state_keeps_one_live_fingerprint_and_reads_the_old_map(self):
        self.begin()
        self.first()
        self.second()
        self.assertTrue(self.run.state["live_hashes"].startswith("sha256:"))
        self.assertTrue(self.run.live_unchanged())
        self.run.state["live_hashes"] = self.run.live_hashes()
        self.assertTrue(self.run.live_unchanged())

    def test_close_removes_the_checkpoint_and_generated_handoff_but_keeps_notes(self):
        (self.root / "NOTES.md").write_text("Keep me.\n", encoding="utf-8")
        self.begin()
        self.first()
        self.second()
        self.third()
        self.locked(self.run.land, self.decision())
        self.assertTrue((self.root / workflow.CHECKPOINT).is_dir())
        self.locked(self.run.close)
        self.assertFalse((self.root / workflow.CHECKPOINT).exists())
        self.assertFalse((self.root / "HANDOFF.md").exists())
        self.assertTrue((self.root / "NOTES.md").is_file())

    def test_operation_lock_names_its_process(self):
        with self.run.locked():
            held = json.loads((self.root / "controller/operation.lock").read_text(encoding="utf-8"))
        self.assertEqual(held["pid"], __import__("os").getpid())
        self.assertFalse((self.root / "controller/operation.lock").exists())

    def test_load_and_preflight_gate_every_later_phase(self):
        with self.assertRaises(workflow.RunError):
            self.run.submit("pass1", {})
        bad = self.run.template()
        bad["documents_read"].append(1)
        with self.assertRaises(workflow.RunError):
            self.run.submit("load", bad)
        self.run.submit("load", self.run.template())
        self.assertIn("source-wide structural preflight", self.run.brief()["authorized_action"])
        with self.assertRaises(workflow.RunError):
            self.run.land(dict(schema_version=1))

    def test_validated_preflight_waits_for_bound_explicit_confirmation(self):
        self.run.submit("load", self.run.template())
        record = self.run.template()
        record.update(title="Original Book", author="Fixture Author", extent="20 pages", text_quality="readable",
                      subject="Revise prose for an observable reader effect.", mode="unit ingestion")
        record["units"] = [dict(unit_id="u01", material="Instructional unit 1", locator="chapter 1",
                                overlap_object_ids=[self.live.stem], card_potential="medium")]
        record["no_extract"] = []
        self.run.submit("preflight", record)
        self.assertEqual(self.run.state["phase"], "preflight_accept")
        with self.assertRaisesRegex(workflow.RunError, "preflight_accept"):
            self.run.submit("pass1", dict(full_read=True))
        packet = self.run.present()
        sha = hashlib.sha256(packet.encode("utf-8")).hexdigest()
        subject = self.run.state["plan"]["subject"]
        for bad in (dict(presentation_sha256="0" * 64, subject=subject, basis="user confirmation"),
                    dict(presentation_sha256=sha, subject="Another subject.", basis="user confirmation"),
                    dict(presentation_sha256=sha, subject=subject, basis="the request to run PASS")):
            with self.assertRaises(workflow.RunError):
                self.run.accept_preflight(dict(schema_version=1, reason="Inferred.", **bad))
        self.assertEqual(self.run.state["phase"], "preflight_accept")
        self.accept()
        self.assertEqual(self.run.state["phase"], "pass1")

    def test_preflight_domain_cannot_be_changed(self):
        self.run.submit("load", self.run.template())
        record = workflow.preflight.template_record()
        record["domain"] = "art"
        with self.assertRaises(workflow.RunError):
            self.run.submit("preflight", record)
        self.assertEqual(self.run.state["phase"], "preflight")

    def test_curriculum_audit_fails_closed_instead_of_falling_through(self):
        self.run.submit("load", self.run.template())
        record = self.run.template()
        record["mode"] = "curriculum audit"
        with self.assertRaisesRegex(workflow.RunError, "unit ingestion only"):
            self.run.submit("preflight", record)

    def test_only_one_active_unit_and_all_three_passes_required(self):
        self.begin(2)
        record = self.run.template()
        record.update(full_read=True, unit_id="u02")
        with self.assertRaisesRegex(workflow.RunError, "only active unit"):
            self.run.submit("pass1", record)
        self.first()
        with self.assertRaises(workflow.RunError):
            self.run.submit("pass3", {})
        self.assertEqual(self.run.brief()["authorized_source_scope"], "chapter 1")

    def test_full_read_and_cold_reread_are_explicit(self):
        self.begin()
        for value in (False, 1, "true"):
            record = self.run.template()
            record["full_read"] = value
            with self.subTest(value=value), self.assertRaises(workflow.RunError):
                self.run.submit("pass1", record)
        self.first()
        with self.assertRaises(workflow.RunError):
            self.run.submit("pass2", self.run.template())

    def test_questions_stop_progress_until_all_are_answered(self):
        self.begin()
        self.first(questions=True)
        with self.assertRaises(workflow.RunError):
            self.run.submit("pass2", {})
        with self.assertRaises(workflow.RunError):
            self.run.submit("checkpoint", dict(schema_version=1, unit_id="u01", answers=[]))
        record = self.run.template()
        record["answers"][0]["resolution"] = "Practitioner chose the narrower interpretation."
        self.run.submit("checkpoint", record)
        self.assertEqual(self.run.state["phase"], "pass2")

    def test_every_secondary_flag_requires_a_reasoned_resolution(self):
        self.begin()
        self.first(flags=True)
        record = self.run.template()
        record.update(full_reread=True, flag_resolutions=[])
        with self.assertRaisesRegex(workflow.RunError, "every PASS 1"):
            self.run.submit("pass2", record)
        self.second()

    def test_dispositions_are_exclusive_and_reinforce_cannot_mutate(self):
        self.begin()
        self.first()
        record = self.run.template()
        record["full_reread"] = True
        item = dict(object_id=self.live.stem, reason="Observed coverage.")
        record["buckets"]["REINFORCE"] = [item]
        record["buckets"]["REFINE"] = [item]
        with self.assertRaisesRegex(workflow.RunError, "duplicate dispositions"):
            self.run.submit("pass2", record)
        record["buckets"]["REFINE"] = []
        name = "drafts/craft/" + self.live.name
        card(self.root / name, self.live.stem, note="Different content.")
        record["changes"] = [name]
        with self.assertRaisesRegex(workflow.RunError, "changing disposition"):
            self.run.submit("pass2", record)

    def test_refinement_overlay_replaces_owner_and_lands_without_duplicate(self):
        self.ready(refine=True)
        staged = self.root / self.run.state["pass2"]["changes"][0]
        expected = staged.read_bytes()
        self.run.land(self.decision())
        self.assertEqual(self.live.read_bytes(), expected)
        self.assertEqual(self.run.state["phase"], "finished")
        self.assertFalse(staged.exists())
        self.assertTrue((self.live.parent / "INDEX.md").is_file())
        self.assertFalse((self.repo / ".git").exists())

    def test_review_rejects_foreign_card_links_and_bad_identity(self):
        self.begin()
        self.first()
        self.second(refine=True)
        staged = self.root / self.run.state["pass2"]["changes"][0]
        card(staged, self.live.stem, links=[dict(rel="related_to", target_object_id="PAT_foreign_card")])
        with self.assertRaisesRegex(workflow.RunError, "validate.py failed"):
            self.third()
        card(staged, "PAT_wrong_identity")
        with self.assertRaisesRegex(workflow.RunError, "filename/object_id"):
            self.third()

    def test_relation_gate_rejects_new_wrong_direction(self):
        second = self.live.parent / "PAT_compare_reading_effect.md"
        card(second, second.stem, note="Another reusable rule.")
        self.begin()
        self.first()
        self.second(refine=True)
        staged = self.root / self.run.state["pass2"]["changes"][0]
        card(staged, self.live.stem, links=[dict(rel="supports", target_object_id=second.stem)])
        with self.assertRaisesRegex(workflow.RunError, "relation contract"):
            self.third()

    def test_actual_reviewed_hashes_are_required(self):
        self.begin()
        self.first()
        self.second(refine=True)
        record = self.run.template()
        record.update(card_only_review=True, checks={n: True for n in workflow.SEMANTIC_CHECKS}, reviewed_sha256={})
        with self.assertRaisesRegex(workflow.RunError, "actual staged files"):
            self.run.submit("pass3", record)

    def test_edited_draft_after_review_requires_rescan(self):
        self.ready(refine=True)
        staged = self.root / self.run.state["pass2"]["changes"][0]
        staged.write_text(staged.read_text(encoding="utf-8") + "\nAdditional verified clarification.\n", encoding="utf-8")
        before = self.live.read_bytes()
        with self.assertRaisesRegex(workflow.RunError, "changed after PASS 3"):
            self.run.land(self.decision())
        self.assertEqual(self.live.read_bytes(), before)
        self.run.rewind("pass3")
        self.third()
        self.run.land(self.decision())

    def test_another_books_landing_invalidates_the_older_review(self):
        self.ready(refine=True)
        other_root = workflow.start(self.repo, self.other_source(), "writing", "book-two")
        older = self.run
        self.run = workflow.Run(self.repo, other_root)
        self.ready(refine=True)
        self.run.land(self.decision())
        self.run = older
        with self.assertRaisesRegex(workflow.RunError, "live domain/prerequisites changed"):
            self.run.land(self.decision())
        self.run.rewind("pass2")
        self.assertEqual(self.run.state["phase"], "pass2")

    def test_domain_landing_lease_prevents_overlapping_integrations(self):
        self.ready()
        lease = self.root.parent / ".landing.lock"
        lease.write_text("", encoding="utf-8")
        with self.assertRaisesRegex(workflow.RunError, "another book"):
            self.run.land(self.decision())
        self.assertTrue(lease.exists())

    def test_failed_atomic_landing_restores_files_and_active_unit(self):
        self.ready(refine=True)
        before = workflow.tree_hashes(self.repo / "library")
        real_write = workflow.atomic_write
        failed = False
        def fail_once(path, content):
            nonlocal failed
            if path.name == "INDEX.md" and not failed:
                failed = True
                raise OSError("injected landing write failure")
            real_write(path, content)
        with patch.object(workflow, "atomic_write", side_effect=fail_once), self.assertRaises(OSError):
            self.run.land(self.decision())
        self.assertTrue(failed)
        self.assertEqual(workflow.tree_hashes(self.repo / "library"), before)
        self.assertEqual(workflow.Run(self.repo, self.root).state["phase"], "land")
        self.assertTrue((self.root / self.run.state["pass2"]["changes"][0]).is_file())
        self.assertFalse((self.root.parent / ".landing.lock").exists())

    def test_landing_advances_only_one_unit(self):
        self.ready(count=2)
        self.run.land(self.decision())
        self.assertEqual(self.run.state["phase"], "pass1")
        self.assertEqual(self.run.brief()["unit_id"], "u02")
        with self.assertRaises(workflow.RunError):
            self.run.close()

    def test_generated_state_can_be_closed_without_deleting_original_inputs(self):
        self.ready()
        original = self.source.read_bytes()
        retained = self.root / "failure-evidence.md"
        retained.write_text("Explicit evidence hold.\n", encoding="utf-8")
        self.run.land(self.decision())
        self.run.close()
        self.assertFalse(self.run.state_path.exists())
        self.assertTrue(retained.exists())
        self.assertEqual(self.source.read_bytes(), original)

    def test_path_traversal_and_staged_indexes_are_rejected(self):
        for name in ("drafts/../PAT_bad.md", "drafts/craft/INDEX.md", "drafts\\craft\\PAT_bad.md", "C:/bad.md"):
            with self.subTest(name=name), self.assertRaises(workflow.RunError):
                self.run.target(name)

    def test_run_lock_reloads_state_and_does_not_steal_another_lease(self):
        stale = workflow.Run(self.repo, self.root)
        self.run.submit("load", self.run.template())
        with stale.locked():
            self.assertEqual(stale.state["phase"], "preflight")
            with self.assertRaises(workflow.RunError):
                with self.run.locked():
                    pass
        self.assertFalse((self.root / "controller/operation.lock").exists())

    def test_new_category_needs_taxonomy_and_foreign_recipe_is_protected(self):
        self.begin()
        self.first()
        record = self.run.template()
        record["full_reread"] = True
        oid = "PAT_compare_reader_expectations"
        name = f"drafts/new-category/{oid}.md"
        card(self.root / name, oid)
        record["changes"] = [name]
        record["buckets"]["NEW_PATTERNS"] = [dict(object_id=oid, reason="Different reusable decision.")]
        with self.assertRaisesRegex(workflow.RunError, "NEW_SUBCATEGORY"):
            self.run.submit("pass2", record)
        recipe = self.repo / "workspace/release-recipes/SkillForge_Art.yaml"
        recipe.write_text("modules: [art/foundations]\n", encoding="utf-8")
        staged = self.root / "recipes/SkillForge_Art.yaml"
        staged.parent.mkdir()
        staged.write_text("modules: [writing/craft]\n", encoding="utf-8")
        with self.assertRaisesRegex(workflow.RunError, "another domain"):
            self.run.target("recipes/SkillForge_Art.yaml")

    def test_invalid_recipe_closure_is_rejected_before_landing(self):
        self.begin()
        self.first()
        record = self.run.template()
        record["full_reread"] = True
        name = "recipes/SkillForge_Writing.yaml"
        staged = self.root / name
        staged.parent.mkdir()
        staged.write_text("modules: [writing/missing]\n", encoding="utf-8")
        record["changes"] = [name]
        self.run.submit("pass2", record)
        with self.assertRaisesRegex(workflow.RunError, "missing module"):
            self.third()

    def test_instructional_replan_preserves_closed_units_and_domain(self):
        self.ready(count=2)
        self.run.land(self.decision())
        plan = copy.deepcopy(self.run.state["plan"])
        plan["units"][1]["locator"] = "chapter 2, instructional sections A and B"
        record = dict(schema_version=1, reason="The author's instruction closes after section B.", preflight=plan)
        self.run.replan(record)
        self.assertEqual(self.run.unit()["locator"], plan["units"][1]["locator"])
        record["preflight"]["units"][0]["locator"] = "different closed unit"
        with self.assertRaisesRegex(workflow.RunError, "closed units"):
            self.run.replan(record)

    def test_entrypoint_executes_from_project_without_installation(self):
        result = subprocess.run([sys.executable, str(ROOT / "PASS/pass.py"), "--repo-root", str(self.repo),
                                 "status", "--run", str(self.root)], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["phase"], "load")

    def test_practitioner_approval_cannot_be_replaced_by_evidence(self):
        self.ready(approval=True)
        with self.assertRaisesRegex(workflow.RunError, "practitioner approval"):
            self.run.land(self.decision())
        self.run.land(self.decision("user approval"))

    def test_integration_rejects_global_id_collision_without_loading_foreign_cards_during_authoring(self):
        self.module("art/craft")
        oid = "PAT_compare_effects_before_acceptance"
        card(self.repo / f"library/art/craft/{oid}.md", oid, note="A separate foreign-domain owner.")
        self.begin()
        self.first()
        record = self.run.template()
        record["full_reread"] = True
        name = f"drafts/craft/{oid}.md"
        card(self.root / name, oid, note="A new writing owner with a colliding ID.")
        record["changes"] = [name]
        record["buckets"]["NEW_PATTERNS"] = [dict(object_id=oid, reason="Different reusable decision.")]
        self.run.submit("pass2", record)
        self.third()
        with self.assertRaisesRegex(workflow.RunError, "validate.py failed"):
            self.run.land(self.decision())
        self.assertFalse((self.repo / f"library/writing/craft/{oid}.md").exists())

    def test_wrong_library_path_and_card_provenance_fail_the_real_schema_gate(self):
        self.begin()
        self.first()
        self.second(refine=True)
        staged = self.root / self.run.state["pass2"]["changes"][0]
        original = staged.read_text(encoding="utf-8")
        staged.write_text(original.replace("- craft", "- another-category"), encoding="utf-8")
        with self.assertRaisesRegex(workflow.RunError, "library_path"):
            self.third()
        staged.write_text(original.replace("object_type: pattern", "object_type: pattern\nsource_id: book"), encoding="utf-8")
        with self.assertRaisesRegex(workflow.RunError, "source_id"):
            self.third()

    def test_untouched_relation_migration_debt_is_not_a_new_blocker(self):
        other = self.live.parent / "PAT_inspect_acceptance_criterion.md"
        card(other, other.stem, links=[dict(rel="supports", target_object_id=self.live.stem)])
        self.ready()
        self.run.land(self.decision())
        self.assertEqual(self.run.state["phase"], "finished")

    def test_live_asset_or_prerequisite_change_also_invalidates_review(self):
        self.ready()
        card(self.repo / "library/metaskills/craft/PAT_check_declared_objective.md", "PAT_check_declared_objective")
        with self.assertRaisesRegex(workflow.RunError, "live domain/prerequisites changed"):
            self.run.land(self.decision())

    def test_taxonomy_move_regenerates_indexes_and_retires_empty_topic_index(self):
        self.live.unlink()
        self.live = self.repo / "library/writing/craft/old-topic/PAT_review_revision_effect.md"
        card(self.live, self.live.stem)
        result = subprocess.run([sys.executable, str(self.repo / "PASS/tools/build_index.py"),
                                 "--library", str(self.repo / "library")], capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        old_index = self.live.parent / "INDEX.md"
        self.assertTrue(old_index.exists())
        self.begin()
        self.first()
        record = self.run.template()
        record["full_reread"] = True
        name = "drafts/craft/new-topic/" + self.live.name
        card(self.root / name, self.live.stem, placement=["writing", "craft", "new-topic"], note="The owner belongs in the revised topic.")
        record["changes"] = [name]
        record["removals"] = ["craft/old-topic/" + self.live.name]
        record["buckets"]["REFINE"] = [dict(object_id=self.live.stem, reason="Reconcile the owner with its actual subject.")]
        record["taxonomy"]["MOVE"] = [dict(path="craft/new-topic", reason="This category owns the decision.")]
        record["taxonomy"]["NEW_SUBCATEGORY"] = [dict(path="craft/new-topic", reason="Give the reusable decision its own topic.")]
        self.run.submit("pass2", record)
        self.third()
        self.run.land(self.decision())
        self.assertFalse(self.live.exists())
        self.assertFalse(old_index.exists())
        self.assertTrue((self.repo / "library/writing/craft/new-topic/INDEX.md").exists())

    def test_failed_state_save_also_restores_landed_files(self):
        self.ready(refine=True)
        before = workflow.tree_hashes(self.repo / "library")
        with patch.object(self.run, "save", side_effect=OSError("injected state write failure")), self.assertRaises(OSError):
            self.run.land(self.decision())
        self.assertEqual(workflow.tree_hashes(self.repo / "library"), before)
        self.assertEqual(workflow.Run(self.repo, self.root).state["phase"], "land")

    def test_asset_support_folder_is_not_a_new_knowledge_subcategory(self):
        self.begin()
        self.first()
        record = self.run.template()
        record["full_reread"] = True
        name = "drafts/craft/assets/new-reference.jpg"
        staged = self.root / name
        staged.parent.mkdir(parents=True)
        staged.write_bytes(b"image fixture, not yet referenced")
        record["changes"] = [name]
        self.run.submit("pass2", record)
        self.assertEqual(self.run.state["phase"], "pass3")

    def test_canonical_recipe_cannot_silently_omit_a_new_module(self):
        self.module("writing/new-module")
        self.begin()
        self.first()
        record = self.run.template()
        record["full_reread"] = True
        name = "recipes/SkillForge_Writing.yaml"
        staged = self.root / name
        staged.parent.mkdir()
        staged.write_text("modules: [writing/craft]\n", encoding="utf-8")
        record["changes"] = [name]
        self.run.submit("pass2", record)
        with self.assertRaisesRegex(workflow.RunError, "every active-domain module"):
            self.third()


if __name__ == "__main__":
    unittest.main()
