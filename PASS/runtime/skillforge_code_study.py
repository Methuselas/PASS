#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Deterministic administration for software Code Apprenticeship studies.

The controller freezes a source-first reading before exposing PASS guidance,
then freezes the card-guided implementation and comparison before grading. It
does not decide engineering semantics or write Skillset Memory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
import uuid
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import yaml


SCHEMA_VERSION = 2
PROGRAM_PURPOSE = "skillset-improvement"
RUN_TYPE = "software-card-field-test"
STATES = {
    "prepared", "discovery-frozen", "guidance-open", "work-frozen",
    "revealed", "invalidated", "finalized",
}
SELECTION_ROLES = {
    "neutral-external-corpus",
    "project-relevant-reference",
    "interest-led-investigation",
}
CRITERION_RESULTS = {"pass", "fail", "not_tested"}
QUALIFICATION_RESULTS = {"pass", "fail", "not_tested"}
IMPROVEMENT_OUTCOMES = {
    "improved", "human-preferred", "tradeoff", "equivalent", "not_tested",
}
ATTRIBUTIONS = {
    "none", "skillcard", "application", "human-code", "source-context",
    "fixture", "runtime-tool", "unresolved",
}
NEXT_ACTIONS = {
    "none", "project-trial", "habit-promotion-review", "card-repair",
    "language-support", "fresh-retest", "source-context-review",
    "repair-administration",
}
HABIT_DISPOSITIONS = {
    "memory-candidate", "card-repair", "language-support", "context-only",
    "no-retention",
}
GRADER_RELATIONS = {"separate", "same-reader"}
SCORES = {"strong", "adequate", "weak", "failed", "unproven"}
CARD_IF_STATUSES = {"established", "not-established"}
REPRODUCTION_FIDELITY = {"verified", "not-verified"}
FLOATING_REVISIONS = {"head", "latest", "main", "master", "tip", "trunk"}
MAX_SOURCE_FILES = 100
MAX_SOURCE_BYTES = 5 * 1024 * 1024
FRONTMATTER_RE = re.compile(
    r"\A---\s*\n(?P<front>.*?)\n---\s*\n(?P<body>.*)\Z", re.DOTALL
)
RUBRIC_CRITERIA = [
    "The frozen discovery reconstructs the human design's contract, ownership, assumptions, and source-backed constraints before card exposure.",
    "Every fact that decides the primary card's IF condition, especially a type, signature, ownership, lifetime, or build fact, is supported by its actual declaration or configuration; a name, cast, comment, or use is not a substitute.",
    "No unavailable or unresolved source context decides whether the primary card applies; if such context is missing, the study is invalid and the card is not tested.",
    "The card analysis establishes whether the primary card applies and distinguishes silence, disagreement, coarseness, and missing language specialization.",
    "The work artifact preserves the source facts that decide the comparison, including relevant declared types, preconditions, and language or toolchain constraints.",
    "A PASS-guided alternative is implemented rather than merely described and preserves the stated contract and constraints.",
    "The human and PASS-guided designs are exercised with equivalent checks, and at least one check can distinguish them on the named improvement property when an improvement is claimed.",
    "The comparison evaluates a named improvement target using behavior and constraints rather than proxy counts or style preference.",
    "The recorded revision, language, and toolchain agree with the source and machine evidence actually used.",
    "The conclusion states whether PASS improved the design, the human design remains preferable, the designs serve different constraints, or they are equivalent.",
    "The primary card's guidance is correct and usable for this case, or the failed criterion and attribution identify why it is not.",
]


class StudyError(RuntimeError):
    """A fail-closed Code Apprenticeship administration error."""


@dataclass(frozen=True)
class SkillCard:
    object_id: str
    object_type: str
    name: str
    domain: str
    relative_path: str
    text: str


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def digest_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise StudyError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise StudyError(f"{path} must contain a JSON object")
    return value


def write_text_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
        os.replace(temporary_name, path)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except OSError:
            pass
        raise


