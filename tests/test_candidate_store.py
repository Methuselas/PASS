"""Contracts for the re-homed candidate store and CRQ's Memory independence.

Standing regression for `canon_workflow/<domain>/card_candidates.yaml` (the
T11 handover shape, exactly as shipped) plus grep-level assertions that no CRQ
file reads the legacy Skillset Memory store. Deleting the legacy store must
never break CRQ; only Training History under the run's `history_root` matters.
"""

from __future__ import annotations

import importlib
import importlib.util
import re
import sys
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "PASS" / "runtime"
PACKAGE = RUNTIME / "candidate_qualification"
ENTRY_SCRIPT = RUNTIME / "pass_candidate_qualification.py"
WRITING_STORE = ROOT / "canon_workflow" / "writing" / "card_candidates.yaml"


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

CROCKFORD_RE = re.compile(r"\A[A-Z][A-Z0-9]*_CAND_[0-9A-HJKMNP-TV-Z]{26}\Z")


class WritingStoreTests(unittest.TestCase):
    """The shipped writing candidate store, exactly as T11 left it."""

    @classmethod
    def setUpClass(cls) -> None:
        assert WRITING_STORE.is_file(), f"candidate store missing: {WRITING_STORE}"
        cls.store = yaml.safe_load(WRITING_STORE.read_text(encoding="utf-8"))

    def test_schema_version_domain_and_candidate_count(self) -> None:
        self.assertEqual(self.store["candidate_schema_version"], 1)
        self.assertEqual(self.store["domain"], "writing")
        self.assertEqual(set(self.store), {"candidate_schema_version", "domain", "candidates"})
        self.assertEqual(len(self.store["candidates"]), 4)

    def test_every_candidate_has_exactly_the_five_store_fields(self) -> None:
        for candidate in self.store["candidates"]:
            with self.subTest(candidate=candidate.get("id")):
                self.assertEqual(
                    set(candidate),
                    {"id", "hypothesis", "evidence", "owners", "state"},
                )

    def test_candidate_ids_are_unique_valid_and_not_memory_ids(self) -> None:
        ids = [candidate["id"] for candidate in self.store["candidates"]]
        self.assertEqual(len(ids), len(set(ids)))
        for candidate_id in ids:
            with self.subTest(candidate_id=candidate_id):
                self.assertRegex(candidate_id, CROCKFORD_RE)
                self.assertNotIn("_MEM_", candidate_id)
                self.assertEqual(crq.run_id_prefix("writing", candidate_id), "WRI")

    def test_states_are_only_open_or_resolved_into_canon(self) -> None:
        states = [candidate["state"] for candidate in self.store["candidates"]]
        self.assertLessEqual(set(states), schemas.CANDIDATE_STATE_VALUES)
        self.assertIn("open", states)
        self.assertIn("resolved_into_canon", states)

    def test_hypotheses_evidence_and_owners_are_self_contained(self) -> None:
        for candidate in self.store["candidates"]:
            with self.subTest(candidate=candidate["id"]):
                hypothesis = candidate["hypothesis"]
                self.assertIsInstance(hypothesis, str)
                self.assertTrue(hypothesis.strip())
                for banned in ("_CAND_", "_MEM_", "_CRQ_", "page ", "hash:", "sha256"):
                    self.assertNotIn(banned, hypothesis)
                self.assertIsInstance(candidate["evidence"], list)
                self.assertTrue(candidate["evidence"])
                self.assertTrue(all(isinstance(item, str) and item for item in candidate["evidence"]))
                self.assertIsInstance(candidate["owners"], list)
                self.assertTrue(candidate["owners"])
                self.assertTrue(all(isinstance(item, str) and item for item in candidate["owners"]))


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
