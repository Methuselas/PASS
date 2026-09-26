"""CRQ controller: run state, freezes, drift, and the lifecycle commands.

`controller/run.json` is the authoritative state of one run. Every mutating
command reopens it, verifies the schema, the controller fingerprint and every
frozen file, performs one atomic transition, and reads the result back.
"""

from __future__ import annotations

import copy
import hashlib
import os
import re
import shutil
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Iterable

from .schemas import (
    _is_int,
    ARM_BUNDLES,
    ARMS,
    assessment_template,
    BASELINE_ROLES,
    BaselineDriftError,
    CANDIDATE_CARDS,
    CANDIDATE_DISPOSITIONS,
    CandidateQualificationError,
    CASE_FILE,
    CASE_ORIGINS,
    CASE_ROLES,
    CLOSING_COMMANDS,
    contained,
    ControllerMismatchError,
    DEFAULT_SCOPE_LIMITS,
    digest_bytes,
    digest_file,
    DISPOSITION_FILE,
    disposition_template,
    DOMAIN_RE,
    ENTRY_SCRIPT,
    EVALUATION_MODES,
    EVALUATOR_RELATIONS,
    EVIDENCE_DIR,
    EXECUTION_STATES,
    FREEZE_NAME_RE,
    MEMORY_ACTIONS,
    NONCANON_DISPOSITIONS,
    now_utc,
    PACKAGE_DIR,
    PACKET_FILE,
    PLAN_CASE_KEYS,
    plan_template,
    PRIMARY_ATTRIBUTIONS,
    QUALIFICATION_RESULT_KEYS,
    read_json,
    READABLE_SCHEMA_VERSIONS,
    REPO_ROOT,
    REPORT_FILE,
    RESULT_FILE,
    result_template,
    RUN_FILES,
    RUN_ID_RE,
    RUNTIME_DIR,
    SCHEMA_VERSION,
    SCOPE_KEYS,
    SHARED_PACKAGE,
    SUMMARY_FILE,
    SYNTHESIS_DECISIONS,
    SYNTHESIS_INPUT,
    SYNTHESIS_LEVELS,
    TERMINAL_STATES,
    TRANSITIONS,
    validate_assessment,
    validate_baseline_manifest,
    validate_disposition,
    validate_intake,
    validate_manifest_template,
    validate_plan,
    validate_run_record,
    validate_summary,
    VISIBILITIES,
    WORKSPACE_BUCKET,
    write_json_atomic,
    write_text_atomic,
)
from .evidence import (
    account_candidate,
    admissible_event_ids,
    attention_items,
    baseline_objects,
    card_index,
    comparison_problems,
    evidence_references,
    exposed_card_ids,
    leaf_packets,
    load_pass_tool,
    module_manifest_for,
    overlay_problems,
    parent_packets,
    resolve_memory_candidate,
    resolve_owners,
    support_closure,
    validate_arm_result,
)
from .gate import case_delta, final_gate


def controller_files() -> list[tuple[str, Path]]:
    """Every file the controller fingerprint covers, as (relative path, path).

    That is every file of this package plus the CLI entry script, keyed by their
    path relative to the runtime folder and sorted.
    """
    if not ENTRY_SCRIPT.is_file():
        raise CandidateQualificationError(f"CRQ entry script is missing: {ENTRY_SCRIPT}")
    files = [
        (path.relative_to(RUNTIME_DIR).as_posix(), path)
        for path in PACKAGE_DIR.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
    ]
    files.append((ENTRY_SCRIPT.relative_to(RUNTIME_DIR).as_posix(), ENTRY_SCRIPT))
    return sorted(files)


def controller_sha256() -> str:
    """One SHA-256 over the controller package and its entry script.

    Each file's source is hashed with CRLF normalized to LF, so a checkout that
    converts line endings fingerprints the same controller identically; the
    combined hash covers every (relative path, file hash) pair in path order.
    Only the controller is normalized; card and evidence hashes stay byte-exact.
    """
    combined = hashlib.sha256()
    for relative, path in controller_files():
        content = path.read_bytes().replace(b"\r\n", b"\n")
        combined.update(f"{relative}\0{digest_bytes(content)}\n".encode("utf-8"))
    return combined.hexdigest()


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


