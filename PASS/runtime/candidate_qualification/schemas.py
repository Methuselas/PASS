"""CRQ schemas: closed vocabularies, run-record and document validation.

Deterministic and dependency-free inside the package: errors, constants, hashes,
stable JSON writes, path containment, and the structural rules for run.json,
the baseline manifest, the intake, the defect assessment, the qualification
plan and cases, and the candidate manifest. It reads files it is pointed at and
never decides domain semantics.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any, Iterable


SCHEMA_VERSION = 1
# A newer controller may read an older run only when its schema is listed here.
# It never migrates or requalifies an older run.
READABLE_SCHEMA_VERSIONS = frozenset({SCHEMA_VERSION})
WORKSPACE_BUCKET = "workspace/candidate-qualification"
PACKAGE_DIR = Path(__file__).resolve().parent
RUNTIME_DIR = PACKAGE_DIR.parent
# The CLI entry point; its bytes are part of the controller fingerprint.
ENTRY_SCRIPT = RUNTIME_DIR / "pass_candidate_qualification.py"
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


# ------------------------------------------------------------ memory intake


CANDIDATE_TYPE = "card_candidate"
CANDIDATE_STATUSES = frozenset({"active", "monitoring"})
INTAKE_KEYS = frozenset({
    "schema_version", "run_id", "domain", "memory_entry", "events",
    "memory_store", "owners",
})
OWNER_RESOLUTIONS = frozenset({"target", "metaskills", "label"})


# ------------------------------------------------------------ library cards


SHARED_PACKAGE = "metaskills"
MODULE_MANIFEST = "MODULE.yaml"
OBJECT_TYPES = frozenset({"pattern", "ap", "drill"})
OBJECT_PREFIXES = {"pattern": "PAT_", "ap": "AP_", "drill": "DRILL_"}
OBJECT_ID_RE = re.compile(r"(?:PAT|DRILL|AP)_[a-z0-9][a-z0-9_]*\Z")


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


# -------------------------------------------------------- candidate staging


CANDIDATE_CARDS = "candidate/cards"
MANIFEST_CHANGE_KEYS = frozenset({"action", "object_id", "relative_path", "rationale"})
FROZEN_CHANGE_KEYS = MANIFEST_CHANGE_KEYS | {
    "baseline_sha256", "candidate_sha256", "changed_sections", "accounting",
}
MANIFEST_KEYS = frozenset({"schema_version", "run_id", "changes", "unmatched_actions", "scope"})
SCOPE_KEYS = ("changed_existing_cards", "new_cards", "deleted_cards", "renamed_object_ids", "moved_existing_cards")


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


# ------------------------------------------------------------ arm results


VERDICTS = ("pass", "fail", "invalid")
CRITERION_RESULTS = ("pass", "fail", "not-assessed")
EXECUTOR_KINDS = ("ai", "human", "tool")
EXECUTOR_KEYS = frozenset({"kind", "runtime", "model"})
CONTAMINATION_STATES = ("none", "suspected", "confirmed")
RESULT_KEYS = frozenset({
    "schema_version", "case_id", "arm", "case_sha256", "verdict", "evaluation_mode",
    "evaluator_relation", "executor", "environment", "criteria", "evidence_manifest",
    "contamination", "invalid_reason", "notes",
})
CRITERION_KEYS = frozenset({"criterion", "result", "evidence"})
EVIDENCE_ENTRY_KEYS = frozenset({"path", "sha256", "kind"})
RESULT_FILE = "result.json"
EVIDENCE_DIR = "evidence"
ARM_BUNDLES = "arms"
QUALIFICATION_RESULT_KEYS = frozenset({
    "schema_version", "run_id", "status", "reason", "candidate_memory_entry",
    "changed_objects", "change_accounting", "case_deltas", "blocking_cases",
    "positive_qualification_cases", "synthetic_cases", "protected_case_gap",
    "contamination_confirmed", "canon_modified",
})


def result_template(case: dict[str, Any], arm: str, case_sha256: str) -> dict[str, Any]:
    """Blank arm result; the arm's executor and evaluator fill it."""
    return {
        "schema_version": SCHEMA_VERSION,
        "case_id": case["case_id"],
        "arm": arm,
        "case_sha256": case_sha256,
        "verdict": None,
        "evaluation_mode": case["evaluation_mode"],
        "evaluator_relation": case["evaluator_relation"],
        "executor": {"kind": None, "runtime": None, "model": None},
        "environment": {},
        "criteria": [
            {"criterion": criterion, "result": None, "evidence": ""}
            for criterion in case["success_contract"]
        ],
        "evidence_manifest": [],
        "contamination": "none",
        "invalid_reason": None,
        "notes": "",
    }


