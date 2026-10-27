#!/usr/bin/env python3
"""Regression gates for PASS scoped validation and low-churn orchestration."""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "PASS" / "tools"))

from PASS.runtime.pass_authoring_workflow import Run, RunError, digest
import build_index
import module_runtime
import validate as pass_validate


MINIMAL_CARD = """---
object_id: PAT_minimal
object_type: pattern
name: Minimal
library_path: [pkg-a]
stage_binding: 0 design
lane_fit: both
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags: []
cross_links: []
confidence: high
references: []
variants: []
---
# Minimal
"""


class ScopedValidationTests(unittest.TestCase):
    def test_package_validation_full_parses_only_selected_package(self) -> None:
        with tempfile.TemporaryDirectory(prefix="pass-scope-") as td:
            library = Path(td)
            a = library / "pkg-a" / "PAT_minimal.md"
            b = library / "pkg-b" / "PAT_other.md"
            a.parent.mkdir(parents=True)
            b.parent.mkdir(parents=True)
            a.write_text(MINIMAL_CARD, encoding="utf-8")
            b.write_text(MINIMAL_CARD.replace("PAT_minimal", "PAT_other").replace("[pkg-a]", "[pkg-b]"), encoding="utf-8")

            parsed: list[Path] = []
            original = pass_validate.parse_object

            def recording(path: Path, root: Path):
                parsed.append(path)
                return original(path, root)

            with mock.patch.object(pass_validate, "parse_object", side_effect=recording):
                pass_validate.validate_library(library, "pkg-a")

            self.assertEqual(parsed, [a])

    def test_package_runtime_scan_ignores_unrelated_package_files(self) -> None:
        with tempfile.TemporaryDirectory(prefix="pass-runtime-scope-") as td:
            library = Path(td)
            (library / "pkg-a").mkdir()
            other = library / "pkg-b"
            other.mkdir()
            (other / "stray.py").write_text("print('outside runtime')\n", encoding="utf-8")
            self.assertEqual(module_runtime.runtime_problems(library, "pkg-a"), [])
            self.assertTrue(any("stray.py" in problem for _, problem in module_runtime.runtime_problems(library)))

    def test_generated_indexes_remain_byte_identical(self) -> None:
        library = REPO / "library"
        cards = build_index.load_cards(library)
        context = build_index.IndexContext(library, cards)
        software = library / "software-engineering"
        directories = {d for d in context.directories if d == software or software in d.parents}
        children = {}
        for directory in directories:
            children.setdefault(directory.parent, []).append(directory)
        old_children = context.children_by_dir
        context.children_by_dir = {parent: sorted(items) for parent, items in children.items()}
        try:
            for directory in directories:
                expected = (directory / "INDEX.md").read_text(encoding="utf-8")
                self.assertEqual(build_index.render_from_context(directory, context), expected)
        finally:
            context.children_by_dir = old_children


class WorkflowPerformanceContractTests(unittest.TestCase):
    def _run_stub(self) -> Run:
        run = Run.__new__(Run)
        run.repo = REPO
        run.root = REPO
        run.state = {
            "domain": "software-engineering",
            "phase": "land",
            "pass2": {
                "changes": [],
                "removals": [],
                "buckets": {key: [] for key in (
                    "NEW_PATTERNS", "REFINE", "REINFORCE", "VARIANTS",
                    "REPLACE", "NEW_APS", "NEW_DRILLS", "REJECT",
                )},
                "taxonomy": {key: [] for key in ("NEW_SUBCATEGORY", "MOVE", "RENAME", "MERGE")},
                "owner_reconciliation": [],
                "metadata_classification": [],
                "approval_required": False,
            },
            "reviewed_sha256": {},
            "source_prep": None,
            "stop_reached": False,
            "stop_after": "complete",
        }
        return run

    def test_content_only_validate_uses_one_scoped_validator_process(self) -> None:
        run = self._run_stub()
        calls: list[tuple] = []
        run.tool = lambda *args: calls.append(args)
        run.validate(Path("/tmp/fake-overlay"))
        self.assertEqual(
            calls,
            [("validate.py", Path("/tmp/fake-overlay"), "--verify-references", "--package", "software-engineering")],
        )

    def test_full_validate_uses_one_full_validator_process(self) -> None:
        run = self._run_stub()
        calls: list[tuple] = []
        run.tool = lambda *args: calls.append(args)
        run.validate(Path("/tmp/fake-overlay"), full=True)
        self.assertEqual(calls, [("validate.py", Path("/tmp/fake-overlay"), "--verify-references")])

    def test_default_landing_brief_is_compact(self) -> None:
        run = self._run_stub()
        run.stage_contract = lambda: {}
        run.unit = lambda: {"unit_id": "u01", "material": "fixture"}
        run.unattended_authorization = lambda required=False: None
        compact = run.brief()
        verbose = run.brief(verbose=True)
        self.assertIn("delta_summary", compact)
        self.assertNotIn("delta", compact)
        self.assertNotIn("reviewed_sha256", compact)
        self.assertIn("delta", verbose)
        self.assertIn("reviewed_sha256", verbose)

    def test_checkpoint_blob_store_reuses_content_hash(self) -> None:
        with tempfile.TemporaryDirectory(prefix="pass-checkpoint-blob-") as td:
            root = Path(td).resolve()
            source = root / "drafts" / "x.txt"
            source.parent.mkdir(parents=True)
            source.write_text("same bytes", encoding="utf-8")
            sha = digest(source)
            run = Run.__new__(Run)
            run.root = root
            first = run.persist_checkpoint_blob(source, sha)
            first_stat = first.stat().st_mtime_ns
            second = run.persist_checkpoint_blob(source, sha)
            self.assertEqual(first, second)
            self.assertEqual(first_stat, second.stat().st_mtime_ns)
            self.assertEqual(first.read_text(encoding="utf-8"), "same bytes")

            first.write_text("corrupt", encoding="utf-8")
            with self.assertRaises(RunError):
                run.persist_checkpoint_blob(source, sha)


if __name__ == "__main__":
    unittest.main()