def load_intake(root: Path, run: dict[str, Any]) -> dict[str, Any]:
    if "intake" not in run["freezes"]:
        raise CandidateQualificationError("this run has no frozen memory intake")
    intake = read_json(contained(root, run["files"]["intake"], "intake"))
    errors = validate_intake(intake, run)
    if errors:
        raise CandidateQualificationError("invalid intake: " + "; ".join(errors))
    return intake


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


# ---------------------------------------------------------------- execution


def frozen_case_hashes(root: Path, run: dict[str, Any]) -> dict[str, str]:
    """case id -> SHA-256 of its frozen case.json, from the plan freeze record."""
    record = read_json(contained(root, run["freezes"]["plan"]["path"], "plan freeze"))
    hashes = {}
    for item in record["files"]:
        parts = PurePosixPath(item["path"]).parts
        if len(parts) == 3 and parts[0] == "cases" and parts[2] == CASE_FILE:
            hashes[parts[1]] = item["sha256"]
    return hashes


def open_execution(run_dir: Path) -> dict[str, Any]:
    """Write one result template per case and arm, and freeze both arm bundles.

    `arms/baseline/cards/` is the frozen baseline; `arms/candidate/cards/` is the
    same bundle with the frozen candidate laid over it. Held-out cases are
    revealed to the execution phase only from here on.
    """

    def update(root: Path, run: dict[str, Any]) -> None:
        plan = load_frozen_json(root, run, "plan", "qualification_plan")
        cases = plan_cases(root, plan)
        hashes = frozen_case_hashes(root, run)
        arms_root = contained(root, ARM_BUNDLES, "arm bundles")
        if arms_root.exists():
            raise CandidateQualificationError(f"{ARM_BUNDLES}/ already exists before execution opened")
        for entry in plan["cases"]:
            for arm in ARMS:
                if contained(root, f"cases/{entry['case_id']}/{arm}", "arm folder").exists():
                    raise CandidateQualificationError(
                        f"cases/{entry['case_id']}/{arm} already exists before execution opened"
                    )
        baseline_cards = contained(root, "baseline/cards", "baseline snapshot")
        candidate_cards = contained(root, CANDIDATE_CARDS, "candidate cards")
        manifest = read_json(contained(root, run["files"]["candidate_manifest"], "candidate manifest"))
        bundle_files = []
        for arm in ARMS:
            destination = contained(root, f"{ARM_BUNDLES}/{arm}/cards", "arm bundle")
            shutil.copytree(baseline_cards, destination)
            if arm == "candidate":
                for change in manifest["changes"]:
                    target = contained(destination, change["relative_path"], "arm bundle card")
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(contained(candidate_cards, change["relative_path"], "candidate card"), target)
            bundle_files += [
                f"{ARM_BUNDLES}/{arm}/cards/{path.relative_to(destination).as_posix()}"
                for path in sorted(destination.rglob("*")) if path.is_file()
            ]
        for entry in plan["cases"]:
            case = dict(cases[entry["case_id"]])
            for arm in ARMS:
                arm_dir = contained(root, f"cases/{entry['case_id']}/{arm}", "arm folder")
                (arm_dir / EVIDENCE_DIR).mkdir(parents=True)
                write_json_atomic(arm_dir / RESULT_FILE, result_template(case, arm, hashes[entry["case_id"]]))
        record_freeze(root, run, "arms", bundle_files)
        write_text_atomic(root / "README.md", execution_brief(run, plan, cases))

    return apply_transition(run_dir, "open-execution", update)


def load_arm_results(
    root: Path, plan: dict[str, Any]
) -> dict[str, dict[str, dict[str, Any]]]:
    results: dict[str, dict[str, dict[str, Any]]] = {}
    for entry in plan["cases"]:
        for arm in ARMS:
            path = contained(root, f"cases/{entry['case_id']}/{arm}/{RESULT_FILE}", "arm result")
            if not path.is_file():
                raise CandidateQualificationError(f"cases/{entry['case_id']}/{arm}/{RESULT_FILE} is missing")
            results.setdefault(entry["case_id"], {})[arm] = read_json(path)
    return results


