#!/usr/bin/env python3
"""Regression tests for Source Prep integrity and preflight-boundary gates.

Run from the project root:

    python workspace/tools/test_pass_source_quality.py
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
from PASS.runtime import pass_source_runner
from PASS.runtime.pass_authoring_workflow import Run, RunError, required_documents, start


def language_plan(units: list[dict] | None = None) -> dict:
    plan = preflight.template_record("software-engineering")
    plan.update(
        author="Regression",
        extent="synthetic",
        text_quality="good",
        subject="Python programming",
    )
    plan["language_policy"] = {
        "classification": "programming-language",
        "language": "Python",
        "target_version": "3.14.7",
        "target_basis": "regression fixture",
        "modernization_required": True,
    }
    if units is not None:
        plan["units"] = units
    return plan


class CorruptionSignalTests(unittest.TestCase):
    def test_explicit_decode_corruption_fails_code_page(self) -> None:
        metrics = source_prep._text_corruption_metrics(">>> value = \ufffd\n", code_signal_lines=3)
        self.assertEqual(metrics["status"], "fail")
        self.assertGreater(metrics["replacement_or_cid_markers"], 0)

    def test_c1_bullet_artifacts_do_not_false_fail(self) -> None:
        text = "\n".join("\x82 Line %d explains the code." % n for n in range(1, 30))
        metrics = source_prep._text_corruption_metrics(text, code_signal_lines=20)
        self.assertEqual(metrics["status"], "pass")
        self.assertGreater(metrics["c1_control_chars"], 0)


class SourceQualityWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = Path(tempfile.mkdtemp(prefix="pass-source-quality-"))
        self.source = self.tempdir / "source.txt"
        self.source.write_text("synthetic source\n", encoding="utf-8")
        self.task = "quality-" + uuid.uuid4().hex[:10]
        self.root = start(REPO, self.source, "software-engineering", self.task, "complete")
        self.run = Run(REPO, self.root)
        self.run.submit("load", {"schema_version": 1, "documents_read": required_documents(REPO)})
        source_prep.prepare(self.run)
        source_prep.finalize(self.run)

    def tearDown(self) -> None:
        if self.root.exists():
            shutil.rmtree(self.root)
        shutil.rmtree(self.tempdir, ignore_errors=True)

    def manifest(self) -> tuple[Path, dict]:
        path = self.root / "prepared-source/source.json"
        return path, json.loads(path.read_text(encoding="utf-8"))

    def write_manifest(self, data: dict) -> None:
        path = self.root / "prepared-source/source.json"
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    def test_hard_integrity_failure_blocks_verify_and_finalize_path(self) -> None:
        path, manifest = self.manifest()
        manifest["schema_version"] = 5
        manifest["integrity_gate"].update(
            status="fail",
            hard_failures=[{"page": 1, "failure": "corrupted code extraction"}],
            review_requirements=[],
        )
        self.write_manifest(manifest)
        with self.assertRaisesRegex(RunError, "failed closed"):
            source_prep.verify(self.run)

    def test_legacy_table_warning_upgrades_to_unattended_review_gate(self) -> None:
        path, manifest = self.manifest()
        manifest["schema_version"] = 4
        manifest["integrity_gate"] = {
            "status": "warning",
            "warnings": [{
                "page": None,
                "warning": "source-wide table sanity check: 9 numbered table signals but zero structured tables; inspect table preservation before preflight acceptance",
            }],
            "policy": "legacy",
            "raw_code_signal_lines": 0,
            "detected_code_blocks": 0,
            "raw_table_signal_lines": 9,
            "detected_structured_tables": 0,
        }
        self.write_manifest(manifest)
        audit = self.run.preflight_quality_audit()
        self.assertEqual(len(audit["source_review"]), 1)

        self.run.submit("preflight", language_plan())
        pass_source_runner.authorize(self.run, "regression unattended source")
        packet = self.run.present()
        marker = self.run.preflight_presentation_marker(required=True)
        decision = {
            "schema_version": 1,
            "presentation_sha256": marker["sha256"],
            "subject": self.run.state["plan"]["subject"],
            "basis": "unattended authorization",
            "reason": "regression",
        }
        self.assertTrue(packet)
        with self.assertRaisesRegex(RunError, "explicit human/frontier review"):
            self.run.accept_preflight(decision)

    def test_strong_heading_in_neighboring_unit_blocks_preflight(self) -> None:
        # Replace the text package with a deterministic synthetic PDF-style page
        # package so the boundary auditor can be exercised without OCR/PDF deps.
        package = self.root / "prepared-source"
        shutil.rmtree(package)
        pages = package / "pages"
        pages.mkdir(parents=True)
        segments = []
        for page_no in range(1, 21):
            content = f"<!-- source-page: {page_no} -->\n\n"
            if page_no == 1:
                content += "# Foundations\n\n"
            if page_no == 12:
                content += "# Dynamic Programming\n\n"
            content += f"Body page {page_no}.\n"
            path = pages / f"P{page_no:04d}.md"
            path.write_text(content, encoding="utf-8")
            segments.append({
                "page": page_no,
                "file": f"pages/{path.name}",
                "chars": len(content),
                "tokens": max(1, len(content) // 4),
                "low_text": False,
                "tables": 0,
                "visuals": 0,
                "integrity_ratio": 1.0,
                "sha256": source_prep.digest(path),
                "raw_sha256": "sha256:synthetic",
                "body_font_size": 10.0,
                "table_inventory": [],
                "visual_inventory": [],
                "integrity": {"code_blocks": 0, "code_blocks_preserved": 0},
                "warnings": [],
                "hard_failures": [],
                "review_requirements": [],
            })
        (package / "INDEX.md").write_text("# synthetic index\n", encoding="utf-8")
        identity = self.run.source_identity()
        files = source_prep.package_files(self.run)
        manifest = {
            "schema_version": 5,
            "source": {"name": identity["name"], "size": identity["size"], "sha256": identity["sha256"]},
            "source_kind": "pdf",
            "extractor": "synthetic",
            "normalization": "synthetic",
            "preservation_contract": "synthetic",
            "low_text_threshold": 80,
            "compatibility_baseline": [],
            "integrity_gate": {
                "status": "pass", "warnings": [], "hard_failures": [], "review_requirements": [],
                "policy": "synthetic", "raw_code_signal_lines": 0, "detected_code_blocks": 0,
                "raw_table_signal_lines": 0, "detected_table_candidates": 0, "detected_structured_tables": 0,
            },
            "segments": segments,
            "unit_files": {},
            "files": files,
            "package_sha256": source_prep.package_digest(files),
        }
        self.write_manifest(manifest)
        self.run.state["source_prep"] = {
            "status": "verified", "package": "prepared-source", "package_sha256": manifest["package_sha256"],
            "segments": 20, "extractor": "synthetic", "integrity": "pass", "compatibility_baseline": [],
        }
        self.run.state["phase"] = "preflight"
        self.run.save()

        units = [
            {"unit_id": "u01", "material": "Foundations", "locator": "PDF 1-9", "source_pages": {"start": 1, "end": 9}, "printed_pages": None, "overlap_object_ids": [], "card_potential": "low"},
            {"unit_id": "u02", "material": "Dynamic Programming", "locator": "PDF 10-10", "source_pages": {"start": 10, "end": 10}, "printed_pages": None, "overlap_object_ids": [], "card_potential": "high"},
            {"unit_id": "u03", "material": "Advanced Topics", "locator": "PDF 11-20", "source_pages": {"start": 11, "end": 20}, "printed_pages": None, "overlap_object_ids": [], "card_potential": "medium"},
        ]
        with self.assertRaisesRegex(RunError, "unit-boundary gate failed"):
            self.run.submit("preflight", language_plan(units))


if __name__ == "__main__":
    unittest.main(verbosity=2)
