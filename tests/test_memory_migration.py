"""R2.5 migration tooling, tickets T13-T15: FREEZE, hash verification, the
sentence inventory, and the A1-A10 accounting checker.

The mechanical half of the migration contract, and only that half. FREEZE
records one legacy store's exact input state — schema version, store version,
entry count, a sha256 per entry's serialized bytes, and the admissible event id
set — into a one-time workspace ledger, and refuses any store that does not
pass the existing Memory validator. `verify-hashes` (check A2) detects a store
edited after FREEZE. `sentences` (T15) emits the numbered sentence inventory A9
runs against: the three jointly-read fields concatenated in the ticket's order
and split with `validate.py`'s SENTENCE_RE, the repository's one splitter.
`account` (T14-T15) validates the ledger's schema and closed vocabularies,
then checks the recorded decompositions, propositions, dispositions, and
sentence maps against the ten completeness rules of R2.5 §7.5, naming every
failure's check — A9 proving sentence coverage and the second-reader mark, not
the truth of any attribution.

What this suite must never do is migrate a domain: no proposition is
decomposed, no disposition is invented, no sentence is attributed by the tool
under test, no vNext claim is authored, no live store or History file is
written, and every live-corpus interaction here is a read. Judgment stays with
models and humans; these tests pin the mechanical boundary around it.
"""

from __future__ import annotations

import ast
import hashlib
import json
import os
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
TOOLS = ROOT / "PASS/tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from validate import SENTENCE_RE  # noqa: E402  the splitter under test, imported