def freeze_execution(run_dir: Path) -> dict[str, Any]:
    """Validate every arm result and its evidence, then freeze them all."""

    def update(root: Path, run: dict[str, Any]) -> None:
        plan = load_frozen_json(root, run, "plan", "qualification_plan")
        cases = plan_cases(root, plan)
        results = load_arm_results(root, plan)
        errors: list[str] = []
        files: list[str] = []
        for entry in plan["cases"]:
            for arm in ARMS:
                prefix = f"cases/{entry['case_id']}/{arm}"
                problems, evidence = validate_arm_result(
                    results[entry["case_id"]][arm], entry=entry, case=cases[entry["case_id"]],
                    arm=arm, arm_dir=contained(root, prefix, "arm folder"),
                )
                errors += problems
                files += [f"{prefix}/{RESULT_FILE}", *(f"{prefix}/{path}" for path in evidence)]
        if errors:
            raise CandidateQualificationError("execution cannot be frozen: " + "; ".join(errors))
        record_freeze(root, run, "execution", files)

    return apply_transition(run_dir, "freeze-execution", update)


def change_accounting(status: str) -> str:
    """How a qualified, rejected or undecided candidate accounts for its changes."""
    if status == "qualified-for-synthesis-review":
        return "accepted-for-synthesis-review"
    if status in {"rejected-regression", "rejected-target-failure", "blocked-by-synthetic-stress"}:
        return "rejected-by-qualification"
    return "applied-to-candidate"


def qualification_result(root: Path, run: dict[str, Any]) -> dict[str, Any]:
    """Compute every per-case delta and the final gate from frozen material."""
    plan = load_frozen_json(root, run, "plan", "qualification_plan")
    results = load_arm_results(root, plan)
    hashes = frozen_case_hashes(root, run)
    manifest = read_json(contained(root, run["files"]["candidate_manifest"], "candidate manifest"))
    deltas = []
    for entry in plan["cases"]:
        baseline, candidate = (results[entry["case_id"]][arm] for arm in ARMS)
        problems = comparison_problems(baseline, candidate, hashes[entry["case_id"]])
        delta = "invalid" if problems else case_delta(baseline["verdict"], candidate["verdict"])
        deltas.append({
            "case_id": entry["case_id"],
            "role": entry["role"],
            "origin": entry["origin"],
            "required": entry["required"],
            "positive_qualification_eligible": entry["positive_qualification_eligible"],
            "baseline": baseline["verdict"],
            "candidate": candidate["verdict"],
            "delta": delta,
            "comparison_problems": problems,
        })
    contamination = any(
        results[entry["case_id"]][arm]["contamination"] == "confirmed"
        for entry in plan["cases"] for arm in ARMS
    )
    gate = final_gate(
        [{key: value for key, value in item.items() if key != "comparison_problems"} for item in deltas],
        contamination_confirmed=contamination,
    )
    accounting = change_accounting(gate["status"])
    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": run["run_id"],
        "status": gate["status"],
        "reason": gate["reason"],
        "candidate_memory_entry": run["memory_entry_id"],
        "changed_objects": [change["object_id"] for change in manifest["changes"]],
        "change_accounting": [
            {"action": change["action"], "object_id": change["object_id"],
             "relative_path": change["relative_path"], "accounting": accounting}
            for change in manifest["changes"]
        ],
        "case_deltas": deltas,
        "blocking_cases": gate["blocking_cases"],
        "positive_qualification_cases": gate["positive_qualification_cases"],
        "synthetic_cases": [entry["case_id"] for entry in plan["cases"] if entry["origin"] == "synthetic"],
        "protected_case_gap": plan["protected_case_gap"],
        "contamination_confirmed": contamination,
        "canon_modified": False,
    }


def evaluate(run_dir: Path) -> dict[str, Any]:
    """Write and freeze `qualification_result.json`. It never edits canon or memory."""

    def update(root: Path, run: dict[str, Any]) -> None:
        document = qualification_result(root, run)
        if set(document) != QUALIFICATION_RESULT_KEYS:
            raise CandidateQualificationError("qualification result does not have its closed key set")
        path = contained(root, run["files"]["qualification_result"], "qualification result")
        write_json_atomic(path, document)
        record_freeze(root, run, "result", [run["files"]["qualification_result"]])
        disposition = contained(root, DISPOSITION_FILE, "disposition")
        if not disposition.exists():
            write_json_atomic(disposition, disposition_template(run, document["status"]))
        write_text_atomic(root / "README.md", review_brief(run, document))

    return apply_transition(run_dir, "evaluate", update)


