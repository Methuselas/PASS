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
from runtime import pass_source_prep


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

    def prep(self):
        pass_source_prep.prepare(self.run)
        pass_source_prep.finalize(self.run)

    def begin(self, count=1):
        self.run.submit("load", self.run.template())
        self.prep()
        record = self.run.template()
        record.update(title="Original Book", author="Fixture Author", extent="20 pages", text_quality="readable",
                      subject="Revise prose for an observable reader effect.", mode="unit ingestion")
        record["units"] = [dict(unit_id=f"u{i:02d}", material=f"Instructional unit {i}", locator=f"chapter {i}",
                                source_pages=None, printed_pages=None,
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

    def complete_pass2_attention(self, record):
        record["omission_sweep"]["complete"] = True
        for flag in record["flag_resolutions"]:
            flag["outcome"] = flag.get("outcome") or "rejected"
            flag["reason"] = flag.get("reason") or "Instruction does not justify another reusable owner."
            flag["deferred_to"] = flag.get("deferred_to") or ""
        reviews = []
        for name in record["changes"]:
            staged = self.run.root / name
            if staged.suffix != ".md":
                continue
            fm = workflow.preflight._frontmatter(staged)
            reviews.append({
                "object_id": fm["object_id"],
                "claims": [{
                    "card_quote": "**IF** a revision changes the reader's understanding",
                    "source_locator": "fixture source unit",
                    "source_quote": "Original user input remains untouched.",
                }],
                "summary": "Re-grounded the staged rule against the bounded fixture source for this test.",
            })
        record["claim_regrounding"] = reviews
        record["reinforcement_evidence"] = []
        for item in record["buckets"]["REINFORCE"]:
            record["reinforcement_evidence"].append({
                "object_id": item["object_id"],
                "owner_claim": "**IF** a revision changes the reader's understanding",
                "source_locator": "fixture source unit",
                "source_quote": "Original user input remains untouched.",
                "scope": "reinforces_core",
            })
        return record

    def second(self, *, refine=False, approval=False):
        record = self.run.template()
        record.update(full_reread=True, approval_required=approval)
        for flag in record["flag_resolutions"]:
            flag["outcome"] = "rejected"
            flag["reason"] = "Instruction does not justify another reusable owner."
            flag["deferred_to"] = ""
        if refine:
            name = "drafts/craft/" + self.live.name
            card(self.run.root / name, self.live.stem, note="Test the change against the declared reader effect before acceptance.")
            record["changes"] = [name]
            record["buckets"]["REFINE"] = [{"object_id": self.live.stem, "reason": "Make the acceptance test explicit."}]
            record["owner_reconciliation"] = [{
                "object_id": self.live.stem,
                "compared_owner_ids": [self.live.stem],
                "reason": "The live card is the nearest existing owner and is being refined rather than duplicated.",
            }]
            record["metadata_classification"] = [{
                "object_id": self.live.stem,
                "stage_binding": "3 rough",
                "lane_fit": "skill",
                "confidence": "high",
                "reason": "The staged refinement preserves the card's demonstrated execution role and confidence.",
            }]
        else:
            record["buckets"]["REINFORCE"] = [{"object_id": self.live.stem, "reason": "The existing owner covers the unit completely."}]
        self.complete_pass2_attention(record)
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


    def audit_changed(self, record, oid, staged_name, owner_ids=None):
        fm = workflow.preflight._frontmatter(self.root / staged_name)
        record["owner_reconciliation"] = [{
            "object_id": oid,
            "compared_owner_ids": list(owner_ids or []),
            "reason": "The candidate was compared against the nearest live owners before disposition.",
        }]
        record["metadata_classification"] = [{
            "object_id": oid,
            "stage_binding": fm["stage_binding"],
            "lane_fit": fm["lane_fit"],
            "confidence": fm["confidence"],
            "reason": "The staged card metadata was classified explicitly for this object.",
        }]

    def close_source(self):
        self.assertEqual(self.run.state["phase"], "closure_pass2")
        record = self.run.template()
        record["closure_audits"] = {name: True for name in record["closure_audits"]}
        self.run.submit("closure_pass2", record)
        record = self.run.template()
        record["card_only_review"] = True
        record["checks"] = {name: True for name in workflow.SEMANTIC_CHECKS}
        self.run.submit("closure_pass3", record)
        packet = self.run.present()
        decision = dict(
            schema_version=1, unit_id="closure", basis="evidence",
            presentation_sha256=hashlib.sha256(packet.encode("utf-8")).hexdigest(),
            reason="The mandatory closure audits found no additional canonical mutation.",
        )
        self.run.land(decision)
        self.assertEqual(self.run.state["phase"], "finished")

    def decision(self, basis="evidence"):
        packet = self.run.present()
        return dict(schema_version=1, unit_id=self.run.unit()["unit_id"], basis=basis,
                    presentation_sha256=hashlib.sha256(packet.encode("utf-8")).hexdigest(),
                    reason="The complete reviewed delta is settled by the source and schema.")

    def test_experimental_sandbox_marker_can_forbid_a_canonical_repo_root(self):
        marker = self.repo / "PASS_SANDBOX.json"
        marker.write_text(json.dumps({
            "mode": "experimental-sandbox",
            "forbidden_repo_paths": [str(self.repo.resolve())],
        }), encoding="utf-8")
        try:
            with self.assertRaisesRegex(workflow.RunError, "experimental PASS sandbox refuses"):
                workflow.enforce_sandbox_boundary(self.repo)
        finally:
            marker.unlink(missing_ok=True)

    def test_start_never_infers_or_creates_a_domain(self):
        self.module("art/foundations")
        (self.repo / "library/apa-style").mkdir()
        for domain in (None, "apa-style", "../writing", "missing"):
            with self.subTest(domain=domain), self.assertRaises(workflow.RunError):
                workflow.start(self.repo, self.source, domain, "another-run")
        self.assertFalse((self.repo / "library/missing").exists())
        self.assertFalse((self.repo / "workspace/skill-staging/apa-style").exists())

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

    def test_genre_subfolder_run_is_loaded_and_discovered(self):
        # beta.105's invariant under the short-ID store: genre is manifest
        # metadata there, so the genre-subfolder path shape is exercised on a
        # legacy skill-staging run, which the runtime keeps resumable.
        legacy_domain = self.repo / "workspace/skill-staging/writing"
        genre = legacy_domain / "prose"
        genre.mkdir(parents=True, exist_ok=True)
        moved = genre / self.root.name
        shutil.move(str(self.root), str(moved))
        self.assertEqual(workflow.Run(self.repo, moved).domain, "writing")
        found = [p.relative_to(self.repo / "workspace/skill-staging").as_posix()
                 for p in workflow.open_runs(self.repo, "writing")]
        self.assertIn("writing/prose/" + self.root.name, found)
        self.assertNotIn("writing/" + self.root.name, found)

    def test_run_root_rejects_unsupported_depths(self):
        with self.subTest(depth="shallow"), self.assertRaises(workflow.RunError):
            workflow.run_root(self.repo, self.repo / "workspace/skill-staging/stray-book")
        with self.subTest(depth="deep"), self.assertRaises(workflow.RunError):
            workflow.run_root(self.repo, self.repo / "workspace/skill-staging/writing/a/b/original-book-run-one")

    def test_start_refuses_a_second_run_of_the_same_source(self):
        self.begin()
        copy = self.repo / "moved/Renamed Copy.txt"
        copy.parent.mkdir()
        copy.write_bytes(self.source.read_bytes())
        for source in (self.source, copy):
            with self.subTest(source=source.name), self.assertRaisesRegex(workflow.RunError, "existing incomplete PASS run"):
                workflow.start(self.repo, source, "writing", None)
        self.assertEqual([item["run_id"] for item in workflow.list_registered_runs(self.repo, domain="writing")], [self.root.name])

    def test_same_source_may_start_in_another_domain_or_after_finishing(self):
        self.module("art/foundations")
        self.assertTrue(workflow.start(self.repo, self.source, "art", "art-reading").is_dir())
        self.ready()
        self.run.land(self.decision())
        self.close_source()
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
        self.close_source()
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
        self.prep()
        check("source prep verified")
        record = self.run.template()
        record.update(title="Original Book", author="Fixture Author", extent="20 pages", text_quality="readable",
                      subject="Revise prose for an observable reader effect.", mode="unit ingestion", no_extract=[],
                      units=[dict(unit_id=f"u0{i}", material=f"Unit {i}", locator=f"chapter {i}",
                                  source_pages=None, printed_pages=None,
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
        result = check("U01 accepted to staging")
        self.assertEqual((result["units_completed"], result["current_unit"], result["unit_count"]), (["U01"], "U02", 2))
        self.assertIn("NEXT ACTION", result["statement"])

    def test_resume_by_source_finds_moved_identical_bytes_and_asks_for_rebind(self):
        self.begin()
        moved = self.repo / "moved/Original Book.txt"
        moved.parent.mkdir()
        self.source.replace(moved)
        # A verified prepared package lets the run continue without the raw source.
        result = self.resumed(domain="writing", source=moved)
        self.assertEqual((result["outcome"], result["source_identity"]), ("resume", "prepared-package"))
        # Without the prepared package, identical bytes at a new path require rebind.
        shutil.rmtree(self.root / "prepared-source")
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
        self.assertEqual((result["outcome"], result["source_identity"]), ("resume", "prepared-package"))
        shutil.rmtree(self.root / "prepared-source")
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
        self.assertEqual((manifest["phase"], manifest["last_accepted"]), ("source_prep", "LOAD"))
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
        self.assertIsInstance(self.run.state["live_hashes"], dict)
        self.assertTrue(self.run.live_unchanged())
        self.run.state["live_hashes"] = self.run.live_snapshot()
        self.assertTrue(self.run.live_unchanged())
        self.run.state["live_hashes"] = self.run.live_hashes()
        self.assertTrue(self.run.live_unchanged())
        self.run.state["live_hashes"] = self.run.live_fingerprint()
        self.assertTrue(self.run.live_unchanged())

    def test_close_removes_the_checkpoint_and_generated_handoff_but_keeps_notes(self):
        (self.root / "NOTES.md").write_text("Keep me.\n", encoding="utf-8")
        self.begin()
        self.first()
        self.second()
        self.third()
        self.locked(self.run.land, self.decision())
        self.close_source()
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
        self.assertIn("source_prep.py prepare", self.run.brief()["authorized_action"])
        with self.assertRaises(workflow.RunError):
            self.run.land(dict(schema_version=1))

    def test_legacy_active_run_backfills_source_prep_without_losing_accepted_progress(self):
        self.begin(count=2)
        self.first()
        self.second()
        self.third()
        self.run.land(self.decision())
        accepted_before = self.run.accepted_file_hashes()
        preserved_before = {
            key: copy.deepcopy(self.run.state[key])
            for key in ("phase", "unit_index", "plan", "pass1", "pass2", "reviewed_sha256", "live_hashes")
        }

        shutil.rmtree(self.root / "prepared-source")
        shutil.rmtree(self.root / "controller/source-prep-raw")
        (self.root / "controller/source-identity.json").unlink()
        self.run.state["source_prep"] = None
        self.run.save()
        self.run.checkpoint()

        with self.assertRaisesRegex(workflow.RunError, "available only in source_prep"):
            pass_source_prep.prepare(self.run)
        self.assertEqual(pass_source_prep.main([
            "--repo-root", str(self.repo), "prepare", "--run", str(self.root), "--legacy-backfill",
        ]), 0)
        self.run.reload()
        self.assertEqual(pass_source_prep.verify(self.run)["source"]["sha256"], self.run.source_identity()["sha256"])
        self.assertEqual(pass_source_prep.main([
            "--repo-root", str(self.repo), "finalize", "--run", str(self.root), "--legacy-backfill",
        ]), 0)
        self.run.reload()

        self.assertEqual(self.run.state["phase"], "pass1")
        self.assertEqual(self.run.state["source_prep"]["status"], "verified")
        self.assertEqual(self.run.accepted_file_hashes(), accepted_before)
        for key, value in preserved_before.items():
            self.assertEqual(self.run.state[key], value)

    def test_validated_preflight_waits_for_bound_explicit_confirmation(self):
        self.run.submit("load", self.run.template())
        self.prep()
        record = self.run.template()
        record.update(title="Original Book", author="Fixture Author", extent="20 pages", text_quality="readable",
                      subject="Revise prose for an observable reader effect.", mode="unit ingestion")
        record["units"] = [dict(unit_id="u01", material="Instructional unit 1", locator="chapter 1",
                                source_pages=None, printed_pages=None,
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

    def test_prepared_pdf_preflight_requires_machine_readable_coordinates(self):
        self.run.submit("load", self.run.template())
        self.prep()
        manifest = {"source_kind": "pdf", "segments": list(range(1, 21))}
        with patch.object(pass_source_prep, "verify", return_value=manifest):
            def parsed(unit, schema_version=workflow.preflight.SCHEMA_VERSION):
                record = self.run.template()
                record["schema_version"] = schema_version
                if schema_version < 3:
                    # A genuine schema-1/2 record never carried the schema-3
                    # language_policy key; each schema has an exact key set.
                    del record["language_policy"]
                record.update(title="Original Book", author="Fixture Author", extent="20 pages",
                             text_quality="readable", subject="Revise prose for an observable reader effect.",
                             mode="unit ingestion", no_extract=[])
                record["units"] = [unit]
                return workflow.preflight.parse_preflight(record)
            base = dict(unit_id="u01", material="Unit 1", locator="chapter 1",
                        source_pages={"start": 1, "end": 10}, printed_pages="1-10",
                        overlap_object_ids=[], card_potential="medium")
            self.run.validate_preflight_source_coordinates(parsed(base))
            self.run.validate_preflight_source_coordinates(parsed(base, schema_version=2))
            hybrid = self.run.template()
            hybrid["schema_version"] = 2
            with self.assertRaisesRegex(workflow.preflight.PreflightError, "unexpected language_policy"):
                workflow.preflight.parse_preflight(hybrid)
            missing = dict(base, source_pages=None)
            with self.assertRaisesRegex(workflow.RunError, "source_pages"):
                self.run.validate_preflight_source_coordinates(parsed(missing))
            outside = dict(base, source_pages={"start": 15, "end": 25})
            with self.assertRaisesRegex(workflow.RunError, "outside prepared PDF"):
                self.run.validate_preflight_source_coordinates(parsed(outside))
            legacy = dict(unit_id="u01", material="Unit 1", locator="pp. 3-10 (PDF 5-12)",
                         overlap_object_ids=[], card_potential="medium")
            self.run.validate_preflight_source_coordinates(parsed(legacy, schema_version=1))
            ambiguous = dict(legacy, locator="pp. 3-10 and pp. 11-20")
            with self.assertRaisesRegex(workflow.RunError, "ambiguous"):
                self.run.validate_preflight_source_coordinates(parsed(ambiguous, schema_version=1))
            conflicting = dict(legacy, locator="pp. 3-10 (PDF 5-12) (source 6-13)")
            with self.assertRaisesRegex(workflow.RunError, "ambiguous"):
                self.run.validate_preflight_source_coordinates(parsed(conflicting, schema_version=1))

    def test_locator_pages_prefers_explicit_pdf_coordinates(self):
        self.assertEqual(pass_source_prep.locator_pages("pp. 3-26 (PDF 55-78)", 1594), list(range(55, 79)))

    def test_locator_pages_accepts_a_single_unlabelled_range(self):
        self.assertEqual(pass_source_prep.locator_pages("pp. 3-26", 1594), list(range(3, 27)))

    def test_locator_pages_rejects_multiple_unlabelled_ranges(self):
        self.assertIsNone(pass_source_prep.locator_pages("pp. 3-26 and pp. 27-42", 1594))

    def test_locator_pages_rejects_conflicting_explicit_ranges(self):
        self.assertIsNone(pass_source_prep.locator_pages("pp. 3-26 (PDF 55-78) (source 56-79)", 1594))

    def test_locator_pages_rejects_out_of_range_explicit_range(self):
        self.assertIsNone(pass_source_prep.locator_pages("pp. 3-26 (PDF 55-1600)", 1594))

    def test_locator_pages_resolves_explicit_single_page(self):
        self.assertEqual(pass_source_prep.locator_pages("PDF p. 55", 1594), [55])

    def test_numbered_table_signals_are_counted_independently(self):
        text = "Table 5-1. Operators\n\nTable 5-2. Precedence\n\nTable 6-1. Types\n\nProse only.\n"
        self.assertEqual(pass_source_prep._raw_table_signal_count(text), 3)

    def test_inline_table_mentions_are_not_counted(self):
        text = "As shown in table 5-1 above, the values differ.\n"
        self.assertEqual(pass_source_prep._raw_table_signal_count(text), 0)

    def test_table_signal_requires_review_when_no_structured_tables_detected(self):
        # Source Prep schema 5 (beta.87): numbered-table evidence with zero
        # structured tables is an explicit review requirement, not only a warning.
        import fitz
        source = self.repo / "Tables Book.pdf"
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((72, 100), "Table 1-1. First table\n\nTable 1-2. Second table\n\nTable 1-3. Third table\n\nSome prose around the tables.\n")
        doc.save(source)
        doc.close()
        root = workflow.start(self.repo, source, "writing", "tables-book-run")
        run = workflow.Run(self.repo, root)
        run.submit("load", run.template())
        pass_source_prep.prepare(run)
        pass_source_prep.finalize(run)
        manifest = pass_source_prep.verify(run)
        gate = manifest["integrity_gate"]
        self.assertEqual(gate["status"], "review")
        self.assertTrue(any("table sanity check" in item["requirement"] for item in gate["review_requirements"]))
        self.assertTrue(any("table sanity check" in warning["warning"] for warning in gate["warnings"]))
        record = run.template()
        record.update(title="Tables Book", author="Fixture Author", extent="1 page", text_quality="readable",
                      subject="Use numbered reference tables.", mode="unit ingestion", no_extract=[])
        record["units"] = [dict(unit_id="u01", material="Table unit", locator="page 1",
                                 source_pages={"start": 1, "end": 1}, printed_pages=None,
                                 overlap_object_ids=[], card_potential="low")]
        run.submit("preflight", record)
        audit = run.preflight_quality_audit()
        self.assertEqual(audit["source_integrity"], "review")
        self.assertTrue(any("table sanity check" in item["requirement"] for item in audit["source_review"]),
                        "the table requirement reaches the unattended-acceptance gate")
        packet = run.present()
        self.assertIn("SOURCE PREP INTEGRITY WARNINGS", packet)
        self.assertIn("table sanity check", packet)

    def test_preflight_domain_cannot_be_changed(self):
        self.run.submit("load", self.run.template())
        self.prep()
        record = workflow.preflight.template_record()
        record["domain"] = "art"
        with self.assertRaises(workflow.RunError):
            self.run.submit("preflight", record)
        self.assertEqual(self.run.state["phase"], "preflight")

    def test_curriculum_audit_fails_closed_instead_of_falling_through(self):
        self.run.submit("load", self.run.template())
        self.prep()
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
        self.assertEqual(self.run.state["phase"], "closure_pass2")
        self.assertFalse(staged.exists())
        # The accepted delta is staged in skill-staging; the live canon is
        # untouched until the source close transaction. Storage is
        # content-addressed (EXP-003), so read through the logical-name API.
        self.assertEqual(
            self.run.read_accepted(f"library/writing/craft/{self.live.name}"), expected
        )
        self.assertNotEqual(self.live.read_bytes(), expected)
        self.close_source()
        self.assertEqual(self.live.read_bytes(), expected)
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
        self.close_source()
        # The other book's source close canonicalized into the live domain; the
        # older run's review predates that change and must be redone.
        self.run = older
        with self.assertRaisesRegex(workflow.RunError, "live domain/prerequisites changed"):
            self.run.land(self.decision())
        self.run.rewind("pass2")
        self.assertEqual(self.run.state["phase"], "pass2")

    def test_pass2_requires_intensification_and_omission_sweep(self):
        self.begin()
        self.first()
        record = self.run.template()
        record["full_reread"] = True
        record["buckets"]["REINFORCE"] = [{"object_id": self.live.stem, "reason": "Existing owner remains sufficient."}]
        with self.assertRaisesRegex(workflow.RunError, "omission_sweep"):
            self.run.submit("pass2", record)
        record["omission_sweep"]["complete"] = True
        self.complete_pass2_attention(record)
        self.run.submit("pass2", record)

    def test_reinforce_requires_registered_source_to_owner_evidence(self):
        self.begin()
        self.first()
        record = self.run.template()
        record["full_reread"] = True
        record["omission_sweep"]["complete"] = True
        record["buckets"]["REINFORCE"] = [{"object_id": self.live.stem, "reason": "The owner remains sufficient."}]
        with self.assertRaisesRegex(workflow.RunError, "source-to-owner evidence"):
            self.run.submit("pass2", record)
        self.complete_pass2_attention(record)
        record["reinforcement_evidence"][0]["owner_claim"] = "claim that does not exist in the owner"
        with self.assertRaisesRegex(workflow.RunError, "owner_claim"):
            self.run.submit("pass2", record)

    def test_changed_card_requires_literal_claim_re_grounding(self):
        self.begin()
        self.first()
        record = self.run.template()
        record["full_reread"] = True
        name = "drafts/craft/" + self.live.name
        card(self.run.root / name, self.live.stem, note="Re-ground this change.")
        record["changes"] = [name]
        record["buckets"]["REFINE"] = [{"object_id": self.live.stem, "reason": "Clarify the owner."}]
        self.audit_changed(record, self.live.stem, name, [self.live.stem])
        record["omission_sweep"]["complete"] = True
        with self.assertRaisesRegex(workflow.RunError, "claim re-grounding"):
            self.run.submit("pass2", record)
        self.complete_pass2_attention(record)
        record["claim_regrounding"][0]["claims"][0]["card_quote"] = "not present in the card"
        with self.assertRaisesRegex(workflow.RunError, "card_quote"):
            self.run.submit("pass2", record)

    def test_accepted_unit_history_is_checkpointed_for_recovery(self):
        self.ready(count=2, refine=True)
        self.run.checkpoint()
        decision = self.decision()
        with self.run.locked():
            self.run.land(decision)
        manifest = self.run.checkpoint_manifest()
        self.assertIn("controller/unit-history/u01/r001/pass3.json", manifest["files"])
        self.assertIn("controller/unit-history/u01/r001/land.json", manifest["files"])

    def test_reopen_last_unit_restores_pass2_without_rewriting_accepted_baseline(self):
        self.ready(count=2, refine=True)
        self.run.land(self.decision())
        accepted_name = f"library/writing/craft/{self.live.name}"
        before = self.run.read_accepted(accepted_name)
        self.assertEqual(self.run.state["phase"], "pass1")
        message = self.run.reopen_last_unit("Independent review found a source-fidelity defect.")
        self.assertIn("UNIT REOPENED", message)
        self.assertEqual(self.run.state["unit_index"], 0)
        self.assertEqual(self.run.state["phase"], "pass2")
        self.assertEqual(self.run.read_accepted(accepted_name), before)
        self.assertTrue((self.root / "controller/unit-history/u01/r002/reopen.json").is_file())

    def test_domain_landing_lease_prevents_overlapping_integrations(self):
        self.ready()
        lease = self.repo / f"{workflow.RUN_STORE}/.landing-{self.run.domain}.lock"
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
            # Accepted storage is content-addressed (EXP-003); the accepted
            # manifest write is the deterministic mid-landing seam.
            if path.name == "manifest.json" and path.parent.name.startswith("accepted") and not failed:
                failed = True
                raise OSError("injected landing write failure")
            real_write(path, content)
        with patch.object(workflow, "atomic_write", side_effect=fail_once), self.assertRaises(OSError):
            self.run.land(self.decision())
        self.assertTrue(failed)
        self.assertEqual(workflow.tree_hashes(self.repo / "library"), before)
        self.assertEqual(workflow.Run(self.repo, self.root).state["phase"], "land")
        self.assertTrue((self.root / self.run.state["pass2"]["changes"][0]).is_file())
        self.assertFalse((self.repo / f"{workflow.RUN_STORE}/.landing-{self.run.domain}.lock").exists())

    def test_landing_advances_only_one_unit(self):
        self.ready(count=2)
        self.run.land(self.decision())
        self.assertEqual(self.run.state["phase"], "pass1")
        self.assertEqual(self.run.brief()["unit_id"], "u02")
        with self.assertRaises(workflow.RunError):
            self.run.close()

    def test_unit_audit_history_survives_until_close_run_then_is_discarded(self):
        self.ready(refine=True)
        self.assertTrue((self.root / "controller/audit/preflight.md").is_file())
        self.run.land(self.decision())
        self.assertTrue((self.root / "controller/audit/u01-landing.md").is_file())
        self.assertTrue((self.root / "controller/audit/u01-state-report.json").is_file())
        self.assertTrue((self.root / "controller/unit-history/u01/r001/pass3.json").is_file())
        self.assertTrue((self.root / "controller/unit-history/u01/r001/land.json").is_file())
        self.close_source()
        self.assertTrue((self.root / "controller/unit-history").is_dir())
        hold = self.root / "controller/audit/HOLD.txt"
        hold.write_text("retain for diagnosis\n", encoding="utf-8")
        self.run.close()
        self.assertTrue(hold.is_file())
        self.assertFalse((self.root / "controller/audit/preflight.md").exists())
        self.assertFalse((self.root / "controller/audit/u01-state-report.json").exists())
        self.assertFalse((self.root / "controller/unit-history").exists())

    def test_generated_state_can_be_closed_without_deleting_original_inputs(self):
        self.ready()
        original = self.source.read_bytes()
        retained = self.root / "failure-evidence.md"
        retained.write_text("Explicit evidence hold.\n", encoding="utf-8")
        self.run.land(self.decision())
        self.close_source()
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
            self.assertEqual(stale.state["phase"], "source_prep")
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
        self.audit_changed(record, oid, name, [self.live.stem])
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
        self.run.submit("pass2", self.complete_pass2_attention(record))
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
        self.audit_changed(record, oid, name, [self.live.stem])
        self.run.submit("pass2", self.complete_pass2_attention(record))
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
        self.assertEqual(self.run.state["phase"], "closure_pass2")

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
        self.audit_changed(record, self.live.stem, name, [self.live.stem])
        self.complete_pass2_attention(record)
        self.run.submit("pass2", record)
        self.third()
        self.run.land(self.decision())
        # The move is staged in skill-staging; the live canon is untouched until close.
        self.assertTrue(self.live.exists())
        self.close_source()
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
        self.complete_pass2_attention(record)
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
        self.complete_pass2_attention(record)
        self.run.submit("pass2", record)
        with self.assertRaisesRegex(workflow.RunError, "every active-domain module"):
            self.third()


    def test_exp002_start_uses_short_id_manifest_and_catalog(self):
        self.assertEqual(self.root.parent, self.repo / workflow.RUN_STORE)
        self.assertRegex(self.root.name, r"^r_[0-9a-f]{8}$")
        manifest = workflow.read_run_manifest(self.root, required=True)
        self.assertEqual(manifest["run_id"], self.root.name)
        self.assertEqual(manifest["domain"], "writing")
        self.assertEqual(manifest["genre"], "unclassified")
        self.assertEqual(manifest["display_label"], "original-book-run-one")
        self.assertEqual(manifest["current"]["phase"], "load")
        catalog = json.loads((self.repo / workflow.RUN_CATALOG).read_text(encoding="utf-8"))
        self.assertEqual(catalog["entries"][0]["path"], f"{workflow.RUN_STORE}/{self.root.name}")

    def test_exp002_genre_is_metadata_not_directory_authority(self):
        root = workflow.start(self.repo, self.other_source(), "writing", "genre-test", genre="python")
        manifest = workflow.read_run_manifest(root, required=True)
        self.assertEqual(manifest["genre"], "python")
        self.assertEqual(root.parent, self.repo / workflow.RUN_STORE)
        self.assertNotIn("python", root.parts)
        listed = workflow.list_registered_runs(self.repo, genre="python")
        self.assertEqual([item["run_id"] for item in listed], [root.name])

    def test_exp002_start_over_marks_prior_short_run_abandoned(self):
        old_root = self.root
        old_run_id = old_root.name
        result = workflow.start_over(self.repo, old_root, "Restart fixture from scratch.")
        self.assertEqual(result["outcome"], "started_over")
        self.assertNotEqual(Path(result["new_run"]).name, old_run_id)
        manifest = workflow.read_run_manifest(old_root, required=True)
        self.assertEqual(manifest["current"]["status"], "abandoned")
        self.assertTrue((old_root / workflow.ABANDONED).is_file())
        self.assertNotIn(old_root, workflow.open_runs(self.repo, "writing"))

    def test_exp002_legacy_genre_level_run_root_remains_compatible(self):
        legacy = self.repo / "workspace/skill-staging/writing/python/legacy-book-run"
        (legacy / "controller").mkdir(parents=True)
        (legacy / "drafts").mkdir()
        shutil.copy2(self.root / "controller/run.json", legacy / "controller/run.json")
        run = workflow.Run(self.repo, legacy)
        self.assertEqual(run.domain, "writing")
        self.assertEqual(run.root, legacy.resolve())

    def test_exp002_template_cli_prints_its_phase(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "PASS/pass.py"), "--repo-root", str(self.repo), "template", "--run", str(self.root)],
            capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["phase"], "load")
        self.assertIn("template", payload)

    def test_exp002_portable_controller_forbids_configured_canonical_target(self):
        marker = workflow.sandbox_manifest(workflow.controller_project_root())
        if marker is None:
            # Outside the experimental portable the controller checkout carries
            # no sandbox marker; exercise the guard with a synthetic controller
            # manifest instead of requiring repository state that must not ship.
            synthetic = {"mode": "experimental-sandbox",
                         "forbidden_repo_paths": [str(self.repo.resolve())]}
            with patch.object(workflow, "sandbox_manifest", return_value=synthetic):
                with self.assertRaisesRegex(workflow.RunError, "refuses canonical repo root"):
                    workflow.enforce_experimental_controller_target(self.repo)
            return
        forbidden = marker.get("forbidden_repo_paths") or []
        self.assertTrue(forbidden)
        with self.assertRaisesRegex(workflow.RunError, "refuses canonical repo root"):
            workflow.enforce_experimental_controller_target(Path(forbidden[0]))

    def test_exp002_run_export_import_hashes_and_collision_policy(self):
        archive = Path(self.temporary.name) / "run-export.zip"
        exported = workflow.export_run(self.repo, self.root, archive)
        self.assertTrue(exported.is_file())
        with self.assertRaisesRegex(workflow.RunError, "run_id collision"):
            workflow.import_run(self.repo, exported)
        imported = workflow.import_run(self.repo, exported, collision="new-id")
        self.assertNotEqual(imported.name, self.root.name)
        imported_manifest = workflow.read_run_manifest(imported, required=True)
        self.assertEqual(imported_manifest["domain"], "writing")
        self.assertEqual(workflow.Run(self.repo, imported).state["phase"], "load")

    def test_exp002_path_budget_rejects_windows_incompatible_paths(self):
        too_long = Path("C:/") / ("a" * 201) / ("b" * 60)
        with self.assertRaisesRegex(workflow.RunError, "Windows path budget|path component"):
            workflow.validate_windows_path_budget(too_long, "fixture path")

    def test_exp002_flag_error_prints_valid_pattern(self):
        self.begin()
        record = self.run.template()
        record["full_read"] = True
        record["secondary_subject_flags"] = [{"flag_id": "Bad-ID", "subject": "Invalid identifier fixture."}]
        with self.assertRaisesRegex(workflow.RunError, r"expected \^\[a-z\]"):
            self.run.submit("pass1", record)

    def test_exp002_deferred_flag_requires_destination_or_closure_condition(self):
        self.begin()
        self.first(flags=True)
        record = self.run.template()
        record["full_reread"] = True
        record["omission_sweep"]["complete"] = True
        flag = record["flag_resolutions"][0]
        flag.update(outcome="deferred", reason="Needs a later bounded evidence check.", deferred_to="")
        with self.assertRaisesRegex(workflow.RunError, "deferred_to"):
            self.run.submit("pass2", record)
        flag["deferred_to"] = "Resolve during U02 when the named API contract is in scope."
        self.complete_pass2_attention(record)
        self.run.submit("pass2", record)
        self.assertEqual(self.run.state["pass2"]["flag_resolutions"][0]["outcome"], "deferred")

    def test_exp002_reinforce_requires_reinforces_core_scope(self):
        self.begin()
        self.first()
        record = self.run.template()
        record["full_reread"] = True
        record["omission_sweep"]["complete"] = True
        record["buckets"]["REINFORCE"] = [{"object_id": self.live.stem, "reason": "The owner remains sufficient."}]
        self.complete_pass2_attention(record)
        record["reinforcement_evidence"][0]["scope"] = "related_background"
        with self.assertRaisesRegex(workflow.RunError, "reinforces_core"):
            self.run.submit("pass2", record)
        record["reinforcement_evidence"][0]["scope"] = "reinforces_core"
        self.run.submit("pass2", record)

    def test_exp002_amendment_preserves_superseded_packet_and_revision(self):
        self.ready(count=2, refine=True)
        decision = self.decision()
        original_packet_sha = decision["presentation_sha256"]
        self.run.land(decision)
        first_land = self.root / "controller/unit-history/u01/r001/land.json"
        first_before = first_land.read_bytes()
        first_record = json.loads(first_before)
        first_fingerprint = first_record["accepted_delta_fingerprint"]

        self.run.reopen_last_unit("Independent review found a source-fidelity defect.")
        amendment = json.loads((self.root / "controller/unit-history/u01/r002/amendment.json").read_text(encoding="utf-8"))
        self.assertEqual(amendment["from_revision"], "r001")
        self.assertEqual(amendment["superseded_landing_packet_sha256"], original_packet_sha)
        self.assertEqual(amendment["superseded_accepted_delta_fingerprint"], first_fingerprint)
        self.assertEqual(amendment["required_rechecks"], ["pass2", "pass3", "land"])

        self.second(refine=False)
        self.third()
        self.run.land(self.decision())
        second_record = json.loads((self.root / "controller/unit-history/u01/r002/land.json").read_text(encoding="utf-8"))
        self.assertEqual(second_record["supersedes_revision"], "r001")
        self.assertEqual(first_land.read_bytes(), first_before, "amendment must not rewrite accepted history")

    def test_exp002_checkpoint_failure_reports_persisted_state_and_recovers_previous_checkpoint(self):
        self.run.checkpoint()
        old_manifest = self.run.checkpoint_manifest()
        self.assertEqual(old_manifest["phase"], "load")
        self.run.state["stop_after"] = "source_prep"
        self.run.save()
        persisted_sha = workflow.digest(self.run.state_path)
        real_rename = Path.rename

        def fail_fresh(path, target):
            if Path(path).name == "checkpoint.new":
                raise PermissionError(13, "Access is denied", str(path))
            return real_rename(path, target)

        with patch.object(Path, "rename", new=fail_fresh):
            with self.assertRaises(workflow.CheckpointPromotionError) as caught:
                self.run.checkpoint()
        self.assertEqual(caught.exception.state_sha256, persisted_sha)
        self.assertTrue(caught.exception.previous_checkpoint_restored)
        diagnostic = json.loads((self.root / "controller/checkpoint-failure.json").read_text(encoding="utf-8"))
        self.assertEqual(diagnostic["outcome"], "authoritative_state_persisted_checkpoint_not_advanced")
        self.assertEqual(workflow.digest(self.run.state_path), persisted_sha)
        self.assertEqual(self.run.checkpoint_manifest()["state_sha256"], old_manifest["state_sha256"])

        message = self.run.recover(rollback_authoritative=True)
        self.assertIn("RECOVERED", message)
        self.assertEqual(self.run.state["stop_after"], "complete")
        self.assertFalse((self.root / "controller/checkpoint-failure.json").exists())
        self.assertFalse((self.root / "controller/checkpoint.new").exists())

    def test_exp002_recover_refuses_silent_rewind_without_explicit_intent(self):
        self.run.checkpoint()
        self.run.state["stop_after"] = "source_prep"
        self.run.save()
        with self.assertRaisesRegex(workflow.RunError, "refusing destructive recovery"):
            self.run.recover()
        self.assertEqual(self.run.state["stop_after"], "source_prep", "refusal must not mutate authoritative state")
        message = self.run.recover(rollback_authoritative=True)
        self.assertIn("RECOVERED", message)
        self.assertEqual(self.run.state["stop_after"], "complete")


if __name__ == "__main__":
    unittest.main()
