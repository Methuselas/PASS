#!/usr/bin/env python3
"""Deterministic administration for PASS Candidate Refinement & Qualification.

A CRQ run compares one bounded candidate change to ordinary PASS cards against a
frozen canonical baseline. This controller owns only administration: the run
state machine, atomic state writes, path containment, frozen-file hashes, the
controller fingerprint, baseline-drift detection, intake of one Skillset Memory
`card_candidate`, the structural checks on a defect assessment and a
qualification plan, candidate staging, mutation accounting, and ordinary PASS
validation of a temporary candidate overlay. It never writes `library/` or
Skillset Memory, never calls a model, and never judges domain semantics.

Run directories live under `workspace/candidate-qualification/<domain>/<run-id>/`
and are disposable administration scratch. `controller/run.json` is the
authoritative state of one run.
"""

from __future__ import annotations

import argparse
import contextlib
import copy
import hashlib
import importlib.util
import io
import json
import os
import re
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any, Callable, Iterable

import yaml


SCHEMA_VERSION = 1
# A newer controller may read an older run only when its schema is listed here.
# It never migrates or requalifies an older run.
READABLE_SCHEMA_VERSIONS = frozenset({SCHEMA_VERSION})
WORKSPACE_BUCKET = "workspace/candidate-qualification"
RUNTIME_DIR = Path(__file__).resolve().parent
TOOLS_DIR = RUNTIME_DIR.parent / "tools"
# Defaults only; every command accepts explicit roots so a run never depends on
# this checkout's layout.
REPO_ROOT = RUNTIME_DIR.parents[1]

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
    "intake": "controller/intake.json",
}
RUN_KEYS = frozenset({
    "schema_version", "run_id", "domain", "state", "created_at", "updated_at",
    "controller_sha256", "closing_controller_sha256", "memory_entry_id",
    "library_root", "memory_root", "scope_limits", "files",
    "baseline_manifest_sha256", "freezes", "history", "invalid_reason",
    "abandoned_reason",
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
    """SHA-256 of this controller's source with CRLF normalized to LF.

    A checkout that converts line endings must fingerprint the same controller
    identically. Only the controller is normalized; card and evidence hashes stay
    byte-exact.
    """
    return digest_bytes(Path(__file__).resolve().read_bytes().replace(b"\r\n", b"\n"))


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
        "closing_controller_sha256": None,
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
    closing = run.get("closing_controller_sha256")
    if state in CLOSING_COMMANDS.values():
        if not isinstance(closing, str) or not SHA256_RE.fullmatch(closing):
            errors.append(f"closing_controller_sha256 is required in state {state}")
    elif closing is not None:
        errors.append("closing_controller_sha256 is allowed only in invalidated or abandoned")
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


def require_current_schema(run: dict[str, Any]) -> None:
    """Refuse to write a run recorded under an older controller-state schema."""
    if run["schema_version"] != SCHEMA_VERSION:
        raise CandidateQualificationError(
            f"schema-v{run['schema_version']} runs are read-only under this controller; "
            f"start a fresh schema-v{SCHEMA_VERSION} run"
        )


def require_current_controller(run: dict[str, Any]) -> None:
    """Refuse to continue a run under a different schema or controller."""
    require_current_schema(run)
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

    Neither baseline drift nor a changed controller blocks closing: drift is a
    legitimate reason to invalidate, a run left open across a controller change
    must still be closable, and closing makes no evidence claim. The run keeps
    the fingerprint it was prepared under and records the closing controller's
    beside it.
    """
    if command not in CLOSING_COMMANDS:
        raise CandidateQualificationError(f"unknown closing command: {command}")
    root, run = load_run(run_dir)
    require_current_schema(run)
    _refuse_terminal(run)
    if not isinstance(reason, str) or not reason.strip():
        raise CandidateQualificationError(f"{command} requires a non-empty reason")
    target = CLOSING_COMMANDS[command]
    working = copy.deepcopy(run)
    working["invalid_reason" if target == "invalidated" else "abandoned_reason"] = reason.strip()
    working["closing_controller_sha256"] = controller_sha256()
    _record_transition(working, command, target)
    return save_run(root, working)


def invalidate(run_dir: Path, reason: str) -> dict[str, Any]:
    return close_run(run_dir, "invalidate", reason)


def abandon(run_dir: Path, reason: str) -> dict[str, Any]:
    return close_run(run_dir, "abandon", reason)


# ------------------------------------------------------------- PASS tools


_TOOLS: dict[str, Any] = {}


def load_pass_tool(name: str) -> Any:
    """Import one `PASS/tools` module privately, once.

    The tools import their siblings (`paths`, ...) as top-level modules. The
    tools directory is on `sys.path` only while the module loads, and sibling
    modules it pulled in are dropped again, so neither leaks into this runtime.
    """
    if name in _TOOLS:
        return _TOOLS[name]
    path = TOOLS_DIR / f"{name}.py"
    if not path.is_file():
        raise CandidateQualificationError(f"PASS tool is missing: {path}")
    tools = str(TOOLS_DIR)
    private = f"_pass_crq_tool_{name}"
    before = set(sys.modules)
    sys.path.insert(0, tools)
    try:
        spec = importlib.util.spec_from_file_location(private, path)
        if spec is None or spec.loader is None:
            raise CandidateQualificationError(f"cannot load PASS tool: {path}")
        module = importlib.util.module_from_spec(spec)
        # Registered under its private name while it executes: dataclasses
        # resolve their defining module through sys.modules.
        sys.modules[private] = module
        try:
            spec.loader.exec_module(module)
        except BaseException:
            del sys.modules[private]
            raise
    finally:
        sys.path.remove(tools)
        for leaked in set(sys.modules) - before - {private}:
            origin = getattr(sys.modules[leaked], "__file__", None)
            if origin and Path(origin).resolve().parent == TOOLS_DIR:
                del sys.modules[leaked]
    _TOOLS[name] = module
    return module


def json_safe(value: Any) -> Any:
    """Return plain JSON data; YAML dates become ISO strings."""
    return json.loads(json.dumps(value, default=str, ensure_ascii=False))


# ------------------------------------------------------------ memory intake


CANDIDATE_TYPE = "card_candidate"
CANDIDATE_STATUSES = frozenset({"active", "monitoring"})
INTAKE_KEYS = frozenset({
    "schema_version", "run_id", "domain", "memory_entry", "events",
    "memory_store", "owners",
})
OWNER_RESOLUTIONS = frozenset({"target", "metaskills", "label"})


def quarantined_events(events: list[dict[str, Any]]) -> set[str]:
    """Event ids removed from capability evidence by an evidence correction."""
    return {
        str(target)
        for event in events
        if event.get("event_kind") == "evidence_correction"
        and (event.get("corrections") or {}).get("disposition") == "quarantined"
        for target in (event.get("supersedes_events") or [])
    }


def resolve_memory_candidate(memory_root: Path, domain: str, entry_id: str) -> dict[str, Any]:
    """Resolve one `card_candidate` and its cited events through `memory.py`.

    The whole store must pass `memory.py validate` first; the entry-level checks
    below then name exactly why this entry cannot start a run.
    """
    memory = load_pass_tool("memory")
    domain_dir = Path(memory_root) / domain
    if not (domain_dir / "skill_memory.yaml").is_file():
        raise CandidateQualificationError(
            f"no Skillset Memory store for domain {domain!r} under {Path(memory_root)}"
        )
    problems = memory.validate_store(domain_dir)
    if problems:
        shown = "; ".join(problems[:10]) + ("; ..." if len(problems) > 10 else "")
        raise CandidateQualificationError(
            f"memory store {domain!r} fails memory.py validate: {shown}"
        )
    try:
        store = memory.load_memory(domain_dir)
    except memory.MemoryError_ as exc:
        raise CandidateQualificationError(str(exc)) from exc
    entry = memory.find_entry(store.get("entries") or [], entry_id)
    if entry is None:
        raise CandidateQualificationError(f"memory entry {entry_id} does not exist in {domain}")
    if entry.get("type") != CANDIDATE_TYPE:
        raise CandidateQualificationError(
            f"memory entry {entry_id} is {entry.get('type')}, not {CANDIDATE_TYPE}"
        )
    if entry.get("status") not in CANDIDATE_STATUSES:
        raise CandidateQualificationError(
            f"memory entry {entry_id} is {entry.get('status')}; only active or "
            "monitoring candidates can start a run"
        )
    cited = entry.get("evidence_events") or []
    if not cited:
        raise CandidateQualificationError(
            f"memory entry {entry_id} cites no evidence event; link valid evidence "
            "with memory.py compact before starting a run"
        )
    events, _ = memory.load_events(domain_dir)
    by_id = {event.get("event_id"): event for event in events}
    quarantined = quarantined_events(events)
    selected = []
    for event_id in cited:
        event = by_id.get(event_id)
        if event is None:
            raise CandidateQualificationError(f"{entry_id} cites unknown event {event_id}")
        if event.get("validity") != "valid":
            raise CandidateQualificationError(f"{entry_id} cites invalid event {event_id}")
        if event.get("event_kind", "performance") != "performance":
            raise CandidateQualificationError(f"{entry_id} cites correction {event_id}")
        if event_id in quarantined:
            raise CandidateQualificationError(f"{entry_id} cites quarantined event {event_id}")
        selected.append(event)
    return {
        "memory_entry": json_safe(entry),
        "events": json_safe(selected),
        "memory_store": {
            "memory_schema_version": store.get("memory_schema_version"),
            "memory_version": store.get("memory_version"),
        },
    }


def exposed_card_ids(events: list[dict[str, Any]]) -> set[str] | None:
    """Cards the cited evidence declares it exposed, or None when no event says."""
    exposed: set[str] | None = None
    for event in events:
        intervention = event.get("intervention")
        if not isinstance(intervention, dict):
            continue
        components = intervention.get("components")
        card_ids = components.get("card_ids") if isinstance(components, dict) else None
        if isinstance(card_ids, list):
            exposed = (exposed or set()) | {str(item) for item in card_ids}
    return exposed


# ------------------------------------------------------------ library cards


SHARED_PACKAGE = "metaskills"
MODULE_MANIFEST = "MODULE.yaml"
OBJECT_TYPES = frozenset({"pattern", "ap", "drill"})
OBJECT_PREFIXES = {"pattern": "PAT_", "ap": "AP_", "drill": "DRILL_"}
OBJECT_ID_RE = re.compile(r"(?:PAT|DRILL|AP)_[a-z0-9][a-z0-9_]*\Z")
FRONTMATTER_RE = re.compile(r"\A---\n(?P<front>.*?)\n---\n", re.DOTALL)
# Relations that make one card a prerequisite of executing another. They are
# followed transitively; every other outgoing link is followed one hop.
HARD_INCOMING_RELATIONS = frozenset({"prerequisite_for", "foundation_of"})
HARD_OUTGOING_RELATIONS = frozenset({"variant_of"})


def card_text(raw: bytes) -> str:
    """A card's text for parsing: CRLF and LF read alike. Hashes use raw bytes."""
    return raw.decode("utf-8", errors="replace").replace("\r\n", "\n")


def card_frontmatter(path: Path) -> dict[str, Any] | None:
    try:
        match = FRONTMATTER_RE.match(card_text(path.read_bytes()))
        data = yaml.safe_load(match.group("front")) if match else None
    except (OSError, UnicodeDecodeError, yaml.YAMLError):
        return None
    return data if isinstance(data, dict) else None


def card_index(library_root: Path, packages: Iterable[str]) -> dict[str, dict[str, Any]]:
    """Index the cards of the named packages only; other domains are never read."""
    index: dict[str, dict[str, Any]] = {}
    library_root = Path(library_root)
    for package in sorted(set(packages)):
        base = library_root / package
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*.md")):
            if path.name in {"README.md", "INDEX.md"}:
                continue
            data = card_frontmatter(path)
            if not data or not isinstance(data.get("object_id"), str):
                continue
            object_id = data["object_id"]
            if object_id in index:
                raise CandidateQualificationError(f"duplicate object_id in canon: {object_id}")
            index[object_id] = {
                "relative_path": path.relative_to(library_root).as_posix(),
                "package": package,
                "object_type": data.get("object_type"),
                "data": data,
            }
    return index


def card_links(data: dict[str, Any]) -> list[tuple[str, str]]:
    links = []
    foundation = data.get("foundation_object_id")
    if isinstance(foundation, str) and foundation and foundation != "none":
        links.append(("foundation", foundation))
    for link in data.get("cross_links") or []:
        if isinstance(link, dict) and isinstance(link.get("target_object_id"), str):
            links.append((str(link.get("rel")), link["target_object_id"]))
    return links


def support_closure(
    targets: Iterable[str], index: dict[str, dict[str, Any]], domain: str
) -> set[str]:
    """The bounded bundle needed to execute the targets, excluding the targets.

    Hard prerequisites (foundation, variant_of, and incoming prerequisite_for or
    foundation_of) are followed transitively; a target's other outgoing links
    are followed one hop. The release closure follows every link transitively
    and would freeze most of a domain.
    """
    targets = set(targets)
    incoming: dict[str, set[str]] = {}
    for source, info in index.items():
        for rel, target in card_links(info["data"]):
            if rel in HARD_INCOMING_RELATIONS:
                incoming.setdefault(target, set()).add(source)

    def require(object_id: str, owner: str) -> None:
        if object_id not in index:
            raise CandidateQualificationError(
                f"{owner} needs {object_id}, which is not a card in {domain} or {SHARED_PACKAGE}"
            )

    selected = set(targets)
    pending = list(targets)
    while pending:
        current = pending.pop()
        hard = set(incoming.get(current, set()))
        for rel, target in card_links(index[current]["data"]):
            if rel == "foundation" or rel in HARD_OUTGOING_RELATIONS:
                hard.add(target)
        for object_id in sorted(hard):
            require(object_id, current)
            if object_id not in selected:
                selected.add(object_id)
                pending.append(object_id)
    for target in sorted(targets):
        for _rel, object_id in card_links(index[target]["data"]):
            require(object_id, target)
            selected.add(object_id)
    return selected - targets


def module_manifest_for(library_root: Path, relative_path: str) -> str | None:
    """The nearest `MODULE.yaml` at or above a card, inside its package."""
    parts = PurePosixPath(relative_path).parts[:-1]
    for depth in range(len(parts), 0, -1):
        candidate = PurePosixPath(*parts[:depth], MODULE_MANIFEST)
        if (Path(library_root) / candidate).is_file():
            return candidate.as_posix()
    return None


# ------------------------------------------------------------------ prepare


def run_id_prefix(domain: str, memory_entry_id: str) -> str:
    match = re.fullmatch(r"([A-Z][A-Z0-9]*(?:_[A-Z0-9]+)*?)_MEM_[0-9]+", memory_entry_id)
    return match.group(1) if match else re.sub(r"[^A-Z0-9]+", "_", domain.upper()).strip("_")


def next_run_id(domain_dir: Path, prefix: str) -> str:
    """Next local run id; scans only this domain's candidate-qualification folder."""
    pattern = re.compile(re.escape(prefix) + r"_CRQ_([0-9]{4,})\Z")
    highest = 0
    if domain_dir.is_dir():
        for child in domain_dir.iterdir():
            match = pattern.fullmatch(child.name)
            if match:
                highest = max(highest, int(match.group(1)))
    return f"{prefix}_CRQ_{highest + 1:04d}"


def resolve_run_dir(
    out: Path | None, domain: str, memory_entry_id: str, protected: Iterable[Path]
) -> Path:
    """Choose or check `<...>/candidate-qualification/<domain>/<run-id>`."""
    if out is None:
        domain_dir = REPO_ROOT / WORKSPACE_BUCKET / domain
        out = domain_dir / next_run_id(domain_dir, run_id_prefix(domain, memory_entry_id))
    out = Path(out).resolve()
    if not RUN_ID_RE.fullmatch(out.name):
        raise CandidateQualificationError(f"run directory name must be a run id like SE_CRQ_0001: {out.name}")
    if out.parent.name != domain or out.parent.parent.name != PurePosixPath(WORKSPACE_BUCKET).name:
        raise CandidateQualificationError(
            f"a run lives at .../{PurePosixPath(WORKSPACE_BUCKET).name}/{domain}/<run-id>: {out}"
        )
    for root in protected:
        try:
            out.relative_to(Path(root).resolve())
        except ValueError:
            continue
        raise CandidateQualificationError(f"a run may not live inside {root}")
    return out


def resolve_owners(
    likely_owners: Iterable[Any], index: dict[str, dict[str, Any]], domain: str
) -> list[dict[str, Any]]:
    """Classify each likely owner; an object id that does not resolve fails."""
    owners = []
    for label in likely_owners:
        label = str(label)
        if not OBJECT_ID_RE.fullmatch(label):
            owners.append({"label": label, "object_id": None, "resolution": "label"})
            continue
        info = index.get(label)
        if info is None:
            raise CandidateQualificationError(
                f"likely owner {label} is not a card in {domain} or {SHARED_PACKAGE}; a "
                "CRQ run authors one domain and never couples to another"
            )
        resolution = "target" if info["package"] == domain else "metaskills"
        owners.append({"label": label, "object_id": label, "resolution": resolution})
    return owners


def validate_intake(intake: Any, run: dict[str, Any]) -> list[str]:
    if not isinstance(intake, dict) or set(intake) != INTAKE_KEYS:
        return [f"intake must have exactly {sorted(INTAKE_KEYS)}"]
    errors = []
    if intake["schema_version"] != SCHEMA_VERSION or intake["run_id"] != run["run_id"]:
        errors.append("intake belongs to a different run or schema")
    if intake["domain"] != run["domain"]:
        errors.append("intake domain does not match the run")
    entry = intake["memory_entry"]
    if not isinstance(entry, dict) or entry.get("id") != run["memory_entry_id"]:
        errors.append("intake memory entry does not match the run")
    if not isinstance(intake["events"], list) or not intake["events"]:
        errors.append("intake must carry the cited evidence events")
    owners = intake["owners"]
    if not isinstance(owners, list) or any(
        not isinstance(owner, dict) or owner.get("resolution") not in OWNER_RESOLUTIONS
        for owner in owners
    ):
        errors.append("intake owners must each carry a known resolution")
    return errors


def load_intake(root: Path, run: dict[str, Any]) -> dict[str, Any]:
    if "intake" not in run["freezes"]:
        raise CandidateQualificationError("this run has no frozen memory intake")
    intake = read_json(contained(root, run["files"]["intake"], "intake"))
    errors = validate_intake(intake, run)
    if errors:
        raise CandidateQualificationError("invalid intake: " + "; ".join(errors))
    return intake


def assessment_template(run: dict[str, Any]) -> dict[str, Any]:
    """Blank assessment; every judgment field must be filled before freezing."""
    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": run["run_id"],
        "memory_entry_id": run["memory_entry_id"],
        "candidate_disposition": None,
        "failure_layer": None,
        "primary_attribution": None,
        "owner_object_ids": [],
        "proposed_object_actions": [],
        "noncanon_failures_considered": [],
        "rationale": "",
        "unresolved_questions": [],
    }


def prepare(
    *,
    domain: str,
    memory_entry_id: str,
    out: Path | None = None,
    library_root: Path | None = None,
    memory_root: Path | None = None,
    max_changed_cards: int | None = None,
    max_new_cards: int | None = None,
    override_reason: str | None = None,
) -> tuple[Path, dict[str, Any]]:
    """Start a run from one `card_candidate`: intake, baseline, and brief.

    Checks run before anything is written. The run directory appears only after
    the baseline snapshot verifies against canon.
    """
    if not DOMAIN_RE.fullmatch(domain or ""):
        raise CandidateQualificationError(f"domain must be a library package name: {domain!r}")
    library = Path(library_root or REPO_ROOT / "library").resolve()
    memory_dir = Path(memory_root or REPO_ROOT / "memory").resolve()
    if not (library / domain).is_dir():
        raise CandidateQualificationError(f"library package not found: {library / domain}")
    resolved = resolve_memory_candidate(memory_dir, domain, memory_entry_id)
    entry = resolved["memory_entry"]
    index = card_index(library, {domain, SHARED_PACKAGE})
    owners = resolve_owners(entry.get("likely_owners") or [], index, domain)
    targets = [owner["object_id"] for owner in owners if owner["resolution"] == "target"]
    if not targets:
        raise CandidateQualificationError(
            f"{memory_entry_id} names no likely owner that is a card in {domain}; "
            "add the exact object_id of the owner (or of the nearest existing card a "
            "new card would join) with memory.py entry update, then prepare again"
        )
    anchors = targets + [o["object_id"] for o in owners if o["resolution"] == "metaskills"]
    support = support_closure(anchors, index, domain) | (set(anchors) - set(targets))
    out = resolve_run_dir(out, domain, memory_entry_id, (library, memory_dir))
    run = new_run_record(
        run_id=out.name,
        domain=domain,
        memory_entry_id=memory_entry_id,
        library_root=library,
        memory_root=memory_dir,
        max_changed_cards=max_changed_cards,
        max_new_cards=max_new_cards,
        override_reason=override_reason,
    )

    entries: list[dict[str, Any]] = []
    for role, object_ids in (("target", sorted(set(targets))), ("support", sorted(support))):
        for object_id in object_ids:
            entries.append(baseline_entry(library, index[object_id]["relative_path"], object_id, role))
    manifests = sorted({
        manifest
        for item in entries
        if (manifest := module_manifest_for(library, item["relative_path"])) is not None
    })
    entries.extend(baseline_entry(library, manifest, None, "module-manifest") for manifest in manifests)

    def populate(staging: Path, run: dict[str, Any]) -> None:
        for item in entries:
            source = contained(library, item["relative_path"], "baseline path")
            destination = contained(staging, f"baseline/cards/{item['relative_path']}", "snapshot")
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)
        manifest_path = contained(staging, run["files"]["baseline_manifest"], "baseline manifest")
        write_json_atomic(manifest_path, {
            "schema_version": SCHEMA_VERSION,
            "run_id": run["run_id"],
            "entries": entries,
        })
        run["baseline_manifest_sha256"] = digest_file(manifest_path)
        intake = {
            "schema_version": SCHEMA_VERSION,
            "run_id": run["run_id"],
            "domain": domain,
            "owners": owners,
            **resolved,
        }
        write_json_atomic(contained(staging, run["files"]["intake"], "intake"), intake)
        record_freeze(staging, run, "intake", [run["files"]["intake"]])
        write_json_atomic(
            contained(staging, run["files"]["assessment"], "assessment"),
            assessment_template(run),
        )
        write_text_atomic(staging / "README.md", assessment_brief(run, intake, entries))

    run = initialize_run(out, run, populate)
    return out, run


