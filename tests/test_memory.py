"""Deterministic contracts for Skillset Memory.

The two that matter most, and the reason this suite exists:

    an invalid run never counts as evidence about a capability
    a write is not persisted until the target is reopened and confirmed

Everything else here guards a boundary that was expensive to learn: memory does
not become canon by being copied into it, temporary state does not become
memory, authoring actions are not training events, and an entry that defers its
content to a conversation is not portable.

What this suite cannot prove is listed in tests/README.md: nothing here touches a
live host, so it cannot show that memory was actually consulted during a real
task. It can only show that the tooling reports honestly what it retrieved.
"""

from __future__ import annotations

import ast
from datetime import date
import importlib.util
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
LIBRARY = ROOT / "library"
TOOL = ROOT / "PASS/tools/memory.py"
SCHEMA_DOC = ROOT / "PASS/docs/MEMORY_SCHEMA.md"

# Most of this suite drives the CLI, which is the supported surface. Claim
# identity is a library function with no CLI of its own yet, so it is imported
# directly.
sys.path.insert(0, str(ROOT / "PASS" / "tools"))
_MEMORY_SPEC = importlib.util.spec_from_file_location("skillset_memory_tool", TOOL)
assert _MEMORY_SPEC and _MEMORY_SPEC.loader
memory_tool = importlib.util.module_from_spec(_MEMORY_SPEC)
sys.modules[_MEMORY_SPEC.name] = memory_tool
_MEMORY_SPEC.loader.exec_module(memory_tool)

# Ephemeral wrong-version input, for the loud-unmigrated tests and nothing
# else. It is test input, not a retained legacy store: every test that uses it
# builds it inside its own temporary directory, no committed file carries this
# shape, and no production path parses it as a supported schema. The entry is
# deliberately minimal - the runtime refuses the store on its declared version
# and never reaches the entry, so a richer one would prove nothing.
UNMIGRATED_ENTRY = {
    "id": "TST_MEM_001",
    "scope_type": "topic",
    "scope_id": "example_topic",
    "type": "recurring_failure",
    "evidence_class": "stochastic_performance",
    "observation": "A specific, factual thing that was seen during a real run.",
    "confidence": "provisional",
    "status": "active",
}


def art_claim(**overrides: object) -> dict:
    """A minimal structurally valid v3 claim in the `art` domain.

    `base_claim` further down is the software-engineering counterpart the v3
    suites use; this one exists because the shared store fixture is an `art`
    tree and a claim id carries its own domain token.
    """
    claim = {
        "id": "ART_MEM_01M55WJVKRQ4N8TDZ3G7XB2VHE",
        "claim": "Blocking the shadow shapes before any contour keeps a figure's weight readable.",
        "claim_class": "conduct",
        "claim_kind": "stochastic",
        "confidence": "provisional",
        "delta": {
            "kinds": ["action"],
            "statement": "Block the shadow shapes before drawing any contour.",
        },
        "envelope": {
            "holds_in": ["single-source lighting on a standing figure"],
            "not_shown_in": ["flat frontal light"],
        },
        "provenance": ["runtime_self_audit"],
        "scope": "figure_weight",
        "retrieval_cues": ["shadow shape", "figure weight"],
        "last_verified": "2026-10-17",
    }
    claim.update(overrides)
    return claim


VALID_EVENT = {
    "event_id": "TST_EV_0001",
    "date": "2026-08-22",
    "task": "Produce a finished render under competing load",
    "validity": "valid",
}
INVALID_EVENT = {
    "event_id": "TST_EV_0002",
    "date": "2026-08-22",
    "task": "Tighten an accepted artifact without redesign",
    "validity": "invalid",
    "invalid_reason": "exact_edit_source_unavailable",
}
CORRECTION_EVENT = {
    "event_id": "TST_EV_0003",
    "date": "2026-08-23",
    "task": "Correct the model revision recorded for an earlier attempt",
    "validity": "valid",
    "event_kind": "metadata_correction",
    "supersedes_events": ["TST_EV_0001"],
    "corrections": {"taker.model.revision": "Q4_K_M"},
}
EVIDENCE_CORRECTION_EVENT = {
    "event_id": "TST_EV_0004",
    "date": "2026-08-24",
    "task": "Correct the evidence classification of an earlier attempt",
    "validity": "valid",
    "event_kind": "evidence_correction",
    "supersedes_events": ["TST_EV_0001"],
    "corrections": {
        "disposition": "quarantined",
        "reason": "The attempt did not exercise the capability it was said to measure.",
        "replacement_outcomes": {"TST_EV_0001": "not-applicable"},
    },
}


def run_tool(*args: object, memory: Path | None = None) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, str(TOOL), *map(str, args)]
    if memory is not None:
        command += ["--memory", str(memory)]
    return subprocess.run(command, capture_output=True, text=True, encoding="utf-8", cwd=ROOT)


class MemoryStoreFixture(unittest.TestCase):
    """A disposable memory tree, so no test mutates the shipped store."""

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="pass-memory-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.domain = self.tmp / "art"
        self.domain.mkdir(parents=True)

    def write(
        self,
        claims: list[dict],
        events: list[dict],
        *,
        schema_version: int = 3,
    ) -> None:
        """A schema-3 store and its History.

        `schema_version` is a parameter only so the wrong-version tests can
        declare a retired number here, inside their own temporary tree. No
        committed file carries that shape: it is ephemeral test input, never a
        retained legacy store (criterion 48).
        """
        store: dict = {
            "memory_schema_version": schema_version,
            "skillset": "art",
            "memory_version": 1,
        }
        store["claims" if schema_version == 3 else "entries"] = claims
        (self.domain / "skill_memory.yaml").write_text(
            yaml.safe_dump(store, sort_keys=False), encoding="utf-8",
        )
        (self.domain / "training_history.jsonl").write_text(
            "".join(json.dumps(event, sort_keys=True) + "\n" for event in events),
            encoding="utf-8",
        )

    def validate(self) -> subprocess.CompletedProcess[str]:
        return run_tool("validate", "--domain", "art", memory=self.tmp)


class AdmissibilityContract(MemoryStoreFixture):
    """An invalid run may be remembered. It may never count.

    This class holds the Training History half, which is not versioned (R2.5
    §8.4) and so survived the cutover unchanged. The claim half - a claim that
    cites an invalid, corrected, or quarantined event - is held by
    `V3ReferentialIntegrity` against the only claim schema there is; the
    duplicate entry-shaped versions that used to sit here went with the legacy
    reader at T21 rather than being re-pointed into a second copy of it.

    `test_evidence_count_must_match_cited_events` was one of them, and it is a
    named reversal: R2.5 §8.2 retires it as obsolete because schema 3 has no
    `evidence_count`. What replaced it is the cap of three
    (`V3ClaimInvariants.test_evidence_is_capped_at_three`) plus the
    admissibility checks below and in `V3ReferentialIntegrity`.
    """

    def test_invalid_events_are_kept_rather_than_discarded(self) -> None:
        """The invalid run is the evidence that a tool or controller needs work."""
        self.write([art_claim()], [VALID_EVENT, INVALID_EVENT])
        self.assertEqual(self.validate().returncode, 0)
        lines = (self.domain / "training_history.jsonl").read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 2)

    def test_metadata_correction_is_valid_history_but_not_evidence(self) -> None:
        self.write([], [VALID_EVENT, CORRECTION_EVENT])
        self.assertEqual(self.validate().returncode, 0)
        self.assertEqual(memory_tool.uncited_valid_events(self.domain), ["TST_EV_0001"])

    def test_metadata_correction_must_point_backward_to_known_event(self) -> None:
        correction = dict(CORRECTION_EVENT, supersedes_events=["TST_EV_9999"])
        self.write([], [VALID_EVENT, correction])
        result = self.validate()
        self.assertEqual(result.returncode, 1)
        self.assertIn("supersedes unknown event", result.stdout)

    def test_evidence_correction_quarantines_history_without_deleting_it(self) -> None:
        self.write([], [VALID_EVENT, EVIDENCE_CORRECTION_EVENT])
        self.assertEqual(self.validate().returncode, 0)
        self.assertEqual(memory_tool.uncited_valid_events(self.domain), [])
        self.assertEqual(
            len((self.domain / "training_history.jsonl").read_text(encoding="utf-8").splitlines()),
            2,
        )

    def test_evidence_correction_requires_a_reason_and_closed_outcome(self) -> None:
        correction = dict(EVIDENCE_CORRECTION_EVENT)
        correction["corrections"] = {
            "disposition": "quarantined",
            "reason": "",
            "replacement_outcomes": {"TST_EV_0001": "partial"},
        }
        self.write([], [VALID_EVENT, correction])
        result = self.validate()
        self.assertEqual(result.returncode, 1)
        self.assertIn("corrections.reason must be non-empty", result.stdout)
        self.assertIn("replacement_outcomes", result.stdout)

    def test_lesson_records_the_transferable_mistake_not_the_model(self) -> None:
        event = dict(
            VALID_EVENT,
            taker={
                "learner_id": "qwen-local-01",
                "learner": {"kind": "ai"},
                "model": {"name": "Qwen"},
                "runtime": {"name": "Bionic"},
            },
            lessons=[{
                "drill_id": "DRILL_example",
                "criterion_index": 1,
                "cause": "application",
                "mistake": "Qwen omitted the boundary check.",
                "correction": "Check the boundary before indexing.",
                "prevention": "Make the boundary case explicit in the preflight.",
            }],
        )
        self.write([], [event])
        result = self.validate()
        self.assertEqual(result.returncode, 1)
        self.assertIn("transferable, not name the taker", result.stdout)

        event["lessons"][0]["mistake"] = "The boundary check was omitted."
        self.write([], [event])
        self.assertEqual(self.validate().returncode, 0)

