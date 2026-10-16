#!/usr/bin/env python3
"""Regression tests for Software Engineering language modernization policy.

Run directly from the project root:

    python workspace/tools/test_pass_language_policy.py
"""

from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
import uuid
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from PASS.runtime import pass_authoring_run as preflight
from PASS.runtime.pass_authoring_workflow import Run, RunError, start


def language_plan() -> dict:
    plan = preflight.template_record("software-engineering")
    plan.update(
        author="Regression",
        extent="1 bounded unit",
        text_quality="good",
        subject="Python programming",
    )
    plan["language_policy"] = {
        "classification": "programming-language",
        "language": "Python",
        "target_version": "3.14.7",
        "target_basis": "current target verified for this regression",
        "modernization_required": True,
    }
    return plan


class PreflightPolicyTests(unittest.TestCase):
    def test_schema3_round_trip_preserves_language_policy(self) -> None:
        record = preflight.parse_preflight(language_plan())
        round_trip = preflight.parse_preflight(preflight.serialize_preflight(record))
        self.assertEqual(round_trip, record)
        self.assertEqual(round_trip.language_policy.target_version, "3.14.7")

    def test_schema2_remains_readable_without_new_policy(self) -> None:
        plan = language_plan()
        plan.pop("language_policy")
        plan["schema_version"] = 2
        record = preflight.parse_preflight(plan)
        self.assertIsNone(record.language_policy)
        self.assertNotIn("language_policy", preflight.serialize_preflight(record))

    def test_new_software_engineering_plan_must_classify_source(self) -> None:
        plan = preflight.template_record("software-engineering")
        plan.update(author="Regression", extent="1 unit", text_quality="good", subject="SE")
        with self.assertRaises(preflight.PreflightError):
            preflight.parse_preflight(plan)

    def test_programming_language_policy_cannot_disable_modernization(self) -> None:
        plan = language_plan()
        plan["language_policy"]["modernization_required"] = False
        with self.assertRaises(preflight.PreflightError):
            preflight.parse_preflight(plan)


class WorkflowPolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = Path(tempfile.mkdtemp(prefix="pass-language-policy-"))
        self.source = self.tempdir / "source.txt"
        self.source.write_text("synthetic source", encoding="utf-8")
        self.task = "language-policy-" + uuid.uuid4().hex[:10]
        self.root = start(REPO, self.source, "software-engineering", self.task, "complete")
        self.run = Run(REPO, self.root)
        # Source Prep is independently tested. Put this synthetic controller run
        # directly at preflight so this file exercises only the policy gates.
        self.run.state["phase"] = "preflight"
        self.run.save()

    def tearDown(self) -> None:
        if self.root.exists():
            shutil.rmtree(self.root)
        shutil.rmtree(self.tempdir, ignore_errors=True)

    def test_pass1_pass2_pass3_language_gates(self) -> None:
        self.run.submit("preflight", language_plan())
        self.run.state["phase"] = "pass1"  # bypass presentation only in regression fixture
        self.run.save()

        pass1 = self.run.template()
        self.assertIn("version_sensitive_flags", pass1)
        pass1["full_read"] = True
        pass1["version_sensitive_flags"] = [
            {
                "flag_id": "dict_order",
                "source_claim": "Dictionary ordering is not guaranteed.",
                "reason": "language guarantee changed across versions",
            }
        ]
        self.run.submit("pass1", pass1)

        pass2 = self.run.template()
        audit = pass2["language_modernization"]
        self.assertEqual(audit["target_version"], "3.14.7")
        pass2["full_reread"] = True
        audit["all_version_sensitive_material_reviewed"] = True
        audit["resolutions"][0].update(
            disposition="modernized",
            current_guidance="Use the target version's current ordering guarantee.",
            verification="Checked against the accepted target-version documentation/toolchain.",
        )
        self.run.submit("pass2", pass2)

        pass3 = self.run.template()
        self.assertIn("core_language_agnosticism", pass3["checks"])
        self.assertIn("language_modernization", pass3["checks"])

    def test_schema3_revision_cannot_drop_language_policy(self) -> None:
        self.run.submit("preflight", language_plan())
        legacy = language_plan()
        legacy.pop("language_policy")
        legacy["schema_version"] = 2
        with self.assertRaisesRegex(RunError, "retain schema_version 3"):
            self.run.revise_preflight(legacy)


if __name__ == "__main__":
    unittest.main(verbosity=2)
