#!/usr/bin/env python3
"""One-time R2.5 migration tooling for legacy Skillset Memory stores: FREEZE
and hash verification only, deleted by ticket T21.

This module is step 0 of the R2.5 migration algorithm (§7.4), and only step 0.
`freeze` records the mechanical facts a later migration needs in order to detect
source drift — for one domain, one store: `memory_schema_version`,
`memory_version`, the entry count, a sha256 of each entry's serialized bytes,
and the admissible event id set (valid + performance + not quarantined). It
refuses a legacy store that does not pass the existing Memory validator, and it
refuses anything that is not a legacy v1/v2 input: a schema-3 store is a migration
output, not an input, and FREEZE never converts one. `verify-hashes` re-checks
every recorded hash against the file (check A2), for use at the VERIFY gate.

The ledger lands in the task's workspace purpose directory and nowhere else. It
is a one-time artifact, never a permanent ledger, a state sidecar, or a Memory
field: `memory/` is read and never written — not the store, not Training History,
not line endings, not metadata. Legacy stores remain read-only migration inputs
until their domain's migration is signed off.

Judgment surfaces are deliberately absent. This tool records and re-checks
mechanical truth only: it never decomposes an entry, never classifies, never
authors a vNext claim, never invents a proposition id, and never computes a
confidence. No runtime path may depend on this module; T21 deletes it together
with the legacy input reader.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import sys
from pathlib import Path
from typing import Any

import yaml

from memory import (
    SUPPORTED_SCHEMA_VERSIONS,
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


def load_ledger(path: Path, domain: str) -> dict[str, Any]:
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
    legacy = data.get("legacy")
    if not isinstance(legacy, dict):
        raise MigrateError_(f"{path.as_posix()}: ledger has no legacy block")
    return legacy


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

    args = parser.parse_args()
    handlers = {"freeze": cmd_freeze, "verify-hashes": cmd_verify_hashes}
    try:
        return handlers[args.command](args)
    except MigrateError_ as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