def write_json_atomic(path: Path, value: dict[str, Any]) -> None:
    write_text_atomic(path, json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def require_inside(path: Path, root: Path, label: str) -> Path:
    resolved = path.resolve()
    root = root.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise StudyError(f"{label} escapes {root}") from exc
    return resolved


def default_library(script: Path) -> Path:
    release = script.resolve().parents[1] / "library"
    if release.is_dir():
        return release
    repo = script.resolve().parents[2] / "library"
    return repo


def skillcard_index(library: Path) -> dict[str, SkillCard]:
    library = library.resolve()
    if not library.is_dir():
        raise StudyError(f"library does not exist: {library}")
    cards: dict[str, SkillCard] = {}
    for path in sorted(library.rglob("*.md")):
        relative = path.relative_to(library)
        if not relative.parts or relative.parts[0] not in {
            "software-engineering", "metaskills"
        }:
            continue
        text = path.read_text(encoding="utf-8")
        match = FRONTMATTER_RE.match(text)
        if not match:
            continue
        front = yaml.safe_load(match.group("front"))
        if not isinstance(front, dict) or front.get("object_type") not in {
            "pattern", "ap"
        }:
            continue
        object_id = str(front.get("object_id", "")).strip()
        if not object_id:
            raise StudyError(f"{relative.as_posix()}: missing object_id")
        if object_id in cards:
            raise StudyError(f"duplicate Pattern/AP object_id: {object_id}")
        cards[object_id] = SkillCard(
            object_id=object_id,
            object_type=str(front["object_type"]),
            name=str(front.get("name") or object_id),
            domain=relative.parts[0],
            relative_path=relative.as_posix(),
            text=text,
        )
    return cards


def select_cards(
    library: Path, primary_id: str, supporting_ids: Iterable[str]
) -> list[SkillCard]:
    requested = [primary_id, *supporting_ids]
    if any(not str(item).strip() for item in requested):
        raise StudyError("card IDs must be non-empty")
    if len(requested) != len(set(requested)):
        raise StudyError("primary and supporting cards may be named only once")
    by_id = skillcard_index(library)
    missing = [item for item in requested if item not in by_id]
    if missing:
        raise StudyError("unknown Pattern/AP card(s): " + ", ".join(missing))
    cards = [by_id[item] for item in requested]
    if cards[0].domain != "software-engineering":
        raise StudyError("the primary card must belong to software-engineering")
    return cards


def source_files(source_root: Path, relative_paths: Iterable[str]) -> list[Path]:
    source_root = source_root.resolve()
    if not source_root.is_dir():
        raise StudyError(f"source root does not exist: {source_root}")
    requested = list(relative_paths)
    if not requested:
        raise StudyError("at least one --source file is required")
    if len(requested) > MAX_SOURCE_FILES:
        raise StudyError(f"a study may include at most {MAX_SOURCE_FILES} source files")
    if len(requested) != len(set(requested)):
        raise StudyError("a source file may be named only once")
    files: list[Path] = []
    total = 0
    for item in requested:
        relative = Path(item)
        if relative.is_absolute() or ".." in relative.parts:
            raise StudyError(f"source path must be relative and bounded: {item}")
        path = require_inside(source_root / relative, source_root, "source file")
        if not path.is_file():
            raise StudyError(f"source file does not exist: {item}")
        total += path.stat().st_size
        if total > MAX_SOURCE_BYTES:
            raise StudyError(
                f"source slice exceeds the {MAX_SOURCE_BYTES}-byte bounded-study limit"
            )
        files.append(path)
    return files


def manifest_for(root: Path, paths: Iterable[Path]) -> list[dict[str, Any]]:
    root = root.resolve()
    result = []
    for path in sorted((item.resolve() for item in paths), key=lambda item: item.as_posix()):
        relative = path.relative_to(root).as_posix()
        result.append({
            "path": relative,
            "bytes": path.stat().st_size,
            "sha256": digest_file(path),
        })
    return result


def tree_manifest(root: Path, prefixes: Iterable[str] | None = None) -> list[dict[str, Any]]:
    root = root.resolve()
    files: list[Path] = []
    for prefix in prefixes or (".",):
        path = require_inside(root / prefix, root, "manifest path")
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            files.extend(item for item in path.rglob("*") if item.is_file())
    return manifest_for(root, files)


def verify_manifest(root: Path, expected: list[dict[str, Any]], label: str) -> None:
    actual = tree_manifest(root)
    if actual != expected:
        raise StudyError(f"{label} changed after it was frozen")


def discovery_brief(run: dict[str, Any]) -> str:
    source_list = "\n".join(f"- `source/{item['path']}`" for item in run["source_files"])
    return f"""# Code Apprenticeship — Human Design Discovery

Study `{run['review_subject']}` at revision `{run['revision']}` as a
`{run['selection_role']}` source. Language: `{run['language']}`. Toolchain:
`{run['toolchain']}`.

Engineering decision: {run['engineering_decision']}

## Source slice

{source_list}

## Produce before any PASS card is opened

Write `answer/discovery.md` with these sections:

1. Purpose and observable contract
2. Ownership, state, and data flow
3. Assumptions and constraints, each tied to source evidence
4. Important design decisions and apparent tradeoffs
5. Declarations, call sites, tests, build settings, and failure paths examined
6. Unavailable context and unresolved hypotheses

Read the human design before judging it. Human code is evidence, not an answer
key. Do not infer a declared type, signature, ownership rule, or build fact from
a name, cast, comment, or use. A cast proves that a conversion was requested; it
does not prove the operand's declared type. If a fact needed to understand the
engineering decision is unavailable, keep it unresolved and stop for more source
context instead of turning the hypothesis into a fact. Do not open `controller/`,
the repository library, or any answer-bearing material. Do not modify `source/`;
copy anything you need to change into `work/`.
"""


def guidance_brief(run: dict[str, Any]) -> str:
    cards = "\n".join(f"- `{item}`" for item in run["exposed_card_ids"])
    return f"""# Code Apprenticeship — PASS-Guided Qualification and Improvement

The source-first discovery is frozen. You may now read only the bounded cards
under `skillcards/`:

{cards}

Primary card: `{run['primary_card_id']}`

## Produce

- `answer/card_analysis.md`: establish whether the primary card applies; record
  where the human design agrees, disagrees, is more precise, or exposes missing
  language support. Cite the exact source declaration or configuration for every
  type, signature, ownership, lifetime, or build fact that decides the card's IF
  condition. A name, cast, comment, or use is not declaration evidence. If a
  deciding fact is unavailable, the run is INVALID; do not force the card to
  apply. If the IF condition is false, the card was not exercised. Classify
  observed techniques as owned, unowned, or owned but coarser only after deciding
  whether the human code is sound.
- `answer/improvement.md`: name one property to improve, implement the smallest
  PASS-guided alternative, state the contract and constraints it preserves, and
  conclude `improved`, `human-preferred`, `tradeoff`, or `equivalent`. Name the
  source facts the reproduction preserves, including the deciding declared
  types. Do not claim an improvement unless a check actually exercises that
  property and could distinguish the designs; ordinary success cases establish
  only the behavior they cover.
- `answer/machine_evidence.md`: record exact build/run commands, outputs, failure
  or boundary cases, and what each result establishes.
- `work/`: place the actual alternative, probes, tests, and build material here.

The alternative must be implemented, not merely described. Compare behavior,
constraints, ownership, failure handling, testability, maintainability, and
language idiom. Counts and stylistic preference cannot establish improvement.
The recorded revision, language, and toolchain must match the source and machine
evidence actually used. Do not change the frozen discovery or the copied human
source.
"""


def rubric() -> dict[str, Any]:
    return {"schema_version": SCHEMA_VERSION, "criteria": RUBRIC_CRITERIA}


def grade_template() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "validity": "invalid",
        "invalid_reason": "complete this grade",
        "grader_relation": "separate",
        "qualification_result": "not_tested",
        "improvement_outcome": "not_tested",
        "improvement_target": "",
        "next_action": "repair-administration",
        "attribution": "unresolved",
        "attributed_object_id": None,
        "artifact_quality": "unproven",
        "process_validity": "unproven",
        "skill_attribution": "unproven",
        "card_if_status": "not-established",
        "card_if_evidence": "",
        "source_context_complete": False,
        "reproduction_fidelity": "not-verified",
        "reproduction_fidelity_evidence": "",
        "improvement_claim_exercised": False,
        "improvement_claim_evidence": "",
        "metadata_consistent": False,
        "metadata_evidence": "",
        "criteria": [
            {"criterion": criterion, "result": "not_tested", "evidence": ""}
            for criterion in RUBRIC_CRITERIA
        ],
        "observations": [],
        "habit_candidates": [],
        "notes": "",
    }


