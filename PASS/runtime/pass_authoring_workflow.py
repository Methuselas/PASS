#!/usr/bin/env python3
"""Disposable, domain-local PASS authoring workflow and staged unit integration.

The host remains responsible for source access and truthful model declarations.
This controller enforces its supported transitions and validates the actual files
it lands; its scratch state is never a library or release dependency.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Iterable
import uuid
import zipfile
import zlib

from . import pass_authoring_run as preflight


RUN_SCHEMA = 2
PHASES = {"load", "source_prep", "preflight", "preflight_accept", "pass1", "checkpoint", "pass2", "pass3", "land",
          "closure_pass2", "closure_pass3", "closure_land", "finished"}
STOP_AFTER = {"source_prep", "preflight", "complete"}
BUCKETS = ("NEW_PATTERNS", "REFINE", "REINFORCE", "VARIANTS", "REPLACE", "NEW_APS", "NEW_DRILLS", "REJECT")
TAXONOMY = ("NEW_SUBCATEGORY", "MOVE", "RENAME", "MERGE")
BUCKET_LABELS = {
    "NEW_PATTERNS": "NEW PATTERNS",
    "REFINE": "REFINE",
    "REINFORCE": "REINFORCE",
    "VARIANTS": "VARIANTS",
    "REPLACE": "REPLACE",
    "NEW_APS": "NEW APS",
    "NEW_DRILLS": "NEW DRILLS",
    "REJECT": "REJECT",
}
TAXONOMY_LABELS = {
    "NEW_SUBCATEGORY": "NEW SUBCATEGORY",
    "MOVE": "MOVE",
    "RENAME": "RENAME",
    "MERGE": "MERGE",
}
SEMANTIC_CHECKS = (
    "identity_and_placement", "relations_and_variant_parentage",
    "contradictions_and_field_meaning", "source_independence",
    "examples_and_overreach", "pattern_ap_drill_ownership",
    "standalone_executability", "instruction_success_contract",
    "cross_library_reconciliation", "metadata_classification",
)
LANGUAGE_SEMANTIC_CHECKS = ("core_language_agnosticism", "language_modernization")
MODERNIZATION_DISPOSITIONS = {"current", "modernized", "historical", "rejected"}
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FLAG_RE = re.compile(r"^[a-z][a-z0-9_]*$")
GENRE_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
RUN_ID_RE = re.compile(r"^r_[0-9a-f]{8}$")
RUN_STORE = "workspace/runs"
RUN_CATALOG = "workspace/runs/catalog.json"
RUN_MANIFEST = "RUN_MANIFEST.json"
RUN_EXPORT_MANIFEST = "PASS_RUN_EXPORT.json"
WINDOWS_PATH_BUDGET = 240
WINDOWS_COMPONENT_BUDGET = 200


class RunError(preflight.PreflightError):
    """The current operation cannot be accepted by the authoring workflow."""


class CheckpointPromotionError(RunError):
    """Authoritative state persisted, but checkpoint promotion did not complete.

    Carries the complete transaction truth so the CLI can emit exactly one
    top-level outcome: whether authoritative state persisted, whether the
    checkpoint advanced, which residue remains, why promotion failed, and which
    recovery action is safe. A failure here must never be reported as a clean
    success, and the operation's own result must never print alongside a
    contradictory BLOCKED line.
    """

    def __init__(
        self,
        message: str,
        *,
        reason: str,
        state_sha256: str,
        authoritative: dict[str, Any],
        checkpoint: dict[str, Any] | None,
        residue: dict[str, bool],
        previous_checkpoint_restored: bool,
        fresh_checkpoint_retained: bool,
        safe_to_continue: str,
    ):
        super().__init__(message)
        self.reason = reason
        self.state_sha256 = state_sha256
        self.authoritative = authoritative
        self.checkpoint = checkpoint
        self.residue = residue
        self.previous_checkpoint_restored = previous_checkpoint_restored
        self.fresh_checkpoint_retained = fresh_checkpoint_retained
        self.safe_to_continue = safe_to_continue

    def as_record(self) -> dict[str, Any]:
        if self.checkpoint is None:
            newer = "authoritative"
        elif self.checkpoint.get("state_sha256") != self.state_sha256:
            newer = "authoritative"
        else:
            newer = "equal"
        return {
            "outcome": "authoritative_state_persisted_checkpoint_not_advanced",
            "authoritative_state_persisted": True,
            "checkpoint_advanced": False,
            "authoritative": self.authoritative,
            "checkpoint": self.checkpoint,
            "newer": newer,
            "residue": self.residue,
            "reason": self.reason,
            "previous_checkpoint_restored": self.previous_checkpoint_restored,
            "fresh_checkpoint_retained": self.fresh_checkpoint_retained,
            "safe_to_continue": self.safe_to_continue,
            "recovery": (
                "run repair-checkpoint to establish a verified checkpoint from the current authoritative state "
                "(non-destructive); recover --rollback-authoritative is the explicit destructive alternative"
            ),
            "message": str(self),
        }


class ResidueBlockedError(RunError):
    """A mutating command refused to run because checkpoint residue is unresolved.

    Raised before any command side effect, so the printed record truthfully
    declares side_effects: false.
    """

    def __init__(self, action: str, residue: dict[str, bool]):
        self.action = action
        self.residue = residue
        super().__init__(
            f"checkpoint residue blocks {action}: {json.dumps(residue, sort_keys=True)}; no side effects were "
            f"taken — inspect {CHECKPOINT_FAILURE}, then run repair-checkpoint (non-destructive; keeps the "
            "current authoritative state) or recover --rollback-authoritative (explicit destructive rollback)"
        )

    def as_record(self) -> dict[str, Any]:
        return {
            "outcome": "blocked_checkpoint_residue",
            "action": self.action,
            "residue": self.residue,
            "side_effects": False,
            "message": str(self),
        }


def exact(data: Any, keys: Iterable[str], label: str) -> None:
    if not isinstance(data, dict):
        raise RunError(f"{label}: expected an object")
    preflight._require_exact_keys(data, set(keys), label)


def string(value: Any, label: str) -> str:
    return preflight._nonempty_string(value, label)


def array(value: Any, label: str) -> list:
    if not isinstance(value, list):
        raise RunError(f"{label}: expected a list (use [] for none)")
    return value


def relative(value: Any) -> PurePosixPath:
    name = string(value, "relative path")
    if "\\" in name or ":" in name or any(p in {"", ".", ".."} for p in name.split("/")):
        raise RunError(f"unsafe relative path: {name}")
    path = PurePosixPath(name)
    if path.is_absolute():
        raise RunError(f"unsafe relative path: {name}")
    return path


def inside(root: Path, name: str | PurePosixPath) -> Path:
    path = root.joinpath(*relative(str(name)).parts)
    if not path.resolve().is_relative_to(root.resolve()):
        raise RunError(f"path escapes its owner: {path}")
    cursor = path
    while cursor != root:
        if cursor.is_symlink() or getattr(cursor, "is_junction", lambda: False)():
            raise RunError(f"linked authoring path is not supported: {cursor}")
        cursor = cursor.parent
    return path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree_hashes(root: Path) -> dict[str, str]:
    result = {}
    if root.is_dir():
        for path in sorted(root.rglob("*")):
            safe = inside(root, path.relative_to(root).as_posix())
            if safe.is_file():
                result[path.relative_to(root).as_posix()] = digest(safe)
    return result


def atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(prefix=f".{path.name}.pass-", dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def sandbox_manifest(repo: Path) -> dict | None:
    """Return the experimental portable marker when this checkout is a sandbox."""
    path = repo / "PASS_SANDBOX.json"
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"mode": "sandbox", "marker": "unreadable"}
    if not isinstance(data, dict):
        return {"mode": "sandbox", "marker": "invalid"}
    return data


def enforce_sandbox_boundary(repo: Path) -> None:
    """Refuse experimental-portable authoring when copied onto a forbidden canonical root."""
    manifest = sandbox_manifest(repo)
    if manifest is None:
        return
    forbidden = manifest.get("forbidden_repo_paths", [])
    if not isinstance(forbidden, list):
        raise RunError("PASS_SANDBOX.json forbidden_repo_paths must be a list")
    current = os.path.normcase(str(repo.resolve()).rstrip("\\/"))
    for raw in forbidden:
        if not isinstance(raw, str) or not raw.strip():
            raise RunError("PASS_SANDBOX.json contains an invalid forbidden repo path")
        target = os.path.normcase(str(Path(raw).resolve()).rstrip("\\/"))
        if current == target:
            raise RunError(
                f"experimental PASS sandbox refuses to run from canonical repo path {repo}; "
                "extract the portable into a separate directory"
            )


def controller_project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def enforce_experimental_controller_target(repo: Path) -> None:
    """Honor the portable's forbidden canonical roots even when --repo-root points elsewhere.

    EXP-001's guard looked only for PASS_SANDBOX.json in the target repo, which
    allowed portable code to be aimed at a configured canonical PASS root. EXP-002 consults the
    controller portable's own marker as well. Test/scratch repos remain usable;
    explicitly forbidden canonical roots do not.
    """
    controller_root = controller_project_root().resolve()
    manifest = sandbox_manifest(controller_root)
    if not manifest or manifest.get("mode") != "experimental-sandbox":
        return
    forbidden = manifest.get("forbidden_repo_paths", [])
    if not isinstance(forbidden, list):
        raise RunError("controller PASS_SANDBOX.json forbidden_repo_paths must be a list")
    target = os.path.normcase(str(repo.resolve()).rstrip("\\/"))
    for raw in forbidden:
        if not isinstance(raw, str) or not raw.strip():
            raise RunError("controller PASS_SANDBOX.json contains an invalid forbidden repo path")
        blocked = os.path.normcase(str(Path(raw).resolve()).rstrip("\\/"))
        if target == blocked:
            raise RunError(
                f"experimental PASS controller refuses canonical repo root {repo.resolve()}; "
                "use the portable's own library/workspace copy for EXP-002 drill work"
            )


def validate_windows_path_budget(path: Path, label: str = "path") -> None:
    """Fail deterministically before a path reaches common Windows compatibility cliffs."""
    rendered = str(path.absolute()).replace("/", "\\")
    if len(rendered) > WINDOWS_PATH_BUDGET:
        raise RunError(
            f"{label} exceeds conservative Windows path budget ({len(rendered)} > {WINDOWS_PATH_BUDGET}): {rendered}"
        )
    for component in path.parts:
        if len(component) > WINDOWS_COMPONENT_BUDGET:
            raise RunError(
                f"{label} has a path component longer than {WINDOWS_COMPONENT_BUDGET} characters: {component[:60]}..."
            )


def run_store(repo: Path) -> Path:
    return inside(repo, RUN_STORE)


def catalog_path(repo: Path) -> Path:
    return inside(repo, RUN_CATALOG)


def run_manifest_path(root: Path) -> Path:
    return inside(root, RUN_MANIFEST)


def read_run_manifest(root: Path, required: bool = False) -> dict | None:
    path = run_manifest_path(root)
    if not path.is_file():
        if required:
            raise RunError(f"short-ID run is missing {RUN_MANIFEST}: {root}")
        return None
    data = preflight._read_json(str(path))
    exact(
        data,
        {"schema_version", "run_id", "domain", "genre", "display_label", "source", "current", "created_at", "updated_at"},
        "run manifest",
    )
    if data["schema_version"] != 1 or not RUN_ID_RE.fullmatch(string(data["run_id"], "run manifest run_id")):
        raise RunError("unsupported or invalid run manifest identity")
    if not GENRE_RE.fullmatch(string(data["genre"], "run manifest genre")):
        raise RunError("run manifest genre must be a lowercase metadata slug")
    if not isinstance(data["source"], dict) or not isinstance(data["current"], dict):
        raise RunError("run manifest source/current must be objects")
    return data


def _catalog_entries(repo: Path) -> list[dict]:
    path = catalog_path(repo)
    if not path.is_file():
        return []
    data = preflight._read_json(str(path))
    if set(data) != {"schema_version", "entries"} or data["schema_version"] != 1 or not isinstance(data["entries"], list):
        raise RunError("workspace/runs/catalog.json is malformed")
    return data["entries"]


def register_run(repo: Path, root: Path, manifest: dict) -> None:
    store = run_store(repo)
    store.mkdir(parents=True, exist_ok=True)
    relative_root = root.relative_to(repo).as_posix()
    entry = {
        "run_id": manifest["run_id"],
        "path": relative_root,
        "domain": manifest["domain"],
        "genre": manifest["genre"],
        "display_label": manifest["display_label"],
        "phase": manifest["current"].get("phase"),
        "status": manifest["current"].get("status"),
    }
    entries = [e for e in _catalog_entries(repo) if isinstance(e, dict) and e.get("run_id") != manifest["run_id"]]
    entries.append(entry)
    entries.sort(key=lambda e: e.get("run_id", ""))
    atomic_write(catalog_path(repo), (json.dumps({"schema_version": 1, "entries": entries}, indent=2) + "\n").encode("utf-8"))


def _new_run_id(repo: Path) -> str:
    store = run_store(repo)
    for _ in range(100):
        run_id = f"r_{uuid.uuid4().hex[:8]}"
        if not (store / run_id).exists():
            return run_id
    raise RunError("could not allocate a unique short run_id")


def _manifest_current(state: dict) -> dict:
    phase = state.get("phase")
    unit_id = None
    plan = state.get("plan")
    index = state.get("unit_index", 0)
    if isinstance(plan, dict) and isinstance(plan.get("units"), list) and isinstance(index, int) and 0 <= index < len(plan["units"]):
        unit_id = plan["units"][index].get("unit_id")
    return {"phase": phase, "unit": unit_id, "status": "finished" if phase == "finished" else "active"}


def sync_run_manifest(repo: Path, root: Path, state: dict) -> None:
    manifest = read_run_manifest(root, required=False)
    if manifest is None:
        return
    manifest["current"] = _manifest_current(state)
    prep_identity = root / "controller" / "source-identity.json"
    if prep_identity.is_file():
        identity = preflight._read_json(str(prep_identity))
        manifest["source"]["sha256"] = identity.get("sha256")
        manifest["source"]["size"] = identity.get("size")
    plan = state.get("plan")
    if isinstance(plan, dict):
        manifest["source"]["title"] = plan.get("title") or manifest["source"].get("title")
        manifest["source"]["author"] = plan.get("author") or manifest["source"].get("author")
        manifest["source"]["edition"] = plan.get("edition") or manifest["source"].get("edition")
    manifest["updated_at"] = now()
    atomic_write(run_manifest_path(root), (json.dumps(manifest, indent=2) + "\n").encode("utf-8"))
    register_run(repo, root, manifest)


def list_registered_runs(repo: Path, *, domain: str | None = None, genre: str | None = None) -> list[dict]:
    result = []
    store = run_store(repo)
    if not store.is_dir():
        return result
    for root in sorted(store.glob("r_*")):
        if not root.is_dir() or not RUN_ID_RE.fullmatch(root.name):
            continue
        manifest = read_run_manifest(root, required=True)
        if manifest["run_id"] != root.name:
            raise RunError(f"run manifest identity/path mismatch: {root}")
        if domain is not None and manifest["domain"] != domain:
            continue
        if genre is not None and manifest["genre"] != genre:
            continue
        result.append({**manifest, "path": str(root)})
    return result


def export_run(repo: Path, root: Path, output: Path) -> Path:
    root = run_root(repo, root)
    manifest = read_run_manifest(root, required=True)
    files = tree_hashes(root)
    if "controller/operation.lock" in files:
        raise RunError("cannot export a run while an operation.lock is present")
    export_record = {
        "schema_version": 1,
        "run_id": manifest["run_id"],
        "run_manifest_sha256": digest(run_manifest_path(root)),
        "files": files,
    }
    output = output.absolute()
    if output.suffix.lower() != ".zip":
        output = output.with_suffix(".zip")
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(RUN_EXPORT_MANIFEST, json.dumps(export_record, indent=2) + "\n")
        for name in sorted(files):
            archive.write(inside(root, name), f"run/{name}")
    return output


def import_run(repo: Path, source: Path, *, collision: str = "error") -> Path:
    """Import a run archive under typed failure (EXP-003 Target F).

    Corrupt, truncated, or structurally unexpected archives surface as a RunError
    that says so and confirms no run was registered; raw KeyError/ValueError/
    BadZipFile tracebacks never reach the CLI. Registration happens only after
    every member hash and manifest check has passed.
    """
    try:
        return _import_run(repo, source, collision=collision)
    except RunError:
        raise
    except (zipfile.BadZipFile, zipfile.LargeZipFile, zlib.error, EOFError, RuntimeError, ValueError, KeyError, TypeError) as exc:
        raise RunError(
            f"run import archive is corrupt or truncated ({type(exc).__name__}: {exc}); no run was registered"
        ) from exc


def _import_run(repo: Path, source: Path, *, collision: str = "error") -> Path:
    if collision not in {"error", "new-id"}:
        raise RunError("run import collision policy must be error or new-id")
    source = source.absolute()
    if not source.is_file():
        raise RunError(f"run import archive does not exist: {source}")
    with zipfile.ZipFile(source) as archive:
        names = archive.namelist()
        if RUN_EXPORT_MANIFEST not in names:
            raise RunError(f"run import archive is missing {RUN_EXPORT_MANIFEST}")
        for name in names:
            posix = PurePosixPath(name)
            if posix.is_absolute() or any(part in {"", ".", ".."} for part in posix.parts):
                raise RunError(f"unsafe run import member: {name}")
        if len(names) != len(set(names)):
            raise RunError("run import archive contains duplicate members")
        export_record = json.loads(archive.read(RUN_EXPORT_MANIFEST))
        exact(export_record, {"schema_version", "run_id", "run_manifest_sha256", "files"}, "run export manifest")
        if export_record["schema_version"] != 1 or not RUN_ID_RE.fullmatch(string(export_record["run_id"], "export run_id")):
            raise RunError("unsupported run export identity")
        files = export_record["files"]
        if not isinstance(files, dict):
            raise RunError("run export files must be an object")
        expected_members = {RUN_EXPORT_MANIFEST, *(f"run/{name}" for name in files)}
        if set(names) != expected_members:
            raise RunError("run import archive members do not exactly match its file manifest")
        for name, sha in files.items():
            relative(name)
            payload = archive.read(f"run/{name}")
            if hashlib.sha256(payload).hexdigest() != sha:
                raise RunError(f"run import hash mismatch: {name}")
        raw_manifest = archive.read(f"run/{RUN_MANIFEST}")
        if hashlib.sha256(raw_manifest).hexdigest() != export_record["run_manifest_sha256"]:
            raise RunError("run import RUN_MANIFEST hash mismatch")
        manifest = json.loads(raw_manifest)
        if manifest.get("run_id") != export_record["run_id"]:
            raise RunError("run import identity mismatch between export and run manifest")
        if manifest.get("domain") not in authorable_domains(repo):
            raise RunError(f"run import domain is not authorable in this portable: {manifest.get('domain')}")
        if not isinstance(manifest.get("genre"), str) or not GENRE_RE.fullmatch(manifest["genre"]):
            raise RunError("run import manifest has invalid genre metadata")
        run_id = manifest["run_id"]
        target = run_store(repo) / run_id
        if target.exists():
            if collision == "error":
                raise RunError(f"run_id collision: {run_id}; use --collision new-id only when a distinct imported identity is intended")
            run_id = _new_run_id(repo)
            target = run_store(repo) / run_id
        validate_windows_path_budget(target, "imported run root")
        target.mkdir(parents=True, exist_ok=False)
        try:
            for name in sorted(files):
                out = inside(target, name)
                validate_windows_path_budget(out, f"imported run member {name}")
                out.parent.mkdir(parents=True, exist_ok=True)
                atomic_write(out, archive.read(f"run/{name}"))
            if run_id != manifest["run_id"]:
                manifest["run_id"] = run_id
                manifest["updated_at"] = now()
                atomic_write(run_manifest_path(target), (json.dumps(manifest, indent=2) + "\n").encode("utf-8"))
            checked = read_run_manifest(target, required=True)
            if checked["run_id"] != run_id:
                raise RunError("imported run manifest failed identity verification")
            register_run(repo, target, checked)
        except BaseException:
            shutil.rmtree(target, ignore_errors=True)
            raise
    return target


def migrate_run(repo: Path, source: Path, *, genre: str | None = None) -> Path:
    """Copy a legacy-layout prepped run into the short-ID store (EXP-003 §5.3).

    The legacy directory is the preserved original: it is copied byte-for-byte
    into workspace/runs/<new short-id>, a short-ID RUN_MANIFEST is built from
    its controller state (genre from the parent directory name or --genre),
    every member is verified against the source, then the copy is registered.
    The source is never modified, and any failure removes the incomplete target
    before re-raising so nothing is half-registered.
    """
    repo = repo.resolve()
    enforce_sandbox_boundary(repo)
    source = source.absolute()
    if not source.is_dir():
        raise RunError(f"legacy run directory does not exist: {source}")
    if read_run_manifest(source, required=False) is not None:
        raise RunError(f"source already carries a short-ID {RUN_MANIFEST}; use runs import for it")
    if inside(source, "controller/operation.lock").exists():
        raise RunError("legacy run holds an operation.lock; its owning operation must finish before migration")
    for residue in ("controller/checkpoint.new", "controller/checkpoint.old", "controller/checkpoint-failure.json"):
        if inside(source, residue).exists():
            raise RunError(f"legacy run holds checkpoint residue ({residue}); resolve it before migration")
    state_path = inside(source, "controller/run.json")
    if not state_path.is_file():
        raise RunError("legacy run is missing controller/run.json")
    state = preflight._read_json(str(state_path))
    domain = state.get("domain")
    if domain not in authorable_domains(repo):
        raise RunError(f"legacy run domain is not authorable in this portable: {domain}")
    if genre is None:
        candidate = source.parent.name.lower().replace("_", "-")
        genre = candidate if GENRE_RE.fullmatch(candidate) else None
    if genre is None or not GENRE_RE.fullmatch(genre):
        raise RunError(
            "could not derive a genre slug from the legacy directory name; pass --genre as a lowercase metadata slug"
        )
    display_label = source.name
    note = inside(source, "RUN_NOTE.md")
    if note.is_file():
        lines = note.read_text(encoding="utf-8", errors="replace").splitlines()
        if lines and lines[0].startswith("# PASS authoring task: "):
            display_label = lines[0][len("# PASS authoring task: "):].strip() or display_label
    identity_path = inside(source, "controller/source-identity.json")
    identity = preflight._read_json(str(identity_path)) if identity_path.is_file() else {}
    plan = state.get("plan") if isinstance(state.get("plan"), dict) else {}
    run_id = _new_run_id(repo)
    target = inside(repo, f"{RUN_STORE}/{run_id}")
    validate_windows_path_budget(target, "migrated run root")
    created = now()
    manifest = {
        "schema_version": 1,
        "run_id": run_id,
        "domain": domain,
        "genre": genre,
        "display_label": display_label,
        "source": {
            "name": str(state.get("source") or "").replace("\\", "/").rsplit("/", 1)[-1] or f"{run_id}.pdf",
            "path": state.get("source"),
            "title": plan.get("title"),
            "author": plan.get("author"),
            "edition": plan.get("edition"),
            "sha256": identity.get("sha256"),
            "size": identity.get("size"),
        },
        "current": _manifest_current(state),
        "created_at": created,
        "updated_at": created,
    }
    try:
        target.mkdir(parents=True, exist_ok=False)
        for path in sorted(source.rglob("*")):
            rel = path.relative_to(source).as_posix()
            out = inside(target, rel)
            if path.is_dir():
                out.mkdir(parents=True, exist_ok=True)
                continue
            validate_windows_path_budget(out, f"migrated run member {rel}")
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, out)
        for path in sorted(source.rglob("*")):
            if path.is_file():
                rel = path.relative_to(source).as_posix()
                if digest(inside(target, rel)) != digest(path):
                    raise RunError(f"migration copy verification failed: {rel}")
        atomic_write(run_manifest_path(target), (json.dumps(manifest, indent=2) + "\n").encode("utf-8"))
        checked = read_run_manifest(target, required=True)
        if checked["run_id"] != run_id:
            raise RunError("migrated run manifest failed identity verification")
        register_run(repo, target, checked)
    except BaseException:
        shutil.rmtree(target, ignore_errors=True)
        raise
    return target


def authorable_domains(repo: Path) -> list[str]:
    return sorted(
        p.name for p in (repo / "library").iterdir()
        if p.is_dir() and p.name != "metaskills" and preflight.DOMAIN_RE.fullmatch(p.name)
        and not p.is_symlink() and not getattr(p, "is_junction", lambda: False)()
        and any(p.rglob("MODULE.yaml"))
        and p.resolve().parent == (repo / "library").resolve()
    )


def required_documents(repo: Path) -> list[str]:
    documents = ["PASS/SKILL.md", "PASS/docs/PASS_RUN.md", "PASS/docs/AUTHORING_RUNTIME.md", "PASS/docs/PASS_DOCTRINE.md", "PASS/docs/PASS_SCHEMA.md", "PASS/docs/PASS_LIBRARY.md"]
    for entry in ("AGENTS.md", "CLAUDE.md"):
        if (repo / entry).is_file():
            documents.insert(0, entry)
            break
    for name in documents:
        if not (repo / name).is_file():
            raise RunError(f"required canonical instructions are missing: {name}")
    return documents


def select_domain(repo: Path, domain: str | None) -> str:
    domains = authorable_domains(repo)
    if domain is None:
        if len(domains) != 1:
            raise RunError("select the user-authorized --domain; this project has no unambiguous single-domain default")
        domain = domains[0]
    if domain not in domains:
        raise RunError(f"domain is not an existing authorable package: {domain}; domain creation is a separate authorized operation")
    return domain


def open_runs(repo: Path, domain: str) -> list[Path]:
    """Every unfinished run of one domain across the short store and legacy layouts."""
    found: list[Path] = []

    # EXP-002 short-ID store. Domain/genre are manifest metadata rather than path authority.
    for item in list_registered_runs(repo, domain=domain):
        root = Path(item["path"])
        state_path = root / "controller/run.json"
        if (root / ABANDONED).is_file() or (item.get("current") or {}).get("status") in {"finished", "abandoned"}:
            continue
        if not state_path.is_file():
            # Missing state without a terminal manifest status fails closed.
            found.append(root)
            continue
        try:
            phase = json.loads(state_path.read_text(encoding="utf-8")).get("phase")
        except (OSError, ValueError, AttributeError):
            phase = None
        if phase != "finished":
            found.append(root)

    # Compatibility: old 2-part <domain>/<run> and observed 3-part
    # <domain>/<genre>/<run> skill-staging roots remain resumable/importable.
    legacy = inside(repo, f"workspace/skill-staging/{domain}")
    if legacy.is_dir():
        candidates = list(legacy.iterdir())
        for child in list(legacy.iterdir()):
            if child.is_dir():
                candidates.extend(child.iterdir())
        for root in sorted(set(candidates)):
            if not root.is_dir():
                continue
            try:
                rel = root.relative_to(legacy)
            except ValueError:
                continue
            if len(rel.parts) not in {1, 2}:
                continue
            state_path = root / "controller/run.json"
            if not state_path.is_file():
                continue
            try:
                state = json.loads(state_path.read_text(encoding="utf-8"))
                phase = state.get("phase")
                state_domain = state.get("domain")
            except (OSError, ValueError, AttributeError):
                phase, state_domain = None, domain
            if state_domain == domain and phase != "finished":
                found.append(root)
    return sorted(set(found), key=lambda path: str(path))


def matching_runs(repo: Path, domain: str, source: Path) -> list[Path]:
    """Unfinished runs of this domain bound to the same source path or the same bytes.

    Only size and SHA-256 are compared; the source's content is not read as
    instruction. Bytes are hashed only when a candidate's size already matches.
    An unreadable candidate matches, so a damaged run fails closed.
    """
    source = source.resolve()
    size = source.stat().st_size
    source_sha = None
    found = []
    for root in open_runs(repo, domain):
        try:
            bound = Path(json.loads((root / "controller/run.json").read_text(encoding="utf-8"))["source"]).resolve()
            if os.path.normcase(str(bound)) == os.path.normcase(str(source)):
                found.append(root)
                continue
            marker = root / "controller/source-identity.json"
            if marker.is_file():
                identity = json.loads(marker.read_text(encoding="utf-8"))
                other_size, other_sha = identity["size"], identity["sha256"]
            elif bound.is_file():
                other_size, other_sha = bound.stat().st_size, None
            else:
                continue
        except (OSError, ValueError, KeyError, TypeError):
            found.append(root)
            continue
        if other_size != size:
            continue
        source_sha = source_sha or digest(source)
        if (other_sha or digest(bound)) == source_sha:
            found.append(root)
    return found


def start(
    repo: Path,
    source: Path,
    domain: str | None,
    task: str | None,
    stop_after: str = "complete",
    genre: str | None = None,
) -> Path:
    repo = repo.resolve()
    enforce_sandbox_boundary(repo)
    domain = select_domain(repo, domain)
    required_documents(repo)
    source = source.resolve()
    if not source.is_file():
        raise RunError(f"source does not exist: {source}")
    existing = matching_runs(repo, domain, source)
    if existing:
        raise RunError(
            f"existing incomplete PASS run found for this source: {existing[0]}. Resume it with "
            f"`python PASS/pass.py resume --run {existing[0]}`, or abandon it explicitly with "
            f"`python PASS/pass.py abandon --run {existing[0]} --reason <user instruction>` before starting again"
        )
    if stop_after not in STOP_AFTER:
        raise RunError("stop_after must be source_prep, preflight, or complete")
    if task is None:
        stem = re.sub(r"[^a-z0-9]+", "-", source.stem.lower()).strip("-") or "book"
        task = f"{stem}-{uuid.uuid4().hex[:8]}"
    if not SLUG_RE.fullmatch(task):
        raise RunError("task must be a lowercase book/run slug")
    genre = genre or "unclassified"
    if not GENRE_RE.fullmatch(genre):
        raise RunError("genre must be a lowercase metadata slug such as python or game-development")

    run_id = _new_run_id(repo)
    root = inside(repo, f"{RUN_STORE}/{run_id}")
    validate_windows_path_budget(root, "short-ID run root")
    if root.exists():
        raise RunError(f"run_id collision: {run_id}")
    (root / "controller").mkdir(parents=True)
    (root / "drafts").mkdir()
    state = {
        "schema_version": RUN_SCHEMA, "domain": domain, "source": str(source),
        "phase": "load", "unit_index": 0, "plan": None, "pass1": None,
        "pass2": None, "reviewed_sha256": None, "live_hashes": None,
        "source_prep": None, "stop_after": stop_after, "stop_reached": False,
    }
    atomic_write(root / "controller/run.json", (json.dumps(state, indent=2) + "\n").encode())
    created = now()
    manifest = {
        "schema_version": 1,
        "run_id": run_id,
        "domain": domain,
        "genre": genre,
        "display_label": task,
        "source": {
            "name": source.name,
            "path": str(source),
            "title": source.stem,
            "author": None,
            "edition": None,
            "sha256": None,
            "size": source.stat().st_size,
        },
        "current": _manifest_current(state),
        "created_at": created,
        "updated_at": created,
    }
    atomic_write(run_manifest_path(root), (json.dumps(manifest, indent=2) + "\n").encode("utf-8"))
    register_run(repo, root, manifest)
    (root / "RUN_NOTE.md").write_text(
        f"# PASS authoring task: {task}\n\nRun ID: `{run_id}`. Domain: `{domain}`. Genre metadata: `{genre}`.\n\n"
        f"Owner: ordinary PASS controller.\nPurpose: {domain} authoring from {source.name}; cards are staged by canonical category.\n"
        "Physical run location is intentionally short; domain/genre/source identity belong to RUN_MANIFEST.json, not the directory hierarchy.\n"
        "Cleanup: accepted unit deltas remain run-local until source close canonicalizes them; close-run removes generated controller state.\n"
        "Preserve original source inputs, other tasks and explicit failure-evidence holds.\n"
        "This directory is disposable and is not card canon or Skillset Memory.\n", encoding="utf-8"
    )
    return root


def run_root(repo: Path, root: Path) -> Path:
    repo = repo.resolve(strict=False)
    raw = str(root)
    if RUN_ID_RE.fullmatch(raw):
        root = run_store(repo) / raw
    else:
        root = root.absolute()
    root = root.resolve(strict=False)

    short_base = run_store(repo).resolve(strict=False)
    try:
        short_rel = root.relative_to(short_base)
    except ValueError:
        short_rel = None
    if short_rel is not None:
        if len(short_rel.parts) != 1 or not RUN_ID_RE.fullmatch(short_rel.parts[0]):
            raise RunError("short-ID run must be workspace/runs/r_<8-hex>")
        inside(repo, root.relative_to(repo).as_posix())
        if root.exists():
            manifest = read_run_manifest(root, required=True)
            if manifest["run_id"] != root.name:
                raise RunError("run_id is identity; RUN_MANIFEST.json does not match the physical short-ID directory")
        return root

    legacy_base = (repo / "workspace/skill-staging").resolve(strict=False)
    try:
        legacy_rel = root.relative_to(legacy_base)
    except ValueError as exc:
        raise RunError(
            "run must be a short-ID workspace/runs/r_<8-hex> root or a legacy "
            "workspace/skill-staging/<domain>/<book-run> / <domain>/<genre>/<book-run> root"
        ) from exc
    if len(legacy_rel.parts) not in {2, 3}:
        raise RunError(
            "legacy run must have domain/book-run or domain/genre/book-run shape; "
            "genre is classification metadata, not durable path identity"
        )
    inside(repo, root.relative_to(repo).as_posix())
    return root


@contextmanager
def operation_lock(root: Path):
    """Exclusive per-run operation lease; it names its process so a leftover can be diagnosed."""
    path = inside(root, "controller/operation.lock")
    try:
        descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        raise RunError(
            "another operation owns this run; if no PASS process is still running, a previous operation was "
            "interrupted: inspect the library and staged files before removing the stale operation.lock"
        ) from exc
    try:
        os.write(descriptor, (json.dumps({"pid": os.getpid(), "acquired_at": now()}) + "\n").encode("utf-8"))
    finally:
        os.close(descriptor)
    try:
        yield
    finally:
        path.unlink(missing_ok=True)


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


ABANDONED = "controller/abandoned-run.json"
RESET_INTENT = "controller/reset-intent.json"
CHECKPOINT = "controller/checkpoint"
CHECKPOINT_FAILURE = "controller/checkpoint-failure.json"
CHECKPOINT_SCHEMA = 3
HANDOFF_MARK = "<!-- Generated by PASS/pass.py after every accepted step; rewritten each time. Do not edit. -->"


def checkpoint_residue(root: Path) -> dict[str, bool]:
    """Read-only facts about unfinished checkpoint-promotion state."""
    return {
        "checkpoint_new": inside(root, f"{CHECKPOINT}.new").exists(),
        "checkpoint_old": inside(root, f"{CHECKPOINT}.old").exists(),
        "failure_record": inside(root, CHECKPOINT_FAILURE).is_file(),
    }


def residue_present(root: Path) -> bool:
    return any(checkpoint_residue(root).values())


def abandon(repo: Path, root: Path, reason: str) -> str:
    """Retire an unfinished run on explicit instruction, preserving its drafts and state for inspection.

    Deliberately tolerant of damaged state, so a run that no longer loads can
    still be retired instead of blocking its source forever.
    """
    repo = repo.resolve()
    root = run_root(repo, root)
    if not isinstance(reason, str) or not reason.strip():
        raise RunError("abandon requires --reason quoting the user's explicit instruction")
    state_path = inside(root, "controller/run.json")
    with operation_lock(root):
        if not state_path.is_file():
            raise RunError("no active run state to abandon")
        raw = state_path.read_text(encoding="utf-8")
        try:
            state = json.loads(raw)
        except ValueError:
            state = raw
        if isinstance(state, dict) and state.get("phase") == "finished":
            raise RunError("a finished run is closed with close-run, not abandoned")
        record = {"schema_version": 1, "abandoned_at": now(), "reason": reason, "state": state}
        atomic_write(inside(root, ABANDONED), (json.dumps(record, indent=2) + "\n").encode("utf-8"))
        manifest = read_run_manifest(root, required=False)
        if manifest is not None:
            current = _manifest_current(state) if isinstance(state, dict) else {"phase": None, "unit": None, "status": "abandoned"}
            current["status"] = "abandoned"
            manifest["current"] = current
            manifest["updated_at"] = record["abandoned_at"]
            atomic_write(run_manifest_path(root), (json.dumps(manifest, indent=2) + "\n").encode("utf-8"))
            register_run(repo, root, manifest)
        inside(root, "controller/next-action.json").unlink(missing_ok=True)
        state_path.unlink()
        note = inside(root, "RUN_NOTE.md")
        if note.is_file():
            with note.open("a", encoding="utf-8") as handle:
                handle.write(f"\nAbandoned {record['abandoned_at']}: {reason}\nRetained for inspection; delete this directory when it is no longer needed.\n")
    return f"RUN ABANDONED: {root.name} — drafts and final state retained in {ABANDONED}; the source may be started again"


class Run:
    def __init__(self, repo: Path, root: Path):
        self.repo = repo.resolve()
        enforce_sandbox_boundary(self.repo)
        self.root = run_root(self.repo, root)
        reset_intent = inside(self.root, RESET_INTENT)
        if reset_intent.is_file():
            raise RunError(
                f"run has an authoritative start-over intent and may not resume/recover: {self.root}; "
                "rerun `python PASS/pass.py start-over --run <run> ...` to finish the reset transaction"
            )
        abandoned = inside(self.root, ABANDONED)
        if abandoned.is_file():
            raise RunError(f"run was abandoned and cannot resume: {self.root}; see {ABANDONED}")
        self.state_path = inside(self.root, "controller/run.json")
        self.reload()

    def reload(self) -> None:
        if inside(self.root, RESET_INTENT).is_file():
            raise RunError(
                "run is being started over; prior checkpoints/handoffs are ineligible and this run may not be resumed"
            )
        self.state = preflight._read_json(str(self.state_path))
        # beta.78 upgrades beta.77 active runs in memory; the next accepted write
        # persists schema 2. No accepted work is discarded during migration.
        if self.state.get("schema_version") == 1:
            self.state.setdefault("source_prep", None)
            self.state.setdefault("stop_after", "complete")
            self.state.setdefault("stop_reached", False)
            self.state["schema_version"] = RUN_SCHEMA
        # EXP-002 normalizes the final EXP-001 drill vocabulary without inventing
        # semantic evidence. Unscoped legacy REINFORCE evidence remains visibly
        # unscoped until PASS 2 is rerun; it is never auto-upgraded to
        # ``scope: reinforces_core``.
        pass2 = self.state.get("pass2")
        if isinstance(pass2, dict):
            if "intensified_claims" in pass2 and "claim_regrounding" not in pass2:
                pass2["claim_regrounding"] = pass2.pop("intensified_claims")
            for resolution in pass2.get("flag_resolutions", []):
                if isinstance(resolution, dict):
                    if resolution.get("outcome") == "captured":
                        resolution["outcome"] = "collected"
                    resolution.setdefault("deferred_to", "")
            sweep = pass2.get("omission_sweep")
            if isinstance(sweep, dict):
                for finding in sweep.get("findings", []):
                    if isinstance(finding, dict) and finding.get("disposition") == "captured":
                        finding["disposition"] = "collected"
        exact(self.state, {"schema_version", "domain", "source", "phase", "unit_index", "plan", "pass1", "pass2", "reviewed_sha256", "live_hashes", "source_prep", "stop_after", "stop_reached"}, "run state")
        if type(self.state["schema_version"]) is not int or self.state["schema_version"] != RUN_SCHEMA:
            raise RunError("unsupported run state version")
        if self.state["stop_after"] not in STOP_AFTER or type(self.state["stop_reached"]) is not bool:
            raise RunError("invalid stop target state")
        manifest = read_run_manifest(self.root, required=False)
        if manifest is not None:
            if manifest["domain"] != self.state["domain"]:
                raise RunError("run manifest domain no longer matches controller state")
        else:
            legacy = self.root.relative_to(self.repo / "workspace/skill-staging")
            if legacy.parts[0] != self.state["domain"]:
                raise RunError("legacy run domain no longer matches its authorized workspace/package")
        if self.state["domain"] not in authorable_domains(self.repo):
            raise RunError("run domain no longer names an authorable package")
        if not isinstance(self.state["phase"], str) or self.state["phase"] not in PHASES or type(self.state["unit_index"]) is not int or self.state["unit_index"] < 0:
            raise RunError("invalid run phase or unit index")
        if self.state["plan"] is not None:
            record = preflight.parse_preflight(self.state["plan"])
            if record.domain != self.state["domain"] or self.state["unit_index"] > len(record.units):
                raise RunError("invalid saved unit plan")
            at_end = self.state["unit_index"] == len(record.units)
            if self.state["phase"] == "finished" and not at_end:
                raise RunError("saved finished phase does not match the unit plan")
            if at_end and self.state["phase"] not in {"closure_pass2", "closure_pass3", "closure_land", "finished"}:
                raise RunError("all source units are accepted to staging but the mandatory closure audit is not active")
            if not at_end and self.state["phase"] in {"closure_pass2", "closure_pass3", "closure_land", "finished"}:
                raise RunError("closure/finished phase cannot start before every source unit lands")
        elif self.state["phase"] not in {"load", "source_prep", "preflight"}:
            raise RunError("saved phase requires a unit plan")

    @contextmanager
    def locked(self, *, require_resolved: bool = True, action: str = "this operation"):
        """Exclusive mutation scope with one shared residue policy.

        Mutating commands enter through here: unresolved checkpoint residue is
        rejected BEFORE any side effect (present included), so a blocked command
        is provably side-effect-free. Recovery/repair paths pass
        require_resolved=False because they are the sanctioned resolvers.
        Every successful operation ends at a hard checkpoint before its result
        is released to the caller.
        """
        with operation_lock(self.root):
            # A competing caller may have loaded state before the preceding
            # operation finished. The lease owns the latest persisted state.
            self.reload()
            if require_resolved:
                residue = checkpoint_residue(self.root)
                if any(residue.values()):
                    raise ResidueBlockedError(action, residue)
            yield
            # Every successful operation ends at a hard checkpoint.
            if self.state_path.is_file():
                self.checkpoint()

    # ------------------------------------------------------------ checkpoints

    def staged_tree(self) -> dict[str, str]:
        """Every recoverable run artifact, by run-relative path.

        Prepared source, accepted source deltas, and accepted-unit history needed
        by the bounded correction path are first-class continuation state: a project
        archive must be sufficient to resume without chat memory or the original
        provider. Controller scratch that is cheaply reproducible (locks, audit
        renderings, raw deterministic extraction) is intentionally excluded.
        """
        files = {}
        for top in ("drafts", "recipes", "accepted", "prepared-source", "controller/unit-history"):
            base = self.root / top
            if base.is_dir():
                for path in sorted(base.rglob("*")):
                    if path.is_file():
                        files[path.relative_to(self.root).as_posix()] = digest(path)
        return files

    def checkpoint_manifest(self) -> dict | None:
        path = inside(self.root, f"{CHECKPOINT}/manifest.json")
        return preflight._read_json(str(path)) if path.is_file() else None

    def checkpoint(self) -> None:
        """Create and verify the complete last-known-good transaction.

        Authoritative controller state is saved before checkpoint promotion, so
        every promotion failure is reported as one typed degraded outcome:
        authoritative persisted, checkpoint not advanced, residue named, reason
        recorded durably in controller/checkpoint-failure.json, safe-continue
        verdict stated (EXP-003 Target A). The payload is stored as
        content-addressed blobs so a long card name can never reproduce the
        EXP-002 duplicated-nesting path blowout (Target D); the deterministic
        path-budget validation stays as the regression guard. Promotion is a
        rename transaction with postcondition judging, never a blind retry.
        """
        state_sha = digest(self.state_path)
        files = self.staged_tree()
        manifest = self.checkpoint_manifest()
        authoritative = {
            "state_sha256": state_sha,
            "phase": self.state.get("phase"),
            "unit_index": self.state.get("unit_index"),
            "last_accepted": self.last_accepted(),
        }
        previous: dict[str, Any] | None = None
        if manifest is not None:
            previous = {
                "state_sha256": manifest.get("state_sha256"),
                "phase": manifest.get("phase"),
                "schema_version": manifest.get("schema_version"),
            }
        if (
            manifest is None
            or manifest.get("schema_version") != CHECKPOINT_SCHEMA
            or manifest.get("state_sha256") != state_sha
            or manifest.get("files") != files
        ):
            folder = inside(self.root, CHECKPOINT)
            fresh = inside(self.root, f"{CHECKPOINT}.new")
            retired = inside(self.root, f"{CHECKPOINT}.old")
            failure_record = inside(self.root, CHECKPOINT_FAILURE)

            def write_failure(reason: str, *, error_type: str, restored: bool) -> None:
                atomic_write(failure_record, (json.dumps({
                    "schema_version": 2,
                    "outcome": "authoritative_state_persisted_checkpoint_not_advanced",
                    "recorded_at": now(),
                    "error_type": error_type,
                    "reason": reason,
                    "authoritative": authoritative,
                    "checkpoint": previous,
                    "residue": {**checkpoint_residue(self.root), "failure_record": True},
                    "previous_checkpoint_restored": restored,
                    "fresh_checkpoint_retained": fresh.exists(),
                    "checkpoint_present": folder.exists(),
                    "retired_checkpoint_present": retired.exists(),
                }, indent=2) + "\n").encode("utf-8"))

            def degraded(reason: str, *, error_type: str, restored: bool) -> CheckpointPromotionError:
                return CheckpointPromotionError(
                    "authoritative run state was persisted, but verified checkpoint promotion did not complete; "
                    "the command must not be reported as a clean success",
                    reason=reason,
                    state_sha256=state_sha,
                    authoritative=authoritative,
                    checkpoint=previous,
                    residue=checkpoint_residue(self.root),
                    previous_checkpoint_restored=restored,
                    fresh_checkpoint_retained=fresh.exists(),
                    safe_to_continue=(
                        "run repair-checkpoint to promote a verified checkpoint from the persisted authoritative "
                        "state; the authoritative run state itself is intact"
                    ),
                )

            if fresh.exists() or retired.exists():
                # locked() should have rejected this before any side effect;
                # reaching here means residue appeared inside this scope (for
                # example an interrupted promotion earlier in the same command).
                reason = (
                    "promotion residue from an interrupted transaction exists "
                    f"({json.dumps(checkpoint_residue(self.root), sort_keys=True)})"
                )
                if not failure_record.is_file():
                    write_failure(reason, error_type="ResiduePresent", restored=folder.exists())
                raise degraded(reason, error_type="ResiduePresent", restored=folder.exists())

            # 1. Pre-validate every destination before creating any residue, so
            #    a deterministic budget failure leaves zero scratch directories.
            try:
                validate_windows_path_budget(fresh / "controller" / "run.json", "checkpoint controller state")
                for sha in sorted(set(files.values())):
                    validate_windows_path_budget(fresh / "blobs" / sha, "checkpoint blob")
                for name in files:
                    if not inside(self.root, name).is_file():
                        raise RunError(f"staged file vanished before checkpoint: {name}")
            except RunError as exc:
                write_failure(str(exc), error_type=type(exc).__name__, restored=folder.exists())
                raise degraded(str(exc), error_type=type(exc).__name__, restored=folder.exists()) from exc

            # 2. Build the fresh checkpoint beside the live one.
            record: dict[str, Any] | None = None
            written: set[str] = set()
            old_moved = False
            try:
                fresh.mkdir(parents=True, exist_ok=True)
                state_copy = fresh / "controller" / "run.json"
                state_copy.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(self.state_path, state_copy)
                for name in sorted(files):
                    sha = files[name]
                    if sha in written:
                        continue
                    blob = fresh / "blobs" / sha
                    blob.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(inside(self.root, name), blob)
                    written.add(sha)
                record = {
                    "schema_version": CHECKPOINT_SCHEMA,
                    "layout": "content-addressed-blobs",
                    "created_at": now(),
                    "state_sha256": state_sha,
                    "phase": self.state["phase"],
                    "unit_index": self.state["unit_index"],
                    "last_accepted": self.last_accepted(),
                    "files": files,
                }
                atomic_write(fresh / "manifest.json", (json.dumps(record, indent=2) + "\n").encode("utf-8"))
                if digest(state_copy) != state_sha:
                    raise RunError("fresh checkpoint controller state failed verification")
                for sha in written:
                    if digest(fresh / "blobs" / sha) != sha:
                        raise RunError(f"fresh checkpoint blob failed verification: {sha[:12]}")
                if preflight._read_json(str(fresh / "manifest.json")) != record:
                    raise RunError("fresh checkpoint manifest failed verification")

                # 3. Promote by rename. Windows may report Access Denied even
                #    when the apparent operation completed; judge postconditions.
                if folder.exists():
                    folder.rename(retired)
                    old_moved = True
                fresh.rename(folder)
            except (OSError, RunError) as exc:
                committed = False
                try:
                    read_back = preflight._read_json(str(folder / "manifest.json")) if (folder / "manifest.json").is_file() else None
                    committed = bool(
                        record is not None
                        and read_back == record
                        and (folder / "controller/run.json").is_file()
                        and digest(folder / "controller/run.json") == state_sha
                        and all(
                            (folder / "blobs" / sha).is_file() and digest(folder / "blobs" / sha) == sha
                            for sha in set(files.values())
                        )
                    )
                except (OSError, ValueError, KeyError, TypeError):
                    committed = False
                if not committed:
                    restored = False
                    if old_moved and retired.exists() and not folder.exists():
                        try:
                            retired.rename(folder)
                            restored = True
                        except OSError:
                            restored = False
                    reason = str(exc)
                    write_failure(reason, error_type=type(exc).__name__, restored=restored)
                    raise degraded(reason, error_type=type(exc).__name__, restored=restored) from exc
            if retired.exists():
                shutil.rmtree(retired)
            failure_record.unlink(missing_ok=True)
        self.write_handoff()
        journal = inside(self.root, "controller/canonical-commit")
        current_manifest = self.checkpoint_manifest()
        if journal.is_dir() and current_manifest and current_manifest.get("state_sha256") == digest(self.state_path):
            shutil.rmtree(journal)

    def checkpoint_state_path(self) -> Path:
        return inside(self.root, f"{CHECKPOINT}/controller/run.json")

    def checkpoint_state_valid(self) -> bool:
        manifest = self.checkpoint_manifest()
        state = self.checkpoint_state_path()
        return bool(manifest and state.is_file() and digest(state) == manifest.get("state_sha256"))

    def recover(self, rollback_authoritative: bool = False) -> str:
        """Roll back to the last verified checkpoint, refusing silent rewinds.

        Recover is the destructive path (EXP-003 Target C). Authoritative run
        state that differs from the verified checkpoint was persisted after that
        checkpoint was built, so restoring would discard it; that now requires
        the explicit --rollback-authoritative intent and leaves an audit record.
        repair-checkpoint is the supported non-destructive alternative. Canonical
        commit journal repair keeps its existing semantics.
        """
        folder = inside(self.root, CHECKPOINT)
        retired = inside(self.root, f"{CHECKPOINT}.old")
        if not folder.exists() and retired.is_dir():
            candidate = retired / "manifest.json"
            state = retired / "controller/run.json"
            if not candidate.is_file() or not state.is_file():
                raise RunError("retired checkpoint residue is incomplete; refusing automatic recovery")
            record = preflight._read_json(str(candidate))
            if digest(state) != record.get("state_sha256"):
                raise RunError("retired checkpoint residue failed state verification")
            retired.rename(folder)
        manifest = self.checkpoint_manifest()
        if manifest is None or not self.checkpoint_state_valid():
            raise RunError("no complete recoverable checkpoint exists for this run")
        lock = inside(self.root, "controller/operation.lock")
        if lock.is_file():
            try:
                owner = preflight._read_json(str(lock))
                pid = int(owner.get("pid", -1))
            except Exception:
                pid = -1
            alive = False
            if pid > 0 and pid != os.getpid():
                try:
                    os.kill(pid, 0)
                    alive = True
                except (OSError, ProcessLookupError, PermissionError):
                    alive = False
            if alive:
                raise RunError(f"PASS operation pid {pid} still appears to be running; recovery would race it")
            evidence = inside(self.root, f"controller/action-history/recovered-lock-{uuid.uuid4().hex[:8]}.json")
            evidence.parent.mkdir(parents=True, exist_ok=True)
            atomic_write(evidence, lock.read_bytes())
            lock.unlink(missing_ok=True)
            # A hard kill inside land() can also leave the domain integration
            # lease behind. The owning per-run process is already proven dead.
            inside(self.repo, f"{RUN_STORE}/.landing-{self.domain}.lock").unlink(missing_ok=True)

        # A journal plus a checkpoint mismatch means canonicalization began but
        # the new controller transaction never became durable: restore before-
        # images. If the new checkpoint already matches run.json, the commit is
        # durable and recovery only needs to retire the verified journal.
        if self.canonical_journal_path().is_dir():
            if manifest.get("state_sha256") == digest(self.state_path):
                if not self.canonical_journal_after_valid():
                    raise RunError("canonical commit journal remains but live canon no longer matches its durable after-state")
                shutil.rmtree(self.canonical_journal_path())
            else:
                self.rollback_canonical_journal()

        # Non-destructive guard: authoritative state that differs from the
        # verified checkpoint was persisted AFTER that checkpoint, so the
        # restore below would silently rewind it (EXP-003 Target C).
        authoritative_sha = digest(self.state_path)
        if authoritative_sha != manifest["state_sha256"]:
            if not rollback_authoritative:
                raise RunError(
                    "refusing destructive recovery: authoritative run state "
                    f"(phase {self.state.get('phase')}, state sha256 {authoritative_sha[:12]}) was persisted after the "
                    f"last verified checkpoint (phase {manifest.get('phase')}, state sha256 {str(manifest.get('state_sha256'))[:12]}) "
                    "and a restore would silently discard it; run repair-checkpoint to keep the current state "
                    "(non-destructive), or re-run recover with --rollback-authoritative to discard it explicitly"
                )
            evidence = inside(self.root, f"controller/action-history/rollback-authoritative-{uuid.uuid4().hex[:8]}.json")
            evidence.parent.mkdir(parents=True, exist_ok=True)
            atomic_write(evidence, (json.dumps({
                "schema_version": 1,
                "recorded_at": now(),
                "intent": "explicit recover --rollback-authoritative",
                "discarded_authoritative_sha256": authoritative_sha,
                "discarded_authoritative_phase": self.state.get("phase"),
                "restored_checkpoint_sha256": manifest.get("state_sha256"),
                "restored_checkpoint_phase": manifest.get("phase"),
            }, indent=2) + "\n").encode("utf-8"))

        saved = manifest["files"]
        for top in ("drafts", "recipes", "accepted", "prepared-source", "controller/unit-history"):
            base = self.root / top
            if base.exists():
                shutil.rmtree(base)
        for name, sha in saved.items():
            source = inside(self.root, f"{CHECKPOINT}/blobs/{sha}")
            if not source.is_file() or digest(source) != sha:
                raise RunError(f"checkpoint blob is damaged: {name} ({sha[:12]})")
            target = inside(self.root, name)
            target.parent.mkdir(parents=True, exist_ok=True)
            atomic_write(target, source.read_bytes())
        saved_state = self.checkpoint_state_path()
        atomic_write(self.state_path, saved_state.read_bytes())
        self.reload()
        if self.staged_tree() != saved or digest(self.state_path) != manifest["state_sha256"]:
            raise RunError("recovery verification failed")
        self.write_handoff()
        fresh = inside(self.root, f"{CHECKPOINT}.new")
        if fresh.exists():
            shutil.rmtree(fresh)
        retired = inside(self.root, f"{CHECKPOINT}.old")
        if retired.exists():
            shutil.rmtree(retired)
        inside(self.root, "controller/checkpoint-failure.json").unlink(missing_ok=True)
        return f"RECOVERED: restored verified checkpoint at {manifest['last_accepted'] or 'run start'}; resume from {self.state['phase']}"

    def repair_checkpoint(self) -> str:
        """Establish a verified checkpoint from the current authoritative state.

        Non-destructive (EXP-003 Target C): never rolls back the authoritative
        run state, drafts, or accepted tree — it only clears unresolved promotion
        residue (.new/.old scratch plus the failure record) and rebuilds the
        checkpoint from what is authoritative right now. Canonical commit
        journals are recover's domain and are refused here.
        """
        if self.canonical_journal_path().is_dir():
            raise RunError(
                "a canonical commit journal is present; run recover (which verifies the after-state or rolls it "
                "back) before repair-checkpoint"
            )
        fresh = inside(self.root, f"{CHECKPOINT}.new")
        retired = inside(self.root, f"{CHECKPOINT}.old")
        if fresh.exists():
            shutil.rmtree(fresh)
        if retired.exists():
            shutil.rmtree(retired)
        # Evidence is dropped only after residue is cleared; checkpoint() below
        # records fresh failure evidence immediately if the rebuild fails.
        inside(self.root, CHECKPOINT_FAILURE).unlink(missing_ok=True)
        self.checkpoint()
        residue_after = checkpoint_residue(self.root)
        if any(residue_after.values()):
            raise RunError(
                f"checkpoint repair failed; residue remains: {json.dumps(residue_after, sort_keys=True)}"
            )
        return (
            "REPAIRED: verified checkpoint rebuilt from authoritative state "
            f"(state sha256 {digest(self.state_path)[:12]}, phase {self.state.get('phase')}); "
            "no data was rolled back"
        )

    def checkpoint_drift(self) -> list[str] | None:
        """Draft paths that differ from the checkpoint, or None when there is no current checkpoint."""
        manifest = self.checkpoint_manifest()
        if manifest is None or manifest.get("state_sha256") != digest(self.state_path):
            return None
        saved, current = manifest["files"], self.staged_tree()
        return sorted(name for name in set(saved) | set(current) if saved.get(name) != current.get(name))

    def rollback(self) -> str:
        """Restore the drafts to the last checkpoint so the interrupted phase starts over."""
        phase = self.state["phase"]
        if phase not in {"preflight", "pass1", "checkpoint", "pass2", "pass3", "closure_pass2", "closure_pass3"}:
            raise RunError(f"rollback restarts an interrupted substantive phase; phase {phase} has none to restart")
        manifest = self.checkpoint_manifest()
        if manifest is None:
            raise RunError("this run has no checkpoint yet; it is created by the next accepted step")
        if manifest.get("state_sha256") != digest(self.state_path):
            raise RunError("run.json changed without a checkpoint; the saved snapshot does not describe the current state")
        saved = manifest["files"]
        current = self.staged_tree()
        removed = [name for name in current if name not in saved]
        restored = [name for name, sha in saved.items() if current.get(name) != sha]
        for name in removed:
            inside(self.root, name).unlink()
        for name in restored:
            source = inside(self.root, f"{CHECKPOINT}/blobs/{saved[name]}")
            if not source.is_file() or digest(source) != saved[name]:
                raise RunError(f"checkpoint blob is damaged: {name}")
            target = inside(self.root, name)
            target.parent.mkdir(parents=True, exist_ok=True)
            atomic_write(target, source.read_bytes())
        for top in ("drafts", "recipes"):
            base = self.root / top
            if base.is_dir():
                for directory in sorted((p for p in base.rglob("*") if p.is_dir()), key=lambda p: len(p.parts), reverse=True):
                    if not any(directory.iterdir()):
                        directory.rmdir()
        if self.staged_tree() != saved:
            raise RunError("rollback verification failed; the drafts do not match the checkpoint")
        unit = self.unit()["unit_id"].upper() if phase != "preflight" else "the source"
        return (f"ROLLED BACK to the end of {manifest['last_accepted'] or 'the run start'}: "
                f"{len(restored)} file(s) restored, {len(removed)} removed. Redo {unit} {phase} from its beginning.")

    def write_handoff(self) -> None:
        """Rewrite HANDOFF.md from controller state: the last safe endpoint, never a model's memory."""
        path = inside(self.root, "HANDOFF.md")
        if path.is_file():
            existing = path.read_text(encoding="utf-8")
            if HANDOFF_MARK not in existing:
                # A model wrote its own handoff here. Keep it as notes rather than lose it.
                notes = inside(self.root, "NOTES.md")
                with notes.open("a", encoding="utf-8") as handle:
                    handle.write(f"\n\n## Preserved from a hand-written HANDOFF.md ({now()})\n\n{existing}")
        rel = self.root.relative_to(self.repo).as_posix()
        phase = self.state["phase"]
        plan = self.state["plan"]
        units = plan["units"] if plan else []
        index = self.state["unit_index"]
        manifest = self.checkpoint_manifest() or {"files": {}}
        try:
            action = self.brief().get("authorized_action", "")
        except (RunError, KeyError) as exc:
            action = f"(controller could not render the brief: {exc})"
        lines = [
            f"# PASS handoff: {plan['title'] if plan else Path(self.state['source']).name}",
            "",
            HANDOFF_MARK,
            "",
            f"Last safe endpoint: **{self.last_accepted() or 'run started'}** (checkpoint {manifest.get('created_at', '-')}).",
            "",
            f"- Run: `{rel}` (domain `{self.domain}`)",
            f"- Source: `{Path(self.state['source']).name}`",
        ]
        lines += [
            f"- Controller schema: `{self.state['schema_version']}`; PASS version: `{(self.repo / 'VERSION').read_text(encoding='utf-8').strip() if (self.repo / 'VERSION').is_file() else 'unknown'}`",
            f"- Checkpoint state SHA-256: `{manifest.get('state_sha256', '-')}`",
            f"- Stop target: `{self.state.get('stop_after', 'complete')}`; reached: `{str(self.state.get('stop_reached', False)).lower()}`",
        ]
        prep = self.state.get("source_prep")
        if isinstance(prep, dict):
            lines += [f"- Source prep: `{prep.get('status', '-')}` — package `{prep.get('package', '-')}` — {prep.get('segments', 0)} segment(s)"]
        if self.accepted_root().is_dir():
            lines += [f"- Accepted staged delta: {len(self.accepted_file_hashes())} file(s), {len(self.accepted_removals())} removal(s)"]
        if units:
            done = ", ".join(u["unit_id"].upper() for u in units[:index]) or "none"
            lines += [f"- Units: {len(units)}; accepted to staging: {done}"]
        if phase not in {"load", "source_prep", "preflight", "preflight_accept", "finished"}:
            unit = self.unit()
            lines += [f"- Current: {unit['unit_id'].upper()} at **{phase}** — {unit['material']}",
                      f"- Unit scope: {unit['locator']}"]
        else:
            lines += [f"- Phase: **{phase}**"]
        recoverable = list(manifest.get("files", {}))
        if len(recoverable) <= 20:
            recoverable_lines = [f"- `{name}`" for name in recoverable] or ["- none"]
        else:
            grouped: dict[str, int] = {}
            for name in recoverable:
                parts = PurePosixPath(name).parts
                key = parts[0] if parts else name
                if key == "prepared-source" and len(parts) > 1:
                    key = "/".join(parts[:2])
                grouped[key] = grouped.get(key, 0) + 1
            recoverable_lines = []
            for key, count in sorted(grouped.items()):
                suffix = "/" if count > 1 or key.endswith(("assets", "pages", "units", "accepted", "drafts", "recipes")) else ""
                recoverable_lines.append(f"- `{key}{suffix}` — {count} verified file(s)")
            recoverable_lines.append(f"- Complete per-file hashes: `controller/checkpoint/manifest.json` ({len(recoverable)} files total)")
        lines += [
            "",
            "## Pick up here",
            "",
            f"1. Run `python PASS/pass.py resume --run {rel}`. It verifies source/prepared input, controller state, staged artifacts and locks",
            "   and names the one next action. It outranks this file.",
            f"2. If `resume` reports an interrupted committed operation, run `python PASS/pass.py recover --run {rel}`. Recovery restores",
            "   the complete verified controller/staging checkpoint and rolls back any interrupted canonical-close transaction.",
            f"3. If only unaccepted working files drifted during the current phase, use `python PASS/pass.py rollback --run {rel}`",
            f"   to return to the end of {self.last_accepted() or 'the run start'} and redo {phase} in full.",
            f"4. Next action at this checkpoint: {action}",
            "",
            "## Recoverable files at this checkpoint",
            "",
            *recoverable_lines,
            "",
            "## Do not",
            "",
            "- Do not read `controller/run.json`; `resume`, `status` and `template` give what you need.",
            "- Do not rerun completed Source Prep/preflight, and do not edit this file: the controller rewrites it.",
            "- Put corrections and traps worth keeping in `NOTES.md` (model-written, not authoritative).",
            "",
        ]
        atomic_write(path, "\n".join(lines).encode("utf-8"))

    def save(self) -> None:
        if inside(self.root, RESET_INTENT).is_file():
            raise RunError(
                "run has an authoritative start-over intent; refusing to resurrect prior controller state"
            )
        atomic_write(self.state_path, (json.dumps(self.state, indent=2) + "\n").encode())
        sync_run_manifest(self.repo, self.root, self.state)

    def source_identity_path(self) -> Path:
        return inside(self.root, "controller/source-identity.json")

    def capture_source_identity(self) -> dict:
        path = Path(self.state["source"]).resolve()
        if not path.is_file():
            raise RunError(f"source does not exist: {path}")
        marker = {
            "schema_version": 1,
            "name": path.name,
            "size": path.stat().st_size,
            "sha256": digest(path),
        }
        atomic_write(self.source_identity_path(), (json.dumps(marker, indent=2) + "\n").encode())
        return marker

    def source_identity(self) -> dict:
        path = self.source_identity_path()
        if not path.is_file():
            raise RunError("source identity marker is missing; complete the LOAD gate before unattended/source-resume operations")
        marker = preflight._read_json(str(path))
        exact(marker, {"schema_version", "name", "size", "sha256"}, "source identity")
        if type(marker["schema_version"]) is not int or marker["schema_version"] != 1:
            raise RunError("unsupported source identity marker")
        string(marker["name"], "source identity name")
        if type(marker["size"]) is not int or marker["size"] < 0:
            raise RunError("invalid source identity size")
        sha = string(marker["sha256"], "source identity sha256")
        if not re.fullmatch(r"[0-9a-f]{64}", sha):
            raise RunError("invalid source identity sha256")
        return marker

    def source_file(self, required: bool = True) -> Path | None:
        path = Path(self.state["source"]).resolve()
        if not path.is_file():
            if required:
                raise RunError(
                    "bound source file is unavailable; rebind the same source by SHA-256 with "
                    "`python PASS/source.py rebind-source --run <run> --source <path>`"
                )
            return None
        identity = self.source_identity()
        if path.stat().st_size != identity["size"] or digest(path) != identity["sha256"]:
            raise RunError("bound source bytes no longer match the run's source identity")
        return path

    def prepared_source_valid(self) -> bool:
        prep = self.state.get("source_prep")
        if not isinstance(prep, dict) or prep.get("status") != "verified":
            return False
        try:
            from .pass_source_prep import verify
            manifest = verify(self)
        except (OSError, RunError, preflight.PreflightError):
            return False
        return manifest.get("package_sha256") == prep.get("package_sha256")

    def source_or_prepared(self) -> str:
        """Verify a usable source authority and return its mode.

        Once deterministic Source Prep is verified, a continuation archive may
        omit the original raw source: prepared-source is sufficient for unit
        reading while source identity remains bound to the archival bytes.
        """
        try:
            self.source_file(required=True)
            return "raw-source"
        except RunError:
            if self.prepared_source_valid():
                return "prepared-source"
            raise

    def rebind_source(self, source: Path) -> str:
        source = source.resolve()
        if not source.is_file():
            raise RunError(f"replacement source does not exist: {source}")
        identity = self.source_identity()
        if source.stat().st_size != identity["size"] or digest(source) != identity["sha256"]:
            raise RunError("replacement source does not match the original source SHA-256 and size")
        self.state["source"] = str(source)
        self.save()
        return f"SOURCE REBOUND: {source.name} — identity verified"

    def unattended_authorization_path(self) -> Path:
        return inside(self.root, "controller/unattended-authorization.json")

    def unattended_action_path(self) -> Path:
        return inside(self.root, "controller/next-action.json")

    def require_unattended_action(self, phase: str) -> None:
        """Require a source-runner-issued action lease for substantive unattended work.

        This makes the source runner the authoritative dispatcher whenever an
        unattended authorization is active. A host may not jump directly into
        PASS phases from prose memory; it must first obtain the exact current
        action from ``PASS/source.py drive``.
        """
        if not self.unattended_authorization_path().is_file():
            return
        # LOAD precedes unattended authorization. Deterministic gates such as
        # preflight acceptance and landing are consumed by source.py itself.
        if phase not in {"preflight", "pass1", "checkpoint", "pass2", "pass3", "closure_pass2", "closure_pass3"}:
            return
        path = self.unattended_action_path()
        if not path.is_file():
            raise RunError(
                "unattended source run has no issued action lease; run "
                "`python PASS/source.py drive --run <run>` and execute only the returned action"
            )
        marker = preflight._read_json(str(path))
        exact(
            marker,
            {"schema_version", "action_id", "phase", "unit_index", "unit_id", "state_sha256", "instruction"},
            "unattended action lease",
        )
        if type(marker["schema_version"]) is not int or marker["schema_version"] != 1:
            raise RunError("unsupported unattended action lease")
        if marker["phase"] != phase or marker["phase"] != self.state["phase"]:
            raise RunError("unattended action lease does not match the current PASS phase; rerun source.py drive")
        if type(marker["unit_index"]) is not int or marker["unit_index"] != self.state["unit_index"]:
            raise RunError("unattended action lease belongs to another unit; rerun source.py drive")
        unit_id = None if phase == "preflight" else self.unit()["unit_id"]
        if marker["unit_id"] != unit_id:
            raise RunError("unattended action lease unit identity mismatch")
        if marker["state_sha256"] != digest(self.state_path):
            raise RunError("unattended run state changed after the action was issued; rerun source.py drive")
        action_id = string(marker["action_id"], "unattended action id")
        if not re.fullmatch(r"[0-9a-f]{64}", action_id):
            raise RunError("invalid unattended action id")
        string(marker["instruction"], "unattended action instruction")

    def consume_unattended_action(self, phase: str, previous_unit_index: int) -> None:
        """Archive the lease that authorized a successful substantive transition."""
        path = self.unattended_action_path()
        if not path.is_file():
            return
        marker = preflight._read_json(str(path))
        if marker.get("phase") != phase or marker.get("unit_index") != previous_unit_index:
            return
        history = inside(self.root, "controller/action-history")
        history.mkdir(parents=True, exist_ok=True)
        record = dict(marker)
        record.update({"result_phase": self.state["phase"], "result_unit_index": self.state["unit_index"], "completed": True})
        atomic_write(inside(history, f"{marker['action_id']}.json"), (json.dumps(record, indent=2) + "\n").encode("utf-8"))
        path.unlink(missing_ok=True)

    def unattended_authorization(self, required: bool = False) -> dict | None:
        path = self.unattended_authorization_path()
        if not path.is_file():
            if required:
                raise RunError("no active unattended source authorization is recorded for this run")
            return None
        marker = preflight._read_json(str(path))
        exact(
            marker,
            {"schema_version", "mode", "scope", "authorized_by", "domain", "source_sha256", "reason"},
            "unattended authorization",
        )
        if type(marker["schema_version"]) is not int or marker["schema_version"] != 1:
            raise RunError("unsupported unattended authorization marker")
        if marker["mode"] != "unattended" or marker["scope"] != "source_completion" or marker["authorized_by"] != "user":
            raise RunError("unattended authorization must be user-authorized and scoped to this source through completion")
        if marker["domain"] != self.domain:
            raise RunError("unattended authorization belongs to another domain")
        identity = self.source_identity()
        if marker["source_sha256"] != identity["sha256"]:
            raise RunError("unattended authorization belongs to another source")
        string(marker["reason"], "unattended authorization reason")
        # Raw source may be absent from a continuation archive once a verified
        # prepared package exists; either authority is acceptable.
        self.source_or_prepared()
        return marker

    def last_accepted(self) -> str | None:
        phase = self.state["phase"]
        units = [u["unit_id"].upper() for u in self.state["plan"]["units"]] if self.state["plan"] else []
        index = self.state["unit_index"]
        if phase == "load":
            return None
        if phase == "source_prep":
            prep = self.state.get("source_prep")
            return "source prep package prepared; verification pending" if isinstance(prep, dict) and prep.get("status") == "prepared" else "LOAD"
        if phase == "preflight":
            return "source prep verified" if self.state.get("source_prep") else "LOAD"
        if phase == "preflight_accept":
            return "preflight validated; acceptance pending"
        if phase == "finished":
            return "source closure canonicalized"
        if phase == "closure_pass2":
            return f"{units[-1]} accepted to staging"
        if phase == "closure_pass3":
            return "closure PASS 2"
        if phase == "closure_land":
            return "closure PASS 3"
        if phase == "pass1":
            return f"{units[index - 1]} accepted to staging" if index else "preflight accepted"
        if phase == "pass2" and self.state["pass1"]["questions"]:
            return f"{units[index]} checkpoint"
        return f"{units[index]} " + {"checkpoint": "PASS 1", "pass2": "PASS 1", "pass3": "PASS 2", "land": "PASS 3"}[phase]

    def pickup(self, source: Path | None = None) -> dict:
        """Verify persisted state and return the one legal next action. Never writes.

        Everything here derives from controller files; a model's memory of the
        run is not consulted, and a failed check leaves every file untouched.
        """
        phase = self.state["phase"]
        blockers: list[str] = []
        lock = inside(self.root, "controller/operation.lock")
        manifest = self.checkpoint_manifest()
        checkpoint_mismatch = bool(
            manifest and self.checkpoint_state_valid() and manifest.get("state_sha256") != digest(self.state_path)
        )
        canonical_journal = self.canonical_journal_path().is_dir()
        if checkpoint_mismatch or canonical_journal:
            blockers.append(
                f"an interrupted committed operation was detected. Run `python PASS/pass.py recover --run {self.root}`; "
                "recovery restores the last verified controller/staging checkpoint and rolls back any interrupted canonical close."
            )
        elif lock.exists():
            held = lock.read_text(encoding="utf-8").strip() or "no owner recorded"
            blockers.append(
                f"a previous PASS operation did not finish ({held}). If no PASS process is still running, run "
                f"`python PASS/pass.py recover --run {self.root}` rather than deleting state by hand."
            )

        identity = self.source_identity() if self.source_identity_path().is_file() else None
        if identity is None:
            source_state = "pending LOAD" if Path(self.state["source"]).is_file() else "missing"
            if source_state == "missing":
                blockers.append(f"the bound source is missing: {self.state['source']}; LOAD has not run, so abandon this run and start again from the new path")
        else:
            try:
                self.source_file(required=True)
                source_state = "unchanged"
            except RunError:
                if self.prepared_source_valid():
                    source_state = "prepared-package"
                else:
                    bound = Path(self.state["source"])
                    source_state = "moved" if not bound.is_file() else "changed"
                    candidate = source.resolve() if source else None
                    if candidate and candidate.is_file() and candidate.stat().st_size == identity["size"] and digest(candidate) == identity["sha256"]:
                        blockers.append(f"the source moved; the given file has identical bytes. Run `python PASS/source.py rebind-source --run {self.root} --source \"{candidate}\"`, then resume again")
                    elif source_state == "moved":
                        blockers.append(f"the bound source is missing and no verified prepared package is available: {bound}. Rebind identical bytes or recover the prepared package from a continuation archive")
                    else:
                        blockers.append("the bound source file's bytes changed since LOAD and no verified prepared package is available; restore the original bytes or abandon the run")

        drafts = "none"
        if phase == "pass1":
            drafts = "unaccepted scratch from an interrupted PASS 1" if any(p.is_file() for p in (self.root / "drafts").rglob("*")) else "none"
        elif phase in {"checkpoint", "pass2"}:
            drafts = "PASS 1 working drafts (not hash-bound until PASS 3)"
        elif phase == "closure_pass2":
            drafts = "source-closure synthesis/reconciliation drafts (not hash-bound until closure PASS 3)"
        elif phase in {"pass3", "land", "closure_pass3", "closure_land"}:
            try:
                if not self.live_unchanged():
                    rewind_phase = "closure_pass2" if phase in {"closure_pass3", "closure_land"} else "pass2"
                    blockers.append(f"live library cards changed after PASS 2; run `python PASS/pass.py rewind --run {self.root} --phase {rewind_phase}`, reconcile, then repeat PASS 3")
                if phase in {"land", "closure_land"}:
                    if self.staged_hashes() != self.state["reviewed_sha256"]:
                        drafts = "changed after PASS 3"
                        rewind_phase = "closure_pass3" if phase == "closure_land" else "pass3"
                        blockers.append(f"staged files changed after PASS 3; run `python PASS/pass.py rewind --run {self.root} --phase {rewind_phase}` and rescan")
                    else:
                        drafts = "verified against PASS 3 hashes"
                else:
                    drafts = "staged by PASS 2; PASS 3 review pending"
            except OSError as exc:
                drafts = "missing"
                blockers.append(f"a staged file is missing ({exc}); rewind to pass2 and restage")

        drift = self.checkpoint_drift() if phase in {"preflight", "pass1", "checkpoint", "pass2", "pass3", "closure_pass2", "closure_pass3"} else None
        rollback_hint = None
        if drift:
            drafts = f"{len(drift)} file(s) changed since the checkpoint at the end of {self.last_accepted() or 'the run start'}"
            rollback_hint = (
                f"Drafts changed after the last accepted step. If this session is continuing after an interruption, run "
                f"`python PASS/pass.py rollback --run {self.root}` to restore the checkpoint, then redo {phase} from its "
                "beginning; never finish a phase another session left half done."
            )
        try:
            authorization = self.unattended_authorization(required=False) if identity and source_state in {"unchanged", "prepared-package"} else None
        except RunError as exc:
            authorization = None
            blockers.append(f"unattended authorization is invalid: {exc}")
        lease = None
        if authorization and phase in {"preflight", "pass1", "checkpoint", "pass2", "pass3", "closure_pass2", "closure_pass3"}:
            path = self.unattended_action_path()
            if not path.is_file():
                lease = "none issued; source.py drive will issue one"
            else:
                held = preflight._read_json(str(path))
                current = held.get("phase") == phase and held.get("unit_index") == self.state["unit_index"] and held.get("state_sha256") == digest(self.state_path)
                lease = "current; source.py drive returns it unchanged" if current else "stale; source.py drive will archive it and issue a new one"

        units = self.state["plan"]["units"] if self.state["plan"] else []
        index = self.state["unit_index"]
        active = self.unit()["unit_id"].upper() if phase not in {"load", "source_prep", "preflight", "preflight_accept", "finished"} else None
        try:
            brief = self.brief()
        except RunError as exc:
            brief = None
            if not blockers:
                blockers.append(str(exc))
        if blockers:
            next_action = blockers[0]
        elif rollback_hint:
            next_action = rollback_hint
        elif self.state.get("stop_reached"):
            next_action = brief["authorized_action"]
        elif authorization and phase != "load":
            next_action = f"Run `python PASS/source.py drive --run {self.root}` and execute only the action it returns."
        else:
            next_action = brief["authorized_action"]
        result = {
            "outcome": "blocked" if blockers else "resume",
            "run": str(self.root),
            "domain": self.domain,
            "source": self.state["source"],
            "title": self.state["plan"]["title"] if self.state["plan"] else None,
            "source_identity": source_state,
            "mode": "unattended" if authorization else "interactive",
            "unit_count": len(units) if units else None,
            "units_completed": [u["unit_id"].upper() for u in units[:index]],
            "current_unit": active,
            "phase": phase,
            "last_accepted": self.last_accepted(),
            "drafts": drafts,
            "changed_since_checkpoint": drift or [],
            "blockers": blockers,
            "next_action": next_action,
            "context": {
                "safe_to_discard": not lock.exists() and not checkpoint_mismatch and not canonical_journal,
                "note": "Every accepted step is persisted. Work inside an unaccepted phase is not: after a context loss, "
                        "perform the current phase again in full; never claim a read that this session did not do.",
            },
            "brief": brief,
        }
        if lease:
            result["action_lease"] = lease
        done = ", ".join(result["units_completed"]) or "none"
        result["statement"] = (
            f"Existing incomplete PASS run: {self.root.name}. Units: {result['unit_count'] or 'not planned yet'}; "
            f"completed: {done}; current: {active or '-'} / {phase}; last accepted: {result['last_accepted'] or 'nothing'}; "
            f"source identity: {source_state}; drafts: {drafts}. NEXT ACTION: {next_action}"
        )
        return result

    @property
    def domain(self) -> str:
        return self.state["domain"]

    def unit(self) -> dict:
        plan = self.state["plan"]
        if plan is None:
            raise RunError("no active unit")
        if self.state["phase"] in {"closure_pass2", "closure_pass3", "closure_land"}:
            return {
                "unit_id": "closure",
                "material": "Source-wide closure synthesis and reconciliation audit",
                "locator": "accepted source corpus plus the cumulative staged working library",
                "overlap_object_ids": [],
                "card_potential": "mixed",
            }
        if self.state["unit_index"] >= len(plan["units"]):
            raise RunError("no active unit")
        return plan["units"][self.state["unit_index"]]

    def language_policy(self) -> dict | None:
        """Return the accepted programming-language modernization policy, if any."""
        plan = self.state.get("plan")
        if self.domain != "software-engineering" or not isinstance(plan, dict):
            return None
        policy = plan.get("language_policy")
        if not isinstance(policy, dict) or policy.get("classification") != "programming-language":
            return None
        return policy

    def language_modernization_required(self) -> bool:
        policy = self.language_policy()
        return bool(policy and policy.get("modernization_required") is True)

    def semantic_checks(self) -> tuple[str, ...]:
        return SEMANTIC_CHECKS + (LANGUAGE_SEMANTIC_CHECKS if self.language_modernization_required() else ())

    def core_card_changes(self, data: dict) -> list[str]:
        """Staged Software Engineering core cards touched by one PASS 2 delta."""
        result: list[str] = []
        for name in array(data.get("changes", []), "changes"):
            if not isinstance(name, str):
                continue
            try:
                target = self.target(name)
            except RunError:
                continue
            if (
                target.startswith("library/software-engineering/core/")
                and target.endswith(".md")
                and not target.endswith("/INDEX.md")
            ):
                result.append(name)
        return sorted(set(result))

    def stage_contract(self) -> dict:
        phase = self.state["phase"]
        preflight_validated = self.state["plan"] is not None
        preflight_accepted = preflight_validated and phase not in {"load", "preflight", "preflight_accept"}
        contract = {
            "source_preflight": {
                "scope": "source",
                "frequency": "once",
                "validated": preflight_validated,
                "accepted": preflight_accepted,
                "complete": preflight_accepted,
                "repeat_for_each_unit": False,
                "unit_preflight_allowed": False,
                "replan_is_preflight": False,
            }
        }
        policy = self.language_policy()
        if policy is not None:
            contract["programming_language_policy"] = {
                "language": policy["language"],
                "target_version": policy["target_version"],
                "target_basis": policy["target_basis"],
                "modernization_required": True,
                "source_rule": (
                    "The prepared/source text remains historical evidence. Every version-sensitive instructional claim must be "
                    "reviewed against the configured current target version before it can become current library guidance."
                ),
                "core_rule": (
                    "Read, create and refine software-engineering/core as language-agnostic decisions. Put syntax, idioms, "
                    "runtime mechanics and necessary language exceptions in the language module, not in the Core rule."
                ),
            }
        unattended = self.unattended_authorization(required=False)
        if phase == "preflight_accept":
            if unattended:
                contract["source_preflight"]["instruction"] = (
                    "The source-wide preflight is validated and this source has active unattended authorization. "
                    "Use the source runner to archive the complete packet and consume the bounded authorization before PASS 1."
                )
                contract["preflight_presentation"] = {
                    "required": True,
                    "renderer": "PASS/source.py advance",
                    "verbatim_audit_copy": True,
                    "chat_display_required": False,
                    "acceptance_command": "source.py advance",
                    "basis": "unattended authorization",
                    "instruction": (
                        "The packet must still be rendered, hash-bound and saved to the run audit. Do not skip preflight. "
                        "No chat reproduction is required while unattended authorization is active."
                    ),
                }
            else:
                contract["source_preflight"]["instruction"] = (
                    "The source-wide preflight is validated but not accepted. Run present, reproduce the complete preflight packet, "
                    "and obtain explicit user confirmation of the stated subject and provisional source-wide plan before PASS 1."
                )
                contract["preflight_presentation"] = {
                    "required": True,
                    "renderer": "present",
                    "verbatim": True,
                    "summary_allowed": False,
                    "acceptance_command": "accept-preflight",
                    "basis": "user confirmation",
                    "instruction": (
                        "Do not infer confirmation from the original request to run PASS. Present the complete packet, wait for an "
                        "explicit user confirmation or correction, then submit a hash-bound preflight acceptance decision."
                    ),
                }
        elif preflight_accepted and phase not in {"finished"}:
            contract["source_preflight"]["instruction"] = (
                "The source-wide preflight is already accepted. Do not run or simulate another preflight for the active unit; "
                "use replan only for evidence-backed amendments to remaining instructional boundaries before PASS 1 is accepted."
            )
        elif phase == "preflight":
            contract["source_preflight"]["instruction"] = (
                "Perform the one source-wide structural preflight. This preflight establishes the provisional plan for every unit."
            )
        if phase in {"land", "closure_land"}:
            if unattended and not self.state["pass2"]["approval_required"]:
                contract["landing_presentation"] = {
                    "required": True,
                    "renderer": "PASS/source.py advance",
                    "verbatim_audit_copy": True,
                    "chat_display_required": False,
                    "basis": "unattended authorization",
                    "instruction": (
                        "The source runner must render, hash-bind and archive the complete packet before auto-landing. "
                        "Routine landing may consume the bounded unattended authorization because approval_required is false."
                    ),
                }
            elif unattended and self.state["pass2"]["approval_required"]:
                contract["landing_presentation"] = {
                    "required": True,
                    "renderer": "PASS/source.py advance",
                    "verbatim_audit_copy": True,
                    "chat_display_required": False,
                    "human_required": True,
                    "instruction": (
                        "Archive the packet and stop. This delta is marked approval_required; unattended authorization may not consume it."
                    ),
                }
            else:
                contract["landing_presentation"] = {
                    "required": True,
                    "renderer": "present",
                    "verbatim": True,
                    "summary_allowed": False,
                    "instruction": (
                        "Run the present command and reproduce its complete packet before recording a landing decision. "
                        "Do not omit empty buckets, reasons, taxonomy actions, changes, removals, or approval status."
                    ),
                }
        return contract

    def brief(self) -> dict:
        phase = self.state["phase"]
        result = {
            "run": str(self.root),
            "domain": self.domain,
            "phase": phase,
            "stage_contract": self.stage_contract(),
        }
        manifest = read_run_manifest(self.root, required=False)
        if manifest is not None:
            result["run_id"] = manifest["run_id"]
            result["genre"] = manifest["genre"]
            result["display_label"] = manifest["display_label"]
        sandbox = sandbox_manifest(self.repo)
        if sandbox is not None:
            result["sandbox"] = sandbox
        transition = self.latest_transition_report()
        if transition is not None:
            result["last_transition_report"] = transition
        prep_state = self.state.get("source_prep")
        if isinstance(prep_state, dict):
            result["source_prep_integrity"] = prep_state.get("integrity")
            result["source_prep_package_sha256"] = prep_state.get("package_sha256")
        if self.state.get("stop_reached"):
            result["stop_target"] = self.state.get("stop_after")
            result["authorized_action"] = (
                f"STOP TARGET REACHED ({self.state.get('stop_after')}). Preserve the checkpoint/archive; do not advance until the user "
                f"requests continuation. Then run `python PASS/pass.py continue-run --run {self.root}`."
            )
        elif phase == "load":
            result["required_documents"] = required_documents(self.repo)
            result["authorized_action"] = "Read canonical instructions only; submit the load record before source access."
        elif phase == "source_prep":
            result["source"] = self.state["source"]
            result["prepared_source"] = str(inside(self.root, "prepared-source"))
            result["authorized_action"] = (
                f"Prepare the source deterministically with `python PASS/source_prep.py prepare --run {self.root}`, inspect any low-text "
                f"segments as needed, then run `python PASS/source_prep.py finalize --run {self.root}`. No PASS unit ingestion is authorized."
            )
        elif phase == "preflight":
            result["source"] = self.state["source"]
            result["authorized_action"] = (
                "Run the one source-wide structural preflight: establish subject, TOC/page map, text quality and the provisional "
                "unit plan for the complete source. No substantive ingestion or library writes."
            )
        elif phase == "preflight_accept":
            result["source"] = self.state["source"]
            result["subject"] = self.state["plan"]["subject"]
            if self.unattended_authorization(required=False):
                result["advance_command"] = f"python PASS/source.py advance --run {self.root}"
                result["authorized_action"] = (
                    "Use the unattended source runner. It will render and archive the complete preflight packet, bind the decision "
                    "to its hash and consume only this source's recorded unattended authorization. Do not reproduce the packet in chat."
                )
            else:
                result["presentation_command"] = f"python PASS/pass.py present --run {self.root}"
                result["acceptance_command"] = f"python PASS/pass.py accept-preflight --run {self.root} --decision <decision.json>"
                result["authorized_action"] = (
                    "Run present and reproduce the complete preflight packet verbatim. Obtain explicit user confirmation of the "
                    "stated subject and provisional source-wide plan; do not begin PASS 1. If the user requests a correction, use "
                    "revise-preflight and present the replacement packet again."
                )
        elif phase == "finished":
            result["authorized_action"] = "Source closure is canonicalized; use close-run to discard generated staging/controller state and inspect any explicitly retained scratch."
        else:
            unit = self.unit()
            result.update({"unit_id": unit["unit_id"], "material": unit["material"]})
            if phase in {"pass1", "pass2"}:
                result.update({"source": self.state["source"], "authorized_source_scope": unit["locator"]})
                if self.state.get("source_prep"):
                    candidate = inside(self.root, f"prepared-source/units/{unit['unit_id'].upper()}.md")
                    result["prepared_source_package"] = str(inside(self.root, "prepared-source"))
                    if candidate.is_file():
                        result["prepared_unit"] = str(candidate)
            if phase == "pass1":
                result["authorized_action"] = (
                    "SOURCE PREFLIGHT IS COMPLETE; do not preflight this unit. Read only this entire unit; draft provisional cards "
                    "by category; record overlaps, secondary-subject flags and consequential questions."
                )
                if self.language_modernization_required():
                    result["authorized_action"] += (
                        " This is a programming-language run: also flag every version-sensitive source claim for PASS 2; "
                        "do not silently copy source-era language behavior into current guidance."
                    )
            elif phase == "checkpoint":
                result["questions"] = self.state["pass1"]["questions"]
                result["authorized_action"] = "Resolve the checkpoint questions; do not begin PASS 2 and do not rerun preflight."
            elif phase == "pass2":
                result["secondary_subject_flags"] = self.state["pass1"]["secondary_subject_flags"]
                result["authorized_action"] = (
                    "SOURCE PREFLIGHT IS COMPLETE; do not preflight this unit. Re-engage the entire unit with three explicit source-reengagement jobs: "
                    "resolve every deferred PASS 1 flag, re-ground each changed card's material/source-sensitive claims against the source, "
                    "and sweep the complete unit for omissions. Then reconcile and declare exclusive dispositions, taxonomy and the exact staged change set. "
                    "For every changed card, record nearest-owner reconciliation and explicit stage/lane/confidence classification."
                )
                if self.language_modernization_required():
                    result["version_sensitive_flags"] = self.state["pass1"].get("version_sensitive_flags", [])
                    result["authorized_action"] += (
                        " Complete the required language-modernization audit against the accepted current target version, resolve "
                        "every version-sensitive flag, and review every changed software-engineering/core card as a language-agnostic decision."
                    )
            elif phase == "closure_pass2":
                result["authorized_action"] = (
                    "Run the mandatory source-closure audit over accepted canon: AP synthesis, DRILL synthesis, cross-library owner "
                    "reconciliation, and metadata classification. Stage only justified closure changes; do not reread the source as "
                    "another unit and do not manufacture APs or DRILLs merely to populate object types."
                )
            elif phase in {"pass3", "closure_pass3"}:
                result["staged_files"] = self.state["pass2"]["changes"]
                result["authorized_action"] = (
                    "Close the source/reading notes; scan staged cards as standalone objects. Repair and rescan; submit actual "
                    "reviewed hashes and every semantic check, including cross-library reconciliation and metadata classification. "
                    "Do not rerun preflight."
                )
                if self.language_modernization_required():
                    result["authorized_action"] += (
                        " Confirm Core rules remain language-agnostic and all current language-specific guidance reflects the accepted target version."
                    )
            elif phase in {"land", "closure_land"}:
                delta_keys = ("flag_resolutions", "claim_regrounding", "omission_sweep", "reinforcement_evidence", "buckets", "taxonomy", "changes", "removals", "approval_required", "owner_reconciliation", "metadata_classification")
                # The closure PASS 2 record replaces the unit delta; it carries
                # no unit-only keys, so render only the keys actually present
                # (the unit LAND path still renders the full delta).
                result["delta"] = {key: self.state["pass2"][key] for key in delta_keys if key in self.state["pass2"]}
                if "closure_audits" in self.state["pass2"]:
                    result["delta"]["closure_audits"] = self.state["pass2"]["closure_audits"]
                result["reviewed_sha256"] = self.state["reviewed_sha256"]
                if self.unattended_authorization(required=False):
                    result["advance_command"] = f"python PASS/source.py advance --run {self.root}"
                    if self.state["pass2"]["approval_required"]:
                        result["authorized_action"] = (
                            "Use the source runner to archive the landing packet, then stop for the practitioner. "
                            "approval_required cannot be consumed by unattended authorization."
                        )
                    else:
                        result["authorized_action"] = (
                            "Use the source runner to archive the complete landing packet and auto-land this routine delta under the "
                            "bounded unattended authorization; no chat reproduction is required."
                        )
                else:
                    result["presentation_command"] = f"python PASS/pass.py present --run {self.root}"
                    result["authorized_action"] = (
                        "Run present and reproduce its complete landing packet verbatim. Then land this unit only under the applicable "
                        "user-approval or evidence decision; no next-unit reading and no new preflight."
                    )
        # EXP-003 Target H: surface unresolved checkpoint residue in the pickup
        # so the next authorized action is recovery, never a blocked mutation.
        residue = checkpoint_residue(self.root)
        if any(residue.values()):
            result["checkpoint_residue"] = residue
            result["authorized_action"] = (
                "UNRESOLVED CHECKPOINT RESIDUE blocks every mutating command: "
                f"{json.dumps(residue, sort_keys=True)}. Inspect controller/checkpoint-failure.json, then run "
                "repair-checkpoint (non-destructive; keeps the current authoritative state) or recover "
                "--rollback-authoritative (explicit destructive rollback) before continuing."
            )
        return result

    def audit_dir_path(self) -> Path:
        path = inside(self.root, "controller/audit")
        path.mkdir(parents=True, exist_ok=True)
        return path

    def archive_presentation(self, name: str, packet: str, sha256: str) -> None:
        directory = self.audit_dir_path()
        atomic_write(inside(directory, f"{name}.md"), packet.encode("utf-8"))
        marker = {"schema_version": 1, "sha256": sha256, "bytes": len(packet.encode("utf-8"))}
        atomic_write(inside(directory, f"{name}.json"), (json.dumps(marker, indent=2) + "\n").encode("utf-8"))

    def unit_history_root(self, unit_id: str | None = None) -> Path:
        base = inside(self.root, "controller/unit-history")
        if unit_id is None:
            return base
        return inside(base, unit_id.lower())

    def history_revision_dir(self, unit_id: str, create: bool = False) -> Path:
        base = self.unit_history_root(unit_id)
        if base.is_dir():
            revisions = sorted(
                (path for path in base.iterdir() if path.is_dir() and re.fullmatch(r"r\d{3}", path.name)),
                key=lambda path: path.name,
            )
        else:
            revisions = []
        if revisions and not (revisions[-1] / "land.json").is_file():
            return revisions[-1]
        if not create:
            return revisions[-1] if revisions else inside(base, "r001")
        number = int(revisions[-1].name[1:]) + 1 if revisions else 1
        target = inside(base, f"r{number:03d}")
        target.mkdir(parents=True, exist_ok=False)
        return target

    def archive_pass3_record(self, unit_id: str, record: dict) -> Path:
        revision = self.history_revision_dir(unit_id, create=True)
        path = inside(revision, "pass3.json")
        atomic_write(path, (json.dumps(record, indent=2) + "\n").encode("utf-8"))
        return path

    def archive_land_record(self, unit_id: str, old_state: dict, decision: dict, writes: int, removals: int, is_closure: bool) -> Path:
        revision = self.history_revision_dir(unit_id, create=True)
        amendment_path = inside(revision, "amendment.json")
        amendment = preflight._read_json(str(amendment_path)) if amendment_path.is_file() else None
        record = {
            "schema_version": 2,
            "unit_id": unit_id,
            "pass1": old_state.get("pass1"),
            "pass2": old_state.get("pass2"),
            "pass3": preflight._read_json(str(inside(revision, "pass3.json"))) if inside(revision, "pass3.json").is_file() else None,
            "landing_decision": decision,
            "accepted_writes": writes,
            "accepted_removals": removals,
            "accepted_delta_fingerprint": self.accepted_fingerprint(),
            "canonical_library_mutated": bool(is_closure),
            "supersedes_revision": amendment.get("from_revision") if isinstance(amendment, dict) else None,
            "next_phase": self.state["phase"],
            "next_unit_index": self.state["unit_index"],
        }
        path = inside(revision, "land.json")
        atomic_write(path, (json.dumps(record, indent=2) + "\n").encode("utf-8"))
        return path

    def write_transition_report(self, unit_id: str, writes: int, removals: int, is_closure: bool) -> Path:
        # Reported as logical accepted paths even though storage is
        # content-addressed; the report documents which cards moved.
        accepted_files = sorted(f"accepted/files/{name}" for name in self.accepted_file_hashes())
        report = {
            "schema_version": 1,
            "unit_id": unit_id,
            "accepted_writes": writes,
            "accepted_removals": removals,
            "canonical_library_mutated": bool(is_closure),
            "phase": self.state["phase"],
            "unit_index": self.state["unit_index"],
            "accepted_files": accepted_files,
            "next_action": self.brief()["authorized_action"],
        }
        path = inside(self.audit_dir_path(), f"{unit_id.lower()}-state-report.json")
        atomic_write(path, (json.dumps(report, indent=2) + "\n").encode("utf-8"))
        return path

    def latest_transition_report(self) -> dict | None:
        directory = inside(self.root, "controller/audit")
        if not directory.is_dir():
            return None
        reports = sorted(directory.glob("*-state-report.json"), key=lambda path: path.stat().st_mtime_ns)
        if not reports:
            return None
        return preflight._read_json(str(reports[-1]))

    def preflight_presentation_path(self) -> Path:
        return inside(self.root, "controller/preflight-presentation.json")

    def clear_preflight_presentation(self) -> None:
        self.preflight_presentation_path().unlink(missing_ok=True)

    def preflight_presentation_marker(self, required: bool = False) -> dict | None:
        path = self.preflight_presentation_path()
        if not path.is_file():
            if required:
                raise RunError("run present and show the complete preflight packet before accepting preflight")
            return None
        marker = preflight._read_json(str(path))
        exact(marker, {"schema_version", "subject", "sha256"}, "preflight presentation marker")
        if type(marker["schema_version"]) is not int or marker["schema_version"] != 1:
            raise RunError("unsupported preflight presentation marker")
        if marker["subject"] != self.state["plan"]["subject"]:
            raise RunError("preflight presentation marker belongs to another plan; run present again")
        sha = string(marker["sha256"], "preflight presentation sha256")
        if not re.fullmatch(r"[0-9a-f]{64}", sha):
            raise RunError("invalid preflight presentation sha256")
        return marker

    def render_preflight_packet(self) -> str:
        if self.state["phase"] != "preflight_accept":
            raise RunError("preflight presentation is available only after the preflight record validates")
        record = preflight.parse_preflight(self.state["plan"])
        cards = preflight.validate_against_library(record, self.repo)
        packet = preflight.render_preflight(record, cards)
        prep = self.state.get("source_prep")
        if isinstance(prep, dict):
            if prep.get("compatibility_baseline"):
                packet += "\n\n**Prepared-source compatibility/version signals:** " + "; ".join(prep["compatibility_baseline"])
                packet += "\n\nTreat UI paths, generated templates, APIs, and tool-specific procedures as version-sensitive until PASS validates durable ownership."
            from .pass_source_prep import verify as verify_prepared_source
            manifest = verify_prepared_source(self)
            warnings = list((manifest.get("integrity_gate") or {}).get("warnings") or [])
            if warnings:
                packet += "\n\n## SOURCE PREP INTEGRITY WARNINGS\n"
                for warning in warnings:
                    page = warning.get("page")
                    prefix = f"PDF/source page {page}: " if page is not None else "source-wide: "
                    packet += f"\n- {prefix}{warning.get('warning', 'unspecified Source Prep warning')}"
                packet += (
                    "\n\nThese warnings must be reviewed before accepting the source-wide plan. "
                    "Do not infer that an integrity warning is harmless merely because deterministic extraction completed."
                )
        audit = self.preflight_quality_audit(record)
        boundary_review = list((audit.get("boundary") or {}).get("review") or [])
        if boundary_review:
            packet += "\n\n## UNIT-BOUNDARY REVIEW WARNINGS\n"
            for issue in boundary_review:
                packet += f"\n- {issue.get('message', 'unspecified unit-boundary warning')}"
            packet += (
                "\n\nThese are deterministic structural warnings, not semantic corrections. Verify the named unit boundaries "
                "against the prepared headings/pages before unattended acceptance."
            )
        return packet + (
            "\n\n**PREFLIGHT ACCEPTANCE REQUIRED:** Confirm the stated instructional subject and provisional "
            "source-wide unit plan before PASS 1. Corrections must be applied with `revise-preflight` and presented again."
        )

    def presentation_path(self) -> Path:
        return inside(self.root, "controller/landing-presentation.json")

    def clear_presentation(self) -> None:
        self.presentation_path().unlink(missing_ok=True)

    def presentation_marker(self, required: bool = False) -> dict | None:
        path = self.presentation_path()
        if not path.is_file():
            if required:
                raise RunError("run present and show its complete packet before submitting a landing decision")
            return None
        marker = preflight._read_json(str(path))
        exact(marker, {"schema_version", "unit_id", "sha256"}, "landing presentation marker")
        if type(marker["schema_version"]) is not int or marker["schema_version"] != 1:
            raise RunError("unsupported landing presentation marker")
        if marker["unit_id"] != self.unit()["unit_id"]:
            raise RunError("landing presentation marker belongs to another unit; run present again")
        sha = string(marker["sha256"], "landing presentation sha256")
        if not re.fullmatch(r"[0-9a-f]{64}", sha):
            raise RunError("invalid landing presentation sha256")
        return marker

    def present(self) -> str:
        if self.state["phase"] == "preflight_accept":
            packet = self.render_preflight_packet()
            marker = {
                "schema_version": 1,
                "subject": self.state["plan"]["subject"],
                "sha256": hashlib.sha256(packet.encode("utf-8")).hexdigest(),
            }
            atomic_write(self.preflight_presentation_path(), (json.dumps(marker, indent=2) + "\n").encode())
            self.archive_presentation("preflight", packet, marker["sha256"])
            return packet
        packet = self.render_land_packet()
        marker = {
            "schema_version": 1,
            "unit_id": self.unit()["unit_id"],
            "sha256": hashlib.sha256(packet.encode("utf-8")).hexdigest(),
        }
        atomic_write(self.presentation_path(), (json.dumps(marker, indent=2) + "\n").encode())
        self.archive_presentation(f"{self.unit()['unit_id'].lower()}-landing", packet, marker["sha256"])
        return packet

    def render_land_packet(self) -> str:
        if self.state["phase"] not in {"land", "closure_land"}:
            raise RunError("landing presentation is available only after PASS 3 passes")
        unit = self.unit()
        delta = self.state["pass2"]
        lines = [
            f"# PASS LANDING PACKET — {unit['unit_id'].upper()}",
            "",
            f"PASS 3: pass — {unit['unit_id'].upper()}",
            f"Material: {unit['material']}",
            "",
        ]
        for bucket in BUCKETS:
            lines.append(f"## {BUCKET_LABELS[bucket]}")
            entries = delta["buckets"][bucket]
            if entries:
                for item in entries:
                    lines.append(f"- `{item['object_id']}` — {item['reason']}")
            else:
                lines.append("- none")
            lines.append("")
        lines.append("## TAXONOMY")
        lines.append("")
        for action in TAXONOMY:
            lines.append(f"### {TAXONOMY_LABELS[action]}")
            entries = delta["taxonomy"][action]
            if entries:
                for item in entries:
                    lines.append(f"- `{item['path']}` — {item['reason']}")
            else:
                lines.append("- none")
            lines.append("")
        if "closure_audits" in delta:
            lines.append("## SOURCE CLOSURE AUDITS")
            lines.append("")
            for name, passed in delta["closure_audits"].items():
                lines.append(f"- `{name}` — {'pass' if passed else 'FAIL'}")
            lines.append("")
        if "claim_regrounding" in delta:
            lines.append("## PASS 2 CLAIM RE-GROUNDING")
            if delta["claim_regrounding"]:
                for item in delta["claim_regrounding"]:
                    lines.append(f"- `{item['object_id']}` — {item['summary']} ({len(item['claims'])} material claim(s) re-grounded)")
            else:
                lines.append("- no changed cards required claim re-grounding")
            lines.append("")
            lines.append("## PASS 2 OMISSION SWEEP")
            sweep = delta["omission_sweep"]
            lines.append(f"- complete: {'yes' if sweep['complete'] else 'NO'}")
            for finding in sweep["findings"]:
                lines.append(f"- {finding['subject']} — {finding['disposition']} — {finding['reason']}")
            if not sweep["findings"]:
                lines.append("- findings: none")
            lines.append("")
            lines.append("## REINFORCEMENT EVIDENCE")
            evidence = delta["reinforcement_evidence"]
            if evidence:
                for item in evidence:
                    lines.append(
                        f"- `{item['object_id']}` — scope: {item.get('scope', 'legacy_unscoped')} — owner claim: {item['owner_claim']} — "
                        f"source: {item['source_locator']} — {item['source_quote']}"
                    )
            else:
                lines.append("- none")
            lines.append("")
        lines.append("## OWNER RECONCILIATION")
        if delta.get("owner_reconciliation"):
            for item in delta["owner_reconciliation"]:
                owners = ", ".join(f"`{oid}`" for oid in item["compared_owner_ids"]) or "none"
                lines.append(f"- `{item['object_id']}` — compared: {owners} — {item['reason']}")
        else:
            lines.append("- none")
        lines.append("")
        lines.append("## METADATA CLASSIFICATION")
        if delta.get("metadata_classification"):
            for item in delta["metadata_classification"]:
                lines.append(
                    f"- `{item['object_id']}` — stage `{item['stage_binding']}`; lane `{item['lane_fit']}`; "
                    f"confidence `{item['confidence']}` — {item['reason']}"
                )
        else:
            lines.append("- none")
        lines.append("")
        lines.append("## CHANGES")
        if delta["changes"]:
            lines.extend(f"- `{name}`" for name in delta["changes"])
        else:
            lines.append("- none")
        lines.append("")
        lines.append("## REMOVALS")
        if delta["removals"]:
            lines.extend(f"- `{name}`" for name in delta["removals"])
        else:
            lines.append("- none")
        lines.append("")
        lines.append(f"**APPROVAL REQUIRED:** {'yes' if delta['approval_required'] else 'no'}")
        lines.append("")
        lines.append(
            "Do not summarize or omit this packet when presenting the proposed delta. "
            "Record a landing decision only after the applicable approval or evidence gate is actually satisfied."
        )
        return "\n".join(lines)

    def template(self) -> dict:
        phase = self.state["phase"]
        if phase == "preflight":
            result = preflight.template_record(self.domain)
            result.update(title=Path(self.state["source"]).stem)
            return result
        if phase == "preflight_accept":
            marker = self.preflight_presentation_marker(required=False)
            return {
                "schema_version": 1,
                "presentation_sha256": marker["sha256"] if marker else "",
                "subject": self.state["plan"]["subject"],
                "basis": "",
                "reason": "",
            }
        result = {"schema_version": 1}
        if phase == "load":
            result["documents_read"] = required_documents(self.repo)
        else:
            result["unit_id"] = self.unit()["unit_id"]
            if phase == "pass1":
                result.update(full_read=False, working_drafts=[], overlap_object_ids=[], secondary_subject_flags=[], questions=[])
                if self.language_modernization_required():
                    result["version_sensitive_flags"] = []
            elif phase == "checkpoint":
                result["answers"] = [{"question_id": q["question_id"], "resolution": ""} for q in self.state["pass1"]["questions"]]
            elif phase == "pass2":
                result.update(
                    full_reread=False,
                    flag_resolutions=[{"flag_id": f["flag_id"], "outcome": "", "reason": "", "deferred_to": ""} for f in self.state["pass1"]["secondary_subject_flags"]],
                    claim_regrounding=[],
                    omission_sweep={"complete": False, "findings": []},
                    reinforcement_evidence=[],
                    buckets={name: [] for name in BUCKETS}, taxonomy={name: [] for name in TAXONOMY}, changes=[], removals=[], approval_required=False,
                    owner_reconciliation=[], metadata_classification=[]
                )
                if self.language_modernization_required():
                    policy = self.language_policy()
                    result["language_modernization"] = {
                        "language": policy["language"],
                        "target_version": policy["target_version"],
                        "target_basis": policy["target_basis"],
                        "all_version_sensitive_material_reviewed": False,
                        "resolutions": [
                            {
                                "flag_id": f["flag_id"],
                                "disposition": "",
                                "current_guidance": "",
                                "verification": "",
                            }
                            for f in self.state["pass1"].get("version_sensitive_flags", [])
                        ],
                        "core_changes": [],
                    }
            elif phase == "closure_pass2":
                result.update(closure_audits={"ap_synthesis": False, "drill_synthesis": False, "cross_library_reconciliation": False, "metadata_classification": False},
                              buckets={name: [] for name in BUCKETS}, taxonomy={name: [] for name in TAXONOMY}, changes=[], removals=[], approval_required=False,
                              owner_reconciliation=[], metadata_classification=[])
            elif phase in {"pass3", "closure_pass3"}:
                result.update(card_only_review=False, checks={name: False for name in self.semantic_checks()}, reviewed_sha256=self.staged_hashes())
            elif phase in {"land", "closure_land"}:
                marker = self.presentation_marker(required=False)
                result.update(presentation_sha256=marker["sha256"] if marker else "", basis="", reason="")
            else:
                raise RunError("this phase has no submission template")
        return result

    def header(self, data: dict, keys: set[str]) -> None:
        exact(data, keys | {"schema_version", "unit_id"}, self.state["phase"])
        if type(data["schema_version"]) is not int or data["schema_version"] != 1:
            raise RunError("phase schema_version must be integer 1")
        if data["unit_id"] != self.unit()["unit_id"]:
            raise RunError("record does not belong to the only active unit")

    def live_hashes(self) -> dict:
        result = {}
        for domain in (self.domain, "metaskills"):
            for name, value in tree_hashes(inside(self.repo, f"library/{domain}")).items():
                result[f"library/{domain}/{name}"] = value
        for path in sorted((self.repo / "workspace/release-recipes").glob("SkillForge_*.yaml")):
            path = inside(self.repo, path.relative_to(self.repo).as_posix())
            spec = preflight.yaml.safe_load(path.read_text(encoding="utf-8"))
            if isinstance(spec, dict) and isinstance(spec.get("modules"), list) and any(str(m).split("/")[0] == self.domain for m in spec["modules"]):
                result[path.relative_to(self.repo).as_posix()] = digest(path)
        result["__accepted_delta__"] = self.accepted_fingerprint()
        return result

    def live_fingerprint(self) -> str:
        """Digest of canonical dependencies plus the cumulative accepted delta."""
        canonical = json.dumps(self.live_hashes(), sort_keys=True).encode("utf-8")
        return "sha256:" + hashlib.sha256(canonical).hexdigest()

    def canonical_live_fingerprint(self) -> str:
        hashes = self.live_hashes()
        hashes.pop("__accepted_delta__", None)
        canonical = json.dumps(hashes, sort_keys=True).encode("utf-8")
        return "sha256:" + hashlib.sha256(canonical).hexdigest()

    def live_snapshot(self) -> dict[str, str]:
        return {"canonical": self.canonical_live_fingerprint(), "accepted": self.accepted_fingerprint()}

    def live_unchanged(self) -> bool:
        stored = self.state["live_hashes"]
        if isinstance(stored, dict) and set(stored) == {"canonical", "accepted"}:
            return self.live_snapshot() == stored
        if isinstance(stored, dict):  # very early runs stored the full path map
            return self.live_hashes() == stored
        # beta.77 stored one fingerprint before accepted staging existed. An
        # empty accepted delta may therefore compare against canonical only.
        return self.live_fingerprint() == stored or (not self.accepted_file_hashes() and not self.accepted_removals() and self.canonical_live_fingerprint() == stored)

    def canonical_live_unchanged(self) -> bool:
        stored = self.state["live_hashes"]
        if isinstance(stored, dict) and set(stored) == {"canonical", "accepted"}:
            return self.canonical_live_fingerprint() == stored["canonical"]
        if isinstance(stored, str):
            return self.canonical_live_fingerprint() == stored or self.live_fingerprint() == stored
        return True

    def target(self, staged: str) -> str:
        path = relative(staged)
        if path.parts[0] == "recipes" and len(path.parts) == 2 and re.fullmatch(r"SkillForge_[A-Za-z_]+\.yaml", path.name):
            spec = preflight.yaml.safe_load(inside(self.root, staged).read_text(encoding="utf-8"))
            modules = spec.get("modules") if isinstance(spec, dict) else None
            if not isinstance(modules, list) or not modules or any(str(m).split("/")[0] not in {self.domain, "metaskills"} for m in modules) or not any(str(m).split("/")[0] == self.domain for m in modules):
                raise RunError("staged recipe must own the active domain plus optional metaskills")
            live = inside(self.repo, f"workspace/release-recipes/{path.name}")
            if not live.is_file():
                raise RunError("ordinary source runs may update their existing canonical recipe; creating a release recipe is separate maintenance")
            owner = preflight.yaml.safe_load(live.read_text(encoding="utf-8"))
            owned = owner.get("modules") if isinstance(owner, dict) else None
            if not isinstance(owned, list) or not any(str(m).split("/")[0] == self.domain for m in owned):
                raise RunError("recipe belongs to another domain")
            if {k: v for k, v in spec.items() if k != "modules"} != {k: v for k, v in owner.items() if k != "modules"}:
                raise RunError("ordinary source runs update recipe modules only; release metadata/composition changes are separate maintenance")
            return f"workspace/release-recipes/{path.name}"
        if path.parts[0] != "drafts" or len(path.parts) < 3:
            raise RunError("changes must be drafts/<canonical-category>/<file> or recipes/<owned-recipe>.yaml")
        if path.name == "INDEX.md":
            raise RunError("indexes are generated, never staged")
        if path.name != "MODULE.yaml" and not re.fullmatch(r"(?:PAT|AP|DRILL)_[a-z0-9_]+\.md", path.name):
            if "assets" not in path.parts or path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", ".json"}:
                raise RunError(f"unsupported staged library file: {staged}")
        return f"library/{self.domain}/" + PurePosixPath(*path.parts[1:]).as_posix()

    def removal_target(self, name: str) -> str:
        path = relative(name)
        if path.name != "MODULE.yaml" and not re.fullmatch(r"(?:PAT|AP|DRILL)_[a-z0-9_]+\.md", path.name):
            if "assets" not in path.parts or path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", ".json"}:
                raise RunError("removals must name canonical cards, modules or assets; indexes are generated")
        return f"library/{self.domain}/{path.as_posix()}"

    def baseline_staged_path(self, canon: str) -> str | None:
        """Run-relative staged path for a canonical accepted file, or None when
        it must not be restaged (generated indexes, foreign paths)."""
        if canon.startswith(f"library/{self.domain}/"):
            rel = canon[len(f"library/{self.domain}/"):]
            if PurePosixPath(rel).name == "INDEX.md":
                return None
            staged = f"drafts/{rel}"
            if self.target(staged) != canon:
                raise RunError(f"accepted file does not round-trip to its staged baseline path: {canon}")
            return staged
        if canon.startswith("workspace/release-recipes/") and re.fullmatch(r"SkillForge_[A-Za-z_]+\.yaml", PurePosixPath(canon).name):
            staged = f"recipes/{PurePosixPath(canon).name}"
            if self.target(staged) != canon:
                raise RunError(f"accepted recipe does not round-trip to its staged baseline path: {canon}")
            return staged
        return None

    def staged_hashes(self) -> dict[str, str]:
        return {name: digest(inside(self.root, name)) for name in self.state["pass2"]["changes"]}

    def check_live(self) -> None:
        if not self.live_unchanged():
            raise RunError("live domain/prerequisites changed; rewind to pass2, reconcile and repeat PASS 3 before landing")

    def submit(self, phase: str, data: dict) -> str:
        if self.state.get("stop_reached"):
            raise RunError(f"stop target {self.state.get('stop_after')} has been reached; run continue-run before advancing")
        if phase != self.state["phase"]:
            raise RunError(f"cannot submit {phase}; current phase is {self.state['phase']}")
        previous_unit_index = self.state["unit_index"]
        self.require_unattended_action(phase)
        if phase == "load":
            exact(data, {"schema_version", "documents_read"}, "load")
            documents = array(data["documents_read"], "documents_read")
            if type(data["schema_version"]) is not int or data["schema_version"] != 1 or any(not isinstance(d, str) for d in documents) or sorted(documents) != sorted(required_documents(self.repo)):
                raise RunError("load record must declare every required current canonical document exactly once")
            # Source-byte access becomes legal only after the LOAD declaration is
            # validated. Capture identity now, before structural preflight begins.
            self.capture_source_identity()
            self.state["phase"] = "source_prep"
            message = "LOAD GATE: pass — source preparation released"
        elif phase == "preflight":
            record = preflight.parse_preflight(data)
            if record.domain != self.domain:
                raise RunError("preflight cannot change the run's authorized domain")
            if record.mode != "unit ingestion":
                raise RunError("controller orchestration currently supports unit ingestion only; curriculum audit requires its own scope contract")
            preflight.validate_against_library(record, self.repo)
            self.validate_preflight_source_coordinates(record)
            self.enforce_preflight_quality(record)
            self.clear_preflight_presentation()
            self.state.update(plan=preflight.serialize_preflight(record), phase="preflight_accept")
            message = "PREFLIGHT: validated — presentation and explicit user confirmation required before PASS 1"
        elif phase == "pass1":
            keys = {"full_read", "working_drafts", "overlap_object_ids", "secondary_subject_flags", "questions"}
            if self.language_modernization_required():
                keys.add("version_sensitive_flags")
            self.header(data, keys)
            if data["full_read"] is not True:
                raise RunError("PASS 1 requires the entire bounded unit's full read")
            for name in array(data["working_drafts"], "working_drafts"):
                self.target(name)
                if not inside(self.root, name).is_file():
                    raise RunError(f"working draft does not exist: {name}")
            cards = self.working_cards()
            overlap = array(data["overlap_object_ids"], "overlap_object_ids")
            if any(not isinstance(oid, str) or oid not in cards for oid in overlap) or len(set(overlap)) != len(overlap):
                raise RunError("PASS 1 overlaps must be unique active-domain live IDs")
            for field, key, text in (("secondary_subject_flags", "flag_id", "subject"), ("questions", "question_id", "question")):
                seen = set()
                for entry in array(data[field], field):
                    exact(entry, {key, text}, field)
                    value = string(entry[key], key)
                    if not FLAG_RE.fullmatch(value) or value in seen:
                        raise RunError(f"invalid or duplicate {key} (expected {FLAG_RE.pattern}; lowercase letters/digits/underscore only, beginning with a letter)")
                    seen.add(value)
                    string(entry[text], text)
            if self.language_modernization_required():
                seen = set()
                for entry in array(data["version_sensitive_flags"], "version_sensitive_flags"):
                    exact(entry, {"flag_id", "source_claim", "reason"}, "version-sensitive flag")
                    value = string(entry["flag_id"], "version-sensitive flag_id")
                    if not FLAG_RE.fullmatch(value) or value in seen:
                        raise RunError(f"invalid or duplicate version-sensitive flag_id (expected {FLAG_RE.pattern})")
                    seen.add(value)
                    string(entry["source_claim"], "version-sensitive source claim")
                    string(entry["reason"], "version-sensitive reason")
            self.state.update(pass1=data, phase="checkpoint" if data["questions"] else "pass2")
            message = f"PASS 1: complete — {self.unit()['unit_id'].upper()}"
        elif phase == "checkpoint":
            self.header(data, {"answers"})
            seen = set()
            for answer in array(data["answers"], "answers"):
                exact(answer, {"question_id", "resolution"}, "answer")
                key = string(answer["question_id"], "question_id")
                if key in seen:
                    raise RunError("duplicate checkpoint answer")
                seen.add(key)
                string(answer["resolution"], "resolution")
            if seen != {q["question_id"] for q in self.state["pass1"]["questions"]}:
                raise RunError("every checkpoint question requires an explicit answer")
            self.state["pass1"]["answers"] = data["answers"]
            self.state["phase"] = "pass2"
            message = "CHECKPOINT: resolved"
        elif phase == "pass2":
            self.accept_pass2(data)
            message = f"PASS 2: complete — {self.unit()['unit_id'].upper()}"
        elif phase == "closure_pass2":
            self.accept_closure_pass2(data)
            message = "CLOSURE PASS 2: synthesis and reconciliation audit complete"
        elif phase in {"pass3", "closure_pass3"}:
            self.header(data, {"card_only_review", "checks", "reviewed_sha256"})
            if data["card_only_review"] is not True:
                raise RunError("PASS 3 requires a card-only review with the source and reading notes closed")
            exact(data["checks"], self.semantic_checks(), "semantic checks")
            if any(value is not True for value in data["checks"].values()):
                raise RunError("PASS 3 has an unresolved semantic/identity defect; repair and rescan")
            self.check_live()
            hashes = self.staged_hashes()
            if data["reviewed_sha256"] != hashes:
                raise RunError("reviewed hashes do not match the actual staged files; rescan and resubmit PASS 3")
            self.check_change_set(self.state["pass2"])
            with self.overlay() as tree:
                self.validate(tree)
            self.check_live()
            if self.staged_hashes() != hashes:
                raise RunError("drafts changed during validation; repeat PASS 3")
            self.clear_presentation()
            self.state.update(reviewed_sha256=hashes, phase="closure_land" if phase == "closure_pass3" else "land")
            message = ("CLOSURE PASS 3: pass" if phase == "closure_pass3" else f"PASS 3: pass — {self.unit()['unit_id'].upper()}")
        else:
            raise RunError("use land or close-run for this phase")
        self.save()
        if phase in {"pass3", "closure_pass3"}:
            self.archive_pass3_record(self.unit()["unit_id"], data)
        self.consume_unattended_action(phase, previous_unit_index)
        return message

    def accept_pass2(self, data: dict) -> None:
        keys = {"full_reread", "flag_resolutions", "claim_regrounding", "omission_sweep", "reinforcement_evidence", "buckets", "taxonomy", "changes", "removals", "approval_required", "owner_reconciliation", "metadata_classification"}
        if self.language_modernization_required():
            keys.add("language_modernization")
        self.header(data, keys)
        if data["full_reread"] is not True or type(data["approval_required"]) is not bool:
            raise RunError("PASS 2 requires a full cold reread and explicit approval_required Boolean")
        resolved = set()
        for item in array(data["flag_resolutions"], "flag_resolutions"):
            exact(item, {"flag_id", "outcome", "reason", "deferred_to"}, "flag resolution")
            key = string(item["flag_id"], "flag_id")
            if key in resolved:
                raise RunError("duplicate flag resolution")
            resolved.add(key)
            outcome = string(item["outcome"], "flag resolution outcome").lower()
            if outcome not in {"collected", "rejected", "deferred"}:
                raise RunError("flag resolution outcome must be collected, rejected, or deferred")
            string(item["reason"], "flag resolution reason")
            deferred_to = item["deferred_to"]
            if type(deferred_to) is not str:
                raise RunError("flag resolution deferred_to must be a string")
            if outcome == "deferred":
                if not deferred_to.strip():
                    raise RunError("deferred flag resolution requires deferred_to naming its destination or closure condition")
            elif deferred_to.strip():
                raise RunError("deferred_to is allowed only when flag resolution outcome is deferred")
        if resolved != {f["flag_id"] for f in self.state["pass1"]["secondary_subject_flags"]}:
            raise RunError("every PASS 1 secondary-subject flag must be explicitly resolved")
        exact(data["buckets"], BUCKETS, "delta buckets")
        cards = self.working_cards()
        seen = set()
        for bucket, entries in data["buckets"].items():
            for item in array(entries, bucket):
                exact(item, {"object_id", "reason"}, bucket)
                oid = string(item["object_id"], "object_id")
                if not preflight.OBJECT_ID_RE.fullmatch(oid) or oid in seen:
                    raise RunError("invalid ID or mutually inconsistent/duplicate dispositions")
                seen.add(oid)
                string(item["reason"], f"{bucket} reason")
                if bucket in {"REFINE", "REINFORCE", "VARIANTS", "REPLACE"} and oid not in cards:
                    raise RunError(f"{bucket} requires an active-domain existing owner: {oid}")
                if bucket.startswith("NEW_") and oid in cards:
                    raise RunError(f"NEW disposition already has a live owner: {oid}")
                prefix = {"NEW_PATTERNS": "PAT_", "NEW_APS": "AP_", "NEW_DRILLS": "DRILL_"}.get(bucket)
                if prefix and not oid.startswith(prefix):
                    raise RunError(f"wrong object type for {bucket}")
        exact(data["taxonomy"], TAXONOMY, "taxonomy buckets")
        for action, entries in data["taxonomy"].items():
            for item in array(entries, action):
                exact(item, {"path", "reason"}, action)
                relative(item["path"])
                string(item["reason"], f"{action} reason")
        self.check_change_set(data)
        self.validate_pass2_intensification(data)
        self.validate_reinforcement_evidence(data)
        self.validate_reconciliation_and_metadata(data)
        if self.language_modernization_required():
            self.validate_language_modernization(data)
        self.state.update(pass2=data, live_hashes=self.live_snapshot(), reviewed_sha256=None, phase="pass3")

    def validate_pass2_intensification(self, data: dict) -> None:
        """Make the second source pass observable without automating semantic truth."""
        changed_cards: dict[str, Path] = {}
        for name in data["changes"]:
            source = inside(self.root, name)
            if source.suffix == ".md":
                fm = preflight._frontmatter(source)
                oid = fm.get("object_id")
                if isinstance(oid, str):
                    changed_cards[oid] = source

        seen: set[str] = set()
        for entry in array(data["claim_regrounding"], "claim_regrounding"):
            exact(entry, {"object_id", "claims", "summary"}, "intensified claim review")
            oid = string(entry["object_id"], "intensified claim object_id")
            if oid in seen or oid not in changed_cards:
                raise RunError("claim_regrounding must name each changed card exactly once")
            seen.add(oid)
            claims = array(entry["claims"], "intensified material claims")
            if not claims:
                raise RunError(f"changed card {oid} requires at least one re-grounded material/source-sensitive claim")
            card_text = changed_cards[oid].read_text(encoding="utf-8")
            for claim in claims:
                exact(claim, {"card_quote", "source_locator", "source_quote"}, "intensified claim")
                card_quote = string(claim["card_quote"], "card_quote")
                if card_quote not in card_text:
                    raise RunError(f"intensified card_quote is not present in the staged card: {oid}")
                string(claim["source_locator"], "source_locator")
                string(claim["source_quote"], "source_quote")
            string(entry["summary"], "intensified claim summary")
        if seen != set(changed_cards):
            missing = sorted(set(changed_cards) - seen)
            raise RunError("every changed card requires PASS 2 claim re-grounding" + (": " + ", ".join(missing) if missing else ""))

        sweep = data["omission_sweep"]
        exact(sweep, {"complete", "findings"}, "omission sweep")
        if sweep["complete"] is not True:
            raise RunError("PASS 2 omission_sweep.complete must be true after sweeping the complete unit for missed durable material")
        for finding in array(sweep["findings"], "omission sweep findings"):
            exact(finding, {"subject", "disposition", "reason"}, "omission sweep finding")
            string(finding["subject"], "omission sweep subject")
            disposition = string(finding["disposition"], "omission sweep disposition").lower()
            if disposition not in {"collected", "rejected"}:
                raise RunError("omission sweep disposition must be collected or rejected")
            string(finding["reason"], "omission sweep reason")

    def validate_reinforcement_evidence(self, data: dict) -> None:
        """Require inspectable source-to-owner evidence for every REINFORCE disposition."""
        reinforce_ids = {item["object_id"] for item in data["buckets"]["REINFORCE"]}
        seen: set[str] = set()
        with self.accepted_overlay() as tree:
            cards = preflight.load_domain_cards(tree, self.domain)
            for entry in array(data["reinforcement_evidence"], "reinforcement_evidence"):
                exact(entry, {"object_id", "owner_claim", "source_locator", "source_quote", "scope"}, "reinforcement evidence")
                oid = string(entry["object_id"], "reinforcement evidence object_id")
                if oid in seen or oid not in reinforce_ids:
                    raise RunError("reinforcement_evidence must name each REINFORCE owner exactly once")
                seen.add(oid)
                owner = cards.get(oid)
                if owner is None:
                    raise RunError(f"reinforcement evidence names no active owner: {oid}")
                claim = string(entry["owner_claim"], "reinforcement owner_claim")
                scope = string(entry["scope"], "reinforcement scope")
                if scope != "reinforces_core":
                    raise RunError("reinforcement evidence scope must be exactly reinforces_core")
                if claim not in owner.path.read_text(encoding="utf-8"):
                    raise RunError(f"reinforcement owner_claim is not present in the active owner: {oid}")
                string(entry["source_locator"], "reinforcement source_locator")
                string(entry["source_quote"], "reinforcement source_quote")
        if seen != reinforce_ids:
            missing = sorted(reinforce_ids - seen)
            raise RunError("every REINFORCE disposition requires source-to-owner evidence" + (": " + ", ".join(missing) if missing else ""))

    def validate_language_modernization(self, data: dict) -> None:
        """Fail closed until source-era language claims are explicitly modernized."""
        policy = self.language_policy()
        if policy is None:
            raise RunError("language modernization was requested without an accepted programming-language policy")
        audit = data.get("language_modernization")
        exact(
            audit,
            {"language", "target_version", "target_basis", "all_version_sensitive_material_reviewed", "resolutions", "core_changes"},
            "language modernization",
        )
        for key in ("language", "target_version", "target_basis"):
            if audit[key] != policy[key]:
                raise RunError(f"language modernization {key} must match the accepted preflight policy")
        if audit["all_version_sensitive_material_reviewed"] is not True:
            raise RunError(
                "PASS 2 cannot accept a programming-language source until all version-sensitive material has been reviewed against the current target version"
            )

        expected_flags = {
            item["flag_id"] for item in self.state["pass1"].get("version_sensitive_flags", [])
        }
        resolved: set[str] = set()
        for item in array(audit["resolutions"], "language modernization resolutions"):
            exact(item, {"flag_id", "disposition", "current_guidance", "verification"}, "language modernization resolution")
            flag_id = string(item["flag_id"], "language modernization flag_id")
            if flag_id in resolved:
                raise RunError("duplicate language modernization resolution")
            resolved.add(flag_id)
            disposition = string(item["disposition"], "language modernization disposition").lower()
            if disposition not in MODERNIZATION_DISPOSITIONS:
                raise RunError(
                    "language modernization disposition must be current, modernized, historical, or rejected"
                )
            string(item["current_guidance"], "language modernization current_guidance")
            string(item["verification"], "language modernization verification")
        if resolved != expected_flags:
            raise RunError("every PASS 1 version-sensitive flag must have exactly one PASS 2 modernization resolution")

        expected_core = set(self.core_card_changes(data))
        reviewed_core: set[str] = set()
        for item in array(audit["core_changes"], "core agnosticism reviews"):
            exact(
                item,
                {
                    "path",
                    "decision_rule_language_agnostic",
                    "language_specific_mechanics_confined_to_examples_or_language_module",
                },
                "core agnosticism review",
            )
            path = string(item["path"], "core agnosticism path")
            if path in reviewed_core:
                raise RunError("duplicate core agnosticism review")
            reviewed_core.add(path)
            if item["decision_rule_language_agnostic"] is not True:
                raise RunError("a Software Engineering Core change must keep its decision rule language-agnostic")
            if item["language_specific_mechanics_confined_to_examples_or_language_module"] is not True:
                raise RunError(
                    "language-specific syntax, idioms, runtime mechanics and exceptions may not define a Software Engineering Core rule"
                )
        if reviewed_core != expected_core:
            missing = sorted(expected_core - reviewed_core)
            extra = sorted(reviewed_core - expected_core)
            detail = []
            if missing:
                detail.append("missing " + ", ".join(missing))
            if extra:
                detail.append("unexpected " + ", ".join(extra))
            raise RunError("every staged Software Engineering Core card change requires an agnosticism review" + (": " + "; ".join(detail) if detail else ""))

    def accept_closure_pass2(self, data: dict) -> None:
        self.header(data, {"closure_audits", "buckets", "taxonomy", "changes", "removals", "approval_required", "owner_reconciliation", "metadata_classification"})
        exact(data["closure_audits"], {"ap_synthesis", "drill_synthesis", "cross_library_reconciliation", "metadata_classification"}, "closure audits")
        if any(value is not True for value in data["closure_audits"].values()):
            raise RunError("source closure requires explicit AP synthesis, DRILL synthesis, cross-library reconciliation, and metadata audits")
        if type(data["approval_required"]) is not bool:
            raise RunError("closure PASS 2 requires an explicit approval_required Boolean")
        exact(data["buckets"], BUCKETS, "delta buckets")
        cards = self.working_cards()
        seen = set()
        for bucket, entries in data["buckets"].items():
            for item in array(entries, bucket):
                exact(item, {"object_id", "reason"}, bucket)
                oid = string(item["object_id"], "object_id")
                if not preflight.OBJECT_ID_RE.fullmatch(oid) or oid in seen:
                    raise RunError("invalid ID or mutually inconsistent/duplicate closure dispositions")
                seen.add(oid)
                string(item["reason"], f"{bucket} reason")
                if bucket in {"REFINE", "REINFORCE", "VARIANTS", "REPLACE"} and oid not in cards:
                    raise RunError(f"{bucket} requires an active-domain existing owner: {oid}")
                if bucket.startswith("NEW_") and oid in cards:
                    raise RunError(f"NEW disposition already has a live owner: {oid}")
                prefix = {"NEW_PATTERNS": "PAT_", "NEW_APS": "AP_", "NEW_DRILLS": "DRILL_"}.get(bucket)
                if prefix and not oid.startswith(prefix):
                    raise RunError(f"wrong object type for {bucket}")
        exact(data["taxonomy"], TAXONOMY, "taxonomy buckets")
        for action, entries in data["taxonomy"].items():
            for item in array(entries, action):
                exact(item, {"path", "reason"}, action)
                relative(item["path"])
                string(item["reason"], f"{action} reason")
        self.check_change_set(data)
        self.validate_reconciliation_and_metadata(data)
        self.state.update(pass2=data, live_hashes=self.live_snapshot(), reviewed_sha256=None, phase="closure_pass3")

    def validate_reconciliation_and_metadata(self, data: dict) -> None:
        cards = self.working_cards()
        changed = {}
        for name in data["changes"]:
            source = inside(self.root, name)
            if source.suffix == ".md":
                fm = preflight._frontmatter(source)
                changed[fm["object_id"]] = fm

        owner_entries = array(data["owner_reconciliation"], "owner_reconciliation")
        owner_seen = set()
        for entry in owner_entries:
            exact(entry, {"object_id", "compared_owner_ids", "reason"}, "owner reconciliation")
            oid = string(entry["object_id"], "owner reconciliation object_id")
            if oid in owner_seen:
                raise RunError("duplicate owner reconciliation entry")
            owner_seen.add(oid)
            compared = array(entry["compared_owner_ids"], "compared_owner_ids")
            if len(set(compared)) != len(compared) or any(not isinstance(x, str) or x not in cards for x in compared):
                bad = [x for x in compared if isinstance(x, str) and x not in cards]
                staged_new = [x for x in bad if x in changed]
                hint = ""
                if staged_new:
                    hint = (
                        f" ({', '.join(sorted(staged_new))} "
                        f"{'is' if len(staged_new) == 1 else 'are'} a staged-new card: its sibling file lives in drafts/ and "
                        "does not exist in live canon until landing, so it cannot appear in compared_owner_ids — reconcile "
                        "against live cards only, and give the new card itself an entry with empty compared_owner_ids)"
                    )
                raise RunError(
                    "owner reconciliation may name only unique live active-domain object IDs" + hint
                )
            string(entry["reason"], "owner reconciliation reason")
        if owner_seen != set(changed):
            missing = sorted(set(changed) - owner_seen)
            extra = sorted(owner_seen - set(changed))
            parts = []
            if missing:
                parts.append(f"missing entries for {', '.join(missing)} (newly staged cards need one too: "
                             "empty compared_owner_ids and a reason noting no live predecessor)")
            if extra:
                parts.append(f"entries for unchanged cards {', '.join(extra)}")
            raise RunError(
                "every changed card requires exactly one owner reconciliation entry"
                + (" — " + "; ".join(parts) if parts else "")
            )

        meta_entries = array(data["metadata_classification"], "metadata_classification")
        meta_seen = set()
        for entry in meta_entries:
            exact(entry, {"object_id", "stage_binding", "lane_fit", "confidence", "reason"}, "metadata classification")
            oid = string(entry["object_id"], "metadata object_id")
            if oid in meta_seen or oid not in changed:
                raise RunError("metadata classification must name each changed card exactly once")
            meta_seen.add(oid)
            stage = string(entry["stage_binding"], "stage_binding")
            lane = string(entry["lane_fit"], "lane_fit")
            confidence = string(entry["confidence"], "confidence")
            if stage not in {"0 design", "1 skeleton", "2 block", "3 rough", "4 final"}:
                raise RunError("metadata stage_binding is outside the PASS vocabulary")
            if lane not in {"teach", "skill", "both"}:
                raise RunError("metadata lane_fit is outside the PASS vocabulary")
            if confidence not in {"low", "medium", "high"}:
                raise RunError("metadata confidence is outside the PASS vocabulary")
            string(entry["reason"], "metadata classification reason")
            fm = changed[oid]
            if fm.get("stage_binding") != stage or fm.get("lane_fit") != lane or fm.get("confidence") != confidence:
                raise RunError(f"metadata classification does not match staged frontmatter: {oid}")
        if meta_seen != set(changed):
            raise RunError("every changed card requires exactly one metadata classification entry")

    def check_change_set(self, data: dict) -> None:
        changes = array(data["changes"], "changes")
        removals = array(data["removals"], "removals")
        if any(not isinstance(p, str) for p in changes + removals) or len(set(changes)) != len(changes) or len(set(removals)) != len(removals):
            raise RunError("change/removal paths must be unique strings")
        dispositions = {item["object_id"]: bucket for bucket, entries in data["buckets"].items() for item in entries}
        with self.accepted_overlay() as working:
            cards = preflight.load_domain_cards(working, self.domain)
            removed_ids = set()
            removal_targets = set()
            for name in removals:
                target = self.removal_target(name)
                path = inside(working, target)
                if not path.is_file():
                    raise RunError(f"removal has no active working target: {name}")
                if target in removal_targets:
                    raise RunError("duplicate removal targets")
                removal_targets.add(target)
                if path.suffix == ".md":
                    oid = preflight._frontmatter(path).get("object_id")
                    if not isinstance(oid, str) or not preflight.OBJECT_ID_RE.fullmatch(oid):
                        raise RunError("removed card has no canonical identity")
                    removed_ids.add(oid)
                if not any(data["taxonomy"].values()) and path.suffix != ".md":
                    raise RunError("resource/module removal needs an explicit taxonomy disposition")
            changed_ids = set()
            targets = set()
            for name in changes:
                source = inside(self.root, name)
                if not source.is_file():
                    raise RunError(f"missing staged file: {name}")
                target = self.target(name)
                work_target = inside(working, target)
                if target in targets or target in removal_targets:
                    raise RunError("duplicate or conflicting change targets")
                targets.add(target)
                if source.suffix == ".md":
                    card = preflight._frontmatter(source)
                    oid = card.get("object_id")
                    if oid != source.stem or oid in changed_ids:
                        raise RunError("filename/object_id mismatch or duplicate draft ID")
                    changed_ids.add(oid)
                    if oid not in dispositions or dispositions[oid] in {"REINFORCE", "REJECT"}:
                        raise RunError("every changed card needs one changing disposition; REINFORCE leaves its owner unchanged")
                    live = cards.get(oid)
                    if live and live.path != work_target and live.path.relative_to(working).as_posix() not in removal_targets:
                        raise RunError("moving an owner requires removal of its original path")
                    if live and digest(live.path) == digest(source) and live.path == work_target:
                        raise RunError("unchanged card belongs in REINFORCE, not a changing disposition")
                category = None
                if target.startswith("library/"):
                    parts = PurePosixPath(target).parent.relative_to(f"library/{self.domain}").parts
                    if "assets" in parts:
                        parts = parts[:parts.index("assets")]
                    category = PurePosixPath(*parts).as_posix() if parts else None
                if category and not inside(working, f"library/{self.domain}/{category}").exists():
                    declared = [e["path"] for e in data["taxonomy"]["NEW_SUBCATEGORY"]]
                    if not any(category == p or category.startswith(p + "/") for p in declared):
                        raise RunError(f"new library category requires NEW_SUBCATEGORY: {category}; staged card paths are drafts/<category-relative-to-library/{self.domain}>/<card>.md, not drafts/library/{self.domain}/...")
            for oid, bucket in dispositions.items():
                if bucket not in {"REINFORCE", "REJECT"} and oid not in changed_ids | removed_ids:
                    raise RunError(f"changing disposition has no staged change/removal: {oid}")
            for oid in removed_ids:
                if dispositions.get(oid) != "REPLACE" and not (oid in changed_ids and any(data["taxonomy"][a] for a in ("MOVE", "RENAME", "MERGE"))):
                    raise RunError("retired owner needs REPLACE or an explicit taxonomy migration with its successor")
        if any(PurePosixPath(p).name == "MODULE.yaml" for p in changes + removals):
            if not any(p.startswith("recipes/") for p in changes):
                raise RunError("module changes must include the active domain's canonical release recipe")

    def accepted_root(self) -> Path:
        return inside(self.root, "accepted")

    def accepted_removals(self) -> list[str]:
        path = inside(self.root, "accepted/removals.json")
        if not path.is_file():
            return []
        data = preflight._read_json(str(path))
        if set(data) != {"schema_version", "paths"} or data["schema_version"] != 1 or not isinstance(data["paths"], list):
            raise RunError("accepted removal manifest is malformed")
        for name in data["paths"]:
            relative(name)
        return list(data["paths"])

    def accepted_manifest(self) -> dict[str, Any] | None:
        path = inside(self.root, "accepted/manifest.json")
        return preflight._read_json(str(path)) if path.is_file() else None

    def accepted_file_hashes(self) -> dict[str, str]:
        manifest = self.accepted_manifest()
        if manifest is None:
            base = inside(self.root, "accepted/files")
            return tree_hashes(base) if base.is_dir() else {}
        if (
            manifest.get("schema_version") != 2
            or manifest.get("layout") != "content-addressed-blobs"
            or not isinstance(manifest.get("files"), dict)
        ):
            raise RunError("accepted manifest is malformed")
        files: dict[str, str] = {}
        for name, sha in manifest["files"].items():
            relative(name)
            if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{64}", sha):
                raise RunError(f"accepted manifest entry is malformed: {name}")
            files[name] = sha
        return files

    def read_accepted(self, name: str) -> bytes:
        """Bytes of one accepted file under either store layout (legacy fallback)."""
        manifest = self.accepted_manifest()
        if manifest is not None:
            sha = self.accepted_file_hashes().get(name)
            if sha is None:
                raise RunError(f"accepted file is not in the manifest: {name}")
            blob = inside(self.root, f"accepted/blobs/{sha}")
            if not blob.is_file():
                raise RunError(f"accepted blob is missing: {name} ({sha[:12]})")
            data = blob.read_bytes()
            if hashlib.sha256(data).hexdigest() != sha:
                raise RunError(f"accepted blob is damaged: {name} ({sha[:12]})")
            return data
        path = inside(self.root, f"accepted/files/{name}")
        if not path.is_file():
            raise RunError(f"accepted file is missing: {name}")
        return path.read_bytes()

    def accepted_content(self) -> dict[str, bytes]:
        return {name: self.read_accepted(name) for name in sorted(self.accepted_file_hashes())}

    def accepted_fingerprint(self) -> str:
        payload = {"files": self.accepted_file_hashes(), "removals": self.accepted_removals()}
        return "sha256:" + hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()

    def apply_accepted(self, tree: Path) -> None:
        for name in self.accepted_removals():
            inside(tree, name).unlink(missing_ok=True)
        for name in sorted(self.accepted_file_hashes()):
            target = inside(tree, name)
            target.parent.mkdir(parents=True, exist_ok=True)
            atomic_write(target, self.read_accepted(name))

    def copy_working_base(self, tree: Path, integration: bool = False) -> None:
        domains = [p.name for p in (self.repo / "library").iterdir() if p.is_dir()] if integration else [self.domain, "metaskills"]
        for domain in domains:
            source = inside(self.repo, f"library/{domain}")
            tree_hashes(source)
            shutil.copytree(source, tree / "library" / domain)
        recipes = self.repo / "workspace" / "release-recipes"
        if recipes.is_dir():
            for path in sorted(recipes.glob("SkillForge_*.yaml")):
                spec = preflight.yaml.safe_load(path.read_text(encoding="utf-8"))
                modules = spec.get("modules") if isinstance(spec, dict) else None
                if isinstance(modules, list) and any(str(m).split("/")[0] == self.domain for m in modules):
                    target = tree / "workspace" / "release-recipes" / path.name
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(path, target)
        self.apply_accepted(tree)

    @contextmanager
    def accepted_overlay(self, integration: bool = False):
        with tempfile.TemporaryDirectory(prefix="pass-accepted-overlay-") as temporary:
            # Windows may return an 8.3 path here while copied/indexed children
            # resolve to the long spelling. Canonicalize the root before any
            # lexical relative_to checks compare those paths.
            tree = Path(temporary).resolve()
            self.copy_working_base(tree, integration=integration)
            yield tree

    def working_cards(self) -> dict[str, preflight.CardRef]:
        with self.accepted_overlay() as tree:
            return preflight.load_domain_cards(tree, self.domain)

    def persist_accepted_delta(self, tree: Path) -> tuple[int, int]:
        """Replace accepted/ with the complete source delta versus live canon."""
        files: dict[str, bytes] = {}
        removals: list[str] = []
        roots = [f"library/{self.domain}"]
        recipe_dir = tree / "workspace" / "release-recipes"
        if recipe_dir.is_dir():
            roots.extend((p.relative_to(tree).as_posix() for p in recipe_dir.glob("SkillForge_*.yaml")))
        for root_name in roots:
            live_root = inside(self.repo, root_name)
            staged_root = inside(tree, root_name)
            if staged_root.is_file():
                live_bytes = live_root.read_bytes() if live_root.is_file() else None
                if live_bytes != staged_root.read_bytes():
                    files[root_name] = staged_root.read_bytes()
                continue
            live_map = tree_hashes(live_root) if live_root.is_dir() else {}
            staged_map = tree_hashes(staged_root) if staged_root.is_dir() else {}
            for rel, sha in staged_map.items():
                target = f"{root_name}/{rel}"
                if live_map.get(rel) != sha:
                    files[target] = inside(staged_root, rel).read_bytes()
            for rel in live_map:
                if rel not in staged_map:
                    removals.append(f"{root_name}/{rel}")
        fresh = inside(self.root, "accepted.new")
        current = self.accepted_root()
        retired = inside(self.root, "accepted.old")
        for path in (fresh, retired):
            if path.exists():
                shutil.rmtree(path)
        fresh.mkdir(parents=True)
        file_shas: dict[str, str] = {}
        for name, content in sorted(files.items()):
            sha = hashlib.sha256(content).hexdigest()
            file_shas[name] = sha
            blob = fresh / "blobs" / sha
            validate_windows_path_budget(blob, f"accepted blob {sha}")
            blob.parent.mkdir(parents=True, exist_ok=True)
            atomic_write(blob, content)
        manifest_record = {
            "schema_version": 2,
            "layout": "content-addressed-blobs",
            "files": file_shas,
        }
        atomic_write(fresh / "manifest.json", (json.dumps(manifest_record, indent=2) + "\n").encode("utf-8"))
        atomic_write(fresh / "removals.json", (json.dumps({"schema_version": 1, "paths": sorted(set(removals))}, indent=2) + "\n").encode("utf-8"))
        # Verify before promotion.
        for name, content in files.items():
            blob = fresh / "blobs" / file_shas[name]
            if not blob.is_file() or blob.read_bytes() != content:
                raise RunError(f"accepted delta verification failed: {name}")
        if preflight._read_json(str(fresh / "manifest.json")) != manifest_record:
            raise RunError("accepted delta manifest verification failed")
        if current.exists():
            current.rename(retired)
        fresh.rename(current)
        if retired.exists():
            shutil.rmtree(retired)
        return len(files), len(set(removals))

    @contextmanager
    def overlay(self, integration: bool = False):
        with tempfile.TemporaryDirectory(prefix="pass-authoring-overlay-") as temporary:
            tree = Path(temporary).resolve()
            self.copy_working_base(tree, integration=integration)
            for name in self.state["pass2"]["removals"]:
                inside(tree, self.removal_target(name)).unlink(missing_ok=True)
            for name in self.state["pass2"]["changes"]:
                target = inside(tree, self.target(name))
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(inside(self.root, name), target)
            yield tree

    def tool(self, name: str, tree: Path, *arguments: str) -> None:
        result = subprocess.run(
            [sys.executable, str(self.repo / "PASS/tools" / name), "--library", str(tree / "library"), *arguments],
            capture_output=True, text=True, encoding="utf-8", env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
        if result.returncode:
            raise RunError(f"{name} failed against live-library overlay:\n{result.stdout}\n{result.stderr}")

    def validate(self, tree: Path) -> None:
        self.tool("validate.py", tree)
        self.tool("verify_references.py", tree)
        # Reuse the canonical tool APIs in a separate process: their imports
        # expect PASS/tools on sys.path, which must not leak into this runtime.
        # Existing relation migration debt may survive untouched; edited cards
        # and newly introduced edges must satisfy today's relation contract.
        audit = '''
import json, sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
import validate, build_release
library, baseline = Path(sys.argv[2]), Path(sys.argv[3])
changed, recipes = json.loads(sys.argv[4]), json.loads(sys.argv[5])
records = validate.validate_library(library)
old = [validate.parse_object(p, baseline) for d in library.iterdir() if d.is_dir()
       for p in validate.discover_objects(baseline / d.name)]
existing = set(validate.relation_problems(old))
problems = [(p, e) for p, e in validate.relation_problems(records)
            if p in changed or (p, e) not in existing]
if problems:
    raise ValueError("relation contract: " + repr(problems))
modules = build_release.discover(library)
by_id, owner = build_release.object_index(library, modules)
for name in recipes:
    spec = build_release.read_yaml(Path(name))
    entries = build_release.recipe_modules(spec)
    selected = build_release.resolve(entries, modules, by_id, owner)
    if any(build_release.module_domain(m) not in {sys.argv[6], "metaskills"} for m in selected):
        raise ValueError("canonical recipe prerequisite closure crossed domains")
    available = {m for m in modules if build_release.module_domain(m) == sys.argv[6]}
    if {m for m in entries if build_release.module_domain(m) == sys.argv[6]} != available:
        raise ValueError("canonical recipe must explicitly cover every active-domain module")
'''
        changes = self.state["pass2"]["changes"]
        changed = [self.target(p).removeprefix("library/") for p in changes if p.endswith(".md")]
        recipes = [str(inside(tree, self.target(p))) for p in changes if p.startswith("recipes/")]
        result = subprocess.run(
            [sys.executable, "-c", audit, str(self.repo / "PASS/tools"), str(tree / "library"),
             str(self.repo / "library"), json.dumps(changed), json.dumps(recipes), self.domain],
            capture_output=True, text=True, encoding="utf-8", env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
        if result.returncode:
            raise RunError(f"identity/relation/release closure audit failed:\n{result.stdout}\n{result.stderr}")

    def preflight_quality_audit(self, record: preflight.PreflightRecord | None = None) -> dict:
        """Return deterministic Source Prep + unit-boundary review gates."""
        if not self.state.get("source_prep"):
            return {
                "source_integrity": "not_applicable",
                "source_review": [],
                "boundary": {"status": "pass", "blocking": [], "review": []},
            }
        from .pass_source_prep import audit_unit_boundaries, verify

        manifest = verify(self)
        gate = manifest.get("integrity_gate") or {}
        source_review = list(gate.get("review_requirements") or [])
        # Prepared packages from beta.80-beta.86 did not have an explicit
        # review_required field. Preserve their warning evidence and upgrade
        # known code/table sanity warnings into the new acceptance gate instead
        # of silently treating a legacy package as cleaner than a fresh one.
        if int(manifest.get("schema_version", 0) or 0) < 5 and not source_review:
            for item in list(gate.get("warnings") or []):
                warning = str(item.get("warning") or "")
                if any(marker in warning for marker in (
                    "code-like/preformatted",
                    "code sanity check",
                    "table sanity check",
                    "zero structured tables",
                )):
                    source_review.append({"page": item.get("page"), "requirement": warning})
        if record is None:
            if self.state.get("plan") is None:
                boundary = {"status": "pass", "blocking": [], "review": []}
            else:
                record = preflight.parse_preflight(self.state["plan"])
                boundary = audit_unit_boundaries(self, record)
        else:
            boundary = audit_unit_boundaries(self, record)
        return {
            "source_integrity": gate.get("status", "pass"),
            "source_review": source_review,
            "boundary": boundary,
        }

    def enforce_preflight_quality(self, record: preflight.PreflightRecord) -> dict:
        audit = self.preflight_quality_audit(record)
        blocking = list((audit.get("boundary") or {}).get("blocking") or [])
        if blocking:
            detail = "; ".join(item.get("message", "boundary defect") for item in blocking[:4])
            raise RunError(
                "preflight unit-boundary gate failed; revise the source-wide plan before presentation: " + detail
            )
        return audit

    def validate_preflight_source_coordinates(self, record: preflight.PreflightRecord) -> None:
        """Validate machine-authoritative source coordinates before presentation.

        Prepared PDF runs must never reach the user-acceptance gate with unit
        boundaries that the materializer cannot resolve deterministically. New
        schema-v2 plans carry structured ``source_pages``; legacy schema-v1
        plans remain resumable but their prose locators must resolve
        unambiguously to explicit PDF/source coordinates.
        """
        if not self.state.get("source_prep"):
            return
        from .pass_source_prep import locator_pages, verify

        manifest = verify(self)
        if manifest.get("source_kind") != "pdf":
            return
        page_count = len(manifest.get("segments") or [])
        if page_count < 1:
            raise RunError("prepared PDF manifest has no source segments")

        for unit in record.units:
            if record.schema_version >= 2:
                span = unit.source_pages
                if span is None:
                    raise RunError(
                        f"preflight {unit.unit_id} requires machine-readable source_pages for a prepared PDF; "
                        "printed pagination and locator prose are display metadata only"
                    )
                if span.start < 1 or span.end < span.start or span.end > page_count:
                    raise RunError(
                        f"preflight {unit.unit_id} source_pages {span.start}-{span.end} fall outside prepared PDF "
                        f"1-{page_count}"
                    )
            else:
                pages = locator_pages(unit.locator, page_count)
                if not pages:
                    raise RunError(
                        f"legacy preflight {unit.unit_id} locator is ambiguous or outside prepared PDF: {unit.locator!r}; "
                        "revise with schema_version 2 and explicit source_pages before presentation"
                    )

    def revise_preflight(self, data: dict) -> str:
        if self.state["phase"] != "preflight_accept":
            raise RunError("preflight can be revised only while it is awaiting acceptance")
        record = preflight.parse_preflight(data)
        if record.domain != self.domain:
            raise RunError("preflight revision cannot change the run's authorized domain")
        if record.mode != "unit ingestion":
            raise RunError("controller orchestration currently supports unit ingestion only; curriculum audit requires its own scope contract")
        preflight.validate_against_library(record, self.repo)
        self.validate_preflight_source_coordinates(record)
        self.enforce_preflight_quality(record)
        self.clear_preflight_presentation()
        # Do not let a schema-3 Software Engineering plan silently fall back to
        # a legacy shape during revision; that would discard the language policy.
        if self.domain == "software-engineering" and self.state["plan"].get("schema_version", 1) >= 3 and record.schema_version < 3:
            raise RunError("a schema-3 software-engineering preflight revision must retain schema_version 3 and its language_policy")
        self.state["plan"] = preflight.serialize_preflight(record)
        self.save()
        return "PREFLIGHT REVISION: validated — present the replacement packet for user confirmation"

    def accept_preflight(self, decision: dict) -> str:
        if self.state["phase"] != "preflight_accept":
            raise RunError("preflight acceptance is available only after a validated preflight is awaiting confirmation")
        exact(decision, {"schema_version", "presentation_sha256", "subject", "basis", "reason"}, "preflight acceptance")
        if type(decision["schema_version"]) is not int or decision["schema_version"] != 1:
            raise RunError("preflight acceptance schema_version must be integer 1")
        marker = self.preflight_presentation_marker(required=True)
        current_packet_sha = hashlib.sha256(self.render_preflight_packet().encode("utf-8")).hexdigest()
        if decision["presentation_sha256"] != marker["sha256"] or marker["sha256"] != current_packet_sha:
            raise RunError("preflight acceptance is not bound to the current complete presentation packet; run present again")
        subject = string(decision["subject"], "preflight acceptance subject")
        if subject != self.state["plan"]["subject"]:
            raise RunError("preflight acceptance must repeat the exact presented instructional subject")
        if decision["basis"] == "unattended authorization":
            self.unattended_authorization(required=True)
            audit = self.preflight_quality_audit(preflight.parse_preflight(self.state["plan"]))
            source_review = list(audit.get("source_review") or [])
            boundary_review = list((audit.get("boundary") or {}).get("review") or [])
            if source_review or boundary_review:
                raise RunError(
                    "preflight requires explicit human/frontier review because Source Prep or unit-boundary integrity warnings remain; "
                    "unattended authorization may not auto-accept this plan"
                )
        elif decision["basis"] != "user confirmation":
            raise RunError(
                "preflight acceptance requires explicit user confirmation or a recorded source-scoped unattended authorization; "
                "do not infer either from the request to run PASS"
            )
        string(decision["reason"], "preflight acceptance reason")
        self.state["phase"] = "pass1"
        self.clear_preflight_presentation()
        # Build deterministic unit files from prepared page segments whenever
        # the accepted locators are machine-readable. Unsupported locators remain
        # routable through the prepared page index without falsifying boundaries.
        if self.state.get("source_prep"):
            from .pass_source_prep import materialize_units, verify
            materialize_units(self)
            manifest = verify(self)
            self.state["source_prep"]["package_sha256"] = manifest["package_sha256"]
        if self.state.get("stop_after") == "preflight":
            self.state["stop_reached"] = True
        self.save()
        suffix = " (stop target reached before unit ingestion)" if self.state.get("stop_reached") else f" — PASS 1 released — {self.unit()['unit_id'].upper()}"
        return "PREFLIGHT ACCEPTED: subject and source-wide plan confirmed" + suffix

    def land(self, decision: dict) -> str:
        # Independent books may stage in parallel, but only one unit in a domain
        # may integrate at a time. This lease contains no research/run state.
        lease = inside(self.repo, f"{RUN_STORE}/.landing-{self.domain}.lock")
        try:
            descriptor = os.open(lease, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError as exc:
            raise RunError("another book owns this domain's landing lease; retry after it finishes and reconcile any live changes") from exc
        os.close(descriptor)
        try:
            return self._land(decision)
        finally:
            lease.unlink(missing_ok=True)

    def canonical_journal_path(self) -> Path:
        return inside(self.root, "controller/canonical-commit")

    def begin_canonical_journal(self, writes: dict[str, bytes], removals: list[str]) -> None:
        current = self.canonical_journal_path()
        if current.exists():
            raise RunError("a canonical commit journal already exists; recover the interrupted transaction before closing")
        fresh = inside(self.root, "controller/canonical-commit.new")
        if fresh.exists():
            shutil.rmtree(fresh)
        fresh.mkdir(parents=True)
        entries = []
        for name in sorted(set(writes) | set(removals)):
            target = inside(self.repo, name)
            before_exists = target.is_file()
            before_sha = digest(target) if before_exists else None
            if before_exists:
                backup = fresh / "before" / name
                backup.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(target, backup)
            entries.append({
                "path": name,
                "before_exists": before_exists,
                "before_sha256": before_sha,
                "after_sha256": hashlib.sha256(writes[name]).hexdigest() if name in writes else None,
            })
        record = {"schema_version": 1, "created_at": now(), "entries": entries}
        atomic_write(fresh / "manifest.json", (json.dumps(record, indent=2) + "\n").encode("utf-8"))
        for entry in entries:
            if entry["before_exists"]:
                backup = fresh / "before" / entry["path"]
                if not backup.is_file() or digest(backup) != entry["before_sha256"]:
                    raise RunError(f"canonical commit journal failed verification: {entry['path']}")
        fresh.rename(current)

    def canonical_journal_after_valid(self) -> bool:
        journal = self.canonical_journal_path()
        if not journal.is_dir():
            return True
        manifest = preflight._read_json(str(journal / "manifest.json"))
        if manifest.get("schema_version") != 1 or not isinstance(manifest.get("entries"), list):
            return False
        for entry in manifest["entries"]:
            target = inside(self.repo, entry["path"])
            after = entry.get("after_sha256")
            if after is None:
                if target.exists():
                    return False
            elif not target.is_file() or digest(target) != after:
                return False
        return True

    def rollback_canonical_journal(self) -> None:
        journal = self.canonical_journal_path()
        if not journal.is_dir():
            return
        manifest = preflight._read_json(str(journal / "manifest.json"))
        if manifest.get("schema_version") != 1 or not isinstance(manifest.get("entries"), list):
            raise RunError("canonical commit journal is malformed; refusing automatic recovery")
        for entry in manifest["entries"]:
            target = inside(self.repo, entry["path"])
            if entry["before_exists"]:
                backup = journal / "before" / entry["path"]
                if not backup.is_file() or digest(backup) != entry["before_sha256"]:
                    raise RunError(f"canonical rollback backup is damaged: {entry['path']}")
                atomic_write(target, backup.read_bytes())
            else:
                target.unlink(missing_ok=True)
        for entry in manifest["entries"]:
            target = inside(self.repo, entry["path"])
            if entry["before_exists"]:
                if not target.is_file() or digest(target) != entry["before_sha256"]:
                    raise RunError(f"canonical rollback verification failed: {entry['path']}")
            elif target.exists():
                raise RunError(f"canonical rollback failed to remove: {entry['path']}")
        shutil.rmtree(journal)

    def commit_accepted_to_canon(self) -> tuple[int, int]:
        writes: dict[str, bytes] = self.accepted_content()
        removals = self.accepted_removals()
        self.begin_canonical_journal(writes, removals)
        try:
            for name in removals:
                inside(self.repo, name).unlink(missing_ok=True)
            for name, content in writes.items():
                atomic_write(inside(self.repo, name), content)
            for name, content in writes.items():
                target = inside(self.repo, name)
                if not target.is_file() or target.read_bytes() != content:
                    raise RunError(f"canonical close verification failed: {name}")
            for name in removals:
                if inside(self.repo, name).exists():
                    raise RunError(f"canonical close removal verification failed: {name}")
        except BaseException:
            self.rollback_canonical_journal()
            raise
        return len(writes), len(removals)

    def _land(self, decision: dict) -> str:
        if self.state["phase"] not in {"land", "closure_land"}:
            raise RunError("delta cannot land or advance before PASS 3 and mechanical validation pass")
        self.header(decision, {"presentation_sha256", "basis", "reason"})
        marker = self.presentation_marker(required=True)
        current_packet_sha = hashlib.sha256(self.render_land_packet().encode("utf-8")).hexdigest()
        if decision["presentation_sha256"] != marker["sha256"] or marker["sha256"] != current_packet_sha:
            raise RunError("landing decision is not bound to the current complete presentation packet; run present again")
        if not isinstance(decision["basis"], str) or decision["basis"] not in {"user approval", "evidence", "unattended authorization"}:
            raise RunError("landing decision requires user approval, an evidence-settled basis, or recorded unattended authorization")
        string(decision["reason"], "landing reason")
        if decision["basis"] == "unattended authorization":
            self.unattended_authorization(required=True)
            if self.state["pass2"]["approval_required"]:
                raise RunError("this delta requires practitioner approval; unattended authorization may not consume it")
        if self.state["pass2"]["approval_required"] and decision["basis"] != "user approval":
            raise RunError("this delta requires practitioner approval; evidence cannot substitute for it")
        self.check_live()
        if self.staged_hashes() != self.state["reviewed_sha256"]:
            rewind_phase = "closure_pass3" if self.state["phase"] == "closure_land" else "pass3"
            raise RunError(f"staged files changed after PASS 3; rewind to {rewind_phase} and rescan")
        self.check_change_set(self.state["pass2"])
        old_state = json.loads(json.dumps(self.state))
        unit = self.unit()["unit_id"]
        is_closure = self.state["phase"] == "closure_land"
        accepted_counts = (0, 0)
        try:
            with self.overlay(integration=True) as tree:
                self.validate(tree)
                # Generated indexes belong to the cumulative source delta, not
                # live canon, until the deliberate source close transaction.
                for path in (tree / "library" / self.domain).rglob("INDEX.md"):
                    path.unlink()
                self.tool("build_index.py", tree, "--package", self.domain)
                accepted_counts = self.persist_accepted_delta(tree)
            if not self.canonical_live_unchanged():
                raise RunError("canonical domain/prerequisites changed during integration validation; repeat PASS 2/PASS 3")
            if self.staged_hashes() != self.state["reviewed_sha256"]:
                raise RunError("staged files changed during integration validation; repeat PASS 3")
            if is_closure:
                writes, removals = self.commit_accepted_to_canon()
                self.state.update(pass1=None, pass2=None, reviewed_sha256=None, live_hashes=None, phase="finished")
            else:
                writes, removals = accepted_counts
                self.state.update(unit_index=self.state["unit_index"] + 1, pass1=None, pass2=None, reviewed_sha256=None, live_hashes=None)
                self.state["phase"] = "closure_pass2" if self.state["unit_index"] == len(self.state["plan"]["units"]) else "pass1"
            self.save()
            history_path = self.archive_land_record(unit, old_state, decision, writes, removals, is_closure)
            report_path = self.write_transition_report(unit, writes, removals, is_closure)
            self.clear_presentation()
        except BaseException:
            self.state = old_state
            # If final canonicalization began, revert it before returning failure.
            self.rollback_canonical_journal()
            raise
        cleanup = []
        for name in old_state["pass2"]["changes"]:
            try:
                inside(self.root, name).unlink()
            except OSError:
                cleanup.append(name)
        suffix = f"; retained scratch needs cleanup: {', '.join(cleanup)}" if cleanup else ""
        evidence = f"; audit={history_path.relative_to(self.root).as_posix()}; state_report={report_path.relative_to(self.root).as_posix()}"
        if is_closure:
            return f"SOURCE CLOSED: staged source delta canonicalized ({writes} writes, {removals} removals; no Git commit created){suffix}{evidence}"
        return f"UNIT ACCEPTED TO SKILL-STAGING: {unit.upper()} ({writes} staged writes, {removals} staged removals){suffix}{evidence}"

    def reopen_last_unit(self, reason: str) -> str:
        """Reopen the immediately previous accepted unit for a bounded correction pass."""
        string(reason, "reopen reason")
        if self.state["unit_index"] <= 0:
            raise RunError("no previously accepted unit exists to reopen")
        if self.state["phase"] not in {"pass1", "closure_pass2"}:
            raise RunError("reopen-last-unit is allowed only before the next unit has accepted PASS 1 or before closure work begins")
        if self.state.get("pass1") is not None or self.state.get("pass2") is not None:
            raise RunError("current unit already has accepted work; finish or explicitly reset it before reopening the prior unit")
        if any(path.is_file() for path in (self.root / "drafts").rglob("*")):
            raise RunError("unaccepted drafts exist for the current unit; preserve or remove them explicitly before reopening the prior unit")
        previous_index = self.state["unit_index"] - 1
        unit_id = self.state["plan"]["units"][previous_index]["unit_id"]
        base = self.unit_history_root(unit_id)
        revisions = sorted((path for path in base.iterdir() if path.is_dir() and re.fullmatch(r"r\d{3}", path.name)), key=lambda path: path.name) if base.is_dir() else []
        landed = [path for path in revisions if (path / "land.json").is_file()]
        if not landed:
            raise RunError(f"no preserved accepted history exists for {unit_id}; this run predates the supported correction path")
        last = preflight._read_json(str(landed[-1] / "land.json"))
        if not isinstance(last.get("pass1"), dict):
            raise RunError("accepted unit history has no reusable PASS 1 record")
        self.clear_presentation()
        self.unattended_action_path().unlink(missing_ok=True)
        self.state.update(
            unit_index=previous_index,
            pass1=last["pass1"],
            pass2=None,
            reviewed_sha256=None,
            live_hashes=None,
            phase="pass2",
        )
        revision = self.history_revision_dir(unit_id, create=True)
        superseded_packet_sha = None
        if isinstance(last.get("landing_decision"), dict):
            superseded_packet_sha = last["landing_decision"].get("presentation_sha256")
        audit_packet = inside(self.root, f"controller/audit/{unit_id.lower()}-landing.md")
        if audit_packet.is_file():
            actual_packet_sha = digest(audit_packet)
            if superseded_packet_sha and actual_packet_sha != superseded_packet_sha:
                raise RunError("preserved landing packet no longer matches the accepted landing decision hash")
            superseded_packet_sha = actual_packet_sha
        record = {
            "schema_version": 2,
            "unit_id": unit_id,
            "reason": reason,
            "opened_at": now(),
            "from_revision": landed[-1].name,
            "superseded_landing_packet_sha256": superseded_packet_sha,
            "superseded_accepted_delta_fingerprint": last.get("accepted_delta_fingerprint") or self.accepted_fingerprint(),
            "required_rechecks": ["pass2", "pass3", "land"],
        }
        # EXP-003 Target E: materialize the accepted source delta into drafts so
        # the correction pass starts from the run's own current card versions
        # instead of requiring manual restaging. Baseline hashes are recorded so
        # close-run can discard untouched copies while retaining user edits.
        baseline: dict[str, str] = {}
        for canon in sorted(self.accepted_file_hashes()):
            staged = self.baseline_staged_path(canon)
            if staged is None:
                continue
            content = self.read_accepted(canon)
            target = inside(self.root, staged)
            if target.is_file():
                raise RunError(f"cannot materialize amendment baseline; drafts already hold {staged}")
            validate_windows_path_budget(target, f"amendment baseline {staged}")
            target.parent.mkdir(parents=True, exist_ok=True)
            atomic_write(target, content)
            baseline[staged] = hashlib.sha256(content).hexdigest()
        record["materialized_baseline"] = baseline
        atomic_write(inside(revision, "amendment.json"), (json.dumps(record, indent=2) + "\n").encode("utf-8"))
        if baseline:
            atomic_write(inside(self.root, "controller/amendment-baseline.json"), (json.dumps({
                "schema_version": 1,
                "unit_id": unit_id,
                "revision": landed[-1].name,
                "files": baseline,
            }, indent=2) + "\n").encode("utf-8"))
        # Keep the EXP-001 filename as an explicit compatibility breadcrumb.
        atomic_write(inside(revision, "reopen.json"), (json.dumps({
            "schema_version": 1, "unit_id": unit_id, "reason": reason,
            "reopened_at": record["opened_at"], "from_revision": landed[-1].name
        }, indent=2) + "\n").encode("utf-8"))
        self.save()
        materialized = f"; {len(baseline)} baseline card(s) materialized into drafts from the accepted source delta" if baseline else ""
        return (f"UNIT REOPENED / AMENDMENT OPENED: {unit_id.upper()} — original landing hash/fingerprint preserved; "
                "PASS 2, PASS 3, and land must run again against the accepted staging baseline"
                + materialized)

    def rewind(self, phase: str) -> None:
        if phase not in {"pass1", "pass2", "pass3", "closure_pass2", "closure_pass3"}:
            raise RunError("rewind supports only pass1/pass2/pass3 or closure_pass2/closure_pass3")
        if self.state["phase"] in {"load", "preflight", "preflight_accept", "finished"}:
            raise RunError("no accepted active unit can be rewound")
        self.clear_presentation()
        if phase == "pass1":
            self.state.update(pass1=None, pass2=None, live_hashes=None, reviewed_sha256=None)
        elif phase == "pass2":
            if self.state["pass1"] is None or (self.state["pass1"]["questions"] and "answers" not in self.state["pass1"]):
                raise RunError("PASS 1 and any checkpoint must pass before PASS 2")
            self.state.update(pass2=None, live_hashes=None, reviewed_sha256=None)
        elif phase in {"pass3", "closure_pass3"}:
            if self.state["pass2"] is None:
                raise RunError("PASS 2 must pass before PASS 3")
            self.check_live()
            self.state["reviewed_sha256"] = None
        self.state["phase"] = phase
        self.save()

    def replan(self, data: dict) -> None:
        if self.state["phase"] != "pass1":
            raise RunError("unit structure may be amended only before accepting the active unit's PASS 1")
        exact(data, {"schema_version", "reason", "preflight"}, "unit-plan amendment (not a new preflight)")
        if type(data["schema_version"]) is not int or data["schema_version"] != 1:
            raise RunError("amendment schema_version must be integer 1")
        string(data["reason"], "instructional boundary evidence")
        if not isinstance(data["preflight"], dict):
            raise RunError("amendment must contain the complete accepted-plan-shaped record; replan does not authorize another preflight read")
        record = preflight.parse_preflight(data["preflight"])
        plan = preflight.serialize_preflight(record)
        original = self.state["plan"]
        immutable_keys = set(original) - {"units", "no_extract"}
        if set(plan) - {"units", "no_extract"} != immutable_keys:
            raise RunError("unit-plan amendment cannot change preflight schema/policy shape")
        for key in immutable_keys:
            if plan[key] != original[key]:
                raise RunError("unit-plan amendment cannot change the source, subject or authorized domain; replan is not a new preflight")
        closed = self.state["unit_index"]
        if len(plan["units"]) <= closed or plan["units"][:closed] != original["units"][:closed]:
            raise RunError("closed units cannot be rewritten or removed")
        preflight.validate_against_library(record, self.repo)
        self.state["plan"] = plan
        self.save()

    def close(self) -> None:
        if self.state["phase"] != "finished":
            raise RunError("cannot close the source run while any unit remains unfinished")
        # Defense in depth behind locked()'s uniform residue gate: close never
        # silently sweeps unresolved checkpoint-promotion state.
        residue = checkpoint_residue(self.root)
        if any(residue.values()):
            raise RunError(
                "checkpoint residue must be resolved before close-run "
                f"({json.dumps(residue, sort_keys=True)}); run repair-checkpoint first"
            )
        # Amendment-baseline drafts: untouched controller-copied scratch is
        # disposable; anything the user edited is retained work (EXP-003 Target G).
        baseline_path = inside(self.root, "controller/amendment-baseline.json")
        if baseline_path.is_file():
            baseline = preflight._read_json(str(baseline_path))
            entries = baseline.get("files") if isinstance(baseline, dict) else None
            if isinstance(entries, dict):
                for staged, sha in entries.items():
                    relative(staged)
                    path = inside(self.root, staged)
                    if path.is_file() and isinstance(sha, str) and digest(path) == sha:
                        path.unlink()
            baseline_path.unlink(missing_ok=True)
        # Remove only controller-owned generated state. Unknown files are retained
        # so an explicit diagnosis/evidence hold cannot be swept accidentally.
        for name in (
            "controller/run.json",
            "controller/source-identity.json",
            "controller/unattended-authorization.json",
            "controller/preflight-presentation.json",
            "controller/landing-presentation.json",
            "controller/source-completion.json",
            "controller/next-action.json",
            "controller/operation.lock",
        ):
            inside(self.root, name).unlink(missing_ok=True)
        history = inside(self.root, "controller/action-history")
        if history.is_dir():
            for path in history.glob("*.json"):
                inside(history, path.name).unlink(missing_ok=True)
            if not any(history.iterdir()):
                history.rmdir()
        audit = inside(self.root, "controller/audit")
        if audit.is_dir():
            # Remove only controller-owned audit artifacts. Unknown files may be
            # explicit evidence holds and must survive close-run.
            owned = [
                "events.jsonl", "preflight.md", "preflight.json",
                "final-validate.txt", "final-verify-references.txt",
            ]
            owned.extend(path.name for path in audit.glob("*-landing.md"))
            owned.extend(path.name for path in audit.glob("*-landing.json"))
            owned.extend(path.name for path in audit.glob("*-state-report.json"))
            for name in sorted(set(owned)):
                inside(audit, name).unlink(missing_ok=True)
            if not any(audit.iterdir()):
                audit.rmdir()
        unit_history = inside(self.root, "controller/unit-history")
        if unit_history.is_dir():
            shutil.rmtree(unit_history)
        inside(self.root, "RUN_NOTE.md").unlink(missing_ok=True)
        for generated_dir in ("accepted", "prepared-source", "controller/source-prep-raw", "controller/canonical-commit"):
            path = inside(self.root, generated_dir)
            if path.is_dir():
                shutil.rmtree(path)
        checkpoint = inside(self.root, CHECKPOINT)
        if checkpoint.is_dir():
            shutil.rmtree(checkpoint)
        handoff = inside(self.root, "HANDOFF.md")
        if handoff.is_file() and HANDOFF_MARK in handoff.read_text(encoding="utf-8"):
            handoff.unlink()


def _lock_pid_alive(lock: Path) -> tuple[int, bool]:
    """Return the recorded PASS pid and whether it still appears to be alive."""
    try:
        owner = preflight._read_json(str(lock))
        pid = int(owner.get("pid", -1))
    except Exception:
        return -1, False
    if pid <= 0 or pid == os.getpid():
        return pid, False
    try:
        os.kill(pid, 0)
        return pid, True
    except (OSError, ProcessLookupError, PermissionError):
        return pid, False


def _load_start_over_state(root: Path) -> dict:
    """Load the state snapshot that an interrupted start-over transaction owns."""
    intent_path = inside(root, RESET_INTENT)
    if intent_path.is_file():
        intent = preflight._read_json(str(intent_path))
        exact(
            intent,
            {
                "schema_version", "requested_at", "reason", "restart_from",
                "carry_notes", "new_task", "replacement_run", "domain", "source", "state",
            },
            "start-over intent",
        )
        if intent["schema_version"] != 1 or not isinstance(intent["state"], dict):
            raise RunError("start-over intent is malformed")
        return intent
    state_path = inside(root, "controller/run.json")
    if state_path.is_file():
        state = preflight._read_json(str(state_path))
        return {
            "schema_version": 1,
            "requested_at": None,
            "reason": None,
            "restart_from": None,
            "carry_notes": None,
            "new_task": None,
            "replacement_run": None,
            "domain": state.get("domain"),
            "source": state.get("source"),
            "state": state,
        }
    abandoned = inside(root, ABANDONED)
    if abandoned.is_file():
        record = preflight._read_json(str(abandoned))
        state = record.get("state")
        if isinstance(state, dict):
            reset = record.get("start_over") or {}
            return {
                "schema_version": 1,
                "requested_at": reset.get("requested_at"),
                "reason": record.get("reason"),
                "restart_from": reset.get("restart_from"),
                "carry_notes": reset.get("carry_notes"),
                "new_task": reset.get("new_task"),
                "replacement_run": reset.get("replacement_run"),
                "domain": state.get("domain"),
                "source": state.get("source"),
                "state": state,
            }
    raise RunError("start-over requires an active or interrupted run with recoverable controller state")


def start_over(
    repo: Path,
    root: Path,
    reason: str,
    restart_from: str = "scratch",
    carry_notes: bool = False,
    task: str | None = None,
) -> dict:
    """Authoritatively abandon one run and create a fresh run from an explicit boundary.

    This command exists so a model never has to infer whether "start over" means
    resume, recover, rewind, or reuse a checkpoint.  User-requested reset is a
    controller transition: prior checkpoints become ineligible before a new run
    is created.  A durable reset-intent marker prevents an interrupted old
    process from resurrecting run.json after reset begins.
    """
    repo = repo.resolve()
    root = run_root(repo, root)
    reason = string(reason, "start-over reason")
    if restart_from not in {"scratch", "source_prep", "preflight"}:
        raise RunError("start-over --from must be scratch, source_prep, or preflight")

    seed = _load_start_over_state(root)
    state = seed["state"]
    prior_manifest = read_run_manifest(root, required=False)
    prior_genre = prior_manifest["genre"] if prior_manifest is not None else None
    domain = state.get("domain")
    source_text = state.get("source")
    if not isinstance(domain, str) or domain not in authorable_domains(repo):
        raise RunError("start-over cannot identify the old run's authorized domain")
    if not isinstance(source_text, str) or not source_text:
        raise RunError("start-over cannot identify the old run's bound source")
    source = Path(source_text).resolve()
    if not source.is_file():
        raise RunError("start-over requires the original bound source bytes to still exist")
    if state.get("phase") == "finished":
        raise RunError("a finished run is closed with close-run, not started over")

    existing_intent = inside(root, RESET_INTENT)
    if existing_intent.is_file():
        # Resume only the same authoritative reset transaction.  Changing the
        # requested boundary mid-transaction would make carry semantics unclear.
        if (
            seed["reason"] != reason
            or seed["restart_from"] != restart_from
            or bool(seed["carry_notes"]) != bool(carry_notes)
            or (task is not None and seed["new_task"] != task)
        ):
            raise RunError(
                "a different start-over transaction is already pending; rerun the original start-over command or inspect reset-intent.json"
            )
        task = seed["new_task"]
    else:
        if task is None:
            stem = re.sub(r"[^a-z0-9]+", "-", source.stem.lower()).strip("-") or "book"
            task = f"{stem}-restart-{uuid.uuid4().hex[:8]}"
        if not SLUG_RE.fullmatch(task):
            raise RunError("start-over task must be a lowercase book/run slug")

    # Validate carry boundaries before making the old run ineligible.
    old_run = None
    if not existing_intent.is_file():
        old_run = Run(repo, root)
        if restart_from in {"source_prep", "preflight"}:
            prep = state.get("source_prep")
            if not isinstance(prep, dict) or prep.get("status") != "verified":
                raise RunError(
                    f"start-over --from {restart_from} requires a verified Source Prep package; use --from scratch instead"
                )
            from . import pass_source_prep as source_prep
            source_prep.verify(old_run)
        if restart_from == "preflight":
            plan = state.get("plan")
            if not isinstance(plan, dict) or state.get("phase") in {"load", "source_prep", "preflight", "preflight_accept"}:
                raise RunError("start-over --from preflight requires an already accepted source-wide preflight")
            if domain == "software-engineering" and int(plan.get("schema_version", 1)) < 3:
                raise RunError(
                    "legacy Software Engineering preflight lacks the schema-3 language policy; restart from source_prep so the new preflight can classify and modernize programming-language material"
                )

    new_root = None
    if not existing_intent.is_file():
        # Replacement identity is newly minted; the human-readable task is metadata.
        # Collision checks are therefore performed after start() returns the short-ID root.
        pass

    # An actually-live old PASS process must be stopped first. A dead process's
    # stale lease is evidence, not authority over an explicit user reset.
    lock = inside(root, "controller/operation.lock")
    if lock.is_file():
        pid, alive = _lock_pid_alive(lock)
        if alive:
            raise RunError(f"PASS operation pid {pid} still appears to be running; stop it before start-over")

    if not existing_intent.is_file():
        intent = {
            "schema_version": 1,
            "requested_at": now(),
            "reason": reason,
            "restart_from": restart_from,
            "carry_notes": bool(carry_notes),
            "new_task": task,
            "replacement_run": None,
            "domain": domain,
            "source": str(source),
            "state": state,
        }
        atomic_write(existing_intent, (json.dumps(intent, indent=2) + "\n").encode("utf-8"))
        seed = intent

    # Reset intent outranks every prior lease/checkpoint/handoff. Archive a stale
    # operation lease, then make automation and the old run state ineligible.
    if lock.is_file():
        history = inside(root, "controller/action-history")
        history.mkdir(parents=True, exist_ok=True)
        evidence = inside(history, f"start-over-stale-lock-{uuid.uuid4().hex[:8]}.json")
        atomic_write(evidence, lock.read_bytes())
        lock.unlink(missing_ok=True)
    inside(root, "controller/unattended-authorization.json").unlink(missing_ok=True)
    inside(root, "controller/next-action.json").unlink(missing_ok=True)

    abandoned_path = inside(root, ABANDONED)
    if not abandoned_path.is_file():
        record = {
            "schema_version": 1,
            "abandoned_at": now(),
            "reason": reason,
            "state": state,
            "start_over": {
                "requested_at": seed["requested_at"],
                "restart_from": restart_from,
                "carry_notes": bool(carry_notes),
                "new_task": task,
                "replacement_run": None,
            },
        }
        atomic_write(abandoned_path, (json.dumps(record, indent=2) + "\n").encode("utf-8"))
    old_manifest = read_run_manifest(root, required=False)
    if old_manifest is not None:
        current = _manifest_current(state)
        current["status"] = "abandoned"
        old_manifest["current"] = current
        old_manifest["updated_at"] = now()
        atomic_write(run_manifest_path(root), (json.dumps(old_manifest, indent=2) + "\n").encode("utf-8"))
        register_run(repo, root, old_manifest)
    inside(root, "controller/run.json").unlink(missing_ok=True)

    # Create or resume creation of the replacement run named in the reset intent.
    replacement = (seed.get("replacement_run") if isinstance(seed, dict) else None)
    if replacement:
        new_root = run_root(repo, Path(replacement))
    else:
        new_root = start(repo, source, domain, task, "complete", prior_genre)
        # Persist the minted short-ID root into reset intent so an interrupted
        # start-over transaction resumes the same replacement identity.
        seed["replacement_run"] = str(new_root)
        atomic_write(existing_intent, (json.dumps(seed, indent=2) + "\n").encode("utf-8"))
    new_run = Run(repo, new_root)
    if new_run.domain != domain or Path(new_run.state["source"]).resolve() != source:
        raise RunError("start-over replacement run exists but belongs to a different source/domain")

    carried: list[str] = []
    if carry_notes:
        notes = inside(root, "NOTES.md")
        if notes.is_file():
            atomic_write(inside(new_root, "NOTES.md"), notes.read_bytes())
            carried.append("NOTES.md")

    if restart_from in {"source_prep", "preflight"} and new_run.state["phase"] == "load":
        from . import pass_source_prep as source_prep

        old_identity = inside(root, "controller/source-identity.json")
        if not old_identity.is_file():
            raise RunError("verified Source Prep has no source identity marker to carry")
        atomic_write(inside(new_root, "controller/source-identity.json"), old_identity.read_bytes())
        old_package = inside(root, "prepared-source")
        new_package = inside(new_root, "prepared-source")
        if not old_package.is_dir():
            raise RunError("verified Source Prep package disappeared during start-over")
        if new_package.exists():
            shutil.rmtree(new_package)
        shutil.copytree(old_package, new_package)
        new_run.state["source_prep"] = json.loads(json.dumps(state["source_prep"]))

        if restart_from == "source_prep":
            # Unit files are derivatives of the old accepted preflight. Carry the
            # prepared source, not the old plan's boundaries.
            units_dir = inside(new_root, "prepared-source/units")
            if units_dir.is_dir():
                shutil.rmtree(units_dir)
            manifest_path = source_prep.manifest_path(new_run)
            manifest = preflight._read_json(str(manifest_path))
            manifest["unit_files"] = {}
            manifest["files"] = source_prep.package_files(new_run)
            manifest["package_sha256"] = source_prep.package_digest(manifest["files"])
            atomic_write(manifest_path, (json.dumps(manifest, indent=2) + "\n").encode("utf-8"))
            new_run.state.update(
                phase="preflight", unit_index=0, plan=None, pass1=None, pass2=None,
                reviewed_sha256=None, live_hashes=None, stop_reached=False,
            )
            carried.append("verified Source Prep")
        else:
            new_run.state.update(
                phase="pass1", unit_index=0, plan=json.loads(json.dumps(state["plan"])),
                pass1=None, pass2=None, reviewed_sha256=None, live_hashes=None,
                stop_reached=False,
            )
            # Re-materialize from the carried accepted plan so the replacement
            # package cannot inherit stale/missing unit derivatives.
            source_prep.materialize_units(new_run)
            carried += ["verified Source Prep", "accepted preflight"]
        manifest = source_prep.verify(new_run)
        new_run.state["source_prep"]["package_sha256"] = manifest["package_sha256"]
        new_run.save()

    # Make the replacement itself a verified recovery boundary before declaring
    # the reset complete.
    new_run.checkpoint()
    new_run.write_handoff()

    abandoned = preflight._read_json(str(abandoned_path))
    if isinstance(abandoned.get("start_over"), dict):
        abandoned["start_over"]["replacement_run"] = str(new_root)
        atomic_write(abandoned_path, (json.dumps(abandoned, indent=2) + "\n").encode("utf-8"))
    existing_intent.unlink(missing_ok=True)

    brief = new_run.brief()
    return {
        "outcome": "started_over",
        "abandoned_run": str(root),
        "new_run": str(new_root),
        "restart_from": restart_from,
        "carried": carried,
        "next_action": brief["authorized_action"],
    }


def resume(repo: Path, root: Path | None = None, domain: str | None = None, source: Path | None = None) -> dict:
    """The re-entry point for a fresh context: find the run, verify it and name the next action."""
    repo = repo.resolve()
    if root is None:
        domain = select_domain(repo, domain)
        if source is not None and not source.is_file():
            raise RunError(f"source does not exist: {source}")
        candidates = matching_runs(repo, domain, source) if source is not None else open_runs(repo, domain)
        if not candidates:
            return {
                "outcome": "no_incomplete_run",
                "domain": domain,
                "next_action": f"No unfinished run exists for this {'source' if source else 'domain'}; begin with "
                               f"`python PASS/pass.py start --source <source> --domain {domain}`.",
            }
        if len(candidates) > 1:
            runs = []
            for candidate in candidates:
                try:
                    state = Run(repo, candidate).state
                    runs.append({"run": str(candidate), "source": state["source"], "phase": state["phase"], "unit_index": state["unit_index"]})
                except (OSError, preflight.PreflightError) as exc:
                    runs.append({"run": str(candidate), "unreadable": str(exc)})
            return {
                "outcome": "choose_run",
                "domain": domain,
                "runs": runs,
                "next_action": "Several unfinished runs exist. Ask the user which one to continue and resume it with --run; "
                               "do not start another.",
            }
        root = candidates[0]
    return Run(repo, root).pickup(source)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, help="auto-detected from the current project by default")
    sub = parser.add_subparsers(dest="command", required=True)
    start_parser = sub.add_parser("start", help="authorize a domain-local book/run workspace; no source reading")
    start_parser.add_argument("--source", type=Path, required=True)
    start_parser.add_argument("--domain", help="must be authorized by the user/project; never infer from source topic")
    start_parser.add_argument("--task", help="optional unique lowercase display/task slug")
    start_parser.add_argument("--genre", help="classification metadata slug; does not control the physical run path")
    start_parser.add_argument("--stop-after", choices=("source_prep", "preflight", "complete"), default="complete",
                              help="optional resumable stop target; preflight stops before PASS 1 unit ingestion")
    resume_parser = sub.add_parser("resume", help="find and verify an unfinished run, then name its one next action; read-only")
    resume_parser.add_argument("--run", type=Path, help="the run to verify; omit to search the domain")
    resume_parser.add_argument("--domain", help="the user-authorized domain to search")
    resume_parser.add_argument("--source", type=Path, help="only runs bound to this source path or identical bytes")
    abandon_parser = sub.add_parser("abandon", help="retire an unfinished run on explicit user instruction; drafts are kept")
    abandon_parser.add_argument("--run", type=Path, required=True)
    abandon_parser.add_argument("--reason", required=True, help="the user's explicit instruction to abandon this run")
    start_over_parser = sub.add_parser(
        "start-over",
        help="authoritatively abandon an old run and create a fresh run without consulting its checkpoints",
    )
    start_over_parser.add_argument("--run", type=Path, required=True)
    start_over_parser.add_argument("--reason", required=True, help="the user's explicit instruction to start over")
    start_over_parser.add_argument(
        "--from",
        dest="restart_from",
        choices=("scratch", "source_prep", "preflight"),
        default="scratch",
        help="only these explicitly named prior artifacts may seed the replacement run",
    )
    start_over_parser.add_argument("--carry-notes", action="store_true", help="copy NOTES.md into the replacement run")
    start_over_parser.add_argument("--task", help="optional replacement run slug; default is a unique restart slug")
    runs_parser = sub.add_parser("runs", help="inspect/import/export the short-ID run store")
    runs_sub = runs_parser.add_subparsers(dest="runs_command", required=True)
    runs_list = runs_sub.add_parser("list", help="list self-describing short-ID runs")
    runs_list.add_argument("--domain")
    runs_list.add_argument("--genre")
    runs_export = runs_sub.add_parser("export", help="export one run as a hash-verified portable ZIP")
    runs_export.add_argument("run", type=Path, help="run_id or run path")
    runs_export.add_argument("--output", type=Path, required=True)
    runs_import = runs_sub.add_parser("import", help="validate and import a portable run ZIP")
    runs_import.add_argument("archive", type=Path)
    runs_import.add_argument("--collision", choices=("error", "new-id"), default="error")
    runs_open = runs_sub.add_parser("open", help="resolve a run_id to its physical short path")
    runs_open.add_argument("run", type=Path, help="run_id or run path")
    runs_migrate = runs_sub.add_parser("migrate", help="copy a legacy-layout prepped run into the short-ID store")
    runs_migrate.add_argument("--from", dest="source", type=Path, required=True, help="legacy run directory; copied, never modified")
    runs_migrate.add_argument("--genre", default=None, help="lowercase genre slug; derived from the parent directory name when omitted")
    for command in ("status", "template", "present", "submit", "accept-preflight", "revise-preflight", "rewind", "reopen-last-unit", "amend-last-unit", "rollback", "recover", "repair-checkpoint", "continue-run", "replan", "land", "close-run"):
        command_parser = sub.add_parser(command)
        command_parser.add_argument("--run", type=Path, required=True)
        if command == "submit":
            command_parser.add_argument("--phase", choices=("load", "preflight", "pass1", "checkpoint", "pass2", "pass3", "closure_pass2", "closure_pass3"), required=True)
            command_parser.add_argument("--input", required=True, help="JSON path or '-' for stdin")
        elif command == "land":
            command_parser.add_argument("--decision", required=True, help="JSON landing decision path or '-' for stdin")
        elif command == "accept-preflight":
            command_parser.add_argument("--decision", required=True, help="JSON preflight acceptance decision path or '-' for stdin")
        elif command == "revise-preflight":
            command_parser.add_argument("--input", required=True, help="replacement preflight JSON path or '-' for stdin")
        elif command == "rewind":
            command_parser.add_argument("--phase", choices=("pass1", "pass2", "pass3", "closure_pass2", "closure_pass3"), required=True)
        elif command in {"reopen-last-unit", "amend-last-unit"}:
            command_parser.add_argument("--reason", required=True, help="why the immediately previous accepted unit must be corrected")
        elif command == "recover":
            command_parser.add_argument(
                "--rollback-authoritative",
                action="store_true",
                help="explicitly discard authoritative state persisted after the last verified checkpoint (destructive; audit-recorded)",
            )
        elif command == "replan":
            command_parser.add_argument("--input", required=True, help="JSON boundary amendment path or '-' for stdin")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)
    # Captured for the degraded-checkpoint record: which operation was in flight
    # and, when present produced a packet, the hash of the packet it built.
    operation_context: dict[str, Any] = {"command": args.command}
    try:
        repo = args.repo_root.resolve() if args.repo_root else preflight.find_repo_root(Path.cwd())
        enforce_experimental_controller_target(repo)
        if args.command == "runs":
            if args.runs_command == "list":
                if args.genre is not None and not GENRE_RE.fullmatch(args.genre):
                    raise RunError("--genre must be a lowercase metadata slug")
                print(json.dumps({"schema_version": 1, "runs": list_registered_runs(repo, domain=args.domain, genre=args.genre)}, indent=2))
                return 0
            if args.runs_command == "export":
                output = export_run(repo, args.run, args.output)
                print(json.dumps({"outcome": "exported", "archive": str(output)}, indent=2))
                return 0
            if args.runs_command == "import":
                imported = import_run(repo, args.archive, collision=args.collision)
                print(json.dumps({"outcome": "imported", "run": str(imported), "manifest": read_run_manifest(imported, required=True)}, indent=2))
                return 0
            if args.runs_command == "open":
                resolved = run_root(repo, args.run)
                print(json.dumps({"run": str(resolved), "manifest": read_run_manifest(resolved, required=True)}, indent=2))
                return 0
            if args.runs_command == "migrate":
                migrated = migrate_run(repo, args.source, genre=args.genre)
                print(json.dumps({"outcome": "migrated", "run": str(migrated), "manifest": read_run_manifest(migrated, required=True)}, indent=2))
                return 0
            raise RunError(f"unsupported runs command: {args.runs_command}")
        if args.command == "start":
            run = Run(repo, start(repo, args.source, args.domain, args.task, args.stop_after, args.genre))
            print(json.dumps(run.brief(), indent=2))
            return 0
        if args.command == "resume":
            result = resume(repo, args.run, args.domain, args.source)
            print(json.dumps(result, indent=2))
            return 1 if result["outcome"] == "blocked" else 0
        if args.command == "abandon":
            print(abandon(repo, args.run, args.reason))
            return 0
        if args.command == "start-over":
            print(json.dumps(start_over(repo, args.run, args.reason, args.restart_from, args.carry_notes, args.task), indent=2))
            return 0
        run = Run(repo, args.run)
        if args.command == "recover":
            print(run.recover(rollback_authoritative=getattr(args, "rollback_authoritative", False)))
            print(json.dumps(run.brief(), indent=2))
            return 0
        if args.command == "repair-checkpoint":
            with run.locked(require_resolved=False, action="repair-checkpoint"):
                outcome = run.repair_checkpoint()
            print(outcome)
            return 0
        if args.command in {"status", "template"}:
            payload = run.brief() if args.command == "status" else {"phase": run.state["phase"], "template": run.template()}
            print(json.dumps(payload, indent=2))
            return 0
        # Operation results are captured inside the lock and released only after
        # checkpoint promotion succeeds, so a degraded checkpoint can never be
        # paired with a contradictory success print (EXP-003 Target A).
        outcomes: list[str] = []
        if args.command == "present":
            with run.locked(action="present"):
                packet = run.present()
                operation_context["presented_packet_sha256"] = hashlib.sha256(packet.encode("utf-8")).hexdigest()
            print(packet)
            return 0
        with run.locked(action=args.command):
            if args.command == "continue-run":
                if not run.state.get("stop_reached"):
                    raise RunError("run is not paused at a stop target")
                run.state["stop_reached"] = False
                run.state["stop_after"] = "complete"
                run.save()
                outcomes.append("RUN CONTINUED: stop target cleared")
            elif args.command == "submit":
                outcomes.append(run.submit(args.phase, preflight._read_json(args.input)))
            elif args.command == "accept-preflight":
                outcomes.append(run.accept_preflight(preflight._read_json(args.decision)))
            elif args.command == "revise-preflight":
                outcomes.append(run.revise_preflight(preflight._read_json(args.input)))
            elif args.command == "land":
                outcomes.append(run.land(preflight._read_json(args.decision)))
            elif args.command == "rewind":
                run.rewind(args.phase)
            elif args.command in {"reopen-last-unit", "amend-last-unit"}:
                outcomes.append(run.reopen_last_unit(args.reason))
            elif args.command == "rollback":
                outcomes.append(run.rollback())
            elif args.command == "replan":
                run.replan(preflight._read_json(args.input))
            elif args.command == "close-run":
                run.close()
            else:
                raise RunError(f"unsupported command: {args.command}")
        for line in outcomes:
            print(line)
        if args.command == "close-run":
            for directory in sorted(run.root.rglob("*"), key=lambda p: len(p.parts), reverse=True):
                inside(run.root, directory.relative_to(run.root).as_posix())
                if directory.is_dir() and not any(directory.iterdir()):
                    directory.rmdir()
            if not any(run.root.iterdir()):
                run.root.rmdir()
            # If a legacy run lived in a genre subfolder, drop that folder too
            # once it is empty. Never touch the domain directory itself, and
            # never treat the short-ID run store as a genre folder.
            try:
                genre = run.root.relative_to(run.repo / "workspace/skill-staging").parent
            except ValueError:
                genre = None
            if genre is not None and genre.name != run.domain and not any(genre.iterdir()):
                genre.rmdir()
            print("RUN CLOSED: generated state discarded; original inputs and nonempty retained work preserved")
        else:
            print(json.dumps(run.brief(), indent=2))
        return 0
    except ResidueBlockedError as exc:
        print("PASS RUN BLOCKED: " + json.dumps(exc.as_record(), sort_keys=True), file=sys.stderr)
        return 1
    except CheckpointPromotionError as exc:
        record = exc.as_record()
        record["operation_context"] = dict(operation_context)
        print("PASS RUN CHECKPOINT DEGRADED: " + json.dumps(record, sort_keys=True), file=sys.stderr)
        return 2
    except (OSError, preflight.PreflightError, preflight.yaml.YAMLError) as exc:
        print(f"PASS RUN BLOCKED: {exc}", file=sys.stderr)
        return 1