def execution_brief(run: dict[str, Any], plan: dict[str, Any], cases: dict[str, dict[str, Any]]) -> str:
    """The brief for executing and grading both arms of every case."""
    lines = [
        f"# CRQ run {run['run_id']}: execute and grade",
        "",
        "Every case runs twice under identical instructions: once with",
        f"`{ARM_BUNDLES}/baseline/cards/` and once with `{ARM_BUNDLES}/candidate/cards/`.",
        "Both bundles are frozen. Never edit `library/`.",
        "",
        "## Isolation",
        "",
        "- Give each arm a fresh context. The candidate arm never sees baseline answers;",
        "  the baseline arm never sees candidate card content.",
        "- Grade the frozen arm artifact, never a summary the arm wrote about itself.",
        "- A required semantic case is graded by a separate evaluator; a deterministic",
        "  case is checked deterministically.",
        "- Record `contamination` as none, suspected or confirmed. Suspected must be",
        "  resolved before `freeze-execution`; confirmed makes the arm invalid and the",
        "  whole qualification invalid.",
        "",
        "## Results",
        "",
        "Fill `cases/<CASE_ID>/<arm>/result.json` for both arms and list every file",
        f"under `cases/<CASE_ID>/<arm>/{EVIDENCE_DIR}/` in `evidence_manifest` with its sha256.",
        "",
        "- `verdict` is pass, fail or invalid; there is no partial result. A pass needs",
        "  every criterion to pass; a fail names the failing criteria. An arm that could",
        "  not exercise the capability (tooling, fixture, contamination, missing",
        "  context) is invalid with an `invalid_reason`, never a fail.",
        "- Keep `case_sha256` as written. `environment` holds only facts that decide",
        "  the comparison (toolchain and runtime versions, model id, relevant flags), and",
        "  both arms must declare exactly the same object; any difference invalidates the",
        "  comparison. Incidental details (timestamps, paths, hostnames) go in `notes` or",
        "  the `executor` block, which are not compared.",
        "",
        "## Cases",
        "",
    ]
    for entry in plan["cases"]:
        case = cases[entry["case_id"]]
        lines += [
            f"### {entry['case_id']} ({entry['role']}, {entry['origin']}, {entry['evaluation_mode']}, "
            f"{entry['visibility']}, {'required' if entry['required'] else 'diagnostic'})",
            "",
            f"Task: {' '.join(case['task'].split())}",
            "",
            "Success contract:",
            "",
            *(f"- {item}" for item in case["success_contract"]),
        ]
        if case["constraints"]:
            lines += ["", "Constraints:", "", *(f"- {item}" for item in case["constraints"])]
        lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------- synthesis


def _level_dir(root: Path, level: int) -> Path:
    return contained(root, f"{SYNTHESIS_LEVELS}/{level}", "synthesis level")


def _batch_dir(root: Path, level: int, number: int) -> Path:
    return contained(root, f"{SYNTHESIS_LEVELS}/{level}/batch-{number:03d}", "synthesis batch")


def _write_level(root: Path, level: int, packets: list[dict[str, Any]]) -> None:
    for number, packet in enumerate(packets, start=1):
        write_json_atomic(_batch_dir(root, level, number) / PACKET_FILE, packet)


