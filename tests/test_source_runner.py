import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from PASS.runtime import pass_authoring_run as preflight
from PASS.runtime import pass_source_prep
from PASS.runtime.pass_authoring_workflow import Run, SEMANTIC_CHECKS, BUCKETS, TAXONOMY, required_documents, resume, start
from PASS.runtime.pass_source_runner import advance, authorize, drive, progress_report


PROJECT = Path(__file__).resolve().parents[1]


class SourceRunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo_temp = tempfile.TemporaryDirectory(prefix="pass-source-runner-repo-")
        cls.repo = Path(cls.repo_temp.name) / "repo"
        cls.repo.mkdir()
        shutil.copytree(PROJECT / "PASS", cls.repo / "PASS")
        shutil.copytree(PROJECT / "library", cls.repo / "library")
        (cls.repo / "workspace" / "release-recipes").mkdir(parents=True)
        for recipe in (PROJECT / "workspace" / "release-recipes").glob("*.yaml"):
            shutil.copy2(recipe, cls.repo / "workspace" / "release-recipes" / recipe.name)
        shutil.copy2(PROJECT / "AGENTS.md", cls.repo / "AGENTS.md")

    @classmethod
    def tearDownClass(cls):
        cls.repo_temp.cleanup()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="pass-source-runner-test-")
        self.source = Path(self.temp.name) / "source.txt"
        # Runs share one fixture repo, so each test needs its own source bytes;
        # identical bytes would be refused as a duplicate of an earlier run.
        self.source.write_text(f"bounded source bytes for {self.id()}\n", encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def make_run(self, task="runner-test"):
        root = start(self.repo, self.source, "writing", task)
        run = Run(self.repo, root)
        run.submit("load", {"schema_version": 1, "documents_read": required_documents(self.repo)})
        pass_source_prep.prepare(run)
        pass_source_prep.finalize(run)
        record = preflight.template_record()
        record.update(
            title="Test Source",
            author="Test Author",
            domain="writing",
            extent="one bounded test unit",
            text_quality="clean text",
            subject="Test one unattended source run without changing canonical knowledge.",
            mode="unit ingestion",
            units=[{
                "unit_id": "u01",
                "material": "Test material",
                "locator": "entire source",
                "source_pages": None,
                "printed_pages": None,
                "overlap_object_ids": [],
                "card_potential": "low",
            }],
            no_extract=[],
        )
        run.submit("preflight", record)
        authorize(run, "User explicitly asked this one source to continue unattended through completion.")
        result = advance(run)
        self.assertEqual(result["outcome"], "advanced")
        self.assertEqual(run.state["phase"], "pass1")
        return run

    def submit_empty_unit(self, run, approval_required=False):
        issued = drive(run)
        self.assertEqual(issued["outcome"], "host_action_required")
        self.assertEqual(issued["action"]["phase"], "pass1")
        run.submit("pass1", {
            "schema_version": 1,
            "unit_id": "u01",
            "full_read": True,
            "working_drafts": [],
            "overlap_object_ids": [],
            "secondary_subject_flags": [],
            "questions": [],
        })
        issued = drive(run)
        self.assertEqual(issued["action"]["phase"], "pass2")
        run.submit("pass2", {
            "schema_version": 1,
            "unit_id": "u01",
            "full_reread": True,
            "flag_resolutions": [],
            "buckets": {name: [] for name in BUCKETS},
            "taxonomy": {name: [] for name in TAXONOMY},
            "changes": [],
            "removals": [],
            "approval_required": approval_required,
            "owner_reconciliation": [],
            "metadata_classification": [],
        })
        issued = drive(run)
        self.assertEqual(issued["action"]["phase"], "pass3")
        with patch.object(run, "validate", return_value=None):
            run.submit("pass3", {
                "schema_version": 1,
                "unit_id": "u01",
                "card_only_review": True,
                "checks": {name: True for name in SEMANTIC_CHECKS},
                "reviewed_sha256": {},
            })
        self.assertEqual(run.state["phase"], "land")

    def submit_empty_closure(self, run):
        issued = drive(run)
        self.assertEqual(issued["outcome"], "host_action_required")
        self.assertEqual(issued["action"]["phase"], "closure_pass2")
        record = run.template()
        record["closure_audits"] = {name: True for name in record["closure_audits"]}
        run.submit("closure_pass2", record)
        issued = drive(run)
        self.assertEqual(issued["action"]["phase"], "closure_pass3")
        record = run.template()
        record["card_only_review"] = True
        record["checks"] = {name: True for name in SEMANTIC_CHECKS}
        with patch.object(run, "validate", return_value=None):
            run.submit("closure_pass3", record)
        self.assertEqual(run.state["phase"], "closure_land")

    def test_source_identity_is_captured_only_after_load(self):
        root = start(self.repo, self.source, "writing", "identity-after-load")
        run = Run(self.repo, root)
        self.assertFalse(run.source_identity_path().exists())
        run.submit("load", {"schema_version": 1, "documents_read": required_documents(self.repo)})
        self.assertTrue(run.source_identity_path().is_file())
        self.assertEqual(run.source_identity()["sha256"], __import__("hashlib").sha256(self.source.read_bytes()).hexdigest())

    def test_unattended_routine_gates_archive_and_complete(self):
        run = self.make_run()
        preflight_packet = run.root / "controller" / "audit" / "preflight.md"
        self.assertTrue(preflight_packet.is_file())
        self.submit_empty_unit(run, approval_required=False)
        with patch.object(run, "validate", return_value=None), patch.object(run, "tool", return_value=None):
            result = advance(run)
        self.assertEqual(result["outcome"], "advanced")
        self.assertEqual(run.state["phase"], "closure_pass2")
        self.assertTrue((run.root / "controller" / "audit" / "u01-landing.md").is_file())
        self.submit_empty_closure(run)
        with patch.object(run, "validate", return_value=None), patch.object(run, "tool", return_value=None):
            result = advance(run)
        self.assertEqual(result["outcome"], "advanced")
        self.assertEqual(run.state["phase"], "finished")
        self.assertTrue((run.root / "controller" / "audit" / "closure-landing.md").is_file())
        with patch("PASS.runtime.pass_source_runner.run_tool", return_value="ok"):
            completion = advance(run)
        self.assertEqual(completion["outcome"], "source_complete")
        self.assertTrue((run.root / "controller" / "source-completion.json").is_file())

    def test_approval_required_is_a_hard_stop(self):
        run = self.make_run(task="approval-stop")
        self.submit_empty_unit(run, approval_required=True)
        result = advance(run)
        self.assertEqual(result["outcome"], "blocked_human_required")
        self.assertEqual(run.state["phase"], "land")
        self.assertTrue((run.root / "controller" / "audit" / "u01-landing.md").is_file())

    def test_close_removes_owned_runner_state_but_preserves_unknown_hold(self):
        run = self.make_run(task="close-test")
        self.submit_empty_unit(run, approval_required=False)
        with patch.object(run, "validate", return_value=None), patch.object(run, "tool", return_value=None):
            advance(run)
        self.submit_empty_closure(run)
        with patch.object(run, "validate", return_value=None), patch.object(run, "tool", return_value=None):
            advance(run)
        hold = run.root / "controller" / "audit" / "HOLD.txt"
        hold.write_text("retain for diagnosis\n", encoding="utf-8")
        run.close()
        self.assertFalse((run.root / "controller" / "run.json").exists())
        self.assertFalse((run.root / "controller" / "audit" / "preflight.md").exists())
        self.assertTrue(hold.is_file())

    def test_authorized_preflight_requires_drive_lease(self):
        root = start(self.repo, self.source, "writing", "preflight-lease")
        run = Run(self.repo, root)
        run.submit("load", {"schema_version": 1, "documents_read": required_documents(self.repo)})
        pass_source_prep.prepare(run)
        pass_source_prep.finalize(run)
        authorize(run, "User asked for unattended source completion.")
        record = preflight.template_record()
        record.update(
            title="Test Source", author="Test Author", domain="writing",
            extent="one unit", text_quality="clean",
            subject="Test unattended dispatcher entry.", mode="unit ingestion",
            units=[{"unit_id":"u01","material":"Test material","locator":"entire source","source_pages":None,"printed_pages":None,"overlap_object_ids":[],"card_potential":"low"}],
            no_extract=[],
        )
        with self.assertRaisesRegex(Exception, "no issued action lease"):
            run.submit("preflight", record)
        issued = drive(run)
        self.assertEqual(issued["action"]["phase"], "preflight")
        run.submit("preflight", record)
        self.assertEqual(run.state["phase"], "preflight_accept")

    def test_unattended_submit_requires_dispatch_lease(self):
        run = self.make_run(task="lease-required")
        with self.assertRaisesRegex(Exception, "no issued action lease"):
            run.submit("pass1", {
                "schema_version": 1, "unit_id": "u01", "full_read": True,
                "working_drafts": [], "overlap_object_ids": [],
                "secondary_subject_flags": [], "questions": [],
            })
        issued = drive(run)
        self.assertEqual(issued["action"]["phase"], "pass1")
        self.assertTrue((run.root / "controller" / "next-action.json").is_file())

    def test_resume_after_context_loss_reissues_the_same_lease(self):
        run = self.make_run(task="lease-resume")
        issued = drive(run)["action"]
        fresh = Run(self.repo, run.root)
        picked = resume(self.repo, run.root)
        self.assertEqual((picked["outcome"], picked["mode"]), ("resume", "unattended"))
        self.assertIn("source.py drive", picked["next_action"])
        self.assertIn("current", picked["action_lease"])
        self.assertEqual(drive(fresh)["action"]["action_id"], issued["action_id"])
        fresh.submit("pass1", {
            "schema_version": 1, "unit_id": "u01", "full_read": True,
            "working_drafts": [], "overlap_object_ids": [],
            "secondary_subject_flags": [], "questions": [],
        })
        self.assertEqual(resume(self.repo, run.root)["action_lease"], "none issued; source.py drive will issue one")
        (run.root / "controller" / "next-action.json").write_text(json.dumps(issued), encoding="utf-8")
        self.assertIn("stale", resume(self.repo, run.root)["action_lease"])
        self.assertEqual(drive(fresh)["action"]["phase"], "pass2")
        self.assertTrue((run.root / "controller" / "action-history" / f"stale-{issued['action_id']}.json").is_file())

    def test_progress_report_is_controller_derived(self):
        run = self.make_run(task="authoritative-report")
        report = progress_report(run)
        self.assertEqual(report["units_completed"], 0)
        self.assertFalse(report["source_complete"])
        self.assertIn("0/1 units accepted", report["statement"])

    def test_rebind_requires_identical_source_bytes(self):
        run = self.make_run(task="rebind-test")
        moved = Path(self.temp.name) / "moved-source.txt"
        self.source.replace(moved)
        # A verified prepared package keeps unattended work possible without the raw source.
        self.assertIsNotNone(run.unattended_authorization(required=True))
        shutil.rmtree(run.root / "prepared-source")
        with self.assertRaisesRegex(Exception, "rebind"):
            run.unattended_authorization(required=True)
        message = run.rebind_source(moved)
        self.assertIn("SOURCE REBOUND", message)
        self.assertIsNotNone(run.unattended_authorization(required=True))
        wrong = Path(self.temp.name) / "wrong.txt"
        wrong.write_text("different bytes\n", encoding="utf-8")
        with self.assertRaisesRegex(Exception, "does not match"):
            run.rebind_source(wrong)


if __name__ == "__main__":
    unittest.main()