# ---------------------------------------------------------------- synthesis


SYNTHESIS_DIR = "synthesis"
SYNTHESIS_LEVELS = "synthesis/levels"
SYNTHESIS_INPUT = "synthesis/input.json"
DISPOSITION_FILE = "synthesis/disposition.json"
REPORT_FILE = "synthesis/report.md"
PACKET_FILE = "input.json"
SUMMARY_FILE = "summary.json"
LEAF_BATCH_SIZE = 6
FAN_IN = 4
SUMMARY_KEYS = frozenset({
    "schema_version", "claims", "persistent_failures", "stable_successes",
    "boundary_notes", "unresolved_conflicts",
})
SUMMARY_CLAIM_KEYS = frozenset({"claim", "supporting_event_ids", "contradicting_event_ids"})
SUMMARY_NOTE_KEYS = frozenset({"note", "event_ids"})
SUMMARY_NOTE_LISTS = ("persistent_failures", "stable_successes", "boundary_notes", "unresolved_conflicts")
# Section 40: what deliberate synthesis review may decide.
SYNTHESIS_DECISIONS = (
    "accept-canonical-delta", "revise-in-fresh-run", "split-candidate",
    "redirect-ownership", "retain-in-memory", "add-deterministic-regression",
    "reject-redundant", "reject-false", "reject-too-narrow",
)
# Section 28.2: the memory update a human or model later applies through memory.py.
MEMORY_ACTIONS = (
    "keep-active", "keep-monitoring", "narrow-boundary", "supersede-candidate",
    "resolve-after-canon-fix", "obsolete", "no-change",
)
DISPOSITION_KEYS = frozenset({
    "schema_version", "run_id", "memory_entry_id", "qualification_status",
    "synthesis_decision", "memory_action", "reason", "reviewer_notes",
})


def summary_event_ids(summary: dict[str, Any], *, contradictions_only: bool = False) -> set[str]:
    """Event ids a valid summary cites; optionally only its contradictions."""
    ids: set[str] = set()
    for claim in summary["claims"]:
        ids.update(claim["contradicting_event_ids"])
        if not contradictions_only:
            ids.update(claim["supporting_event_ids"])
    for key in SUMMARY_NOTE_LISTS:
        if contradictions_only and key != "unresolved_conflicts":
            continue
        for note in summary[key]:
            ids.update(note["event_ids"])
    return ids


