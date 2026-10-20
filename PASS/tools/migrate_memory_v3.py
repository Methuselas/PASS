#!/usr/bin/env python3
"""One-time R2.5 migration tooling for legacy Skillset Memory stores: FREEZE,
hash verification, the sentence inventory, the A1–A10 accounting checker, the
three migration reports with item-by-item loss signoff, and the VERIFY gate,
deleted by ticket T21.

`freeze` is step 0 of the R2.5 migration algorithm (§7.4), and only step 0.
It records the mechanical facts a later migration needs in order to detect
source drift — for one domain, one store: `memory_schema_version`,
`memory_version`, the entry count, a sha256 of each entry's serialized bytes,
and the admissible event id set (valid + performance + not quarantined). It
refuses a legacy store that does not pass the existing Memory validator, and it
refuses anything that is not a legacy v1/v2 input: a schema-3 store is a migration
output, not an input, and FREEZE never converts one. `verify-hashes` re-checks
every recorded hash against the file (check A2), for use at the VERIFY gate.

`account` (step 4, pass 4 of §7.4) checks a judgment-filled ledger against the
ten mechanical completeness rules of §7.5: the ledger's schema and closed
vocabularies first (required blocks, disposition classes, rewrite reasons,
rejection reason kinds, destination authorities, proposition id shape, the
sentence map's row shape and its closed non-propositional reason set), then
A1–A10 against the frozen `legacy:` block, the ledger's own decompositions and
dispositions, and the candidate v3 store the targets must resolve into. Every
failure names its check. A9 proves sentence coverage: every sentence of every
frozen entry must appear exactly once in that entry's `sentence_map`,
attributed to a proposition id recorded in that entry's decomposition or to a
closed-set non-propositional reason, and every entry the ledger declares in
`accretion_entries` must carry the second-reader mark on its decomposition
record. The script records and checks those marks; it never attempts the
second reading.

`report` (still pass 4) derives the three §7.5 reports from the ledger alone —
survival, loss, and re-homing — into the same purpose directory, and the loss
report is the signoff artifact: every loss item carries its own `signed_off`
field and reviewer note, there is no document-level approval key, and
regeneration refuses while existing reports would be overwritten so a signoff
is never silently destroyed. Reports are derived, never hand-maintained
duplicates: a REJECT already in `dispositions` becomes a loss row, never a
second record that could disagree with the accounting.

`gate` (pass 5, VERIFY) is the single verification entry point: it re-runs
A1–A10 through `account`'s checker — so A2 source drift and A7 HOLDs refuse,
never warn — requires the loss report's items to equal the ledger's own loss
set with every item individually signed, runs the repository's actual v3
validator on the candidate store (ERRORs refuse), and requires every FLAG to
be cleared or individually accepted with a note in the review artifact. It
writes nothing, generates no reason or note, refuses an unsigned item rather
than filling one in, and has no bulk-approval path to accept-all.

`sentence coverage` has a fixed boundary. A complete map proves every source
sentence was consciously accounted for — nothing more (§7.5). The checker
never reads what a sentence means, never decides whether it carries a
proposition, and never judges whether the recorded attribution is true.

`sentences --domain <d> --entry <id>` emits the numbered sentence inventory A9
runs against: the entry's `observation`, `boundary`, and `diagnosis.hypothesis`
concatenated as one text in that order (§7.4 step 1 reads the three fields
together as one semantic source; per-field extraction is forbidden) and split
with `validate.py`'s SENTENCE_RE — the repository's one sentence splitter,
imported so segmentation stays a single deterministic implementation. Emission
only: nothing is attributed, decomposed, or written.

The ledger and the three reports land in the task's workspace purpose
directory and nowhere else. They are one-time artifacts, never a permanent
ledger, a state sidecar, or a Memory field: `memory/` is read and never
written — not the store, not Training History, not line endings, not metadata.
Legacy stores remain read-only migration inputs until their domain's
migration is signed off.

Judgment surfaces are deliberately absent. This tool records and re-checks
mechanical truth only: it never decomposes an entry, never classifies, never
attributes a sentence to a proposition, never chooses a non-propositional
reason, never authors a vNext claim, never invents a proposition id, never
assigns, proposes, or suggests a disposition, never computes a confidence,
never generates a loss reason or a reviewer's note, and never decides whether
a recorded loss is acceptable — `gate` proves each loss item carries its own
signoff and nothing more. The accounting checker proves completeness and
referential integrity of recorded judgments, never semantic fidelity (§7.5).
No runtime path may depend on this module; T21 deletes it together with the
legacy input reader.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys
from pathlib import Path
from typing import Any

import yaml

from memory import (
    SUPPORTED_SCHEMA_VERSIONS,
    claim_id_problems,
    domain_dirs,
    load_events,
    load_memory,
    quarantined_event_ids,
    validate_store,
    validate_v3_contents,
)
from paths import default_memory_root
from validate import SENTENCE_RE


class MigrateError_(Exception):
    """A refusal with a message the operator can act on."""


def admissible_event_ids(events: list[dict[str, Any]]) -> list[str]:
    """The admissible event id set: valid, performance, not quarantined.

    The one mechanical admissibility rule of R2.5 §7.4 step 0, mirrored here
    rather than imported from CRQ — a PASS tool never depends on a runtime
    package. History stays read-only; nothing is synthesized and nothing outside
    this filter is admissible.
    """
    quarantined = quarantined_event_ids(events)
    return sorted(
        str(event["event_id"])
        for event in events
        if isinstance(event.get("event_id"), str)
        and event.get("validity") == "valid"
        and event.get("event_kind", "performance") == "performance"
        and str(event["event_id"]) not in quarantined
    )


def entry_serialized_blocks(store_path: Path) -> dict[str, bytes]:
    """Each entry's exact serialized bytes in the store file, keyed by id.

    The hash unit A2 needs: the entry as it is serialized in the file, cut at
    the YAML node boundaries of the `entries` sequence. Any byte change inside
    an entry — text, structure, line endings — changes its block; nothing the
    file merely re-orders outside an entry can. Line marks come from the YAML
    parser, so the cut is one deterministic implementation rather than a scan
    that drifts from the file's actual shape.
    """
    text = store_path.read_bytes().decode("utf-8")
    lines = text.splitlines(keepends=True)
    document = yaml.compose(text, Loader=yaml.SafeLoader)
    entries_node = None
    if isinstance(document, yaml.MappingNode):
        for key, value in document.value:
            if getattr(key, "value", None) == "entries":
                entries_node = value
                break
    if not isinstance(entries_node, yaml.SequenceNode):
        raise MigrateError_(f"{store_path.as_posix()}: no entries sequence to freeze")
    blocks: dict[str, bytes] = {}
    for item in entries_node.value:
        block = "".join(lines[item.start_mark.line:item.end_mark.line])
        parsed = yaml.safe_load(block)
        entry = parsed[0] if isinstance(parsed, list) else parsed
        entry_id = entry.get("id") if isinstance(entry, dict) else None
        if not isinstance(entry_id, str) or not entry_id:
            raise MigrateError_(
                f"{store_path.as_posix()}: an entry block carries no id; FREEZE "
                "hashes entries the validator already accepted, so this is a cut "
                "bug rather than a store defect"
            )
        if entry_id in blocks:
            raise MigrateError_(f"{store_path.as_posix()}: duplicate entry id '{entry_id}'")
        blocks[entry_id] = block.encode("utf-8")
    return blocks


def legacy_freeze_block(domain_dir: Path) -> dict[str, Any]:
    """The ledger's `legacy:` block for one validated legacy store.

    Validation runs first and in full — the same `validate_store` the
    `memory.py validate` command uses, which reaches the isolated legacy input
    reader through the schema-version dispatch. A store that fails it is never
    frozen, never repaired, and never rewritten: freeze records the input as it
    is or refuses it.
    """
    domain = domain_dir.name
    errors, flags = validate_store(domain_dir)
    for flag in flags:
        print(f"{domain}: FLAG: {flag}")
    if errors:
        for error in errors:
            print(f"{domain}: {error}", file=sys.stderr)
        raise MigrateError_(
            f"freeze refused: {domain} fails memory.py validate; a legacy store "
            "is frozen exactly as it validates, never repaired in place"
        )
    memory = load_memory(domain_dir)
    schema_version = memory.get("memory_schema_version")
    if schema_version not in SUPPORTED_SCHEMA_VERSIONS:
        raise MigrateError_(
            f"freeze refused: {domain} declares memory_schema_version "
            f"{schema_version}; FREEZE records a legacy v1/v2 migration input, "
            "and a schema-3 store is a migration output"
        )
    events, event_errors = load_events(domain_dir)
    if event_errors:
        raise MigrateError_(
            f"freeze refused: {domain} training history did not load: "
            f"{'; '.join(event_errors)}"
        )
    entries = memory.get("entries") or []
    blocks = entry_serialized_blocks(domain_dir / "skill_memory.yaml")
    recorded_ids = [
        entry["id"] for entry in entries
        if isinstance(entry, dict) and isinstance(entry.get("id"), str)
    ]
    if sorted(recorded_ids) != sorted(blocks):
        raise MigrateError_(
            f"freeze refused: {domain} entry blocks do not match the parsed "
            "entries; FREEZE hashes the serialized entry the file actually holds"
        )
    return {
        "memory_schema_version": schema_version,
        "memory_version": memory["memory_version"],
        "entry_count": len(entries),
        "entry_hashes": {
            entry_id: hashlib.sha256(blocks[entry_id]).hexdigest()
            for entry_id in recorded_ids
        },
        "admissible_event_ids": admissible_event_ids(events),
    }


def purpose_directory(ledger_dir: Path, memory_root: Path) -> Path:
    """The task directory the ledger lands in — never loose, never in Memory.

    Two refusals, both mechanical. The workspace root itself is where loose
    generated files are forbidden (PASS_RUN.md §Workspace lifecycle), so a
    ledger directly inside it is refused; a task-named directory under a
    purpose bucket is the shape that is accepted. And migration accounting
    never lands inside the memory tree: legacy stores are read-only inputs,
    and no migration metadata is written into `skill_memory.yaml`,
    `training_history.jsonl`, or anything beside them.
    """
    resolved = Path(ledger_dir).resolve()
    workspace_root = Path(__file__).resolve().parents[2] / "workspace"
    if resolved == workspace_root.resolve():
        raise MigrateError_(
            f"refused: {resolved.as_posix()} is the workspace root; the ledger "
            "lands in the task's purpose directory, never loose in workspace/"
        )
    memory_resolved = Path(memory_root).resolve()
    if resolved == memory_resolved or memory_resolved in resolved.parents:
        raise MigrateError_(
            f"refused: {resolved.as_posix()} is inside the memory tree; the "
            "ledger is workspace migration state and never a Memory artifact"
        )
    return resolved


def ledger_file(ledger_dir: Path, domain: str) -> Path:
    return Path(ledger_dir) / f"ledger-{domain}.yaml"


def write_yaml_atomic(path: Path, document: dict[str, Any]) -> None:
    """Write one YAML artifact atomically. The only writer in this tool."""
    text = yaml.safe_dump(document, sort_keys=False, default_flow_style=False)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        temporary.write_text(text, encoding="utf-8", newline="\n")
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def hash_problems(domain_dir: Path, recorded: dict[str, Any]) -> list[str]:
    """Every way the store's entries disagree with the frozen hashes (A2).

    The entry id set is checked as well as each recorded hash: an entry edited,
    removed, or added after FREEZE is a mid-migration edit, and a recorded hash
    that still matches the surviving entries would miss the last two.
    """
    problems: list[str] = []
    recorded_hashes = recorded.get("entry_hashes")
    if not isinstance(recorded_hashes, dict) or not recorded_hashes:
        return [f"ledger legacy.entry_hashes is missing or empty for {domain_dir.name}"]
    try:
        blocks = entry_serialized_blocks(domain_dir / "skill_memory.yaml")
    except (MigrateError_, OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        return [f"{domain_dir.name}: entries no longer load for hash verification: {exc}"]
    for entry_id, digest in recorded_hashes.items():
        block = blocks.get(entry_id)
        if block is None:
            problems.append(
                f"{domain_dir.name}: entry '{entry_id}' recorded at FREEZE is "
                "absent from the store"
            )
            continue
        actual = hashlib.sha256(block).hexdigest()
        if actual != digest:
            problems.append(
                f"{domain_dir.name}: entry '{entry_id}' hash mismatch: the entry "
                "changed after FREEZE"
            )
    for entry_id in blocks:
        if entry_id not in recorded_hashes:
            problems.append(
                f"{domain_dir.name}: entry '{entry_id}' was not recorded at FREEZE"
            )
    return problems


def load_ledger_document(path: Path, domain: str) -> dict[str, Any]:
    """The whole ledger document, or a refusal naming the file and the mismatch."""
    if not path.is_file():
        raise MigrateError_(
            f"no ledger at {path.as_posix()}; run freeze for this domain first"
        )
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise MigrateError_(f"{path.as_posix()}: ledger must be a mapping")
    if data.get("domain") != domain:
        raise MigrateError_(
            f"{path.as_posix()}: ledger is for domain '{data.get('domain')}', "
            f"not '{domain}'"
        )
    if not isinstance(data.get("legacy"), dict):
        raise MigrateError_(f"{path.as_posix()}: ledger has no legacy block")
    return data


def load_ledger(path: Path, domain: str) -> dict[str, Any]:
    return load_ledger_document(path, domain)["legacy"]


# --- T14: ledger schema and the A1-A10 accounting checker --------------------
#
# Everything below is mechanical. The schema validator proves shape, closed
# vocabularies, and proposition identity format; the accounting checker proves
# completeness and referential integrity of the judgments a human or model
# recorded in the ledger. Neither ever decides what a disposition should be,
# what a proposition means, or whether a claim is faithful to its source
# (R2.5 §7.5, §7.7).

DISPOSITION_CLASS_ORDER = (
    "CARRY", "REWRITE", "SPLIT", "CONDENSE", "EXTRACT", "REHOME", "REJECT", "HOLD",
)
DISPOSITION_CLASSES = frozenset(DISPOSITION_CLASS_ORDER)
# The five classes whose dispositions survive into Memory as claim targets.
SURVIVING_CLASSES = frozenset({"CARRY", "REWRITE", "SPLIT", "CONDENSE", "EXTRACT"})
# HOLD is a transient state, never a surviving disposition.
TARGETLESS_CLASSES = frozenset({"REHOME", "REJECT", "HOLD"})
REWRITE_REASONS = frozenset({
    "named_actor", "specimen_flavor", "environment_leak",
    "over_length", "mislabeled_polarity", "voice",
})
REJECT_REASON_KINDS = frozenset({
    "fails_canon_only_baseline", "not_portable", "not_craft_scope",
    "belongs_to_history", "belongs_to_canon_workflow",
    "belongs_to_regression", "duplicate_of",
})
REHOME_DESTINATIONS = frozenset({"training_history", "canon_workflow", "regression"})
EXTRACT_DESTINATIONS = REHOME_DESTINATIONS
LEDGER_KEYS = frozenset({
    "domain", "legacy", "vnext", "decompositions", "dispositions", "holds",
    "accretion_entries",
})
LEGACY_BLOCK_KEYS = frozenset({
    "memory_schema_version", "memory_version", "entry_count",
    "entry_hashes", "admissible_event_ids",
})
VNEXT_BLOCK_KEYS = frozenset({"memory_schema_version", "claim_count"})
DECOMPOSITION_KEYS = frozenset({
    "legacy_entry", "legacy_sha256", "propositions", "sentence_map",
    "second_reader",
})
# `second_reader` is presence-only and appears only where accretion_entries
# declares the entry an accretion narrative; every other key is required.
DECOMPOSITION_REQUIRED_KEYS = DECOMPOSITION_KEYS - {"second_reader"}
SENTENCE_ROW_KEYS = frozenset({"sentence", "propositions", "non_propositional"})
# The closed non-propositional reason set of R2.5 §7.2, in the specification's
# own order. Closed here, never extended: a sentence that fits no reason is a
# decomposition problem for judgment, not permission to widen the vocabulary.
NON_PROPOSITIONAL_REASONS = (
    "evidence_recitation", "episode_narrative", "restatement",
    "environment_context", "canon_restatement",
)
NON_PROPOSITIONAL_REASON_SET = frozenset(NON_PROPOSITIONAL_REASONS)
PROPOSITION_KEYS = frozenset({"id", "text"})
HOLD_KEYS = frozenset({"question", "must_answer"})
SHED_KEYS = frozenset({"proposition", "shed_reason"})
DISPOSITION_COMMON_KEYS = frozenset({"proposition", "class"})
DISPOSITION_EXTRA_KEYS = {
    "CARRY": frozenset({"targets", "note"}),
    "REWRITE": frozenset({"targets", "rewrite_reason", "note"}),
    "SPLIT": frozenset({"targets", "note"}),
    "CONDENSE": frozenset({"targets", "shed", "note"}),
    "EXTRACT": frozenset({"targets", "destination", "note"}),
    "REHOME": frozenset({"destination", "pointer", "hand_off", "note"}),
    "REJECT": frozenset({"reason_kind", "reason", "duplicate_of", "note"}),
    "HOLD": frozenset({"question", "must_answer", "note"}),
}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
PROPOSITION_INDEX_RE = re.compile(r"^#p[1-9][0-9]*$")
ACCOUNT_CHECKS = ("A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10")


def _non_empty_str(value: Any) -> bool:
    return isinstance(value, str) and bool(value)


def _is_count(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def ledger_schema_problems(ledger: dict[str, Any]) -> list[str]:
    """Every way the ledger disagrees with its schema.

    Shape, closed vocabularies, and identity format only. A malformed artifact
    fails loudly here and the accounting checks never run on it: the checker
    refuses rather than normalizes, drops, or repairs anything.
    """
    problems: list[str] = []

    def require_keys(mapping: dict, allowed: Any, required: Any, where: str) -> None:
        for key in sorted(required - set(mapping)):
            problems.append(f"{where}: required key '{key}' is missing")
        for key in sorted(set(mapping) - allowed):
            problems.append(f"{where}: unknown key '{key}'")

    require_keys(ledger, LEDGER_KEYS, LEDGER_KEYS, "ledger")

    legacy = ledger.get("legacy")
    if not isinstance(legacy, dict):
        problems.append("ledger: legacy must be a mapping")
    else:
        require_keys(legacy, LEGACY_BLOCK_KEYS, LEGACY_BLOCK_KEYS, "ledger.legacy")
        if legacy.get("memory_schema_version") not in SUPPORTED_SCHEMA_VERSIONS:
            problems.append(
                f"ledger.legacy: memory_schema_version "
                f"{legacy.get('memory_schema_version')!r} is not a legacy v1/v2 input version"
            )
        if not isinstance(legacy.get("memory_version"), int) or isinstance(
            legacy.get("memory_version"), bool
        ):
            problems.append("ledger.legacy: memory_version must be an integer")
        entry_count = legacy.get("entry_count")
        if not _is_count(entry_count):
            problems.append("ledger.legacy: entry_count must be a non-negative integer")
        hashes = legacy.get("entry_hashes")
        if not isinstance(hashes, dict) or not hashes:
            problems.append(
                "ledger.legacy: entry_hashes must be a non-empty mapping of "
                "legacy entry id to sha256"
            )
        else:
            for entry_id, digest in hashes.items():
                if not _non_empty_str(entry_id):
                    problems.append(
                        "ledger.legacy: entry_hashes carries an entry id that "
                        "is not a non-empty string"
                    )
                if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest):
                    problems.append(
                        f"ledger.legacy: entry_hashes['{entry_id}'] is not a "
                        "lowercase sha256 digest"
                    )
            if _is_count(entry_count) and len(hashes) != entry_count:
                problems.append(
                    f"ledger.legacy: entry_count {entry_count} disagrees with "
                    f"{len(hashes)} recorded hash(es)"
                )
        events = legacy.get("admissible_event_ids")
        if not isinstance(events, list) or any(
            not _non_empty_str(event) for event in events
        ):
            problems.append(
                "ledger.legacy: admissible_event_ids must be a list of "
                "non-empty strings"
            )

    vnext = ledger.get("vnext")
    if not isinstance(vnext, dict):
        problems.append("ledger: vnext must be a mapping")
    else:
        require_keys(vnext, VNEXT_BLOCK_KEYS, VNEXT_BLOCK_KEYS, "ledger.vnext")
        if vnext.get("memory_schema_version") != 3:
            problems.append(
                f"ledger.vnext: memory_schema_version must be 3, not "
                f"{vnext.get('memory_schema_version')!r}"
            )
        if not _is_count(vnext.get("claim_count")):
            problems.append("ledger.vnext: claim_count must be a non-negative integer")

    seen_proposition_ids: set[str] = set()
    decompositions = ledger.get("decompositions")
    if not isinstance(decompositions, list):
        problems.append("ledger: decompositions must be a list")
    else:
        for position, item in enumerate(decompositions):
            where = f"ledger.decompositions[{position}]"
            if not isinstance(item, dict):
                problems.append(f"{where}: must be a mapping")
                continue
            require_keys(item, DECOMPOSITION_KEYS, DECOMPOSITION_REQUIRED_KEYS, where)
            entry_id = item.get("legacy_entry")
            if not _non_empty_str(entry_id):
                problems.append(f"{where}: legacy_entry must be a non-empty string")
            digest = item.get("legacy_sha256")
            if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest):
                problems.append(f"{where}: legacy_sha256 is not a lowercase sha256 digest")
            sentence_map = item.get("sentence_map")
            if not isinstance(sentence_map, list):
                problems.append(
                    f"{where}: sentence_map must be a list carrying one record "
                    "per source sentence"
                )
            else:
                for s_position, row in enumerate(sentence_map):
                    s_where = f"{where}.sentence_map[{s_position}]"
                    if not isinstance(row, dict):
                        problems.append(f"{s_where}: must be a mapping")
                        continue
                    require_keys(row, SENTENCE_ROW_KEYS, frozenset({"sentence"}), s_where)
                    number = row.get("sentence")
                    if (
                        not isinstance(number, int)
                        or isinstance(number, bool)
                        or number < 1
                    ):
                        problems.append(
                            f"{s_where}: sentence must be a positive integer "
                            "sentence number"
                        )
                    has_propositions = "propositions" in row
                    has_reason = "non_propositional" in row
                    if has_propositions and has_reason:
                        problems.append(
                            f"{s_where}: carries both propositions and "
                            "non_propositional; a sentence is attributed to one "
                            "mode or the other, never both"
                        )
                    elif not has_propositions and not has_reason:
                        problems.append(
                            f"{s_where}: carries neither propositions nor "
                            "non_propositional; every sentence is attributed"
                        )
                    if has_propositions:
                        references = row["propositions"]
                        if not isinstance(references, list) or not references:
                            problems.append(
                                f"{s_where}: propositions must be a non-empty "
                                "list of proposition ids"
                            )
                        elif any(not _non_empty_str(ref) for ref in references):
                            problems.append(
                                f"{s_where}: propositions must be a list of "
                                "non-empty strings"
                            )
                        elif len(set(references)) != len(references):
                            problems.append(
                                f"{s_where}: propositions repeats an id; each "
                                "reference is recorded once"
                            )
                    if has_reason and (
                        not _non_empty_str(row["non_propositional"])
                        or row["non_propositional"] not in NON_PROPOSITIONAL_REASON_SET
                    ):
                        problems.append(
                            f"{s_where}: non_propositional "
                            f"{row['non_propositional']!r} is not in the closed "
                            f"set {list(NON_PROPOSITIONAL_REASONS)}"
                        )
            if "second_reader" in item and item["second_reader"] is not True:
                problems.append(
                    f"{where}: second_reader must be `true`; the mark is "
                    "presence-only and the script reads no second decomposition"
                )
            propositions = item.get("propositions")
            if not isinstance(propositions, list) or not propositions:
                problems.append(
                    f"{where}: propositions must be a non-empty list; even a "
                    "single-proposition decomposition is written out explicitly"
                )
                continue
            for p_position, proposition in enumerate(propositions):
                p_where = f"{where}.propositions[{p_position}]"
                if not isinstance(proposition, dict):
                    problems.append(f"{p_where}: must be a mapping")
                    continue
                require_keys(proposition, PROPOSITION_KEYS, PROPOSITION_KEYS, p_where)
                proposition_id = proposition.get("id")
                if not _non_empty_str(proposition_id):
                    problems.append(f"{p_where}: id must be a non-empty string")
                elif _non_empty_str(entry_id):
                    prefix = f"{entry_id}#"
                    if not proposition_id.startswith(prefix) or not (
                        PROPOSITION_INDEX_RE.fullmatch(proposition_id[len(entry_id):])
                    ):
                        problems.append(
                            f"{p_where}: id '{proposition_id}' is not shaped "
                            f"'<{entry_id}>#p<n>'; a proposition id carries its "
                            "legacy entry id and a positive index"
                        )
                if proposition_id in seen_proposition_ids:
                    problems.append(
                        f"{p_where}: proposition id '{proposition_id}' appears "
                        "more than once in the ledger"
                    )
                if _non_empty_str(proposition_id):
                    seen_proposition_ids.add(proposition_id)
                if not _non_empty_str(proposition.get("text")):
                    problems.append(f"{p_where}: text must be a non-empty string")

    dispositions = ledger.get("dispositions")
    if not isinstance(dispositions, list):
        problems.append("ledger: dispositions must be a list")
    else:
        for position, item in enumerate(dispositions):
            where = f"ledger.dispositions[{position}]"
            if not isinstance(item, dict):
                problems.append(f"{where}: must be a mapping")
                continue
            cls = item.get("class")
            allowed = DISPOSITION_COMMON_KEYS | DISPOSITION_EXTRA_KEYS.get(
                cls, frozenset()
            )
            require_keys(item, allowed, DISPOSITION_COMMON_KEYS, where)
            if not _non_empty_str(cls) or cls not in DISPOSITION_CLASSES:
                problems.append(
                    f"{where}: class {cls!r} is not in the closed disposition "
                    f"class vocabulary {list(DISPOSITION_CLASS_ORDER)}"
                )
            if not _non_empty_str(item.get("proposition")):
                problems.append(f"{where}: proposition must be a non-empty string")
            if "targets" in item:
                targets = item["targets"]
                if (
                    not isinstance(targets, list)
                    or not targets
                    or any(not _non_empty_str(target) for target in targets)
                ):
                    problems.append(
                        f"{where}: targets must be a non-empty list of "
                        "non-empty claim ids"
                    )
            if "rewrite_reason" in item and (
                not _non_empty_str(item["rewrite_reason"])
                or item["rewrite_reason"] not in REWRITE_REASONS
            ):
                problems.append(
                    f"{where}: rewrite_reason {item['rewrite_reason']!r} is not "
                    f"in the closed set {sorted(REWRITE_REASONS)}"
                )
            if "destination" in item:
                vocabulary = (
                    EXTRACT_DESTINATIONS if cls == "EXTRACT" else REHOME_DESTINATIONS
                )
                if not _non_empty_str(item["destination"]) or (
                    item["destination"] not in vocabulary
                ):
                    problems.append(
                        f"{where}: destination {item['destination']!r} is not in "
                        f"the closed destination authority set {sorted(vocabulary)}"
                    )
            if "reason_kind" in item and (
                not _non_empty_str(item["reason_kind"])
                or item["reason_kind"] not in REJECT_REASON_KINDS
            ):
                problems.append(
                    f"{where}: reason_kind {item['reason_kind']!r} is not in the "
                    f"closed set {sorted(REJECT_REASON_KINDS)}"
                )
            for key in ("reason", "duplicate_of", "pointer", "hand_off", "note"):
                if key in item and not _non_empty_str(item[key]):
                    problems.append(f"{where}: {key} must be a non-empty string")
            if "question" in item and not _non_empty_str(item["question"]):
                problems.append(f"{where}: question must be a non-empty string")
            if "must_answer" in item and not _non_empty_str(item["must_answer"]):
                problems.append(f"{where}: must_answer must be a non-empty string")
            if "shed" in item:
                shed = item["shed"]
                if not isinstance(shed, list):
                    problems.append(f"{where}: shed must be a list")
                else:
                    for s_position, shed_item in enumerate(shed):
                        s_where = f"{where}.shed[{s_position}]"
                        if not isinstance(shed_item, dict):
                            problems.append(f"{s_where}: must be a mapping")
                            continue
                        require_keys(shed_item, SHED_KEYS, SHED_KEYS, s_where)
                        if not _non_empty_str(shed_item.get("proposition")):
                            problems.append(
                                f"{s_where}: proposition must be a non-empty string"
                            )
                        if not _non_empty_str(shed_item.get("shed_reason")):
                            problems.append(
                                f"{s_where}: shed_reason must be a non-empty string"
                            )

    holds = ledger.get("holds")
    if not isinstance(holds, list):
        problems.append("ledger: holds must be a list")
    else:
        for position, item in enumerate(holds):
            where = f"ledger.holds[{position}]"
            if not isinstance(item, dict):
                problems.append(f"{where}: must be a mapping")
                continue
            require_keys(item, HOLD_KEYS, HOLD_KEYS, where)
            for key in sorted(HOLD_KEYS):
                if key in item and not _non_empty_str(item[key]):
                    problems.append(f"{where}: {key} must be a non-empty string")

    # The ledger's record of which entries require a second independent
    # decomposition (R2.5 §7.2). Which entries those are is judgment; the
    # schema accepts only the declaration's shape, and A9 checks the
    # per-entry marks against it.
    accretion = ledger.get("accretion_entries")
    if not isinstance(accretion, list):
        problems.append("ledger: accretion_entries must be a list")
    else:
        seen_accretion: set[str] = set()
        for position, entry_id in enumerate(accretion):
            if not _non_empty_str(entry_id):
                problems.append(
                    f"ledger.accretion_entries[{position}] must be a non-empty "
                    "legacy entry id"
                )
            elif entry_id in seen_accretion:
                problems.append(
                    f"ledger: accretion_entries names '{entry_id}' more than once"
                )
            else:
                seen_accretion.add(entry_id)

    return problems


def candidate_store_claim_ids(store_path: Path) -> list[str]:
    """The candidate v3 store's claim ids, in file order.

    Account reads the candidate store for claim existence only (A5, A6, A8).
    It does not run the v3 validator — that is the VERIFY gate's job — but it
    refuses anything that is not a parseable candidate v3 store carrying a
    non-empty id on every claim, so the accounting never runs against a file
    whose claim set is ambiguous.
    """
    path = Path(store_path)
    if not path.is_file():
        raise MigrateError_(
            f"no candidate store at {path.as_posix()}; account checks the "
            "ledger's targets against the candidate v3 store"
        )
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise MigrateError_(f"{path.as_posix()}: candidate store must be a mapping")
    if data.get("memory_schema_version") != 3:
        raise MigrateError_(
            f"{path.as_posix()}: account reads a candidate v3 store; "
            f"memory_schema_version is {data.get('memory_schema_version')!r}"
        )
    claims = data.get("claims")
    if not isinstance(claims, list):
        raise MigrateError_(f"{path.as_posix()}: candidate store has no claims list")
    ids: list[str] = []
    for index, claim in enumerate(claims):
        if not isinstance(claim, dict):
            raise MigrateError_(
                f"{path.as_posix()}: claim #{index + 1} is not a mapping"
            )
        claim_id = claim.get("id")
        if not _non_empty_str(claim_id):
            raise MigrateError_(
                f"{path.as_posix()}: claim #{index + 1} has no non-empty id"
            )
        if claim_id in ids:
            raise MigrateError_(
                f"{path.as_posix()}: duplicate claim id '{claim_id}' in the "
                "candidate store"
            )
        ids.append(claim_id)
    return ids


# --- T15: the sentence inventory and the A9 under-decomposition check --------
#
# A9 is coverage, not comprehension. A1-A8 are airtight downstream of
# decomposition and have no purchase on it: an entry that actually makes three
# propositions but records two fails nothing, because the lost proposition was
# never written down. The sentence map is the counter — every source sentence
# must be attributed, mechanically — and this section checks that map against
# the frozen entry bytes. It never decides what a sentence means, which
# proposition it belongs to, or whether a recorded reason is honest: those are
# judgment, and the check exists to make an omission reviewable, not to prove
# a decomposition right (R2.5 §7.2, §7.5).

def entry_fields(block: bytes) -> dict[str, Any] | None:
    """One frozen entry block parsed back into its fields, or nothing.

    The same cut `freeze` hashes (the entry's serialized bytes at its YAML
    node boundaries), so the sentence inventory A9 derives here and the hash
    A2 re-verifies there cover the same bytes: source drift cannot move one
    without moving the other.
    """
    parsed = yaml.safe_load(block.decode("utf-8"))
    entry = parsed[0] if isinstance(parsed, list) else parsed
    return entry if isinstance(entry, dict) else None


def entry_sentence_texts(entry: dict[str, Any]) -> list[str]:
    """The entry's source sentences, numbered from 1 in the ticket's order.

    `observation`, `boundary`, and `diagnosis.hypothesis` are concatenated as
    one text in that order — §7.4 step 1 reads the three fields together as
    one semantic source, so the inventory keeps no field provenance and never
    slices per field — then split with `validate.py`'s SENTENCE_RE: the
    repository's one sentence splitter, imported so segmentation has a single
    deterministic implementation. Each segment is stripped and empty segments
    are dropped; everything else is kept verbatim. Unchanged bytes therefore
    yield an identical inventory on every run, in every locale, with no model
    call, tokenizer, or host-specific parsing in the path.
    """
    parts: list[str] = []
    for value in (entry.get("observation"), entry.get("boundary")):
        if isinstance(value, str) and value:
            parts.append(value)
    diagnosis = entry.get("diagnosis")
    if isinstance(diagnosis, dict):
        hypothesis = diagnosis.get("hypothesis")
        if isinstance(hypothesis, str) and hypothesis:
            parts.append(hypothesis)
    texts: list[str] = []
    for segment in SENTENCE_RE.split("\n".join(parts)):
        sentence = segment.strip()
        if sentence:
            texts.append(sentence)
    return texts


def sentence_coverage_problems(
    ledger: dict[str, Any],
    domain_dir: Path,
    all_proposition_ids: set[str],
) -> tuple[list[str], str]:
    """Every A9 failure for one ledger, plus the report `account` prints.

    Three properties, all mechanical:

    * every sentence of every frozen entry appears exactly once in that
      entry's `sentence_map` — no omission, no duplicate row, no index
      outside the inventory the frozen bytes yield;
    * every proposition reference resolves to a proposition id recorded in
      that same decomposition, never another entry's and never an unrecorded
      one;
    * every entry declared in `accretion_entries` carries `second_reader` on
      its decomposition record, and no undeclared record carries the mark —
      the script records and checks the mark's presence and never attempts
      the second reading itself.

    Nothing here reads a sentence's meaning. An attribution the checker
    accepts can still be wrong; that is precisely why it stays reviewable
    rather than proved (§7.5).
    """
    entry_hashes = ledger["legacy"]["entry_hashes"]
    decompositions = ledger["decompositions"]
    declared_ids = set(ledger["accretion_entries"])
    problems: list[str] = []
    sentences_total = 0
    entries_checked = 0

    try:
        blocks = entry_serialized_blocks(domain_dir / "skill_memory.yaml")
    except (MigrateError_, OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        return (
            [
                "the frozen legacy entries no longer load, so no sentence "
                f"inventory can be derived: {exc}"
            ],
            "sentence inventory unavailable",
        )

    for entry_id in sorted(entry_hashes):
        block = blocks.get(entry_id)
        entry = entry_fields(block) if block is not None else None
        if entry is None:
            # Absent or unparseable bytes are source drift, and A2 owns that
            # detector. A9 never substitutes an inventory it did not derive
            # from the frozen store.
            continue
        records = [
            item for item in decompositions if item.get("legacy_entry") == entry_id
        ]
        sentences = entry_sentence_texts(entry)
        entries_checked += 1
        sentences_total += len(sentences)
        expected = set(range(1, len(sentences) + 1))
        if not records:
            problems.append(
                f"legacy entry '{entry_id}' has no decomposition carrying a "
                f"sentence map; {len(sentences)} sentence(s) are unaccounted"
            )
            continue
        for record in records:
            recorded_ids = {
                proposition["id"] for proposition in record["propositions"]
            }
            counted: dict[int, int] = {}
            for row in record["sentence_map"]:
                number = row["sentence"]
                counted[number] = counted.get(number, 0) + 1
                for proposition_id in row.get("propositions") or []:
                    if proposition_id in recorded_ids:
                        continue
                    if proposition_id not in all_proposition_ids:
                        problems.append(
                            f"legacy entry '{entry_id}' sentence {number} "
                            f"references unknown proposition '{proposition_id}'"
                        )
                    elif proposition_id.split("#", 1)[0] != entry_id:
                        problems.append(
                            f"legacy entry '{entry_id}' sentence {number} "
                            f"references proposition '{proposition_id}', which "
                            "belongs to another entry's decomposition"
                        )
                    else:
                        problems.append(
                            f"legacy entry '{entry_id}' sentence {number} "
                            f"references proposition '{proposition_id}', which "
                            "is not recorded in this decomposition record"
                        )
            for number in sorted(counted):
                if counted[number] > 1:
                    problems.append(
                        f"legacy entry '{entry_id}' sentence {number} appears "
                        "more than once in its sentence map"
                    )
                if number not in expected:
                    problems.append(
                        f"legacy entry '{entry_id}' sentence {number} is out of "
                        f"range; the entry has {len(sentences)} sentence(s)"
                    )
            for number in sorted(expected - set(counted)):
                problems.append(
                    f"legacy entry '{entry_id}' sentence {number} is not "
                    "accounted for"
                )

    marks = 0
    for record in decompositions:
        if "second_reader" not in record:
            continue
        marks += 1
        entry_id = record.get("legacy_entry")
        if entry_id not in declared_ids:
            problems.append(
                f"decomposition record '{entry_id}' carries the second-reader "
                "mark, but accretion_entries does not declare it an accretion "
                "entry"
            )
    for entry_id in sorted(declared_ids):
        if entry_id not in entry_hashes:
            problems.append(
                f"accretion_entries names '{entry_id}', which is not a legacy "
                "entry recorded at FREEZE"
            )
            continue
        records = [
            item for item in decompositions if item.get("legacy_entry") == entry_id
        ]
        if not records or any("second_reader" not in record for record in records):
            problems.append(
                f"legacy entry '{entry_id}' requires a second independent "
                "decomposition, but its ledger record lacks the second-reader "
                "mark"
            )

    report = (
        f"{sentences_total} sentence(s) in {entries_checked} entr(ies) each "
        f"accounted exactly once; {len(declared_ids)} accretion entr(ies) "
        f"declared, {marks} second-reader mark(s) recorded"
    )
    return problems, report


def account_problems(
    ledger: dict[str, Any],
    domain_dir: Path,
    store_claim_ids: list[str],
) -> tuple[list[tuple[str, str]], str, str]:
    """Every A1-A10 failure as (check, message), plus the A8 and A9 reports.

    Each check is reported independently; one broken fixture names the checks
    it actually breaks. Nothing here infers a disposition, compares a shared
    target against any source id, reads any numeric or lexical relationship
    between a legacy id and a target id (§7.5 traceability note), or reads
    any sentence's meaning: A9 checks coverage and references against the
    frozen bytes, never the truth of an attribution.
    """
    domain = domain_dir.name
    legacy = ledger["legacy"]
    decompositions = ledger["decompositions"]
    dispositions = ledger["dispositions"]
    holds = ledger["holds"]
    failures: list[tuple[str, str]] = []

    def fail(check: str, message: str) -> None:
        failures.append((check, message))

    entry_hashes: dict = legacy["entry_hashes"]

    # A1 — every legacy entry id appears exactly once in decompositions.
    decomposed_entries = [item["legacy_entry"] for item in decompositions]
    for entry_id in sorted(entry_hashes):
        count = decomposed_entries.count(entry_id)
        if count == 0:
            fail("A1", f"legacy entry '{entry_id}' has no decomposition")
        elif count > 1:
            fail(
                "A1",
                f"legacy entry '{entry_id}' appears in {count} decompositions; "
                "exactly once is required",
            )
    for entry_id in decomposed_entries:
        if entry_id not in entry_hashes:
            fail(
                "A1",
                f"decomposition names '{entry_id}', which is not a legacy entry "
                "recorded at FREEZE",
            )

    # A2 — the recorded hashes still match the legacy store (T13's mechanics).
    if legacy.get("memory_schema_version") not in SUPPORTED_SCHEMA_VERSIONS:
        fail(
            "A2",
            f"ledger records memory_schema_version "
            f"{legacy.get('memory_schema_version')}; A2 verifies a frozen "
            "legacy v1/v2 input",
        )
    else:
        for problem in hash_problems(domain_dir, legacy):
            fail("A2", problem)

    # A3 — every proposition has exactly one disposition. Coverage comes from
    # a disposition record's own `proposition` or from a CONDENSE shed entry;
    # either way, once and only once.
    universe = {
        proposition["id"]
        for item in decompositions
        for proposition in item["propositions"]
    }
    coverage: dict[str, int] = {proposition_id: 0 for proposition_id in universe}
    for position, record in enumerate(dispositions):
        where = f"dispositions[{position}] ({record.get('proposition')})"
        proposition_id = record.get("proposition")
        if proposition_id not in universe:
            fail(
                "A3",
                f"{where} names proposition '{proposition_id}', which is absent "
                "from this ledger's decompositions",
            )
        else:
            coverage[proposition_id] += 1
        if record.get("class") == "CONDENSE":
            for shed_item in record.get("shed") or []:
                shed_proposition = (
                    shed_item.get("proposition") if isinstance(shed_item, dict) else None
                )
                if shed_proposition not in universe:
                    fail(
                        "A3",
                        f"{where} sheds proposition '{shed_proposition}', which "
                        "is absent from this ledger's decompositions",
                    )
                else:
                    coverage[shed_proposition] += 1
    for proposition_id in sorted(coverage):
        if coverage[proposition_id] == 0:
            fail("A3", f"proposition '{proposition_id}' has no disposition")
        elif coverage[proposition_id] > 1:
            fail(
                "A3",
                f"proposition '{proposition_id}' is dispositioned "
                f"{coverage[proposition_id]} times; exactly one disposition "
                "is required",
            )

    # A4 — every disposition carries its class's obligation. Vocabulary
    # membership is the schema validator's; presence and cardinality are here.
    for position, record in enumerate(dispositions):
        where = f"dispositions[{position}] ({record.get('proposition')})"
        cls = record.get("class")
        targets = record.get("targets")
        if cls in TARGETLESS_CLASSES and targets is not None:
            fail(
                "A4",
                f"{where}: class {cls} carries targets; no Memory claim "
                "survives this disposition",
            )
        if cls in ("CARRY", "REWRITE", "CONDENSE", "EXTRACT"):
            if targets is None:
                fail("A4", f"{where}: class {cls} requires exactly one target claim id")
            elif len(targets) != 1:
                fail(
                    "A4",
                    f"{where}: class {cls} requires exactly one target claim id, "
                    f"not {len(targets)}",
                )
        if cls == "SPLIT":
            if targets is None:
                fail("A4", f"{where}: class SPLIT requires at least 2 target claim ids")
            elif len(targets) < 2:
                fail(
                    "A4",
                    f"{where}: class SPLIT requires at least 2 target claim ids, "
                    f"not {len(targets)}",
                )
        if cls == "REWRITE" and "rewrite_reason" not in record:
            fail(
                "A4",
                f"{where}: class REWRITE requires a rewrite_reason from the "
                "closed set",
            )
        if cls == "EXTRACT" and "destination" not in record:
            fail(
                "A4",
                f"{where}: class EXTRACT requires a destination authority for "
                "the episode",
            )
        if cls == "REHOME":
            if "destination" not in record:
                fail("A4", f"{where}: class REHOME requires a destination authority")
            if not ("pointer" in record or "hand_off" in record):
                fail(
                    "A4",
                    f"{where}: class REHOME requires a pointer or a stated hand-off",
                )
        if cls == "REJECT":
            if "reason_kind" not in record:
                fail(
                    "A4",
                    f"{where}: class REJECT requires a reason_kind from the "
                    "closed set",
                )
            if "reason" not in record:
                fail("A4", f"{where}: class REJECT requires a prose reason")
            if record.get("reason_kind") == "duplicate_of" and not record.get(
                "duplicate_of"
            ):
                fail(
                    "A4",
                    f"{where}: reason_kind duplicate_of requires the surviving "
                    "target claim id in duplicate_of",
                )
        if cls == "HOLD":
            if "question" not in record:
                fail("A4", f"{where}: class HOLD requires the unresolved question")
            if "must_answer" not in record:
                fail("A4", f"{where}: class HOLD requires who must answer")

    store_ids = set(store_claim_ids)

    # A5 — every target claim id exists and is non-empty in the new store.
    for position, record in enumerate(dispositions):
        where = f"dispositions[{position}] ({record.get('proposition')})"
        for target in record.get("targets") or []:
            if target not in store_ids:
                fail(
                    "A5",
                    f"{where}: target '{target}' does not exist in the "
                    "candidate store",
                )
        duplicate_of = record.get("duplicate_of")
        if _non_empty_str(duplicate_of) and duplicate_of not in store_ids:
            fail(
                "A5",
                f"{where}: duplicate_of '{duplicate_of}' does not exist in the "
                "candidate store",
            )

    # A6 — every claim in the new store is named as a target by at least one
    # disposition: no claim invented from nothing.
    named_targets = {
        target for record in dispositions for target in (record.get("targets") or [])
    }
    for claim_id in store_claim_ids:
        if claim_id not in named_targets:
            fail(
                "A6",
                f"claim '{claim_id}' in the candidate store is named by no "
                "disposition",
            )

    # A7 — zero HOLDs at completion, in the holds block or as a disposition.
    if holds:
        fail("A7", f"{len(holds)} hold(s) remain in the ledger; completion requires zero")
    for position, record in enumerate(dispositions):
        if record.get("class") == "HOLD":
            fail(
                "A7",
                f"dispositions[{position}] ({record.get('proposition')}) is "
                "still HOLD; completion requires zero HOLDs",
            )

    # A8 — counts reported and mutually consistent, stating the difference
    # where dispositions share a target (a merge) rather than asserting
    # equality. Only the two ledger-declared equalities are asserted here;
    # the 1:1 proposition/disposition pairing is A3's and the target/store
    # pairing is A5's and A6's.
    entry_count = legacy["entry_count"]
    class_counts = {cls: 0 for cls in DISPOSITION_CLASS_ORDER}
    for record in dispositions:
        cls = record.get("class")
        if cls in class_counts:
            class_counts[cls] += 1
    surviving = sum(class_counts[cls] for cls in SURVIVING_CLASSES)
    distinct_targets = len(named_targets)
    shared_targets = sum(
        1
        for target in named_targets
        if sum(
            1 for record in dispositions if target in (record.get("targets") or [])
        )
        > 1
    )
    multi_target_records = sum(
        1 for record in dispositions if len(record.get("targets") or []) > 1
    )
    declared_claims = ledger["vnext"]["claim_count"]
    a8_report = (
        f"entries {entry_count}; propositions {len(universe)}; dispositions "
        + ", ".join(
            f"{cls}: {class_counts[cls]}"
            for cls in DISPOSITION_CLASS_ORDER
            if class_counts[cls]
        )
        + f"; {surviving} surviving disposition(s) naming {distinct_targets} "
        f"distinct target claim(s); {shared_targets} target(s) shared across "
        f"dispositions (merge); {multi_target_records} multi-target "
        f"disposition(s) (split); candidate store claims {len(store_claim_ids)}; "
        f"vnext.claim_count {declared_claims}"
    )
    if entry_count != len(decompositions):
        fail(
            "A8",
            f"legacy entry_count {entry_count} disagrees with "
            f"{len(decompositions)} decomposition(s)",
        )
    if declared_claims != len(store_claim_ids):
        fail(
            "A8",
            f"vnext.claim_count {declared_claims} disagrees with "
            f"{len(store_claim_ids)} claim(s) in the candidate store",
        )

    # A9 — every sentence of every frozen entry accounted exactly once in
    # that entry's sentence_map, proposition references resolving inside the
    # same decomposition, and the second-reader mark present on every entry
    # declared accretion (T15). Coverage against the frozen bytes only.
    a9_problems, a9_report = sentence_coverage_problems(
        ledger, domain_dir, universe
    )
    for message in a9_problems:
        fail("A9", message)

    # A10 — every disposition target id is a well-formed vNext id for this
    # domain and equals no legacy entry id and no proposition id in this
    # ledger: no legacy id survives as a live claim id.
    for position, record in enumerate(dispositions):
        where = f"dispositions[{position}] ({record.get('proposition')})"
        references = list(record.get("targets") or [])
        duplicate_of = record.get("duplicate_of")
        if _non_empty_str(duplicate_of):
            references.append(duplicate_of)
        for claim_id in references:
            for problem in claim_id_problems(claim_id, domain):
                fail("A10", f"{where}: {problem}")
            if claim_id in entry_hashes:
                fail(
                    "A10",
                    f"{where}: '{claim_id}' equals a legacy entry id; no legacy "
                    "id survives as a live claim id",
                )
            if claim_id in universe:
                fail(
                    "A10",
                    f"{where}: '{claim_id}' equals a proposition id in this ledger",
                )

    return failures, a8_report, a9_report


# --- T16: the three reports, item-by-item loss signoff, and the VERIFY gate ---
#
# `report` derives the three §7.5 reports from the ledger alone: survival
# (every CARRY / REWRITE / SPLIT / CONDENSE / EXTRACT proposition and the
# target claim(s) it survives as), loss (every REJECT, every REHOME, and every
# proposition shed inside a CONDENSE, with its reason — the anti-silent-drop
# report), and re-homing (everything sent to another authority, with its
# destination and complete-or-owed hand-off status). The loss report is the
# signoff artifact: each item carries its own `signed_off` field and reviewer
# note, the schema has no document-level approval key, and regeneration
# refuses while existing reports would be overwritten so a signoff is never
# silently destroyed. `gate` is the single VERIFY-step entry point: it re-runs
# A1-A10 through the existing accounting checker (A2 source drift and A7
# HOLDs remain failures, never warnings), requires the loss artifact to equal
# the ledger's own loss set item by item with every item signed, runs the
# repository's actual v3 validator on the candidate store, and requires every
# FLAG to be cleared or individually accepted with a note. Nothing here writes
# under memory/, generates a reason or a note, decides whether a loss is
# acceptable, or offers a bulk-approval path: mechanical tooling proves each
# loss carries its signoff; whether the loss was right stays review judgment
# (R2.5 §7.5, criterion 45).

SURVIVING_REPORT_CLASSES = ("CARRY", "REWRITE", "SPLIT", "CONDENSE", "EXTRACT")
REPORT_FILENAMES = {
    "survival": "survival-{domain}.yaml",
    "loss": "loss-{domain}.yaml",
    "re-homing": "re-homing-{domain}.yaml",
}
REVIEW_FILENAME = "review-{domain}.yaml"
REPORT_ARTIFACT_KEYS = frozenset({"domain", "items"})
REVIEW_ARTIFACT_KEYS = frozenset({"domain", "flags"})
LOSS_SIGNOFF_KEYS = frozenset({"signed_off", "reviewer_note"})
FLAG_ROW_KEYS = frozenset({"flag", "accepted", "note"})
HAND_OFF_COMPLETE = "complete"
HAND_OFF_OWED = "owed"


def _present(mapping: dict[str, Any], key: str) -> dict[str, Any]:
    """Only the keys actually recorded, so a report row mirrors the ledger."""
    return {key: mapping[key]} if key in mapping else {}


def loss_items(ledger: dict[str, Any]) -> list[dict[str, Any]]:
    """Every loss-bearing disposition, one row per lost proposition (§7.5).

    Three populations, kept distinct: every REJECT (nothing survives anywhere
    under that disposition), every REHOME (content survives under another
    authority but leaves current Memory), and every proposition shed inside a
    CONDENSE (the condensed target survives; the shed material does not, and
    a surviving target never excuses its omission). An EXTRACT is not a loss:
    its residue survives as its target and its episode is routed, so it
    appears in the survival and re-homing reports instead. Derived from
    `dispositions` alone — never a second hand-maintained record — so the
    report cannot drift from the accounting the gate re-checks. Rows sort by
    item id, and the item id is the lost proposition's id, which A3 proved
    unique across dispositions and sheds.
    """
    rows: list[dict[str, Any]] = []
    for record in ledger["dispositions"]:
        cls = record.get("class")
        if cls == "REJECT":
            rows.append({
                "item": record["proposition"],
                "class": "REJECT",
                "reason_kind": record["reason_kind"],
                "reason": record["reason"],
                **_present(record, "duplicate_of"),
                **_present(record, "note"),
            })
        elif cls == "REHOME":
            rows.append({
                "item": record["proposition"],
                "class": "REHOME",
                "destination": record["destination"],
                **_present(record, "pointer"),
                **_present(record, "hand_off"),
                **_present(record, "note"),
            })
        elif cls == "CONDENSE":
            for shed_item in record.get("shed") or []:
                rows.append({
                    "item": shed_item["proposition"],
                    "class": "CONDENSE",
                    "via": record["proposition"],
                    "shed_reason": shed_item["shed_reason"],
                    **_present(record, "note"),
                })
    rows.sort(key=lambda row: row["item"])
    return rows


def survival_report_document(ledger: dict[str, Any]) -> dict[str, Any]:
    """Every surviving proposition and the target claim(s) it survives as.

    CARRY, REWRITE, SPLIT, CONDENSE, and EXTRACT — the five classes whose
    dispositions name Memory targets. A SPLIT row carries its full target
    list; a CONDENSE row carries the one target its proposition condenses
    into (its sheds are loss rows, not survival rows); an EXTRACT row carries
    the residue target and the episode's destination. No one-to-one shape is
    imposed: a merge's shared target appears on each surviving proposition,
    and a split's targets appear together, exactly as the ledger records them
    (§7.3, §7.5).
    """
    items: list[dict[str, Any]] = []
    for record in ledger["dispositions"]:
        cls = record.get("class")
        if cls not in SURVIVING_REPORT_CLASSES:
            continue
        row: dict[str, Any] = {
            "proposition": record["proposition"],
            "class": cls,
            "targets": list(record["targets"]),
        }
        if cls == "REWRITE":
            row["rewrite_reason"] = record["rewrite_reason"]
        if cls == "EXTRACT":
            row["destination"] = record["destination"]
        if "note" in record:
            row["note"] = record["note"]
        items.append(row)
    items.sort(key=lambda row: row["proposition"])
    return {"domain": ledger["domain"], "items": items}


def loss_report_document(ledger: dict[str, Any]) -> dict[str, Any]:
    """The loss report: derived items, each with an empty per-item signoff.

    The signoff scaffold is fields, never content: `signed_off` starts false
    and `reviewer_note` starts empty, and this tool never fills either — the
    script refuses an unsigned item at the gate; it never generates the
    signoff. There is no document-level approval key in the artifact schema,
    so the only way to approve a loss is to sign its own row (criterion 45).
    """
    items = [
        {**row, "signed_off": False, "reviewer_note": ""}
        for row in loss_items(ledger)
    ]
    return {"domain": ledger["domain"], "items": items}


def rehoming_report_document(ledger: dict[str, Any]) -> dict[str, Any]:
    """Everything sent to another authority, with destination and status.

    REHOME rows leave current Memory entirely; EXTRACT rows route the episode
    while the distilled residue survives as the disposition's target, so the
    two never blur and a REJECT never appears here — a rejected proposition
    survives under no authority. The status is derived from the ledger's own
    obligation vocabulary, never judged: A4 accepts a REHOME with a pointer
    or a stated hand-off, and the difference is exactly named-vs-stated — a
    recorded `hand_off` is complete, a pointer-only REHOME is owed — while an
    EXTRACT's destination is A4-mandatory, so its routing decision is
    recorded and therefore complete.
    """
    rows: list[dict[str, Any]] = []
    for record in ledger["dispositions"]:
        cls = record.get("class")
        if cls == "REHOME":
            rows.append({
                "proposition": record["proposition"],
                "class": "REHOME",
                "destination": record["destination"],
                **_present(record, "pointer"),
                **_present(record, "hand_off"),
                **_present(record, "note"),
                "hand_off_status": (
                    HAND_OFF_COMPLETE if "hand_off" in record else HAND_OFF_OWED
                ),
            })
        elif cls == "EXTRACT":
            rows.append({
                "proposition": record["proposition"],
                "class": "EXTRACT",
                "destination": record["destination"],
                "targets": list(record["targets"]),
                **_present(record, "note"),
                "hand_off_status": HAND_OFF_COMPLETE,
            })
    rows.sort(key=lambda row: row["proposition"])
    return {"domain": ledger["domain"], "items": rows}


def report_path(ledger_dir: Path, kind: str, domain: str) -> Path:
    return Path(ledger_dir) / REPORT_FILENAMES[kind].format(domain=domain)


def review_path(ledger_dir: Path, domain: str) -> Path:
    return Path(ledger_dir) / REVIEW_FILENAME.format(domain=domain)


def write_report_set(
    ledger_dir: Path, ledger: dict[str, Any]
) -> list[tuple[str, Path, int]]:
    """Derive and write all three reports, or none of them.

    Inputs are schema-checked by the caller and every document is derived
    before the first write; an existing artifact refuses the whole set, so a
    regeneration can never silently destroy a reviewer's signoffs — the
    operator removes the existing reports explicitly, re-reports, and re-signs.
    Each file is written atomically, the same pattern the ledger uses.
    """
    domain = ledger["domain"]
    order = ("survival", "loss", "re-homing")
    documents: dict[str, dict[str, Any]] = {
        "survival": survival_report_document(ledger),
        "loss": loss_report_document(ledger),
        "re-homing": rehoming_report_document(ledger),
    }
    paths = {kind: report_path(ledger_dir, kind, domain) for kind in order}
    existing = [paths[kind] for kind in order if paths[kind].exists()]
    if existing:
        raise MigrateError_(
            "refused: "
            + ", ".join(path.as_posix() for path in existing)
            + " already exists; regenerating reports replaces signoff state, so "
            "the operator removes the existing artifacts first"
        )
    written: list[tuple[str, Path, int]] = []
    for kind in order:
        write_yaml_atomic(paths[kind], documents[kind])
        written.append((kind, paths[kind], len(documents[kind]["items"])))
    return written


def _load_yaml_mapping(path: Path, what: str) -> dict[str, Any]:
    if not path.is_file():
        raise MigrateError_(f"no {what} at {path.as_posix()}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise MigrateError_(f"{path.as_posix()}: {what} must be a mapping")
    return data


def loss_artifact_problems(
    document: dict[str, Any],
    domain: str,
    derived: list[dict[str, Any]],
    path: Path,
) -> list[str]:
    """Every way the signed loss artifact disagrees with the ledger.

    Exact-set equality in both directions: every derived loss item appears
    exactly once with its ledger fields unchanged and its own signoff, and no
    row exists for a proposition the ledger does not loss. A row whose reason
    was edited after derivation, a row naming something that is not a loss, a
    missing row, a duplicate row, an extra top-level approval key, a
    `signed_off` that is not the literal true, or an empty reviewer note —
    each refuses. The script never decides whether a loss is acceptable; it
    only proves the reviewer signed the exact losses the ledger records, item
    by item (criterion 45).
    """
    problems: list[str] = []
    label = path.as_posix()
    for key in sorted(set(document) - REPORT_ARTIFACT_KEYS):
        problems.append(
            f"{label}: unknown top-level key '{key}'; there is no "
            "document-level approval, only per-item signoff"
        )
    if document.get("domain") != domain:
        problems.append(
            f"{label}: domain {document.get('domain')!r} does not match '{domain}'"
        )
    items = document.get("items")
    if not isinstance(items, list):
        problems.append(f"{label}: items must be a list")
        return problems
    derived_by_id = {row["item"]: row for row in derived}
    seen: set[str] = set()
    for position, row in enumerate(items):
        where = f"{label}: items[{position}]"
        if not isinstance(row, dict):
            problems.append(f"{where}: must be a mapping")
            continue
        item_id = row.get("item")
        if not _non_empty_str(item_id):
            problems.append(f"{where}: item must be a non-empty proposition id")
            continue
        if item_id in seen:
            problems.append(
                f"{where}: duplicate signoff row for '{item_id}'; one row per "
                "loss item"
            )
            continue
        seen.add(item_id)
        expected = derived_by_id.get(item_id)
        if expected is None:
            problems.append(
                f"{where}: '{item_id}' is not a loss item of this ledger; a "
                "signoff must name exactly one real loss"
            )
            continue
        allowed = set(expected) | LOSS_SIGNOFF_KEYS
        for key in sorted(set(row) - allowed):
            problems.append(f"{where}: unknown key '{key}'")
        for key in sorted(set(expected) - set(row)):
            problems.append(f"{where}: required key '{key}' is missing")
        for key in sorted(set(expected) & set(row)):
            if row[key] != expected[key]:
                problems.append(
                    f"{where}: '{key}' no longer matches the ledger; the report "
                    "was mutated after derivation and its signoff no longer "
                    "covers this content"
                )
        if row.get("signed_off") is not True:
            problems.append(
                f"{where}: '{item_id}' is unsigned; every loss item carries "
                "its own signoff and no bulk approval exists"
            )
        if not _non_empty_str(row.get("reviewer_note")):
            problems.append(f"{where}: '{item_id}' has no reviewer note")
    for row in derived:
        if row["item"] not in seen:
            problems.append(
                f"{label}: loss item '{row['item']}' has no signoff row; every "
                "REJECT, REHOME, and CONDENSE shed is signed item by item"
            )
    return problems


def review_artifact_problems(
    document: dict[str, Any] | None,
    domain: str,
    flags: list[str],
    path: Path,
) -> list[str]:
    """Every way the FLAG review artifact disagrees with the validator.

    A FLAG is cleared by no longer firing, or accepted here with a note — one
    row per exact flag text, `accepted` literal true, note non-empty. A stale
    row refuses: an acceptance that no longer names a live FLAG is residue,
    not a record. An absent artifact is fine exactly when the validator emits
    no FLAGs. Nothing here edits the candidate store to silence a flag;
    acceptance is recorded beside the ledger, never inside Memory.
    """
    label = path.as_posix()
    if document is None:
        if not flags:
            return []
        return [
            f"{label}: no review artifact; every FLAG must be individually "
            "accepted with a note or cleared in the candidate store: "
            + " | ".join(flags)
        ]
    problems: list[str] = []
    for key in sorted(set(document) - REVIEW_ARTIFACT_KEYS):
        problems.append(f"{label}: unknown top-level key '{key}'")
    if document.get("domain") != domain:
        problems.append(
            f"{label}: domain {document.get('domain')!r} does not match '{domain}'"
        )
    rows = document.get("flags")
    if not isinstance(rows, list):
        problems.append(f"{label}: flags must be a list")
        return problems
    seen: set[str] = set()
    for position, row in enumerate(rows):
        where = f"{label}: flags[{position}]"
        if not isinstance(row, dict):
            problems.append(f"{where}: must be a mapping")
            continue
        for key in sorted(set(row) - FLAG_ROW_KEYS):
            problems.append(f"{where}: unknown key '{key}'")
        for key in sorted(FLAG_ROW_KEYS - set(row)):
            problems.append(f"{where}: required key '{key}' is missing")
        text = row.get("flag")
        if not _non_empty_str(text):
            problems.append(f"{where}: flag must be non-empty text")
            continue
        if text in seen:
            problems.append(f"{where}: duplicate row for this flag")
            continue
        seen.add(text)
        if text not in flags:
            problems.append(
                f"{where}: acknowledges a flag the validator no longer emits; "
                "remove the stale row"
            )
        if row.get("accepted") is not True:
            problems.append(f"{where}: FLAG '{text}' is not accepted")
        if not _non_empty_str(row.get("note")):
            problems.append(f"{where}: FLAG '{text}' has no acceptance note")
    for text in flags:
        if text not in seen:
            problems.append(f"{label}: FLAG neither cleared nor annotated: {text}")
    return problems


def one_domain(args: argparse.Namespace) -> Path:
    dirs = domain_dirs(args.memory, args.domain)
    if len(dirs) != 1:
        raise MigrateError_("freeze operates on exactly one --domain")
    return dirs[0]


def cmd_freeze(args: argparse.Namespace) -> int:
    domain_dir = one_domain(args)
    domain = domain_dir.name
    ledger_dir = purpose_directory(args.ledger_dir, args.memory)
    target = ledger_file(ledger_dir, domain)
    if target.exists():
        raise MigrateError_(
            f"refused: {target.as_posix()} already exists; FREEZE establishes "
            "the migration input once, so a re-freeze is an explicit operator "
            "action that removes the existing ledger first"
        )
    legacy = legacy_freeze_block(domain_dir)
    write_yaml_atomic(target, {"domain": domain, "legacy": legacy})
    print(
        f"frozen: {domain} schema {legacy['memory_schema_version']} "
        f"memory_version {legacy['memory_version']}, {legacy['entry_count']} "
        f"entr(ies), {len(legacy['admissible_event_ids'])} admissible event(s); "
        f"ledger {target.as_posix()}"
    )
    return 0


def cmd_verify_hashes(args: argparse.Namespace) -> int:
    domain_dir = one_domain(args)
    domain = domain_dir.name
    ledger_dir = purpose_directory(args.ledger_dir, args.memory)
    legacy = load_ledger(ledger_file(ledger_dir, domain), domain)
    recorded_version = legacy.get("memory_schema_version")
    if recorded_version not in SUPPORTED_SCHEMA_VERSIONS:
        raise MigrateError_(
            f"ledger records memory_schema_version {recorded_version}; A2 "
            "verifies a frozen legacy v1/v2 input"
        )
    problems = hash_problems(domain_dir, legacy)
    if problems:
        for problem in problems:
            print(problem, file=sys.stderr)
        print(f"FAIL: {len(problems)} hash problem(s) against {ledger_file(ledger_dir, domain).as_posix()}")
        return 1
    print(
        f"PASS: {legacy.get('entry_count')} entr(ies) in {domain} match the "
        "frozen hashes (A2)"
    )
    return 0


def cmd_sentences(args: argparse.Namespace) -> int:
    domain_dir = one_domain(args)
    domain = domain_dir.name
    try:
        blocks = entry_serialized_blocks(domain_dir / "skill_memory.yaml")
    except (MigrateError_, OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        raise MigrateError_(
            f"cannot read the {domain} legacy store: {exc}"
        ) from exc
    block = blocks.get(args.entry)
    if block is None:
        raise MigrateError_(
            f"'{args.entry}' is not an entry of the {domain} legacy store"
        )
    entry = entry_fields(block)
    if entry is None:
        raise MigrateError_(
            f"{domain}: entry '{args.entry}' does not parse as a mapping"
        )
    sentences = entry_sentence_texts(entry)
    print(f"{args.entry}: {len(sentences)} sentence(s)")
    for number, sentence in enumerate(sentences, start=1):
        print(f"{number}: {sentence}")
    return 0


def cmd_account(args: argparse.Namespace) -> int:
    domain_dir = one_domain(args)
    domain = domain_dir.name
    ledger_dir = purpose_directory(args.ledger_dir, args.memory)
    ledger = load_ledger_document(ledger_file(ledger_dir, domain), domain)
    schema_problems = ledger_schema_problems(ledger)
    if schema_problems:
        for problem in schema_problems:
            print(f"ledger schema: {problem}", file=sys.stderr)
        print(
            f"FAIL: {len(schema_problems)} ledger schema problem(s); the A1-A10 "
            "checks do not run on a malformed ledger"
        )
        return 1
    store_claim_ids = candidate_store_claim_ids(args.store)
    failures, a8_report, a9_report = account_problems(
        ledger, domain_dir, store_claim_ids
    )
    problems_by_check: dict[str, list[str]] = {check: [] for check in ACCOUNT_CHECKS}
    for check, message in failures:
        problems_by_check[check].append(message)
    for check in ACCOUNT_CHECKS:
        problems = problems_by_check[check]
        if problems:
            print(f"{check}: FAIL")
            for message in problems:
                print(f"  {check}: {message}", file=sys.stderr)
        elif check == "A8":
            print(f"A8: PASS: {a8_report}")
        elif check == "A9":
            print(f"A9: PASS: {a9_report}")
        else:
            print(f"{check}: PASS")
    if failures:
        print(
            f"FAIL: {len(failures)} accounting problem(s) across A1-A10 for {domain}",
            file=sys.stderr,
        )
        return 1
    print(f"PASS: account: A1-A10 accounting holds for {domain}")
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    domain = args.domain
    ledger_dir = purpose_directory(args.ledger_dir, args.memory)
    ledger = load_ledger_document(ledger_file(ledger_dir, domain), domain)
    schema_problems = ledger_schema_problems(ledger)
    if schema_problems:
        for problem in schema_problems:
            print(f"ledger schema: {problem}", file=sys.stderr)
        print(
            "FAIL: reports are not derived from a malformed ledger; the A1-A10 "
            "checks do not run on it either"
        )
        return 1
    for kind, path, count in write_report_set(ledger_dir, ledger):
        print(f"report: {kind}: {count} item(s): {path.as_posix()}")
    print(
        f"PASS: report: {domain} survival, loss, and re-homing derived from "
        "the ledger; loss items await item-by-item signoff"
    )
    return 0


def cmd_gate(args: argparse.Namespace) -> int:
    domain_dir = one_domain(args)
    domain = domain_dir.name
    ledger_dir = purpose_directory(args.ledger_dir, args.memory)
    ledger = load_ledger_document(ledger_file(ledger_dir, domain), domain)
    schema_problems = ledger_schema_problems(ledger)
    if schema_problems:
        for problem in schema_problems:
            print(f"ledger schema: {problem}", file=sys.stderr)
        print("FAIL: gate: the A1-A10 checks do not run on a malformed ledger")
        return 1
    failed = False

    # Loss sign-off: exact-set equality against the ledger's own losses, every
    # item individually signed. This is the anti-laundering control: a loss
    # that vanished from the artifact, an item that is not a loss, an edited
    # reason, a duplicate row, a truthy-but-not-true `signed_off`, an empty
    # note, or a document-level approval key each refuse.
    derived = loss_items(ledger)
    loss_file = report_path(ledger_dir, "loss", domain)
    try:
        loss_document = _load_yaml_mapping(loss_file, "loss report")
    except MigrateError_ as exc:
        print(f"FAIL: gate: {exc}", file=sys.stderr)
        failed = True
    else:
        problems = loss_artifact_problems(loss_document, domain, derived, loss_file)
        if problems:
            for problem in problems:
                print(f"loss signoff: {problem}", file=sys.stderr)
            print(f"loss signoff: FAIL ({len(problems)} problem(s))")
            failed = True
        else:
            print(
                f"loss signoff: PASS ({len(derived)} item(s) signed "
                "individually, none in bulk)"
            )

    # A1-A10 through the existing checker, zero HOLDs among them (A7): gate
    # adds no parallel accounting and no bypass. Source drift (A2) and a
    # remaining HOLD refuse here exactly as they do under `account`.
    try:
        store_claim_ids = candidate_store_claim_ids(args.store)
    except MigrateError_ as exc:
        print(f"FAIL: gate: {exc}", file=sys.stderr)
        return 1
    failures, a8_report, a9_report = account_problems(
        ledger, domain_dir, store_claim_ids
    )
    problems_by_check: dict[str, list[str]] = {check: [] for check in ACCOUNT_CHECKS}
    for check, message in failures:
        problems_by_check[check].append(message)
    for check in ACCOUNT_CHECKS:
        problems = problems_by_check[check]
        if problems:
            print(f"{check}: FAIL")
            for message in problems:
                print(f"  {check}: {message}", file=sys.stderr)
            failed = True
        elif check == "A8":
            print(f"A8: PASS: {a8_report}")
        elif check == "A9":
            print(f"A9: PASS: {a9_report}")
        else:
            print(f"{check}: PASS")
    if not problems_by_check["A7"]:
        print("zero HOLDs: PASS (A7)")

    # The candidate goes through the repository's actual v3 validator — the
    # same `validate_v3_contents` `memory.py validate` dispatches to for a
    # schema-3 store — with the migration domain rather than a directory name,
    # because a candidate has not been installed under memory/ yet. Errors
    # refuse; a History file beside the candidate resolves evidence, its
    # absence does not (I5). Nothing is silently repaired.
    candidate_path = Path(args.store)
    try:
        candidate = yaml.safe_load(candidate_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        print(f"FAIL: gate: candidate store does not load: {exc}", file=sys.stderr)
        return 1
    if not isinstance(candidate, dict):
        print(
            f"FAIL: gate: {candidate_path.as_posix()}: candidate store must be "
            "a mapping",
            file=sys.stderr,
        )
        return 1
    events: list[dict[str, Any]] | None = None
    event_errors: list[str] | None = None
    if (candidate_path.parent / "training_history.jsonl").is_file():
        events, event_errors = load_events(candidate_path.parent)
    errors, flags = validate_v3_contents(
        domain, candidate, events=events, event_errors=event_errors
    )
    if errors:
        for error in errors:
            print(f"candidate: {error}", file=sys.stderr)
        print(f"candidate validation: FAIL ({len(errors)} error(s))")
        failed = True
    else:
        print("candidate validation: PASS (every section-4 ERROR rule)")

    # FLAG review: cleared (no longer emitted) or individually accepted with a
    # note beside the ledger. An unreviewed FLAG refuses; acceptance never
    # mutates the candidate store.
    review_file = review_path(ledger_dir, domain)
    review_document: dict[str, Any] | None = None
    if review_file.is_file():
        try:
            review_document = _load_yaml_mapping(review_file, "review artifact")
        except MigrateError_ as exc:
            print(f"FAIL: gate: {exc}", file=sys.stderr)
            return 1
    flag_problems = review_artifact_problems(
        review_document, domain, flags, review_file
    )
    if flag_problems:
        for problem in flag_problems:
            print(f"flag review: {problem}", file=sys.stderr)
        print(f"flag review: FAIL ({len(flag_problems)} problem(s))")
        failed = True
    else:
        print(f"flag review: PASS ({len(flags)} FLAG(s) cleared or accepted)")

    if failed:
        print(f"FAIL: gate: {domain} is not verified; the legacy store stays", file=sys.stderr)
        return 1
    print(
        f"PASS: gate: {domain} — A1-A10 hold, zero HOLDs, FLAGs reviewed, "
        f"{len(derived)} loss item(s) signed individually, candidate validates"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--memory", type=Path, default=default_memory_root())
    common.add_argument("--domain", required=True, help="Exactly one domain (e.g. software-engineering).")
    common.add_argument(
        "--ledger-dir", type=Path, required=True,
        help="The migration task's workspace purpose directory. The ledger "
             "lands inside it as ledger-<domain>.yaml; never the workspace "
             "root, and never inside memory/.",
    )

    freeze = sub.add_parser(
        "freeze", parents=[common],
        help="Record a legacy store's inventory, per-entry hashes, and the "
             "admissible event set into a one-time workspace ledger.",
        description=(
            "Step 0 of the R2.5 migration (§7.4), and only step 0: the store is "
            "read, validated, and recorded. Nothing is decomposed, classified, "
            "authored, converted, repaired, or rewritten, and nothing is "
            "written under memory/."
        ),
    )
    verify = sub.add_parser(
        "verify-hashes", parents=[common],
        help="Re-check every recorded entry hash against the store (A2).",
        description=(
            "Detects a legacy store edited after FREEZE: every recorded hash is "
            "recomputed from the file, and the entry id set must match — an "
            "edited, removed, or added entry fails."
        ),
    )
    sentences = sub.add_parser(
        "sentences",
        help="Emit the numbered sentence inventory of one legacy entry (A9's source).",
        description=(
            "Segmentation of the jointly-read legacy text: observation, "
            "boundary, and diagnosis.hypothesis concatenated in that order "
            "and split with validate.py's SENTENCE_RE - the repository's one "
            "sentence splitter, imported rather than copied. Emission only: "
            "nothing is attributed, decomposed, classified, or written, and "
            "no ledger is read or touched."
        ),
    )
    sentences.add_argument("--memory", type=Path, default=default_memory_root())
    sentences.add_argument(
        "--domain", required=True, help="Exactly one domain (e.g. software-engineering)."
    )
    sentences.add_argument(
        "--entry", required=True,
        help="One legacy entry id of that domain (e.g. SE_MEM_001).",
    )
    account = sub.add_parser(
        "account", parents=[common],
        help="Run the A1-A10 completeness checks against a judgment-filled "
             "ledger and its candidate store.",
        description=(
            "Pass 4 of the R2.5 migration (§7.4): the ledger's schema and "
            "closed vocabularies are validated, then checks A1-A10 run against "
            "the frozen legacy block, the recorded decompositions and "
            "dispositions, and the candidate v3 store. A9 proves sentence "
            "coverage against the frozen entry bytes and the second-reader "
            "mark's presence on declared accretion entries - never the truth "
            "of an attribution. Every failure names its check. The checker "
            "never assigns, proposes, or suggests a disposition, never judges "
            "semantic fidelity, and writes nothing."
        ),
    )
    account.add_argument(
        "--store", type=Path, required=True,
        help="The candidate v3 store (skill_memory.yaml) whose claim ids the "
             "ledger's targets must resolve into (A5, A6, A8).",
    )
    report = sub.add_parser(
        "report", parents=[common],
        help="Derive the survival, loss, and re-homing reports from the ledger.",
        description=(
            "Pass 4's report surface (§7.5): three artifacts derived "
            "deterministically from the ledger's recorded dispositions - "
            "survival (every CARRY/REWRITE/SPLIT/CONDENSE/EXTRACT proposition "
            "and its target claim), loss (every REJECT, REHOME, and CONDENSE "
            "shed with its reason, each row carrying an empty per-item "
            "signoff), and re-homing (everything sent to another authority, "
            "with destination and complete-or-owed status). Nothing is "
            "inferred, no reason or note is generated, existing reports "
            "refuse regeneration so a signoff is never silently destroyed, "
            "and the artifacts land beside the ledger - never under memory/."
        ),
    )
    gate = sub.add_parser(
        "gate", parents=[common],
        help="The VERIFY-step entry point: A1-A10, zero HOLDs, reviewed "
             "FLAGs, signed loss items, valid candidate.",
        description=(
            "Pass 5 of the R2.5 migration (§7.4): re-runs the A1-A10 "
            "accounting through the existing checker (A2 source drift and A7 "
            "HOLDs refuse, never warn), requires the loss report's items to "
            "equal the ledger's own loss set with every item individually "
            "signed and no document-level approval, runs the repository's v3 "
            "validator on the candidate store (ERRORs refuse), and requires "
            "every FLAG cleared or individually accepted with a note in the "
            "review artifact. Writes nothing, judges nothing semantic, and "
            "has no bulk-approval path."
        ),
    )
    gate.add_argument(
        "--store", type=Path, required=True,
        help="The candidate v3 store (skill_memory.yaml) the gate validates.",
    )

    args = parser.parse_args()
    handlers = {
        "freeze": cmd_freeze,
        "verify-hashes": cmd_verify_hashes,
        "sentences": cmd_sentences,
        "account": cmd_account,
        "report": cmd_report,
        "gate": cmd_gate,
    }
    try:
        return handlers[args.command](args)
    except MigrateError_ as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
