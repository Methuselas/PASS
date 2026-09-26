#!/usr/bin/env python3
"""Deterministic administration for PASS Candidate Refinement & Qualification.

A CRQ run compares one bounded candidate change to ordinary PASS cards against a
frozen canonical baseline. This controller owns only administration: the run
state machine, atomic state writes, path containment, frozen-file hashes, the
controller fingerprint, and baseline-drift detection. It never writes
`library/` or Skillset Memory, never calls a model, and never judges domain
semantics.

Run directories live under `workspace/candidate-qualification/<domain>/<run-id>/`
and are disposable administration scratch. `controller/run.json` is the
authoritative state of one run.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any, Callable, Iterable


SCHEMA_VERSION = 1
# A newer controller may read an older run only when its schema is listed here.
# It never migrates or requalifies an older run.
READABLE_SCHEMA_VERSIONS = frozenset({SCHEMA_VERSION})
WORKSPACE_BUCKET = "workspace/candidate-qualification"

LIFECYCLE_STATES = (
    "prepared",
    "assessment-frozen",
    "plan-frozen",
    "candidate-staged",
    "candidate-frozen",
    "execution-open",
    "execution-frozen",
    "evaluated",
    "finalized",
)
EXCEPTIONAL_STATES = ("invalidated", "abandoned")
STATES = frozenset(LIFECYCLE_STATES + EXCEPTIONAL_STATES)
TERMINAL_STATES = frozenset({"finalized", "invalidated", "abandoned"})

# command -> (required current state, next state). `prepare` creates a run in
# `prepared`; it has no current state and is handled by `initialize_run`.
TRANSITIONS: dict[str, tuple[str, str]] = {
    "freeze-assessment": ("prepared", "assessment-frozen"),
    "freeze-plan": ("assessment-frozen", "plan-frozen"),
    "stage-candidate": ("plan-frozen", "candidate-staged"),
    "freeze-candidate": ("candidate-staged", "candidate-frozen"),
    "open-execution": ("candidate-frozen", "execution-open"),
    "freeze-execution": ("execution-open", "execution-frozen"),
    "evaluate": ("execution-frozen", "evaluated"),
    "finalize": ("evaluated", "finalized"),
}
# Allowed from any nonterminal state.
CLOSING_COMMANDS: dict[str, str] = {
    "invalidate": "invalidated",
    "abandon": "abandoned",
}
EXECUTION_STATES = frozenset({
    "execution-open", "execution-frozen", "evaluated", "finalized",
})

DEFAULT_SCOPE_LIMITS = {"max_changed_cards": 3, "max_new_cards": 2}
SCOPE_LIMIT_KEYS = frozenset(DEFAULT_SCOPE_LIMITS) | {"override_reason"}
RUN_FILES = {
    "baseline_manifest": "controller/baseline_manifest.json",
    "assessment": "controller/assessment.json",
    "qualification_plan": "controller/qualification_plan.json",
    "candidate_manifest": "controller/candidate_manifest.json",
    "qualification_result": "qualification_result.json",
}
RUN_KEYS = frozenset({
    "schema_version", "run_id", "domain", "state", "created_at", "updated_at",
    "controller_sha256", "memory_entry_id", "library_root", "memory_root",
    "scope_limits", "files", "baseline_manifest_sha256", "freezes", "history",
    "invalid_reason", "abandoned_reason",
})
HISTORY_KEYS = frozenset({"command", "from", "to", "at"})
FREEZE_KEYS = frozenset({"path", "sha256", "frozen_at"})
BASELINE_ROLES = frozenset({"target", "support", "module-manifest"})
BASELINE_ENTRY_KEYS = frozenset({"relative_path", "object_id", "sha256", "role"})
ARMS = ("baseline", "candidate")

RUN_ID_RE = re.compile(r"[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)*_CRQ_[0-9]{4,}\Z")
DOMAIN_RE = re.compile(r"[a-z0-9][a-z0-9-]*\Z")
SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
FREEZE_NAME_RE = re.compile(r"[a-z][a-z0-9-]*\Z")


class CandidateQualificationError(RuntimeError):
    """An administration error. The command fails and run state is unchanged."""


class ControllerMismatchError(CandidateQualificationError):
    """The run was prepared under a different controller implementation."""


class BaselineDriftError(CandidateQualificationError):
    """A frozen baseline file no longer matches its recorded hash."""


# ---------------------------------------------------------------- time / hash


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def digest_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def controller_sha256() -> str:
    """SHA-256 of this controller file's bytes."""
    return digest_file(Path(__file__).resolve())