def save_run(root: Path, run: dict[str, Any]) -> None:
    run["revision_number"] = int(run.get("revision_number", 0)) + 1
    write_json_atomic(root / "controller" / "run.json", run)


def load_run(path: Path) -> tuple[Path, dict[str, Any]]:
    root = path.resolve()
    run_path = root / "controller" / "run.json"
    run = read_json(run_path)
    if run.get("schema_version") != SCHEMA_VERSION:
        raise StudyError(f"unsupported study schema: {run.get('schema_version')}")
    if run.get("state") not in STATES:
        raise StudyError(f"invalid study state: {run.get('state')}")
    return root, run


def verify_sources(root: Path, run: dict[str, Any]) -> None:
    verify_manifest(root / "student" / "source", run["source_files"], "human source")


def verify_discovery(root: Path, run: dict[str, Any]) -> None:
    frozen = run.get("discovery_freeze")
    if not isinstance(frozen, dict):
        raise StudyError("discovery has not been frozen")
    path = root / "student" / "answer" / "discovery.md"
    if not path.is_file() or digest_file(path) != frozen.get("sha256"):
        raise StudyError("discovery changed after it was frozen")


def verify_cards(root: Path, run: dict[str, Any]) -> None:
    expected = run.get("exposed_cards") or []
    if not expected:
        raise StudyError("guidance has not been opened")
    verify_manifest(root / "student" / "skillcards", expected, "exposed skillcards")