# --------------------------------------------------------------- assessment


CANDIDATE_DISPOSITIONS = (
    "canon-candidate", "memory-only", "runtime-tool-repair", "fixture-repair",
    "source-context-review", "fresh-retest", "no-action", "unresolved",
)
PRIMARY_ATTRIBUTIONS = (
    "skillcard", "application", "source-context", "fixture", "runtime-tool",
    "unresolved", "other",
)
# Only a missing or wrong reusable decision, orchestration, or practice can
# justify a card change; the other Skillset Memory failure layers cannot.
CANON_FAILURE_LAYERS = {"knowledge": "pattern", "orchestration": "ap", "training": "drill"}
ASSESSMENT_KEYS = frozenset({
    "schema_version", "run_id", "memory_entry_id", "candidate_disposition",
    "failure_layer", "primary_attribution", "owner_object_ids",
    "proposed_object_actions", "noncanon_failures_considered", "rationale",
    "unresolved_questions",
})
OBJECT_ACTIONS = ("revise", "create")
ACTION_KEYS = frozenset({"action", "object_id", "object_type", "reason"})
ACTION_OPTIONAL_KEYS = frozenset({"relative_path", "routing_reason"})
NONCANON_KEYS = frozenset({"kind", "disposition", "reason"})
NONCANON_DISPOSITIONS = ("not-supported", "supported", "unresolved")
QUESTION_KEYS = frozenset({"question", "decides_ownership"})


