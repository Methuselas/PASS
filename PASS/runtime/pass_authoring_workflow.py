#!/usr/bin/env python3
"""Disposable, domain-local PASS authoring workflow and staged unit integration.

The host remains responsible for source access and truthful model declarations.
This controller enforces its supported transitions and validates the actual files
it lands; its scratch state is never a library or release dependency.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from dataclasses import asdict
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

from . import pass_authoring_run as preflight


RUN_SCHEMA = 1
PHASES = {"load", "preflight", "preflight_accept", "pass1", "checkpoint", "pass2", "pass3", "land", "finished"}
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
    "standalone_executability",
)
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FLAG_RE = re.compile(r"^[a-z][a-z0-9_]*$")


class RunError(preflight.PreflightError):
    """The current operation cannot be accepted by the authoring workflow."""


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


def authorable_domains(repo: Path) -> list[str]:
    return sorted(
        p.name for p in (repo / "library").iterdir()
        if p.is_dir() and p.name != "metaskills" and preflight.DOMAIN_RE.fullmatch(p.name)
        and not p.is_symlink() and not getattr(p, "is_junction", lambda: False)()
        and any(p.rglob("MODULE.yaml"))
        and p.resolve().parent == (repo / "library").resolve()
    )


def required_documents(repo: Path) -> list[str]:
    documents = ["PASS/SKILL.md", "PASS/docs/PASS_RUN.md", "PASS/docs/AUTHORING_RUNTIME.md", "PASS/docs/PASS_DOCTRINE.md", "PASS/docs/PASS_SCHEMA.md"]
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
    """Every unfinished run of one domain. An unreadable run counts as unfinished."""
    base = inside(repo, f"workspace/authoring/{domain}")
    found = []
    if not base.is_dir():
        return found
    for root in sorted(base.iterdir()):
        state_path = root / "controller/run.json"
        if not state_path.is_file():
            continue
        try:
            phase = json.loads(state_path.read_text(encoding="utf-8")).get("phase")
        except (OSError, ValueError, AttributeError):
            phase = None
        if phase != "finished":
            found.append(root)
    return found


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


def start(repo: Path, source: Path, domain: str | None, task: str | None) -> Path:
    repo = repo.resolve()
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
    if task is None:
        stem = re.sub(r"[^a-z0-9]+", "-", source.stem.lower()).strip("-") or "book"
        task = f"{stem}-{uuid.uuid4().hex[:8]}"
    if not SLUG_RE.fullmatch(task):
        raise RunError("task must be a lowercase book/run slug")
    root = inside(repo, f"workspace/authoring/{domain}/{task}")
    if root.exists():
        raise RunError(f"run already exists; resume it with `python PASS/pass.py resume --run {root}`")
    (root / "controller").mkdir(parents=True)
    (root / "drafts").mkdir()
    state = {
        "schema_version": RUN_SCHEMA, "domain": domain, "source": str(source),
        "phase": "load", "unit_index": 0, "plan": None, "pass1": None,
        "pass2": None, "reviewed_sha256": None, "live_hashes": None,
    }
    atomic_write(root / "controller/run.json", (json.dumps(state, indent=2) + "\n").encode())
    (root / "RUN_NOTE.md").write_text(
        f"# PASS authoring task: {task}\n\nOwner: ordinary PASS controller.\n"
        f"Purpose: {domain} authoring from {source.name}; cards are staged by canonical category.\n"
        "Cleanup: delete integrated drafts after verified landing; close-run removes generated state.\n"
        "Preserve original source inputs, other tasks and explicit failure-evidence holds.\n"
        "This directory is disposable and is not card canon or Skillset Memory.\n", encoding="utf-8"
    )
    return root


def run_root(repo: Path, root: Path) -> Path:
    root = root.absolute()
    try:
        path = root.relative_to(repo / "workspace/authoring")
    except ValueError as exc:
        raise RunError("run must belong to this project's workspace/authoring/<domain>/<book-run>") from exc
    if len(path.parts) != 2:
        raise RunError("run must have exactly a domain and book/run directory")
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
CHECKPOINT = "controller/checkpoint"
HANDOFF_MARK = "<!-- Generated by PASS/pass.py after every accepted step; rewritten each time. Do not edit. -->"


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
        self.root = run_root(self.repo, root)
        abandoned = inside(self.root, ABANDONED)
        if abandoned.is_file():
            raise RunError(f"run was abandoned and cannot resume: {self.root}; see {ABANDONED}")
        self.state_path = inside(self.root, "controller/run.json")
        self.reload()

    def reload(self) -> None:
        self.state = preflight._read_json(str(self.state_path))
        exact(self.state, {"schema_version", "domain", "source", "phase", "unit_index", "plan", "pass1", "pass2", "reviewed_sha256", "live_hashes"}, "run state")
        if type(self.state["schema_version"]) is not int or self.state["schema_version"] != RUN_SCHEMA:
            raise RunError("unsupported run state version")
        if self.state["domain"] != self.root.parent.name or self.state["domain"] not in authorable_domains(self.repo):
            raise RunError("run domain no longer matches its authorized workspace/package")
        if not isinstance(self.state["phase"], str) or self.state["phase"] not in PHASES or type(self.state["unit_index"]) is not int or self.state["unit_index"] < 0:
            raise RunError("invalid run phase or unit index")
        if self.state["plan"] is not None:
            record = preflight.parse_preflight(self.state["plan"])
            if record.domain != self.state["domain"] or self.state["unit_index"] > len(record.units):
                raise RunError("invalid saved unit plan")
            if (self.state["phase"] == "finished") != (self.state["unit_index"] == len(record.units)):
                raise RunError("saved phase does not match the unit plan")
        elif self.state["phase"] not in {"load", "preflight"}:
            raise RunError("saved phase requires a unit plan")

    @contextmanager
    def locked(self):
        with operation_lock(self.root):
            # A competing caller may have loaded state before the preceding
            # operation finished. The lease owns the latest persisted state.
            self.reload()
            yield
            # Every successful operation ends at a hard checkpoint.
            if self.state_path.is_file():
                self.checkpoint()

    # ------------------------------------------------------------ checkpoints

    def staged_tree(self) -> dict[str, str]:
        """Every file under the run's drafts/ and recipes/, by run-relative path."""
        files = {}
        for top in ("drafts", "recipes"):
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
        """Snapshot the drafts at a newly accepted state and rewrite HANDOFF.md.

        A snapshot is taken only when run.json differs from the last one, so an
        operation that accepted nothing (present, drive) never captures
        half-finished work as the safe endpoint.
        """
        state_sha = digest(self.state_path)
        manifest = self.checkpoint_manifest()
        if manifest is None or manifest.get("state_sha256") != state_sha:
            folder = inside(self.root, CHECKPOINT)
            fresh = inside(self.root, f"{CHECKPOINT}.new")
            retired = inside(self.root, f"{CHECKPOINT}.old")
            for leftover in (fresh, retired):
                if leftover.exists():
                    shutil.rmtree(leftover)
            files = self.staged_tree()
            for name in files:
                target = fresh / "files" / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(inside(self.root, name), target)
            record = {
                "schema_version": 1, "created_at": now(), "state_sha256": state_sha,
                "phase": self.state["phase"], "unit_index": self.state["unit_index"],
                "last_accepted": self.last_accepted(), "files": files,
            }
            fresh.mkdir(parents=True, exist_ok=True)
            atomic_write(fresh / "manifest.json", (json.dumps(record, indent=2) + "\n").encode("utf-8"))
            if folder.exists():
                folder.rename(retired)
            fresh.rename(folder)
            if retired.exists():
                shutil.rmtree(retired)
        self.write_handoff()

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
        if phase not in {"preflight", "pass1", "checkpoint", "pass2", "pass3"}:
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
            source = inside(self.root, f"{CHECKPOINT}/files/{name}")
            if digest(source) != saved[name]:
                raise RunError(f"checkpoint copy is damaged: {name}")
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
        except RunError as exc:
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
        if units:
            done = ", ".join(u["unit_id"].upper() for u in units[:index]) or "none"
            lines += [f"- Units: {len(units)}; landed: {done}"]
        if phase not in {"load", "preflight", "preflight_accept", "finished"}:
            unit = units[index]
            lines += [f"- Current: {unit['unit_id'].upper()} at **{phase}** — {unit['material']}",
                      f"- Unit scope: {unit['locator']}"]
        else:
            lines += [f"- Phase: **{phase}**"]
        lines += [
            "",
            "## Pick up here",
            "",
            f"1. Run `python PASS/pass.py resume --run {rel}`. It verifies the source, drafts and lock",
            "   and names the one next action. It outranks this file.",
            f"2. If you are continuing after an interruption and `resume` reports drafts changed since",
            f"   the checkpoint, run `python PASS/pass.py rollback --run {rel}` first. The drafts return",
            f"   to the end of {self.last_accepted() or 'the run start'} and {phase} restarts from its beginning;",
            "   never finish a phase another session left half done.",
            f"3. Next action at this checkpoint: {action}",
            "",
            "## Drafts at this checkpoint",
            "",
            *([f"- `{name}`" for name in manifest["files"]] or ["- none"]),
            "",
            "## Do not",
            "",
            "- Do not read `controller/run.json`; `resume`, `status` and `template` give what you need.",
            "- Do not rerun preflight, and do not edit this file: the controller rewrites it.",
            "- Put corrections and traps worth keeping in `NOTES.md` (model-written, not authoritative).",
            "",
        ]
        atomic_write(path, "\n".join(lines).encode("utf-8"))

    def save(self) -> None:
        atomic_write(self.state_path, (json.dumps(self.state, indent=2) + "\n").encode())

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
        if phase not in {"preflight", "pass1", "checkpoint", "pass2", "pass3"}:
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
        unit_id = self.unit()["unit_id"] if self.state["plan"] is not None and self.state["unit_index"] < len(self.state["plan"]["units"]) else None
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
        # Fail closed if the current source path is stale, missing, or replaced.
        self.source_file(required=True)
        return marker

    def last_accepted(self) -> str | None:
        phase = self.state["phase"]
        units = [u["unit_id"].upper() for u in self.state["plan"]["units"]] if self.state["plan"] else []
        index = self.state["unit_index"]
        if phase == "load":
            return None
        if phase == "preflight":
            return "LOAD"
        if phase == "preflight_accept":
            return "preflight validated; acceptance pending"
        if phase == "finished":
            return f"{units[-1]} landed"
        if phase == "pass1":
            return f"{units[index - 1]} landed" if index else "preflight accepted"
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
        if lock.exists():
            held = lock.read_text(encoding="utf-8").strip() or "no owner recorded"
            blockers.append(
                f"a previous PASS operation did not finish ({held}). Confirm no PASS process is still running, inspect the "
                "library and staged files for a partial write, then remove controller/operation.lock and resume again"
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
                bound = Path(self.state["source"])
                source_state = "moved" if not bound.is_file() else "changed"
                candidate = source.resolve() if source else None
                if candidate and candidate.is_file() and candidate.stat().st_size == identity["size"] and digest(candidate) == identity["sha256"]:
                    blockers.append(f"the source moved; the given file has identical bytes. Run `python PASS/source.py rebind-source --run {self.root} --source \"{candidate}\"`, then resume again")
                elif source_state == "moved":
                    blockers.append(f"the bound source is missing: {bound}. Find the identical file and run `python PASS/source.py rebind-source --run {self.root} --source <path>`")
                else:
                    blockers.append("the bound source file's bytes changed since LOAD; this run cannot continue on different bytes. Restore the original file or abandon the run")

        drafts = "none"
        if phase == "pass1":
            drafts = "unaccepted scratch from an interrupted PASS 1" if any(p.is_file() for p in (self.root / "drafts").rglob("*")) else "none"
        elif phase in {"checkpoint", "pass2"}:
            drafts = "PASS 1 working drafts (not hash-bound until PASS 3)"
        elif phase in {"pass3", "land"}:
            try:
                if not self.live_unchanged():
                    blockers.append(f"live library cards changed after PASS 2; run `python PASS/pass.py rewind --run {self.root} --phase pass2`, reconcile, then repeat PASS 3")
                if phase == "land":
                    if self.staged_hashes() != self.state["reviewed_sha256"]:
                        drafts = "changed after PASS 3"
                        blockers.append(f"staged files changed after PASS 3; run `python PASS/pass.py rewind --run {self.root} --phase pass3` and rescan")
                    else:
                        drafts = "verified against PASS 3 hashes"
                else:
                    drafts = "staged by PASS 2; PASS 3 review pending"
            except OSError as exc:
                drafts = "missing"
                blockers.append(f"a staged file is missing ({exc}); rewind to pass2 and restage")

        drift = self.checkpoint_drift() if phase in {"preflight", "pass1", "checkpoint", "pass2", "pass3"} else None
        rollback_hint = None
        if drift:
            drafts = f"{len(drift)} file(s) changed since the checkpoint at the end of {self.last_accepted() or 'the run start'}"
            rollback_hint = (
                f"Drafts changed after the last accepted step. If this session is continuing after an interruption, run "
                f"`python PASS/pass.py rollback --run {self.root}` to restore the checkpoint, then redo {phase} from its "
                "beginning; never finish a phase another session left half done."
            )
        try:
            authorization = self.unattended_authorization(required=False) if identity and source_state == "unchanged" else None
        except RunError as exc:
            authorization = None
            blockers.append(f"unattended authorization is invalid: {exc}")
        lease = None
        if authorization and phase in {"preflight", "pass1", "checkpoint", "pass2", "pass3"}:
            path = self.unattended_action_path()
            if not path.is_file():
                lease = "none issued; source.py drive will issue one"
            else:
                held = preflight._read_json(str(path))
                current = held.get("phase") == phase and held.get("unit_index") == self.state["unit_index"] and held.get("state_sha256") == digest(self.state_path)
                lease = "current; source.py drive returns it unchanged" if current else "stale; source.py drive will archive it and issue a new one"

        units = self.state["plan"]["units"] if self.state["plan"] else []
        index = self.state["unit_index"]
        active = units[index]["unit_id"].upper() if phase not in {"load", "preflight", "preflight_accept", "finished"} else None
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
                "safe_to_discard": not lock.exists(),
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
        if plan is None or self.state["unit_index"] >= len(plan["units"]):
            raise RunError("no active unit")
        return plan["units"][self.state["unit_index"]]

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
        if phase == "land":
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
        if phase == "load":
            result["required_documents"] = required_documents(self.repo)
            result["authorized_action"] = "Read canonical instructions only; submit the load record before source access."
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
            result["authorized_action"] = "All units landed; use close-run to discard generated state and inspect remaining owned scratch."
        else:
            unit = self.unit()
            result.update({"unit_id": unit["unit_id"], "material": unit["material"]})
            if phase in {"pass1", "pass2"}:
                result.update({"source": self.state["source"], "authorized_source_scope": unit["locator"]})
            if phase == "pass1":
                result["authorized_action"] = (
                    "SOURCE PREFLIGHT IS COMPLETE; do not preflight this unit. Read only this entire unit; draft provisional cards "
                    "by category; record overlaps, secondary-subject flags and consequential questions."
                )
            elif phase == "checkpoint":
                result["questions"] = self.state["pass1"]["questions"]
                result["authorized_action"] = "Resolve the checkpoint questions; do not begin PASS 2 and do not rerun preflight."
            elif phase == "pass2":
                result["secondary_subject_flags"] = self.state["pass1"]["secondary_subject_flags"]
                result["authorized_action"] = (
                    "SOURCE PREFLIGHT IS COMPLETE; do not preflight this unit. Reread this entire unit from scratch; resolve every "
                    "flag; declare exclusive dispositions, taxonomy and the exact staged change set."
                )
            elif phase == "pass3":
                result["staged_files"] = self.state["pass2"]["changes"]
                result["authorized_action"] = (
                    "Close the source/reading notes; scan staged cards as standalone objects. Repair and rescan; submit actual "
                    "reviewed hashes and every semantic check. Do not rerun preflight."
                )
            elif phase == "land":
                result["delta"] = {key: self.state["pass2"][key] for key in ("buckets", "taxonomy", "changes", "removals", "approval_required")}
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
        return result

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
            return packet
        packet = self.render_land_packet()
        marker = {
            "schema_version": 1,
            "unit_id": self.unit()["unit_id"],
            "sha256": hashlib.sha256(packet.encode("utf-8")).hexdigest(),
        }
        atomic_write(self.presentation_path(), (json.dumps(marker, indent=2) + "\n").encode())
        return packet

    def render_land_packet(self) -> str:
        if self.state["phase"] != "land":
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
            result = preflight.template_record()
            result.update(domain=self.domain, title=Path(self.state["source"]).stem)
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
            elif phase == "checkpoint":
                result["answers"] = [{"question_id": q["question_id"], "resolution": ""} for q in self.state["pass1"]["questions"]]
            elif phase == "pass2":
                result.update(full_reread=False, flag_resolutions=[{"flag_id": f["flag_id"], "reason": ""} for f in self.state["pass1"]["secondary_subject_flags"]],
                              buckets={name: [] for name in BUCKETS}, taxonomy={name: [] for name in TAXONOMY}, changes=[], removals=[], approval_required=False)
            elif phase == "pass3":
                result.update(card_only_review=False, checks={name: False for name in SEMANTIC_CHECKS}, reviewed_sha256=self.staged_hashes())
            elif phase == "land":
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
        return result

    def live_fingerprint(self) -> str:
        """One digest of every live file PASS 2 depends on. run.json once stored
        the full map, hundreds of hashes a model would read on every resume."""
        canonical = json.dumps(self.live_hashes(), sort_keys=True).encode("utf-8")
        return "sha256:" + hashlib.sha256(canonical).hexdigest()

    def live_unchanged(self) -> bool:
        stored = self.state["live_hashes"]
        if isinstance(stored, dict):  # runs saved before the fingerprint
            return self.live_hashes() == stored
        return self.live_fingerprint() == stored

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

    def staged_hashes(self) -> dict[str, str]:
        return {name: digest(inside(self.root, name)) for name in self.state["pass2"]["changes"]}

    def check_live(self) -> None:
        if not self.live_unchanged():
            raise RunError("live domain/prerequisites changed; rewind to pass2, reconcile and repeat PASS 3 before landing")

    def submit(self, phase: str, data: dict) -> str:
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
            self.state["phase"] = "preflight"
            message = "LOAD GATE: pass"
        elif phase == "preflight":
            record = preflight.parse_preflight(data)
            if record.domain != self.domain:
                raise RunError("preflight cannot change the run's authorized domain")
            if record.mode != "unit ingestion":
                raise RunError("controller orchestration currently supports unit ingestion only; curriculum audit requires its own scope contract")
            preflight.validate_against_library(record, self.repo)
            self.clear_preflight_presentation()
            self.state.update(plan=json.loads(json.dumps(asdict(record))), phase="preflight_accept")
            message = "PREFLIGHT: validated — presentation and explicit user confirmation required before PASS 1"
        elif phase == "pass1":
            self.header(data, {"full_read", "working_drafts", "overlap_object_ids", "secondary_subject_flags", "questions"})
            if data["full_read"] is not True:
                raise RunError("PASS 1 requires the entire bounded unit's full read")
            for name in array(data["working_drafts"], "working_drafts"):
                self.target(name)
                if not inside(self.root, name).is_file():
                    raise RunError(f"working draft does not exist: {name}")
            cards = preflight.load_domain_cards(self.repo, self.domain)
            overlap = array(data["overlap_object_ids"], "overlap_object_ids")
            if any(not isinstance(oid, str) or oid not in cards for oid in overlap) or len(set(overlap)) != len(overlap):
                raise RunError("PASS 1 overlaps must be unique active-domain live IDs")
            for field, key, text in (("secondary_subject_flags", "flag_id", "subject"), ("questions", "question_id", "question")):
                seen = set()
                for entry in array(data[field], field):
                    exact(entry, {key, text}, field)
                    value = string(entry[key], key)
                    if not FLAG_RE.fullmatch(value) or value in seen:
                        raise RunError(f"invalid or duplicate {key}")
                    seen.add(value)
                    string(entry[text], text)
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
        elif phase == "pass3":
            self.header(data, {"card_only_review", "checks", "reviewed_sha256"})
            if data["card_only_review"] is not True:
                raise RunError("PASS 3 requires a card-only review with the source and reading notes closed")
            exact(data["checks"], SEMANTIC_CHECKS, "semantic checks")
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
            self.state.update(reviewed_sha256=hashes, phase="land")
            message = f"PASS 3: pass — {self.unit()['unit_id'].upper()}"
        else:
            raise RunError("use land or close-run for this phase")
        self.save()
        self.consume_unattended_action(phase, previous_unit_index)
        return message

    def accept_pass2(self, data: dict) -> None:
        self.header(data, {"full_reread", "flag_resolutions", "buckets", "taxonomy", "changes", "removals", "approval_required"})
        if data["full_reread"] is not True or type(data["approval_required"]) is not bool:
            raise RunError("PASS 2 requires a full cold reread and explicit approval_required Boolean")
        resolved = set()
        for item in array(data["flag_resolutions"], "flag_resolutions"):
            exact(item, {"flag_id", "reason"}, "flag resolution")
            key = string(item["flag_id"], "flag_id")
            if key in resolved:
                raise RunError("duplicate flag resolution")
            resolved.add(key)
            string(item["reason"], "flag resolution reason")
        if resolved != {f["flag_id"] for f in self.state["pass1"]["secondary_subject_flags"]}:
            raise RunError("every PASS 1 secondary-subject flag must be explicitly resolved")
        exact(data["buckets"], BUCKETS, "delta buckets")
        cards = preflight.load_domain_cards(self.repo, self.domain)
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
        self.state.update(pass2=data, live_hashes=self.live_fingerprint(), reviewed_sha256=None, phase="pass3")

    def check_change_set(self, data: dict) -> None:
        changes = array(data["changes"], "changes")
        removals = array(data["removals"], "removals")
        if any(not isinstance(p, str) for p in changes + removals) or len(set(changes)) != len(changes) or len(set(removals)) != len(removals):
            raise RunError("change/removal paths must be unique strings")
        dispositions = {item["object_id"]: bucket for bucket, entries in data["buckets"].items() for item in entries}
        cards = preflight.load_domain_cards(self.repo, self.domain)
        removed_ids = set()
        removal_targets = set()
        for name in removals:
            target = self.removal_target(name)
            path = inside(self.repo, target)
            if not path.is_file():
                raise RunError(f"removal has no live target: {name}")
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
            inside(self.repo, target)
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
                if live and live.path != inside(self.repo, target) and live.path.relative_to(self.repo).as_posix() not in removal_targets:
                    raise RunError("moving an owner requires removal of its original path")
                if live and digest(live.path) == digest(source) and live.path == inside(self.repo, target):
                    raise RunError("unchanged card belongs in REINFORCE, not a changing disposition")
            category = None
            if target.startswith("library/"):
                parts = PurePosixPath(target).parent.relative_to(f"library/{self.domain}").parts
                if "assets" in parts:
                    parts = parts[:parts.index("assets")]
                category = PurePosixPath(*parts).as_posix() if parts else None
            if category and not inside(self.repo, f"library/{self.domain}/{category}").exists():
                declared = [e["path"] for e in data["taxonomy"]["NEW_SUBCATEGORY"]]
                if not any(category == p or category.startswith(p + "/") for p in declared):
                    raise RunError(f"new library category requires NEW_SUBCATEGORY: {category}")
        for oid, bucket in dispositions.items():
            if bucket not in {"REINFORCE", "REJECT"} and oid not in changed_ids | removed_ids:
                raise RunError(f"changing disposition has no staged change/removal: {oid}")
        for oid in removed_ids:
            if dispositions.get(oid) != "REPLACE" and not (oid in changed_ids and any(data["taxonomy"][a] for a in ("MOVE", "RENAME", "MERGE"))):
                raise RunError("retired owner needs REPLACE or an explicit taxonomy migration with its successor")
        if any(PurePosixPath(p).name == "MODULE.yaml" for p in changes + removals):
            if not any(p.startswith("recipes/") for p in changes):
                raise RunError("module changes must include the active domain's canonical release recipe")

    @contextmanager
    def overlay(self, integration: bool = False):
        with tempfile.TemporaryDirectory(prefix="pass-authoring-overlay-") as temporary:
            tree = Path(temporary)
            domains = [p.name for p in (self.repo / "library").iterdir() if p.is_dir()] if integration else [self.domain, "metaskills"]
            for domain in domains:
                source = inside(self.repo, f"library/{domain}")
                tree_hashes(source)
                shutil.copytree(source, tree / "library" / domain)
            for name in self.state["pass2"]["removals"]:
                inside(tree, self.removal_target(name)).unlink()
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

    def revise_preflight(self, data: dict) -> str:
        if self.state["phase"] != "preflight_accept":
            raise RunError("preflight can be revised only while it is awaiting acceptance")
        record = preflight.parse_preflight(data)
        if record.domain != self.domain:
            raise RunError("preflight revision cannot change the run's authorized domain")
        if record.mode != "unit ingestion":
            raise RunError("controller orchestration currently supports unit ingestion only; curriculum audit requires its own scope contract")
        preflight.validate_against_library(record, self.repo)
        self.clear_preflight_presentation()
        self.state["plan"] = json.loads(json.dumps(asdict(record)))
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
        elif decision["basis"] != "user confirmation":
            raise RunError(
                "preflight acceptance requires explicit user confirmation or a recorded source-scoped unattended authorization; "
                "do not infer either from the request to run PASS"
            )
        string(decision["reason"], "preflight acceptance reason")
        self.state["phase"] = "pass1"
        self.clear_preflight_presentation()
        self.save()
        return f"PREFLIGHT ACCEPTED: subject and source-wide plan confirmed — PASS 1 released — {self.unit()['unit_id'].upper()}"

    def land(self, decision: dict) -> str:
        # Independent books may stage in parallel, but only one unit in a domain
        # may integrate at a time. This lease contains no research/run state.
        lease = inside(self.repo, f"workspace/authoring/{self.domain}/.landing.lock")
        try:
            descriptor = os.open(lease, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError as exc:
            raise RunError("another book owns this domain's landing lease; retry after it finishes and reconcile any live changes") from exc
        os.close(descriptor)
        try:
            return self._land(decision)
        finally:
            lease.unlink(missing_ok=True)

    def _land(self, decision: dict) -> str:
        if self.state["phase"] != "land":
            raise RunError("unit cannot land or advance before PASS 3 and mechanical validation pass")
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
            raise RunError("staged files changed after PASS 3; rewind to pass3 and rescan")
        self.check_change_set(self.state["pass2"])
        writes = {}
        generated_removals = []
        with self.overlay(integration=True) as tree:
            self.validate(tree)
            # Regeneration must also retire indexes of categories whose last
            # card moved away. The existing builder only writes current topics.
            for path in (tree / "library" / self.domain).rglob("INDEX.md"):
                path.unlink()
            self.tool("build_index.py", tree, "--package", self.domain)
            for name in self.state["pass2"]["changes"]:
                target = self.target(name)
                writes[target] = inside(tree, target).read_bytes()
            for path in (tree / "library" / self.domain).rglob("INDEX.md"):
                target = path.relative_to(tree).as_posix()
                live = inside(self.repo, target)
                if not live.is_file() or live.read_bytes() != path.read_bytes():
                    writes[target] = path.read_bytes()
            for path in inside(self.repo, f"library/{self.domain}").rglob("INDEX.md"):
                target = path.relative_to(self.repo).as_posix()
                if not inside(tree, target).exists():
                    generated_removals.append(target)
        self.check_live()
        if self.staged_hashes() != self.state["reviewed_sha256"]:
            raise RunError("staged files changed during integration validation; repeat PASS 3")
        removals = [self.removal_target(p) for p in self.state["pass2"]["removals"]] + generated_removals
        targets = {name: inside(self.repo, name) for name in {*writes, *removals}}
        before = {name: path.read_bytes() if path.is_file() else None for name, path in targets.items()}
        old_state = json.loads(json.dumps(self.state))
        unit = self.unit()["unit_id"]
        try:
            for name in removals:
                targets[name].unlink()
            for name, content in writes.items():
                atomic_write(targets[name], content)
            for name, content in writes.items():
                if targets[name].read_bytes() != content:
                    raise RunError(f"landed file verification failed: {name}")
            self.state.update(unit_index=self.state["unit_index"] + 1, pass1=None, pass2=None, reviewed_sha256=None, live_hashes=None)
            self.state["phase"] = "finished" if self.state["unit_index"] == len(self.state["plan"]["units"]) else "pass1"
            self.save()
            self.clear_presentation()
        except BaseException:
            self.state = old_state
            for name, content in before.items():
                if content is None:
                    targets[name].unlink(missing_ok=True)
                else:
                    atomic_write(targets[name], content)
            raise
        cleanup = []
        for name in old_state["pass2"]["changes"]:
            try:
                inside(self.root, name).unlink()
            except OSError:
                cleanup.append(name)
        suffix = f"; retained scratch needs cleanup: {', '.join(cleanup)}" if cleanup else ""
        return f"UNIT CLOSED AND LANDED: {unit.upper()} (no Git commit created){suffix}"

    def rewind(self, phase: str) -> None:
        if phase not in {"pass1", "pass2", "pass3"}:
            raise RunError("rewind supports only pass1, pass2 or pass3")
        if self.state["phase"] in {"load", "preflight", "preflight_accept", "finished"}:
            raise RunError("no accepted active unit can be rewound")
        self.clear_presentation()
        if phase == "pass1":
            self.state.update(pass1=None, pass2=None, live_hashes=None, reviewed_sha256=None)
        elif phase == "pass2":
            if self.state["pass1"] is None or (self.state["pass1"]["questions"] and "answers" not in self.state["pass1"]):
                raise RunError("PASS 1 and any checkpoint must pass before PASS 2")
            self.state.update(pass2=None, live_hashes=None, reviewed_sha256=None)
        elif phase == "pass3":
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
        plan = json.loads(json.dumps(asdict(record)))
        original = self.state["plan"]
        for key in preflight.TOP_LEVEL_KEYS - {"units", "no_extract"}:
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
            owned = ["events.jsonl", "preflight.md", "preflight.json", "final-validate.txt", "final-verify-references.txt"]
            owned.extend(p.name for p in audit.glob("u*-landing.md"))
            owned.extend(p.name for p in audit.glob("u*-landing.json"))
            for name in sorted(set(owned)):
                inside(audit, name).unlink(missing_ok=True)
            if not any(audit.iterdir()):
                audit.rmdir()
        inside(self.root, "RUN_NOTE.md").unlink(missing_ok=True)
        checkpoint = inside(self.root, CHECKPOINT)
        if checkpoint.is_dir():
            shutil.rmtree(checkpoint)
        handoff = inside(self.root, "HANDOFF.md")
        if handoff.is_file() and HANDOFF_MARK in handoff.read_text(encoding="utf-8"):
            handoff.unlink()


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
    start_parser.add_argument("--task", help="optional unique lowercase book/run slug")
    resume_parser = sub.add_parser("resume", help="find and verify an unfinished run, then name its one next action; read-only")
    resume_parser.add_argument("--run", type=Path, help="the run to verify; omit to search the domain")
    resume_parser.add_argument("--domain", help="the user-authorized domain to search")
    resume_parser.add_argument("--source", type=Path, help="only runs bound to this source path or identical bytes")
    abandon_parser = sub.add_parser("abandon", help="retire an unfinished run on explicit user instruction; drafts are kept")
    abandon_parser.add_argument("--run", type=Path, required=True)
    abandon_parser.add_argument("--reason", required=True, help="the user's explicit instruction to abandon this run")
    for command in ("status", "template", "present", "submit", "accept-preflight", "revise-preflight", "rewind", "rollback", "replan", "land", "close-run"):
        command_parser = sub.add_parser(command)
        command_parser.add_argument("--run", type=Path, required=True)
        if command == "submit":
            command_parser.add_argument("--phase", choices=("load", "preflight", "pass1", "checkpoint", "pass2", "pass3"), required=True)
            command_parser.add_argument("--input", required=True, help="JSON path or '-' for stdin")
        elif command == "land":
            command_parser.add_argument("--decision", required=True, help="JSON landing decision path or '-' for stdin")
        elif command == "accept-preflight":
            command_parser.add_argument("--decision", required=True, help="JSON preflight acceptance decision path or '-' for stdin")
        elif command == "revise-preflight":
            command_parser.add_argument("--input", required=True, help="replacement preflight JSON path or '-' for stdin")
        elif command == "rewind":
            command_parser.add_argument("--phase", choices=("pass1", "pass2", "pass3"), required=True)
        elif command == "replan":
            command_parser.add_argument("--input", required=True, help="JSON boundary amendment path or '-' for stdin")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)
    try:
        repo = args.repo_root.resolve() if args.repo_root else preflight.find_repo_root(Path.cwd())
        if args.command == "start":
            run = Run(repo, start(repo, args.source, args.domain, args.task))
            print(json.dumps(run.brief(), indent=2))
            return 0
        if args.command == "resume":
            result = resume(repo, args.run, args.domain, args.source)
            print(json.dumps(result, indent=2))
            return 1 if result["outcome"] == "blocked" else 0
        if args.command == "abandon":
            print(abandon(repo, args.run, args.reason))
            return 0
        run = Run(repo, args.run)
        if args.command in {"status", "template"}:
            print(json.dumps(run.brief() if args.command == "status" else run.template(), indent=2))
            return 0
        if args.command == "present":
            with run.locked():
                packet = run.present()
            print(packet)
            return 0
        with run.locked():
            if args.command == "submit":
                print(run.submit(args.phase, preflight._read_json(args.input)))
            elif args.command == "accept-preflight":
                print(run.accept_preflight(preflight._read_json(args.decision)))
            elif args.command == "revise-preflight":
                print(run.revise_preflight(preflight._read_json(args.input)))
            elif args.command == "land":
                print(run.land(preflight._read_json(args.decision)))
            elif args.command == "rewind":
                run.rewind(args.phase)
            elif args.command == "rollback":
                print(run.rollback())
            elif args.command == "replan":
                run.replan(preflight._read_json(args.input))
            elif args.command == "close-run":
                run.close()
        if args.command == "close-run":
            for directory in sorted(run.root.rglob("*"), key=lambda p: len(p.parts), reverse=True):
                inside(run.root, directory.relative_to(run.root).as_posix())
                if directory.is_dir() and not any(directory.iterdir()):
                    directory.rmdir()
            if not any(run.root.iterdir()):
                run.root.rmdir()
            print("RUN CLOSED: generated state discarded; original inputs and nonempty retained work preserved")
        else:
            print(json.dumps(run.brief(), indent=2))
        return 0
    except (OSError, preflight.PreflightError, preflight.yaml.YAMLError) as exc:
        print(f"PASS RUN BLOCKED: {exc}", file=sys.stderr)
        return 1