class PersistenceContract(MemoryStoreFixture):
    """Reported written is not verified written."""

    def test_append_confirms_the_write_by_reading_it_back(self) -> None:
        self.write([], [])
        result = run_tool(
            "append", "--domain", "art", "--task", "Render a figure under competing load",
            memory=self.tmp,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("confirmed it on readback", result.stdout)
        events = [json.loads(line) for line in (self.domain / "training_history.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["validity"], "valid")

    def test_append_refuses_an_authoring_action(self) -> None:
        """Authoring a card is not exercising a capability."""
        self.write([], [])
        result = run_tool(
            "append", "--domain", "art", "--task", "Authored a Drill and committed it",
            memory=self.tmp,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("authoring action", result.stderr)
        self.assertEqual((self.domain / "training_history.jsonl").read_text(encoding="utf-8"), "")

    def test_append_refuses_a_card_currency_update_as_training(self) -> None:
        self.write([], [])
        result = run_tool(
            "append", "--domain", "art",
            "--task", "Currency update of four Drills against their linked Patterns",
            memory=self.tmp,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("authoring action", result.stderr)

    def test_append_requires_a_reason_for_an_invalid_run(self) -> None:
        self.write([], [])
        result = run_tool(
            "append", "--domain", "art", "--task", "Attempt a local edit",
            "--validity", "invalid", memory=self.tmp,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("invalid_reason is required", result.stderr)

    def test_append_fails_when_the_readback_cannot_find_the_event(self) -> None:
        """The readback is the contract, not the success message.

        Driven in-process because the point is the failure path: if the write is
        reported and the target does not contain it, append must refuse to claim
        persistence. A subprocess test that only checks the happy path would
        still pass with the readback deleted.
        """
        sys.path.insert(0, str(ROOT / "PASS/tools"))
        self.addCleanup(sys.path.remove, str(ROOT / "PASS/tools"))
        import memory as memory_tool

        self.write([], [])
        original = memory_tool.load_events
        # Simulate a target that accepts the write but does not contain it.
        memory_tool.load_events = lambda domain_dir: ([], [])
        self.addCleanup(setattr, memory_tool, "load_events", original)

        ok, problems = memory_tool.append_event(self.domain, dict(VALID_EVENT))
        self.assertFalse(ok)
        self.assertTrue(any("readback failed" in problem for problem in problems), problems)

    def test_append_refuses_a_duplicate_event_id(self) -> None:
        self.write([], [VALID_EVENT])
        result = run_tool(
            "append", "--domain", "art",
            "--json", json.dumps(dict(VALID_EVENT, task="A different task")),
            memory=self.tmp,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("already exists", result.stderr)


class SchemaContract(MemoryStoreFixture):
    """One schema, loudly (R2.5 §9.1): the runtime reads schema 3 and refuses
    everything else, and it refuses the two retired versions differently from a
    version nobody has ever defined.

    What used to be here was the v1/v2 entry-shape contract - closed
    vocabularies, unknown keys, missing required keys, duplicate ids. Every one
    of those statements is now made against the only claim schema there is, by
    `V3Schema` and `V3ClaimInvariants`, so T21 retired the entry-shaped copies
    rather than re-pointing them into duplicates. The six R2.5 §8.2 reversals
    that lived in this class - `test_learned_principle_is_an_accepted_memory_type`,
    `test_v2_accepts_specialization_profiles_and_card_candidates`,
    `test_v1_rejects_v2_only_entry_types`,
    `test_superseded_status_requires_a_successor`,
    `test_unknown_evidence_origin_is_rejected`, and
    `test_human_teaching_is_a_recognized_evidence_origin` - are obsolete for the
    reason §8.2 gives in each case: schema 3 has no `type`, no `status`, no
    `evidence_origin`, and no second version to gate a type behind. Provenance
    survives as a required claim key, held by
    `V3Leakage.test_provenance_is_required_and_never_a_forbidden_key`.
    """

    def unmigrated_commands(self) -> dict[str, tuple[object, ...]]:
        """Every command that reads a store, with arguments that reach the read."""
        return {
            "validate": ("validate", "--domain", "art"),
            "query": ("query", "--cues", "shadow shape", "--domain", "art"),
            "review": ("review", "--domain", "art"),
            "add": ("add", "--domain", "art", "--json", "{}"),
            "link-evidence": (
                "link-evidence", "--domain", "art",
                "--claim", "TST_MEM_001", "--events", "TST_EV_0001",
            ),
        }

    def assertLoudlyUnmigrated(self, version: int) -> str:
        """Every reading command refuses the store, and none of them edits it."""
        self.write([dict(UNMIGRATED_ENTRY)], [VALID_EVENT], schema_version=version)
        before = (self.domain / "skill_memory.yaml").read_bytes()
        transcript = ""
        for label, args in self.unmigrated_commands().items():
            with self.subTest(command=label):
                result = run_tool(*args, memory=self.tmp)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                output = result.stdout + result.stderr
                transcript += output
                self.assertIn("unmigrated", output)
                self.assertEqual(
                    (self.domain / "skill_memory.yaml").read_bytes(), before,
                    f"{label} changed an unmigrated store",
                )
        return transcript

    def test_a_v1_store_is_loudly_unmigrated(self) -> None:
        """Criterion 34. The message names the store it refused and the way
        forward, so the operator is not left guessing which domain and which
        procedure."""
        transcript = self.assertLoudlyUnmigrated(1)
        self.assertIn("skill_memory.yaml", transcript)
        self.assertIn("memory_schema_version 1", transcript)
        self.assertIn("migrate_memory_v3.py", transcript)
        self.assertIn("MEMORY_SCHEMA.md", transcript)

    def test_a_v2_store_is_loudly_unmigrated(self) -> None:
        transcript = self.assertLoudlyUnmigrated(2)
        self.assertIn("skill_memory.yaml", transcript)
        self.assertIn("memory_schema_version 2", transcript)
        self.assertIn("migrate_memory_v3.py", transcript)

    def test_unmigrated_is_not_corrupt(self) -> None:
        """The distinction R2.5 §9.1 insists on. The bytes are fine; the version
        is retired. Calling it corruption would send a reader looking for damage
        that is not there, and this ticket is explicit that the loud-unmigrated
        message must not generalise into a corruption policy."""
        self.write([dict(UNMIGRATED_ENTRY)], [VALID_EVENT], schema_version=1)
        result = self.validate()
        self.assertEqual(result.returncode, 1)
        output = (result.stdout + result.stderr).lower()
        self.assertIn("unmigrated, not corrupt", output)
        for word in ("corrupt file", "damaged", "malformed", "unreadable"):
            self.assertNotIn(word, output)

    def test_unknown_schema_version_is_rejected(self) -> None:
        """The R2.5 §8.2 reversal that survives in spirit: an unknown version is
        still rejected, and criterion 8 requires it to read differently from an
        unmigrated one. A version nobody has defined is a validation error; a v1
        store is a migration that has not been run."""
        self.write([art_claim()], [], schema_version=4)
        unknown = self.validate()
        self.assertEqual(unknown.returncode, 1)
        self.assertIn("memory_schema_version must be one of [3]", unknown.stdout)
        self.assertNotIn("unmigrated", unknown.stdout + unknown.stderr)

        self.write([dict(UNMIGRATED_ENTRY)], [VALID_EVENT], schema_version=2)
        unmigrated = self.validate()
        self.assertEqual(unmigrated.returncode, 1)
        self.assertIn("unmigrated", unmigrated.stdout)
        self.assertNotIn("must be one of", unmigrated.stdout)

    def test_absence_is_still_silent_and_fail_open(self) -> None:
        """Criterion 32, stated beside its opposite. Absence is silent and exits
        0; a wrong-version store is presence - it asserts that learned state
        exists while being unreadable - so it is loud. Both belong in one test:
        the cutover must not have made absence loud, and must not have left
        presence quiet."""
        self.write([], [])
        cases = {
            "empty store": (self.tmp, ("--domain", "art")),
            "missing domain": (self.tmp, ("--domain", "writing")),
            "missing root": (self.tmp / "no-such-root", ()),
        }
        for label, (memory, args) in cases.items():
            with self.subTest(case=label):
                result = run_tool("query", "--cues", "shadow shape", *args, memory=memory)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("retrieved: (none)", result.stdout)
                self.assertNotIn("unmigrated", result.stdout + result.stderr)

        self.write([dict(UNMIGRATED_ENTRY)], [VALID_EVENT], schema_version=1)
        loud = run_tool("query", "--cues", "shadow shape", "--domain", "art", memory=self.tmp)
        self.assertEqual(loud.returncode, 1)
        self.assertIn("unmigrated", loud.stdout + loud.stderr)

    def test_no_runtime_path_parses_schema_one_or_two(self) -> None:
        """Criterion 35, read off the syntax tree rather than off behavior.

        Two deleted modules that cannot return, one accepted version, and the
        retired numbers named in exactly one function - the one that builds the
        refusal. A behavioral test only proves the paths somebody remembered to
        drive; a reader on the source proves there is no branch left to drive.
        """
        for name in ("memory_legacy_input", "migrate_memory_v3"):
            self.assertFalse(
                (ROOT / "PASS/tools" / f"{name}.py").exists(),
                f"{name}.py survived the cutover",
            )
        self.assertEqual(memory_tool.SUPPORTED_SCHEMA_VERSIONS, {3})
        self.assertEqual(memory_tool.LEGACY_SCHEMA_VERSIONS, {1, 2})
        for gone in (
            "score_entry", "query_store", "review_legacy_store", "validate_entry",
            "STALE_DAYS", "ENTRY_REQUIRED", "RETRIEVABLE_STATUS",
        ):
            with self.subTest(name=gone):
                self.assertFalse(hasattr(memory_tool, gone), f"{gone} survived T21")

        for relative in ("PASS/tools/memory.py", "PASS/tools/build_release.py"):
            source = (ROOT / relative).read_text(encoding="utf-8")
            tree = ast.parse(source)
            with self.subTest(module=relative):
                self.assertNotIn("memory_legacy_input", source)
                legacy_literals = [
                    ast.unparse(node)
                    for node in ast.walk(tree)
                    if isinstance(node, ast.Compare)
                    and "schema_version" in ast.unparse(node)
                    and any(
                        isinstance(side, ast.Constant) and side.value in (1, 2)
                        for side in node.comparators
                    )
                ]
                self.assertEqual(
                    legacy_literals, [],
                    "a schema version is still compared against 1 or 2",
                )
                readers = sorted(
                    node.name for node in ast.walk(tree)
                    if isinstance(node, ast.FunctionDef)
                    and "LEGACY_SCHEMA_VERSIONS" in ast.unparse(node)
                )
                self.assertEqual(
                    readers,
                    ["unmigrated_problem"] if relative.endswith("memory.py") else [],
                    "the retired versions are read somewhere other than the refusal",
                )

class ShippedStore(unittest.TestCase):
    """The memory that actually ships in this repository."""

    def test_shipped_memory_validates(self) -> None:
        result = run_tool("validate")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_no_legacy_store_remains_in_the_working_tree(self) -> None:
        """Criterion 48, read literally and over the whole repository.

        Every `skill_memory.yaml` in the tree declares schema 3 - not just the
        four under `memory/`, because a committed fixture that is itself a v1 or
        v2 store would be a transition scaffold surviving the ticket that
        deleted them. The wrong-version tests build their input in a temporary
        directory instead, which is test input rather than a retained store.

        `workspace/` is excluded, and only `workspace/`: the FREEZE inputs and
        signed ledgers under `workspace/handoffs/` are untracked migration
        evidence that this ticket is explicitly forbidden to delete, and the
        owner releases them. Nothing active reads them, and a release never
        ships them.
        """
        offenders: list[str] = []
        for store in ROOT.rglob("skill_memory.yaml"):
            relative = store.relative_to(ROOT).as_posix()
            if relative.startswith(("workspace/", "archive/")):
                continue
            data = yaml.safe_load(store.read_text(encoding="utf-8")) or {}
            declared = data.get("memory_schema_version") if isinstance(data, dict) else None
            if declared != 3:
                offenders.append(f"{relative}: memory_schema_version {declared!r}")
        self.assertEqual(offenders, [], "a pre-schema-3 store survives in the working tree")

    def test_every_domain_with_memory_is_a_real_library_package(self) -> None:
        for domain_dir in MEMORY.iterdir():
            if domain_dir.is_dir() and (domain_dir / "skill_memory.yaml").is_file():
                self.assertTrue(
                    (LIBRARY / domain_dir.name).is_dir(),
                    f"memory/{domain_dir.name} has no matching library package",
                )

    def test_memory_is_not_inlined_into_canon(self) -> None:
        """An entry that must apply every turn earns promotion, not a paste.

        Copying memory into an always-loaded file creates a second write site and
        lets the retrieval path decay unobserved. Learned principles and empirical
        calibration may overlap conceptually with the canon they inform, so shared
        phrases are not proof of inlining. No complete memory observation and no
        entry id may appear in a card or skill entrypoint.
        """
        canon_texts: list[tuple[str, str]] = []
        for path in LIBRARY.rglob("*.md"):
            canon_texts.append((path.as_posix(), path.read_text(encoding="utf-8")))
        for folder in (ROOT / ".claude", ROOT / ".agents"):
            for path in folder.rglob("*.md") if folder.is_dir() else []:
                canon_texts.append((path.as_posix(), path.read_text(encoding="utf-8")))

        normalized = [(label, " ".join(text.lower().split())) for label, text in canon_texts]

        for domain_dir in MEMORY.iterdir():
            store = domain_dir / "skill_memory.yaml"
            if not store.is_file():
                continue
            data = yaml.safe_load(store.read_text(encoding="utf-8")) or {}
            for entry in data.get("entries") or []:
                entry_id = str(entry.get("id", ""))
                for label, text in normalized:
                    self.assertNotIn(
                        entry_id.lower(), text,
                        f"memory id {entry_id} appears in canon at {label}",
                    )
                observation = " ".join(
                    str(entry.get("observation", "")).lower().split()
                )
                for label, text in normalized:
                    self.assertNotIn(
                        observation, text,
                        f"complete memory observation from {entry_id} appears verbatim in canon at {label}",
                    )

    def test_memory_carries_no_practice_history_into_cards(self) -> None:
        """CLAUDE.md rule 15, checked from the other side."""
        for path in LIBRARY.rglob("*.md"):
            text = path.read_text(encoding="utf-8").lower()
            for marker in ("skill_memory", "training_history", "memory_schema_version"):
                self.assertNotIn(marker, text, f"{path.as_posix()} references the memory store")


class Portability(unittest.TestCase):
    """Cold portability: the lesson survives without the repository around it."""

    def test_memory_validates_and_retrieves_with_nothing_but_itself(self) -> None:
        tmp = Path(tempfile.mkdtemp(prefix="pass-memory-portable-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        shutil.copytree(MEMORY, tmp / "memory")

        validated = run_tool("validate", memory=tmp / "memory")
        self.assertEqual(validated.returncode, 0, validated.stdout + validated.stderr)

        queried = run_tool("query", "--cues", "hand", memory=tmp / "memory")
        self.assertEqual(queried.returncode, 0, queried.stderr)
        self.assertNotIn("retrieved: (none)", queried.stdout)

    def test_deleting_memory_does_not_invalidate_the_library(self) -> None:
        """The test that keeps memory from becoming the retired machinery.

        Canon does not depend on the empirical record of using it, exactly as it
        does not depend on the sources it was learned from. If this ever fails,
        memory has become a runtime dependency and ARCHITECTURE.md item 20 is
        broken.
        """
        tmp = Path(tempfile.mkdtemp(prefix="pass-no-memory-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        shutil.copytree(LIBRARY, tmp / "library")
        result = subprocess.run(
            [sys.executable, str(ROOT / "PASS/tools/validate.py"), "--library", str(tmp / "library")],
            capture_output=True, text=True, encoding="utf-8", cwd=ROOT,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse((tmp / "memory").exists())

    def test_no_entry_depends_on_a_conversation_or_a_source(self) -> None:
        for domain_dir in MEMORY.iterdir():
            store = domain_dir / "skill_memory.yaml"
            if not store.is_file():
                continue
            text = store.read_text(encoding="utf-8").lower()
            for phrase in ("see the chat", "see the conversation", "see the transcript", "source_id", "page "):
                self.assertNotIn(phrase, text, f"{store.as_posix()} depends on {phrase!r}")

    @staticmethod
    def v3_reference_store() -> dict:
        """A v3 store exercising every reference kind: canon, evidence, and a
        symmetric contradiction pair."""
        first = base_claim(
            canon=["PAT_state_the_lifetime_contract_at_the_interface"],
            evidence=["SE_EV_0001"],
        )
        second = base_claim(id="SE_MEM_01M55WJVKR0QB8C42T4SSG2KW2")
        first["contradicts"] = [second["id"]]
        second["contradicts"] = [first["id"]]
        return v3_store([first, second])

    def write_v3_domain(self, root: Path, store: dict) -> Path:
        domain_dir = root / "memory" / "software-engineering"
        domain_dir.mkdir(parents=True, exist_ok=True)
        (domain_dir / "skill_memory.yaml").write_text(
            yaml.safe_dump(store, sort_keys=False), encoding="utf-8",
        )
        return domain_dir

    def test_v3_store_validates_in_a_bare_directory(self) -> None:
        """Criterion 28a: a copy containing only memory/<domain>/skill_memory.yaml
        — no version-control repository, no History, no Library, no sibling
        domains — validates exactly as the same store does in place, and a
        `.git` directory beside it changes nothing because nothing reads it."""
        store = self.v3_reference_store()
        expected = memory_tool.validate_v3_contents("software-engineering", store)
        self.assertEqual(expected, ([], []))

        bare = Path(tempfile.mkdtemp(prefix="pass-v3-bare-"))
        self.addCleanup(shutil.rmtree, bare, ignore_errors=True)
        bare_domain = self.write_v3_domain(bare, store)
        self.assertEqual(
            sorted(path.name for path in (bare / "memory").iterdir()),
            ["software-engineering"],
        )
        self.assertFalse((bare_domain / "training_history.jsonl").exists())
        self.assertFalse((bare / "library").exists())
        self.assertFalse((bare / ".git").exists())
        self.assertEqual(memory_tool.validate_v3_store(bare_domain), expected)

        with_repository = Path(tempfile.mkdtemp(prefix="pass-v3-repo-"))
        self.addCleanup(shutil.rmtree, with_repository, ignore_errors=True)
        (with_repository / ".git").mkdir()
        repo_domain = self.write_v3_domain(with_repository, store)
        self.assertEqual(memory_tool.validate_v3_store(repo_domain), expected)

    def test_no_tool_invokes_version_control(self) -> None:
        """Criterion 28a (grep-level): the memory tool never names, imports, or
        runs a version-control command on any path — a store must validate with
        no repository around it."""
        source = TOOL.read_text(encoding="utf-8")
        self.assertIsNone(
            re.search(r"(?i)\bgit\b", source),
            "PASS/tools/memory.py names version control",
        )
        tree = ast.parse(source)
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module)
        for banned in ("subprocess", "git", "pexpect"):
            self.assertNotIn(banned, imported, f"memory.py imports {banned}")
        for banned in ("os.system", "Popen", "check_call", "check_output"):
            self.assertNotIn(banned, source, f"memory.py can execute {banned}")


class ToolingBoundary(unittest.TestCase):
    """The memory tool reads memory. It does not grow a ledger."""

    def test_tool_takes_no_source_ledger_or_provenance_arguments(self) -> None:
        help_text = run_tool("--help").stdout + run_tool("validate", "--help").stdout
        for banned in ("--source", "--ledger", "--provenance", "--receipt", "--manifest"):
            self.assertNotIn(banned, help_text)

    def test_card_validator_still_reads_only_the_library(self) -> None:
        """Memory must not have been bolted onto the card validator."""
        validator = (ROOT / "PASS/tools/validate.py").read_text(encoding="utf-8")
        for marker in ("skill_memory", "training_history", "memory."):
            self.assertNotIn(marker, validator)

    def test_schema_document_exists_and_declares_the_invariants(self) -> None:
        text = SCHEMA_DOC.read_text(encoding="utf-8")
        for required in (
            "never increment",
            "Presence is not consultation",
            "authoritative writable working state",
            "reopens and contains the expected state",
        ):
            self.assertIn(required, text, f"MEMORY_SCHEMA.md is missing: {required}")


class V3WriteFixture(unittest.TestCase):
    """A disposable schema-3 store, so no test mutates the shipped corpus.

    A temporary store rather than the live one, because a write test that
    edited the shipped corpus would be recording its own fixtures as learned
    state. Every store here declares schema 3, which since T21 is the only
    version any command will read or write.
    """

    DOMAIN = "software-engineering"

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="pass-memory-v3-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.domain = self.tmp / self.DOMAIN
        self.domain.mkdir(parents=True)

    def write(
        self, claims: list[dict], events: list[dict] | None = None, **overrides: object,
    ) -> None:
        (self.domain / "skill_memory.yaml").write_text(
            yaml.safe_dump(
                v3_store(claims, skillset=self.DOMAIN, **overrides), sort_keys=False,
            ),
            encoding="utf-8",
        )
        if events is not None:
            (self.domain / "training_history.jsonl").write_text(
                "".join(json.dumps(event, sort_keys=True) + "\n" for event in events),
                encoding="utf-8",
            )

    def tool(self, *args: object) -> subprocess.CompletedProcess[str]:
        return run_tool(*args, "--domain", self.DOMAIN, memory=self.tmp)

    def validate_tool(self) -> subprocess.CompletedProcess[str]:
        return run_tool("validate", "--domain", self.DOMAIN, memory=self.tmp)

    def store(self) -> bytes:
        return (self.domain / "skill_memory.yaml").read_bytes()

    def claims(self) -> dict[str, dict]:
        return {
            claim["id"]: claim
            for claim in yaml.safe_load(self.store()).get("claims") or []
        }

    def version(self) -> int:
        return yaml.safe_load(self.store())["memory_version"]

    def new_claim(self, **changes: object) -> str:
        """A structurally valid claim with no `id`: `add` generates that."""
        claim = {key: value for key, value in base_claim().items() if key != "id"}
        claim.update(changes)
        return json.dumps(claim)

    def added_id(self, result: subprocess.CompletedProcess[str]) -> str:
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        match = re.search(r"added (\S+);", result.stdout)
        self.assertIsNotNone(match, result.stdout)
        return match.group(1)

    def add(self, **changes: object) -> str:
        return self.added_id(self.tool("add", "--json", self.new_claim(**changes)))

    def assert_refused(
        self, result: subprocess.CompletedProcess[str], before: bytes, text: str,
    ) -> None:
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn(text, result.stderr)
        self.assertIn("memory unchanged", result.stderr)
        self.assertEqual(self.store(), before)


class V3WriteIdentity(V3WriteFixture):
    """R2.5 §3.4/§9.3: `add` owns the id, `update` cannot reach it, and a
    retired id never comes back."""

    def test_add_generates_a_unique_id(self) -> None:
        self.write([])
        first = self.add()
        second = self.add(scope="other_contracts")
        self.assertNotEqual(first, second)
        for claim_id in (first, second):
            with self.subTest(id=claim_id):
                self.assertRegex(claim_id, memory_tool.CLAIM_ID_RE)
                self.assertEqual(
                    memory_tool.claim_id_problems(claim_id, self.DOMAIN), [],
                )
        self.assertEqual(sorted(self.claims()), sorted([first, second]))

    def test_add_refuses_a_caller_supplied_id(self) -> None:
        self.write([])
        before = self.store()
        supplied = json.dumps(base_claim())
        self.assert_refused(
            self.tool("add", "--json", supplied), before, "never supplied",
        )
        self.assertEqual(self.claims(), {})

    def test_add_bumps_the_version(self) -> None:
        self.write([base_claim()])
        self.assertEqual(self.version(), 1)
        self.add(scope="other_contracts")
        self.assertEqual(self.version(), 2)
        self.add(scope="third_contracts")
        self.assertEqual(self.version(), 3)

    def test_update_refuses_to_change_an_id(self) -> None:
        claim = base_claim()
        self.write([claim])
        before = self.store()
        fresh = memory_tool.new_claim_id(self.DOMAIN)
        self.assert_refused(
            self.tool("update", "--id", claim["id"], "--json", json.dumps({"id": fresh})),
            before,
            "never changes",
        )
        self.assertEqual(sorted(self.claims()), [claim["id"]])

    def test_update_leaves_the_id_byte_identical(self) -> None:
        """Criterion 7e, over every field the criterion names: each rewrite is
        allowed and none of them can move the claim's identity."""
        claim = base_claim()
        self.write([claim], [V3_VALID_EVENT])
        patches = (
            {"claim": "A const overload carries the lifetime obligation of its mutating twin."},
            {"delta": {"kinds": ["verification"], "statement": "Check both overloads."}},
            {"envelope": {"holds_in": ["const overload pairs"], "not_shown_in": ["free functions"]}},
            {"confidence": "strong"},
            {"canon": ["PAT_state_the_lifetime_contract_at_the_interface"]},
            {"evidence": ["SE_EV_0001"]},
            {"retrieval_cues": ["const overload", "lifetime"]},
            {"last_verified": "2026-10-18"},
        )
        for patch in patches:
            with self.subTest(patch=sorted(patch)):
                result = self.tool(
                    "update", "--id", claim["id"], "--json", json.dumps(patch),
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(sorted(self.claims()), [claim["id"]])
        self.assertIn(claim["id"].encode("utf-8"), self.store())

    def test_update_merges_and_null_removes_an_optional_key(self) -> None:
        claim = base_claim(revalidate_after="2026-12-01")
        self.write([claim])
        result = self.tool(
            "update", "--id", claim["id"],
            "--json", '{"confidence": "strong", "revalidate_after": null}',
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        stored = self.claims()[claim["id"]]
        self.assertEqual(stored["confidence"], "strong")
        self.assertNotIn("revalidate_after", stored)

    def test_update_refuses_to_remove_a_required_key_or_add_an_unknown_one(self) -> None:
        claim = base_claim()
        self.write([claim])
        before = self.store()
        for patch, text in (
            ('{"claim": null}', "required key(s) cannot be removed"),
            ('{"colour": "blue"}', "unknown key"),
            ('{}', "non-empty JSON object"),
        ):
            with self.subTest(patch=patch):
                self.assert_refused(
                    self.tool("update", "--id", claim["id"], "--json", patch), before, text,
                )

    def test_a_retired_id_is_never_reissued(self) -> None:
        """Criterion 7g. The legacy allocator read the highest surviving entry,
        so the first `add` after a retirement handed the retired number straight
        back. The generated token needs no surviving state, so there is nothing
        to collide with and nothing to maintain."""
        self.write([])
        retired = self.add()
        self.assertEqual(
            self.tool("retire", "--id", retired, "--reason", "no longer current").returncode,
            0,
        )
        issued = {self.add(scope="other_contracts")}
        for _ in range(20):
            ok, problems, claim_id = memory_tool.add_claim(
                self.domain, json.loads(self.new_claim(scope="loop_contracts")),
            )
            self.assertTrue(ok, problems)
            issued.add(claim_id)
        self.assertNotIn(retired, issued)
        self.assertEqual(len(issued), 21)

    def test_write_operations_work_in_a_bare_directory(self) -> None:
        """Criterion 7i: a store copied somewhere with nothing beside it — no
        History, no Library, no sibling domain, no version-control directory —
        still accepts `add`, `update` and `retire`, because identity comes from
        this process and not from anything on disk."""
        claim = base_claim()
        self.write([claim])
        bare = Path(tempfile.mkdtemp(prefix="pass-memory-bare-write-"))
        self.addCleanup(shutil.rmtree, bare, ignore_errors=True)
        root = bare / "memory"
        (root / self.DOMAIN).mkdir(parents=True)
        shutil.copy2(self.domain / "skill_memory.yaml", root / self.DOMAIN / "skill_memory.yaml")
        self.assertEqual(
            sorted(path.name for path in (root / self.DOMAIN).iterdir()),
            ["skill_memory.yaml"],
        )

        def tool(*args: object) -> subprocess.CompletedProcess[str]:
            return run_tool(*args, "--domain", self.DOMAIN, memory=root)

        added = tool("add", "--json", self.new_claim(scope="bare_contracts"))
        self.assertEqual(added.returncode, 0, added.stderr)
        fresh = re.search(r"added (\S+);", added.stdout).group(1)
        self.assertEqual(memory_tool.claim_id_problems(fresh, self.DOMAIN), [])
        self.assertEqual(
            tool("update", "--id", fresh, "--json", '{"confidence": "strong"}').returncode, 0,
        )
        self.assertEqual(
            tool("retire", "--id", claim["id"], "--reason", "superseded by craft review").returncode,
            0,
        )
        self.assertEqual(
            sorted(path.name for path in (root / self.DOMAIN).iterdir()),
            ["skill_memory.yaml"],
        )
        # The only thing beside the store is the write lock's folder, which the
        # lock empties on release. It is concurrency control, not allocator state.
        self.assertEqual(sorted(path.name for path in root.iterdir()), [".locks", self.DOMAIN])
        self.assertEqual(list((root / ".locks").iterdir()), [])


class V3Retirement(V3WriteFixture):
    """R2.5 §1.4–§1.5: currentness is presence, so retirement is removal and
    the reason it happened is not Memory's to keep."""

    def test_retirement_removes_the_claim_and_requires_a_reason(self) -> None:
        """The reversal of `test_there_is_no_delete`, and the reason for it.

        The old invariant existed to stop evidence destruction. Evidence lives
        in Training History and is untouched by this; what `retire` removes is a
        conclusion that is no longer current, and under current-state semantics
        keeping it was the defect.
        """
        claim = base_claim()
        other = base_claim(id="SE_MEM_01M55WJVKR0QB8C42T4SSG2KW2", scope="other_contracts")
        self.write([claim, other])
        before = self.store()

        missing = self.tool("retire", "--id", claim["id"])
        self.assertEqual(missing.returncode, 2, missing.stdout)
        self.assertEqual(self.store(), before)
        self.assert_refused(
            self.tool("retire", "--id", claim["id"], "--reason", "   "),
            before,
            "requires an explicit reason",
        )

        result = self.tool("retire", "--id", claim["id"], "--reason", "contradicted by later work")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(sorted(self.claims()), [other["id"]])
        self.assertEqual(self.version(), 2)
        self.assertNotIn(claim["id"].encode("utf-8"), self.store())
        self.assertEqual(self.tool("show", "--id", claim["id"]).returncode, 1)
        self.assertEqual(self.validate_tool().returncode, 0)

    def test_retiring_an_unknown_claim_changes_nothing(self) -> None:
        self.write([base_claim()])
        before = self.store()
        self.assert_refused(
            self.tool("retire", "--id", memory_tool.new_claim_id(self.DOMAIN), "--reason", "x"),
            before,
            "no claim",
        )

    def test_retirement_writes_no_tombstone_or_allocator_record(self) -> None:
        """Criterion 7f. The reason is operator-facing at the moment of the
        write: it is not a field, not a tombstone, not a lineage record, and not
        a sidecar. Nothing in or beside the store mentions the removed claim
        afterwards, which is what makes the surviving store a complete statement
        of current state rather than a view over a graveyard."""
        self.write([base_claim(), base_claim(
            id="SE_MEM_01M55WJVKR0QB8C42T4SSG2KW2", scope="other_contracts",
        )])
        retired = sorted(self.claims())[0]
        reason = "replaced after the envelope turned out to be narrower"
        self.assertEqual(
            self.tool("retire", "--id", retired, "--reason", reason).returncode, 0,
        )
        files = sorted(
            path for path in self.tmp.rglob("*") if path.is_file()
        )
        self.assertEqual(
            [path.relative_to(self.tmp).as_posix() for path in files],
            [f"{self.DOMAIN}/skill_memory.yaml"],
        )
        for path in files:
            text = path.read_bytes().decode("utf-8")
            self.assertNotIn(retired, text, f"{path.name} still names the retired claim")
            self.assertNotIn(reason, text, f"{path.name} persisted the retirement reason")
        for word in ("retired", "tombstone", "superseded", "lineage"):
            self.assertNotIn(word, self.store().decode("utf-8"))

    def test_replacement_is_retire_then_add_with_a_fresh_id(self) -> None:
        """Criterion 22 and F4, in the one sequence that replaces `supersede`.

        The replacement carries nothing forward: not the id, and not the
        confidence. A tool that copied either would be deciding, on the
        operator's behalf, that the new claim is as well evidenced as the old
        one — which is exactly the judgment §4.9 reserves for a human write.
        """
        self.write([])
        retired = self.add(confidence="strong")
        self.assertEqual(
            self.tool("retire", "--id", retired, "--reason", "envelope was wrong").returncode, 0,
        )
        replacement = self.add(
            confidence="provisional",
            claim="A const overload narrows what a call may change, not how long the object must live.",
        )
        self.assertNotEqual(replacement, retired)
        stored = self.claims()
        self.assertEqual(sorted(stored), [replacement])
        self.assertEqual(stored[replacement]["confidence"], "provisional")
        # add, retire, add: one bump each, and the retirement is a write like
        # any other rather than a deletion that happens off the books.
        self.assertEqual(self.version(), 4)

    def test_retiring_a_contradiction_target_is_refused(self) -> None:
        """A claim another claim contradicts cannot leave on its own: the
        whole-store validation fails I6 and nothing is written.

        That refusal is the specified behavior, not a convenience. R2.5 §4.8 is
        explicit that a contradicted pair carries "no automatic demotion, no
        automatic merge, no automatic erasure" — so `retire` must not quietly
        strip the surviving side's marker to let itself succeed.

        It also locks the pair: neither claim can be retired while the other
        names it, and no single-claim `update` can reach a state where one can,
        because dropping either side's `contradicts` leaves the other one-sided.
        Resolving a pair needs one write that touches both claims, which is not
        on R2.5 §8.3's operation surface. T08 sees the pair as a review item;
        this test records the gap rather than inventing a resolver here.
        """
        first = base_claim(contradicts=["SE_MEM_01M55WJVKR0QB8C42T4SSG2KW2"])
        second = base_claim(
            id="SE_MEM_01M55WJVKR0QB8C42T4SSG2KW2",
            scope="other_contracts",
            contradicts=[first["id"]],
        )
        self.write([first, second])
        before = self.store()
        for claim_id in (first["id"], second["id"]):
            with self.subTest(retire=claim_id):
                self.assert_refused(
                    self.tool("retire", "--id", claim_id, "--reason", "resolved"),
                    before,
                    "(I6)",
                )
        for claim_id in (first["id"], second["id"]):
            with self.subTest(update=claim_id):
                self.assert_refused(
                    self.tool("update", "--id", claim_id, "--json", '{"contradicts": null}'),
                    before,
                    "one-sided",
                )

    def test_three_claims_from_one_source_are_independent(self) -> None:
        """Criterion 7j: three propositions split out of one legacy entry are
        three claims, each retrievable, updatable and retirable on its own."""
        self.write([])
        ids = [
            self.add(scope=f"split_{index}", claim=text)
            for index, text in enumerate((
                "Const-ness narrows what a call may change, not the lifetime it requires.",
                "A value-returning accessor carries no lifetime obligation on the receiver.",
                "A span returned from a temporary dangles even when the call is const.",
            ))
        ]
        self.assertEqual(len(set(ids)), 3)
        untouched = self.claims()[ids[0]]
        self.assertEqual(
            self.tool("update", "--id", ids[1], "--json", '{"confidence": "strong"}').returncode, 0,
        )
        self.assertEqual(
            self.tool("retire", "--id", ids[2], "--reason", "folded into the second").returncode, 0,
        )
        after = self.claims()
        self.assertEqual(after[ids[0]], untouched)
        self.assertEqual(after[ids[1]]["confidence"], "strong")
        self.assertNotIn(ids[2], after)
        self.assertEqual(self.tool("show", "--id", ids[0]).returncode, 0)


class V3WriteConfidence(V3WriteFixture):
    """R2.5 §4.9 F1–F4 as a tool contract: confidence is stated, never derived."""

    # Every function a write passes through. The confidence rules are negative
    # requirements, so the lock is over this exact set rather than over prose.
    WRITE_FUNCTIONS = (
        "add_claim", "update_claim", "retire_claim", "link_evidence", "change_claims",
        "ordered_claim",
    )

    def write_path_functions(self) -> list[ast.FunctionDef]:
        tree = ast.parse(TOOL.read_text(encoding="utf-8"))
        found = [
            node for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name in self.WRITE_FUNCTIONS
        ]
        self.assertEqual(
            sorted(f.name for f in found), sorted(self.WRITE_FUNCTIONS),
            "the v3 write path is not where this test expects it",
        )
        return found

    def test_no_write_path_computes_or_suggests_a_confidence(self) -> None:
        """F1 at the syntax tree, so a convenience default cannot sneak in.

        Three things are banned outright on a write path: naming the confidence
        vocabulary (nothing here needs to know the ladder), assigning to a
        `confidence` key, and measuring the evidence list. Each is a step on the
        road from "the caller said repeated" to "three events, so repeated".
        """
        for function in self.write_path_functions():
            for node in ast.walk(function):
                if isinstance(node, ast.Name) and node.id == "CONFIDENCE_VALUES":
                    self.fail(f"{function.name} reads the confidence vocabulary")
                if (
                    isinstance(node, ast.Subscript)
                    and isinstance(node.ctx, ast.Store)
                    and isinstance(node.slice, ast.Constant)
                    and node.slice.value == "confidence"
                ):
                    self.fail(f"{function.name} assigns a confidence value")
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "len":
                    measured = ast.dump(node)
                    self.assertNotIn("'evidence'", measured, f"{function.name} measures evidence")

    def test_a_claim_with_no_confidence_is_refused_rather_than_defaulted(self) -> None:
        self.write([])
        before = self.store()
        claim = json.loads(self.new_claim())
        del claim["confidence"]
        self.assert_refused(
            self.tool("add", "--json", json.dumps(claim)), before, "missing required keys",
        )

    def test_the_stored_confidence_is_exactly_what_was_stated(self) -> None:
        """F1 end to end: three admissible events behind a claim do not make it
        `strong`, and no amount of evidence moves the value the caller set."""
        self.write([], [V3_VALID_EVENT, dict(V3_VALID_EVENT, event_id="SE_EV_0005"),
                        dict(V3_VALID_EVENT, event_id="SE_EV_0006")])
        claim_id = self.add(
            confidence="provisional",
            evidence=["SE_EV_0001", "SE_EV_0005", "SE_EV_0006"],
        )
        self.assertEqual(self.claims()[claim_id]["confidence"], "provisional")

    def test_no_write_output_names_a_confidence_it_was_not_given(self) -> None:
        """Criterion 18 over the write surface: nothing a write prints suggests
        or promotes a value. The heuristic that used to derive one from an
        `evidence_count` is gone from `review` as well: T08 kept it off the v3
        path, and T21 deleted it with the legacy reader."""
        self.write([], [V3_VALID_EVENT])
        transcript: list[str] = []
        added = self.tool("add", "--json", self.new_claim(evidence=["SE_EV_0001"]))
        transcript += [added.stdout, added.stderr]
        claim_id = self.added_id(added)
        for args in (
            ("update", "--id", claim_id, "--json", '{"last_verified": "2026-10-18"}'),
            ("retire", "--id", claim_id, "--reason", "no longer current"),
        ):
            result = self.tool(*args)
            self.assertEqual(result.returncode, 0, result.stderr)
            transcript += [result.stdout, result.stderr]
        for value in memory_tool.CONFIDENCE_VALUES:
            for text in transcript:
                self.assertNotIn(value, text, f"a write suggested confidence '{value}'")

    def test_a_claim_citing_an_invalid_run_is_refused(self) -> None:
        """The invariant this suite exists for, on the v3 write path: an invalid
        run is never evidence about a capability (I4)."""
        self.write([], [V3_VALID_EVENT, V3_INVALID_EVENT])
        before = self.store()
        self.assert_refused(
            self.tool("add", "--json", self.new_claim(evidence=["SE_EV_0002"])),
            before,
            "never evidence about a capability",
        )


class V3Admission(V3WriteFixture):
    """R2.5 §9.4: the admission question is asked at the moment of the write."""

    def assert_prompted(self, result: subprocess.CompletedProcess[str]) -> None:
        self.assertIn(memory_tool.ADMISSION_QUESTION, result.stdout)
        self.assertIn(memory_tool.CANON_ONLY_BASELINE, result.stdout)

    def test_the_writer_prints_the_admission_question(self) -> None:
        self.write([])
        added = self.tool("add", "--json", self.new_claim())
        self.assertEqual(added.returncode, 0, added.stderr)
        self.assert_prompted(added)
        self.assertIn("Relative to this skill with Canon and no Memory", added.stdout)
        self.assertIn("Canon-as-written sits at the baseline", added.stdout)

    def test_a_refused_add_is_still_prompted(self) -> None:
        """A prompt, not a gate. The question is for the operator, so it is
        printed before the tool has an opinion about the write at all."""
        self.write([])
        refused = self.tool("add", "--json", self.new_claim(confidence="certain"))
        self.assertEqual(refused.returncode, 1)
        self.assert_prompted(refused)

    def test_an_update_to_the_claim_or_the_delta_re_asks_the_question(self) -> None:
        claim = base_claim()
        self.write([claim])
        for patch in (
            {"claim": "Const-ness narrows what a call changes, not the lifetime it needs."},
            {"delta": {"kinds": ["action"], "statement": "Re-check the mutating twin."}},
        ):
            with self.subTest(patch=sorted(patch)):
                result = self.tool("update", "--id", claim["id"], "--json", json.dumps(patch))
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assert_prompted(result)

    def test_an_update_that_admits_nothing_new_is_not_prompted(self) -> None:
        claim = base_claim()
        self.write([claim])
        for patch in (
            '{"confidence": "strong"}',
            '{"last_verified": "2026-10-18"}',
            '{"retrieval_cues": ["const overload"]}',
        ):
            with self.subTest(patch=patch):
                result = self.tool("update", "--id", claim["id"], "--json", patch)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertNotIn(memory_tool.ADMISSION_QUESTION, result.stdout)
        retired = self.tool("retire", "--id", claim["id"], "--reason", "no longer current")
        self.assertEqual(retired.returncode, 0, retired.stderr)
        self.assertNotIn(memory_tool.ADMISSION_QUESTION, retired.stdout)

    def test_the_prompt_never_waits_for_an_answer(self) -> None:
        """It would stop being a prompt and become a gate — and the gate would
        be a validator deciding whether a delta is real, which §4.7 says no
        validator can do."""
        source = TOOL.read_text(encoding="utf-8")
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                self.assertNotEqual(node.func.id, "input", "the tool reads from stdin")
        self.assertNotIn("sys.stdin", source)


class V3WriteSafety(V3WriteFixture):
    """The safety properties carried over from the legacy writer unchanged:
    whole-store validation, one lock, one version bump, readback, and a refusal
    that leaves the file byte-identical."""

    def test_an_invalid_claim_changes_nothing(self) -> None:
        self.write([base_claim()])
        before = self.store()
        for changes, text in (
            ({"confidence": "certain"}, "closed vocabulary"),
            ({"claim_class": "reach", "delta": {"kinds": ["action"], "statement": "Do it."}}, "(R1)"),
            ({"envelope": {"holds_in": ["everywhere"], "not_shown_in": ["none"]}}, "(E2)"),
            ({"scope": "Not A Slug"}, "(S10)"),
        ):
            with self.subTest(changes=sorted(changes)):
                self.assert_refused(
                    self.tool("add", "--json", self.new_claim(**changes)), before, text,
                )

    def test_a_store_of_another_schema_is_not_writable(self) -> None:
        """Writing is schema-3 only (R2.5 §9.1), and the refusal distinguishes
        the two ways a store can fail that. A retired version is unmigrated: the
        fix is a migration. An undefined version is unknown: there is nothing to
        migrate from. Neither is edited, and the loud-unmigrated half of this -
        across every reading command, with the bytes checked afterwards - is
        `SchemaContract.assertLoudlyUnmigrated`.
        """
        domain = self.tmp / "art"
        domain.mkdir()
        store = domain / "skill_memory.yaml"
        # `link-evidence` checks History before it checks the version, so the
        # file has to be there for the version refusal to be what is tested.
        (domain / "training_history.jsonl").write_text(
            json.dumps(dict(VALID_EVENT, event_id="TST_EV_0001"), sort_keys=True) + chr(10),
            encoding="utf-8",
        )
        cases = {
            1: "unmigrated, not corrupt",
            4: "writes schema 3 only",
        }
        for version, expected in cases.items():
            with self.subTest(schema_version=version):
                # Ephemeral wrong-version input in this test's own temporary
                # tree: no committed store carries either version (criterion 48).
                store.write_text(
                    yaml.safe_dump(
                        {
                            "memory_schema_version": version, "skillset": "art",
                            "memory_version": 1, "claims": [],
                        },
                        sort_keys=False,
                    ),
                    encoding="utf-8",
                )
                before = store.read_bytes()
                added = run_tool("add", "--domain", "art", "--json", "{}", memory=self.tmp)
                self.assertEqual(added.returncode, 1)
                self.assertIn(expected, added.stderr)
                linked = run_tool(
                    "link-evidence", "--domain", "art", "--claim", "TST_MEM_001",
                    "--events", "TST_EV_0001", memory=self.tmp,
                )
                self.assertEqual(linked.returncode, 1)
                self.assertIn(expected, linked.stderr)
                self.assertEqual(store.read_bytes(), before)

    def test_an_already_invalid_store_must_be_repaired_first(self) -> None:
        self.write([base_claim(), base_claim()])
        before = self.store()
        self.assert_refused(
            self.tool("add", "--json", self.new_claim()), before, "already invalid",
        )

    def test_a_held_lock_refuses_the_write_and_nothing_is_left_behind(self) -> None:
        self.write([base_claim()])
        before = self.store()
        lock = self.tmp / ".locks" / f"{self.DOMAIN}.lock"
        lock.parent.mkdir()
        lock.write_text("{}", encoding="utf-8")
        result = self.tool("add", "--json", self.new_claim(scope="other_contracts"))
        self.assertEqual(result.returncode, 1)
        self.assertIn("another memory.py write", result.stderr)
        self.assertEqual(self.store(), before)
        lock.unlink()
        self.assertEqual(
            self.tool("add", "--json", self.new_claim(scope="other_contracts")).returncode, 0,
        )
        self.assertFalse(lock.exists())
        self.assertEqual(sorted(p.name for p in self.domain.iterdir()), ["skill_memory.yaml"])

    def test_untouched_claims_keep_their_bytes_and_line_endings(self) -> None:
        """Re-pointed at `claims`. R2.0 calls byte-splicing implementation rather
        than contract; it survives because one key name was its whole cost."""
        first = base_claim()
        second = base_claim(
            id="SE_MEM_01M55WJVKR0QB8C42T4SSG2KW2", scope="other_contracts",
        )
        hand = yaml.safe_dump(
            v3_store([first, second], skillset=self.DOMAIN, memory_version=4),
            sort_keys=False, width=40,
        ).replace("\n", "\r\n")
        (self.domain / "skill_memory.yaml").write_bytes(hand.encode("utf-8"))
        result = self.tool("update", "--id", second["id"], "--json", '{"confidence": "strong"}')
        self.assertEqual(result.returncode, 0, result.stderr)
        after = self.store().decode("utf-8")
        untouched = hand.split(f"- id: {second['id']}")[0].replace(
            "memory_version: 4", "memory_version: 5",
        )
        self.assertTrue(after.startswith(untouched), "an untouched claim was rewritten")
        self.assertNotIn("\n", after.replace("\r\n", ""), "line endings were converted")
        self.assertEqual(self.claims()[second["id"]]["confidence"], "strong")

    def test_long_literal_json_is_parsed_not_probed_as_a_path(self) -> None:
        # Regression: a literal JSON argument longer than a filename may be was
        # stat()ed as a path first, which raises ENAMETOOLONG on Linux.
        self.write([])
        long_claim = self.new_claim(
            envelope={
                "holds_in": ["overload pairs where only const-ness differs"],
                "not_shown_in": ["value-returning accessors"],
                "conditions": ["a reviewed call site"] * 40,
            },
        )
        self.assertGreater(len(long_claim.encode("utf-8")), 1024)
        result = self.tool("add", "--json", long_claim)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_json_argument_may_still_name_a_file(self) -> None:
        self.write([])
        path = self.tmp / "claim.json"
        path.write_bytes(self.new_claim().encode("utf-8"))
        result = self.tool("add", "--json", str(path))
        self.assertEqual(result.returncode, 0, result.stderr)
        missing = self.tool("add", "--json", str(self.tmp / "missing.json"))
        self.assertEqual(missing.returncode, 1)
        self.assertIn("literal JSON object or a readable JSON file", missing.stderr)
        scalar = self.tool("add", "--json", "[1, 2]")
        self.assertEqual(scalar.returncode, 1)
        self.assertIn("must be a JSON object", scalar.stderr)

    def test_literal_json_never_touches_the_filesystem(self) -> None:
        from unittest import mock

        def refuse(*_args: object, **_kwargs: object) -> None:
            raise AssertionError("a literal JSON argument was treated as a path")

        with mock.patch.object(Path, "is_file", refuse), mock.patch.object(Path, "read_text", refuse), \
                mock.patch.object(Path, "stat", refuse):
            self.assertEqual(memory_tool.read_json_argument('{"a": 1}'), {"a": 1})
            self.assertEqual(memory_tool.read_json_argument('  \n [1, 2]'), [1, 2])
            self.assertEqual(memory_tool.read_json_argument("{" + '"k": "' + "x" * 5000 + '"}'), {"k": "x" * 5000})
            with self.assertRaisesRegex(memory_tool.MemoryError_, "not valid JSON"):
                memory_tool.read_json_argument("{not json")

    def test_show_prints_one_claim_and_fails_honestly_on_a_missing_one(self) -> None:
        claim = base_claim()
        self.write([claim])
        shown = self.tool("show", "--id", claim["id"])
        self.assertEqual(shown.returncode, 0, shown.stderr)
        self.assertEqual(yaml.safe_load(shown.stdout)["id"], claim["id"])
        missing = self.tool("show", "--id", memory_tool.new_claim_id(self.DOMAIN))
        self.assertEqual(missing.returncode, 1)
        self.assertIn("no claim", missing.stderr)

    def test_a_write_needs_exactly_one_domain(self) -> None:
        self.write([])
        result = run_tool("add", "--json", self.new_claim(), memory=self.tmp)
        self.assertEqual(result.returncode, 1)
        self.assertIn("requires exactly one --domain", result.stderr)
        linked = run_tool(
            "link-evidence", "--claim", "SE_MEM_01M55WJVKRKX5ZNTWCWARDTT8N",
            "--events", "SE_EV_0001", memory=self.tmp,
        )
        self.assertEqual(linked.returncode, 1)
        self.assertIn("requires exactly one --domain", linked.stderr)


class V3LinkEvidence(V3WriteFixture):
    """R2.5 A3.5 / A8.3 / A8.4: evidence reaches a claim through one bounded
    command. One to three representative events, no count field, no backlog -
    the number of linked ids is never a measure of support."""

    def events(self, *ids: str) -> list[dict]:
        return [dict(V3_VALID_EVENT, event_id=event_id) for event_id in ids]

    def link(
        self, claim_id: str, events: list[str], *flags: str,
    ) -> subprocess.CompletedProcess[str]:
        return self.tool(
            "link-evidence", "--claim", claim_id, "--events", ",".join(events), *flags,
        )

    def test_link_evidence_accepts_three_ids_and_confirms_the_write(self) -> None:
        claim = base_claim()
        self.write([claim], self.events("SE_EV_0001", "SE_EV_0005", "SE_EV_0006"))
        result = self.link(claim["id"], ["SE_EV_0001", "SE_EV_0005", "SE_EV_0006"])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        stored = self.claims()[claim["id"]]
        self.assertEqual(stored["evidence"], ["SE_EV_0001", "SE_EV_0005", "SE_EV_0006"])
        self.assertEqual(str(stored["last_verified"]), date.today().isoformat())
        self.assertEqual(self.version(), 2)
        self.assertIn(claim["id"], result.stdout)
        self.assertIn("confirmed on readback", result.stdout)

    def test_link_evidence_refuses_a_fourth_id(self) -> None:
        """Criterion 15: the cap is closed at three at the write seam, so a
        fourth id never reaches the store to be caught by S9 after the fact."""
        claim = base_claim()
        self.write([claim], self.events("SE_EV_0001", "SE_EV_0005", "SE_EV_0006", "SE_EV_0007"))
        before = self.store()
        result = self.link(
            claim["id"], ["SE_EV_0001", "SE_EV_0005", "SE_EV_0006", "SE_EV_0007"],
        )
        self.assert_refused(result, before, "capped at 3")

    def test_link_evidence_refuses_an_invalid_event(self) -> None:
        claim = base_claim()
        self.write([claim], [V3_VALID_EVENT, V3_INVALID_EVENT])
        before = self.store()
        result = self.link(claim["id"], ["SE_EV_0002"])
        self.assert_refused(result, before, "never evidence about a capability")
        self.assertIn("invalid event", result.stderr)

    def test_link_evidence_refuses_a_correction_event(self) -> None:
        claim = base_claim()
        self.write([claim], [V3_VALID_EVENT, V3_METADATA_CORRECTION])
        before = self.store()
        result = self.link(claim["id"], ["SE_EV_0003"])
        self.assert_refused(result, before, "correction is not capability evidence")

    def test_link_evidence_refuses_a_quarantined_event(self) -> None:
        claim = base_claim()
        self.write([claim], [V3_VALID_EVENT, V3_EVIDENCE_CORRECTION])
        before = self.store()
        result = self.link(claim["id"], ["SE_EV_0001"])
        self.assert_refused(result, before, "quarantined event")

    def test_link_evidence_refuses_to_drop_a_cited_event_without_replace(self) -> None:
        """`--events` is the claim's final evidence, which reads like "add these".
        It must not lose an id silently."""
        claim = base_claim(evidence=["SE_EV_0001"])
        self.write([claim], self.events("SE_EV_0001", "SE_EV_0005"))
        before = self.store()
        result = self.link(claim["id"], ["SE_EV_0005"])
        self.assert_refused(result, before, "SE_EV_0001")
        self.assertIn("--replace", result.stderr)

    def test_link_evidence_drops_and_reports_the_loss_with_replace(self) -> None:
        """Dropping a citation is sometimes right, so `--replace` turns the
        refusal into a confirmation - and the loss is reported, not swallowed."""
        claim = base_claim(evidence=["SE_EV_0001"])
        self.write([claim], self.events("SE_EV_0001", "SE_EV_0005"))
        result = self.link(claim["id"], ["SE_EV_0005"], "--replace")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.claims()[claim["id"]]["evidence"], ["SE_EV_0005"])
        self.assertIn("dropped", result.stdout)
        self.assertIn("SE_EV_0001", result.stdout)

    def test_link_evidence_keeps_everything_that_is_still_named(self) -> None:
        """The safe path: name the whole final list and nothing is refused or
        needs confirming."""
        claim = base_claim(evidence=["SE_EV_0001"])
        self.write([claim], self.events("SE_EV_0001", "SE_EV_0005", "SE_EV_0006"))
        result = self.link(claim["id"], ["SE_EV_0001", "SE_EV_0005", "SE_EV_0006"])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(
            self.claims()[claim["id"]]["evidence"],
            ["SE_EV_0001", "SE_EV_0005", "SE_EV_0006"],
        )
        self.assertNotIn("dropped", result.stdout)

    def test_link_evidence_writes_no_count(self) -> None:
        claim = base_claim()
        self.write([claim], self.events("SE_EV_0001", "SE_EV_0005"))
        result = self.link(claim["id"], ["SE_EV_0001", "SE_EV_0005"])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("evidence_count", self.claims()[claim["id"]])
        self.assertNotIn("evidence_count", self.tool("link-evidence", "--help").stdout)
        # The writer never assigns a count or confidence key. Checked on the
        # syntax tree so a docstring explaining the refusal cannot trip it.
        tree = ast.parse(TOOL.read_text(encoding="utf-8"))
        writer = next(
            node for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "link_evidence"
        )
        for node in ast.walk(writer):
            if (
                isinstance(node, ast.Subscript)
                and isinstance(node.ctx, ast.Store)
                and isinstance(node.slice, ast.Constant)
                and node.slice.value in {"evidence_count", "confidence"}
            ):
                self.fail(f"link_evidence assigns {node.slice.value}")

    def test_link_evidence_never_changes_or_prints_a_confidence(self) -> None:
        claim = base_claim(confidence="provisional")
        self.write([claim], self.events("SE_EV_0001", "SE_EV_0005"))
        result = self.link(claim["id"], ["SE_EV_0001", "SE_EV_0005"])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.claims()[claim["id"]]["confidence"], "provisional")
        for value in memory_tool.CONFIDENCE_VALUES:
            self.assertNotIn(
                value, result.stdout + result.stderr,
                f"link-evidence printed confidence '{value}'",
            )

    def test_compact_is_gone_and_link_evidence_took_its_place(self) -> None:
        """Criterion 5: the compaction command is removed rather than kept
        beside its replacement."""
        help_text = run_tool("--help").stdout
        self.assertIn("link-evidence", help_text)
        self.assertNotIn("compact", help_text)
        self.assertEqual(
            run_tool("compact", "--domain", self.DOMAIN, memory=self.tmp).returncode, 2,
        )
        source = TOOL.read_text(encoding="utf-8")
        for token in ('"compact"', "'compact'", "cmd_compact", "compact_link"):
            self.assertNotIn(token, source, f"{token} survived T06")

    def test_uncited_events_are_reported_as_informational_not_a_backlog(self) -> None:
        """A8.4: with the cap at three, the uncited list is a view of History no
        claim mentions - not a queue to drain, and not a measure of support."""
        claim = base_claim(evidence=["SE_EV_0001"])
        self.write([claim], self.events("SE_EV_0001", "SE_EV_0005", "SE_EV_0006"))
        result = self.tool("review")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        line = next(
            (line for line in result.stdout.splitlines() if "valid event(s)" in line),
            "",
        )
        self.assertTrue(line, result.stdout)
        self.assertIn("SE_EV_0005", line)
        self.assertIn("SE_EV_0006", line)
        self.assertNotIn("SE_EV_0001", line)
        self.assertIn("informational", line)
        self.assertIn("not a backlog", line)
        self.assertIn("not a measure", line)


class V3RetrievalFixture(V3WriteFixture):
    """A disposable v3 store placed claim by claim, for reading rather than writing.

    The claims go in through the fixture's file writer rather than through
    `add`, because retrieval reads whatever parses and never validates: a
    ranking test needs to place exactly the claims it means to rank, in the
    order it means to place them, without admission deciding anything first.
    """

    def claim_id(self, suffix: str) -> str:
        """A distinct, structurally valid claim id.

        The suffix is a spelling device for the test author. Nothing in
        retrieval reads any part of an id except by exact equality, which is
        what `test_ids_are_matched_by_equality_and_nothing_else` holds.
        """
        return "SE_MEM_" + suffix.upper().rjust(memory_tool.CLAIM_ID_TAIL_LENGTH, "0")

    def claim(self, suffix: str, **changes: object) -> dict:
        return base_claim(id=self.claim_id(suffix), **changes)

    def contradiction_pair(self) -> list[dict]:
        """The §6.3 shape: two current claims, symmetric `contradicts`, neither
        demoted, held together by the marker alone."""
        first, second = self.claim_id("A"), self.claim_id("B")
        return [
            base_claim(
                id=first,
                claim="Compressing resolution steps before adding consequence keeps a "
                      "subsystem teachable.",
                scope="subsystem_pacing",
                retrieval_cues=["compress before consequence"],
                contradicts=[second],
            ),
            base_claim(
                id=second,
                claim="Consequence layers carry attention further than step count does.",
                scope="subsystem_pacing",
                confidence="provisional",
                retrieval_cues=["consequence over step count"],
                contradicts=[first],
            ),
        ]

    def query(self, *args: object) -> subprocess.CompletedProcess[str]:
        result = self.tool("query", *args)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def receipt(self, result: subprocess.CompletedProcess[str]) -> str:
        lines = [l for l in result.stdout.splitlines() if l.startswith("retrieved:")]
        self.assertEqual(len(lines), 1, f"expected exactly one receipt:\n{result.stdout}")
        return lines[0]

    def returned(self, result: subprocess.CompletedProcess[str]) -> list[str]:
        """The ids the receipt names as the bounded, ranked result.

        A contradiction counterpart is not one of these: it arrives in the
        receipt's own segment precisely so it cannot be mistaken for a claim
        that spent one of the caller's slots.
        """
        body = self.receipt(result).split("retrieved: ", 1)[1].split(";", 1)[0].strip()
        return [] if body == "(none)" else [part.strip() for part in body.split(",")]

    def counterparts(self, result: subprocess.CompletedProcess[str]) -> list[str]:
        receipt = self.receipt(result)
        if ";" not in receipt:
            return []
        segment = receipt.split(":")[-1]
        return [part.strip() for part in segment.split(",")]


class RetrievalContract(V3RetrievalFixture):
    """Retrieval is bounded, and it reports what it actually returned.

    Re-pointed at schema 3 by T07, and since T21 there is nothing else to
    point at: `score_entry` and `query_store` went with the legacy reader, so
    retrieval has one ranking path. What carried over from the entry-shaped
    version of this class is the contract, not the field names.
    """

    def test_query_returns_only_matching_claims(self) -> None:
        self.write([
            self.claim("A", scope="hands", retrieval_cues=["hand", "grip"]),
            self.claim("B", scope="landscape", retrieval_cues=["terrain"]),
        ])
        result = self.query("--cues", "grip")
        self.assertEqual(self.returned(result), [self.claim_id("A")])
        self.assertNotIn(self.claim_id("B"), result.stdout)

    def test_query_respects_the_limit(self) -> None:
        self.write([
            self.claim(f"{n:02d}", scope=f"topic_{n}", retrieval_cues=["shared cue"])
            for n in range(1, 6)
        ])
        result = self.query("--cues", "shared cue", "--limit", "2")
        self.assertEqual(len(self.returned(result)), 2)

    def test_a_retired_claim_is_absent_from_the_store(self) -> None:
        """What survives of `test_resolved_entries_stop_being_retrieved`.

        Legacy retrieval filtered a `resolved` entry out of a store that still
        held it. Schema 3 has no retrievability status, because retirement
        physically removes the claim (R2.5 §1.4): the guarantee moved to the
        writer, and retrieval simply cannot see what is not there.
        """
        self.write([])
        kept = self.add(scope="kept_topic", retrieval_cues=["hand"])
        gone = self.add(scope="gone_topic", retrieval_cues=["hand"])
        retired = self.tool("retire", "--id", gone, "--reason", "replaced by a wider claim")
        self.assertEqual(retired.returncode, 0, retired.stdout + retired.stderr)
        result = self.query("--cues", "hand")
        self.assertEqual(self.returned(result), [kept])
        self.assertNotIn(gone, result.stdout)

    def test_query_reports_an_empty_retrieval_honestly(self) -> None:
        self.write([self.claim("A", retrieval_cues=["hand"])])
        result = self.query("--cues", "nothing in this store")
        self.assertEqual(self.receipt(result), "retrieved: (none)")


class V3Retrieval(V3RetrievalFixture):
    """R2.5 §9.2: what ranks above what, what always comes back in pairs, and
    what an unanswerable request is allowed to return."""

    CARD = "PAT_state_the_lifetime_contract_at_the_interface"

    def test_every_result_set_is_bounded_by_the_limit(self) -> None:
        """Criterion 29, across every request shape including the empty one."""
        self.write([
            self.claim(f"{n:02d}", scope="lifetime_contracts", retrieval_cues=["shared cue"])
            for n in range(1, 13)
        ])
        requests = (
            (),
            ("--cues", "shared cue"),
            ("--scope", "lifetime_contracts"),
            ("--scope", "lifetime_contracts", "--cues", "shared cue"),
            ("--canon", self.CARD),
        )
        for limit in (0, 1, 3, 5):
            for request in requests:
                with self.subTest(limit=limit, request=request):
                    result = self.query(*request, "--limit", str(limit))
                    self.assertLessEqual(len(self.returned(result)), limit)

    def test_an_exact_scope_match_outranks_a_cue_match(self) -> None:
        self.write([
            self.claim("A", scope="cue_only_topic", retrieval_cues=["shared cue"]),
            self.claim("B", scope="ranked_topic", retrieval_cues=["shared cue"]),
        ])
        result = self.query("--scope", "ranked_topic", "--cues", "shared cue")
        self.assertEqual(self.returned(result), [self.claim_id("B"), self.claim_id("A")])

    def test_canon_id_match_outranks_a_cue_match(self) -> None:
        self.write([
            self.claim("A", scope="cue_only_topic", retrieval_cues=["shared cue"]),
            self.claim("B", scope="canon_topic", retrieval_cues=["shared cue"], canon=[self.CARD]),
        ])
        result = self.query("--canon", self.CARD, "--cues", "shared cue")
        self.assertEqual(self.returned(result), [self.claim_id("B"), self.claim_id("A")])

    def test_a_cue_matches_the_claim_text_as_well_as_the_cues(self) -> None:
        self.write([self.claim("A", retrieval_cues=["nothing like the request"])])
        result = self.query("--cues", "const safety")
        self.assertEqual(self.returned(result), [self.claim_id("A")])

    def test_a_reach_claim_with_a_matching_canon_id_is_returned(self) -> None:
        """Criterion 13, second half. A reach claim may carry a Canon link and
        be found by it; what it may never do is route, which is held by the
        caller supplying the ids rather than Memory proposing them."""
        self.write([self.claim(
            "A",
            claim_class="reach",
            claim_kind="stochastic",
            confidence="provisional",
            delta={"kinds": ["posture"], "statement": "Decline to claim demonstrated capability."},
            canon=[self.CARD],
        )])
        result = self.query("--canon", self.CARD)
        self.assertEqual(self.returned(result), [self.claim_id("A")])

    def test_a_canon_id_the_caller_did_not_supply_matches_nothing(self) -> None:
        self.write([self.claim("A", canon=[self.CARD])])
        result = self.query("--canon", "PAT_some_other_card")
        self.assertEqual(self.returned(result), [])

    def test_the_output_names_no_canon_object(self) -> None:
        """Criterion 9, from the outside. Canon is already selected when
        retrieval runs, so printing the links of everything returned would hand
        the caller a list of Canon objects that Memory assembled - the backwards
        authority §9.2 forbids. Nothing is lost: the caller supplied the ids."""
        self.write([self.claim("A", canon=[self.CARD])])
        result = self.query("--canon", self.CARD)
        self.assertEqual(self.returned(result), [self.claim_id("A")])
        self.assertNotIn(self.CARD, result.stdout)

    def test_the_contradiction_fixture_is_a_store_the_validator_accepts(self) -> None:
        """Retrieval reads whatever parses, so the co-return tests would pass
        just as happily over a store that could never exist. This is what says
        they are about a real one."""
        self.write(self.contradiction_pair())
        result = self.validate_tool()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_a_contradicted_claim_arrives_with_its_counterpart(self) -> None:
        self.write(self.contradiction_pair())
        result = self.query("--cues", "compress before consequence")
        self.assertEqual(self.returned(result), [self.claim_id("A")])
        self.assertEqual(
            self.counterparts(result), [f"{self.claim_id('B')} with {self.claim_id('A')}"],
        )
        self.assertIn(self.claim_id("B"), result.stdout)

    def test_a_contradiction_counterpart_does_not_consume_the_limit(self) -> None:
        self.write(self.contradiction_pair() + [base_claim(
            id=self.claim_id("C"),
            claim="Running a subsystem once before tuning it tells you which half is slow.",
            scope="subsystem_pacing",
            retrieval_cues=["compress before consequence"],
        )])
        result = self.query("--cues", "compress before consequence", "--limit", "2")
        self.assertEqual(self.returned(result), [self.claim_id("A"), self.claim_id("C")])
        self.assertEqual(
            self.counterparts(result), [f"{self.claim_id('B')} with {self.claim_id('A')}"],
        )

    def test_a_limit_of_one_cannot_expand_into_a_contradiction_chain(self) -> None:
        """The T07 defect, as a regression.

        Co-return originally followed the whole contradiction-connected
        component, so a chain of 10, 100 or 1,000 claims came back entire from
        `--limit 1` - bounded by the store rather than by the request, which is
        the store dump R2.5 §9.2 forbids outright. One ranked claim plus its
        one direct counterpart is the whole of the answer, at every length.
        """
        for length in (10, 100, 1000):
            with self.subTest(length=length):
                ids, claims = contradiction_chain(length)
                self.write(claims)
                result = self.query("--cues", "shared cue", "--limit", "1")
                self.assertEqual(self.returned(result), [ids[0]])
                self.assertEqual(
                    self.counterparts(result), [f"{ids[1]} with {ids[0]}"],
                )
                self.assertEqual(
                    [claim_id for claim_id in ids if claim_id in result.stdout],
                    ids[:2],
                    "retrieval expanded past the ranked claim and its counterpart",
                )

    def test_expansion_is_bounded_by_the_request_at_every_limit(self) -> None:
        """The general form of the bound: at most one counterpart per ranked
        claim, so nothing a query returns exceeds twice what was asked for,
        whatever the store's contradiction structure looks like."""
        ids, claims = contradiction_chain(100)
        self.write(claims)
        for limit in (0, 1, 3, 5):
            with self.subTest(limit=limit):
                result = self.query("--cues", "shared cue", "--limit", str(limit))
                returned = self.returned(result)
                self.assertLessEqual(len(returned), limit)
                self.assertLessEqual(
                    len([claim_id for claim_id in ids if claim_id in result.stdout]),
                    2 * limit,
                )

    def test_a_store_that_breaks_the_pair_rule_still_cannot_dump(self) -> None:
        """The bound belongs to retrieval, not to the store it happens to read.

        A claim naming many counterparts is invalid (S9) and the validator is
        what keeps it out of a live store. Retrieval reads whatever parses, so
        it attaches the one counterpart a valid claim has and stops - a query
        cannot be made unbounded by handing it a malformed file.
        """
        ids = [self.claim_id(format(index, "x")) for index in range(40)]
        self.write([
            base_claim(
                id=claim_id,
                scope="disputed_topic",
                retrieval_cues=["shared cue"],
                contradicts=ids[1:] if position == 0 else [ids[0]],
            )
            for position, claim_id in enumerate(ids)
        ])
        result = self.query("--cues", "shared cue", "--limit", "1")
        self.assertEqual(self.returned(result), [ids[0]])
        self.assertEqual(self.counterparts(result), [f"{ids[1]} with {ids[0]}"])
        self.assertEqual(
            [claim_id for claim_id in ids if claim_id in result.stdout], ids[:2],
        )

    def test_a_counterpart_that_is_itself_a_hit_is_not_relabelled(self) -> None:
        """Both sides matched and both fit, so neither arrived as the other's
        passenger and the receipt says so."""
        self.write(self.contradiction_pair())
        result = self.query("--scope", "subsystem_pacing")
        self.assertEqual(self.returned(result), [self.claim_id("A"), self.claim_id("B")])
        self.assertEqual(self.counterparts(result), [])

    def test_revalidate_after_does_not_change_retrieval(self) -> None:
        """Criterion 19. Past due is T08's listing and nothing else: no
        suppression, no penalty, no reordering, no confidence touched."""
        current = [
            self.claim("A", scope="first_topic", retrieval_cues=["shared cue"]),
            self.claim("B", scope="second_topic", confidence="strong", retrieval_cues=["shared cue"]),
        ]
        self.write(current)
        before = self.query("--cues", "shared cue").stdout
        self.write([
            dict(claim, last_verified="2024-01-01", revalidate_after="2024-06-01")
            for claim in current
        ])
        self.assertEqual(self.query("--cues", "shared cue").stdout, before)

    def test_confidence_ranks_last_and_the_store_is_not_written(self) -> None:
        """F3. Confidence breaks a tie between equally specific matches and
        loses to every signal above it, and ranking leaves the file alone."""
        self.write([
            self.claim("A", scope="cue_only_topic", confidence="strong", retrieval_cues=["shared cue"]),
            self.claim("B", scope="ranked_topic", confidence="provisional", retrieval_cues=["shared cue"]),
            self.claim("C", scope="other_topic", confidence="provisional", retrieval_cues=["shared cue"]),
        ])
        before = self.store()
        result = self.query("--scope", "ranked_topic", "--cues", "shared cue")
        self.assertEqual(
            self.returned(result),
            [self.claim_id("B"), self.claim_id("A"), self.claim_id("C")],
        )
        self.assertEqual(self.store(), before)

    def test_ids_are_matched_by_equality_and_nothing_else(self) -> None:
        """Criterion 7l, from the outside. Two claims that differ only in their
        ids rank identically, so what orders them is the store, not the id. An
        implementation that sorted by id would put the second one first."""
        self.write([
            self.claim("Z", scope="first_topic", retrieval_cues=["shared cue"]),
            self.claim("A", scope="second_topic", retrieval_cues=["shared cue"]),
        ])
        result = self.query("--cues", "shared cue")
        self.assertEqual(self.returned(result), [self.claim_id("Z"), self.claim_id("A")])

    def test_a_missing_root_a_missing_domain_or_an_empty_store_retrieves_nothing(self) -> None:
        """Criterion 32. Retrieval fails open with an honest receipt: nothing in
        PASS is allowed to stop because Memory is absent."""
        self.write([])
        cases = {
            "empty store": (self.tmp, ("--domain", self.DOMAIN)),
            "missing domain": (self.tmp, ("--domain", "art")),
            "missing root": (self.tmp / "no-such-root", ()),
        }
        for label, (memory, args) in cases.items():
            with self.subTest(case=label):
                result = run_tool("query", "--cues", "hand", *args, memory=memory)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual(self.receipt(result), "retrieved: (none)")

    def test_exactly_one_receipt_is_printed(self) -> None:
        """Criterion 33, in one format, over every shape of answer."""
        self.write(self.contradiction_pair())
        for request in (
            ("--cues", "compress before consequence"),
            ("--cues", "nothing in this store"),
            ("--scope", "subsystem_pacing"),
            ("--canon", self.CARD),
            (),
        ):
            with self.subTest(request=request):
                result = self.query(*request)
                receipts = [
                    line for line in result.stdout.splitlines()
                    if line.startswith("retrieved:")
                ]
                self.assertEqual(len(receipts), 1, result.stdout)

    def test_empty_query_is_reported_as_not_a_strategy(self) -> None:
        """An empty scope with no cues and no Canon ids asks nothing, so it is
        answered as nothing and said out loud. The alternative - returning the
        first N claims - is a store dump wearing a limit."""
        self.write([self.claim("A"), self.claim("B", scope="other_topic")])
        result = self.query()
        self.assertEqual(self.returned(result), [])
        self.assertIn("not a retrieval strategy", result.stdout)
        self.assertNotIn(self.claim_id("A"), result.stdout)


class V3RetrievalSurface(unittest.TestCase):
    """What v3 retrieval is allowed to reach for: criteria 7l, 9 and F3 read off
    the syntax tree rather than the behavior.

    The same instrument `ClaimIdentity` uses on id generation, for the same
    reason. A denylist only catches the shapes somebody already thought of, and
    scanning raw text would match the comments that explain what retrieval
    refuses to do.
    """

    # The ranking and selection path, where an id may only be compared. Display
    # is surveyed separately and less strictly, because §9.2 permits reading an
    # id for display and whitespace-normalising prose needs `.split`.
    RANKING_FUNCTIONS = ("score_claim", "query_v3_store")
    RETRIEVAL_FUNCTIONS = RANKING_FUNCTIONS + ("print_v3_claim",)

    # Everything v3 retrieval may load. Anything new fails here until somebody
    # justifies it in this list - which is the point, because id parsing, Canon
    # enumeration and a confidence write all have to reach for something.
    RETRIEVAL_ALLOWED_NAMES = frozenset({
        "load_memory", "score_claim",      # reading the store, scoring one claim
        "CONFIDENCE_RANK",                 # confidence, read last and read only
        "Any", "Path", "bool", "dict", "isinstance", "list", "print", "set",
        "str", "sum", "tuple",             # builtins and typing
    })

    # Every method v3 retrieval calls, on anything. Flat rather than dotted,
    # because the interesting reach is `.split` on an id however it was spelled
    # - `str(claim.get("id")).split(...)` roots at a call, not at a name.
    RETRIEVAL_ALLOWED_ATTRIBUTES = frozenset({
        "get",                 # claim fields, and the exact-equality counterpart lookup
        "sort",                # the rank tuple; nothing sorts on a claim or an id
        "append", "add",       # the co-return attach, over local collections
        "lower", "join",       # case-folding and assembling the cue haystack
    })

    def retrieval_functions(self, names: tuple[str, ...]) -> list[ast.FunctionDef]:
        """The named v3 retrieval functions, with their type annotations stripped.

        An annotation names `int` and `str` without using them, and leaving it
        in the tree would force both onto the allowlist - where `int` is one of
        the few names that would actually betray an id being parsed.
        """
        tree = ast.parse((ROOT / "PASS/tools/memory.py").read_text(encoding="utf-8"))
        functions = [
            node for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name in names
        ]
        self.assertEqual(
            sorted(f.name for f in functions), sorted(names),
            "v3 retrieval is not where this test expects it",
        )
        for function in functions:
            function.returns = None
            for argument in function.args.args:
                argument.annotation = None
            for node in ast.walk(function):
                if isinstance(node, ast.AnnAssign):
                    node.annotation = ast.Constant(value=None)
        return functions

    def test_retrieval_reaches_for_nothing_that_could_parse_an_id(self) -> None:
        names: set[str] = set()
        attributes: set[str] = set()
        for function in self.retrieval_functions(self.RANKING_FUNCTIONS):
            local = {argument.arg for argument in function.args.args}
            for node in ast.walk(function):
                if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                    local.add(node.id)
                elif isinstance(node, ast.comprehension) and isinstance(node.target, ast.Name):
                    local.add(node.target.id)
                elif isinstance(node, (ast.FunctionDef, ast.Lambda)):
                    local.update(argument.arg for argument in node.args.args)
            for node in ast.walk(function):
                if isinstance(node, ast.Attribute):
                    attributes.add(node.attr)
                elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                    if node.id not in local:
                        names.add(node.id)
        unexpected = sorted(
            (names - self.RETRIEVAL_ALLOWED_NAMES)
            | (attributes - self.RETRIEVAL_ALLOWED_ATTRIBUTES)
        )
        self.assertEqual(
            unexpected, [],
            "v3 retrieval reached for something new; if it does not parse an id, "
            "enumerate Canon, or write confidence, add it to the allowlists above "
            f"deliberately: {unexpected}",
        )

    def test_retrieval_assigns_into_nothing_it_was_given(self) -> None:
        """F3 structurally: ranking cannot write `confidence`, or any other
        field, because it never stores into a subscript or an attribute - which
        covers the augmented forms too, since their target is also a store. A
        mutating *method* on a claim would be caught by the allowlist above
        instead, and that a query leaves the file byte-identical is held
        behaviorally by `V3Retrieval`.
        """
        for function in self.retrieval_functions(self.RETRIEVAL_FUNCTIONS):
            for node in ast.walk(function):
                if isinstance(node, (ast.Subscript, ast.Attribute)):
                    self.assertNotIsInstance(
                        node.ctx, ast.Store, f"{function.name} assigns into a loaded object",
                    )

    def test_no_path_enumerates_canon_links(self) -> None:
        """Criterion 9. Every read of a claim's `canon` key anywhere under
        `PASS/`, with the reason it is allowed to exist. A new reader fails
        here, which is where somebody has to say out loud whether Memory just
        started selecting Canon.
        """
        allowed = {
            # S9: the member cap. Reads the list's length, never its members.
            "validate_claim",
            # I1/I2: member shape, and resolution against a Library that is
            # already there. Validation, not selection, and it proposes nothing.
            "validate_v3_references",
            # Exact equality against ids Canon selection already pinned and the
            # caller supplied. The only reader on the retrieval path.
            "score_claim",
        }
        readers: set[str] = set()
        sources = [
            path for path in (ROOT / "PASS").rglob("*.py")
            if "__pycache__" not in path.parts
        ]
        self.assertIn(ROOT / "PASS/tools/memory.py", sources)
        for source in sources:
            tree = ast.parse(source.read_text(encoding="utf-8"))
            for function in ast.walk(tree):
                if not isinstance(function, ast.FunctionDef):
                    continue
                for node in ast.walk(function):
                    reads_canon = (
                        isinstance(node, ast.Call)
                        and isinstance(node.func, ast.Attribute)
                        and node.func.attr == "get"
                        and any(
                            isinstance(argument, ast.Constant) and argument.value == "canon"
                            for argument in node.args
                        )
                    ) or (
                        isinstance(node, ast.Subscript)
                        and isinstance(node.slice, ast.Constant)
                        and node.slice.value == "canon"
                    )
                    if reads_canon:
                        readers.add(function.name)
        self.assertEqual(readers, allowed)


class V3WriterSurface(unittest.TestCase):
    """What the write surface no longer offers, and who else may write."""

    def test_the_sequential_claim_allocator_is_gone(self) -> None:
        """T01 added the vNext mechanism beside the old one; T05 removes the old
        one rather than porting it. It derived the next number from the highest
        *surviving* entry, so the first `add` after a retirement reissued the
        retired id. Training History keeps its own sequence: event ids are
        append-only and nothing removes an event, so `next_event_id` is sound and
        R2.5 §8.4 leaves it alone."""
        self.assertFalse(hasattr(memory_tool, "next_entry_id"))
        self.assertTrue(hasattr(memory_tool, "next_event_id"))
        source = TOOL.read_text(encoding="utf-8")
        for gone in ("next_entry_id", "add_entry", "update_entry", "supersede_entry"):
            self.assertNotIn(gone, source, f"{gone} survived T05")

    def test_training_history_event_ids_are_untouched(self) -> None:
        events = [{"event_id": "ART_EV_0001"}, {"event_id": "ART_EV_0002"}]
        self.assertEqual(memory_tool.next_event_id(events, "art"), "ART_EV_0003")

    def test_supersede_is_gone_from_the_help_and_the_source(self) -> None:
        """Criterion 11. A replacement is `retire` then `add`; what survives of
        the word is Training History correction vocabulary, which R2.5 §8.4
        leaves exactly as it is."""
        help_text = run_tool("--help").stdout
        self.assertNotIn("supersede", help_text)
        self.assertIn("`retire` then", help_text + run_tool("retire", "--help").stdout)
        self.assertEqual(run_tool("supersede", "--id", "x").returncode, 2)
        source = TOOL.read_text(encoding="utf-8")
        self.assertNotIn("superseded_by", source)
        self.assertEqual(
            {match.group(0) for match in re.finditer(r"supersede[a-z_]*", source)},
            {"supersedes_events", "supersedes", "superseded"},
        )

    def test_there_is_no_delete_command(self) -> None:
        """`delete` is still not a command, because `retire` is: removal without
        a stated reason is what the old invariant was actually protecting
        against."""
        self.assertEqual(run_tool("delete", "--id", "x").returncode, 2)

    def test_only_the_memory_tool_writes_a_memory_file(self) -> None:
        """Criterion 36. Scanned as a syntax tree rather than as text, so a
        read-only mention of a store filename — the release gate's existence
        check, a docstring — does not read as a write."""
        writers = {"write_text", "write_bytes", "open", "replace", "copy", "copy2", "copyfile"}
        stores = ("skill_memory", "training_history", "MEMORY_STORE")
        offenders: list[str] = []
        for path in (ROOT / "PASS").rglob("*.py"):
            if "__pycache__" in path.parts or path.name == "memory.py":
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                name = node.func.attr if isinstance(node.func, ast.Attribute) else (
                    node.func.id if isinstance(node.func, ast.Name) else ""
                )
                if name not in writers:
                    continue
                rendered = ast.dump(node)
                if any(store in rendered for store in stores):
                    offenders.append(f"{path.relative_to(ROOT).as_posix()}:{node.lineno}")
        self.assertEqual(offenders, [], "something other than memory.py writes a Memory file")


class ClaimIdentity(unittest.TestCase):
    """Schema 3 claim identity: opaque, generated once, never reused.

    The legacy allocator derives the next number from the highest *surviving*
    entry, so once retirement deletes a claim it hands the same id out twice.
    A locally generated token needs no surviving state to be unique, which is
    why these tests care as much about what the generator does not read as
    about what it produces.
    """

    # Everything the generator and its helpers are allowed to reach for. An
    # allowlist rather than a banned-word list: a denylist only catches the
    # allocator shapes we thought of, and scanning raw text would match the
    # docstring that explains what the generator refuses to read. Anything new
    # appearing here fails until somebody justifies it in this list.
    GENERATION_ALLOWED_REFERENCES = frozenset({
        "CLAIM_DOMAIN_TOKENS", "CLAIM_DOMAIN_TOKENS.get",
        "CLAIM_ID_TAIL_LENGTH", "CROCKFORD_ALPHABET",
        "MemoryError_", "claim_domain_token", "_crockford",
        # the randomness, and the timestamp that only shapes the token
        "secrets.token_bytes", "time.time",
        # builtins
        "int", "int.from_bytes", "range", "str", "sorted", "len",
    })

    GENERATION_FUNCTIONS = ("claim_domain_token", "_crockford", "new_claim_id")

    def generation_references(self) -> set[str]:
        """Every non-local name the generator trio loads, as dotted paths.

        Built from the syntax tree rather than the text, so prose in a docstring
        cannot pass or fail this check.
        """
        tree = ast.parse((ROOT / "PASS/tools/memory.py").read_text(encoding="utf-8"))
        functions = [
            node for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name in self.GENERATION_FUNCTIONS
        ]
        self.assertEqual(
            sorted(f.name for f in functions), sorted(self.GENERATION_FUNCTIONS),
            "the claim id generator is not where this test expects it",
        )

        references: set[str] = set()
        for function in functions:
            local = {argument.arg for argument in function.args.args}
            for node in ast.walk(function):
                if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                    local.add(node.id)
                elif isinstance(node, ast.comprehension) and isinstance(node.target, ast.Name):
                    local.add(node.target.id)
            for node in ast.walk(function):
                if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
                    references.add(f"{node.value.id}.{node.attr}")
                elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                    if node.id not in local:
                        references.add(node.id)
        # An attribute access contributes its dotted path, not its root.
        return {
            reference for reference in references
            if not any(other.startswith(f"{reference}.") for other in references)
        }

    def test_generated_id_matches_the_locked_shape(self) -> None:
        claim_id = memory_tool.new_claim_id("software-engineering")
        self.assertRegex(claim_id, memory_tool.CLAIM_ID_RE)
        self.assertTrue(claim_id.startswith("SE_MEM_"), claim_id)
        self.assertEqual(len(claim_id.split("_MEM_")[1]), 26, claim_id)
        self.assertEqual(memory_tool.claim_id_problems(claim_id, "software-engineering"), [])

    def test_domain_token_comes_from_the_table_not_the_directory_name(self) -> None:
        # The case the table exists for: no string rule turns `game-design`
        # into `GD` and `art` into `ART` and `writing` into `WRI`.
        self.assertTrue(memory_tool.new_claim_id("game-design").startswith("GD_MEM_"))
        self.assertTrue(memory_tool.new_claim_id("art").startswith("ART_MEM_"))
        self.assertTrue(memory_tool.new_claim_id("writing").startswith("WRI_MEM_"))
        for domain, token in memory_tool.CLAIM_DOMAIN_TOKENS.items():
            with self.subTest(domain=domain):
                self.assertTrue(memory_tool.new_claim_id(domain).startswith(f"{token}_MEM_"))

    def test_unmapped_domain_is_an_error(self) -> None:
        with self.assertRaises(memory_tool.MemoryError_) as caught:
            memory_tool.new_claim_id("mathematics")
        self.assertIn("CLAIM_DOMAIN_TOKENS", str(caught.exception))

    def test_a_legacy_sequence_tail_is_rejected(self) -> None:
        for legacy in ("SE_MEM_104", "SE_MEM_001", "SE_MEM_46"):
            with self.subTest(id=legacy):
                self.assertTrue(memory_tool.claim_id_problems(legacy, "software-engineering"))

    def test_shape_alone_cannot_catch_a_legacy_id_padded_to_the_full_length(self) -> None:
        """Stated so the shape check is not mistaken for the no-legacy-id guarantee.

        Digits are Crockford base32 characters, so a sequence number padded to 26
        places is a structurally valid id. What actually stops a legacy id
        becoming a live claim id is the migration check that compares every
        emitted id against the real legacy entry ids; no regex can do it.
        """
        padded = "SE_MEM_" + "104".rjust(26, "0")
        self.assertEqual(memory_tool.claim_id_problems(padded, "software-engineering"), [])

    def test_a_foreign_domain_prefix_is_rejected(self) -> None:
        foreign = memory_tool.new_claim_id("game-design")
        self.assertTrue(memory_tool.claim_id_problems(foreign, "software-engineering"))
        self.assertEqual(memory_tool.claim_id_problems(foreign, "game-design"), [])

    def test_excluded_crockford_letters_are_rejected(self) -> None:
        for letter in "ILOU":
            tail = letter + "0" * 25
            with self.subTest(letter=letter):
                self.assertTrue(memory_tool.claim_id_problems(f"SE_MEM_{tail}", "software-engineering"))

    def test_a_malformed_id_is_rejected_rather_than_crashing(self) -> None:
        for bad in (None, "", 104, "SE_MEM_", "SE_MEM_" + "0" * 25, "SE_MEM_" + "0" * 27, "se_mem_" + "0" * 26):
            with self.subTest(id=bad):
                self.assertTrue(memory_tool.claim_id_problems(bad, "software-engineering"))

    def test_ten_thousand_ids_are_distinct(self) -> None:
        ids = [memory_tool.new_claim_id("writing") for _ in range(10_000)]
        self.assertEqual(len(set(ids)), 10_000)
        self.assertEqual(memory_tool.duplicate_claim_ids(ids), [])

    def test_duplicates_are_reported_within_and_across_stores(self) -> None:
        one = memory_tool.new_claim_id("art")
        two = memory_tool.new_claim_id("art")
        self.assertEqual(memory_tool.duplicate_claim_ids([one, two]), [])
        self.assertEqual(memory_tool.duplicate_claim_ids([one, two, one]), [one])
        # S5b is the same check over the ids of every store the caller could read.
        self.assertEqual(memory_tool.duplicate_claim_ids([one] + [two] + [one, two]), sorted([one, two]))

    def test_generation_reads_no_allocator_counter_or_identity(self) -> None:
        """The grep that keeps the allocator from growing back.

        If the generator ever needs to read a file, a counter, or the ids already
        present, never-reuse has stopped being a property of the token and has
        become state somebody has to maintain.
        """
        references = self.generation_references()
        unexpected = sorted(references - self.GENERATION_ALLOWED_REFERENCES)
        self.assertEqual(
            unexpected, [],
            "claim id generation reached for something new; if it is not allocator "
            "state, machine identity, or a file, add it to GENERATION_ALLOWED_REFERENCES "
            f"deliberately: {unexpected}",
        )
        # The randomness is the uniqueness, so its absence is the real failure.
        self.assertIn("secrets.token_bytes", references)


def v3_store(claims: list, *, skillset: str = "software-engineering", **overrides: object) -> dict:
    store = {
        "memory_schema_version": 3,
        "skillset": skillset,
        "memory_version": 1,
        "claims": claims,
    }
    store.update(overrides)
    return store


def base_claim(**overrides: object) -> dict:
    """A minimal structurally valid v3 claim; each test mutates one face."""
    claim = {
        "id": "SE_MEM_01M55WJVKRKX5ZNTWCWARDTT8N",
        "claim": "Checking both overloads before declaring const safety prevents lifetime mistakes.",
        "claim_class": "conduct",
        "claim_kind": "deterministic",
        "confidence": "repeated",
        "delta": {
            "kinds": ["judgment"],
            "statement": "Check the lifetime contract on both overloads.",
        },
        "envelope": {
            "holds_in": ["overload pairs where only const-ness differs"],
            "not_shown_in": ["value-returning accessors"],
        },
        "provenance": ["runtime_self_audit"],
        "scope": "lifetime_contracts",
        "retrieval_cues": ["const overload lifetime"],
        "last_verified": "2026-10-17",
    }
    claim.update(overrides)
    return claim


def contradiction_chain(length: int) -> tuple[list[str], list[dict]]:
    """`length` claims, all matching one cue, each naming its neighbours.

    Every link is symmetric and resolves, so this is the shape I6 alone
    accepts and a contradiction *pair* does not: every interior claim names two
    counterparts. Independent review built exactly this - at 10, 100 and 1,000 -
    to show T07's co-return walking the whole connected component out of a
    `limit` of 1. The validator refuses it now, and retrieval is tested over it
    anyway, because retrieval reads whatever parses: the bound on what a query
    returns cannot be delegated to validation of the store it happens to read.
    """
    ids = [
        "SE_MEM_" + str(index).rjust(memory_tool.CLAIM_ID_TAIL_LENGTH, "0")
        for index in range(length)
    ]
    claims = [
        base_claim(
            id=claim_id,
            scope="disputed_topic",
            retrieval_cues=["shared cue"],
            contradicts=ids[max(position - 1, 0):position] + ids[position + 1:position + 2],
        )
        for position, claim_id in enumerate(ids)
    ]
    return ids, claims


# The three valid examples of R2.5 §6.1–§6.3, verbatim, each in its own domain.
SPEC_V3_VALID = (
    (
        "software-engineering",
        v3_store([{
            "id": "SE_MEM_01M55WJVKRKX5ZNTWCWARDTT8N",
            "claim": (
                "A non-mutating overload carries the same lifetime obligation as its "
                "mutating counterpart; const-ness narrows what the call may change, not "
                "how long the referenced object must outlive it."
            ),
            "claim_class": "conduct",
            "claim_kind": "deterministic",
            "confidence": "repeated",
            "delta": {
                "kinds": ["judgment", "verification"],
                "statement": (
                    "Check the lifetime contract on both overloads before declaring a "
                    "const overload safe, instead of inferring safety from const-ness."
                ),
            },
            "envelope": {
                "holds_in": [
                    "reference-returning accessors on owning containers",
                    "overload pairs where only const-ness differs",
                ],
                "not_shown_in": [
                    "value-returning accessors",
                    "types with custom reference wrappers",
                ],
                "conditions": ["applies where the callee stores or forwards the reference"],
            },
            "provenance": ["runtime_self_audit", "regression_failure"],
            "scope": "lifetime_contracts",
            "retrieval_cues": [
                "const overload lifetime",
                "dangling reference accessor",
                "overload pair obligation",
            ],
            "canon": ["PAT_state_the_lifetime_contract_at_the_interface"],
            "evidence": ["SOFTWAREENGINEERING_EV_0088", "SOFTWAREENGINEERING_EV_0119"],
            "last_verified": "2026-10-17",
        }]),
    ),
    (
        "writing",
        v3_store([{
            "id": "WRI_MEM_01M55WJVKR0QB8C42T4SSG2KW2",
            "claim": (
                "Poetry craft knowledge is available to this skill at explanation level, "
                "while original poetic production is not yet demonstrated at the level "
                "analytical prose has reached."
            ),
            "claim_class": "reach",
            "claim_kind": "stochastic",
            "confidence": "provisional",
            "delta": {
                "kinds": ["posture", "verification"],
                "statement": (
                    "Decline to claim demonstrated poetic capability, and route original "
                    "poetry through an extra review pass before delivery."
                ),
            },
            "envelope": {
                "holds_in": ["lineation, meter, sound, compression, persona, and form"],
                "not_shown_in": ["narrative, image, and recurrence lessons drawn from verse works"],
                "conditions": ["prose renderings of verse sources are not evidence about sonic craft"],
            },
            "provenance": ["human_teaching"],
            "scope": "specialization_poetry",
            "retrieval_cues": [
                "poetry specialization",
                "poetry transfer",
                "poetic production evidence",
            ],
            "last_verified": "2026-10-17",
            "revalidate_after": "2027-04-17",
        }], skillset="writing"),
    ),
    (
        "game-design",
        v3_store([
            {
                "id": "GD_MEM_01M55WJVKRN841MC2Z91MFFFBR",
                "claim": (
                    "Compressing resolution steps before adding consequence layers keeps a "
                    "subsystem teachable at the table."
                ),
                "claim_class": "conduct",
                "claim_kind": "stochastic",
                "confidence": "repeated",
                "delta": {
                    "kinds": ["judgment"],
                    "statement": (
                        "Cut procedural steps before trimming consequence when a subsystem "
                        "is too slow to run."
                    ),
                },
                "envelope": {
                    "holds_in": ["table-facing combat and chase subsystems"],
                    "not_shown_in": ["asynchronous or play-by-post resolution"],
                },
                "provenance": ["human_teaching", "training_benchmark"],
                "scope": "subsystem_pacing",
                "retrieval_cues": ["compress before consequence", "subsystem pacing"],
                "last_verified": "2026-10-17",
                "contradicts": ["GD_MEM_01M55WJVKRCFWPAHPB4DMNP0QB"],
            },
            {
                "id": "GD_MEM_01M55WJVKRCFWPAHPB4DMNP0QB",
                "claim": (
                    "Consequence layers carry the table's attention more than step count "
                    "does, so trimming consequence costs more than trimming procedure saves."
                ),
                "claim_class": "conduct",
                "claim_kind": "stochastic",
                "confidence": "provisional",
                "delta": {
                    "kinds": ["judgment"],
                    "statement": (
                        "Preserve consequence layers and accept a longer procedure when the "
                        "subsystem's job is dramatic weight."
                    ),
                },
                "envelope": {
                    "holds_in": ["climactic set-piece subsystems"],
                    "not_shown_in": ["routine high-frequency resolution"],
                },
                "provenance": ["user_feedback"],
                "scope": "subsystem_pacing",
                "retrieval_cues": ["consequence over step count", "subsystem pacing"],
                "last_verified": "2026-10-17",
                "contradicts": ["GD_MEM_01M55WJVKRN841MC2Z91MFFFBR"],
            },
        ], skillset="game-design"),
    ),
)


class V3StoreChecks(unittest.TestCase):
    """Shared assertions over the two result channels.

    Errors make a store invalid; flags leave it valid and mark it for review.
    Every error names the rule it enforced, so a rejection is legible against
    the R2.5 §4 tables rather than against prose.
    """

    def errors_of(self, store: dict, domain: str = "software-engineering") -> list[str]:
        errors, _flags = memory_tool.validate_v3_contents(domain, store)
        return errors

    def flags_of(self, store: dict, domain: str = "software-engineering") -> list[str]:
        _errors, flags = memory_tool.validate_v3_contents(domain, store)
        return flags

    def assertValid(self, store: dict, domain: str = "software-engineering") -> list[str]:
        errors, flags = memory_tool.validate_v3_contents(domain, store)
        self.assertEqual(errors, [])
        return flags

    def assertRejected(self, rule: str, store: dict, domain: str = "software-engineering") -> list[str]:
        errors, _flags = memory_tool.validate_v3_contents(domain, store)
        self.assertTrue(
            any(f"({rule})" in error for error in errors),
            f"expected rule {rule} to reject the store, got: {errors}",
        )
        return errors


class V3Schema(V3StoreChecks):
    """R2.5 §2/§4.1: the v3 store refuses the legacy shape outright (S1–S10)."""

    def test_an_empty_v3_store_is_valid(self) -> None:
        self.assertValid(v3_store([]))

    def test_every_valid_spec_example_validates(self) -> None:
        for domain, store in SPEC_V3_VALID:
            with self.subTest(domain=domain):
                flags = self.assertValid(store, domain)
                self.assertEqual(flags, [], "a §6 valid example raised a FLAG")

    def test_the_mechanical_invalid_spec_examples_name_their_rule(self) -> None:
        """Thirteen of the seventeen §6.4 examples are mechanically decidable.

        1 and 5 are semantic (§4.7), 11 and 12 are referential (T03); each of
        those groups has its own test that locks the boundary instead.
        """
        accretion_claim = (
            "The early sessions established that shared primitives reduce fragmentation. "
            "GURPS further showed that shared primitives reduce fragmentation across "
            "otherwise unrelated subsystems when the vocabulary is small enough to hold "
            "in mind at the table. " + "And the supporting notes kept accreting. " * 12
        )
        examples: dict[int, tuple[str, dict, tuple[str, ...]]] = {
            2: ("software-engineering", v3_store([base_claim(claim=accretion_claim)]), ("C6", "C1")),
            3: (
                "software-engineering",
                v3_store([base_claim(envelope={"holds_in": ["generally"], "not_shown_in": ["none"]})]),
                ("E2",),
            ),
            4: (
                "software-engineering",
                v3_store([base_claim(
                    claim_class="reach",
                    delta={"kinds": ["action"], "statement": "Apply the new sequencing immediately."},
                )]),
                ("R1",),
            ),
            6: (
                "software-engineering",
                v3_store([base_claim(
                    claim="MiMo and the reviewing agent both missed the write barrier, "
                          "so the fix was applied twice.",
                )]),
                ("L3",),
            ),
            7: (
                "software-engineering",
                v3_store([base_claim(
                    claim="The learner's story earned an A- from the evaluator, so the "
                          "profile was marked complete.",
                )]),
                ("L4",),
            ),
            8: ("software-engineering", v3_store([base_claim(type="known_boundary")]), ("S2",)),
            9: ("software-engineering", v3_store([base_claim(status="resolved")]), ("S2",)),
            10: (
                "software-engineering",
                v3_store([base_claim(
                    evidence=[f"SOFTWAREENGINEERING_EV_{n:04d}" for n in range(1, 22)],
                )]),
                ("S9",),
            ),
            13: (
                "software-engineering",
                v3_store([base_claim(runtime_scope="Flash-Next on the 4090 workstation")]),
                ("S2",),
            ),
            14: ("software-engineering", v3_store([]) | {"memory_schema_version": 2}, ("S1",)),
            15: (
                "software-engineering",
                v3_store([{k: v for k, v in base_claim().items() if k != "delta"}]),
                ("S3",),
            ),
            16: ("software-engineering", v3_store([base_claim(id="SE_MEM_104")]), ("S5",)),
            17: (
                "software-engineering",
                v3_store([base_claim(id="GD_MEM_01M55WJVKRMQ4H8PTNZB6JXAFVE0")]),
                ("S5",),
            ),
        }
        self.assertEqual(sorted(examples), [2, 3, 4, 6, 7, 8, 9, 10, 13, 14, 15, 16, 17])
        for number, (domain, store, rules) in sorted(examples.items()):
            with self.subTest(example=number):
                errors = self.assertRejected(rules[0], store, domain)
                for rule in rules:
                    self.assertTrue(
                        any(f"({rule})" in error for error in errors),
                        f"example {number} must also name {rule}: {errors}",
                    )

    def test_the_semantic_only_spec_examples_pass_the_mechanical_validator(self) -> None:
        """§6.4 examples 1 and 5 fail the Canon-only baseline and a class/delta
        mismatch — semantic judgment §4.7 states no script may make. The
        validator's silence here is the contract, not a gap to fill in."""
        example_1 = base_claim(
            claim="The card held on every tested claim.",
            delta={"kinds": ["judgment"], "statement": "Trust the card."},
        )
        example_5 = base_claim(
            claim="Use the three-pass structure for every chapter opening.",
            delta={"kinds": ["posture"], "statement": "Prefer the three-pass structure."},
        )
        for number, claim in ((1, example_1), (5, example_5)):
            with self.subTest(example=number):
                self.assertValid(v3_store([claim]))

    def test_the_referential_spec_examples_are_t03_scope(self) -> None:
        """§6.4 examples 11 (I4) and 12 (I6), flipped by T03.

        11 flips exactly when History is present to show the cited event is
        invalid — with History absent the same claim must still validate (I5),
        because absence is not corruption. 12 flips unconditionally: a
        contradiction resolves inside the store alone, so no surrounding file
        excuses a target that is not there.
        """
        example_11 = base_claim(evidence=["SOFTWAREENGINEERING_EV_0002"])
        example_12 = base_claim(contradicts=["WRI_MEM_01M55WJVKR0QB8C42T4SSG2KW2"])
        self.assertValid(v3_store([example_11]))
        errors, _flags = memory_tool.validate_v3_contents(
            "software-engineering",
            v3_store([example_11]),
            events=[{
                "event_id": "SOFTWAREENGINEERING_EV_0002",
                "date": "2026-10-17",
                "task": "Run the isolation drill under load",
                "validity": "invalid",
                "invalid_reason": "grader_failed_open",
            }],
        )
        self.assertTrue(any("(I4)" in error for error in errors), errors)
        self.assertRejected("I6", v3_store([example_12]))

    def test_every_closed_vocabulary_accepts_every_member_and_rejects_a_nonmember(self) -> None:
        for key, allowed, nonmember in (
            ("claim_class", memory_tool.CLAIM_CLASSES, "neutral"),
            ("claim_kind", memory_tool.CLAIM_KINDS, "sometimes"),
            ("confidence", memory_tool.CONFIDENCE_VALUES, "certain"),
        ):
            for member in sorted(allowed):
                with self.subTest(key=key, member=member):
                    claim = base_claim(**{key: member})
                    if key == "claim_class" and member == "reach":
                        claim["delta"] = {
                            "kinds": ["posture"],
                            "statement": "Decline to claim demonstrated capability.",
                        }
                    self.assertValid(v3_store([claim]))
            with self.subTest(key=key, nonmember=nonmember):
                self.assertRejected("S4", v3_store([base_claim(**{key: nonmember})]))
        for kind in sorted(memory_tool.DELTA_KINDS):
            with self.subTest(delta_kind=kind):
                self.assertValid(v3_store([base_claim(
                    delta={"kinds": [kind], "statement": "Check the contract before declaring safety."},
                )]))
        self.assertRejected("S4", v3_store([base_claim(
            delta={"kinds": ["habit"], "statement": "Check the contract before declaring safety."},
        )]))
        for origin in sorted(memory_tool.PROVENANCE_VALUES):
            with self.subTest(provenance=origin):
                self.assertValid(v3_store([base_claim(provenance=[origin])]))
        # The renamed and dropped legacy values must not survive as members.
        for origin in ("book_close_training", "cross_model_test", "vibes"):
            with self.subTest(provenance=origin):
                self.assertRejected("S4", v3_store([base_claim(provenance=[origin])]))

    def test_every_unknown_top_level_or_claim_key_is_rejected(self) -> None:
        self.assertRejected("S2", v3_store([]) | {"entries": []})
        self.assertRejected("S2", v3_store([base_claim(vibe="strong")]))

    def test_every_legacy_only_claim_key_is_rejected_as_unknown(self) -> None:
        for key in (
            "type", "scope_type", "status", "evidence_count", "evidence_events",
            "evidence_origin", "observation", "boundary", "diagnosis",
            "interventions", "runtime_scope", "superseded_by", "likely_owners",
        ):
            with self.subTest(key=key):
                errors = self.assertRejected("S2", v3_store([base_claim(**{key: "x"})]))
                self.assertTrue(any(key in error for error in errors), errors)

    def test_a_duplicate_claim_id_in_one_store_is_rejected(self) -> None:
        claim = base_claim()
        self.assertRejected("S5a", v3_store([claim, dict(claim)]))

    def test_the_same_id_in_two_supplied_stores_is_rejected(self) -> None:
        """S5b is the same uniqueness check over every store the caller could
        read; each store alone stays complete on its own terms."""
        claim = base_claim()
        first = v3_store([claim])
        second = v3_store([dict(claim)])
        self.assertValid(first)
        self.assertValid(second)
        gathered = [
            entry["id"]
            for store in (first, second)
            for entry in store["claims"]
        ]
        self.assertEqual(memory_tool.duplicate_claim_ids(gathered), [claim["id"]])

    def test_skillset_must_equal_the_directory_name(self) -> None:
        self.assertRejected("S6", v3_store([base_claim()], skillset="writing"))

    def test_memory_version_must_be_a_positive_integer(self) -> None:
        for bad in (0, -1, True, "2", 1.5):
            with self.subTest(memory_version=bad):
                self.assertRejected("S7", v3_store([], memory_version=bad))
        self.assertValid(v3_store([], memory_version=2))

    def test_an_unmapped_domain_is_a_collected_error_not_an_exception(self) -> None:
        """claim_id_problems raises for an unmapped skillset, so the store-level
        token check must fire first and the ids simply go unchecked."""
        errors = self.errors_of(v3_store([base_claim()], skillset="mathematics"), "mathematics")
        self.assertTrue(any("CLAIM_DOMAIN_TOKENS" in error and "(S5)" in error for error in errors), errors)

    def test_scope_must_be_a_snake_case_slug(self) -> None:
        for bad in ("Lifetime Contracts", "Lifetime-Contracts", "1lifetime", ""):
            with self.subTest(scope=bad):
                self.assertRejected("S10", v3_store([base_claim(scope=bad)]))
        for good in ("lifetime", "lifetime_contracts2", "a"):
            with self.subTest(scope=good):
                self.assertValid(v3_store([base_claim(scope=good)]))

    def test_dates_follow_s8(self) -> None:
        self.assertRejected("S8", v3_store([base_claim(last_verified="17-10-2026")]))
        self.assertRejected("S8", v3_store([base_claim(revalidate_after="17-10-2026")]))
        self.assertRejected("S8", v3_store([base_claim(revalidate_after="2026-10-16")]))
        self.assertValid(v3_store([base_claim(revalidate_after="2026-10-17")]))
        self.assertValid(v3_store([base_claim(revalidate_after="2027-04-17")]))

    def test_provisional_with_deterministic_validates(self) -> None:
        """No threshold table exists; reproducible-on-demand and not-yet-broad
        is the honest reading, not a contradiction."""
        self.assertValid(v3_store([base_claim(confidence="provisional", claim_kind="deterministic")]))

    def test_a_non_mapping_claim_is_rejected_rather_than_crashing(self) -> None:
        errors = self.errors_of(v3_store(["not a claim"]))
        self.assertTrue(any("must be a mapping" in error for error in errors), errors)

    def test_claims_must_be_a_list(self) -> None:
        errors = self.errors_of(v3_store({}) | {"claims": {}})
        self.assertTrue(any("claims must be a list" in error for error in errors), errors)

    def test_no_code_path_reads_memory_version_to_produce_a_claim_id(self) -> None:
        """Criterion 7/8: memory_version counts file revisions and is never an
        identity input. Checked on the syntax tree so docstrings that explain
        the refusal cannot trip it."""
        tree = ast.parse(TOOL.read_text(encoding="utf-8"))
        producers = [
            node for node in tree.body
            if isinstance(node, ast.FunctionDef)
            and ("claim_id" in node.name or node.name in {"_crockford", "claim_domain_token"})
        ]
        self.assertTrue(producers, "the claim id functions are not where this test expects them")
        for function in producers:
            loaded = {
                node.id for node in ast.walk(function)
                if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)
            }
            self.assertNotIn("memory_version", loaded, function.name)

    def test_schema_document_declares_the_v3_contract(self) -> None:
        text = SCHEMA_DOC.read_text(encoding="utf-8")
        for required in (
            "Schema version 3 — the claim",
            "memory_schema_version: 3",
            "claim_class",
            "claim_kind",
            "source_study",
            "posture",
            "S1",
            "S5a",
            "C1",
            "C6",
            "E2",
            "R1",
            "L1",
            "L5",
            "I1",
            "I4",
            "I6",
            "standing alone",
            "FLAG",
            "whether the stated delta is",
        ):
            self.assertIn(required, text, f"MEMORY_SCHEMA.md is missing the v3 contract: {required}")


class V3ClaimInvariants(V3StoreChecks):
    """R2.5 §4.2 and §4.1 S3/S8/S9: one claim per entry, and the caps that
    actually resist the accretion shape (C1–C5, S9)."""

    def test_every_required_key_is_checked(self) -> None:
        for key in sorted(memory_tool.CLAIM_REQUIRED):
            with self.subTest(key=key):
                claim = base_claim()
                del claim[key]
                errors = self.errors_of(v3_store([claim]))
                self.assertTrue(
                    any(key in error and "(S3)" in error for error in errors),
                    f"missing {key} was not reported: {errors}",
                )

    def test_the_claim_word_cap_is_seventy_five(self) -> None:
        at_cap = " ".join(["word"] * 75)
        over_cap = " ".join(["word"] * 76)
        self.assertValid(v3_store([base_claim(claim=at_cap)]))
        self.assertRejected("C1", v3_store([base_claim(claim=over_cap)]))

    def test_a_fifty_word_claim_is_flagged_and_still_valid(self) -> None:
        """C2 is a review smell: exit stays zero, the channel stays separate."""
        errors, flags = memory_tool.validate_v3_contents(
            "software-engineering", v3_store([base_claim(claim=" ".join(["word"] * 50))]),
        )
        self.assertEqual(errors, [])
        self.assertTrue(any("(C2)" in flag for flag in flags), flags)

    def test_the_delta_statement_cap_is_fifty(self) -> None:
        at_cap = " ".join(["word"] * 50)
        over_cap = " ".join(["word"] * 51)
        self.assertValid(v3_store([base_claim(delta={"kinds": ["judgment"], "statement": at_cap})]))
        self.assertRejected("C4", v3_store([base_claim(delta={"kinds": ["judgment"], "statement": over_cap})]))

    def test_every_accretion_connective_is_rejected(self) -> None:
        for connective in memory_tool.ACCRETION_CONNECTIVES:
            with self.subTest(connective=connective):
                claim = base_claim(
                    claim=f"The evidence set {connective} that the fix held under load.",
                )
                self.assertRejected("C6", v3_store([claim]))

    def test_evidence_is_capped_at_three(self) -> None:
        three = [f"SOFTWAREENGINEERING_EV_{n:04d}" for n in range(1, 4)]
        self.assertValid(v3_store([base_claim(evidence=three)]))
        self.assertRejected("S9", v3_store([base_claim(evidence=three + ["SOFTWAREENGINEERING_EV_0004"])]))
        self.assertRejected("S9", v3_store([base_claim(evidence=[])]))

    def test_canon_is_capped_at_five(self) -> None:
        five = [f"PAT_example_object_{n}" for n in range(1, 6)]
        self.assertValid(v3_store([base_claim(canon=five)]))
        self.assertRejected("S9", v3_store([base_claim(canon=five + ["PAT_example_object_6"])]))
        self.assertRejected("S9", v3_store([base_claim(canon=[])]))

    def test_delta_kinds_cardinality(self) -> None:
        three = ["action", "judgment", "verification"]
        errors, flags = memory_tool.validate_v3_contents(
            "software-engineering", v3_store([base_claim(delta={"kinds": three, "statement": "Check the contract."})]),
        )
        self.assertEqual(errors, [])
        self.assertTrue(any("(C5)" in flag for flag in flags), flags)
        self.assertRejected("S9", v3_store([base_claim(
            delta={"kinds": three + ["posture"], "statement": "Check the contract."},
        )]))

    def test_contradicts_must_be_non_empty_when_present(self) -> None:
        self.assertRejected("S9", v3_store([base_claim(contradicts=[])]))
        # Non-empty is only half of I6: the target must exist in this store,
        # so a valid `contradicts` here carries its counterpart as well.
        first = base_claim()
        second = base_claim(
            id="SE_MEM_01M55WJVKR0QB8C42T4SSG2KW2",
            contradicts=[first["id"]],
        )
        first["contradicts"] = [second["id"]]
        self.assertValid(v3_store([first, second]))

    def test_a_contradiction_carries_exactly_one_counterpart(self) -> None:
        """R2.5 §4.8 defines a Memory contradiction as a disputed **pair** and
        names the other side a **counterpart**, singular. The cardinality is
        the whole of it: one member plus I6 symmetry makes every contradiction
        component exactly two claims, and two members is the shape that admits
        a chain. A chain is what let T07's component walk answer a `limit` of 1
        with a thousand claims, so the bound lives here, in the schema, and not
        in a traversal budget at the reader.
        """
        first = base_claim()
        second = base_claim(id="SE_MEM_01M55WJVKR0QB8C42T4SSG2KW2")
        third = base_claim(id="SE_MEM_01M55WJVKR0QB8C42T4SSG2KW3")
        first["contradicts"] = [second["id"], third["id"]]
        second["contradicts"] = [first["id"]]
        third["contradicts"] = [first["id"]]
        errors = self.assertRejected("S9", v3_store([first, second, third]))
        self.assertTrue(
            any("exactly one counterpart" in error for error in errors), errors,
        )

    def test_delta_and_envelope_unknown_subkeys_are_rejected(self) -> None:
        self.assertRejected("S2", v3_store([base_claim(delta={
            "kinds": ["judgment"], "statement": "Check the contract.", "weight": 3,
        })]))
        self.assertRejected("S2", v3_store([base_claim(envelope={
            "holds_in": ["overload pairs"], "not_shown_in": ["value accessors"], "verified_by": "x",
        })]))


class V3Envelope(V3StoreChecks):
    """R2.5 §4.3: a claim with no statable un-demonstrated region asserts
    universality, which is the overreach the envelope exists to prevent."""

    def test_both_envelope_halves_are_required(self) -> None:
        self.assertRejected("E1", v3_store([base_claim(envelope={"holds_in": ["overload pairs"]})]))
        self.assertRejected("E1", v3_store([base_claim(envelope={"not_shown_in": ["value accessors"]})]))
        self.assertRejected("E1", v3_store([base_claim(envelope={"holds_in": [], "not_shown_in": ["x"]})]))
        self.assertRejected("E1", v3_store([base_claim(envelope={"holds_in": ["x"], "not_shown_in": []})]))

    def test_every_sentinel_evasion_is_rejected(self) -> None:
        for sentinel in ("n/a", "none", "unknown", "everywhere", "no limits", "None", "NO LIMITS"):
            with self.subTest(sentinel=sentinel):
                claim = base_claim(envelope={
                    "holds_in": ["overload pairs"],
                    "not_shown_in": [sentinel],
                })
                self.assertRejected("E2", v3_store([claim]))

    def test_a_real_not_shown_in_member_is_accepted(self) -> None:
        claim = base_claim(envelope={
            "holds_in": ["overload pairs"],
            "not_shown_in": ["regions the evidence has not reached"],
        })
        self.assertValid(v3_store([claim]))

    def test_envelope_items_are_capped_at_forty_words(self) -> None:
        at_cap = " ".join(["word"] * 40)
        over_cap = " ".join(["word"] * 41)
        for key in ("holds_in", "not_shown_in", "conditions"):
            with self.subTest(key=key):
                envelope = {"holds_in": ["overload pairs"], "not_shown_in": ["value accessors"]}
                envelope[key] = [at_cap]
                self.assertValid(v3_store([base_claim(envelope=envelope)]))
                envelope[key] = [over_cap]
                self.assertRejected("C3", v3_store([base_claim(envelope=envelope)]))

    def test_conditions_are_optional(self) -> None:
        self.assertValid(v3_store([base_claim(envelope={
            "holds_in": ["overload pairs"],
            "not_shown_in": ["value accessors"],
        })]))


class V3ReachInvariant(V3StoreChecks):
    """R2.5 §4.4: reach may change posture and verification posture, and must
    never prescribe conduct — the one mechanical rule the invariant needs."""

    def test_reach_rejects_conduct_prescribing_delta_kinds(self) -> None:
        for kind in ("action", "judgment", "application_limit"):
            with self.subTest(kind=kind):
                claim = base_claim(
                    claim_class="reach",
                    delta={"kinds": [kind], "statement": "Check the contract before declaring safety."},
                )
                self.assertRejected("R1", v3_store([claim]))

    def test_reach_accepts_posture_and_verification(self) -> None:
        for kinds in (["posture"], ["verification"], ["posture", "verification"]):
            with self.subTest(kinds=kinds):
                claim = base_claim(
                    claim_class="reach",
                    delta={"kinds": kinds, "statement": "Decline to claim demonstrated capability."},
                )
                self.assertValid(v3_store([claim]))

    def test_a_reach_claim_may_carry_a_canon_link(self) -> None:
        claim = base_claim(
            claim_class="reach",
            claim_kind="stochastic",
            confidence="provisional",
            delta={"kinds": ["posture"], "statement": "Decline to claim demonstrated capability."},
            canon=["PAT_state_the_lifetime_contract_at_the_interface"],
        )
        self.assertValid(v3_store([claim]))

    def test_conduct_claims_accept_every_closed_delta_kind(self) -> None:
        for kind in sorted(memory_tool.DELTA_KINDS):
            with self.subTest(kind=kind):
                claim = base_claim(delta={"kinds": [kind], "statement": "Check the contract."})
                self.assertValid(v3_store([claim]))


class V3Leakage(V3StoreChecks):
    """R2.5 §4.5: model-neutral, learner-neutral, portable prose - and the one
    collision that outlived the legacy reader: `provenance` is required on a
    claim and forbidden on a History event (SR1), so the two rejection lists
    can never be merged.

    This class is also where the temporary-state firewall now lives. The
    entry-shaped `TemporaryStateFirewall` that used to state it - session keys
    refused, retired provenance keys refused, an observation that defers to a
    conversation refused - was deleted at T21 with the schema it was written
    against, because `test_retired_authoring_and_lineage_keys_are_rejected` and
    `test_conversation_deference_is_rejected` below make the same three
    statements against claims. Nothing becomes Memory except a portable
    empirical claim; that rule did not move, only the shape it is enforced on.
    """

    def test_model_identity_tokens_are_rejected_in_claim_and_envelope(self) -> None:
        for token in memory_tool.MODEL_IDENTITY_TOKENS:
            with self.subTest(token=token, surface="claim"):
                claim = base_claim(claim=f"The contract held when {token} checked the interface.")
                self.assertRejected("L3", v3_store([claim]))
            with self.subTest(token=token, surface="envelope"):
                claim = base_claim(envelope={
                    "holds_in": [f"reviews where {token} applied the const rule"],
                    "not_shown_in": ["value accessors"],
                })
                self.assertRejected("L3", v3_store([claim]))

    def test_conversation_deference_is_rejected(self) -> None:
        for phrase in ("see the chat", "as discussed", "in the session above", "earlier in this conversation"):
            with self.subTest(phrase=phrase):
                claim = base_claim(claim=f"The contract held; {phrase} for the full trace.")
                self.assertRejected("L2", v3_store([claim]))

    def test_learner_identity_and_specimen_grades_are_rejected(self) -> None:
        for phrase in ("the learner", "the taker", "the evaluator", "the user preferred"):
            with self.subTest(phrase=phrase):
                claim = base_claim(claim=f"The contract held until {phrase} changed the task.")
                self.assertRejected("L4", v3_store([claim]))
        for text in (
            "The draft earned an A- from the review.",
            "The profile was graded B+.",
            "The artifact scored C+ on the first pass.",
            "The sitting was graded A under the frozen criteria.",
        ):
            with self.subTest(grade=text):
                self.assertRejected("L4", v3_store([base_claim(claim=text)]))

    def test_local_state_prose_is_flagged_not_rejected(self) -> None:
        claim = base_claim(claim="The check holds on this machine after the driver update.")
        errors, flags = memory_tool.validate_v3_contents("software-engineering", v3_store([claim]))
        self.assertEqual(errors, [])
        self.assertTrue(any("(L5)" in flag for flag in flags), flags)

    def test_retired_authoring_and_lineage_keys_are_rejected(self) -> None:
        self.assertEqual(
            sorted(memory_tool.CLAIM_FORBIDDEN_KEYS),
            sorted([
                "source_id", "locator", "page", "hash", "receipt", "attestation",
                "ledger", "session_id", "current_stage", "unit", "next_unit",
                "parent_gen_id", "legacy_id", "migrated_from", "source_entry",
                "previous_id",
            ]),
        )
        for key in sorted(memory_tool.CLAIM_FORBIDDEN_KEYS):
            with self.subTest(key=key):
                errors = self.assertRejected("L1", v3_store([base_claim(**{key: "x"})]))
                self.assertTrue(any(key in error for error in errors), errors)

    def test_provenance_is_required_and_never_a_forbidden_key(self) -> None:
        """The SR1 collision: FORBIDDEN_KEYS rejects `provenance` for v1/v2,
        and every v3 claim requires it. Reusing the legacy list here would
        reject every valid claim."""
        for origins in (["human_teaching"], ["user_feedback", "runtime_self_audit"]):
            with self.subTest(provenance=origins):
                errors, flags = memory_tool.validate_v3_contents(
                    "software-engineering", v3_store([base_claim(provenance=origins)]),
                )
                self.assertEqual(errors, [])
                self.assertEqual(flags, [])
                self.assertFalse(any("forbidden" in error for error in errors))


# History fixtures for the referential tests. The prefixes are this store's
# own event-id family (SR2), derived from the events themselves — never from
# CLAIM_DOMAIN_TOKENS, whose `SE` token is not how any live History is numbered.
V3_VALID_EVENT = {
    "event_id": "SE_EV_0001",
    "date": "2026-10-16",
    "task": "Run the isolation drill under competing load",
    "validity": "valid",
}
V3_INVALID_EVENT = {
    "event_id": "SE_EV_0002",
    "date": "2026-10-16",
    "task": "Tighten an accepted artifact without redesign",
    "validity": "invalid",
    "invalid_reason": "grader_failed_open",
}
V3_METADATA_CORRECTION = {
    "event_id": "SE_EV_0003",
    "date": "2026-10-17",
    "task": "Correct the recorded runtime for an earlier attempt",
    "validity": "valid",
    "event_kind": "metadata_correction",
    "supersedes_events": ["SE_EV_0001"],
    "corrections": {"taker.runtime.name": "recorded-runtime-corrected"},
}
V3_EVIDENCE_CORRECTION = {
    "event_id": "SE_EV_0004",
    "date": "2026-10-17",
    "task": "Correct the evidence classification of an earlier attempt",
    "validity": "valid",
    "event_kind": "evidence_correction",
    "supersedes_events": ["SE_EV_0001"],
    "corrections": {
        "disposition": "quarantined",
        "reason": "The attempt did not exercise the capability it was said to measure.",
    },
}


class V3ReferentialIntegrity(V3StoreChecks):
    """R2.5 §4.6 I1–I6: references checked exactly as far as the files beside
    the store permit. Shape runs always; resolution runs only against a History
    or a Library root that is actually present; the store stays valid with
    neither (I5, §9.1.1)."""

    def check(
        self,
        store: dict,
        *,
        events: list[dict] | None = None,
        event_errors: list[str] | None = None,
        library: Path | None = None,
        domain: str = "software-engineering",
    ) -> tuple[list[str], list[str]]:
        return memory_tool.validate_v3_contents(
            domain, store, events=events, event_errors=event_errors, library_root=library,
        )

    def assertReferentiallyRejected(
        self, rule: str, store: dict, **kwargs: object,
    ) -> list[str]:
        errors, _flags = self.check(store, **kwargs)
        self.assertTrue(
            any(f"({rule})" in error for error in errors),
            f"expected rule {rule} to reject the store, got: {errors}",
        )
        return errors

    def tempdir(self, prefix: str) -> Path:
        tmp = Path(tempfile.mkdtemp(prefix=prefix))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        return tmp

    def write_library_card(self, root: Path, package: str, name: str, body: str) -> None:
        package_dir = root / package
        package_dir.mkdir(parents=True, exist_ok=True)
        (package_dir / f"{name}.md").write_text(body, encoding="utf-8")

    # --- I1: canon shape -------------------------------------------------

    def test_a_malformed_canon_member_is_rejected(self) -> None:
        for bad in ("PAT_", "PAT_UPPERCASE_TAIL", "AP", "DRILL", "1_lifetime", "PAT-fail", 42, None):
            with self.subTest(member=bad):
                errors = self.assertReferentiallyRejected(
                    "I1", v3_store([base_claim(canon=[bad])]),
                )
                self.assertTrue(any("canon member" in error for error in errors), errors)

    def test_a_well_formed_canon_member_validates(self) -> None:
        for good in (
            "PAT_state_the_lifetime_contract_at_the_interface",
            "AP_check_both_overloads",
            "DRILL_practise_the_lifetime_contract",
        ):
            with self.subTest(member=good):
                errors, flags = self.check(v3_store([base_claim(canon=[good])]))
                self.assertEqual(errors, [])
                self.assertEqual(flags, [])

    def test_a_bare_variant_canon_id_validates(self) -> None:
        """Variant ids are bare lowercase snake tokens, not (PAT|AP|DRILL)_
        prefixed — I1 admits them as they are and never rewrites them."""
        variant = "writing_fiction_variant_anchor_absurdity_in_legible_operating_logic"
        errors, flags = self.check(v3_store([base_claim(canon=[variant])]))
        self.assertEqual(errors, [])
        self.assertEqual(flags, [])

    # --- I2: canon resolution -------------------------------------------

    def test_a_nonexistent_but_well_formed_canon_id_flags_only(self) -> None:
        library = self.tempdir("pass-v3-library-") / "library"
        library.mkdir()
        store = v3_store([base_claim(canon=["PAT_nothing_by_this_name"])])
        errors, flags = self.check(store, library=library)
        self.assertEqual(errors, [])
        self.assertTrue(
            any("(I2)" in flag and "PAT_nothing_by_this_name" in flag for flag in flags),
            flags,
        )

    def test_the_library_is_never_required(self) -> None:
        store = v3_store([base_claim(canon=["PAT_nothing_by_this_name"])])
        absent = self.tempdir("pass-v3-nolib-") / "never-created"
        for library in (None, absent):
            with self.subTest(library=library):
                errors, flags = self.check(store, library=library)
                self.assertEqual(errors, [])
                self.assertEqual(flags, [])

    def test_canon_resolves_within_the_package_and_metaskills_only(self) -> None:
        library = self.tempdir("pass-v3-ownership-") / "library"
        self.write_library_card(
            library, "software-engineering", "PAT_local",
            "---\nobject_id: PAT_local_object\n---\n\n# Pattern Rule\n\nLocal.\n",
        )
        self.write_library_card(
            library, "metaskills", "AP_shared",
            "---\nobject_id: AP_shared_object\n---\n\n# Objective\n\nShared.\n",
        )
        self.write_library_card(
            library, "writing", "PAT_other",
            "---\nobject_id: PAT_writing_only_object\n---\n\n# Pattern Rule\n\nOther.\n",
        )
        own = v3_store([base_claim(canon=["PAT_local_object", "AP_shared_object"])])
        errors, flags = self.check(own, library=library)
        self.assertEqual(errors, [])
        self.assertEqual(flags, [])
        cross = v3_store([base_claim(canon=["PAT_writing_only_object"])])
        errors, flags = self.check(cross, library=library)
        self.assertEqual(errors, [])
        self.assertTrue(any("(I2)" in flag for flag in flags), flags)

    def test_an_existing_package_variant_resolves_instead_of_flagging(self) -> None:
        library = self.tempdir("pass-v3-variant-") / "library"
        variant = "software_engineering_variant_check_both_overloads_first"
        self.write_library_card(
            library, "software-engineering", "PAT_variant_owner",
            "---\nobject_id: PAT_variant_owner_object\nvariants:\n"
            f"  - variant_id: {variant}\n---\n\n# Pattern Rule\n\nOwned.\n",
        )
        errors, flags = self.check(v3_store([base_claim(canon=[variant])]), library=library)
        self.assertEqual(errors, [])
        self.assertEqual(flags, [])

    # --- I3: evidence-id shape ------------------------------------------

    def test_a_malformed_evidence_id_is_rejected_without_history(self) -> None:
        for bad in ("se_ev_0001", "SE-EV-0001", "EV_0001", "SE_EV_", "SE_MEM_0001", 42):
            with self.subTest(member=bad):
                self.assertReferentiallyRejected("I3", v3_store([base_claim(evidence=[bad])]))

    def test_the_evidence_family_is_derived_from_the_store_history(self) -> None:
        """SR2: the spec's illustrative prefix and every other domain's live
        prefix are wrong for this store; only its own History decides."""
        resolved = v3_store([base_claim(evidence=["SE_EV_0001"])])
        errors, flags = self.check(resolved, events=[V3_VALID_EVENT])
        self.assertEqual(errors, [])
        self.assertEqual(flags, [])
        for foreign in ("SOFTWAREENGINEERING_EV_0088", "ART_EV_0001", "GAMEDESIGN_EV_0119"):
            with self.subTest(member=foreign):
                self.assertReferentiallyRejected(
                    "I3", v3_store([base_claim(evidence=[foreign])]),
                    events=[V3_VALID_EVENT],
                )

    def test_without_history_the_generic_event_family_is_the_shape(self) -> None:
        for good in ("SE_EV_0001", "ART_EV_0001", "SOFTWAREENGINEERING_EV_0088", "GAMEDESIGN_EV_0119"):
            with self.subTest(member=good):
                errors, flags = self.check(v3_store([base_claim(evidence=[good])]))
                self.assertEqual(errors, [])
                self.assertEqual(flags, [])
        for bad in ("se_ev_0001", "SE_EV_0001_EXTRA", "EV_0001"):
            with self.subTest(member=bad):
                self.assertReferentiallyRejected("I3", v3_store([base_claim(evidence=[bad])]))

    # --- I4: evidence admissibility, only when History is present --------

    def test_an_invalid_history_event_is_rejected(self) -> None:
        store = v3_store([base_claim(evidence=["SE_EV_0002"])])
        errors, flags = self.check(store, events=[V3_VALID_EVENT, V3_INVALID_EVENT])
        self.assertTrue(
            any("(I4)" in error and "invalid event" in error for error in errors), errors,
        )
        self.assertEqual(flags, [])

    def test_a_metadata_correction_is_rejected_as_evidence(self) -> None:
        store = v3_store([base_claim(evidence=["SE_EV_0003"])])
        errors, _flags = self.check(
            store, events=[V3_VALID_EVENT, V3_METADATA_CORRECTION],
        )
        self.assertTrue(
            any("(I4)" in error and "metadata correction" in error for error in errors),
            errors,
        )

    def test_an_evidence_correction_is_rejected_as_evidence(self) -> None:
        store = v3_store([base_claim(evidence=["SE_EV_0004"])])
        errors, _flags = self.check(
            store, events=[V3_VALID_EVENT, V3_EVIDENCE_CORRECTION],
        )
        self.assertTrue(
            any("(I4)" in error and "evidence correction" in error for error in errors),
            errors,
        )

    def test_a_quarantined_event_is_rejected(self) -> None:
        store = v3_store([base_claim(evidence=["SE_EV_0001"])])
        errors, _flags = self.check(store, events=[V3_VALID_EVENT, V3_EVIDENCE_CORRECTION])
        self.assertTrue(
            any("(I4)" in error and "quarantined" in error for error in errors), errors,
        )

    def test_evidence_must_exist_when_history_is_present(self) -> None:
        store = v3_store([base_claim(evidence=["SE_EV_0099"])])
        errors, _flags = self.check(store, events=[V3_VALID_EVENT])
        self.assertTrue(
            any("(I4)" in error and "unknown event" in error for error in errors), errors,
        )

    # --- I5: History absence ---------------------------------------------

    def test_the_same_evidence_validates_when_history_is_absent(self) -> None:
        """The exact claim I4 rejects above must pass with no History at all:
        nothing to resolve against, and absence is not corruption."""
        store = v3_store([base_claim(evidence=["SE_EV_0002"])])
        errors, flags = self.check(store, events=None)
        self.assertEqual(errors, [])
        self.assertEqual(flags, [])

    def test_a_store_with_no_history_file_validates(self) -> None:
        tmp = self.tempdir("pass-v3-nohistory-")
        domain_dir = tmp / "memory" / "software-engineering"
        domain_dir.mkdir(parents=True)
        store = v3_store([base_claim(evidence=["SE_EV_0002"])])
        (domain_dir / "skill_memory.yaml").write_text(
            yaml.safe_dump(store, sort_keys=False), encoding="utf-8",
        )
        errors, flags = memory_tool.validate_v3_store(domain_dir)
        self.assertEqual(errors, [])
        self.assertEqual(flags, [])

    # --- I6: contradictions ----------------------------------------------

    def test_a_one_sided_contradiction_is_rejected(self) -> None:
        first = base_claim(contradicts=["SE_MEM_01M55WJVKR0QB8C42T4SSG2KW2"])
        second = base_claim(id="SE_MEM_01M55WJVKR0QB8C42T4SSG2KW2")
        errors = self.assertReferentiallyRejected("I6", v3_store([first, second]))
        self.assertTrue(any("one-sided" in error for error in errors), errors)

    def test_a_symmetric_contradiction_is_accepted(self) -> None:
        first = base_claim()
        second = base_claim(id="SE_MEM_01M55WJVKR0QB8C42T4SSG2KW2")
        first["contradicts"] = [second["id"]]
        second["contradicts"] = [first["id"]]
        errors, flags = self.check(v3_store([first, second]))
        self.assertEqual(errors, [])
        self.assertEqual(flags, [])

    def test_a_nonexistent_contradiction_target_is_rejected(self) -> None:
        errors = self.assertReferentiallyRejected(
            "I6", v3_store([base_claim(contradicts=["SE_MEM_01M55WJVKR0QB8C42T4SSG2KW2"])]),
        )
        self.assertTrue(any("does not resolve" in error for error in errors), errors)

    def test_a_contradiction_cannot_reference_itself(self) -> None:
        claim = base_claim()
        errors = self.assertReferentiallyRejected(
            "I6", v3_store([base_claim(contradicts=[claim["id"]])]),
        )
        self.assertTrue(any("itself" in error for error in errors), errors)

    def test_a_three_claim_contradiction_chain_is_structurally_rejected(self) -> None:
        """A↔B↔C has no asymmetric link and no dangling target, so I6 accepts
        it. The pair cardinality is what refuses it: the middle claim names two
        counterparts. With that rule, no valid component is larger than two
        claims and a component walk has nothing to walk."""
        errors = self.assertRejected("S9", v3_store(contradiction_chain(3)[1]))
        self.assertTrue(
            any("disputed pair" in error for error in errors), errors,
        )
        self.assertEqual(self.check(v3_store(contradiction_chain(2)[1]))[0], [])

    def test_a_contradiction_triangle_is_structurally_rejected(self) -> None:
        """The other three-claim component: a cycle rather than a chain. Every
        link is symmetric and resolvable here too, and every claim names two."""
        ids = [
            "SE_MEM_01M55WJVKRKX5ZNTWCWARDTT8N",
            "SE_MEM_01M55WJVKR0QB8C42T4SSG2KW2",
            "SE_MEM_01M55WJVKR0QB8C42T4SSG2KW3",
        ]
        triangle = [
            base_claim(id=claim_id, contradicts=[ids[(index + 1) % 3], ids[(index + 2) % 3]])
            for index, claim_id in enumerate(ids)
        ]
        self.assertRejected("S9", v3_store(triangle))


class V3Review(unittest.TestCase):
    """T08: `review` reports what needs a human and changes nothing.

    The line this class holds is the one the operation is named for. Review is
    a *reporting* surface: it distinguishes structurally invalid state (an
    ERROR, which stays an error) from a mechanically detectable but
    semantically undecidable concern (a review item), and it never crosses from
    the second into a verdict. It computes no confidence, resolves no
    contradiction, and writes no byte - not even a note to itself that a
    finding was already seen.
    """

    DOMAIN = "software-engineering"

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="pass-memory-review-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.root = self.tmp / "memory"
        self.domain = self.root / self.DOMAIN
        self.domain.mkdir(parents=True)

    # -------------------------------------------------- fixture construction

    def write(self, claims: list[dict], events: list[dict] | None = None, **overrides) -> None:
        (self.domain / "skill_memory.yaml").write_text(
            yaml.safe_dump(v3_store(claims, skillset=self.DOMAIN, **overrides), sort_keys=False),
            encoding="utf-8",
        )
        if events is not None:
            (self.domain / "training_history.jsonl").write_text(
                "".join(json.dumps(event, sort_keys=True) + "\n" for event in events),
                encoding="utf-8",
            )

    def library(self, package: str, *object_ids: str) -> Path:
        """A minimal library root carrying one package and its cards."""
        root = self.tmp / "library"
        package_dir = root / package
        package_dir.mkdir(parents=True, exist_ok=True)
        for object_id in object_ids:
            (package_dir / f"{object_id}.md").write_text(
                f"---\nobject_id: {object_id}\n---\n\nA card.\n", encoding="utf-8",
            )
        return root

    def claim_id(self, suffix: str) -> str:
        return "SE_MEM_" + suffix.rjust(memory_tool.CLAIM_ID_TAIL_LENGTH, "0")

    def dated_claim(self, revalidate_after: str, **overrides) -> dict:
        """A claim whose dates are unambiguous: `last_verified` long before the
        due date, so S8 holds and no test depends on today being the boundary."""
        return base_claim(
            last_verified="2020-01-01", revalidate_after=revalidate_after, **overrides,
        )

    # -------------------------------------------------- running and snapshots

    def review(self, *args: object) -> subprocess.CompletedProcess[str]:
        return run_tool("review", "--domain", self.DOMAIN, *args, memory=self.root)

    def validate(self) -> subprocess.CompletedProcess[str]:
        return run_tool("validate", "--domain", self.DOMAIN, memory=self.root)

    def snapshot(self) -> dict[str, bytes]:
        """Every byte under the temporary tree, keyed by path.

        Hashing the whole tree rather than one file is deliberate: the thing
        being proved is that review leaves no receipt, sidecar, cache, or
        acknowledgement file anywhere, and a new file is invisible to a check
        that only re-reads the files it already knew about.
        """
        return {
            path.relative_to(self.tmp).as_posix(): path.read_bytes()
            for path in sorted(self.tmp.rglob("*")) if path.is_file()
        }

    def assertReviewed(self, *args: object) -> str:
        """Run review over an unchanged tree and return its stdout."""
        before = self.snapshot()
        result = self.review(*args)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.snapshot(), before, "review wrote to the tree")
        return result.stdout

    # -------------------------------------------------- revalidate_after

    def test_a_past_due_claim_is_listed_and_nothing_is_written(self) -> None:
        """Criterion 20. The listing is the whole consequence of age: the file
        is byte-identical afterwards, down to `memory_version`."""
        claim = self.dated_claim("2020-06-01")
        self.write([claim])
        path = self.domain / "skill_memory.yaml"
        before = yaml.safe_load(path.read_text(encoding="utf-8"))
        output = self.assertReviewed()
        self.assertIn(f"{claim['id']}: revalidate_after 2020-06-01 is past due", output)
        self.assertIn("1 item(s) suggested for review", output)
        after = yaml.safe_load(path.read_text(encoding="utf-8"))
        self.assertEqual(after, before)
        self.assertEqual(after["memory_version"], 1)
        self.assertEqual(str(after["claims"][0]["revalidate_after"]), "2020-06-01")
        self.assertEqual(str(after["claims"][0]["last_verified"]), "2020-01-01")

    def test_a_future_revalidate_after_is_not_listed_for_age(self) -> None:
        self.write([self.dated_claim("2099-01-01")])
        output = self.assertReviewed()
        self.assertNotIn("past due", output)
        self.assertIn("0 item(s) suggested for review", output)

    def test_the_due_date_changes_nothing_about_retrieval(self) -> None:
        """F2 and criterion 19, cross-checked against T07: age is a listing and
        never a suppression, a rank penalty, or a label change."""
        retrieved = {}
        for label, due in (("past", "2020-06-01"), ("future", "2099-01-01")):
            self.write([self.dated_claim(due)])
            result = run_tool(
                "query", "--domain", self.DOMAIN, "--scope", "lifetime_contracts",
                memory=self.root,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            retrieved[label] = [
                line for line in result.stdout.splitlines() if not line.startswith("note:")
            ]
        self.assertEqual(retrieved["past"], retrieved["future"])
        self.assertTrue(
            any("retrieved:" in line for line in retrieved["past"]), retrieved["past"],
        )

    # -------------------------------------------------- the FLAG surface

    def assertFlagged(self, claim: dict, rule: str) -> None:
        """The claim is valid, and review surfaces exactly this rule."""
        self.write([claim])
        self.assertEqual(self.validate().returncode, 0, "the store should stay valid")
        output = self.assertReviewed()
        self.assertIn(f"FLAG: {claim['id']}", output)
        self.assertIn(f"({rule})", output)

    def test_review_surfaces_the_fusion_word_count_flag(self) -> None:
        """C2: at or past 50 words a claim smells fused - a smell, not a fact
        about the claim, which is why it is a flag and the human decides."""
        self.assertFlagged(base_claim(claim=" ".join(["prose"] * 52)), "C2")

    def test_review_surfaces_the_three_kind_delta_flag(self) -> None:
        """C5: three delta kinds is the cap and the smell at once."""
        self.assertFlagged(
            base_claim(delta={
                "kinds": ["action", "judgment", "verification"],
                "statement": "Check the lifetime contract on both overloads.",
            }),
            "C5",
        )

    def test_review_surfaces_the_local_state_flag(self) -> None:
        """L5: prose naming host-local state is a portability smell."""
        self.assertFlagged(
            base_claim(claim="The const check holds on this machine after the driver update."),
            "L5",
        )

    def test_a_flagged_store_is_still_valid_and_still_retrievable(self) -> None:
        """A flag is not an invalidity: the store validates, review exits zero,
        and the claim comes back from a query exactly as any other would."""
        claim = base_claim(claim="The const check holds on this machine after the driver update.")
        self.write([claim])
        self.assertEqual(self.validate().returncode, 0)
        output = self.assertReviewed()
        self.assertIn("(L5)", output)
        found = run_tool(
            "query", "--domain", self.DOMAIN, "--scope", "lifetime_contracts", memory=self.root,
        )
        self.assertIn(claim["id"], found.stdout)

    # -------------------------------------------------- canon resolution (I2)

    def test_a_resolvable_canon_id_produces_no_finding(self) -> None:
        library = self.library(self.DOMAIN, "PAT_const_overloads")
        self.write([base_claim(canon=["PAT_const_overloads"])])
        output = self.assertReviewed("--library", library)
        self.assertNotIn("(I2)", output)
        self.assertIn("0 item(s) suggested for review", output)
        # Review reports what failed to resolve. It never prints the canon ids
        # that did: enumerating them would be Memory offering a Canon list, and
        # Canon is selected before Memory is read at all.
        self.assertNotIn("PAT_const_overloads", output)

    def test_an_unresolved_canon_id_stays_valid_and_is_flagged(self) -> None:
        """Criterion 26. A well-formed id that resolves to nothing is a review
        item, never a structural error: Memory does not become invalid because
        a card left the library."""
        library = self.library(self.DOMAIN, "PAT_const_overloads")
        claim = base_claim(canon=["PAT_a_card_that_left"])
        self.write([claim])
        self.assertEqual(self.validate().returncode, 0)
        output = self.assertReviewed("--library", library)
        self.assertIn(f"FLAG: {claim['id']}", output)
        self.assertIn("PAT_a_card_that_left", output)
        self.assertIn("(I2)", output)

    def test_an_absent_library_is_not_memory_corruption(self) -> None:
        """The same store, reviewed with no library to resolve against, is
        neither invalid nor flagged. Memory is self-sufficient; library absence
        is a missing input, not a defect in Memory."""
        claim = base_claim(canon=["PAT_a_card_that_left"])
        self.write([claim])
        self.assertEqual(self.validate().returncode, 0)
        output = self.assertReviewed("--library", self.tmp / "no-library-here")
        self.assertNotIn("(I2)", output)
        self.assertNotIn("PAT_a_card_that_left", output)
        self.assertIn("0 item(s) suggested for review", output)

    # -------------------------------------------------- disputed pairs

    def disputed_pair(self) -> tuple[dict, dict]:
        left, right = self.claim_id("A1"), self.claim_id("B2")
        return (
            base_claim(id=left, contradicts=[right]),
            base_claim(
                id=right, contradicts=[left],
                claim="Checking one overload suffices when the pair differs only in const-ness.",
            ),
        )

    def test_a_valid_disputed_pair_is_one_review_item(self) -> None:
        """R2.5 §4.8 with T07's cardinality: a contradiction component is two
        claims, so the pair is reported once - from the pair, not once from
        each claim's link because both sides name each other."""
        left, right = self.disputed_pair()
        self.write([left, right])
        self.assertEqual(self.validate().returncode, 0, "a symmetric pair is valid")
        output = self.assertReviewed()
        self.assertIn(f"{left['id']} and {right['id']} are a disputed pair", output)
        self.assertIn("1 item(s) suggested for review", output)
        # Not an asymmetric-link flag: the stale R2.5 wording that `review`
        # reports asymmetric `contradicts` was closed by T07, which made
        # asymmetry an error instead.
        self.assertNotIn("one-sided", output)
        self.assertNotIn("(I6)", output)

    def test_a_disputed_pair_is_reported_and_otherwise_untouched(self) -> None:
        """No demotion, no merge, no erasure, no winner. Both claims stay in
        the file, both still retrieve, and nothing is written."""
        left, right = self.disputed_pair()
        self.write([left, right])
        before = self.snapshot()
        output = self.assertReviewed()
        self.assertEqual(self.snapshot(), before)
        for verdict in ("demote", "retire", "merge", "winner", "supersede", "should be"):
            self.assertNotIn(verdict, output.lower(), f"review issued a verdict: '{verdict}'")
        found = run_tool(
            "query", "--domain", self.DOMAIN, "--scope", "lifetime_contracts",
            "--limit", "1", memory=self.root,
        )
        self.assertIn(left["id"], found.stdout)
        self.assertIn(right["id"], found.stdout)

    def test_review_does_not_downgrade_a_malformed_contradiction(self) -> None:
        """T07's ERROR boundary survives T08. A one-sided link, a missing
        target and a two-member `contradicts` are each invalid, and review
        reports them as errors with a non-zero exit rather than listing them as
        softer concerns."""
        left, right = self.disputed_pair()
        third = self.claim_id("C3")
        shapes = {
            "one-sided": (
                [left, {k: v for k, v in right.items() if k != "contradicts"}],
                "(I6)",
            ),
            "missing target": ([dict(left, contradicts=[third])], "(I6)"),
            "two counterparts": (
                [
                    dict(left, contradicts=[right["id"], third]),
                    right,
                    base_claim(id=third, contradicts=[left["id"]]),
                ],
                "(S9)",
            ),
        }
        for label, (claims, rule) in shapes.items():
            with self.subTest(shape=label):
                self.write(claims)
                self.assertEqual(self.validate().returncode, 1, f"{label} must stay invalid")
                result = self.review()
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertIn("ERROR: ", result.stdout)
                self.assertIn(rule, result.stdout)
                self.assertNotIn("item(s) suggested for review", result.stdout)
                self.assertNotIn("are a disputed pair", result.stdout)

    # -------------------------------------------------- the confidence firewall

    def test_review_never_suggests_a_confidence(self) -> None:
        """SR4, F1 and F2, and criterion 18. The store is engineered to trip
        heuristic the deleted legacy path had and every one a reader might be
        tempted to add back: a `strong` label on a single event, a long-past due
        date, a `stochastic` kind, and a live contradiction. No confidence
        vocabulary may appear in the output at all."""
        left, right = self.disputed_pair()
        left = dict(
            left, confidence="strong", claim_kind="stochastic", evidence=["SE_EV_0001"],
            last_verified="2020-01-01", revalidate_after="2020-06-01",
        )
        right = dict(right, confidence="provisional")
        self.write([left, right], [V3_VALID_EVENT])
        output = self.assertReviewed()
        self.assertIn("past due", output)
        self.assertIn("disputed pair", output)
        for value in memory_tool.CONFIDENCE_VALUES:
            self.assertNotIn(value, output, f"review printed the confidence '{value}'")
        for word in ("confidence", "promote", "demote", "raise", "lower", "downgrade"):
            self.assertNotIn(word, output.lower(), f"review discussed confidence: '{word}'")
        # The evidence length is read by nothing: one event behind a `strong`
        # claim is the exact shape the removed heuristic reported on.
        self.assertNotIn("event(s)", output.replace("valid event(s) are not cited", ""))

    def test_the_legacy_confidence_heuristic_is_not_on_the_v3_path(self) -> None:
        """SR4 as a source check, because an output scan only proves what this
        fixture happened to trip. `STALE_DAYS` and the evidence-count remark
        went with the legacy review heuristics at T21; this holds the ground
        after the deletion, so neither can be reintroduced on the v3 path by a
        later convenience."""
        tree = ast.parse(TOOL.read_text(encoding="utf-8"))
        wanted = {"review_v3_store", "disputed_pairs", "uncited_events_note"}
        found = {}
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef) or node.name not in wanted:
                continue
            # The docstrings name what these functions must not reach, so the
            # scan reads code only: `ast.unparse` of the body without its
            # docstring drops prose and comments alike.
            body = [
                statement for statement in node.body
                if not (
                    isinstance(statement, ast.Expr)
                    and isinstance(statement.value, ast.Constant)
                    and isinstance(statement.value.value, str)
                )
            ]
            found[node.name] = "; ".join(ast.unparse(statement) for statement in body)
        self.assertEqual(set(found), wanted, "the v3 review functions moved or were renamed")
        for name, code in found.items():
            for token in ("STALE_DAYS", "evidence_count", "CONFIDENCE", "'confidence'"):
                self.assertNotIn(token, code, f"{name} reaches '{token}'")

    # -------------------------------------------------- read-only, end to end

    def test_review_writes_nothing_with_every_finding_at_once(self) -> None:
        """One store carrying a past-due date, a C2 claim, a C5 delta, an L5
        smell, an unresolvable canon id and a disputed pair. Every byte in the
        tree - store, history and library alike - is identical afterwards, and
        no file appeared beside them."""
        left, right = self.disputed_pair()
        claims = [
            dict(left, last_verified="2020-01-01", revalidate_after="2020-06-01"),
            right,
            base_claim(id=self.claim_id("D4"), claim=" ".join(["prose"] * 52)),
            base_claim(id=self.claim_id("E5"), delta={
                "kinds": ["action", "judgment", "posture"],
                "statement": "Check the lifetime contract on both overloads.",
            }),
            base_claim(
                id=self.claim_id("F6"),
                claim="The const check holds on this host after the driver update.",
            ),
            base_claim(id=self.claim_id("G7"), canon=["PAT_a_card_that_left"]),
        ]
        library = self.library(self.DOMAIN, "PAT_const_overloads")
        self.write(claims, [V3_VALID_EVENT])
        self.assertEqual(self.validate().returncode, 0, "the fixture must be valid")
        before = self.snapshot()
        first = self.review("--library", library)
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        self.assertEqual(self.snapshot(), before, "review wrote to the tree")
        for rule in ("(C2)", "(C5)", "(L5)", "(I2)"):
            self.assertIn(rule, first.stdout)
        self.assertIn("past due", first.stdout)
        self.assertIn("disputed pair", first.stdout)
        # A finding is a property of current state, not an event: nothing
        # remembers that it was seen, so the second run says the same thing.
        second = self.review("--library", library)
        self.assertEqual(second.stdout, first.stdout)
        self.assertEqual(self.snapshot(), before)

    def test_review_has_no_repair_mode(self) -> None:
        self.write([self.dated_claim("2020-06-01")])
        for flag in ("--fix", "--repair", "--resolve", "--acknowledge"):
            result = self.review(flag)
            self.assertEqual(result.returncode, 2, f"review accepted {flag}")
            self.assertIn("unrecognized arguments", result.stderr)

    def test_each_finding_identifies_its_claim_and_its_reason(self) -> None:
        """Criterion 5 and the §6 output contract: every line names the claim
        or the pair it is about, and review does not dump the store it read."""
        claims = [
            self.dated_claim("2020-06-01"),
            base_claim(id=self.claim_id("D4"), claim=" ".join(["prose"] * 52)),
        ]
        self.write(claims)
        output = self.assertReviewed()
        findings = [line for line in output.splitlines() if line.startswith(f"{self.DOMAIN}: ")]
        self.assertEqual(len(findings), 2, output)
        for line in findings:
            self.assertTrue(any(claim["id"] in line for claim in claims), line)
        self.assertNotIn("Checking both overloads", output, "review dumped claim prose")


class CorpusSurface(unittest.TestCase):
    """What one `validate` run says about a whole corpus.

    This was `SchemaDispatch`, and T04 built it to prove that one run could
    answer a corpus part way through migration: a v1 store beside a v3 store,
    each routed by its own declared version. T21 deleted the dispatch, so the
    mixed-state tests went with it - `test_a_v3_store_and_a_v1_store_validate_in_one_run`,
    `test_one_query_answers_a_mixed_corpus_with_one_receipt`,
    `test_only_the_dispatch_imports_the_legacy_input_module`, and
    `test_the_legacy_module_states_it_is_transitional` all described an
    arrangement the cutover removed. The boundary they protected is now held
    structurally by `SchemaContract.test_no_runtime_path_parses_schema_one_or_two`:
    there is no second claim side to keep behind a dispatch.

    What survives is the part that was never about the dispatch - the two
    channels of a validate run, and the summary line.
    """

    def temp_root(self, prefix: str) -> Path:
        root = Path(tempfile.mkdtemp(prefix=prefix))
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        return root

    def write_store(
        self, root: Path, domain: str, store: dict, events: list[dict] | None,
    ) -> None:
        domain_dir = root / domain
        domain_dir.mkdir(parents=True)
        (domain_dir / "skill_memory.yaml").write_text(
            yaml.safe_dump(store, sort_keys=False), encoding="utf-8",
        )
        if events is not None:
            (domain_dir / "training_history.jsonl").write_text(
                "".join(json.dumps(event, sort_keys=True) + "\n" for event in events),
                encoding="utf-8",
            )

    def test_review_flags_print_without_failing_the_run(self) -> None:
        root = self.temp_root("pass-memory-flags-")
        claim = base_claim(claim="The check holds on this machine after the driver update.")
        self.write_store(root, "software-engineering", v3_store([claim]), None)
        result = run_tool("validate", memory=root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("software-engineering: FLAG: ", result.stdout)
        self.assertIn("(L5)", result.stdout)
        self.assertIn("PASS: 1 store(s), 1 claim(s), 0 event(s) validated", result.stdout)

    def test_the_summary_counts_claims_across_every_store(self) -> None:
        """The reporting gap beta.130 left for this ticket. The summary used to
        count `entries`, so every migrated store reported zero content and the
        printed total silently under-reported the corpus. It counts claims now,
        and a store with no History file contributes no events rather than an
        error - absence beside a v3 store means no resolution (I5).
        """
        root = self.temp_root("pass-memory-summary-")
        self.write_store(
            root, "software-engineering",
            v3_store([base_claim(), base_claim(id="SE_MEM_01M55WJVKR0QB8C42T4SSG2KW2")]),
            None,
        )
        self.write_store(
            root, "art",
            v3_store([art_claim()], skillset="art"),
            [dict(VALID_EVENT, event_id="ART_EV_0001")],
        )
        result = run_tool("validate", memory=root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS: 2 store(s), 3 claim(s), 1 event(s) validated", result.stdout)
        self.assertNotIn("entr(ies)", result.stdout)


if __name__ == "__main__":
    unittest.main()