def prepare_synthesis(run_dir: Path) -> dict[str, Any]:
    """Build, check and advance hierarchical evidence packets; never changes state.

    The first call writes level 0: the frozen intake's cited events, each exactly
    once, six per batch. Each later call re-derives every existing level from the
    intake and the summaries below it, requires a valid `summary.json` in every
    batch of the top level, and then either merges four summaries per parent
    batch into the next level or, when one batch remains, writes
    `synthesis/input.json` for the assessor. It runs only before the assessment
    freezes.
    """
    root, run = load_run(run_dir)
    require_current_controller(run)
    _refuse_terminal(run)
    if run["state"] != "prepared":
        raise CandidateQualificationError(
            f"prepare-synthesis informs the assessment and runs only in prepared, found {run['state']}"
        )
    verify_frozen_state(root, run)
    events = load_intake(root, run)["events"]
    levels_root = contained(root, SYNTHESIS_LEVELS, "synthesis levels")
    if not levels_root.exists():
        packets = leaf_packets(run["run_id"], events)
        _write_level(root, 0, packets)
        return {"level": 0, "batches": len(packets), "complete": False}

    found = sorted(int(path.name) for path in levels_root.iterdir() if path.is_dir() and path.name.isdigit())
    if found != list(range(len(found))):
        raise CandidateQualificationError(f"synthesis levels must be 0..n without gaps, found {found}")
    expected = leaf_packets(run["run_id"], events)
    errors: list[str] = []
    level_pairs: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for level in found:
        if level:
            expected = parent_packets(run["run_id"], level, level_pairs)
        present = sorted(path.name for path in _level_dir(root, level).iterdir())
        wanted = [f"batch-{number:03d}" for number in range(1, len(expected) + 1)]
        if present != wanted:
            raise CandidateQualificationError(f"synthesis level {level} must hold exactly {wanted}")
        level_pairs = []
        for number, packet in enumerate(expected, start=1):
            batch = _batch_dir(root, level, number)
            if read_json(batch / PACKET_FILE) != packet:
                errors.append(f"{packet['batch_id']}: input.json no longer matches the evidence it was built from")
                continue
            summary_path = batch / SUMMARY_FILE
            if not summary_path.is_file():
                errors.append(f"{packet['batch_id']}: summary.json is missing")
                continue
            summary = read_json(summary_path)
            children = [child["summary"] for child in packet["children"]]
            problems = validate_summary(summary, set(packet["event_ids"]), children)
            errors += [f"{packet['batch_id']}: {problem}" for problem in problems]
            level_pairs.append((packet, summary))
    if errors:
        raise CandidateQualificationError("synthesis cannot advance: " + "; ".join(errors))
    top = found[-1]
    if len(level_pairs) == 1:
        packet, summary = level_pairs[0]
        write_json_atomic(contained(root, SYNTHESIS_INPUT, "synthesis input"), {
            "schema_version": SCHEMA_VERSION,
            "run_id": run["run_id"],
            "complete": True,
            "levels": top + 1,
            "final_batch": packet["batch_id"],
            "event_ids": [str(event["event_id"]) for event in events],
            "attention": attention_items(packet["batch_id"], summary),
            "summary": summary,
        })
        return {"level": top, "batches": 1, "complete": True}
    packets = parent_packets(run["run_id"], top + 1, level_pairs)
    _write_level(root, top + 1, packets)
    return {"level": top + 1, "batches": len(packets), "complete": False}


def synthesis_report(root: Path, run: dict[str, Any], disposition: dict[str, Any]) -> str:
    """The human-readable qualification report, generated from frozen material."""
    result = load_frozen_json(root, run, "result", "qualification_result")
    assessment = load_frozen_json(root, run, "assessment", "assessment")
    intake = load_intake(root, run)
    manifest = read_json(contained(root, run["files"]["candidate_manifest"], "candidate manifest"))
    entry = intake["memory_entry"]
    deltas = result["case_deltas"]

    def case_lines(select: Callable[[dict[str, Any]], bool]) -> list[str]:
        chosen = [d for d in deltas if select(d)]
        if not chosen:
            return ["None."]
        return [
            f"- {d['case_id']} ({d['origin']}, {'required' if d['required'] else 'diagnostic'}): "
            f"baseline {d['baseline']}, candidate {d['candidate']}, delta {d['delta']}"
            + (f"; {'; '.join(d['comparison_problems'])}" if d["comparison_problems"] else "")
            for d in chosen
        ]

    lines = [
        "# Candidate Qualification Report",
        "",
        f"Run {run['run_id']} ({run['domain']}). This report changes nothing in `library/` or",
        "Skillset Memory; an accepted delta still lands through the ordinary repository workflow.",
        "",
        "## Candidate",
        "",
        *(f"- {c['action']} `{c['object_id']}` (`{c['relative_path']}`): sections {', '.join(c['changed_sections'])}"
          for c in manifest["changes"]),
        "",
        "## Why it was proposed",
        "",
        f"Memory candidate {entry.get('id')}: {' '.join(str(entry.get('observation', '')).split())}",
        "",
        "## Canon ownership assessment",
        "",
        f"- Disposition {assessment['candidate_disposition']}, failure layer {assessment['failure_layer']}, "
        f"attribution {assessment['primary_attribution']}.",
        f"- Owners: {', '.join(assessment['owner_object_ids']) or 'none'}.",
        f"- Rationale: {' '.join(assessment['rationale'].split())}",
        "",
        "## Changed cards",
        "",
        *(f"- `{c['object_id']}`: {c['accounting']}" for c in result["change_accounting"]),
        "",
        "## Target cases",
        "",
        *case_lines(lambda d: d["role"] == "target"),
        "",
        "## Protected cases",
        "",
        *case_lines(lambda d: d["role"] == "protected" and d["origin"] != "synthetic"),
        "",
        "## Synthetic stress cases",
        "",
        *case_lines(lambda d: d["origin"] == "synthetic"),
        "",
        "Synthetic results never count as positive qualification or empirical evidence.",
        "",
        "## Baseline vs candidate deltas",
        "",
        *(f"- {d['case_id']}: {d['delta']}" for d in deltas),
        "",
        "## Regressions",
        "",
        *(case_lines(lambda d: d["delta"] == "regressed")),
        "",
        "## Invalid or unresolved evidence",
        "",
        *(case_lines(lambda d: d["delta"] == "invalid")),
        *(["", "Confirmed contamination invalidated this batch."] if result["contamination_confirmed"] else []),
        *(["", f"Protection gap: {result['protected_case_gap']}"] if result["protected_case_gap"] else []),
        "",
        "## Qualification status",
        "",
        f"{result['status']}: {result['reason']}.",
        *([f"Blocking cases: {', '.join(result['blocking_cases'])}."] if result["blocking_cases"] else []),
        "",
        "## Recommended synthesis disposition",
        "",
        f"{disposition['synthesis_decision']}: {' '.join(disposition['reason'].split())}",
        *(["", disposition["reviewer_notes"].strip()] if disposition["reviewer_notes"].strip() else []),
        "",
        "## Memory disposition recommendation",
        "",
        f"{disposition['memory_action']} for {disposition['memory_entry_id']}. Apply it deliberately with",
        "`memory.py entry`; this run never writes Skillset Memory.",
        "",
    ]
    return "\n".join(lines)


