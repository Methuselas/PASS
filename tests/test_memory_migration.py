"""R2.5 migration tooling, ticket T13: FREEZE and hash verification.

The mechanical half of the migration contract, and only that half. FREEZE
records one legacy store's exact input state — schema version, store version,
entry count, a sha256 per entry's serialized bytes, and the admissible event id
set — into a one-time workspace ledger, and refuses any store that does not
pass the existing Memory validator. `verify-hashes` (check A2) detects a store
edited after FREEZE.

What this suite must never do is migrate a domain: no proposition is
decomposed, no disposition is invented, no vNext claim is authored, no live
store or History file is written, and every live-corpus interaction here is a
read. Judgment stays with models and humans; these tests pin the mechanical
boundary around it.
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
MEMORY = ROOT / "memory"
TOOL = ROOT / "PASS/tools/migrate_memory_v3.py"


def run_migrator(
    *args: object, memory: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, str(TOOL), *map(str, args)]
    if memory is not None:
        command += ["--memory", str(memory)]
    return subprocess.run(
        command, capture_output=True, text=True, encoding="utf-8", cwd=ROOT,
    )


def valid_entry(entry_id: str, observation: str, **extra: object) -> dict:
    entry = {
        "id": entry_id,
        "scope_type": "topic",
        "scope_id": "example_topic",
        "type": "recurring_failure",
        "evidence_class": "stochastic_performance",
        "observation": observation,
        "confidence": "provisional",
        "status": "active",
    }
    entry.update(extra)
    return entry


VALID_EVENT = {
    "event_id": "TST_EV_0001",
    "date": "2026-09-01",
    "task": "Exercise the capability under review",
    "validity": "valid",
}


def entry_block_lines(text: str, entry_id: str) -> str:
    """The serialized bytes of one entry, cut by the `- id:` file convention.

    A second, independent implementation of the hash unit: the fixtures this
    runs against are dumped stores whose top-level entries begin at a
    `- id: <entry_id>` line and run to the next one or to end of file. If FREEZE
    ever hashed the whole file, a normalized re-serialization, or a slice that
    crossed entry boundaries, this cut and its digest would disagree with the
    ledger.
    """
    lines = text.splitlines(keepends=True)
    starts = [i for i, line in enumerate(lines) if line.startswith("- id: ")]
    for position, start in enumerate(starts):
        if lines[start].startswith(f"- id: {entry_id}\n") or lines[start] == f"- id: {entry_id}\n":
            end = starts[position + 1] if position + 1 < len(starts) else len(lines)
            return "".join(lines[start:end])
    raise AssertionError(f"no serialized block for {entry_id}")


class MigrationFixture(unittest.TestCase):
    """A disposable legacy store tree; nothing here touches the live corpus."""

    DOMAIN = "art"

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="pass-migrate-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.memory_root = self.tmp / "memory"
        self.domain = self.memory_root / self.DOMAIN
        self.domain.mkdir(parents=True)
        self.ledger_dir = self.tmp / "workspace" / "t13-freeze"
        self.ledger_dir.mkdir(parents=True)

    def write_store(
        self,
        entries: list[dict],
        events: list[dict] | None = None,
        *,
        schema_version: int = 1,
        memory_version: int = 3,
    ) -> None:
        (self.domain / "skill_memory.yaml").write_bytes(
            yaml.safe_dump(
                {
                    "memory_schema_version": schema_version,
                    "skillset": self.DOMAIN,
                    "memory_version": memory_version,
                    "entries": entries,
                },
                sort_keys=False,
            ).encode("utf-8")
        )
        if events is not None:
            (self.domain / "training_history.jsonl").write_bytes(
                "".join(json.dumps(event, sort_keys=True) + "\n" for event in events).encode("utf-8")
            )

    def freeze(self, ledger_dir: Path | None = None) -> subprocess.CompletedProcess[str]:
        return run_migrator(
            "freeze", "--domain", self.DOMAIN,
            "--ledger-dir", ledger_dir or self.ledger_dir,
            memory=self.memory_root,
        )

    def verify(self, ledger_dir: Path | None = None) -> subprocess.CompletedProcess[str]:
        return run_migrator(
            "verify-hashes", "--domain", self.DOMAIN,
            "--ledger-dir", ledger_dir or self.ledger_dir,
            memory=self.memory_root,
        )

    def ledger_path(self, ledger_dir: Path | None = None, domain: str | None = None) -> Path:
        return (ledger_dir or self.ledger_dir) / f"ledger-{domain or self.DOMAIN}.yaml"

    def ledger(self, ledger_dir: Path | None = None, domain: str | None = None) -> dict:
        path = self.ledger_path(ledger_dir, domain)
        return yaml.safe_load(path.read_bytes().decode("utf-8"))

    def store_text(self) -> str:
        # Bytes in, bytes out: the hash unit is the file's serialized entries,
        # and a text-mode read would silently normalize the line endings the
        # digest covers.
        return (self.domain / "skill_memory.yaml").read_bytes().decode("utf-8")

    def write_store_text(self, text: str) -> None:
        (self.domain / "skill_memory.yaml").write_bytes(text.encode("utf-8"))

    def tree_bytes(self, root: Path | None = None) -> dict[str, bytes]:
        base = root or self.memory_root
        return {
            path.relative_to(base).as_posix(): path.read_bytes()
            for path in sorted(base.rglob("*"))
            if path.is_file() and "__pycache__" not in path.parts
        }


class Freeze(MigrationFixture):
    """Step 0 records the legacy input exactly, or not at all."""

    def test_freeze_records_the_legacy_store_exactly(self) -> None:
        self.write_store(
            [
                valid_entry("ART_MEM_001", "A specific thing a run revealed."),
                valid_entry("ART_MEM_002", "A second thing, held separately."),
            ],
            [dict(VALID_EVENT)],
        )
        result = self.freeze()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        ledger = self.ledger()
        self.assertEqual(ledger["domain"], self.DOMAIN)
        legacy = ledger["legacy"]
        self.assertEqual(legacy["memory_schema_version"], 1)
        self.assertEqual(legacy["memory_version"], 3)
        self.assertEqual(legacy["entry_count"], 2)
        text = self.store_text()
        for entry_id in ("ART_MEM_001", "ART_MEM_002"):
            expected = hashlib.sha256(
                entry_block_lines(text, entry_id).encode("utf-8")
            ).hexdigest()
            self.assertEqual(legacy["entry_hashes"][entry_id], expected)
        self.assertEqual(legacy["admissible_event_ids"], ["TST_EV_0001"])

    @unittest.skipUnless(
        (MEMORY / "software-engineering" / "skill_memory.yaml").is_file(),
        "no software-engineering store in this checkout",
    )
    def test_freeze_matches_the_live_software_engineering_store(self) -> None:
        """Acceptance criterion 1: the frozen block names the live store exactly.

        The live corpus is pinned at this baseline — schema 1, memory_version
        61, 46 entries — and stays legacy until its own migration ticket. This
        is a read: the ledger lands in a temp purpose directory, and the store
        is never opened for writing.
        """
        result = run_migrator(
            "freeze", "--domain", "software-engineering",
            "--ledger-dir", self.ledger_dir, memory=MEMORY,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        legacy = self.ledger(domain="software-engineering")["legacy"]
        self.assertEqual(legacy["memory_schema_version"], 1)
        self.assertEqual(legacy["memory_version"], 61)
        self.assertEqual(legacy["entry_count"], 46)
        self.assertEqual(len(legacy["entry_hashes"]), 46)
        for digest in legacy["entry_hashes"].values():
            self.assertRegex(digest, r"^[0-9a-f]{64}$")
        verified = run_migrator(
            "verify-hashes", "--domain", "software-engineering",
            "--ledger-dir", self.ledger_dir, memory=MEMORY,
        )
        self.assertEqual(verified.returncode, 0, verified.stdout + verified.stderr)

    def test_freeze_refuses_an_invalid_legacy_store(self) -> None:
        broken = valid_entry("ART_MEM_001", "Kept.")
        del broken["observation"]
        self.write_store([broken], [dict(VALID_EVENT)])
        result = self.freeze()
        self.assertEqual(result.returncode, 1)
        self.assertIn("FAIL: freeze refused", result.stderr)
        self.assertIn("observation", result.stderr)
        self.assertFalse(self.ledger_path().exists())

    def test_freeze_refuses_a_store_already_at_schema_3(self) -> None:
        """No silent conversion: a schema-3 store is a migration output, and
        FREEZE records legacy inputs only."""
        (self.domain / "skill_memory.yaml").write_bytes(
            yaml.safe_dump(
                {
                    "memory_schema_version": 3,
                    "skillset": self.DOMAIN,
                    "memory_version": 1,
                    "claims": [],
                },
                sort_keys=False,
            ).encode("utf-8")
        )
        result = self.freeze()
        self.assertEqual(result.returncode, 1)
        self.assertIn("v1/v2 migration input", result.stderr)
        self.assertFalse(self.ledger_path().exists())

    def test_freeze_refuses_to_overwrite_an_existing_ledger(self) -> None:
        """FREEZE establishes the migration input once. A silent re-freeze
        would replace the baseline the A2 check protects."""
        self.write_store([valid_entry("ART_MEM_001", "Held.")], [dict(VALID_EVENT)])
        self.assertEqual(self.freeze().returncode, 0)
        first = self.ledger_path().read_bytes()
        second = self.freeze()
        self.assertEqual(second.returncode, 1)
        self.assertIn("already exists", second.stderr)
        self.assertEqual(self.ledger_path().read_bytes(), first)

    def test_the_ledger_lands_in_a_purpose_directory_not_the_workspace_root(self) -> None:
        """Acceptance criterion 6: never loose in workspace/."""
        self.write_store([valid_entry("ART_MEM_001", "Held.")], [dict(VALID_EVENT)])
        workspace = ROOT / "workspace"
        result = run_migrator(
            "freeze", "--domain", self.DOMAIN,
            "--ledger-dir", workspace, memory=self.memory_root,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("workspace root", result.stderr)
        self.assertFalse((workspace / f"ledger-{self.DOMAIN}.yaml").exists())

    def test_the_ledger_never_lands_inside_the_memory_tree(self) -> None:
        self.write_store([valid_entry("ART_MEM_001", "Held.")], [dict(VALID_EVENT)])
        before = self.tree_bytes()
        for landing in (self.memory_root, self.domain):
            with self.subTest(landing=landing.as_posix()):
                result = run_migrator(
                    "freeze", "--domain", self.DOMAIN,
                    "--ledger-dir", landing, memory=self.memory_root,
                )
                self.assertEqual(result.returncode, 1)
                self.assertIn("inside the memory tree", result.stderr)
        self.assertEqual(self.tree_bytes(), before)

    def test_the_frozen_ledger_is_deterministic(self) -> None:
        self.write_store(
            [
                valid_entry("ART_MEM_001", "A specific thing a run revealed."),
                valid_entry("ART_MEM_002", "A second thing, held separately."),
            ],
            [dict(VALID_EVENT)],
        )
        other = self.tmp / "workspace" / "t13-freeze-again"
        other.mkdir(parents=True)
        self.assertEqual(self.freeze().returncode, 0)
        self.assertEqual(self.freeze(other).returncode, 0)
        self.assertEqual(
            self.ledger_path().read_bytes(), self.ledger_path(other).read_bytes(),
        )


class EntryHashes(MigrationFixture):
    """A2: if a legacy entry changes after FREEZE, verification detects it."""

    def setUp(self) -> None:
        super().setUp()
        self.write_store(
            [
                valid_entry("ART_MEM_001", "The first entry's distinct observation."),
                valid_entry(
                    "ART_MEM_002", "The second entry's distinct observation.",
                    confidence="repeated",
                ),
            ],
            [dict(VALID_EVENT)],
        )
        self.assertEqual(self.freeze().returncode, 0)
        self.assertEqual(self.verify().returncode, 0)

    def edit(self, old: str, new: str) -> None:
        text = self.store_text()
        self.assertIn(old, text)
        self.write_store_text(text.replace(old, new, 1))

    def test_the_hash_is_the_sha256_of_the_entry_serialized_bytes(self) -> None:
        """The unit is the entry as serialized in the file — not the whole
        file, not a normalized re-serialization. Cut independently here by the
        `- id:` convention, so a substitution of hash unit fails this test."""
        legacy = self.ledger()["legacy"]
        text = self.store_text()
        self.assertEqual(
            legacy["entry_hashes"]["ART_MEM_001"],
            hashlib.sha256(
                entry_block_lines(text, "ART_MEM_001").encode("utf-8")
            ).hexdigest(),
        )
        self.assertEqual(
            legacy["entry_hashes"]["ART_MEM_002"],
            hashlib.sha256(
                entry_block_lines(text, "ART_MEM_002").encode("utf-8")
            ).hexdigest(),
        )
        # The two digests cover disjoint bytes: a whole-file hash could not
        # produce both, and a per-entry hash that included the file header
        # would not match either cut.
        self.assertNotEqual(
            legacy["entry_hashes"]["ART_MEM_001"],
            legacy["entry_hashes"]["ART_MEM_002"],
        )

    def test_verify_hashes_detects_an_edited_entry(self) -> None:
        self.edit("The first entry's distinct observation.", "An edited observation entirely.")
        result = self.verify()
        self.assertEqual(result.returncode, 1)
        self.assertIn("ART_MEM_001", result.stderr)
        self.assertIn("changed after FREEZE", result.stderr)
        self.assertNotIn("ART_MEM_002", result.stderr)

    def test_verify_hashes_detects_a_material_field_edit(self) -> None:
        self.edit("confidence: repeated", "confidence: strong")
        result = self.verify()
        self.assertEqual(result.returncode, 1)
        self.assertIn("ART_MEM_002", result.stderr)

    def test_verify_hashes_detects_a_removed_entry(self) -> None:
        text = self.store_text()
        self.write_store_text(text.split("- id: ART_MEM_002", 1)[0].rstrip("\n") + "\n")
        result = self.verify()
        self.assertEqual(result.returncode, 1)
        self.assertIn("ART_MEM_002", result.stderr)
        self.assertIn("absent from the store", result.stderr)

    def test_verify_hashes_detects_an_added_entry(self) -> None:
        with (self.domain / "skill_memory.yaml").open("ab") as handle:
            handle.write(
                b"- id: ART_MEM_003\n"
                b"  scope_type: topic\n"
                b"  scope_id: example_topic\n"
                b"  type: recurring_failure\n"
                b"  evidence_class: stochastic_performance\n"
                b"  observation: An entry added after the freeze.\n"
                b"  confidence: provisional\n"
                b"  status: active\n"
            )
        result = self.verify()
        self.assertEqual(result.returncode, 1)
        self.assertIn("ART_MEM_003", result.stderr)
        self.assertIn("not recorded at FREEZE", result.stderr)


class AdmissibleSet(MigrationFixture):
    """The admissible event set is valid + performance + not quarantined, and
    nothing broader."""

    def test_the_admissible_set_excludes_invalid_and_quarantined_events(self) -> None:
        events = [
            dict(VALID_EVENT),  # admissible
            {
                "event_id": "TST_EV_0002", "date": "2026-09-01",
                "task": "An attempt that never counted", "validity": "invalid",
                "invalid_reason": "contaminated",
            },  # invalid: excluded
            {
                "event_id": "TST_EV_0003", "date": "2026-09-02",
                "task": "Correct a field on an earlier event", "validity": "valid",
                "event_kind": "metadata_correction",
                "supersedes_events": ["TST_EV_0001"],
                "corrections": {"scope_id": "revised_topic"},
            },  # correction: excluded; its target stays admissible
            {
                "event_id": "TST_EV_0005", "date": "2026-09-02",
                "task": "A run later quarantined", "validity": "valid",
            },  # quarantined below: excluded
            {
                "event_id": "TST_EV_0004", "date": "2026-09-03",
                "task": "Quarantine the evidence of an earlier run",
                "validity": "valid", "event_kind": "evidence_correction",
                "supersedes_events": ["TST_EV_0005"],
                "corrections": {
                    "disposition": "quarantined",
                    "reason": "The attempt did not exercise the capability.",
                },
            },  # correction: excluded
            {
                "event_id": "TST_EV_0006", "date": "2026-09-04",
                "task": "Another admissible run", "validity": "valid",
            },  # admissible
        ]
        self.write_store([valid_entry("ART_MEM_001", "Held.")], events)
        result = self.freeze()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        admissible = self.ledger()["legacy"]["admissible_event_ids"]
        self.assertEqual(admissible, ["TST_EV_0001", "TST_EV_0006"])

    @unittest.skipUnless(
        (MEMORY / "software-engineering" / "training_history.jsonl").is_file(),
        "no software-engineering history in this checkout",
    )
    def test_the_live_software_engineering_set_excludes_invalid_and_quarantined(self) -> None:
        """Acceptance criterion 4, against the live store named in the ticket.

        The corpus is pinned at this baseline: 124 events, of which five are
        invalid and two are evidence corrections, and thirty valid performance
        events are quarantined by those corrections (three of the invalid
        events are among the quarantined, so 124 - 5 - 2 - 30 + 3 = 90 remain).
        """
        result = run_migrator(
            "freeze", "--domain", "software-engineering",
            "--ledger-dir", self.ledger_dir, memory=MEMORY,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        admissible = self.ledger(domain="software-engineering")["legacy"]["admissible_event_ids"]
        self.assertEqual(len(admissible), 90)
        self.assertEqual(admissible, sorted(admissible))
        excluded = [
            "SE_EV_0042", "SE_EV_0053", "SE_EV_0091", "SE_EV_0104", "SE_EV_0106",
            "SE_EV_0111", "SE_EV_0112",
            *[f"SE_EV_{number:04d}" for number in range(81, 111)],
        ]
        for event_id in excluded:
            self.assertNotIn(event_id, admissible)
        self.assertIn("SE_EV_0001", admissible)


class MemoryTreeFirewall(MigrationFixture):
    """Legacy stores are read-only migration inputs. The migrator writes only
    its ledger, needs no version control, and converts nothing silently."""

    @unittest.skipUnless(
        (MEMORY / "software-engineering" / "skill_memory.yaml").is_file(),
        "no live memory tree in this checkout",
    )
    def test_the_migrator_never_writes_to_the_memory_tree(self) -> None:
        """Acceptance criterion 5: a byte-identity check across all four live
        stores and both of each domain's files, through freeze and
        verify-hashes on every domain."""
        before = self.tree_bytes(MEMORY)
        stores = [name for name in before if name.endswith("skill_memory.yaml")]
        histories = [name for name in before if name.endswith("training_history.jsonl")]
        self.assertEqual(len(stores), 4, "expected four live stores")
        self.assertEqual(len(histories), 4, "expected four live histories")
        for domain in ("art", "game-design", "software-engineering", "writing"):
            with self.subTest(domain=domain):
                frozen = run_migrator(
                    "freeze", "--domain", domain,
                    "--ledger-dir", self.ledger_dir, memory=MEMORY,
                )
                self.assertEqual(frozen.returncode, 0, frozen.stdout + frozen.stderr)
                verified = run_migrator(
                    "verify-hashes", "--domain", domain,
                    "--ledger-dir", self.ledger_dir, memory=MEMORY,
                )
                self.assertEqual(verified.returncode, 0, verified.stdout + verified.stderr)
        self.assertEqual(self.tree_bytes(MEMORY), before)

    def test_the_migrator_source_names_no_memory_write_and_no_version_control(self) -> None:
        source = TOOL.read_text(encoding="utf-8")
        self.assertIsNone(
            re.search(r"(?i)\bgit\b", source),
            "the migrator names version control; migration state is carried by "
            "the store and the ledger, never by repository history",
        )
        tree = ast.parse(source)
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module)
        self.assertNotIn("subprocess", imported)
        for banned in (
            "write_memory", "append_event", "change_entries", "add_entry",
            "update_entry", "retire_claim", "link_evidence", "spliced_store",
            "store_lock",
        ):
            self.assertNotIn(banned, source, f"the migrator names {banned}")
        for runtime_module in (
            "PASS.runtime", "candidate_qualification", "memory_legacy_input",
        ):
            self.assertNotIn(runtime_module, source)


class LegacyValidatorBoundary(unittest.TestCase):
    """T13 reaches the legacy claim side only through `memory.py`'s dispatch —
    the one validation implementation — never by re-implementing a rule."""

    def test_the_migrator_imports_no_legacy_or_runtime_module(self) -> None:
        source = TOOL.read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module)
        self.assertEqual(
            imported & {"memory_legacy_input", "evidence", "controller"},
            set(),
        )
        self.assertIn("validate_store", source)


if __name__ == "__main__":
    unittest.main()