def verify_work(root: Path, run: dict[str, Any]) -> None:
    expected = run.get("work_freeze")
    if not isinstance(expected, list) or not expected:
        raise StudyError("study work has not been frozen")
    actual = tree_manifest(root / "student", ["answer", "work"])
    if actual != expected:
        raise StudyError("study work changed after it was frozen")


def prepare(
    library: Path,
    primary_card_id: str,
    supporting_card_ids: Iterable[str],
    source_root: Path,
    source_paths: Iterable[str],
    selection_role: str,
    review_subject: str,
    revision: str,
    language: str,
    toolchain: str,
    engineering_decision: str,
    out: Path,
) -> dict[str, Any]:
    if selection_role not in SELECTION_ROLES:
        raise StudyError(f"selection role must be one of {sorted(SELECTION_ROLES)}")
    values = {
        "review subject": review_subject,
        "revision": revision,
        "language": language,
        "toolchain": toolchain,
        "engineering decision": engineering_decision,
    }
    for label, value in values.items():
        if not str(value).strip():
            raise StudyError(f"{label} must be non-empty")
    if (
        selection_role == "neutral-external-corpus"
        and revision.strip().casefold() in FLOATING_REVISIONS
    ):
        raise StudyError(
            "a neutral external corpus requires an immutable revision, not a "
            f"floating ref such as {revision.strip()!r}"
        )
    cards = select_cards(library, primary_card_id, supporting_card_ids)
    files = source_files(source_root, source_paths)
    source_root = source_root.resolve()
    out = out.resolve()
    if out.exists():
        raise StudyError(f"refusing to overwrite existing study directory: {out}")
    out.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=f".{out.name}.", dir=out.parent))
    run: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "run_id": uuid.uuid4().hex,
        "state": "prepared",
        "revision_number": 0,
        "created_at": now_utc(),
        "program_purpose": PROGRAM_PURPOSE,
        "run_type": RUN_TYPE,
        "selection_role": selection_role,
        "review_subject": review_subject.strip(),
        "revision": revision.strip(),
        "language": language.strip(),
        "toolchain": toolchain.strip(),
        "engineering_decision": engineering_decision.strip(),
        "primary_card_id": cards[0].object_id,
        "supporting_card_ids": [card.object_id for card in cards[1:]],
        "exposed_card_ids": [],
        "source_files": [],
        "discovery_freeze": None,
        "exposed_cards": [],
        "work_freeze": None,
        "invalid_reason": None,
    }
    try:
        (temporary / "student" / "source").mkdir(parents=True)
        (temporary / "student" / "answer").mkdir(parents=True)
        (temporary / "student" / "work").mkdir(parents=True)
        (temporary / "controller" / "cards").mkdir(parents=True)
        for path in files:
            relative = path.relative_to(source_root)
            destination = temporary / "student" / "source" / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, destination)
        run["source_files"] = tree_manifest(temporary / "student" / "source")
        private_cards = []
        for card in cards:
            destination = temporary / "controller" / "cards" / card.relative_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(card.text, encoding="utf-8")
            private_cards.append({
                "object_id": card.object_id,
                "object_type": card.object_type,
                "relative_path": card.relative_path,
                "sha256": digest_file(destination),
            })
        run["private_cards"] = private_cards
        write_text_atomic(temporary / "student" / "brief.md", discovery_brief(run))
        write_json_atomic(temporary / "controller" / "rubric.json", rubric())
        save_run(temporary, run)
        os.replace(temporary, out)
    except BaseException:
        if temporary.exists():
            shutil.rmtree(temporary)
        raise
    return load_run(out)[1]


def freeze_discovery(run_path: Path) -> dict[str, Any]:
    root, run = load_run(run_path)
    if run["state"] != "prepared":
        raise StudyError(f"freeze-discovery requires prepared, found {run['state']}")
    verify_sources(root, run)
    discovery = root / "student" / "answer" / "discovery.md"
    if not discovery.is_file() or not discovery.read_text(encoding="utf-8").strip():
        raise StudyError("student/answer/discovery.md must be produced before freezing")
    run["discovery_freeze"] = {
        "path": "answer/discovery.md",
        "bytes": discovery.stat().st_size,
        "sha256": digest_file(discovery),
        "frozen_at": now_utc(),
    }
    run["state"] = "discovery-frozen"
    save_run(root, run)
    return run