def validate_summary(
    summary: Any, known: set[str], children: Iterable[dict[str, Any]] = ()
) -> list[str]:
    """Structure and traceability of one synthesis summary.

    Every cited id must be an event under the batch; a claim needs support; and a
    parent must keep every contradiction its children recorded, as a
    contradiction or an unresolved conflict. Whether the prose is faithful is
    the reviewer's judgment, not this check's.
    """
    if not isinstance(summary, dict) or set(summary) != SUMMARY_KEYS:
        return [f"summary must have exactly {sorted(SUMMARY_KEYS)}"]
    errors: list[str] = []
    if summary["schema_version"] != SCHEMA_VERSION:
        errors.append("summary schema_version mismatch")

    def check_ids(value: Any, where: str, *, nonempty: bool) -> None:
        if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
            errors.append(f"{where} must be a list of event ids")
            return
        if nonempty and not value:
            errors.append(f"{where} must cite at least one event")
        for event_id in value:
            if event_id not in known:
                errors.append(f"{where} cites {event_id}, which is not an event under this batch")

    claims = summary["claims"]
    if not isinstance(claims, list):
        errors.append("claims must be a list")
        claims = []
    for index, claim in enumerate(claims):
        if not isinstance(claim, dict) or set(claim) != SUMMARY_CLAIM_KEYS or not _nonempty_str(claim.get("claim")):
            errors.append(f"claims[{index}] needs claim, supporting_event_ids and contradicting_event_ids")
            continue
        check_ids(claim["supporting_event_ids"], f"claims[{index}].supporting_event_ids", nonempty=True)
        check_ids(claim["contradicting_event_ids"], f"claims[{index}].contradicting_event_ids", nonempty=False)
    for key in SUMMARY_NOTE_LISTS:
        notes = summary[key]
        if not isinstance(notes, list):
            errors.append(f"{key} must be a list")
            continue
        for index, note in enumerate(notes):
            if not isinstance(note, dict) or set(note) != SUMMARY_NOTE_KEYS or not _nonempty_str(note.get("note")):
                errors.append(f"{key}[{index}] needs note and event_ids")
                continue
            check_ids(note["event_ids"], f"{key}[{index}].event_ids", nonempty=True)
    if errors:
        return errors
    kept = summary_event_ids(summary, contradictions_only=True)
    for child in children:
        lost = sorted(summary_event_ids(child, contradictions_only=True) - kept)
        if lost:
            errors.append(
                "a parent summary may not erase a contradiction; keep "
                + ", ".join(lost) + " as a contradicting event or an unresolved conflict"
            )
    return errors


def disposition_template(run: dict[str, Any], status: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": run["run_id"],
        "memory_entry_id": run["memory_entry_id"],
        "qualification_status": status,
        "synthesis_decision": None,
        "memory_action": None,
        "reason": "",
        "reviewer_notes": "",
    }


def validate_disposition(disposition: Any, *, run: dict[str, Any], status: str) -> list[str]:
    """The synthesis review's decision; only a qualified candidate may be accepted."""
    if not isinstance(disposition, dict) or set(disposition) != DISPOSITION_KEYS:
        return [f"disposition must have exactly {sorted(DISPOSITION_KEYS)}"]
    errors: list[str] = []
    if (
        disposition["schema_version"] != SCHEMA_VERSION or disposition["run_id"] != run["run_id"]
        or disposition["memory_entry_id"] != run["memory_entry_id"]
    ):
        errors.append("disposition belongs to a different run, memory entry or schema")
    if disposition["qualification_status"] != status:
        errors.append(f"disposition must restate the frozen qualification status {status}")
    decision = disposition["synthesis_decision"]
    if decision not in SYNTHESIS_DECISIONS:
        errors.append(f"synthesis_decision must be one of {list(SYNTHESIS_DECISIONS)}")
    elif decision == "accept-canonical-delta" and status != "qualified-for-synthesis-review":
        errors.append(f"a {status} candidate cannot be accepted as a canonical delta")
    action = disposition["memory_action"]
    if action not in MEMORY_ACTIONS:
        errors.append(f"memory_action must be one of {list(MEMORY_ACTIONS)}")
    elif action == "resolve-after-canon-fix" and decision not in {
        "accept-canonical-delta", "add-deterministic-regression",
    }:
        errors.append("resolve-after-canon-fix needs an accepted delta or a deterministic regression")
    if not _nonempty_str(disposition["reason"]):
        errors.append("reason must explain the decision")
    if not isinstance(disposition["reviewer_notes"], str):
        errors.append("reviewer_notes must be a string")
    return errors