# ------------------------------------------------------------- stable JSON IO


def stable_json(value: Any) -> str:
    """Deterministic serialization for controller-generated JSON."""
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CandidateQualificationError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise CandidateQualificationError(f"{path} must contain a JSON object")
    return value


def write_text_atomic(path: Path, text: str) -> None:
    """Replace `path` with `text` so a crash leaves the previous file intact."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_name, path)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except OSError:
            pass
        raise


def write_json_atomic(path: Path, value: Any) -> None:
    write_text_atomic(path, stable_json(value))


# ---------------------------------------------------------- path containment


def safe_relative(value: Any, label: str) -> PurePosixPath:
    """Validate a run-owned or library-relative POSIX path."""
    if not isinstance(value, str) or not value.strip():
        raise CandidateQualificationError(f"{label} must be a non-empty relative path")
    if "\\" in value or "\0" in value:
        raise CandidateQualificationError(f"{label} must use forward slashes: {value!r}")
    windows = PureWindowsPath(value)
    relative = PurePosixPath(value)
    if relative.is_absolute() or windows.drive or windows.root:
        raise CandidateQualificationError(f"{label} must be relative: {value!r}")
    if value != relative.as_posix() or any(part in {"", ".", ".."} for part in relative.parts):
        raise CandidateQualificationError(f"{label} must be a normalized bounded path: {value!r}")
    return relative


def require_inside(path: Path, root: Path, label: str) -> Path:
    """Resolve `path`, following symlinks, and require it inside `root`."""
    resolved = path.resolve()
    resolved_root = root.resolve()
    try:
        resolved.relative_to(resolved_root)
    except ValueError as exc:
        raise CandidateQualificationError(f"{label} escapes {resolved_root}") from exc
    return resolved


def contained(root: Path, relative: Any, label: str) -> Path:
    """Join a validated relative path to `root` and require containment."""
    parts = safe_relative(relative, label).parts
    return require_inside(root.resolve().joinpath(*parts), root, label)


# ------------------------------------------------------------------ run record


def new_run_record(
    *,
    run_id: str,
    domain: str,
    memory_entry_id: str,
    library_root: Path,
    memory_root: Path,
    max_changed_cards: int | None = None,
    max_new_cards: int | None = None,
    override_reason: str | None = None,
) -> dict[str, Any]:
    """Build a `prepared` run record. Raising limits needs a recorded reason."""
    limits: dict[str, Any] = dict(DEFAULT_SCOPE_LIMITS)
    if max_changed_cards is not None:
        limits["max_changed_cards"] = max_changed_cards
    if max_new_cards is not None:
        limits["max_new_cards"] = max_new_cards
    if override_reason is not None and override_reason.strip():
        limits["override_reason"] = override_reason.strip()
    created = now_utc()
    run: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "domain": domain,
        "state": "prepared",
        "created_at": created,
        "updated_at": created,
        "controller_sha256": controller_sha256(),
        "memory_entry_id": memory_entry_id,
        "library_root": str(Path(library_root).resolve()),
        "memory_root": str(Path(memory_root).resolve()),
        "scope_limits": limits,
        "files": dict(RUN_FILES),
        "baseline_manifest_sha256": None,
        "freezes": {},
        "history": [
            {"command": "prepare", "from": None, "to": "prepared", "at": created}
        ],
        "invalid_reason": None,
        "abandoned_reason": None,
    }
    errors = validate_run_record(run)
    if errors:
        raise CandidateQualificationError("invalid run record: " + "; ".join(errors))
    return run


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_timestamp(value: Any) -> bool:
    if not isinstance(value, str) or not value.endswith("Z"):
        return False
    try:
        datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        return False
    return True


def _nonempty_str(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_run_record(run: Any) -> list[str]:
    """Return every schema problem in a run record; empty means valid."""
    if not isinstance(run, dict):
        return ["run record must be a JSON object"]
    errors: list[str] = []
    missing = sorted(RUN_KEYS - set(run))
    unknown = sorted(set(run) - RUN_KEYS)
    if missing:
        errors.append("missing run key(s): " + ", ".join(missing))
    if unknown:
        errors.append("unknown run key(s): " + ", ".join(unknown))
    if not _is_int(run.get("schema_version")) or (
        run.get("schema_version") not in READABLE_SCHEMA_VERSIONS
    ):
        errors.append(f"unsupported schema_version: {run.get('schema_version')!r}")
    if not isinstance(run.get("run_id"), str) or not RUN_ID_RE.fullmatch(run["run_id"]):
        errors.append(f"run_id must look like SE_CRQ_0001: {run.get('run_id')!r}")
    if not isinstance(run.get("domain"), str) or not DOMAIN_RE.fullmatch(run["domain"]):
        errors.append(f"domain must be a library package name: {run.get('domain')!r}")
    state = run.get("state")
    if state not in STATES:
        errors.append(f"unknown state: {state!r}")
    for key in ("created_at", "updated_at"):
        if not _is_timestamp(run.get(key)):
            errors.append(f"{key} must be a UTC timestamp ending in Z")
    if not isinstance(run.get("controller_sha256"), str) or not SHA256_RE.fullmatch(
        run["controller_sha256"]
    ):
        errors.append("controller_sha256 must be a SHA-256 hex digest")
    if not _nonempty_str(run.get("memory_entry_id")):
        errors.append("memory_entry_id must be non-empty")
    for key in ("library_root", "memory_root"):
        value = run.get(key)
        if not _nonempty_str(value) or not Path(value).is_absolute():
            errors.append(f"{key} must be an absolute path")

    limits = run.get("scope_limits")
    if not isinstance(limits, dict):
        errors.append("scope_limits must be an object")
    else:
        extra = sorted(set(limits) - SCOPE_LIMIT_KEYS)
        if extra:
            errors.append(
                "scope_limits may set only max_changed_cards and max_new_cards; "
                "deletion, renaming and moving are never enabled: " + ", ".join(extra)
            )
        raised = False
        for key, default in DEFAULT_SCOPE_LIMITS.items():
            value = limits.get(key)
            if not _is_int(value) or value < 0:
                errors.append(f"scope_limits.{key} must be a non-negative integer")
            elif value > default:
                raised = True
        if "override_reason" in limits and not _nonempty_str(limits["override_reason"]):
            errors.append("scope_limits.override_reason must be non-empty when present")
        if raised and not _nonempty_str(limits.get("override_reason")):
            errors.append("raising a scope ceiling above its default requires override_reason")

    files = run.get("files")
    if not isinstance(files, dict) or set(files) != set(RUN_FILES):
        errors.append("files must name exactly: " + ", ".join(sorted(RUN_FILES)))
    else:
        for key, value in files.items():
            try:
                safe_relative(value, f"files.{key}")
            except CandidateQualificationError as exc:
                errors.append(str(exc))

    baseline_hash = run.get("baseline_manifest_sha256")
    if baseline_hash is not None and (
        not isinstance(baseline_hash, str) or not SHA256_RE.fullmatch(baseline_hash)
    ):
        errors.append("baseline_manifest_sha256 must be null or a SHA-256 hex digest")

    freezes = run.get("freezes")
    if not isinstance(freezes, dict):
        errors.append("freezes must be an object")
    else:
        for name, freeze in freezes.items():
            if not isinstance(name, str) or not FREEZE_NAME_RE.fullmatch(name):
                errors.append(f"invalid freeze name: {name!r}")
            if not isinstance(freeze, dict) or set(freeze) != FREEZE_KEYS:
                errors.append(f"freeze {name!r} must have exactly path, sha256, frozen_at")
                continue
            try:
                safe_relative(freeze["path"], f"freeze {name} path")
            except CandidateQualificationError as exc:
                errors.append(str(exc))
            if not isinstance(freeze["sha256"], str) or not SHA256_RE.fullmatch(freeze["sha256"]):
                errors.append(f"freeze {name!r} sha256 must be a SHA-256 hex digest")
            if not _is_timestamp(freeze["frozen_at"]):
                errors.append(f"freeze {name!r} frozen_at must be a UTC timestamp")

    history = run.get("history")
    if not isinstance(history, list) or not history:
        errors.append("history must be a non-empty list")
    else:
        for index, item in enumerate(history):
            if not isinstance(item, dict) or set(item) != HISTORY_KEYS:
                errors.append(f"history[{index}] must have exactly command, from, to, at")
                continue
            if item["to"] not in STATES or (
                item["from"] is not None and item["from"] not in STATES
            ):
                errors.append(f"history[{index}] names an unknown state")
            if not _is_timestamp(item["at"]):
                errors.append(f"history[{index}].at must be a UTC timestamp")
        last = history[-1]
        if isinstance(last, dict) and last.get("to") != state:
            errors.append("history must end in the current state")

    for key, owner in (("invalid_reason", "invalidated"), ("abandoned_reason", "abandoned")):
        value = run.get(key)
        if state == owner:
            if not _nonempty_str(value):
                errors.append(f"{key} is required in state {owner}")
        elif value is not None:
            errors.append(f"{key} is allowed only in state {owner}")
    return errors


def run_json_path(root: Path) -> Path:
    return root / "controller" / "run.json"


def load_run(run_dir: Path) -> tuple[Path, dict[str, Any]]:
    """Reopen a run and verify its schema. Never migrates an older run."""
    root = Path(run_dir).resolve()
    path = run_json_path(root)
    if not path.is_file():
        raise CandidateQualificationError(f"not a CRQ run (no controller/run.json): {root}")
    run = read_json(path)
    version = run.get("schema_version")
    if not _is_int(version) or version not in READABLE_SCHEMA_VERSIONS:
        raise CandidateQualificationError(
            f"unsupported CRQ run schema {version!r}; this controller reads only "
            f"{sorted(READABLE_SCHEMA_VERSIONS)} and does not migrate runs"
        )
    errors = validate_run_record(run)
    if errors:
        raise CandidateQualificationError(f"invalid run.json at {path}: " + "; ".join(errors))
    return root, run


def save_run(root: Path, run: dict[str, Any]) -> dict[str, Any]:
    """Atomically write run.json, then read it back before claiming success."""
    errors = validate_run_record(run)
    if errors:
        raise CandidateQualificationError("refusing to write invalid run.json: " + "; ".join(errors))
    path = run_json_path(root)
    write_json_atomic(path, run)
    persisted = read_json(path)
    if persisted != run:
        raise CandidateQualificationError(
            f"run.json read-back does not match what was written: {path}"
        )
    return persisted


def require_current_controller(run: dict[str, Any]) -> None:
    """Refuse to continue a run under a different schema or controller."""
    if run["schema_version"] != SCHEMA_VERSION:
        raise CandidateQualificationError(
            f"schema-v{run['schema_version']} runs are read-only under this controller; "
            f"start a fresh schema-v{SCHEMA_VERSION} run"
        )
    if run["controller_sha256"] != controller_sha256():
        raise ControllerMismatchError(
            "controller fingerprint changed since this run was prepared; start a "
            "fresh run instead of continuing under different administration rules"
        )


# ------------------------------------------------------------ baseline drift


def baseline_entry(
    library_root: Path, relative_path: str, object_id: str | None, role: str
) -> dict[str, Any]:
    """Describe one canonical file for the baseline manifest."""
    if role not in BASELINE_ROLES:
        raise CandidateQualificationError(f"baseline role must be one of {sorted(BASELINE_ROLES)}")
    path = contained(Path(library_root), relative_path, "baseline path")
    if not path.is_file():
        raise CandidateQualificationError(f"baseline file does not exist: {relative_path}")
    return {
        "relative_path": relative_path,
        "object_id": object_id,
        "sha256": digest_file(path),
        "role": role,
    }


def validate_baseline_manifest(manifest: Any, run_id: str) -> list[str]:
    if not isinstance(manifest, dict):
        return ["baseline manifest must be a JSON object"]
    errors: list[str] = []
    if set(manifest) != {"schema_version", "run_id", "entries"}:
        errors.append("baseline manifest must have exactly schema_version, run_id, entries")
    if manifest.get("schema_version") != SCHEMA_VERSION:
        errors.append("baseline manifest schema_version mismatch")
    if manifest.get("run_id") != run_id:
        errors.append("baseline manifest belongs to a different run")
    entries = manifest.get("entries")
    if not isinstance(entries, list) or not entries:
        errors.append("baseline manifest must list at least one entry")
        return errors
    seen: set[str] = set()
    for index, entry in enumerate(entries):
        label = f"baseline entry {index}"
        if not isinstance(entry, dict) or set(entry) != BASELINE_ENTRY_KEYS:
            errors.append(f"{label} must have exactly {sorted(BASELINE_ENTRY_KEYS)}")
            continue
        try:
            safe_relative(entry["relative_path"], label)
        except CandidateQualificationError as exc:
            errors.append(str(exc))
            continue
        if entry["relative_path"] in seen:
            errors.append(f"{label} duplicates {entry['relative_path']}")
        seen.add(entry["relative_path"])
        if entry["role"] not in BASELINE_ROLES:
            errors.append(f"{label} has unknown role {entry['role']!r}")
        if entry["role"] == "module-manifest":
            if entry["object_id"] is not None:
                errors.append(f"{label}: a module manifest has no object_id")
        elif not _nonempty_str(entry["object_id"]):
            errors.append(f"{label}: a card entry requires object_id")
        if not isinstance(entry["sha256"], str) or not SHA256_RE.fullmatch(entry["sha256"]):
            errors.append(f"{label} sha256 must be a SHA-256 hex digest")
    return errors


def load_baseline_manifest(root: Path, run: dict[str, Any]) -> dict[str, Any]:
    """Read the frozen baseline manifest after checking its recorded hash."""
    expected = run.get("baseline_manifest_sha256")
    if expected is None:
        raise BaselineDriftError("no baseline manifest was frozen for this run")
    path = contained(root, run["files"]["baseline_manifest"], "baseline manifest")
    if not path.is_file():
        raise BaselineDriftError("baseline manifest is missing")
    if digest_file(path) != expected:
        raise BaselineDriftError("baseline manifest changed after it was frozen")
    manifest = read_json(path)
    errors = validate_baseline_manifest(manifest, run["run_id"])
    if errors:
        raise CandidateQualificationError("invalid baseline manifest: " + "; ".join(errors))
    return manifest


def baseline_drift(root: Path, run: dict[str, Any]) -> list[str]:
    """List every way the frozen baseline no longer matches; empty means clean.

    Two copies are checked for each entry: the canonical file under
    `library_root`, whose drift invalidates the comparison, and the run's
    `baseline/cards/` snapshot, whose change means the frozen evidence was
    edited.
    """
    try:
        manifest = load_baseline_manifest(root, run)
    except CandidateQualificationError as exc:
        return [str(exc)]
    library = Path(run["library_root"])
    snapshot_root = root / "baseline" / "cards"
    problems: list[str] = []
    if not library.is_dir():
        return [f"library root is missing: {library}"]
    for entry in manifest["entries"]:
        relative = entry["relative_path"]
        for label, base in (("canonical", library), ("snapshot", snapshot_root)):
            try:
                path = contained(base, relative, f"{label} baseline path")
            except CandidateQualificationError as exc:
                problems.append(str(exc))
                continue
            if not path.is_file():
                problems.append(f"{label} baseline file is missing: {relative}")
            elif digest_file(path) != entry["sha256"]:
                problems.append(f"{label} baseline file changed: {relative}")
    return problems


def verify_baseline(root: Path, run: dict[str, Any]) -> None:
    problems = baseline_drift(root, run)
    if problems:
        raise BaselineDriftError(
            "baseline drift; this comparison can no longer continue, start a fresh "
            "run against the current library: " + "; ".join(problems)
        )


# ------------------------------------------------------------- frozen files


def file_manifest(root: Path, relative_paths: Iterable[str]) -> list[dict[str, Any]]:
    """Hash run-owned files by their bytes, sorted by path."""
    manifest = []
    for relative in sorted(set(relative_paths)):
        path = contained(root, relative, "frozen file")
        if not path.is_file():
            raise CandidateQualificationError(f"cannot freeze missing file: {relative}")
        manifest.append({
            "path": relative,
            "bytes": path.stat().st_size,
            "sha256": digest_file(path),
        })
    return manifest


def record_freeze(
    root: Path, run: dict[str, Any], name: str, relative_paths: Iterable[str]
) -> dict[str, Any]:
    """Write `controller/<name>.freeze.json` and record its hash in `run`.

    The caller persists `run` through a state transition. A freeze is never
    replaced; revising frozen material requires a fresh run.
    """
    if not FREEZE_NAME_RE.fullmatch(name):
        raise CandidateQualificationError(f"invalid freeze name: {name!r}")
    if name in run["freezes"]:
        raise CandidateQualificationError(f"{name} is already frozen; start a fresh run to revise it")
    files = file_manifest(root, relative_paths)
    if not files:
        raise CandidateQualificationError(f"{name} freeze must name at least one file")
    frozen_at = now_utc()
    relative = f"controller/{name}.freeze.json"
    path = contained(root, relative, "freeze file")
    write_json_atomic(path, {
        "schema_version": SCHEMA_VERSION,
        "run_id": run["run_id"],
        "name": name,
        "frozen_at": frozen_at,
        "files": files,
    })
    run["freezes"][name] = {
        "path": relative,
        "sha256": digest_file(path),
        "frozen_at": frozen_at,
    }
    return run["freezes"][name]


def freeze_problems(root: Path, run: dict[str, Any]) -> list[str]:
    """List every frozen run file that changed; empty means clean."""
    problems: list[str] = []
    for name, freeze in sorted(run["freezes"].items()):
        try:
            path = contained(root, freeze["path"], f"{name} freeze file")
        except CandidateQualificationError as exc:
            problems.append(str(exc))
            continue
        if not path.is_file() or digest_file(path) != freeze["sha256"]:
            problems.append(f"{name} freeze record changed or is missing")
            continue
        try:
            record = read_json(path)
            files = record["files"]
            if record.get("run_id") != run["run_id"] or not isinstance(files, list):
                raise KeyError("files")
            for item in files:
                target = contained(root, item["path"], f"{name} frozen file")
                if not target.is_file() or digest_file(target) != item["sha256"]:
                    problems.append(f"{name}: {item['path']} changed after it was frozen")
        except (CandidateQualificationError, KeyError, TypeError) as exc:
            problems.append(f"{name} freeze record is unreadable: {exc}")
    return problems


def verify_frozen_state(root: Path, run: dict[str, Any]) -> None:
    """Refuse continuation when the baseline or any frozen run file drifted."""
    verify_baseline(root, run)
    problems = freeze_problems(root, run)
    if problems:
        raise CandidateQualificationError(
            "frozen run material changed; start a fresh run: " + "; ".join(problems)
        )


# ------------------------------------------------------------ state machine


def _record_transition(run: dict[str, Any], command: str, target: str) -> None:
    at = now_utc()
    run["history"].append({"command": command, "from": run["state"], "to": target, "at": at})
    run["state"] = target
    run["updated_at"] = at


def _refuse_terminal(run: dict[str, Any]) -> None:
    if run["state"] in TERMINAL_STATES:
        raise CandidateQualificationError(
            f"run is {run['state']} and read-only except for status"
        )


def initialize_run(
    out: Path,
    run: dict[str, Any],
    populate: Callable[[Path, dict[str, Any]], None] | None = None,
) -> dict[str, Any]:
    """Create a run directory atomically in state `prepared`.

    `populate(staging_root, run)` writes the baseline snapshot and manifest into
    a sibling staging directory and records `baseline_manifest_sha256`. The
    directory appears at `out` only after the baseline verifies.
    """
    if run.get("state") != "prepared" or len(run.get("history") or []) != 1:
        raise CandidateQualificationError("a new run must start in prepared with one history entry")
    out = Path(out).resolve()
    if out.exists():
        raise CandidateQualificationError(f"refusing to overwrite existing run directory: {out}")
    out.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{out.name}.", dir=out.parent))
    try:
        (staging / "controller").mkdir()
        if populate is not None:
            populate(staging, run)
        verify_baseline(staging, run)
        save_run(staging, run)
        os.replace(staging, out)
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return load_run(out)[1]


def apply_transition(
    run_dir: Path,
    command: str,
    update: Callable[[Path, dict[str, Any]], None] | None = None,
) -> dict[str, Any]:
    """Perform one lifecycle transition or fail without changing state.

    Order: reopen and verify the schema, verify the controller fingerprint,
    require the command's source state, verify the frozen baseline and freezes,
    let `update` validate and stage the command's work on a copy, then write the
    new state atomically and read it back.
    """
    if command not in TRANSITIONS:
        raise CandidateQualificationError(f"unknown lifecycle command: {command}")
    root, run = load_run(run_dir)
    require_current_controller(run)
    _refuse_terminal(run)
    required, target = TRANSITIONS[command]
    if run["state"] != required:
        raise CandidateQualificationError(
            f"{command} requires state {required}, found {run['state']}"
        )
    verify_frozen_state(root, run)
    working = copy.deepcopy(run)
    if update is not None:
        update(root, working)
        if working["state"] != run["state"]:
            raise CandidateQualificationError(f"{command} update may not set state directly")
    _record_transition(working, command, target)
    return save_run(root, working)


def close_run(run_dir: Path, command: str, reason: str) -> dict[str, Any]:
    """Invalidate or abandon a nonterminal run.

    Baseline drift does not block closing: drift is a legitimate reason to
    invalidate, and closing makes no evidence claim.
    """
    if command not in CLOSING_COMMANDS:
        raise CandidateQualificationError(f"unknown closing command: {command}")
    root, run = load_run(run_dir)
    require_current_controller(run)
    _refuse_terminal(run)
    if not isinstance(reason, str) or not reason.strip():
        raise CandidateQualificationError(f"{command} requires a non-empty reason")
    target = CLOSING_COMMANDS[command]
    working = copy.deepcopy(run)
    working["invalid_reason" if target == "invalidated" else "abandoned_reason"] = reason.strip()
    _record_transition(working, command, target)
    return save_run(root, working)


def invalidate(run_dir: Path, reason: str) -> dict[str, Any]:
    return close_run(run_dir, "invalidate", reason)


def abandon(run_dir: Path, reason: str) -> dict[str, Any]:
    return close_run(run_dir, "abandon", reason)


# -------------------------------------------------------------------- status


def _optional_json(root: Path, relative: str) -> dict[str, Any] | None:
    try:
        path = contained(root, relative, "run file")
        return read_json(path) if path.is_file() else None
    except CandidateQualificationError:
        return None


def status_report(run_dir: Path) -> dict[str, Any]:
    """Read-only summary of a run. Never writes and never requires a match."""
    root, run = load_run(run_dir)
    files = run["files"]
    drift = baseline_drift(root, run)
    frozen = freeze_problems(root, run)

    if "assessment" in run["freezes"]:
        assessment = "frozen"
    elif _optional_json(root, files["assessment"]) is not None:
        assessment = "draft"
    else:
        assessment = "missing"

    candidate = _optional_json(root, files["candidate_manifest"])
    mutations = candidate.get("scope") if candidate and isinstance(candidate.get("scope"), dict) else None

    plan = _optional_json(root, files["qualification_plan"])
    cases: dict[str, Any] | None = None
    missing_results: list[str] | None = None
    plan_cases = plan.get("cases") if plan else None
    if isinstance(plan_cases, list):
        by_role: dict[str, int] = {}
        by_origin: dict[str, int] = {}
        for case in plan_cases:
            if not isinstance(case, dict):
                continue
            role = str(case.get("role"))
            origin = str(case.get("origin"))
            by_role[role] = by_role.get(role, 0) + 1
            by_origin[origin] = by_origin.get(origin, 0) + 1
        cases = {"total": len(plan_cases), "by_role": by_role, "by_origin": by_origin}
        if run["state"] in EXECUTION_STATES:
            missing_results = []
            for case in plan_cases:
                case_id = case.get("case_id") if isinstance(case, dict) else None
                for arm in ARMS:
                    label = f"{case_id}/{arm}"
                    try:
                        path = contained(root, f"cases/{case_id}/{arm}/result.json", "result")
                    except CandidateQualificationError:
                        missing_results.append(label)
                        continue
                    if not path.is_file():
                        missing_results.append(label)

    result = _optional_json(root, files["qualification_result"])
    return {
        "run": str(root),
        "run_id": run["run_id"],
        "domain": run["domain"],
        "state": run["state"],
        "terminal": run["state"] in TERMINAL_STATES,
        "schema_version": run["schema_version"],
        "current_schema": run["schema_version"] == SCHEMA_VERSION,
        "controller_matches": run["controller_sha256"] == controller_sha256(),
        "memory_entry_id": run["memory_entry_id"],
        "scope_limits": run["scope_limits"],
        "baseline": {"status": "drifted" if drift else "clean", "problems": drift},
        "frozen_files": {
            "status": "changed" if frozen else "clean",
            "frozen": sorted(run["freezes"]),
            "problems": frozen,
        },
        "assessment": assessment,
        "candidate_mutations": mutations,
        "cases": cases,
        "missing_results": missing_results,
        "gate": result.get("status") if result else None,
        "invalid_reason": run["invalid_reason"],
        "abandoned_reason": run["abandoned_reason"],
        "canon_modified": False,
    }


# ----------------------------------------------------------------------- CLI


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    status = commands.add_parser("status", help="print a read-only run summary")
    status.add_argument("--run", type=Path, required=True)
    for name, text in (
        ("invalidate", "close a run whose qualification is invalid"),
        ("abandon", "close a run intentionally stopped without an evidence claim"),
    ):
        command = commands.add_parser(name, help=text)
        command.add_argument("--run", type=Path, required=True)
        command.add_argument("--reason", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "status":
            print(json.dumps(status_report(args.run), indent=2, ensure_ascii=False))
        elif args.command == "invalidate":
            run = invalidate(args.run, args.reason)
            print(f"INVALIDATED: {run['run_id']}: {run['invalid_reason']}")
        elif args.command == "abandon":
            run = abandon(args.run, args.reason)
            print(f"ABANDONED: {run['run_id']}: {run['abandoned_reason']}")
        return 0
    except (CandidateQualificationError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