def baseline_objects(root: Path, manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Frozen baseline cards by object id, typed from their snapshot bytes."""
    objects = {}
    for entry in manifest["entries"]:
        if entry["role"] == "module-manifest":
            continue
        data = card_frontmatter(contained(root, f"baseline/cards/{entry['relative_path']}", "snapshot"))
        objects[entry["object_id"]] = {
            "relative_path": entry["relative_path"],
            "role": entry["role"],
            "package": PurePosixPath(entry["relative_path"]).parts[0],
            "object_type": (data or {}).get("object_type"),
        }
    return objects


def validate_assessment(
    assessment: Any,
    *,
    run: dict[str, Any],
    baseline: dict[str, dict[str, Any]],
    exposed: set[str] | None,
    failure_layers: Iterable[str],
    library_root: Path,
    existing_ids: Iterable[str] = (),
) -> list[str]:
    """Every structural reason the assessment cannot be frozen; empty means valid.

    This checks shape, routing and scope. Whether the canon really owns the
    defect is the assessor's judgment, recorded in the rationale.
    """
    if not isinstance(assessment, dict):
        return ["assessment must be a JSON object"]
    errors: list[str] = []
    missing = sorted(ASSESSMENT_KEYS - set(assessment))
    unknown = sorted(set(assessment) - ASSESSMENT_KEYS)
    if missing:
        errors.append("missing assessment key(s): " + ", ".join(missing))
    if unknown:
        errors.append("unknown assessment key(s): " + ", ".join(unknown))
    if assessment.get("schema_version") != SCHEMA_VERSION:
        errors.append("assessment schema_version mismatch")
    if assessment.get("run_id") != run["run_id"]:
        errors.append("assessment belongs to a different run")
    if assessment.get("memory_entry_id") != run["memory_entry_id"]:
        errors.append("assessment names a different memory entry")

    disposition = assessment.get("candidate_disposition")
    if disposition not in CANDIDATE_DISPOSITIONS:
        errors.append(f"candidate_disposition must be one of {list(CANDIDATE_DISPOSITIONS)}")
    layer = assessment.get("failure_layer")
    if layer not in set(failure_layers):
        errors.append(f"failure_layer must be one of {sorted(failure_layers)}")
    attribution = assessment.get("primary_attribution")
    if attribution not in PRIMARY_ATTRIBUTIONS:
        errors.append(f"primary_attribution must be one of {list(PRIMARY_ATTRIBUTIONS)}")
    if not _nonempty_str(assessment.get("rationale")):
        errors.append("rationale must explain the attribution")
    canon = disposition == "canon-candidate"

    owners = assessment.get("owner_object_ids")
    if not isinstance(owners, list) or any(not isinstance(item, str) for item in owners):
        errors.append("owner_object_ids must be a list of object ids")
        owners = []
    elif len(owners) != len(set(owners)):
        errors.append("owner_object_ids may not repeat")
    for object_id in owners:
        if object_id not in baseline:
            errors.append(f"owner {object_id} is not a card in the frozen baseline")

    considered = assessment.get("noncanon_failures_considered")
    if not isinstance(considered, list):
        errors.append("noncanon_failures_considered must be a list")
        considered = []
    for index, item in enumerate(considered):
        if (
            not isinstance(item, dict) or set(item) != NONCANON_KEYS
            or not _nonempty_str(item.get("kind")) or not _nonempty_str(item.get("reason"))
            or item.get("disposition") not in NONCANON_DISPOSITIONS
        ):
            errors.append(
                f"noncanon_failures_considered[{index}] needs kind, reason and a "
                f"disposition in {list(NONCANON_DISPOSITIONS)}"
            )

    questions = assessment.get("unresolved_questions")
    if not isinstance(questions, list):
        errors.append("unresolved_questions must be a list")
        questions = []
    for index, item in enumerate(questions):
        if (
            not isinstance(item, dict) or set(item) != QUESTION_KEYS
            or not _nonempty_str(item.get("question"))
            or not isinstance(item.get("decides_ownership"), bool)
        ):
            errors.append(f"unresolved_questions[{index}] needs question and a boolean decides_ownership")

    actions = assessment.get("proposed_object_actions")
    if not isinstance(actions, list):
        errors.append("proposed_object_actions must be a list")
        actions = []
    if actions and not canon:
        errors.append("only a canon-candidate may propose object actions")
    seen: set[str] = set()
    counts = {"revise": 0, "create": 0}
    for index, action in enumerate(actions):
        label = f"proposed_object_actions[{index}]"
        if not isinstance(action, dict):
            errors.append(f"{label} must be an object")
            continue
        keys = set(action)
        if not ACTION_KEYS <= keys or keys - ACTION_KEYS - ACTION_OPTIONAL_KEYS:
            errors.append(
                f"{label} must have {sorted(ACTION_KEYS)} and optionally "
                f"{sorted(ACTION_OPTIONAL_KEYS)}"
            )
            continue
        kind, object_id, object_type = action["action"], action["object_id"], action["object_type"]
        if kind not in OBJECT_ACTIONS:
            errors.append(
                f"{label}: action {kind!r} is not allowed; v1 may only revise or create "
                "(never delete, rename or move)"
            )
            continue
        counts[kind] += 1
        if not isinstance(object_id, str) or not OBJECT_ID_RE.fullmatch(object_id):
            errors.append(f"{label}: object_id must be a card id like PAT_example")
            continue
        if object_id in seen:
            errors.append(f"{label}: {object_id} has more than one action")
        seen.add(object_id)
        if object_type not in OBJECT_TYPES:
            errors.append(f"{label}: object_type must be one of {sorted(OBJECT_TYPES)}")
        elif not object_id.startswith(OBJECT_PREFIXES[object_type]):
            errors.append(f"{label}: {object_type} ids start with {OBJECT_PREFIXES[object_type]}")
        if not _nonempty_str(action["reason"]):
            errors.append(f"{label}: reason must be non-empty")
        if "routing_reason" in action and not _nonempty_str(action["routing_reason"]):
            errors.append(f"{label}: routing_reason must be non-empty when present")
        natural = CANON_FAILURE_LAYERS.get(layer)
        if canon and natural and object_type in OBJECT_TYPES and object_type != natural:
            if not _nonempty_str(action.get("routing_reason")):
                errors.append(
                    f"{label}: a {layer} defect normally belongs to a {natural}; routing it "
                    f"to a {object_type} needs a routing_reason saying why that card itself "
                    "is defective"
                )
        if kind == "revise":
            if "relative_path" in action:
                errors.append(f"{label}: a revision takes its path from the baseline")
            info = baseline.get(object_id)
            if info is None:
                errors.append(f"{label}: {object_id} is not in the frozen baseline; start a fresh run whose candidate names it")
                continue
            if info["package"] != run["domain"]:
                errors.append(
                    f"{label}: {object_id} is in {info['package']}; a CRQ run modifies only "
                    f"{run['domain']}, and a {SHARED_PACKAGE} defect needs its own authorized run"
                )
            if info["object_type"] != object_type:
                errors.append(f"{label}: {object_id} is a {info['object_type']}, not a {object_type}")
            if object_id not in owners:
                errors.append(f"{label}: a revised card must be listed in owner_object_ids")
        else:
            relative = action.get("relative_path")
            try:
                path = safe_relative(relative, f"{label} relative_path")
            except CandidateQualificationError as exc:
                errors.append(str(exc))
                continue
            if path.parts[0] != run["domain"] or len(path.parts) < 3:
                errors.append(f"{label}: a new card belongs in a {run['domain']} module folder")
            if path.name != f"{object_id}.md":
                errors.append(f"{label}: a new card file is named {object_id}.md")
            if object_id in baseline or object_id in set(existing_ids):
                errors.append(f"{label}: {object_id} already exists")
            elif (Path(library_root) / Path(*path.parts)).exists():
                errors.append(f"{label}: {relative} already exists in the library")

    limits = run["scope_limits"]
    if counts["revise"] > limits["max_changed_cards"]:
        errors.append(
            f"{counts['revise']} revised cards exceed max_changed_cards {limits['max_changed_cards']}"
        )
    if counts["create"] > limits["max_new_cards"]:
        errors.append(f"{counts['create']} new cards exceed max_new_cards {limits['max_new_cards']}")

    if canon:
        if not actions:
            errors.append("a canon-candidate must propose at least one object action")
        if layer in set(failure_layers) and layer not in CANON_FAILURE_LAYERS:
            errors.append(
                f"a {layer} failure cannot justify a card change; only "
                f"{sorted(CANON_FAILURE_LAYERS)} failures can"
            )
        if attribution in PRIMARY_ATTRIBUTIONS and attribution != "skillcard":
            errors.append(f"a canon-candidate must be attributed to skillcard, not {attribution}")
        if not owners and not counts["create"]:
            errors.append("a skillcard attribution names an exact owner or proposes a new card")
        if not considered:
            errors.append("a canon-candidate must record the non-canon causes it considered")
        for item in considered:
            if isinstance(item, dict) and item.get("disposition") == "unresolved":
                errors.append(f"non-canon cause {item.get('kind')!r} is unresolved; it decides ownership")
        for item in questions:
            if isinstance(item, dict) and item.get("decides_ownership") is True:
                errors.append(f"unresolved question decides ownership: {item.get('question')}")
        if exposed is not None:
            for object_id in owners:
                info = baseline.get(object_id) or {}
                if info.get("object_type") in {"pattern", "ap"} and object_id not in exposed:
                    errors.append(
                        f"{object_id} was not exposed by the cited evidence; a skillcard "
                        "attribution needs the card to have been exposed"
                    )
    return errors


def freeze_assessment(run_dir: Path) -> dict[str, Any]:
    """Validate `controller/assessment.json` and freeze it; never re-freezes."""
    failure_layers = load_pass_tool("memory").FAILURE_LAYERS

    def update(root: Path, run: dict[str, Any]) -> None:
        manifest = load_baseline_manifest(root, run)
        intake = load_intake(root, run)
        path = contained(root, run["files"]["assessment"], "assessment")
        if not path.is_file():
            raise CandidateQualificationError("controller/assessment.json is missing")
        errors = validate_assessment(
            read_json(path),
            run=run,
            baseline=baseline_objects(root, manifest),
            exposed=exposed_card_ids(intake["events"]),
            failure_layers=failure_layers,
            library_root=Path(run["library_root"]),
            existing_ids=card_index(Path(run["library_root"]), {run["domain"], SHARED_PACKAGE}),
        )
        if errors:
            raise CandidateQualificationError("assessment cannot be frozen: " + "; ".join(errors))
        record_freeze(root, run, "assessment", [run["files"]["assessment"]])
        plan = contained(root, run["files"]["qualification_plan"], "qualification plan")
        if not plan.exists():
            write_json_atomic(plan, plan_template(run))

    return apply_transition(run_dir, "freeze-assessment", update)


def assessment_brief(run: dict[str, Any], intake: dict[str, Any], entries: list[dict[str, Any]]) -> str:
    """The operator brief for the assessment phase, written to `README.md`."""
    entry = intake["memory_entry"]
    diagnosis = entry.get("diagnosis") or {}
    limits = run["scope_limits"]
    events = intake["events"]
    lines = [
        f"# CRQ run {run['run_id']} ({run['domain']})",
        "",
        "Administration scratch for one Candidate Refinement & Qualification run.",
        "It never ships and nothing here enters a card or Skillset Memory. Do not",
        "edit `library/`; a qualified candidate still needs deliberate synthesis review.",
        "",
        f"## Memory candidate {entry.get('id')}",
        "",
        f"- Status: {entry.get('status')}; confidence: {entry.get('confidence')}; "
        f"evidence class: {entry.get('evidence_class')}",
        f"- Observation: {' '.join(str(entry.get('observation', '')).split())}",
        f"- Diagnosis: {diagnosis.get('failure_layer', 'not recorded')}"
        + (f" ({' '.join(str(diagnosis['hypothesis']).split())})" if diagnosis.get("hypothesis") else ""),
        "",
        "Likely owners:",
        "",
    ]
    for owner in intake["owners"]:
        meaning = {
            "target": "editable target in this domain",
            "metaskills": f"{SHARED_PACKAGE} card; frozen as support, never modified by this run",
            "label": "free-text label; not a card",
        }[owner["resolution"]]
        lines.append(f"- `{owner['label']}`: {meaning}")
    lines += ["", f"Cited evidence ({len(events)} event(s), frozen in `controller/intake.json`):", ""]
    lines += [f"- {event.get('event_id')}: {' '.join(str(event.get('task', '')).split())}" for event in events]
    if len(events) > 24:
        lines += ["", "More than 24 events: hierarchical synthesis is required before assessment unless the user chooses direct review."]
    elif len(events) > 8:
        lines += ["", "More than 8 events: hierarchical synthesis is recommended before assessment."]
    lines += ["", "## Frozen baseline", ""]
    lines += [f"- {item['role']}: `{item['relative_path']}`" for item in entries]
    lines += [
        "",
        "## Assess the defect",
        "",
        "Fill `controller/assessment.json`, then run `freeze-assessment`. A frozen",
        "assessment is never revised in place; a different conclusion starts a fresh run.",
        "",
        f"- `candidate_disposition`: one of {', '.join(CANDIDATE_DISPOSITIONS)}. Only",
        "  `canon-candidate` can go on to candidate authoring.",
        f"- `primary_attribution`: one of {', '.join(PRIMARY_ATTRIBUTIONS)}; a canon-candidate is `skillcard`.",
        "- `failure_layer`: the Skillset Memory vocabulary. Route by layer:",
        "  - knowledge: a missing or wrong reusable decision belongs to a Pattern;",
        "  - orchestration: a missing or wrong goal-directed flow belongs to an AP;",
        "  - training: a defective practice or evaluation belongs to a Drill;",
        "  - retrieval, application, continuity, reference, tool and interface failures",
        "    never justify a card change: route them to memory, the runtime, the fixture",
        "    or a fresh retest.",
        "- A repair routed against its layer (for example an orchestration defect to a",
        "  Pattern) needs a `routing_reason` saying why that card itself is defective.",
        "- `owner_object_ids`: exact baseline cards. A skillcard attribution needs the card",
        "  to have been exposed when the cited evidence records what it exposed.",
        "- `proposed_object_actions`: `revise` a baseline card of this domain, or `create`",
        "  a new card with its `relative_path`. Delete, rename and move are never allowed.",
        f"  Ceilings: {limits['max_changed_cards']} revised, {limits['max_new_cards']} new.",
        "- `noncanon_failures_considered`: each non-canon cause weighed, with disposition",
        f"  {', '.join(NONCANON_DISPOSITIONS)}; an unresolved one blocks a canon-candidate.",
        "- `unresolved_questions`: `{question, decides_ownership}`; a question that decides",
        "  ownership blocks a canon-candidate.",
        "",
        "## Plan the qualification",
        "",
        "After the assessment freezes, fill `controller/qualification_plan.json` and write",
        "`cases/<CASE_ID>/case.json` for every planned case, then run `freeze-plan`. The plan",
        "freezes before any candidate is staged, so held-out cases cannot shape the edit.",
        "",
        f"- Each plan case: {', '.join(sorted(PLAN_CASE_KEYS))}; a synthetic case adds",
        "  `in_scope_reason`. `case.json` repeats the metadata and adds `task`,",
        "  `success_contract`, `constraints`, `fixture_manifest` and `notes`.",
        f"- role {'/'.join(CASE_ROLES)}; origin {'/'.join(CASE_ORIGINS)}; evaluation_mode",
        f"  {'/'.join(EVALUATION_MODES)}; visibility {'/'.join(VISIBILITIES)}; evaluator_relation",
        f"  {'/'.join(EVALUATOR_RELATIONS)}.",
        "- A synthetic case is only a protected stress probe: never positive qualification,",
        "  never an empirical event. A required semantic case is graded by a separate",
        "  evaluator; a deterministic case is checked deterministically.",
        "- The plan needs a required non-synthetic target case eligible for positive",
        "  qualification. Without a required non-synthetic protected case it must record",
        "  `protected_case_gap`, and the run cannot qualify beyond that gap.",
        "- Fixtures live under `cases/<CASE_ID>/fixture/` and are each listed with a sha256.",
        "",
    ]
    return "\n".join(lines)


# ------------------------------------------------------- qualification plan


CASE_ROLES = ("target", "protected")
CASE_ORIGINS = ("empirical", "deterministic", "synthetic")
EVALUATION_MODES = ("deterministic", "semantic")
VISIBILITIES = ("author-visible", "held-out")
EVALUATOR_RELATIONS = ("deterministic", "separate", "same-reader")
CASE_ID_RE = re.compile(r"[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)*\Z")
PLAN_KEYS = frozenset({"schema_version", "run_id", "cases", "protected_case_gap"})
# Plan metadata that each case.json repeats and must agree with.
CASE_METADATA = (
    "role", "origin", "evaluation_mode", "visibility", "required",
    "positive_qualification_eligible", "evaluator_relation", "source_event_ids",
)
PLAN_CASE_KEYS = frozenset({"case_id", "purpose", *CASE_METADATA})
PLAN_CASE_OPTIONAL_KEYS = frozenset({"in_scope_reason"})
CASE_KEYS = frozenset({
    "schema_version", "case_id", *CASE_METADATA, "task", "success_contract",
    "constraints", "fixture_manifest", "notes",
})
FIXTURE_ENTRY_KEYS = frozenset({"path", "sha256"})
CASE_FILE = "case.json"
FIXTURE_DIR = "fixture"


def plan_template(run: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": run["run_id"],
        "cases": [],
        "protected_case_gap": None,
    }


def admissible_event_ids(memory_root: Path, domain: str) -> set[str]:
    """Events a case may cite: valid, performance, not quarantined."""
    memory = load_pass_tool("memory")
    events, _ = memory.load_events(Path(memory_root) / domain)
    quarantined = quarantined_events(events)
    return {
        str(event["event_id"])
        for event in events
        if isinstance(event.get("event_id"), str)
        and event.get("validity") == "valid"
        and event.get("event_kind", "performance") == "performance"
        and event["event_id"] not in quarantined
    }


def validate_plan_entry(entry: Any, label: str, admissible: set[str]) -> list[str]:
    """Rules one plan case must satisfy on its own."""
    if not isinstance(entry, dict):
        return [f"{label} must be an object"]
    keys = set(entry)
    if not PLAN_CASE_KEYS <= keys or keys - PLAN_CASE_KEYS - PLAN_CASE_OPTIONAL_KEYS:
        return [f"{label} must have {sorted(PLAN_CASE_KEYS)} and optionally {sorted(PLAN_CASE_OPTIONAL_KEYS)}"]
    errors: list[str] = []
    for key, allowed in (
        ("role", CASE_ROLES), ("origin", CASE_ORIGINS), ("evaluation_mode", EVALUATION_MODES),
        ("visibility", VISIBILITIES), ("evaluator_relation", EVALUATOR_RELATIONS),
    ):
        if entry[key] not in allowed:
            errors.append(f"{label}: {key} must be one of {list(allowed)}")
    for key in ("required", "positive_qualification_eligible"):
        if not isinstance(entry[key], bool):
            errors.append(f"{label}: {key} must be true or false")
    if not _nonempty_str(entry["purpose"]):
        errors.append(f"{label}: purpose must say what the case protects or proves")
    events = entry["source_event_ids"]
    if not isinstance(events, list) or any(not isinstance(item, str) for item in events):
        errors.append(f"{label}: source_event_ids must be a list of event ids")
        events = []
    elif len(events) != len(set(events)):
        errors.append(f"{label}: source_event_ids may not repeat")
    for event_id in events:
        if event_id not in admissible:
            errors.append(
                f"{label}: {event_id} is not a valid, uncorrected, unquarantined event in this domain's history"
            )

    origin, role = entry["origin"], entry["role"]
    eligible = entry["positive_qualification_eligible"]
    if origin == "synthetic":
        if role != "protected":
            errors.append(f"{label}: a synthetic case is a stress probe and may only be protected")
        if eligible is not False:
            errors.append(f"{label}: a synthetic case never provides positive qualification")
        if events:
            errors.append(f"{label}: a synthetic case cites no empirical event")
        if not _nonempty_str(entry.get("in_scope_reason")):
            errors.append(f"{label}: a synthetic case needs in_scope_reason saying why it stays inside the card's contract")
    elif "in_scope_reason" in entry:
        errors.append(f"{label}: in_scope_reason belongs only to a synthetic case")
    if origin == "empirical" and not events:
        errors.append(f"{label}: an empirical case cites the events it comes from")
    if eligible is True and role != "target":
        errors.append(f"{label}: only a target case can provide positive qualification")

    mode, relation = entry["evaluation_mode"], entry["evaluator_relation"]
    if mode == "deterministic" and relation != "deterministic":
        errors.append(f"{label}: a deterministic case is checked deterministically")
    if mode == "semantic" and relation == "deterministic":
        errors.append(f"{label}: a semantic case needs a separate or same-reader evaluator")
    if mode == "semantic" and entry["required"] is True and relation != "separate":
        errors.append(f"{label}: a required semantic case must be graded by a separate evaluator")
    return errors


def validate_case_directory(root: Path, entry: dict[str, Any], label: str) -> tuple[list[str], list[str]]:
    """Check `cases/<id>/`; return (errors, run-relative files to freeze)."""
    case_id = entry["case_id"]
    case_dir = contained(root, f"cases/{case_id}", label)
    case_path = case_dir / CASE_FILE
    if not case_path.is_file():
        return [f"{label}: cases/{case_id}/{CASE_FILE} is missing"], []
    errors: list[str] = []
    for child in sorted(case_dir.iterdir()):
        if child.name not in {CASE_FILE, FIXTURE_DIR}:
            errors.append(f"{label}: unexpected cases/{case_id}/{child.name} before execution")
    try:
        case = read_json(case_path)
    except CandidateQualificationError as exc:
        return [f"{label}: {exc}"], []
    keys = set(case)
    if keys != CASE_KEYS:
        errors.append(f"{label}: case.json must have exactly {sorted(CASE_KEYS)}")
        return errors, []
    if case["schema_version"] != SCHEMA_VERSION or case["case_id"] != case_id:
        errors.append(f"{label}: case.json names a different case or schema")
    for key in CASE_METADATA:
        if case[key] != entry[key]:
            errors.append(f"{label}: case.json {key} disagrees with the plan")
    if not _nonempty_str(case["task"]):
        errors.append(f"{label}: task must be the identical instruction both arms receive")
    for key, required in (("success_contract", True), ("constraints", False)):
        value = case[key]
        if not isinstance(value, list) or any(not _nonempty_str(item) for item in value):
            errors.append(f"{label}: {key} must be a list of non-empty strings")
        elif required and not value:
            errors.append(f"{label}: success_contract needs at least one observable criterion")
        elif len(value) != len(set(value)):
            errors.append(f"{label}: {key} may not repeat an item")
    if not isinstance(case["notes"], str):
        errors.append(f"{label}: notes must be a string")

    files = [f"cases/{case_id}/{CASE_FILE}"]
    fixtures = case["fixture_manifest"]
    listed: set[str] = set()
    if not isinstance(fixtures, list):
        errors.append(f"{label}: fixture_manifest must be a list")
        fixtures = []
    for index, item in enumerate(fixtures):
        where = f"{label} fixture {index}"
        if not isinstance(item, dict) or set(item) != FIXTURE_ENTRY_KEYS:
            errors.append(f"{where} must have exactly path and sha256")
            continue
        try:
            relative = safe_relative(item["path"], where)
            if relative.parts[0] != FIXTURE_DIR or len(relative.parts) < 2:
                raise CandidateQualificationError(f"{where} must sit under {FIXTURE_DIR}/")
            path = contained(case_dir, item["path"], where)
        except CandidateQualificationError as exc:
            errors.append(str(exc))
            continue
        if item["path"] in listed:
            errors.append(f"{where} repeats {item['path']}")
        listed.add(item["path"])
        if not path.is_file():
            errors.append(f"{where}: {item['path']} does not exist")
        elif digest_file(path) != item["sha256"]:
            errors.append(f"{where}: {item['path']} does not match its sha256")
        else:
            files.append(f"cases/{case_id}/{item['path']}")
    fixture_root = case_dir / FIXTURE_DIR
    if fixture_root.exists():
        for path in sorted(fixture_root.rglob("*")):
            if path.is_symlink():
                errors.append(f"{label}: fixture symlinks are not allowed: {path.name}")
            elif path.is_file():
                relative = path.relative_to(case_dir).as_posix()
                if relative not in listed:
                    errors.append(f"{label}: {relative} is not in fixture_manifest")
    return errors, files


def validate_plan(
    plan: Any, *, run: dict[str, Any], root: Path, admissible: set[str]
) -> tuple[list[str], list[str]]:
    """Every reason the plan cannot be frozen, and the files a freeze covers."""
    if not isinstance(plan, dict) or set(plan) != PLAN_KEYS:
        return [f"qualification plan must have exactly {sorted(PLAN_KEYS)}"], []
    errors: list[str] = []
    if plan["schema_version"] != SCHEMA_VERSION or plan["run_id"] != run["run_id"]:
        errors.append("qualification plan belongs to a different run or schema")
    cases = plan["cases"]
    if not isinstance(cases, list) or not cases:
        return errors + ["qualification plan must list at least one case"], []
    files = [run["files"]["qualification_plan"]]
    seen: set[str] = set()
    valid_entries = []
    for index, entry in enumerate(cases):
        case_id = entry.get("case_id") if isinstance(entry, dict) else None
        label = f"case {case_id}" if isinstance(case_id, str) else f"cases[{index}]"
        if not isinstance(case_id, str) or not CASE_ID_RE.fullmatch(case_id):
            errors.append(f"{label}: case_id must look like TARGET_001")
            continue
        if case_id in seen:
            errors.append(f"{label}: case_id repeats")
            continue
        seen.add(case_id)
        problems = validate_plan_entry(entry, label, admissible)
        errors.extend(problems)
        if problems:
            continue
        valid_entries.append(entry)
        directory_errors, case_files = validate_case_directory(root, entry, label)
        errors.extend(directory_errors)
        files.extend(case_files)
    cases_root = root / "cases"
    if cases_root.is_dir():
        for child in sorted(cases_root.iterdir()):
            if child.name not in seen:
                errors.append(f"cases/{child.name} is not a planned case")

    required = [entry for entry in valid_entries if entry["required"]]
    if not any(entry["role"] == "target" for entry in required):
        errors.append("the plan needs at least one required target case")
    if not any(
        entry["role"] == "target" and entry["origin"] != "synthetic"
        and entry["positive_qualification_eligible"] for entry in required
    ):
        errors.append("the plan needs a required non-synthetic target case eligible for positive qualification")
    protected = any(entry["role"] == "protected" and entry["origin"] != "synthetic" for entry in required)
    gap = plan["protected_case_gap"]
    if protected and gap is not None:
        errors.append("protected_case_gap must be null when a required non-synthetic protected case exists")
    if not protected and not _nonempty_str(gap):
        errors.append(
            "no required non-synthetic protected case: record protected_case_gap; the run "
            "then cannot qualify beyond inconclusive-protection-gap"
        )
    return errors, files


def load_frozen_json(root: Path, run: dict[str, Any], name: str, key: str) -> dict[str, Any]:
    if name not in run["freezes"]:
        raise CandidateQualificationError(f"{name} is not frozen in this run")
    return read_json(contained(root, run["files"][key], name))


def plan_cases(root: Path, plan: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        entry["case_id"]: read_json(contained(root, f"cases/{entry['case_id']}/{CASE_FILE}", "case"))
        for entry in plan["cases"]
    }


def freeze_plan(run_dir: Path) -> dict[str, Any]:
    """Validate the qualification plan and every case, then freeze them."""

    def update(root: Path, run: dict[str, Any]) -> None:
        path = contained(root, run["files"]["qualification_plan"], "qualification plan")
        if not path.is_file():
            raise CandidateQualificationError("controller/qualification_plan.json is missing")
        errors, files = validate_plan(
            read_json(path), run=run, root=root,
            admissible=admissible_event_ids(Path(run["memory_root"]), run["domain"]),
        )
        if errors:
            raise CandidateQualificationError("plan cannot be frozen: " + "; ".join(errors))
        record_freeze(root, run, "plan", files)

    return apply_transition(run_dir, "freeze-plan", update)


# -------------------------------------------------------- candidate staging


CANDIDATE_CARDS = "candidate/cards"
MANIFEST_CHANGE_KEYS = frozenset({"action", "object_id", "relative_path", "rationale"})
FROZEN_CHANGE_KEYS = MANIFEST_CHANGE_KEYS | {
    "baseline_sha256", "candidate_sha256", "changed_sections", "accounting",
}
MANIFEST_KEYS = frozenset({"schema_version", "run_id", "changes", "unmatched_actions", "scope"})
SCOPE_KEYS = ("changed_existing_cards", "new_cards", "deleted_cards", "renamed_object_ids", "moved_existing_cards")


def action_paths(assessment: dict[str, Any], baseline: dict[str, dict[str, Any]]) -> list[dict[str, str]]:
    """Each frozen object action with the library-relative path it edits."""
    return [
        {
            "action": action["action"],
            "object_id": action["object_id"],
            "object_type": action["object_type"],
            "relative_path": (
                baseline[action["object_id"]]["relative_path"]
                if action["action"] == "revise" else action["relative_path"]
            ),
        }
        for action in assessment["proposed_object_actions"]
    ]


def stage_candidate(run_dir: Path) -> dict[str, Any]:
    """Copy the revisable cards out of the baseline for editing.

    Refused unless the frozen assessment is a canon-candidate. A new-card action
    gets only its empty destination folder; Python never writes card content.
    """

    def update(root: Path, run: dict[str, Any]) -> None:
        assessment = load_frozen_json(root, run, "assessment", "assessment")
        disposition = assessment["candidate_disposition"]
        if disposition != "canon-candidate":
            raise CandidateQualificationError(
                f"the frozen assessment routes this candidate to {disposition}; only a "
                "canon-candidate is staged for authoring. Close the run with abandon and "
                "handle the finding where it belongs"
            )
        candidate_root = root / "candidate"
        if candidate_root.exists():
            raise CandidateQualificationError(
                "candidate/ already exists before staging; remove the leftover folder first"
            )
        manifest = load_baseline_manifest(root, run)
        baseline = baseline_objects(root, manifest)
        actions = action_paths(assessment, baseline)
        cards = contained(root, CANDIDATE_CARDS, "candidate cards")
        cards.mkdir(parents=True)
        changes = []
        for action in actions:
            destination = contained(cards, action["relative_path"], "candidate path")
            destination.parent.mkdir(parents=True, exist_ok=True)
            if action["action"] == "revise":
                shutil.copyfile(
                    contained(root, f"baseline/cards/{action['relative_path']}", "snapshot"), destination
                )
            changes.append({key: action[key] for key in ("action", "object_id", "relative_path")} | {"rationale": ""})
        write_json_atomic(contained(root, run["files"]["candidate_manifest"], "candidate manifest"), {
            "schema_version": SCHEMA_VERSION,
            "run_id": run["run_id"],
            "changes": changes,
            "unmatched_actions": [],
            "scope": {key: 0 for key in SCOPE_KEYS},
        })
        plan = load_frozen_json(root, run, "plan", "qualification_plan")
        write_text_atomic(root / "README.md", candidate_brief(
            run, load_intake(root, run), assessment, plan, plan_cases(root, plan), actions,
        ))

    return apply_transition(run_dir, "stage-candidate", update)


def candidate_brief(
    run: dict[str, Any],
    intake: dict[str, Any],
    assessment: dict[str, Any],
    plan: dict[str, Any],
    cases: dict[str, dict[str, Any]],
    actions: list[dict[str, str]],
) -> str:
    """The candidate-author brief. Held-out case details are never written here."""
    entry = intake["memory_entry"]
    diagnosis = entry.get("diagnosis") or {}
    limits = run["scope_limits"]
    visible = [e for e in plan["cases"] if e["role"] == "target" and e["visibility"] == "author-visible"]
    held_out = [e for e in plan["cases"] if e["visibility"] == "held-out"]
    lines = [
        f"# CRQ run {run['run_id']}: author the candidate",
        "",
        "Edit only the files under `candidate/cards/`. Never edit `library/`; a",
        "qualified candidate still needs deliberate synthesis review.",
        "",
        "## Why this candidate exists",
        "",
        f"- Memory candidate {entry.get('id')}: {' '.join(str(entry.get('observation', '')).split())}",
        f"- Diagnosis: {diagnosis.get('failure_layer', 'not recorded')}"
        + (f" ({' '.join(str(diagnosis['hypothesis']).split())})" if diagnosis.get("hypothesis") else ""),
        f"- Likely owners: {', '.join(o['label'] for o in intake['owners'])}",
        "",
        "## Frozen assessment",
        "",
        f"- Disposition: {assessment['candidate_disposition']}; failure layer: "
        f"{assessment['failure_layer']}; attribution: {assessment['primary_attribution']}",
        f"- Owners: {', '.join(assessment['owner_object_ids']) or 'none (new card)'}",
        f"- Rationale: {' '.join(assessment['rationale'].split())}",
        "",
        "## Allowed actions",
        "",
    ]
    for action in actions:
        if action["action"] == "revise":
            lines.append(
                f"- revise {action['object_type']} `{action['object_id']}` at "
                f"`candidate/cards/{action['relative_path']}` (copied from the frozen baseline)"
            )
        else:
            lines.append(
                f"- create {action['object_type']} `{action['object_id']}` as "
                f"`candidate/cards/{action['relative_path']}` (its folder exists; write the card)"
            )
    lines += [
        "",
        f"Ceilings: {limits['max_changed_cards']} revised, {limits['max_new_cards']} new. Nothing",
        "else may appear under `candidate/cards/`: no deleted, renamed, moved or extra files.",
        "",
        "## Card rules",
        "",
        "- Each card must stay an ordinary, valid, source-independent PASS card; the ordinary",
        "  validators run on a temporary overlay at `freeze-candidate`.",
        "- A card never names this run, a memory entry, a training event, a qualification",
        "  case, a workspace path or an evidence hash. The evidence justifies the edit; it",
        "  is not a runtime dependency of the card.",
        "- Fill each `rationale` in `controller/candidate_manifest.json`; the controller",
        "  computes hashes, changed sections and scope when it freezes the candidate.",
        "",
        "## Author-visible target cases",
        "",
    ]
    for entry_ in visible:
        case = cases[entry_["case_id"]]
        lines += [f"### {entry_['case_id']}", "", f"Task: {' '.join(case['task'].split())}", "", "Success contract:", ""]
        lines += [f"- {item}" for item in case["success_contract"]]
        if case["constraints"]:
            lines += ["", "Constraints:", ""] + [f"- {item}" for item in case["constraints"]]
        lines.append("")
    if not visible:
        lines += ["None.", ""]
    lines += [
        "## Withheld cases",
        "",
        f"{len(held_out)} held-out case(s) are intentionally withheld until the candidate is",
        "frozen. Do not open `cases/` for them; reading one early is contamination and",
        "invalidates the qualification it touches.",
        "",
    ]
    return "\n".join(lines)


# ------------------------------------------------------- candidate freezing


# An identifier shaped like a run, memory entry or history event never belongs in a card.
EVIDENCE_ID_RE = re.compile(r"\b[A-Z][A-Z0-9]*_(?:CRQ|MEM|EV)_[0-9]+\b")
CARD_HEADING_RE = re.compile(r"(?m)^## ([^\r\n]+?)\s*$")
CARD_TITLE_RE = re.compile(r"(?m)^# ([^\r\n]+?)\s*$")


def card_parts(raw: bytes) -> tuple[dict[str, Any] | None, str | None, dict[str, str]]:
    """Frontmatter, H1 and `##` sections of a card's bytes."""
    text = card_text(raw)
    match = re.match(r"\A---\n(?P<front>.*?)\n---\n(?P<body>.*)\Z", text, re.DOTALL)
    if not match:
        return None, None, {}
    try:
        front = yaml.safe_load(match.group("front"))
    except yaml.YAMLError:
        front = None
    body = match.group("body")
    title = CARD_TITLE_RE.search(body)
    headings = list(CARD_HEADING_RE.finditer(body))
    sections = {}
    for index, heading in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(body)
        sections[heading.group(1)] = " ".join(body[heading.end():end].split())
    return front if isinstance(front, dict) else None, title.group(1) if title else None, sections


def changed_sections(before: bytes | None, after: bytes) -> list[str]:
    """Which parts of a card changed: Frontmatter, Title, and each `##` section."""
    new_front, new_title, new_sections = card_parts(after)
    if before is None:
        return ["Frontmatter", "Title", *new_sections]
    old_front, old_title, old_sections = card_parts(before)
    changed = []
    if old_front != new_front:
        changed.append("Frontmatter")
    if old_title != new_title:
        changed.append("Title")
    for heading in [*new_sections, *(h for h in old_sections if h not in new_sections)]:
        if old_sections.get(heading) != new_sections.get(heading):
            changed.append(heading)
    return changed


def candidate_file_list(cards: Path) -> tuple[list[str], list[str]]:
    """(files, problems) under `candidate/cards/`, refusing symlinks."""
    files, problems = [], []
    if not cards.is_dir():
        return files, ["candidate/cards/ is missing"]
    for path in sorted(cards.rglob("*")):
        relative = path.relative_to(cards).as_posix()
        if path.is_symlink():
            problems.append(f"{relative}: symlinks are not allowed in a candidate")
        elif path.is_file():
            files.append(relative)
    return files, problems


def account_candidate(
    root: Path,
    actions: list[dict[str, str]],
    baseline_ids: set[str],
) -> tuple[list[dict[str, Any]], list[dict[str, str]], dict[str, int]]:
    """Match every authorized action to a real change and every file to an action.

    Returns (applied changes, unmatched actions, scope counts). Anything
    unmatched blocks the freeze; nothing is silently dropped.
    """
    cards = contained(root, CANDIDATE_CARDS, "candidate cards")
    files, problems = candidate_file_list(cards)
    unmatched = [{"object_id": None, "relative_path": None, "problem": text} for text in problems]
    scope = {key: 0 for key in SCOPE_KEYS}
    applied = []
    expected = {action["relative_path"] for action in actions}

    def miss(action: dict[str, str], text: str) -> None:
        unmatched.append({
            "object_id": action["object_id"], "relative_path": action["relative_path"], "problem": text,
        })

    for action in actions:
        relative = action["relative_path"]
        path = contained(cards, relative, "candidate path")
        before = (
            contained(root, f"baseline/cards/{relative}", "snapshot").read_bytes()
            if action["action"] == "revise" else None
        )
        if not path.is_file():
            if action["action"] == "revise":
                scope["deleted_cards"] += 1
                miss(action, "the revised card is missing; deleting a card is never allowed")
            else:
                miss(action, "the new-card action created no card")
            continue
        after = path.read_bytes()
        front, _title, _sections = card_parts(after)
        if front is None:
            miss(action, "the file is not a card with readable frontmatter")
            continue
        if front.get("object_id") != action["object_id"]:
            if action["action"] == "revise":
                scope["renamed_object_ids"] += 1
            miss(action, f"object_id is {front.get('object_id')!r}; renaming is never allowed")
            continue
        if front.get("object_type") != action["object_type"]:
            miss(action, f"object_type is {front.get('object_type')!r}, not {action['object_type']}")
            continue
        if before is not None and after == before:
            miss(action, "the staged card is byte-identical to the baseline")
            continue
        sections = changed_sections(before, after)
        if not sections:
            miss(action, "only whitespace or line endings changed")
            continue
        scope["changed_existing_cards" if action["action"] == "revise" else "new_cards"] += 1
        applied.append({
            "action": action["action"],
            "object_id": action["object_id"],
            "relative_path": relative,
            "baseline_sha256": digest_bytes(before) if before is not None else None,
            "candidate_sha256": digest_bytes(after),
            "changed_sections": sections,
            "accounting": "applied-to-candidate",
        })
    for relative in files:
        if relative in expected:
            continue
        front, _title, _sections = card_parts(contained(cards, relative, "candidate file").read_bytes())
        object_id = front.get("object_id") if front else None
        if object_id in baseline_ids:
            scope["moved_existing_cards"] += 1
            text = f"a copy of existing card {object_id} at an unauthorized path; moving or changing an unauthorized card is never allowed"
        else:
            text = "this file was never authorized by the frozen assessment"
        unmatched.append({"object_id": object_id, "relative_path": relative, "problem": text})
    return applied, unmatched, scope


def evidence_references(
    root: Path, files: Iterable[str], forbidden: Iterable[str]
) -> list[str]:
    """Candidate files that name the run's evidence instead of standing alone."""
    tokens = sorted({token for token in forbidden if token})
    patterns = [re.compile(r"(?<![A-Za-z0-9_])" + re.escape(token) + r"(?![A-Za-z0-9_])") for token in tokens]
    problems = []
    for relative in files:
        text = card_text(contained(root, f"{CANDIDATE_CARDS}/{relative}", "candidate file").read_bytes())
        found = set(EVIDENCE_ID_RE.findall(text))
        found |= {token for token, pattern in zip(tokens, patterns) if pattern.search(text)}
        if PurePosixPath(WORKSPACE_BUCKET).name in text:
            found.add("a candidate-qualification workspace path")
        if found:
            problems.append(f"{relative} names run evidence ({', '.join(sorted(found))}); a card must stand alone")
    return problems


def run_tool_cli(name: str, argv: list[str]) -> tuple[int, str]:
    """Run a PASS tool's own `main()` in-process with `argv`; return (code, output)."""
    module = load_pass_tool(name)
    output = io.StringIO()
    saved = sys.argv
    sys.argv = [f"{name}.py", *argv]
    try:
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            try:
                code = module.main()
            except SystemExit as exc:
                code = exc.code if isinstance(exc.code, int) else 1
    finally:
        sys.argv = saved
    return int(code or 0), output.getvalue()


OVERLAY_PREFIX = "pass-crq-overlay-"
OVERLAY_VALIDATORS = ("validate", "verify_references")


def overlay_problems(library_root: Path, cards: Path, files: Iterable[str]) -> list[str]:
    """Validate the live library with the candidate files laid over it.

    The overlay is a temporary copy named `library/` (the reference checker
    finds its repo root by that name). It is removed on success and failure,
    and the canonical library is only ever read.
    """
    problems = []
    with tempfile.TemporaryDirectory(prefix=OVERLAY_PREFIX) as temporary:
        overlay = Path(temporary) / "library"
        shutil.copytree(library_root, overlay, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
        for relative in files:
            destination = overlay.joinpath(*PurePosixPath(relative).parts)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(contained(cards, relative, "candidate file"), destination)
        for tool in OVERLAY_VALIDATORS:
            code, output = run_tool_cli(tool, ["--library", str(overlay)])
            if code:
                shown = "\n".join(output.strip().splitlines()[-40:]).replace(str(overlay), "<overlay>")
                problems.append(f"{tool}.py --library <overlay> failed:\n{shown}")
    return problems


def validate_manifest_template(
    template: Any, run: dict[str, Any], actions: list[dict[str, str]]
) -> tuple[list[str], dict[str, str]]:
    """Check the author's manifest; return (errors, rationale by object id)."""
    if not isinstance(template, dict) or set(template) != MANIFEST_KEYS:
        return [f"candidate manifest must have exactly {sorted(MANIFEST_KEYS)}"], {}
    if template["schema_version"] != SCHEMA_VERSION or template["run_id"] != run["run_id"]:
        return ["candidate manifest belongs to a different run or schema"], {}
    changes = template["changes"]
    if not isinstance(changes, list) or any(not isinstance(c, dict) or set(c) != MANIFEST_CHANGE_KEYS for c in changes):
        return [f"each candidate manifest change must have exactly {sorted(MANIFEST_CHANGE_KEYS)}"], {}
    expected = sorted((a["action"], a["object_id"], a["relative_path"]) for a in actions)
    found = sorted((c["action"], c["object_id"], c["relative_path"]) for c in changes)
    if found != expected:
        return ["candidate manifest changes must be exactly the frozen assessment's actions"], {}
    errors = [
        f"{change['object_id']}: rationale must explain the change"
        for change in changes if not _nonempty_str(change["rationale"])
    ]
    return errors, {change["object_id"]: change["rationale"].strip() for change in changes}


def freeze_candidate(run_dir: Path) -> dict[str, Any]:
    """Account for every candidate change, validate the overlay, and freeze."""

    def update(root: Path, run: dict[str, Any]) -> None:
        assessment = load_frozen_json(root, run, "assessment", "assessment")
        manifest = load_baseline_manifest(root, run)
        baseline = baseline_objects(root, manifest)
        actions = action_paths(assessment, baseline)
        manifest_path = contained(root, run["files"]["candidate_manifest"], "candidate manifest")
        if not manifest_path.is_file():
            raise CandidateQualificationError("controller/candidate_manifest.json is missing")
        errors, rationale = validate_manifest_template(read_json(manifest_path), run, actions)
        library = Path(run["library_root"])
        for action in actions:
            if action["action"] == "create" and (library / Path(*PurePosixPath(action["relative_path"]).parts)).exists():
                errors.append(f"{action['relative_path']} now exists in the library; start a fresh run")
        applied, unmatched, scope = account_candidate(root, actions, set(baseline))
        errors += [f"unmatched {item['relative_path'] or '-'}: {item['problem']}" for item in unmatched]
        limits = run["scope_limits"]
        if scope["changed_existing_cards"] > limits["max_changed_cards"]:
            errors.append(f"{scope['changed_existing_cards']} changed cards exceed max_changed_cards")
        if scope["new_cards"] > limits["max_new_cards"]:
            errors.append(f"{scope['new_cards']} new cards exceed max_new_cards")
        files = [change["relative_path"] for change in applied]
        intake = load_intake(root, run)
        plan = load_frozen_json(root, run, "plan", "qualification_plan")
        errors += evidence_references(root, files, [
            run["run_id"], run["memory_entry_id"],
            *(str(event.get("event_id")) for event in intake["events"]),
            *(entry["case_id"] for entry in plan["cases"]),
        ])
        if errors:
            raise CandidateQualificationError("candidate cannot be frozen: " + "; ".join(errors))
        problems = overlay_problems(library, contained(root, CANDIDATE_CARDS, "candidate cards"), files)
        if problems:
            raise CandidateQualificationError(
                "candidate overlay fails ordinary PASS validation:\n" + "\n".join(problems)
            )
        for change in applied:
            change["rationale"] = rationale[change["object_id"]]
        write_json_atomic(manifest_path, {
            "schema_version": SCHEMA_VERSION,
            "run_id": run["run_id"],
            "changes": applied,
            "unmatched_actions": [],
            "scope": scope,
        })
        record_freeze(root, run, "candidate", [
            run["files"]["candidate_manifest"], *(f"{CANDIDATE_CARDS}/{path}" for path in files),
        ])

    return apply_transition(run_dir, "freeze-candidate", update)


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
        "closing_controller_sha256": run["closing_controller_sha256"],
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
    prepare_command = commands.add_parser(
        "prepare", help="start a run from one Skillset Memory card_candidate"
    )
    prepare_command.add_argument("--domain", required=True)
    prepare_command.add_argument("--memory-entry", required=True)
    prepare_command.add_argument(
        "--out", type=Path, default=None,
        help=f"run directory; default {WORKSPACE_BUCKET}/<domain>/<next run id>",
    )
    prepare_command.add_argument("--library", type=Path, default=None)
    prepare_command.add_argument("--memory-root", type=Path, default=None)
    prepare_command.add_argument("--max-changed-cards", type=int, default=None)
    prepare_command.add_argument("--max-new-cards", type=int, default=None)
    prepare_command.add_argument(
        "--override-reason", default=None,
        help="required when a ceiling is raised above its default",
    )
    freeze = commands.add_parser(
        "freeze-assessment", help="validate and freeze controller/assessment.json"
    )
    freeze.add_argument("--run", type=Path, required=True)
    for name, text in (
        ("freeze-plan", "validate and freeze the qualification plan and its cases"),
        ("stage-candidate", "copy the revisable cards into candidate/cards/ for authoring"),
        ("freeze-candidate", "account for the candidate, validate its overlay, and freeze it"),
    ):
        command = commands.add_parser(name, help=text)
        command.add_argument("--run", type=Path, required=True)
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
        if args.command == "prepare":
            out, run = prepare(
                domain=args.domain,
                memory_entry_id=args.memory_entry,
                out=args.out,
                library_root=args.library,
                memory_root=args.memory_root,
                max_changed_cards=args.max_changed_cards,
                max_new_cards=args.max_new_cards,
                override_reason=args.override_reason,
            )
            entries = load_baseline_manifest(out, run)["entries"]
            roles = {role: sum(1 for e in entries if e["role"] == role) for role in sorted(BASELINE_ROLES)}
            print(
                f"PREPARED: {run['run_id']} at {out}; baseline "
                + ", ".join(f"{count} {role}" for role, count in roles.items())
                + "; fill controller/assessment.json, then run freeze-assessment"
            )
        elif args.command == "freeze-assessment":
            run = freeze_assessment(args.run)
            print(f"ASSESSMENT FROZEN: {run['run_id']}")
        elif args.command == "freeze-plan":
            run = freeze_plan(args.run)
            print(f"PLAN FROZEN: {run['run_id']}")
        elif args.command == "stage-candidate":
            run = stage_candidate(args.run)
            print(f"CANDIDATE STAGED: {run['run_id']}; edit candidate/cards/ as README.md describes")
        elif args.command == "freeze-candidate":
            run = freeze_candidate(args.run)
            print(f"CANDIDATE FROZEN: {run['run_id']}")
        elif args.command == "status":
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
