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
PHASES = {"load", "preflight", "pass1", "checkpoint", "pass2", "pass3", "land", "finished"}
BUCKETS = ("NEW_PATTERNS", "REFINE", "REINFORCE", "VARIANTS", "REPLACE", "NEW_APS", "NEW_DRILLS", "REJECT")
TAXONOMY = ("NEW_SUBCATEGORY", "MOVE", "RENAME", "MERGE")
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


def start(repo: Path, source: Path, domain: str | None, task: str | None) -> Path:
    repo = repo.resolve()
    domains = authorable_domains(repo)
    if domain is None:
        if len(domains) != 1:
            raise RunError("select the user-authorized --domain; this project has no unambiguous single-domain default")
        domain = domains[0]
    if domain not in domains:
        raise RunError(f"domain is not an existing authorable package: {domain}; domain creation is a separate authorized operation")
    required_documents(repo)
    source = source.resolve()
    if not source.is_file():
        raise RunError(f"source does not exist: {source}")
    if task is None:
        stem = re.sub(r"[^a-z0-9]+", "-", source.stem.lower()).strip("-") or "book"
        task = f"{stem}-{uuid.uuid4().hex[:8]}"
    if not SLUG_RE.fullmatch(task):
        raise RunError("task must be a lowercase book/run slug")
    root = inside(repo, f"workspace/authoring/{domain}/{task}")
    if root.exists():
        raise RunError(f"run already exists; resume it with --run: {root}")
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


