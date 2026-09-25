#!/usr/bin/env python3
"""Regression tests for authoritative PASS start-over semantics.

Run directly from the project root:

    python workspace/tools/test_pass_start_over.py
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
import uuid
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from PASS.runtime import pass_authoring_run as preflight
from PASS.runtime import pass_source_prep as source_prep
from PASS.runtime.pass_authoring_workflow import (
    Run,
    RunError,
    required_documents,
    start,
    start_over,
)


class StartOverTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = Path(tempfile.mkdtemp(prefix="pass-start-over-"))
        self.source = self.tempdir / "source.md"
        self.source.write_text("# Synthetic source\n\nPython 2 and Python 3 material.\n", encoding="utf-8")
        self.created: list[Path] = []

    def tearDown(self) -> None:
        for path in self.created:
            if path.exists():
                shutil.rmtree(path)
        shutil.rmtree(self.tempdir, ignore_errors=True)

    def new_run(self, prefix: str) -> Run:
        task = f"{prefix}-{uuid.uuid4().hex[:8]}"
        root = start(REPO, self.source, "software-engineering", task, "complete")
        self.created.append(root)
        return Run(REPO, root)

    def prepare_source(self, run: Run) -> None:
        run.submit("load", {"schema_version": 1, "documents_read": required_documents(REPO)})
        source_prep.prepare(run)
        source_prep.finalize(run)
        self.assertEqual(run.state["source_prep"]["status"], "verified")

    def language_plan(self) -> dict:
        plan = preflight.template_record("software-engineering")
        plan.update(
            author="Regression",
            extent="1 unit",
            text_quality="good",
            subject="Python programming",
        )
        plan["language_policy"] = {
            "classification": "programming-language",
            "language": "Python",
            "target_version": "3.14.7",
            "target_basis": "verified current target for regression",
            "modernization_required": True,
        }
        return plan

    def track_replacement(self, result: dict) -> Run:
        root = Path(result["new_run"])
        self.created.append(root)
        return Run(REPO, root)

    def test_scratch_reset_overrides_stale_checkpoint_lease_and_carries_notes(self) -> None:
        old = self.new_run("reset-scratch")
        (old.root / "NOTES.md").write_text("carry this correction\n", encoding="utf-8")
        (old.root / "controller/operation.lock").write_text(
            json.dumps({"pid": 99999999, "acquired_at": "stale"}) + "\n",
            encoding="utf-8",
        )

        result = start_over(
            REPO,
            old.root,
            "user explicitly said start completely over",
            "scratch",
            True,
        )
        replacement = self.track_replacement(result)

        self.assertEqual(replacement.state["phase"], "load")
        self.assertEqual((replacement.root / "NOTES.md").read_text(encoding="utf-8"), "carry this correction\n")
        self.assertTrue((old.root / "controller/abandoned-run.json").is_file())
        self.assertFalse((old.root / "controller/run.json").exists())
        self.assertFalse((old.root / "controller/reset-intent.json").exists())
        with self.assertRaisesRegex(RunError, "abandoned"):
            Run(REPO, old.root)

    def test_source_prep_reset_carries_only_verified_preparation(self) -> None:
        old = self.new_run("reset-source-prep")
        self.prepare_source(old)
        result = start_over(REPO, old.root, "rerun from prepared source only", "source_prep")
        replacement = self.track_replacement(result)

        self.assertEqual(replacement.state["phase"], "preflight")
        self.assertIsNone(replacement.state["plan"])
        manifest = source_prep.verify(replacement)
        self.assertEqual(manifest["unit_files"], {})

    def test_preflight_reset_starts_at_pass1_with_schema3_plan(self) -> None:
        old = self.new_run("reset-preflight")
        self.prepare_source(old)
        old.submit("preflight", self.language_plan())
        # This fixture bypasses only the presentation ceremony; it represents an
        # already-accepted preflight so start-over carry semantics can be tested.
        old.state["phase"] = "pass1"
        old.save()

        result = start_over(REPO, old.root, "reuse only prep and accepted preflight", "preflight")
        replacement = self.track_replacement(result)

        self.assertEqual(replacement.state["phase"], "pass1")
        self.assertEqual(replacement.state["unit_index"], 0)
        self.assertEqual(replacement.state["plan"]["language_policy"]["target_version"], "3.14.7")
        source_prep.verify(replacement)

    def test_legacy_se_preflight_cannot_bypass_new_language_policy(self) -> None:
        old = self.new_run("reset-legacy-preflight")
        self.prepare_source(old)
        plan = self.language_plan()
        plan.pop("language_policy")
        plan["schema_version"] = 2
        old.submit("preflight", plan)
        old.state["phase"] = "pass1"
        old.save()

        with self.assertRaisesRegex(RunError, "restart from source_prep"):
            start_over(REPO, old.root, "reuse legacy preflight", "preflight")

    def test_reset_intent_blocks_old_state_resurrection(self) -> None:
        old = self.new_run("reset-intent")
        intent = {
            "schema_version": 1,
            "requested_at": "2026-09-25T00:00:00+00:00",
            "reason": "start over",
            "restart_from": "scratch",
            "carry_notes": False,
            "new_task": "synthetic-restart",
            "domain": "software-engineering",
            "source": str(self.source.resolve()),
            "state": old.state,
        }
        (old.root / "controller/reset-intent.json").write_text(json.dumps(intent), encoding="utf-8")
        with self.assertRaisesRegex(RunError, "start-over intent"):
            Run(REPO, old.root)
        with self.assertRaisesRegex(RunError, "start-over intent"):
            old.save()


if __name__ == "__main__":
    unittest.main(verbosity=2)