def run_migrator(
    *args: object, memory: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, str(TOOL), *map(str, args)]
    if memory is not None:
        command += ["--memory", str(memory)]
    # The migrator's own output must survive the trip: a legacy store may
    # carry non-ASCII bytes (a quoted name, a smart apostrophe), and a child
    # Python writing to a pipe in the console's codepage would emit them
    # un-decodable. Same contract as build_release's subprocess calls.
    return subprocess.run(
        command, capture_output=True, text=True, encoding="utf-8", cwd=ROOT,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
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


def reference_inventory(store_path: Path, entry_id: str) -> list[str]:
    """The sentence inventory recomputed from store bytes with SENTENCE_RE.

    An independent second implementation of the rule under test: read the
    entry, concatenate `observation`, `boundary`, and `diagnosis.hypothesis`
    in that order (§7.4 step 1 — one text, no per-field slicing), split with
    the repository's one imported splitter, strip, drop empties. The migrator
    derives its inventory through its own code path; if the two ever disagree,
    the emitted sequence comparison in the T15 tests fails.
    """
    store = yaml.safe_load(store_path.read_bytes().decode("utf-8"))
    entry = next(item for item in store["entries"] if item.get("id") == entry_id)
    parts: list[str] = []
    for value in (entry.get("observation"), entry.get("boundary")):
        if isinstance(value, str) and value:
            parts.append(value)
    diagnosis = entry.get("diagnosis")
    if isinstance(diagnosis, dict):
        hypothesis = diagnosis.get("hypothesis")
        if isinstance(hypothesis, str) and hypothesis:
            parts.append(hypothesis)
    return [
        segment.strip()
        for segment in SENTENCE_RE.split("\n".join(parts))
        if segment.strip()
    ]


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
        stores and both of each domain's files, through freeze,
        verify-hashes, and the sentence inventory (T15) on every domain."""
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
                store = yaml.safe_load(
                    (MEMORY / domain / "skill_memory.yaml").read_bytes()
                )
                first_entry = store["entries"][0]["id"]
                emitted = run_migrator(
                    "sentences", "--domain", domain, "--entry", first_entry,
                    memory=MEMORY,
                )
                self.assertEqual(emitted.returncode, 0, emitted.stdout + emitted.stderr)
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
        # ART_MEM_001 deliberately reads across all three jointly-read fields
        # (two observation sentences, one boundary, one hypothesis), so the
        # fixture's sentence inventory has provenance-free numbering 1..4 in
        # the ticket's order: observation, boundary, diagnosis.hypothesis.
        self.write_store(
            [
                valid_entry(
                    "ART_MEM_001",
                    "An entry carrying two independently evaluable propositions. "
                    "Its second sentence carries the second proposition.",
                    boundary="A boundary sentence naming where the entry holds.",
                    diagnosis={"hypothesis": "A hypothesis sentence naming the cause."},
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
        """A fully consistent hand-built ledger: every check passes on it.

        The sentence maps are complete for the fixture's four-sentence and
        one-sentence inventories, one record per source sentence, each
        attributed to exactly one mode. `accretion_entries` is empty: no
        fixture entry is declared an accretion narrative unless a test says
        so.
        """
        return {
            "domain": self.DOMAIN,
            "legacy": self.legacy_block,
            "vnext": {"memory_schema_version": 3, "claim_count": 2},
            "accretion_entries": [],
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
                    "sentence_map": [
                        {"sentence": 1, "propositions": ["ART_MEM_001#p1"]},
                        {"sentence": 2, "propositions": ["ART_MEM_001#p2"]},
                        {"sentence": 3, "non_propositional": "environment_context"},
                        {"sentence": 4, "non_propositional": "restatement"},
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
                    "sentence_map": [
                        {"sentence": 1, "propositions": ["ART_MEM_002#p1"]},
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

    def assert_schema_refusal(self, ledger: dict, *expected: str) -> None:
        result = self.account(ledger)
        self.assertEqual(result.returncode, 1, self.output(result))
        self.assertIn("ledger schema:", result.stderr)
        self.assertIn("checks do not run", result.stdout)
        for fragment in expected:
            self.assertIn(fragment, result.stderr)

    def sentences(
        self, entry_id: str, domain: str | None = None,
    ) -> subprocess.CompletedProcess[str]:
        return run_migrator(
            "sentences", "--domain", domain or self.DOMAIN, "--entry", entry_id,
            memory=self.memory_root,
        )

    @staticmethod
    def sentence_lines(stdout: str) -> list[str]:
        """The emitted inventory with its `N: ` prefixes stripped.

        Numbered lines are reassembled by prefix rather than by line, so a
        segment that legitimately spans a newline survives the parse intact.
        """
        sentences: dict[int, str] = {}
        current: int | None = None
        for line in stdout.splitlines():
            match = re.match(r"^(\d+): (.*)$", line)
            if match:
                current = int(match.group(1))
                sentences[current] = match.group(2)
            elif current is not None:
                sentences[current] += "\n" + line
        return [sentences[number] for number in sorted(sentences)]


class Accounting(AccountLedgerFixture):
    """T14: one test per completeness check A1-A8 and A10, each fixture
    breaking exactly its own; the baseline ledger then proves all ten, A9
    included. A9's dedicated failure fixtures live under SentenceCoverage."""

    def test_a_hand_built_ledger_passes_all_ten_checks(self) -> None:
        """Acceptance criterion 1 (T14) and criterion 2 (T15): the baseline
        ledger holds, and A9 reports real sentence coverage rather than a
        delegation stub."""
        result = self.account(self.base_ledger())
        self.assertEqual(result.returncode, 0, self.output(result))
        for check in ("A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10"):
            self.assertIn(f"{check}: PASS", result.stdout)
        self.assertIn("5 sentence(s) in 2 entr(ies) each accounted exactly once", result.stdout)
        self.assertIn("0 accretion entr(ies) declared", result.stdout)
        self.assertIn("PASS: account", result.stdout)

    def test_a1_fails_on_a_missing_or_duplicate_decomposition(self) -> None:
        ledger = self.base_ledger()
        # One mutation covering both directions: ART_MEM_002's decomposition
        # is replaced by a second decomposition of ART_MEM_001, so the entry
        # count still matches A8 while A1 alone reports the duplicate and the
        # omission. The duplicate carries a fresh proposition id (with its own
        # disposition) and a complete sentence map, so the ledger stays
        # schema-valid, A3 stays green, and A1 owns the duplicate; A9 mirrors
        # only the unmapped entry's unaccounted sentence.
        ledger["decompositions"][1] = {
            "legacy_entry": "ART_MEM_001",
            "legacy_sha256": self.hashes["ART_MEM_001"],
            "propositions": [
                {
                    "id": "ART_MEM_001#p3",
                    "text": "A proposition recorded under the wrong entry.",
                },
            ],
            # A complete map for the same four source sentences, so A9 stays
            # green and every failure here remains A1's.
            "sentence_map": [
                {"sentence": number, "propositions": ["ART_MEM_001#p3"]}
                for number in (1, 2, 3, 4)
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
        # A9 reports the same omission from its own side — the unmapped
        # entry's sentence is unaccounted — and every other check stays green.
        self.assertIn("A9: FAIL", result.stdout)
        self.assertIn(
            "legacy entry 'ART_MEM_002' has no decomposition carrying a "
            "sentence map",
            self.output(result),
        )
        for check in ("A3", "A4", "A5", "A6", "A7", "A8", "A10"):
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
                "sentence_map": [
                    {"sentence": 1, "propositions": ["ART_MEM_001#p1"]},
                    {"sentence": 2, "propositions": ["ART_MEM_001#p2"]},
                    {"sentence": 3, "propositions": ["ART_MEM_001#p3"]},
                    {"sentence": 4, "non_propositional": "restatement"},
                ],
            },
            {
                "legacy_entry": "ART_MEM_002",
                "legacy_sha256": self.hashes["ART_MEM_002"],
                "propositions": [
                    {"id": "ART_MEM_002#p1", "text": "The other entry's claim."},
                ],
                "sentence_map": [
                    {"sentence": 1, "propositions": ["ART_MEM_002#p1"]},
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
    """The ledger schema validator: closed vocabularies, required blocks,
    sentence-map row shape, and proposition identity format, fail-closed
    before any accounting runs."""

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

    def test_a_decomposition_requires_a_sentence_map(self) -> None:
        ledger = self.base_ledger()
        del ledger["decompositions"][0]["sentence_map"]
        self.assert_schema_refusal(ledger, "sentence_map must be a list")

    def test_an_unknown_sentence_map_row_key_is_rejected(self) -> None:
        ledger = self.base_ledger()
        ledger["decompositions"][0]["sentence_map"][0]["field"] = "observation"
        self.assert_schema_refusal(ledger, "unknown key 'field'")

    def test_a_sentence_map_row_cannot_carry_both_modes(self) -> None:
        ledger = self.base_ledger()
        row = ledger["decompositions"][0]["sentence_map"][0]
        row["non_propositional"] = "restatement"
        self.assert_schema_refusal(
            ledger, "carries both propositions and non_propositional"
        )

    def test_a_sentence_map_row_cannot_carry_neither_mode(self) -> None:
        ledger = self.base_ledger()
        del ledger["decompositions"][0]["sentence_map"][0]["propositions"]
        self.assert_schema_refusal(
            ledger, "carries neither propositions nor non_propositional"
        )

    def test_a_sentence_map_reference_list_is_non_empty_and_unique(self) -> None:
        empty = self.base_ledger()
        empty["decompositions"][0]["sentence_map"][0]["propositions"] = []
        self.assert_schema_refusal(empty, "propositions must be a non-empty list")
        repeated = self.base_ledger()
        repeated["decompositions"][0]["sentence_map"][0]["propositions"] = [
            "ART_MEM_001#p1",
            "ART_MEM_001#p1",
        ]
        self.assert_schema_refusal(repeated, "repeats an id")

    def test_a_sentence_number_must_be_a_positive_integer(self) -> None:
        for bad in (0, -1, "1", True, 1.5):
            with self.subTest(sentence=bad):
                ledger = self.base_ledger()
                ledger["decompositions"][0]["sentence_map"][0]["sentence"] = bad
                self.assert_schema_refusal(ledger, "positive integer")

    def test_second_reader_must_be_the_literal_mark(self) -> None:
        ledger = self.base_ledger()
        ledger["decompositions"][0]["second_reader"] = "yes"
        self.assert_schema_refusal(ledger, "second_reader must be `true`")

    def test_accretion_entries_shape_is_checked(self) -> None:
        not_a_list = self.base_ledger()
        not_a_list["accretion_entries"] = "ART_MEM_001"
        self.assert_schema_refusal(not_a_list, "accretion_entries must be a list")
        duplicated = self.base_ledger()
        duplicated["accretion_entries"] = ["ART_MEM_001", "ART_MEM_001"]
        self.assert_schema_refusal(duplicated, "more than once")

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
                "sentence_map": [
                    {"sentence": 1, "propositions": ["ART_MEM_002#p1"]},
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


class SentenceCoverage(AccountLedgerFixture):
    """T15: the sentence inventory, A9's under-decomposition check, and the
    second-reader mark. Coverage and presence only — the checker never reads
    what a sentence means, so an accepted attribution can still be wrong;
    that is the point (R2.5 §7.2, §7.5)."""

    def test_segmentation_is_stable_and_matches_the_frozen_bytes(self) -> None:
        """Acceptance criteria 1 and 2: two emissions are byte-identical, the
        header count equals the numbered lines, and the emitted sequence
        equals an independent recompute of the frozen entry's fields through
        the imported SENTENCE_RE.

        The sequence comparison also pins the §7.4 step-1 order — observation,
        boundary, diagnosis.hypothesis as one text: a per-field slicer or a
        reordered join cannot reproduce it.
        """
        expected = reference_inventory(
            self.memory_root / self.DOMAIN / "skill_memory.yaml", "ART_MEM_001"
        )
        self.assertEqual(
            expected,
            [
                "An entry carrying two independently evaluable propositions.",
                "Its second sentence carries the second proposition.",
                "A boundary sentence naming where the entry holds.",
                "A hypothesis sentence naming the cause.",
            ],
        )
        first = self.sentences("ART_MEM_001")
        second = self.sentences("ART_MEM_001")
        self.assertEqual(first.returncode, 0, self.output(first))
        self.assertEqual(first.stdout, second.stdout, "emission is not stable")
        header = re.fullmatch(
            r"ART_MEM_001: (\d+) sentence\(s\)", first.stdout.splitlines()[0]
        )
        self.assertIsNotNone(header, first.stdout)
        count = int(header.group(1))
        emitted = self.sentence_lines(first.stdout)
        self.assertEqual(count, len(emitted))
        self.assertEqual(emitted, expected)

    @unittest.skipUnless(
        (MEMORY / "software-engineering" / "skill_memory.yaml").is_file(),
        "no software-engineering store in this checkout",
    )
    def test_the_live_se_entry_inventory_is_stable_across_runs(self) -> None:
        """Acceptance criterion 1 against the live entry the ticket names:
        `sentences --domain software-engineering --entry SE_MEM_001` is stable
        across runs and equals the recompute from the live store's bytes (a
        read of the corpus; the tree is asserted unchanged by the firewall
        test)."""
        store_path = MEMORY / "software-engineering" / "skill_memory.yaml"
        expected = reference_inventory(store_path, "SE_MEM_001")
        self.assertTrue(expected)
        first = run_migrator(
            "sentences", "--domain", "software-engineering",
            "--entry", "SE_MEM_001", memory=MEMORY,
        )
        second = run_migrator(
            "sentences", "--domain", "software-engineering",
            "--entry", "SE_MEM_001", memory=MEMORY,
        )
        self.assertEqual(first.returncode, 0, self.output(first))
        self.assertEqual(first.stdout, second.stdout, "emission is not stable")
        header = re.fullmatch(
            r"SE_MEM_001: (\d+) sentence\(s\)", first.stdout.splitlines()[0]
        )
        self.assertIsNotNone(header, first.stdout)
        self.assertEqual(int(header.group(1)), len(expected))
        self.assertEqual(self.sentence_lines(first.stdout), expected)

    def test_the_sentences_command_takes_no_ledger_flag(self) -> None:
        """Emission only: the subcommand can neither read nor write a ledger —
        it is not even in its argument parser — and the fixture ledger's bytes
        are untouched by a run."""
        ledger_bytes = self.ledger_path().read_bytes()
        result = self.sentences("ART_MEM_001")
        self.assertEqual(result.returncode, 0, self.output(result))
        self.assertEqual(self.ledger_path().read_bytes(), ledger_bytes)
        help_result = run_migrator("sentences", "--help", memory=self.memory_root)
        self.assertEqual(help_result.returncode, 0, self.output(help_result))
        self.assertNotIn("--ledger-dir", help_result.stdout)

    def test_a9_passes_on_a_complete_fixture_map(self) -> None:
        """Acceptance criterion 2: the baseline ledger's complete maps pass
        A9, with the report stating the exact coverage and mark counts."""
        result = self.account(self.base_ledger())
        self.assertEqual(result.returncode, 0, self.output(result))
        self.assertIn(
            "A9: PASS: 5 sentence(s) in 2 entr(ies) each accounted exactly "
            "once; 0 accretion entr(ies) declared, 0 second-reader mark(s) "
            "recorded",
            result.stdout,
        )

    def test_an_unattributed_sentence_fails_a9(self) -> None:
        """Acceptance criterion 3 (44a): a dropped row fails A9, naming the
        legacy entry and the sentence number, and no other check trips."""
        ledger = self.base_ledger()
        del ledger["decompositions"][0]["sentence_map"][1]  # sentence 2 loses its row
        result = self.account(ledger)
        self.assertEqual(result.returncode, 1, self.output(result))
        self.assertIn("A9: FAIL", result.stdout)
        self.assertIn(
            "legacy entry 'ART_MEM_001' sentence 2 is not accounted for",
            self.output(result),
        )
        for check in ("A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A10"):
            self.assertIn(f"{check}: PASS", result.stdout)

    def test_a_doubly_attributed_sentence_fails_a9(self) -> None:
        """Acceptance criterion 4: a second row for a counted sentence fails
        A9 — exactly once, not at least once."""
        ledger = self.base_ledger()
        ledger["decompositions"][0]["sentence_map"].append(
            {"sentence": 1, "non_propositional": "restatement"}
        )
        result = self.account(ledger)
        self.assertEqual(result.returncode, 1, self.output(result))
        self.assertIn("A9: FAIL", result.stdout)
        self.assertIn(
            "legacy entry 'ART_MEM_001' sentence 1 appears more than once in "
            "its sentence map",
            self.output(result),
        )
        for check in ("A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A10"):
            self.assertIn(f"{check}: PASS", result.stdout)

    def test_a_proposition_absent_from_the_decomposition_fails_a9(self) -> None:
        """Acceptance criterion 5: a reference to a proposition id that is not
        recorded in that entry's decomposition fails A9 by name."""
        ledger = self.base_ledger()
        ledger["decompositions"][0]["sentence_map"][0]["propositions"] = [
            "ART_MEM_001#p9"
        ]
        result = self.account(ledger)
        self.assertEqual(result.returncode, 1, self.output(result))
        self.assertIn("A9: FAIL", result.stdout)
        self.assertIn(
            "legacy entry 'ART_MEM_001' sentence 1 references unknown "
            "proposition 'ART_MEM_001#p9'",
            self.output(result),
        )
        for check in ("A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A10"):
            self.assertIn(f"{check}: PASS", result.stdout)

    def test_a_sentence_cannot_reference_another_entry_s_proposition(self) -> None:
        """The neighbouring direction of criterion 5: the id exists in the
        ledger, but belongs to a different legacy entry's decomposition."""
        ledger = self.base_ledger()
        ledger["decompositions"][0]["sentence_map"][0]["propositions"] = [
            "ART_MEM_002#p1"
        ]
        result = self.account(ledger)
        self.assertEqual(result.returncode, 1, self.output(result))
        self.assertIn("A9: FAIL", result.stdout)
        self.assertIn(
            "references proposition 'ART_MEM_002#p1', which belongs to "
            "another entry's decomposition",
            self.output(result),
        )

    def test_an_out_of_range_sentence_number_fails_a9(self) -> None:
        """A row for a sentence the frozen bytes never yielded is an
        invented sentence, not coverage."""
        ledger = self.base_ledger()
        ledger["decompositions"][0]["sentence_map"].append(
            {"sentence": 99, "non_propositional": "restatement"}
        )
        result = self.account(ledger)
        self.assertEqual(result.returncode, 1, self.output(result))
        self.assertIn("A9: FAIL", result.stdout)
        self.assertIn(
            "legacy entry 'ART_MEM_001' sentence 99 is out of range; the "
            "entry has 4 sentence(s)",
            self.output(result),
        )
        for check in ("A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A10"):
            self.assertIn(f"{check}: PASS", result.stdout)

    def test_an_unknown_non_propositional_reason_fails(self) -> None:
        """Acceptance criterion 6: the reason set is closed at the schema, so
        a non-member is refused before any check runs — and the refusal shows
        the whole closed set."""
        ledger = self.base_ledger()
        ledger["decompositions"][0]["sentence_map"][2]["non_propositional"] = (
            "sounds_about_right"
        )
        result = self.account(ledger)
        self.assertEqual(result.returncode, 1, self.output(result))
        self.assertIn("ledger schema:", result.stderr)
        self.assertIn("'sounds_about_right'", result.stderr)
        self.assertIn("evidence_recitation", result.stderr)
        self.assertIn("checks do not run", result.stdout)

    def test_an_accretion_entry_requires_the_second_reader_mark(self) -> None:
        """Acceptance criterion 7, both directions, and the passing pair: the
        script records and checks the mark's presence — never the reading."""
        declared = self.base_ledger()
        declared["accretion_entries"] = ["ART_MEM_001"]
        result = self.account(declared)
        self.assertEqual(result.returncode, 1, self.output(result))
        self.assertIn("A9: FAIL", result.stdout)
        self.assertIn(
            "legacy entry 'ART_MEM_001' requires a second independent "
            "decomposition, but its ledger record lacks the second-reader mark",
            self.output(result),
        )
        for check in ("A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A10"):
            self.assertIn(f"{check}: PASS", result.stdout)

        stray = self.base_ledger()
        stray["decompositions"][1]["second_reader"] = True
        result = self.account(stray)
        self.assertEqual(result.returncode, 1, self.output(result))
        self.assertIn("A9: FAIL", result.stdout)
        self.assertIn(
            "decomposition record 'ART_MEM_002' carries the second-reader "
            "mark, but accretion_entries does not declare it an accretion entry",
            self.output(result),
        )

        marked = self.base_ledger()
        marked["accretion_entries"] = ["ART_MEM_001"]
        marked["decompositions"][0]["second_reader"] = True
        result = self.account(marked)
        self.assertEqual(result.returncode, 0, self.output(result))
        self.assertIn(
            "A9: PASS: 5 sentence(s) in 2 entr(ies) each accounted exactly "
            "once; 1 accretion entr(ies) declared, 1 second-reader mark(s) "
            "recorded",
            result.stdout,
        )

    def test_a9_accepts_any_attribution_of_the_same_sentences(self) -> None:
        """The firewall proof: A9 proves coverage, not judgment. Swapping
        every row to the other mode — all non-propositional, then all one
        proposition — leaves the check green, because which proposition a
        sentence belongs to (and whether `restatement` is honest) is review
        judgment, never the script's (§7.2, §7.5)."""
        everything_recited = self.base_ledger()
        for record in everything_recited["decompositions"]:
            record["sentence_map"] = [
                {"sentence": row["sentence"], "non_propositional": "evidence_recitation"}
                for row in record["sentence_map"]
            ]
        result = self.account(everything_recited)
        self.assertEqual(result.returncode, 0, self.output(result))
        self.assertIn("A9: PASS", result.stdout)

        everything_attributed = self.base_ledger()
        for record in everything_attributed["decompositions"]:
            first_proposition = record["propositions"][0]["id"]
            record["sentence_map"] = [
                {"sentence": row["sentence"], "propositions": [first_proposition]}
                for row in record["sentence_map"]
            ]
        result = self.account(everything_attributed)
        self.assertEqual(result.returncode, 0, self.output(result))
        self.assertIn("A9: PASS", result.stdout)

    def test_there_is_one_sentence_splitter_in_the_repository(self) -> None:
        """Acceptance criterion 8: one SENTENCE_RE definition in the whole
        repository, in validate.py; the migrator imports it and never copies
        the pattern."""
        defined_at: list[str] = []
        for path in sorted(ROOT.rglob("*.py")):
            if "__pycache__" in path.parts or ".git" in path.parts:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            if re.search(r"^SENTENCE_RE\s*=", text, re.MULTILINE):
                defined_at.append(path.relative_to(ROOT).as_posix())
        self.assertEqual(defined_at, ["PASS/tools/validate.py"])

        source = TOOL.read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported = [
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module == "validate"
            for alias in node.names
        ]
        self.assertIn("SENTENCE_RE", imported)
        self.assertNotIn(r"(?<=[.!?])", source, "the splitter pattern was copied")


CLAIM_TAILS = (
    "01M55WJVKRMGS6KTMQ5TSXRQDC",
    "01M55WJVKRFNJW5TVAPVTVSM7T",
    "01M55WJVKRTZQ3EHK6RJP8XWVY",
)


@unittest.skipUnless(
    (MEMORY / "software-engineering" / "skill_memory.yaml").is_file()
    and (MEMORY / "game-design" / "skill_memory.yaml").is_file(),
    "no software-engineering and game-design stores in this checkout",
)
class SpecificationExamples(MigrationFixture):
    """T15 completion evidence: the specification's own example decompositions
    (R2.5 §7.2) carry complete sentence maps that pass A9 end to end.

    Each live entry is read into a disposable single-entry store beside a copy
    of its domain's history — a read of the corpus, never a write to it, and
    never a migration input for the live tree. GAMEDESIGN_MEM_001's
    propositions are the specification's example verbatim; SE_MEM_001 records
    the three propositions R2.1 counts for it, with text labelled as
    placeholder. Every map row is coverage-only: rows are built from the
    tool's own emission so A9's independent derivation must agree with them,
    and no row asserts what a sentence means — decomposition is judgment
    (§7.2) and this suite never exercises it. Both entries are declared
    accretion with the second-reader mark, per R2.1's ~16 accretion
    narratives (which name SE_MEM_001 and GD_MEM_001)."""

    def frozen_single_entry(self, domain: str, entry_id: str) -> dict:
        store = yaml.safe_load((MEMORY / domain / "skill_memory.yaml").read_bytes())
        matches = [
            entry for entry in store["entries"] if entry.get("id") == entry_id
        ]
        self.assertEqual(
            len(matches), 1, f"the live {domain} store must carry {entry_id}"
        )
        domain_dir = self.memory_root / domain
        domain_dir.mkdir(parents=True)
        single = dict(store)
        single["entries"] = matches
        (domain_dir / "skill_memory.yaml").write_bytes(
            yaml.safe_dump(single, sort_keys=False).encode("utf-8")
        )
        shutil.copyfile(
            MEMORY / domain / "training_history.jsonl",
            domain_dir / "training_history.jsonl",
        )
        frozen = run_migrator(
            "freeze", "--domain", domain,
            "--ledger-dir", self.ledger_dir, memory=self.memory_root,
        )
        self.assertEqual(frozen.returncode, 0, frozen.stdout + frozen.stderr)
        return self.ledger(domain=domain)["legacy"]

    def account_example(
        self,
        domain: str,
        entry_id: str,
        token: str,
        propositions: list[dict],
        spec_rows: dict[int, dict],
    ) -> tuple[subprocess.CompletedProcess[str], int]:
        """One complete migration-shaped run over one live entry; returns the
        `account` result and the emitted sentence count."""
        legacy = self.frozen_single_entry(domain, entry_id)
        emitted = run_migrator(
            "sentences", "--domain", domain, "--entry", entry_id,
            memory=self.memory_root,
        )
        self.assertEqual(emitted.returncode, 0, emitted.stdout + emitted.stderr)
        header = re.fullmatch(
            rf"{re.escape(entry_id)}: (\d+) sentence\(s\)",
            emitted.stdout.splitlines()[0],
        )
        self.assertIsNotNone(header, emitted.stdout)
        count = int(header.group(1))
        rows: list[dict] = []
        for number in range(1, count + 1):
            if number in spec_rows:
                rows.append({"sentence": number, **spec_rows[number]})
            else:
                rows.append(
                    {"sentence": number, "propositions": [propositions[0]["id"]]}
                )
        claim_ids = [
            f"{token}_MEM_{tail}" for tail in CLAIM_TAILS[: len(propositions)]
        ]
        ledger = {
            "domain": domain,
            "legacy": legacy,
            "vnext": {"memory_schema_version": 3, "claim_count": len(claim_ids)},
            "accretion_entries": [entry_id],
            "decompositions": [
                {
                    "legacy_entry": entry_id,
                    "legacy_sha256": legacy["entry_hashes"][entry_id],
                    "propositions": propositions,
                    "sentence_map": rows,
                    "second_reader": True,
                }
            ],
            "dispositions": [
                {
                    "proposition": proposition["id"],
                    "class": "CARRY",
                    "targets": [claim_id],
                }
                for proposition, claim_id in zip(propositions, claim_ids)
            ],
            "holds": [],
        }
        candidate = self.tmp / "candidate" / f"{domain}.yaml"
        candidate.parent.mkdir(parents=True, exist_ok=True)
        candidate.write_bytes(
            yaml.safe_dump(
                {
                    "memory_schema_version": 3,
                    "skillset": domain,
                    "memory_version": 1,
                    "claims": [
                        {"id": claim_id, "claim": "A candidate claim standing in the new store."}
                        for claim_id in claim_ids
                    ],
                },
                sort_keys=False,
            ).encode("utf-8")
        )
        self.ledger_path(self.ledger_dir, domain).write_bytes(
            yaml.safe_dump(ledger, sort_keys=False).encode("utf-8")
        )
        result = run_migrator(
            "account", "--domain", domain,
            "--ledger-dir", self.ledger_dir, "--store", candidate,
            memory=self.memory_root,
        )
        return result, count

    def test_the_specification_example_sentence_maps_pass_a9(self) -> None:
        """Completion evidence: both named entries pass the whole A1-A10 run,
        A9 reporting their exact sentence and second-reader counts."""
        cases = [
            (
                "software-engineering",
                "SE_MEM_001",
                "SE",
                [
                    {"id": "SE_MEM_001#p1", "text": "Placeholder for the first of the three roughly 24-word claims R2.1 counts in this entry; no text is authored here."},
                    {"id": "SE_MEM_001#p2", "text": "Placeholder for the second of the three roughly 24-word claims R2.1 counts in this entry; no text is authored here."},
                    {"id": "SE_MEM_001#p3", "text": "Placeholder for the third of the three roughly 24-word claims R2.1 counts in this entry; no text is authored here."},
                ],
                {},
            ),
            (
                "game-design",
                "GAMEDESIGN_MEM_001",
                "GD",
                [
                    {"id": "GAMEDESIGN_MEM_001#p1", "text": "Designs reusing a small mechanical vocabulary across many situations are easier to explain, compare, and extend."},
                    {"id": "GAMEDESIGN_MEM_001#p2", "text": "A shared randomizer can sit above several operational grammars that still require different interpretation procedures."},
                    {"id": "GAMEDESIGN_MEM_001#p3", "text": "Programmed actions that replace the attribute half of a pool preserve common resolution while changing competence architecture."},
                ],
                {
                    1: {"propositions": ["GAMEDESIGN_MEM_001#p1"]},
                    4: {"non_propositional": "evidence_recitation"},
                    7: {"non_propositional": "episode_narrative"},
                },
            ),
        ]
        for domain, entry_id, token, propositions, spec_rows in cases:
            with self.subTest(entry=entry_id):
                result, count = self.account_example(
                    domain, entry_id, token, propositions, spec_rows,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                for check in ("A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10"):
                    self.assertIn(f"{check}: PASS", result.stdout)
                self.assertIn(
                    f"A9: PASS: {count} sentence(s) in 1 entr(ies) each "
                    "accounted exactly once; 1 accretion entr(ies) declared, "
                    "1 second-reader mark(s) recorded",
                    result.stdout,
                )


if __name__ == "__main__":
    unittest.main()