class Run:
    def __init__(self, repo: Path, root: Path):
        self.repo = repo.resolve()
        self.root = root.absolute()
        try:
            path = self.root.relative_to(self.repo / "workspace/authoring")
        except ValueError as exc:
            raise RunError("run must belong to this project's workspace/authoring/<domain>/<book-run>") from exc
        if len(path.parts) != 2:
            raise RunError("run must have exactly a domain and book/run directory")
        inside(self.repo, self.root.relative_to(self.repo).as_posix())
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
        path = inside(self.root, "controller/operation.lock")
        try:
            descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError as exc:
            raise RunError("another operation owns this run; inspect a stale operation.lock before removing it") from exc
        os.close(descriptor)
        try:
            # A competing caller may have loaded state before the preceding
            # operation finished. The lease owns the latest persisted state.
            self.reload()
            yield
        finally:
            path.unlink(missing_ok=True)

    def save(self) -> None:
        atomic_write(self.state_path, (json.dumps(self.state, indent=2) + "\n").encode())

    @property
    def domain(self) -> str:
        return self.state["domain"]

    def unit(self) -> dict:
        plan = self.state["plan"]
        if plan is None or self.state["unit_index"] >= len(plan["units"]):
            raise RunError("no active unit")
        return plan["units"][self.state["unit_index"]]

    def brief(self) -> dict:
        phase = self.state["phase"]
        result = {"run": str(self.root), "domain": self.domain, "phase": phase}
        if phase == "load":
            result["required_documents"] = required_documents(self.repo)
            result["authorized_action"] = "Read canonical instructions only; submit the load record before source access."
        elif phase == "preflight":
            result["source"] = self.state["source"]
            result["authorized_action"] = "Structural orientation only: establish subject, TOC/page map, text quality and instructional units. No substantive ingestion or library writes."
        elif phase == "finished":
            result["authorized_action"] = "All units landed; use close-run to discard generated state and inspect remaining owned scratch."
        else:
            unit = self.unit()
            result.update({"unit_id": unit["unit_id"], "material": unit["material"]})
            if phase in {"pass1", "pass2"}:
                result.update({"source": self.state["source"], "authorized_source_scope": unit["locator"]})
            if phase == "pass1":
                result["authorized_action"] = "Read only this entire unit; draft provisional cards by category; record overlaps, secondary-subject flags and consequential questions."
            elif phase == "checkpoint":
                result["questions"] = self.state["pass1"]["questions"]
                result["authorized_action"] = "Resolve the checkpoint questions; do not begin PASS 2 yet."
            elif phase == "pass2":
                result["secondary_subject_flags"] = self.state["pass1"]["secondary_subject_flags"]
                result["authorized_action"] = "Reread this entire unit from scratch; resolve every flag; declare exclusive dispositions, taxonomy and the exact staged change set."
            elif phase == "pass3":
                result["staged_files"] = self.state["pass2"]["changes"]
                result["authorized_action"] = "Close the source/reading notes; scan staged cards as standalone objects. Repair and rescan; submit actual reviewed hashes and every semantic check."
            elif phase == "land":
                result["delta"] = {key: self.state["pass2"][key] for key in ("buckets", "taxonomy", "changes", "removals", "approval_required")}
                result["reviewed_sha256"] = self.state["reviewed_sha256"]
                result["authorized_action"] = "Present the full delta and reasons. Land this unit only under the applicable user-approval or evidence decision; no next-unit reading yet."
        return result

    def template(self) -> dict:
        phase = self.state["phase"]
        if phase == "preflight":
            result = preflight.template_record()
            result.update(domain=self.domain, title=Path(self.state["source"]).stem)
            return result
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
                result.update(basis="user approval", reason="")
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
        if self.live_hashes() != self.state["live_hashes"]:
            raise RunError("live domain/prerequisites changed; rewind to pass2, reconcile and repeat PASS 3 before landing")

    def submit(self, phase: str, data: dict) -> str:
        if phase != self.state["phase"]:
            raise RunError(f"cannot submit {phase}; current phase is {self.state['phase']}")
        if phase == "load":
            exact(data, {"schema_version", "documents_read"}, "load")
            documents = array(data["documents_read"], "documents_read")
            if type(data["schema_version"]) is not int or data["schema_version"] != 1 or any(not isinstance(d, str) for d in documents) or sorted(documents) != sorted(required_documents(self.repo)):
                raise RunError("load record must declare every required current canonical document exactly once")
            self.state["phase"] = "preflight"
            message = "LOAD GATE: pass"
        elif phase == "preflight":
            record = preflight.parse_preflight(data)
            if record.domain != self.domain:
                raise RunError("preflight cannot change the run's authorized domain")
            if record.mode != "unit ingestion":
                raise RunError("controller orchestration currently supports unit ingestion only; curriculum audit requires its own scope contract")
            cards = preflight.validate_against_library(record, self.repo)
            self.state.update(plan=json.loads(json.dumps(asdict(record))), phase="pass1")
            message = preflight.render_preflight(record, cards)
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
            self.state.update(reviewed_sha256=hashes, phase="land")
            message = f"PASS 3: pass — {self.unit()['unit_id'].upper()}"
        else:
            raise RunError("use land or close-run for this phase")
        self.save()
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
        self.state.update(pass2=data, live_hashes=self.live_hashes(), reviewed_sha256=None, phase="pass3")

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
        self.header(decision, {"basis", "reason"})
        if not isinstance(decision["basis"], str) or decision["basis"] not in {"user approval", "evidence"}:
            raise RunError("landing decision requires user approval or an evidence-settled basis")
        string(decision["reason"], "landing reason")
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
        if self.state["phase"] in {"load", "preflight", "finished"}:
            raise RunError("no active unit can be rewound")
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
        exact(data, {"schema_version", "reason", "preflight"}, "unit-plan amendment")
        if type(data["schema_version"]) is not int or data["schema_version"] != 1:
            raise RunError("amendment schema_version must be integer 1")
        string(data["reason"], "instructional boundary evidence")
        if not isinstance(data["preflight"], dict):
            raise RunError("amendment must contain a complete preflight record")
        record = preflight.parse_preflight(data["preflight"])
        plan = json.loads(json.dumps(asdict(record)))
        original = self.state["plan"]
        for key in preflight.TOP_LEVEL_KEYS - {"units", "no_extract"}:
            if plan[key] != original[key]:
                raise RunError("unit-plan amendment cannot change the source, subject or authorized domain")
        closed = self.state["unit_index"]
        if len(plan["units"]) <= closed or plan["units"][:closed] != original["units"][:closed]:
            raise RunError("closed units cannot be rewritten or removed")
        preflight.validate_against_library(record, self.repo)
        self.state["plan"] = plan
        self.save()

    def close(self) -> None:
        if self.state["phase"] != "finished":
            raise RunError("cannot close the source run while any unit remains unfinished")
        self.state_path.unlink()
        inside(self.root, "RUN_NOTE.md").unlink(missing_ok=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, help="auto-detected from the current project by default")
    sub = parser.add_subparsers(dest="command", required=True)
    start_parser = sub.add_parser("start", help="authorize a domain-local book/run workspace; no source reading")
    start_parser.add_argument("--source", type=Path, required=True)
    start_parser.add_argument("--domain", help="must be authorized by the user/project; never infer from source topic")
    start_parser.add_argument("--task", help="optional unique lowercase book/run slug")
    for command in ("status", "template", "submit", "rewind", "replan", "land", "close-run"):
        command_parser = sub.add_parser(command)
        command_parser.add_argument("--run", type=Path, required=True)
        if command == "submit":
            command_parser.add_argument("--phase", choices=("load", "preflight", "pass1", "checkpoint", "pass2", "pass3"), required=True)
            command_parser.add_argument("--input", required=True, help="JSON path or '-' for stdin")
        elif command == "land":
            command_parser.add_argument("--decision", required=True, help="JSON landing decision path or '-' for stdin")
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
        run = Run(repo, args.run)
        if args.command in {"status", "template"}:
            print(json.dumps(run.brief() if args.command == "status" else run.template(), indent=2))
            return 0
        with run.locked():
            if args.command == "submit":
                print(run.submit(args.phase, preflight._read_json(args.input)))
            elif args.command == "land":
                print(run.land(preflight._read_json(args.decision)))
            elif args.command == "rewind":
                run.rewind(args.phase)
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
