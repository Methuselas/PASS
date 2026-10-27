"""Contracts for CRQ's Memory independence.

The legacy `canon_workflow/<domain>/card_candidates.yaml` store was deleted in
7426471; only Training History under the run's `history_root` matters. Deleting
the legacy store must never break CRQ. This module keeps the grep-level
assertions that no CRQ file reads the legacy Skillset Memory store.
"""

from __future__ import annotations

import importlib
import importlib.util
import re
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "PASS" / "runtime"
PACKAGE = RUNTIME / "candidate_qualification"
ENTRY_SCRIPT = RUNTIME / "pass_candidate_qualification.py"


def load_package(runtime: Path, name: str = "candidate_qualification"):
    """Load the CRQ package found in `runtime` under `name`; return its controller."""
    if name not in sys.modules:
        package_dir = runtime / "candidate_qualification"
        spec = importlib.util.spec_from_file_location(
            name, package_dir / "__init__.py", submodule_search_locations=[str(package_dir)]
        )
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return importlib.import_module(f"{name}.controller")


crq = load_package(RUNTIME)
schemas = importlib.import_module("candidate_qualification.schemas")


class CrqIndependenceTests(unittest.TestCase):
    """No CRQ file may read the legacy Skillset Memory store or its vocabulary."""

    def sources(self) -> dict[Path, str]:
        files = [
            path
            for path in PACKAGE.rglob("*.py")
            if "__pycache__" not in path.parts
        ] + [ENTRY_SCRIPT]
        return {path: path.read_text(encoding="utf-8") for path in files}

    def test_no_crq_file_reads_the_legacy_memory_store(self) -> None:
        forbidden = (
            "skill_memory.yaml",
            "validate_store",
            "find_entry",
            "load_memory",
            "MemoryError_",
            "memory_entry_id",
            "memory_root",
            "MEMORY_ACTIONS",
            "resolve_memory_candidate",
            "_MEM_[0-9]",
            "memory_action",
        )
        for path, text in self.sources().items():
            for token in forbidden:
                with self.subTest(file=path.name, token=token):
                    self.assertNotIn(token, text)

    def test_no_crq_file_treats_card_candidate_as_a_memory_type(self) -> None:
        pattern = re.compile(r"['\"]card_candidate['\"]")
        for path, text in self.sources().items():
            with self.subTest(file=path.name):
                self.assertIsNone(pattern.search(text))

    def test_no_crq_file_may_mention_legacy_status_vocabulary(self) -> None:
        for path, text in self.sources().items():
            for token in ("keep-active", "keep-monitoring", "supersede-candidate",
                          "resolve-after-canon-fix", "narrow-boundary"):
                with self.subTest(file=path.name, token=token):
                    self.assertNotIn(token, text)

    def test_crq_owns_its_failure_layer_vocabulary(self) -> None:
        self.assertEqual(schemas.FAILURE_LAYERS, {
            "knowledge", "orchestration", "retrieval", "application", "continuity",
            "reference", "tool", "interface", "training",
        })
        self.assertIs(crq.FAILURE_LAYERS, schemas.FAILURE_LAYERS)


if __name__ == "__main__":
    unittest.main()