def finalize(run_dir: Path) -> dict[str, Any]:
    """Check the synthesis disposition, write the report, freeze both, and close.

    A finalized run is read-only. Finalizing never writes `library/` or Skillset
    Memory, and only a qualified candidate may be recorded as accepted.
    """

    def update(root: Path, run: dict[str, Any]) -> None:
        result = load_frozen_json(root, run, "result", "qualification_result")
        path = contained(root, DISPOSITION_FILE, "disposition")
        if not path.is_file():
            raise CandidateQualificationError(f"{DISPOSITION_FILE} is missing")
        disposition = read_json(path)
        errors = validate_disposition(disposition, run=run, status=result["status"])
        if errors:
            raise CandidateQualificationError("run cannot be finalized: " + "; ".join(errors))
        write_text_atomic(contained(root, REPORT_FILE, "report"), synthesis_report(root, run, disposition))
        record_freeze(root, run, "synthesis", [DISPOSITION_FILE, REPORT_FILE])

    return apply_transition(run_dir, "finalize", update)


def review_brief(run: dict[str, Any], result: dict[str, Any]) -> str:
    """The brief for deliberate synthesis review, written at evaluation."""
    return "\n".join([
        f"# CRQ run {run['run_id']}: synthesis review",
        "",
        f"Qualification status: **{result['status']}** ({result['reason']}).",
        "",
        "`qualification_result.json` is frozen. Review it, the candidate and the arm",
        f"evidence, then fill `{DISPOSITION_FILE}` and run `finalize`, which writes",
        f"`{REPORT_FILE}` and closes the run read-only.",
        "",
        f"- `synthesis_decision`: one of {', '.join(SYNTHESIS_DECISIONS)}. Only a",
        "  qualified candidate may be accepted as a canonical delta, and accepting still",
        "  changes nothing: the approved edit lands through the ordinary repository",
        "  workflow with validation, index regeneration, tests and a version bump.",
        f"- `memory_action`: one of {', '.join(MEMORY_ACTIONS)}. It is a",
        "  recommendation; apply it deliberately with `memory.py entry`. Mark a",
        "  candidate resolved only once the fix holds, never because Markdown changed.",
        "- A different candidate, plan or assessment is a fresh run; nothing frozen is",
        "  revised in place.",
        "",
    ])


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
                    result = _optional_json(root, f"cases/{case_id}/{arm}/result.json") if path.is_file() else None
                    if result is None or result.get("verdict") is None:
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