def open_guidance(run_path: Path) -> dict[str, Any]:
    root, run = load_run(run_path)
    if run["state"] != "discovery-frozen":
        raise StudyError(f"open-guidance requires discovery-frozen, found {run['state']}")
    verify_sources(root, run)
    verify_discovery(root, run)
    exposed_root = root / "student" / "skillcards"
    for card in run["private_cards"]:
        source = root / "controller" / "cards" / card["relative_path"]
        if not source.is_file() or digest_file(source) != card["sha256"]:
            raise StudyError(f"private skillcard changed before exposure: {card['object_id']}")
        destination = exposed_root / card["relative_path"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    run["exposed_cards"] = tree_manifest(exposed_root)
    run["exposed_card_ids"] = [
        run["primary_card_id"], *run["supporting_card_ids"]
    ]
    write_text_atomic(root / "student" / "guidance.md", guidance_brief(run))
    run["state"] = "guidance-open"
    run["guidance_opened_at"] = now_utc()
    save_run(root, run)
    return run


def freeze_work(run_path: Path) -> dict[str, Any]:
    root, run = load_run(run_path)
    if run["state"] != "guidance-open":
        raise StudyError(f"freeze-work requires guidance-open, found {run['state']}")
    verify_sources(root, run)
    verify_discovery(root, run)
    verify_cards(root, run)
    for name in ("card_analysis.md", "improvement.md", "machine_evidence.md"):
        path = root / "student" / "answer" / name
        if not path.is_file() or not path.read_text(encoding="utf-8").strip():
            raise StudyError(f"student/answer/{name} must be produced before freezing")
    work_files = [item for item in (root / "student" / "work").rglob("*") if item.is_file()]
    if not work_files or not any(item.stat().st_size for item in work_files):
        raise StudyError("student/work must contain an implemented alternative or executable probe")
    run["work_freeze"] = tree_manifest(root / "student", ["answer", "work"])
    run["work_frozen_at"] = now_utc()
    run["state"] = "work-frozen"
    save_run(root, run)
    return run


def reveal(run_path: Path) -> dict[str, Any]:
    root, run = load_run(run_path)
    if run["state"] != "work-frozen":
        raise StudyError(f"reveal requires work-frozen, found {run['state']}")
    verify_sources(root, run)
    verify_discovery(root, run)
    verify_cards(root, run)
    verify_work(root, run)
    grader = root / "grader"
    grader.mkdir()
    shutil.copy2(root / "controller" / "rubric.json", grader / "rubric.json")
    write_json_atomic(grader / "grade.json", grade_template())
    run["state"] = "revealed"
    run["revealed_at"] = now_utc()
    save_run(root, run)
    return run


def invalidate(run_path: Path, reason: str) -> dict[str, Any]:
    root, run = load_run(run_path)
    if run["state"] == "finalized":
        raise StudyError("a finalized study cannot be invalidated")
    if not reason.strip():
        raise StudyError("invalidation reason must be non-empty")
    run["state"] = "invalidated"
    run["invalid_reason"] = reason.strip()
    run["invalidated_at"] = now_utc()
    save_run(root, run)
    return run


def validate_grade(grade: dict[str, Any], run: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    validity = grade.get("validity")
    if grade.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    if validity not in {"valid", "invalid"}:
        errors.append("validity must be valid or invalid")
    reason = str(grade.get("invalid_reason") or "").strip()
    if validity == "invalid" and not reason:
        errors.append("invalid_reason is required when invalid")
    if validity == "valid" and reason:
        errors.append("invalid_reason must be empty when valid")
    if grade.get("grader_relation") not in GRADER_RELATIONS:
        errors.append(f"grader_relation must be one of {sorted(GRADER_RELATIONS)}")
    for key in ("artifact_quality", "process_validity", "skill_attribution"):
        if grade.get(key) not in SCORES:
            errors.append(f"{key} must be one of {sorted(SCORES)}")
    if grade.get("skill_attribution") != "unproven":
        errors.append("one field test cannot prove skill attribution")
    if grade.get("card_if_status") not in CARD_IF_STATUSES:
        errors.append(f"card_if_status must be one of {sorted(CARD_IF_STATUSES)}")
    if not isinstance(grade.get("source_context_complete"), bool):
        errors.append("source_context_complete must be true or false")
    if grade.get("reproduction_fidelity") not in REPRODUCTION_FIDELITY:
        errors.append(
            "reproduction_fidelity must be one of "
            f"{sorted(REPRODUCTION_FIDELITY)}"
        )
    for key in ("improvement_claim_exercised", "metadata_consistent"):
        if not isinstance(grade.get(key), bool):
            errors.append(f"{key} must be true or false")
    if grade.get("qualification_result") not in QUALIFICATION_RESULTS:
        errors.append("invalid qualification_result")
    if grade.get("improvement_outcome") not in IMPROVEMENT_OUTCOMES:
        errors.append("invalid improvement_outcome")
    if grade.get("next_action") not in NEXT_ACTIONS:
        errors.append("invalid next_action")
    attribution = grade.get("attribution")
    if attribution not in ATTRIBUTIONS:
        errors.append("invalid attribution")
    object_id = grade.get("attributed_object_id")
    if attribution == "skillcard":
        if object_id not in set(run.get("exposed_card_ids") or []):
            errors.append("skillcard attribution must name an exposed Pattern/AP")
    elif object_id is not None:
        errors.append(f"{attribution} attribution may not name a skillcard")
    criteria = grade.get("criteria")
    if not isinstance(criteria, list):
        return errors + ["criteria must be a list"]
    actual_text = [item.get("criterion") for item in criteria if isinstance(item, dict)]
    if actual_text != RUBRIC_CRITERIA:
        errors.append("criteria differ from the canonical rubric")
        return errors
    results: list[str] = []
    for index, item in enumerate(criteria, start=1):
        result = item.get("result")
        results.append(str(result))
        if result not in CRITERION_RESULTS:
            errors.append(f"criterion {index}: invalid result")
        elif validity == "valid" and result == "not_tested":
            errors.append(f"criterion {index}: a valid study must pass or fail every criterion")
        elif validity == "invalid" and result != "not_tested":
            errors.append(f"criterion {index}: an invalid study cannot grade craft")
        if validity == "valid" and not str(item.get("evidence") or "").strip():
            errors.append(f"criterion {index}: evidence is required")
    expected_result = "pass" if all(result == "pass" for result in results) else "fail"
    if validity == "valid":
        if grade.get("card_if_status") != "established":
            errors.append("a valid study requires the primary card IF to be established")
        if not str(grade.get("card_if_evidence") or "").strip():
            errors.append("a valid study requires source-backed card_if_evidence")
        if grade.get("source_context_complete") is not True:
            errors.append("a valid study requires complete deciding source context")
        if grade.get("reproduction_fidelity") != "verified":
            errors.append("a valid study requires verified reproduction fidelity")
        if not str(grade.get("reproduction_fidelity_evidence") or "").strip():
            errors.append("a valid study requires reproduction_fidelity_evidence")
        if grade.get("improvement_claim_exercised") is not True:
            errors.append("a valid study must exercise the named improvement claim")
        if not str(grade.get("improvement_claim_evidence") or "").strip():
            errors.append("a valid study requires improvement_claim_evidence")
        if grade.get("metadata_consistent") is not True:
            errors.append("a valid study requires consistent revision, language, and toolchain metadata")
        if not str(grade.get("metadata_evidence") or "").strip():
            errors.append("a valid study requires metadata_evidence")
        if grade.get("qualification_result") != expected_result:
            errors.append(f"qualification_result must be {expected_result}")
        if grade.get("improvement_outcome") == "not_tested":
            errors.append("a valid study must conclude the improvement comparison")
        if not str(grade.get("improvement_target") or "").strip():
            errors.append("a valid study requires a named improvement_target")
        if expected_result == "fail" and attribution == "none":
            errors.append("a failed qualification requires attribution")
        if expected_result == "pass" and grade.get("next_action") not in {
            "none", "project-trial", "habit-promotion-review"
        }:
            errors.append("a passing qualification has an incompatible next_action")
        if expected_result == "fail" and grade.get("next_action") not in {
            "card-repair", "language-support", "fresh-retest"
        }:
            errors.append("a failed qualification has an incompatible next_action")
        if attribution not in {"none", "skillcard", "application", "human-code"}:
            errors.append("a valid study cannot attribute a craft result to a blocker")
    else:
        if grade.get("qualification_result") != "not_tested":
            errors.append("an invalid study must use qualification_result not_tested")
        if grade.get("improvement_outcome") != "not_tested":
            errors.append("an invalid study must use improvement_outcome not_tested")
        allowed_invalid_actions = {
            "source-context-review"
        } if attribution == "source-context" else {"repair-administration"}
        if grade.get("next_action") not in allowed_invalid_actions:
            errors.append("an invalid study has an incompatible next_action")
        if attribution not in {"source-context", "fixture", "runtime-tool", "unresolved"}:
            errors.append("an invalid study must attribute its blocker")
        if attribution == "source-context" and grade.get("source_context_complete") is True:
            errors.append("source-context attribution requires incomplete deciding context")
    observations = grade.get("observations")
    if not isinstance(observations, list) or any(
        not isinstance(item, str) for item in observations
    ):
        errors.append("observations must be a list of strings")
    elif validity == "valid" and not any(item.strip() for item in observations):
        errors.append("a valid study requires at least one observation")
    habits = grade.get("habit_candidates")
    if not isinstance(habits, list):
        errors.append("habit_candidates must be a list")
    else:
        for index, habit in enumerate(habits, start=1):
            label = f"habit candidate {index}"
            if not isinstance(habit, dict):
                errors.append(f"{label} must be an object")
                continue
            unknown = sorted(
                set(habit)
                - {"observation", "habit", "verification", "disposition", "owner_object_id"}
            )
            if unknown:
                errors.append(f"{label} has unknown keys: {', '.join(unknown)}")
            for key in ("observation", "habit", "verification"):
                if not str(habit.get(key) or "").strip():
                    errors.append(f"{label}.{key} is required")
            if habit.get("disposition") not in HABIT_DISPOSITIONS:
                errors.append(f"{label}.disposition must be one of {sorted(HABIT_DISPOSITIONS)}")
            owner = habit.get("owner_object_id")
            if owner is not None and owner not in set(run.get("exposed_card_ids") or []):
                errors.append(f"{label}.owner_object_id must name an exposed Pattern/AP")
            if habit.get("disposition") in {"card-repair", "language-support"} and owner is None:
                errors.append(f"{label} must name the skillcard proposed for repair")
    if validity == "invalid" and habits:
        errors.append("an invalid study cannot retain coding-habit candidates")
    if grade.get("next_action") == "habit-promotion-review" and not habits:
        errors.append("habit-promotion-review requires at least one habit candidate")
    return errors


def candidate_event(
    run: dict[str, Any], grade: dict[str, Any] | None, event_id: str,
    task: str, event_date: str,
) -> dict[str, Any]:
    if not event_id.strip() or not task.strip():
        raise StudyError("event_id and task must be non-empty")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", event_date):
        raise StudyError("date must be YYYY-MM-DD")
    if grade is None:
        validity = "invalid"
        invalid_reason = str(run.get("invalid_reason") or "study invalidated")
        observations: list[str] = []
        artifact_quality = "failed"
        process_validity = "failed"
        notes = "Code Apprenticeship study invalidated before qualification."
    else:
        validity = str(grade["validity"])
        invalid_reason = str(grade.get("invalid_reason") or "")
        observations = [item.strip() for item in grade["observations"] if item.strip()]
        for habit in grade.get("habit_candidates") or []:
            observations.append(
                "Habit candidate "
                f"[{habit['disposition']}]: {habit['observation']} "
                f"Adopt: {habit['habit']} Verify: {habit['verification']}"
            )
        artifact_quality = str(grade["artifact_quality"])
        process_validity = str(grade["process_validity"])
        notes = (
            f"Code Apprenticeship field test; qualification={grade['qualification_result']}; "
            f"improvement={grade['improvement_outcome']}; "
            f"target={grade.get('improvement_target') or 'not tested'}; "
            f"attribution={grade['attribution']}; next={grade['next_action']}; "
            f"grader={grade['grader_relation']}."
        )
        if str(grade.get("notes") or "").strip():
            notes += " " + str(grade["notes"]).strip()
    notes += (
        f" Subject: {run['review_subject']} at {run['revision']}; "
        f"selection={run['selection_role']}; language={run['language']}; "
        f"toolchain={run['toolchain']}."
    )
    event: dict[str, Any] = {
        "event_id": event_id.strip(),
        "date": event_date,
        "task": task.strip(),
        "validity": validity,
        "scope_id": run["primary_card_id"],
        "delivery": "skillforge-code-study:source-first-card-guided-improvement",
        "run_type": RUN_TYPE,
        "program_purpose": PROGRAM_PURPOSE,
        "training_stage": "qualification",
        "intervention": {
            "intervention_id": "code-study-card-bundle",
            "kind": "software-card-field-test",
            "description": "Frozen human-code discovery followed by bounded PASS-guided implementation and comparison.",
            "components": {
                "drill_instructions": False,
                "card_ids": [run["primary_card_id"], *run["supporting_card_ids"]],
                "external_material": True,
            },
        },
        "observations": observations,
        "baseline": "untested",
        "isolation": "untested",
        "retention": "untested",
        "transfer": "untested",
        "artifact_quality": artifact_quality,
        "process_validity": process_validity,
        "skill_attribution": "unproven",
        "notes": notes,
    }
    if validity == "invalid":
        event["invalid_reason"] = invalid_reason
    return event


def finalize(
    run_path: Path, event_id: str, task: str, event_date: str | None = None,
    grade_path: Path | None = None,
) -> dict[str, Any]:
    root, run = load_run(run_path)
    if run["state"] not in {"revealed", "invalidated"}:
        raise StudyError(f"finalize requires revealed or invalidated, found {run['state']}")
    grade: dict[str, Any] | None = None
    if run["state"] == "revealed":
        verify_sources(root, run)
        verify_discovery(root, run)
        verify_cards(root, run)
        verify_work(root, run)
        grade = read_json((grade_path or root / "grader" / "grade.json").resolve())
        errors = validate_grade(grade, run)
        if errors:
            raise StudyError("invalid grade: " + "; ".join(errors))
    event = candidate_event(
        run, grade, event_id, task, event_date or date.today().isoformat()
    )
    write_json_atomic(root / "study_result.json", grade or {
        "validity": "invalid", "invalid_reason": run.get("invalid_reason")
    })
    write_json_atomic(root / "candidate_training_event.json", event)
    run["state"] = "finalized"
    run["finalized_at"] = now_utc()
    run["candidate_event"] = "candidate_training_event.json"
    save_run(root, run)
    return event


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--library", type=Path, default=default_library(Path(__file__)))
    commands = parser.add_subparsers(dest="command", required=True)

    prepare_parser = commands.add_parser("prepare")
    prepare_parser.add_argument("--primary-card", required=True)
    prepare_parser.add_argument("--supporting-card", action="append", default=[])
    prepare_parser.add_argument("--source-root", type=Path, required=True)
    prepare_parser.add_argument("--source", action="append", required=True)
    prepare_parser.add_argument("--selection-role", choices=sorted(SELECTION_ROLES), required=True)
    prepare_parser.add_argument("--subject", required=True)
    prepare_parser.add_argument("--revision", required=True)
    prepare_parser.add_argument("--language", required=True)
    prepare_parser.add_argument("--toolchain", required=True)
    prepare_parser.add_argument("--decision", required=True)
    prepare_parser.add_argument("--out", type=Path, required=True)

    for name in ("freeze-discovery", "open-guidance", "freeze-work", "reveal", "status"):
        command = commands.add_parser(name)
        command.add_argument("--run", type=Path, required=True)
    invalid = commands.add_parser("invalidate")
    invalid.add_argument("--run", type=Path, required=True)
    invalid.add_argument("--reason", required=True)
    final = commands.add_parser("finalize")
    final.add_argument("--run", type=Path, required=True)
    final.add_argument("--event-id", required=True)
    final.add_argument("--task", required=True)
    final.add_argument("--date")
    final.add_argument("--grade", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "prepare":
            run = prepare(
                args.library, args.primary_card, args.supporting_card,
                args.source_root, args.source, args.selection_role, args.subject,
                args.revision, args.language, args.toolchain, args.decision, args.out,
            )
            print(f"PREPARED: {args.out.resolve()}")
            print(f"Primary card held private: {run['primary_card_id']}")
            print("Expose only student/; complete discovery before opening guidance.")
        elif args.command == "freeze-discovery":
            run = freeze_discovery(args.run)
            print(f"DISCOVERY FROZEN: {run['discovery_freeze']['sha256']}")
        elif args.command == "open-guidance":
            run = open_guidance(args.run)
            print("GUIDANCE OPEN: " + ", ".join(run["exposed_card_ids"]))
        elif args.command == "freeze-work":
            run = freeze_work(args.run)
            print(f"WORK FROZEN: {len(run['work_freeze'])} file(s)")
        elif args.command == "reveal":
            reveal(args.run)
            print(f"GRADER PACKET REVEALED: {args.run.resolve() / 'grader'}")
        elif args.command == "invalidate":
            run = invalidate(args.run, args.reason)
            print(f"INVALIDATED: {run['invalid_reason']}")
        elif args.command == "finalize":
            event = finalize(args.run, args.event_id, args.task, args.date, args.grade)
            print(f"FINALIZED: {event['event_id']} ({event['validity']})")
            print("Skillset Memory was not modified.")
        elif args.command == "status":
            root, run = load_run(args.run)
            print(json.dumps({
                "run": str(root),
                "state": run["state"],
                "primary_card_id": run["primary_card_id"],
                "supporting_card_ids": run["supporting_card_ids"],
                "source_files": [item["path"] for item in run["source_files"]],
                "discovery_frozen": bool(run.get("discovery_freeze")),
                "guidance_open": bool(run.get("exposed_cards")),
                "work_frozen": bool(run.get("work_freeze")),
                "invalid_reason": run.get("invalid_reason"),
                "candidate_event": run.get("candidate_event"),
            }, indent=2, ensure_ascii=False))
        return 0
    except (StudyError, OSError, yaml.YAMLError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
