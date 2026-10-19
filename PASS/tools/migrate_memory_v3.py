#!/usr/bin/env python3
"""One-time R2.5 migration tooling for legacy Skillset Memory stores: FREEZE,
hash verification, and the A1–A10 accounting checker, deleted by ticket T21.

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
rejection reason kinds, destination authorities, proposition id shape), then
A1–A10 against the frozen `legacy:` block, the ledger's own decompositions and
dispositions, and the candidate v3 store the targets must resolve into. Every
failure names its check. A9 is delegated to the T15 sentence-coverage checker
and is reported as such; this command owns no sentence map.

The ledger lands in the task's workspace purpose directory and nowhere else. It
is a one-time artifact, never a permanent ledger, a state sidecar, or a Memory
field: `memory/` is read and never written — not the store, not Training History,
not line endings, not metadata. Legacy stores remain read-only migration inputs
until their domain's migration is signed off.

Judgment surfaces are deliberately absent. This tool records and re-checks
mechanical truth only: it never decomposes an entry, never classifies, never
authors a vNext claim, never invents a proposition id, never assigns, proposes,
or suggests a disposition, and never computes a confidence. The accounting
checker proves completeness and referential integrity of recorded judgments,
never semantic fidelity (§7.5). No runtime path may depend on this module; T21
deletes it together with the legacy input reader.
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
)
from paths import default_memory_root


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


def write_ledger(path: Path, ledger: dict[str, Any]) -> None:
    """Write the ledger atomically. The only file this tool ever writes."""
    text = yaml.safe_dump(ledger, sort_keys=False, default_flow_style=False)
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
})
LEGACY_BLOCK_KEYS = frozenset({
    "memory_schema_version", "memory_version", "entry_count",
    "entry_hashes", "admissible_event_ids",
})
VNEXT_BLOCK_KEYS = frozenset({"memory_schema_version", "claim_count"})
DECOMPOSITION_KEYS = frozenset({"legacy_entry", "legacy_sha256", "propositions"})
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
            require_keys(item, DECOMPOSITION_KEYS, DECOMPOSITION_KEYS, where)
            entry_id = item.get("legacy_entry")
            if not _non_empty_str(entry_id):
                problems.append(f"{where}: legacy_entry must be a non-empty string")
            digest = item.get("legacy_sha256")
            if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest):
                problems.append(f"{where}: legacy_sha256 is not a lowercase sha256 digest")
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


def account_problems(
    ledger: dict[str, Any],
    domain_dir: Path,
    store_claim_ids: list[str],
) -> tuple[list[tuple[str, str]], str]:
    """Every A1-A10 failure as (check, message), plus the A8 report line.

    Each check is reported independently; one broken fixture names the checks
    it actually breaks. Nothing here infers a disposition, compares a shared
    target against any source id, or reads any numeric or lexical relationship
    between a legacy id and a target id (§7.5 traceability note).
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

    return failures, a8_report



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
    write_ledger(target, {"domain": domain, "legacy": legacy})
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
    failures, a8_report = account_problems(ledger, domain_dir, store_claim_ids)
    problems_by_check: dict[str, list[str]] = {check: [] for check in ACCOUNT_CHECKS}
    for check, message in failures:
        problems_by_check[check].append(message)
    for check in ACCOUNT_CHECKS:
        problems = problems_by_check[check]
        if check == "A9":
            print(
                "A9: delegated to the T15 sentence-coverage checker; not owned "
                "by this command"
            )
            continue
        if problems:
            print(f"{check}: FAIL")
            for message in problems:
                print(f"  {check}: {message}", file=sys.stderr)
        elif check == "A8":
            print(f"A8: PASS: {a8_report}")
        else:
            print(f"{check}: PASS")
    if failures:
        print(
            f"FAIL: {len(failures)} accounting problem(s) across A1-A10 for {domain}",
            file=sys.stderr,
        )
        return 1
    print(
        f"PASS: account: A1-A10 accounting holds for {domain} "
        "(A9 delegated to T15)"
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
    account = sub.add_parser(
        "account", parents=[common],
        help="Run the A1-A10 completeness checks against a judgment-filled "
             "ledger and its candidate store.",
        description=(
            "Pass 4 of the R2.5 migration (§7.4): the ledger's schema and "
            "closed vocabularies are validated, then checks A1-A10 run against "
            "the frozen legacy block, the recorded decompositions and "
            "dispositions, and the candidate v3 store. Every failure names its "
            "check. The checker never assigns, proposes, or suggests a "
            "disposition, never judges semantic fidelity, and writes nothing."
        ),
    )
    account.add_argument(
        "--store", type=Path, required=True,
        help="The candidate v3 store (skill_memory.yaml) whose claim ids the "
             "ledger's targets must resolve into (A5, A6, A8).",
    )

    args = parser.parse_args()
    handlers = {
        "freeze": cmd_freeze,
        "verify-hashes": cmd_verify_hashes,
        "account": cmd_account,
    }
    try:
        return handlers[args.command](args)
    except MigrateError_ as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
