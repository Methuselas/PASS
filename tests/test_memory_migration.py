"""R2.5 migration tooling, tickets T13-T14: FREEZE, hash verification, and the
A1-A10 accounting checker.

The mechanical half of the migration contract, and only that half. FREEZE
records one legacy store's exact input state — schema version, store version,
entry count, a sha256 per entry's serialized bytes, and the admissible event id
set — into a one-time workspace ledger, and refuses any store that does not
pass the existing Memory validator. `verify-hashes` (check A2) detects a store
edited after FREEZE. `account` (T14) validates the ledger's schema and closed
vocabularies, then checks the recorded decompositions, propositions, and
dispositions against the ten completeness rules of R2.5 §7.5, naming every
failure's check.

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


class AccountLedgerFixture(MigrationFixture):
    """A frozen two-entry legacy store plus a hand-built judgment ledger and a
    candidate v3 store. Every fixture here is disposable; the live corpus is
    never a migration input to this suite."""

    STORE_T1 = "ART_MEM_01M55WJVKRMGS6KTMQ5TSXRQDC"
    STORE_T2 = "ART_MEM_01M55WJVKRFNJW5TVAPVTVSM7T"
    STORE_T3 = "ART_MEM_01M55WJVKRTZQ3EHK6RJP8XWVY"
    FOREIGN = "GD_MEM_01M55WJVKRMGS6KTMQ5TSXRQDC"

    def setUp(self) -> None:
        super().setUp()
        self.write_store(
            [
                valid_entry(
                    "ART_MEM_001",
                    "An entry carrying two independently evaluable propositions.",
                ),
                valid_entry(
                    "ART_MEM_002",
                    "A second entry carrying one proposition.",
                    confidence="repeated",
                ),
            ],
            [dict(VALID_EVENT)],
        )
        self.assertEqual(self.freeze().returncode, 0)
        frozen = self.ledger()
        self.legacy_block = frozen["legacy"]
        self.hashes = self.legacy_block["entry_hashes"]
        self.candidate = self.tmp / "candidate" / "skill_memory.yaml"
        self.write_candidate_store([self.STORE_T1, self.STORE_T2])

    def write_candidate_store(self, claim_ids: list[str]) -> None:
        self.candidate.parent.mkdir(parents=True, exist_ok=True)
        self.candidate.write_bytes(
            yaml.safe_dump(
                {
                    "memory_schema_version": 3,
                    "skillset": self.DOMAIN,
                    "memory_version": 1,
                    "claims": [
                        {
                            "id": claim_id,
                            "claim": "A candidate claim standing in the new store.",
                        }
                        for claim_id in claim_ids
                    ],
                },
                sort_keys=False,
            ).encode("utf-8")
        )

    def base_ledger(self) -> dict:
        """A fully consistent hand-built ledger: every check passes on it."""
        return {
            "domain": self.DOMAIN,
            "legacy": self.legacy_block,
            "vnext": {"memory_schema_version": 3, "claim_count": 2},
            "decompositions": [
                {
                    "legacy_entry": "ART_MEM_001",
                    "legacy_sha256": self.hashes["ART_MEM_001"],
                    "propositions": [
                        {
                            "id": "ART_MEM_001#p1",
                            "text": "The first proposition of the first entry.",
                        },
                        {
                            "id": "ART_MEM_001#p2",
                            "text": "The second proposition of the first entry.",
                        },
                    ],
                },
                {
                    "legacy_entry": "ART_MEM_002",
                    "legacy_sha256": self.hashes["ART_MEM_002"],
                    "propositions": [
                        {
                            "id": "ART_MEM_002#p1",
                            "text": "The single proposition of the second entry.",
                        },
                    ],
                },
            ],
            "dispositions": [
                {
                    "proposition": "ART_MEM_001#p1",
                    "class": "CARRY",
                    "targets": [self.STORE_T1],
                },
                {
                    "proposition": "ART_MEM_001#p2",
                    "class": "REWRITE",
                    "targets": [self.STORE_T2],
                    "rewrite_reason": "voice",
                },
                {
                    "proposition": "ART_MEM_002#p1",
                    "class": "REJECT",
                    "reason_kind": "fails_canon_only_baseline",
                    "reason": "The claim fails the Canon-only baseline.",
                },
            ],
            "holds": [],
        }

    def account(
        self, ledger: dict, store_claim_ids: list[str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        if store_claim_ids is not None:
            self.write_candidate_store(store_claim_ids)
        self.ledger_path().write_bytes(
            yaml.safe_dump(ledger, sort_keys=False).encode("utf-8")
        )
        return run_migrator(
            "account", "--domain", self.DOMAIN,
            "--ledger-dir", self.ledger_dir,
            "--store", self.candidate,
            memory=self.memory_root,
        )

    def output(self, result: subprocess.CompletedProcess[str]) -> str:
        return result.stdout + result.stderr


class Accounting(AccountLedgerFixture):
    """T14: one test per completeness check, each fixture breaking exactly it."""

    def test_a_hand_built_ledger_passes_all_ten_checks(self) -> None:
        """Acceptance criterion 1: the baseline ledger holds, and A9 is
        honestly reported as delegated rather than silently skipped."""
        result = self.account(self.base_ledger())
        self.assertEqual(result.returncode, 0, self.output(result))
        for check in ("A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A10"):
            self.assertIn(f"{check}: PASS", result.stdout)
        self.assertIn("A9: delegated", result.stdout)
        self.assertIn("PASS: account", result.stdout)

    def test_a1_fails_on_a_missing_or_duplicate_decomposition(self) -> None:
        ledger = self.base_ledger()
        # One mutation covering both directions: ART_MEM_002's decomposition
        # is replaced by a second decomposition of ART_MEM_001, so the entry
        # count still matches A8 while A1 alone reports the duplicate and the
        # omission. The duplicate carries a fresh proposition id (with its own
        # disposition) so the ledger stays schema-valid, A3 stays green, and
        # every failure here is A1's.
        ledger["decompositions"][1] = {
            "legacy_entry": "ART_MEM_001",
            "legacy_sha256": self.hashes["ART_MEM_001"],
            "propositions": [
                {
                    "id": "ART_MEM_001#p3",
                    "text": "A proposition recorded under the wrong entry.",
                },
            ],
        }
        ledger["dispositions"] = ledger["dispositions"][:2] + [
            {
                "proposition": "ART_MEM_001#p3",
                "class": "REJECT",
                "reason_kind": "not_portable",
                "reason": "Not portable across instances.",
            }
        ]
        result = self.account(ledger)
        self.assertEqual(result.returncode, 1)
        self.assertIn("A1: FAIL", result.stdout)
        self.assertIn("appears in 2 decompositions", self.output(result))
        self.assertIn("ART_MEM_002", self.output(result))
        self.assertIn("no decomposition", self.output(result))
        self.assertIn("A8: PASS", result.stdout)
        for check in ("A3", "A4", "A5", "A6", "A7", "A10"):
            self.assertIn(f"{check}: PASS", result.stdout)

    def test_a3_fails_when_a_proposition_loses_its_disposition(self) -> None:
        ledger = self.base_ledger()
        del ledger["dispositions"][1]  # ART_MEM_001#p2 left undispositioned
        ledger["vnext"]["claim_count"] = 1
        result = self.account(ledger, store_claim_ids=[self.STORE_T1])
        self.assertEqual(result.returncode, 1)
        self.assertIn("A3: FAIL", result.stdout)
        self.assertIn("ART_MEM_001#p2", self.output(result))
        self.assertIn("has no disposition", self.output(result))
        for check in ("A1", "A2", "A4", "A5", "A6", "A7", "A8", "A10"):
            self.assertIn(f"{check}: PASS", result.stdout)

    def test_a_proposition_deleted_from_the_ledger_fails_a3(self) -> None:
        """Acceptance criterion 47: a proposition deleted between passes
        leaves its disposition pointing at nothing, and A3 says so."""
        ledger = self.base_ledger()
        del ledger["decompositions"][0]["propositions"][1]  # ART_MEM_001#p2
        result = self.account(ledger)
        self.assertEqual(result.returncode, 1)
        self.assertIn("A3: FAIL", result.stdout)
        self.assertIn("ART_MEM_001#p2", self.output(result))
        self.assertIn("absent from this ledger's decompositions", self.output(result))
        for check in ("A1", "A2", "A4", "A5", "A6", "A7", "A8", "A10"):
            self.assertIn(f"{check}: PASS", result.stdout)

    def test_a4_fails_when_a_disposition_lacks_its_obligation(self) -> None:
        ledger = self.base_ledger()
        ledger["dispositions"][1] = {
            "proposition": "ART_MEM_001#p2",
            "class": "SPLIT",
            "targets": [self.STORE_T2],
        }
        result = self.account(ledger)
        self.assertEqual(result.returncode, 1)
        self.assertIn("A4: FAIL", result.stdout)
        self.assertIn("SPLIT requires at least 2 target claim ids", self.output(result))
        for check in ("A1", "A2", "A3", "A5", "A6", "A7", "A8", "A10"):
            self.assertIn(f"{check}: PASS", result.stdout)

    def test_a4_fails_when_a_rewrite_has_no_reason(self) -> None:
        ledger = self.base_ledger()
        del ledger["dispositions"][1]["rewrite_reason"]
        result = self.account(ledger)
        self.assertEqual(result.returncode, 1)
        self.assertIn("A4: FAIL", result.stdout)
        self.assertIn("REWRITE requires a rewrite_reason", self.output(result))
        self.assertIn("A3: PASS", result.stdout)

    def test_a5_fails_when_a_target_is_absent_from_the_store(self) -> None:
        ledger = self.base_ledger()
        ledger["vnext"]["claim_count"] = 1
        result = self.account(ledger, store_claim_ids=[self.STORE_T1])
        self.assertEqual(result.returncode, 1)
        self.assertIn("A5: FAIL", result.stdout)
        self.assertIn(self.STORE_T2, self.output(result))
        self.assertIn("does not exist in the candidate store", self.output(result))
        for check in ("A1", "A2", "A3", "A4", "A6", "A7", "A8", "A10"):
            self.assertIn(f"{check}: PASS", result.stdout)

    def test_a6_fails_when_a_claim_is_named_by_no_disposition(self) -> None:
        """Acceptance criterion 7: a claim injected into the new store without
        a source proposition fails the gate."""
        ledger = self.base_ledger()
        ledger["vnext"]["claim_count"] = 3
        result = self.account(
            ledger, store_claim_ids=[self.STORE_T1, self.STORE_T2, self.STORE_T3],
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("A6: FAIL", result.stdout)
        self.assertIn(self.STORE_T3, self.output(result))
        self.assertIn("named by no disposition", self.output(result))
        for check in ("A1", "A2", "A3", "A4", "A5", "A7", "A8", "A10"):
            self.assertIn(f"{check}: PASS", result.stdout)

    def test_a7_fails_while_a_hold_remains(self) -> None:
        ledger = self.base_ledger()
        ledger["holds"] = [
            {
                "question": "Does the specimen claim survive as its own proposition?",
                "must_answer": "the domain owner",
            }
        ]
        result = self.account(ledger)
        self.assertEqual(result.returncode, 1)
        self.assertIn("A7: FAIL", result.stdout)
        self.assertIn("1 hold(s) remain", self.output(result))
        for check in ("A1", "A2", "A3", "A4", "A5", "A6", "A8", "A10"):
            self.assertIn(f"{check}: PASS", result.stdout)

    def test_a7_fails_while_a_disposition_is_still_hold(self) -> None:
        ledger = self.base_ledger()
        ledger["dispositions"][1] = {
            "proposition": "ART_MEM_001#p2",
            "class": "HOLD",
            "question": "Is this proposition portable?",
            "must_answer": "the migration reviewer",
        }
        ledger["vnext"]["claim_count"] = 1
        result = self.account(ledger, store_claim_ids=[self.STORE_T1])
        self.assertEqual(result.returncode, 1)
        self.assertIn("A7: FAIL", result.stdout)
        self.assertIn("still HOLD", self.output(result))
        for check in ("A1", "A2", "A3", "A4", "A5", "A6", "A8", "A10"):
            self.assertIn(f"{check}: PASS", result.stdout)

    def test_a8_reports_the_counts_and_fails_on_a_claim_count_mismatch(self) -> None:
        ledger = self.base_ledger()
        ledger["vnext"]["claim_count"] = 5
        result = self.account(ledger)
        self.assertEqual(result.returncode, 1)
        self.assertIn("A8: FAIL", result.stdout)
        self.assertIn("vnext.claim_count 5 disagrees with 2", self.output(result))
        for check in ("A1", "A2", "A3", "A4", "A5", "A6", "A7", "A10"):
            self.assertIn(f"{check}: PASS", result.stdout)

    def test_a_merge_passes_accounting_and_a8_states_the_difference(self) -> None:
        """Acceptance criterion 6: three propositions collapsing into one
        shared target passes A3, A5, A6, and A8, and A8 states the difference
        rather than asserting equality. That it passes at all is the proof
        that no check compares the shared target against its source ids —
        the id encodes no lineage, and none is inferred (§7.3, §7.5)."""
        ledger = self.base_ledger()
        ledger["vnext"] = {"memory_schema_version": 3, "claim_count": 1}
        ledger["decompositions"] = [
            {
                "legacy_entry": "ART_MEM_001",
                "legacy_sha256": self.hashes["ART_MEM_001"],
                "propositions": [
                    {"id": "ART_MEM_001#p1", "text": "First merged proposition."},
                    {"id": "ART_MEM_001#p2", "text": "Second merged proposition."},
                    {"id": "ART_MEM_001#p3", "text": "Third merged proposition."},
                ],
            },
            {
                "legacy_entry": "ART_MEM_002",
                "legacy_sha256": self.hashes["ART_MEM_002"],
                "propositions": [
                    {"id": "ART_MEM_002#p1", "text": "The other entry's claim."},
                ],
            },
        ]
        ledger["dispositions"] = [
            {
                "proposition": "ART_MEM_001#p1",
                "class": "CARRY",
                "targets": [self.STORE_T1],
            },
            {
                "proposition": "ART_MEM_001#p2",
                "class": "REWRITE",
                "targets": [self.STORE_T1],
                "rewrite_reason": "voice",
            },
            {
                "proposition": "ART_MEM_001#p3",
                "class": "CARRY",
                "targets": [self.STORE_T1],
            },
            {
                "proposition": "ART_MEM_002#p1",
                "class": "REJECT",
                "reason_kind": "fails_canon_only_baseline",
                "reason": "The claim fails the Canon-only baseline.",
            },
        ]
        result = self.account(ledger, store_claim_ids=[self.STORE_T1])
        self.assertEqual(result.returncode, 0, self.output(result))
        for check in ("A3", "A5", "A6", "A8"):
            self.assertIn(f"{check}: PASS", result.stdout)
        self.assertIn(
            "3 surviving disposition(s) naming 1 distinct target claim(s)",
            result.stdout,
        )
        self.assertIn("1 target(s) shared across dispositions (merge)", result.stdout)

    def test_a10_rejects_a_carried_legacy_id(self) -> None:
        """Acceptance criterion 4: a one-to-one CARRY that kept its legacy id
        fails A10. The id is placed in the candidate store so the failure is
        exactly A10's — the shape rule fires before the legacy-equality rule."""
        ledger = self.base_ledger()
        ledger["dispositions"][0]["targets"] = ["ART_MEM_001"]
        result = self.account(
            ledger, store_claim_ids=["ART_MEM_001", self.STORE_T2],
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("A10: FAIL", result.stdout)
        self.assertIn("legacy sequence number is not a claim id", self.output(result))
        self.assertIn("equals a legacy entry id", self.output(result))
        for check in ("A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8"):
            self.assertIn(f"{check}: PASS", result.stdout)

    def test_a10_rejects_a_foreign_domain_token(self) -> None:
        """Acceptance criterion 5: a target carrying another domain's token
        fails A10 even though the shape itself is well formed."""
        ledger = self.base_ledger()
        ledger["dispositions"][0]["targets"] = [self.FOREIGN]
        result = self.account(ledger, store_claim_ids=[self.FOREIGN, self.STORE_T2])
        self.assertEqual(result.returncode, 1)
        self.assertIn("A10: FAIL", result.stdout)
        self.assertIn("does not carry this store's domain token 'ART'", self.output(result))
        for check in ("A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8"):
            self.assertIn(f"{check}: PASS", result.stdout)

    def test_the_account_command_writes_nothing(self) -> None:
        """Account is a read-only checker: the ledger is written by this test,
        the candidate store by this test, and the legacy tree is untouched."""
        self.ledger_path().write_bytes(
            yaml.safe_dump(self.base_ledger(), sort_keys=False).encode("utf-8")
        )
        before = self.tree_bytes()
        ledger_bytes = self.ledger_path().read_bytes()
        candidate_bytes = self.candidate.read_bytes()
        result = run_migrator(
            "account", "--domain", self.DOMAIN,
            "--ledger-dir", self.ledger_dir,
            "--store", self.candidate,
            memory=self.memory_root,
        )
        self.assertEqual(result.returncode, 0, self.output(result))
        self.assertEqual(self.tree_bytes(), before)
        self.assertEqual(self.ledger_path().read_bytes(), ledger_bytes)
        self.assertEqual(self.candidate.read_bytes(), candidate_bytes)


class LedgerSchema(AccountLedgerFixture):
    """The ledger schema validator: closed vocabularies, required blocks, and
    proposition identity format, fail-closed before any accounting runs."""

    def assert_schema_refusal(self, ledger: dict, *expected: str) -> None:
        result = self.account(ledger)
        self.assertEqual(result.returncode, 1, self.output(result))
        self.assertIn("ledger schema:", result.stderr)
        self.assertIn("checks do not run", result.stdout)
        for fragment in expected:
            self.assertIn(fragment, result.stderr)

    def test_an_unknown_top_level_key_is_rejected(self) -> None:
        ledger = self.base_ledger()
        ledger["signoffs"] = []
        self.assert_schema_refusal(ledger, "unknown key 'signoffs'")

    def test_an_unknown_disposition_class_is_rejected(self) -> None:
        ledger = self.base_ledger()
        ledger["dispositions"][0]["class"] = "MERGE"
        self.assert_schema_refusal(ledger, "closed disposition class vocabulary")

    def test_every_closed_vocabulary_rejects_a_non_member(self) -> None:
        cases = [
            ({"rewrite_reason": "because"}, "rewrite_reason"),
            ({"reason_kind": "bogus"}, "reason_kind"),
        ]
        for patch, field in cases:
            with self.subTest(field=field):
                ledger = self.base_ledger()
                ledger["dispositions"][1].update(patch)
                self.assert_schema_refusal(ledger, field)
        ledger = self.base_ledger()
        ledger["dispositions"].append(
            {
                "proposition": "ART_MEM_002#p1",
                "class": "REHOME",
                "destination": "the_crdt_ledger",
                "pointer": "A pointer to the destination.",
            }
        )
        # The duplicate disposition for ART_MEM_002#p1 would also break A3,
        # but schema refuses first: the destination vocabulary is closed.
        self.assert_schema_refusal(ledger, "destination")

    def test_a_malformed_proposition_id_is_rejected(self) -> None:
        for bad_id in ("ART_MEM_001#p0", "OTHER_MEM_001#p1", "ART_MEM_001#p1x"):
            with self.subTest(proposition_id=bad_id):
                ledger = self.base_ledger()
                ledger["decompositions"][0]["propositions"][0]["id"] = bad_id
                self.assert_schema_refusal(ledger, "is not shaped")

    def test_the_vnext_block_must_declare_schema_3(self) -> None:
        ledger = self.base_ledger()
        ledger["vnext"]["memory_schema_version"] = 2
        self.assert_schema_refusal(ledger, "memory_schema_version must be 3")

    def test_a_class_inappropriate_key_is_rejected(self) -> None:
        ledger = self.base_ledger()
        ledger["dispositions"][0]["rewrite_reason"] = "voice"
        self.assert_schema_refusal(ledger, "unknown key 'rewrite_reason'")

    def test_a_hold_without_its_question_is_rejected(self) -> None:
        ledger = self.base_ledger()
        ledger["holds"] = [{"question": "An open question."}]
        self.assert_schema_refusal(ledger, "required key 'must_answer' is missing")

    def test_the_schema_validator_accepts_the_whole_closed_class_set(self) -> None:
        """Every member of every closed vocabulary is accepted, not just the
        members the baseline fixture happens to use."""
        ledger = self.base_ledger()
        ledger["vnext"] = {"memory_schema_version": 3, "claim_count": 3}
        ledger["decompositions"] = ledger["decompositions"][:1] + [
            {
                "legacy_entry": "ART_MEM_002",
                "legacy_sha256": self.hashes["ART_MEM_002"],
                "propositions": [
                    {"id": "ART_MEM_002#p1", "text": "One."},
                    {"id": "ART_MEM_002#p2", "text": "Two."},
                    {"id": "ART_MEM_002#p3", "text": "Three."},
                    {"id": "ART_MEM_002#p4", "text": "Four."},
                    {"id": "ART_MEM_002#p5", "text": "Five."},
                    {"id": "ART_MEM_002#p6", "text": "Six."},
                    {"id": "ART_MEM_002#p7", "text": "Seven."},
                ],
            }
        ]
        ledger["dispositions"] = [
            {
                "proposition": "ART_MEM_001#p1",
                "class": "CARRY",
                "targets": [self.STORE_T1],
            },
            {
                "proposition": "ART_MEM_001#p2",
                "class": "SPLIT",
                "targets": [self.STORE_T2, self.STORE_T3],
            },
            {
                "proposition": "ART_MEM_002#p1",
                "class": "CONDENSE",
                "targets": [self.STORE_T1],
                "shed": [
                    {
                        "proposition": "ART_MEM_002#p2",
                        "shed_reason": "Restates the surviving claim.",
                    }
                ],
            },
            {
                "proposition": "ART_MEM_002#p3",
                "class": "EXTRACT",
                "targets": [self.STORE_T1],
                "destination": "training_history",
            },
            {
                "proposition": "ART_MEM_002#p4",
                "class": "REHOME",
                "destination": "canon_workflow",
                "hand_off": "Handed to the candidate store; acceptance owed.",
            },
            {
                "proposition": "ART_MEM_002#p5",
                "class": "REJECT",
                "reason_kind": "duplicate_of",
                "reason": "Duplicates the surviving claim.",
                "duplicate_of": self.STORE_T1,
            },
            {
                "proposition": "ART_MEM_002#p6",
                "class": "HOLD",
                "question": "Does this proposition survive?",
                "must_answer": "the domain owner",
            },
            {
                "proposition": "ART_MEM_002#p7",
                "class": "REJECT",
                "reason_kind": "belongs_to_regression",
                "reason": "The content belongs to the regression authority.",
            },
        ]
        result = self.account(
            ledger, store_claim_ids=[self.STORE_T1, self.STORE_T2, self.STORE_T3],
        )
        # Schema accepts every class; the run then fails on A7 for the HOLD,
        # which is the completion gate's own refusal, not a schema one.
        self.assertNotIn("ledger schema:", result.stderr)
        self.assertIn("A7: FAIL", result.stdout)
        for check in ("A1", "A2", "A3", "A4", "A5", "A6", "A8", "A10"):
            self.assertIn(f"{check}: PASS", result.stdout)


if __name__ == "__main__":
    unittest.main()
