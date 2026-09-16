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


SCHEMA_VERSION = 3
READABLE_SCHEMA_VERSIONS = {2, SCHEMA_VERSION}
PROGRAM_PURPOSE = "skillset-improvement"
RUN_TYPE = "software-card-field-test"
STATES = {
    "prepared", "discovery-frozen", "guidance-open", "work-frozen",
    "revealed", "evidence-audited", "invalidated", "finalized",
}
SELECTION_ROLES = {
    "neutral-external-corpus",
    "project-relevant-reference",
    "interest-led-investigation",
}
EVIDENCE_ROLES = {
    "held-out-validation", "motivating-example-regression", "exploratory",
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
FACT_KINDS = {
    "type", "signature", "ownership", "lifetime", "build", "behavior",
    "syntax", "contract", "other",
}
EVIDENCE_KINDS = {
    "declaration", "configuration", "implementation", "call-site", "test",
    "machine-output",
}
IMPROVEMENT_PROPERTIES = {
    "correctness", "safety", "ownership", "lifetime", "interface-clarity",
    "failure-handling", "testability", "maintainability", "performance",
    "portability", "robustness", "language-idiom", "other",
}
CONTEXT_DISPOSITIONS = {"resolved", "not-deciding", "unresolved"}
FACT_ID_RE = re.compile(r"[A-Za-z][A-Za-z0-9_-]{0,63}\Z")
MAX_SOURCE_FILES = 100
MAX_SOURCE_BYTES = 5 * 1024 * 1024
FRONTMATTER_RE = re.compile(
    r"\A---\s*\n(?P<front>.*?)\n---\s*\n(?P<body>.*)\Z", re.DOTALL
)
EVIDENCE_GATES = [
    "Every fact that decides the primary card's IF condition is tied to frozen source evidence of the required kind.",
    "Every unresolved discovery question is resolved from evidence or shown not to decide the study; unresolved deciding context invalidates the run.",
    "The reproduction maps every deciding comparison fact to a frozen fixture location and preserves it.",
    "The checks exercise one named engineering property and are capable of distinguishing the human and alternative designs on that property, including when the conclusion is equivalent.",
    "The source snapshot, revision, language, project toolchain, fixture toolchain, language standard, and executed commands are recorded consistently.",
]
CRAFT_CRITERIA = [
    "The card analysis establishes whether the primary card applies and distinguishes silence, disagreement, coarseness, and missing language specialization.",
    "A PASS-guided alternative is implemented rather than merely described and preserves the stated contract and constraints.",
    "The comparison evaluates a named improvement target using behavior and constraints rather than proxy counts or style preference.",
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


def manifest_digest(manifest: list[dict[str, Any]]) -> str:
    encoded = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return digest_bytes(encoded)


def discovery_template() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "source_facts": [],
        "unresolved_context": [],
    }


def validate_locator(
    locator: Any, root: Path, allowed_areas: set[str], label: str,
) -> list[str]:
    errors: list[str] = []
    if not isinstance(locator, dict):
        return [f"{label} must be an object"]
    unknown = sorted(set(locator) - {"area", "path", "start_line", "end_line", "kind"})
    if unknown:
        errors.append(f"{label} has unknown keys: {', '.join(unknown)}")
    area = locator.get("area")
    if area not in allowed_areas:
        errors.append(f"{label}.area must be one of {sorted(allowed_areas)}")
        return errors
    evidence_kind = locator.get("kind")
    if evidence_kind not in EVIDENCE_KINDS:
        errors.append(f"{label}.kind must be one of {sorted(EVIDENCE_KINDS)}")
    relative = Path(str(locator.get("path") or ""))
    if not str(relative) or relative.is_absolute() or ".." in relative.parts:
        errors.append(f"{label}.path must be relative and bounded")
        return errors
    area_root = root / "student" / str(area)
    try:
        path = require_inside(area_root / relative, area_root, label)
    except StudyError as exc:
        errors.append(str(exc))
        return errors
    if not path.is_file():
        errors.append(f"{label}.path does not exist: {relative.as_posix()}")
        return errors
    start = locator.get("start_line")
    end = locator.get("end_line")
    if not isinstance(start, int) or isinstance(start, bool) or start < 1:
        errors.append(f"{label}.start_line must be a positive integer")
        return errors
    if not isinstance(end, int) or isinstance(end, bool) or end < start:
        errors.append(f"{label}.end_line must be an integer at least start_line")
        return errors
    line_count = len(path.read_text(encoding="utf-8", errors="replace").splitlines())
    if end > line_count:
        errors.append(f"{label} ends at line {end}, beyond {relative.as_posix()}:{line_count}")
    return errors


def validate_discovery(discovery: dict[str, Any], root: Path) -> list[str]:
    errors: list[str] = []
    if discovery.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"discovery schema_version must be {SCHEMA_VERSION}")
    facts = discovery.get("source_facts")
    if not isinstance(facts, list) or not facts:
        errors.append("discovery.source_facts must be a non-empty list")
        facts = []
    seen: set[str] = set()
    for index, fact in enumerate(facts, start=1):
        label = f"source fact {index}"
        if not isinstance(fact, dict):
            errors.append(f"{label} must be an object")
            continue
        unknown = sorted(set(fact) - {"fact_id", "claim", "fact_kind", "evidence"})
        if unknown:
            errors.append(f"{label} has unknown keys: {', '.join(unknown)}")
        fact_id = str(fact.get("fact_id") or "")
        if not FACT_ID_RE.fullmatch(fact_id):
            errors.append(f"{label}.fact_id must be a stable identifier")
        elif fact_id in seen:
            errors.append(f"duplicate discovery identifier: {fact_id}")
        else:
            seen.add(fact_id)
        if not str(fact.get("claim") or "").strip():
            errors.append(f"{label}.claim is required")
        fact_kind = fact.get("fact_kind")
        if fact_kind not in FACT_KINDS:
            errors.append(f"{label}.fact_kind must be one of {sorted(FACT_KINDS)}")
        evidence = fact.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            errors.append(f"{label}.evidence must be a non-empty list")
            evidence = []
        for evidence_index, locator in enumerate(evidence, start=1):
            errors.extend(validate_locator(
                locator, root, {"source"}, f"{label} evidence {evidence_index}"
            ))
        kinds = {
            item.get("kind") for item in evidence if isinstance(item, dict)
        }
        if fact_kind in {"type", "signature"} and "declaration" not in kinds:
            errors.append(f"{label} requires declaration evidence")
        if fact_kind == "build" and "configuration" not in kinds:
            errors.append(f"{label} requires configuration evidence")
    unresolved = discovery.get("unresolved_context")
    if not isinstance(unresolved, list):
        errors.append("discovery.unresolved_context must be a list")
        unresolved = []
    for index, item in enumerate(unresolved, start=1):
        label = f"unresolved context {index}"
        if not isinstance(item, dict):
            errors.append(f"{label} must be an object")
            continue
        unknown = sorted(set(item) - {"context_id", "question", "potentially_deciding"})
        if unknown:
            errors.append(f"{label} has unknown keys: {', '.join(unknown)}")
        context_id = str(item.get("context_id") or "")
        if not FACT_ID_RE.fullmatch(context_id):
            errors.append(f"{label}.context_id must be a stable identifier")
        elif context_id in seen:
            errors.append(f"duplicate discovery identifier: {context_id}")
        else:
            seen.add(context_id)
        if not str(item.get("question") or "").strip():
            errors.append(f"{label}.question is required")
        if not isinstance(item.get("potentially_deciding"), bool):
            errors.append(f"{label}.potentially_deciding must be true or false")
    return errors


def read_discovery(root: Path) -> dict[str, Any]:
    return read_json(root / "student" / "answer" / "discovery.json")


def discovery_brief(run: dict[str, Any]) -> str:
    source_list = "\n".join(f"- `source/{item['path']}`" for item in run["source_files"])
    return f"""# Code Apprenticeship — Human Design Discovery

Study `{run['review_subject']}` at revision `{run['revision']}` as a
`{run['selection_role']}` source. Evidence role: `{run['evidence_role']}`.
Language: `{run['language']}` at `{run['language_standard']}`. Project
toolchain: `{run['project_toolchain']}`. Frozen source snapshot:
`{run['source_snapshot_sha256']}`.

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

Also complete `answer/discovery.json`. Give every source-backed fact a stable
`fact_id`, a fact kind, and exact frozen source line locations. A type or
signature fact requires declaration evidence; a build fact requires
configuration evidence. List every unavailable question under
`unresolved_context`, even when you currently believe it will not decide the
study. The evidence auditor, not the discoverer, dispositions those questions.

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
  only the behavior they cover. `equivalent` does not waive this requirement: it
  means a property-sensitive check could distinguish the designs but observed no
  material difference.
- `answer/machine_evidence.md`: record exact build/run commands, outputs, failure
  or boundary cases, and what each result establishes.
- `work/`: place the actual alternative, probes, tests, and build material here.

The alternative must be implemented, not merely described. Compare behavior,
constraints, ownership, failure handling, testability, maintainability, and
language idiom. Counts and stylistic preference cannot establish improvement.
Record the project toolchain separately from the actual fixture compiler,
language standard, and exact commands. Do not change the frozen discovery or the
copied human source.
"""


def rubric() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "evidence_gates": EVIDENCE_GATES,
        "craft_criteria": CRAFT_CRITERIA,
    }


def audit_brief(run: dict[str, Any]) -> str:
    return f"""# Code Apprenticeship — Evidence Audit

Audit evidence validity only. Do not decide whether the card is good or whether
the alternative is preferable; a valid audit causes the controller to create a
separate craft-grade form.

Complete `audit.json`. Evidence role: `{run['evidence_role']}`.

## Evidence locators

Every locator has this exact shape:

```json
{{"area":"source","path":"relative/file.cpp","start_line":1,"end_line":3,"kind":"declaration"}}
```

Allowed areas are constrained by each field. Allowed kinds are declaration,
configuration, implementation, call-site, test, and machine-output.

## Required valid-audit records

- `card_if_fact_ids`: discovery fact IDs that establish the primary card's IF.
- `comparison_fact_ids`: every discovery fact the human/alternative comparison
  depends on; it must include every card-IF fact.
- `context_resolutions`: exactly one entry for every discovery unresolved-context
  ID, with `disposition` resolved or not-deciding, a rationale, and evidence when
  resolved. Any unresolved deciding item makes the audit invalid.
- `reproduction_map`: exactly one entry per comparison fact:
  `{{"source_fact_id":"...","preservation":"preserved","explanation":"...","fixture_evidence":[...]}}`.
- Distinct `human_implementation_evidence` and
  `alternative_implementation_evidence` locations.
- One `improvement_property` from the template vocabulary, a concrete target,
  and at least one check with this shape:
  `{{"check_id":"...","property":"...","capable_of_distinguishing":true,"observed_difference":false,"result":"...","evidence":[...]}}`.
  Equivalent is not an exemption: at least one check must be capable of seeing a
  difference on the named property.
- Metadata copied exactly from the frozen run, plus the actual fixture toolchain,
  exact commands, and machine-evidence locations.

Set every gate to pass with specific evidence only when all five structures are
complete. Otherwise set `validity` to invalid, name the blocker attribution and
reason, leave every gate not_tested, and stop. A valid held-out audit requires a
separate auditor role.
"""


def grade_brief(run: dict[str, Any], audit: dict[str, Any]) -> str:
    return f"""# Code Apprenticeship — Craft Grade

The evidence audit is frozen and valid. Grade the card and engineering
comparison; do not rewrite or re-grade the evidence audit.

Property: `{audit['improvement_property']}`
Target: {audit['improvement_target']}
Evidence role: `{run['evidence_role']}`

Complete `grade.json`. Each criterion is binary pass/fail with specific evidence.
The overall qualification is pass only when every criterion passes. Conclude
improved, human-preferred, tradeoff, or equivalent. Equivalent is allowed only
when the audit's property-sensitive checks observed no difference; the other
three outcomes require an observed difference. One study never proves skill
attribution. A held-out validation requires a separate craft grader.

Motivating-example regressions and exploratory studies cannot retain habit
candidates or request habit promotion, card repair, or language-support changes;
they finalize as local study records rather than candidate memory events.
"""


def audit_template(run: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "validity": "invalid",
        "invalid_reason": "complete this evidence audit",
        "blocker_attribution": "unresolved",
        "auditor_relation": "separate",
        "card_if_status": "not-established",
        "card_if_fact_ids": [],
        "comparison_fact_ids": [],
        "context_resolutions": [],
        "reproduction_map": [],
        "human_implementation_evidence": [],
        "alternative_implementation_evidence": [],
        "improvement_property": "correctness",
        "improvement_target": "",
        "improvement_checks": [],
        "metadata": {
            "revision": run["revision"],
            "source_snapshot_sha256": run["source_snapshot_sha256"],
            "language": run["language"],
            "language_standard": run["language_standard"],
            "project_toolchain": run["project_toolchain"],
            "fixture_toolchain": "",
            "commands": [],
            "evidence": [],
        },
        "gates": [
            {"gate": gate, "result": "not_tested", "evidence": ""}
            for gate in EVIDENCE_GATES
        ],
        "notes": "",
    }


def grade_template() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "grader_relation": "separate",
        "qualification_result": "not_tested",
        "improvement_outcome": "not_tested",
        "next_action": "repair-administration",
        "attribution": "unresolved",
        "attributed_object_id": None,
        "artifact_quality": "unproven",
        "process_validity": "unproven",
        "skill_attribution": "unproven",
        "criteria": [
            {"criterion": criterion, "result": "not_tested", "evidence": ""}
            for criterion in CRAFT_CRITERIA
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
    if run.get("schema_version") not in READABLE_SCHEMA_VERSIONS:
        raise StudyError(f"unsupported study schema: {run.get('schema_version')}")
    if run.get("state") not in STATES:
        raise StudyError(f"invalid study state: {run.get('state')}")
    return root, run


def require_current_schema(run: dict[str, Any]) -> None:
    if run.get("schema_version") != SCHEMA_VERSION:
        raise StudyError(
            f"schema-v{run.get('schema_version')} studies are read-only; "
            f"start a fresh schema-v{SCHEMA_VERSION} study"
        )


def verify_sources(root: Path, run: dict[str, Any]) -> None:
    verify_manifest(root / "student" / "source", run["source_files"], "human source")


def verify_discovery(root: Path, run: dict[str, Any]) -> None:
    frozen = run.get("discovery_freeze")
    if not isinstance(frozen, dict):
        raise StudyError("discovery has not been frozen")
    expected = frozen.get("manifest")
    if not isinstance(expected, list) or not expected:
        raise StudyError("discovery freeze has no manifest")
    actual = tree_manifest(root / "student" / "answer", ["discovery.md", "discovery.json"])
    if actual != expected:
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
    evidence_role: str = "held-out-validation",
    language_standard: str = "unspecified",
) -> dict[str, Any]:
    if selection_role not in SELECTION_ROLES:
        raise StudyError(f"selection role must be one of {sorted(SELECTION_ROLES)}")
    if evidence_role not in EVIDENCE_ROLES:
        raise StudyError(f"evidence role must be one of {sorted(EVIDENCE_ROLES)}")
    values = {
        "review subject": review_subject,
        "revision": revision,
        "language": language,
        "toolchain": toolchain,
        "language standard": language_standard,
        "engineering decision": engineering_decision,
    }
    for label, value in values.items():
        if not str(value).strip():
            raise StudyError(f"{label} must be non-empty")
    if revision.strip().casefold() in FLOATING_REVISIONS:
        raise StudyError(
            "a Code Apprenticeship study requires an immutable revision, not a "
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
        "evidence_role": evidence_role,
        "review_subject": review_subject.strip(),
        "revision": revision.strip(),
        "language": language.strip(),
        "language_standard": language_standard.strip(),
        "project_toolchain": toolchain.strip(),
        "engineering_decision": engineering_decision.strip(),
        "primary_card_id": cards[0].object_id,
        "supporting_card_ids": [card.object_id for card in cards[1:]],
        "exposed_card_ids": [],
        "source_files": [],
        "source_snapshot_sha256": None,
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
        run["source_snapshot_sha256"] = manifest_digest(run["source_files"])
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
        write_json_atomic(
            temporary / "student" / "answer" / "discovery.json",
            discovery_template(),
        )
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
    require_current_schema(run)
    if run["state"] != "prepared":
        raise StudyError(f"freeze-discovery requires prepared, found {run['state']}")
    verify_sources(root, run)
    discovery = root / "student" / "answer" / "discovery.md"
    if not discovery.is_file() or not discovery.read_text(encoding="utf-8").strip():
        raise StudyError("student/answer/discovery.md must be produced before freezing")
    discovery_data = read_discovery(root)
    discovery_errors = validate_discovery(discovery_data, root)
    if discovery_errors:
        raise StudyError("invalid discovery evidence: " + "; ".join(discovery_errors))
    run["discovery_freeze"] = {
        "manifest": tree_manifest(
            root / "student" / "answer", ["discovery.md", "discovery.json"]
        ),
        "frozen_at": now_utc(),
    }
    run["state"] = "discovery-frozen"
    save_run(root, run)
    return run


def open_guidance(run_path: Path) -> dict[str, Any]:
    root, run = load_run(run_path)
    require_current_schema(run)
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
    require_current_schema(run)
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
    require_current_schema(run)
    if run["state"] != "work-frozen":
        raise StudyError(f"reveal requires work-frozen, found {run['state']}")
    verify_sources(root, run)
    verify_discovery(root, run)
    verify_cards(root, run)
    verify_work(root, run)
    grader = root / "grader"
    grader.mkdir()
    shutil.copy2(root / "controller" / "rubric.json", grader / "rubric.json")
    write_text_atomic(grader / "audit_guidance.md", audit_brief(run))
    write_json_atomic(grader / "audit.json", audit_template(run))
    run["state"] = "revealed"
    run["revealed_at"] = now_utc()
    save_run(root, run)
    return run


def invalidate(run_path: Path, reason: str) -> dict[str, Any]:
    root, run = load_run(run_path)
    require_current_schema(run)
    if run["state"] == "finalized":
        raise StudyError("a finalized study cannot be invalidated")
    if not reason.strip():
        raise StudyError("invalidation reason must be non-empty")
    run["state"] = "invalidated"
    run["invalid_reason"] = reason.strip()
    run["invalidated_at"] = now_utc()
    save_run(root, run)
    return run


def validate_locator_list(
    value: Any, root: Path, allowed_areas: set[str], label: str,
    *, required: bool = True,
) -> list[str]:
    if not isinstance(value, list) or (required and not value):
        return [f"{label} must be a{' non-empty' if required else ''} list"]
    errors: list[str] = []
    for index, locator in enumerate(value, start=1):
        errors.extend(validate_locator(locator, root, allowed_areas, f"{label} {index}"))
    return errors


def validate_audit(audit: dict[str, Any], run: dict[str, Any], root: Path) -> list[str]:
    errors: list[str] = []
    validity = audit.get("validity")
    if audit.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"audit schema_version must be {SCHEMA_VERSION}")
    if validity not in {"valid", "invalid"}:
        errors.append("audit validity must be valid or invalid")
    reason = str(audit.get("invalid_reason") or "").strip()
    if validity == "invalid" and not reason:
        errors.append("invalid_reason is required when the audit is invalid")
    if validity == "valid" and reason:
        errors.append("invalid_reason must be empty when the audit is valid")
    blocker = audit.get("blocker_attribution")
    if validity == "invalid" and blocker not in {
        "source-context", "fixture", "runtime-tool", "unresolved"
    }:
        errors.append("an invalid audit must attribute its blocker")
    if validity == "valid" and blocker != "none":
        errors.append("a valid audit must use blocker_attribution none")
    if audit.get("auditor_relation") not in GRADER_RELATIONS:
        errors.append(f"auditor_relation must be one of {sorted(GRADER_RELATIONS)}")
    if (
        validity == "valid"
        and run.get("evidence_role") == "held-out-validation"
        and audit.get("auditor_relation") != "separate"
    ):
        errors.append("held-out validation requires a separate evidence auditor")

    gates = audit.get("gates")
    if not isinstance(gates, list):
        return errors + ["audit gates must be a list"]
    actual_gates = [item.get("gate") for item in gates if isinstance(item, dict)]
    if actual_gates != EVIDENCE_GATES:
        return errors + ["audit gates differ from the canonical evidence gates"]
    for index, item in enumerate(gates, start=1):
        result = item.get("result")
        expected = "pass" if validity == "valid" else "not_tested"
        if result != expected:
            errors.append(f"audit gate {index} must be {expected}")
        if validity == "valid" and not str(item.get("evidence") or "").strip():
            errors.append(f"audit gate {index} requires evidence")
    if validity != "valid":
        return errors

    discovery = read_discovery(root)
    facts = {item["fact_id"]: item for item in discovery["source_facts"]}
    contexts = {item["context_id"]: item for item in discovery["unresolved_context"]}
    if audit.get("card_if_status") != "established":
        errors.append("a valid audit requires the primary card IF to be established")
    card_if_ids = audit.get("card_if_fact_ids")
    if not isinstance(card_if_ids, list) or not card_if_ids:
        errors.append("card_if_fact_ids must be a non-empty list")
        card_if_ids = []
    unknown_if = sorted(set(card_if_ids) - set(facts))
    if unknown_if:
        errors.append("unknown card IF fact IDs: " + ", ".join(unknown_if))
    comparison_ids = audit.get("comparison_fact_ids")
    if not isinstance(comparison_ids, list) or not comparison_ids:
        errors.append("comparison_fact_ids must be a non-empty list")
        comparison_ids = []
    unknown_comparison = sorted(set(comparison_ids) - set(facts))
    if unknown_comparison:
        errors.append("unknown comparison fact IDs: " + ", ".join(unknown_comparison))
    if not set(card_if_ids).issubset(set(comparison_ids)):
        errors.append("comparison_fact_ids must include every card_if_fact_id")

    resolutions = audit.get("context_resolutions")
    if not isinstance(resolutions, list):
        errors.append("context_resolutions must be a list")
        resolutions = []
    resolution_ids: list[str] = []
    for index, resolution in enumerate(resolutions, start=1):
        label = f"context resolution {index}"
        if not isinstance(resolution, dict):
            errors.append(f"{label} must be an object")
            continue
        context_id = str(resolution.get("context_id") or "")
        resolution_ids.append(context_id)
        disposition = resolution.get("disposition")
        if disposition not in CONTEXT_DISPOSITIONS:
            errors.append(f"{label}.disposition must be one of {sorted(CONTEXT_DISPOSITIONS)}")
        if disposition == "unresolved":
            errors.append(f"{label} remains unresolved")
        if not str(resolution.get("rationale") or "").strip():
            errors.append(f"{label}.rationale is required")
        evidence = resolution.get("evidence")
        errors.extend(validate_locator_list(
            evidence, root, {"source", "answer"}, f"{label} evidence",
            required=disposition == "resolved",
        ))
    if len(resolution_ids) != len(set(resolution_ids)):
        errors.append("context resolutions may name each context only once")
    if set(resolution_ids) != set(contexts):
        missing = sorted(set(contexts) - set(resolution_ids))
        extra = sorted(set(resolution_ids) - set(contexts))
        if missing:
            errors.append("missing context resolutions: " + ", ".join(missing))
        if extra:
            errors.append("unknown context resolutions: " + ", ".join(extra))

    reproduction = audit.get("reproduction_map")
    if not isinstance(reproduction, list):
        errors.append("reproduction_map must be a list")
        reproduction = []
    reproduced_ids: list[str] = []
    for index, entry in enumerate(reproduction, start=1):
        label = f"reproduction entry {index}"
        if not isinstance(entry, dict):
            errors.append(f"{label} must be an object")
            continue
        fact_id = str(entry.get("source_fact_id") or "")
        reproduced_ids.append(fact_id)
        if entry.get("preservation") != "preserved":
            errors.append(f"{label}.preservation must be preserved")
        if not str(entry.get("explanation") or "").strip():
            errors.append(f"{label}.explanation is required")
        errors.extend(validate_locator_list(
            entry.get("fixture_evidence"), root, {"work"},
            f"{label} fixture_evidence",
        ))
    if len(reproduced_ids) != len(set(reproduced_ids)):
        errors.append("reproduction_map may name each fact only once")
    if set(reproduced_ids) != set(comparison_ids):
        errors.append("reproduction_map must cover exactly the comparison_fact_ids")

    human_evidence = audit.get("human_implementation_evidence")
    alternative_evidence = audit.get("alternative_implementation_evidence")
    errors.extend(validate_locator_list(
        human_evidence, root, {"source", "work"}, "human implementation evidence"
    ))
    errors.extend(validate_locator_list(
        alternative_evidence, root, {"work"}, "alternative implementation evidence"
    ))
    if isinstance(human_evidence, list) and isinstance(alternative_evidence, list):
        human_locations = {
            (item.get("area"), item.get("path"), item.get("start_line"), item.get("end_line"))
            for item in human_evidence if isinstance(item, dict)
        }
        alternative_locations = {
            (item.get("area"), item.get("path"), item.get("start_line"), item.get("end_line"))
            for item in alternative_evidence if isinstance(item, dict)
        }
        if human_locations & alternative_locations:
            errors.append("human and alternative implementations require distinct evidence locations")

    property_name = audit.get("improvement_property")
    if property_name not in IMPROVEMENT_PROPERTIES:
        errors.append(f"improvement_property must be one of {sorted(IMPROVEMENT_PROPERTIES)}")
    if not str(audit.get("improvement_target") or "").strip():
        errors.append("improvement_target is required")
    checks = audit.get("improvement_checks")
    if not isinstance(checks, list) or not checks:
        errors.append("improvement_checks must be a non-empty list")
        checks = []
    capable = False
    check_ids: set[str] = set()
    for index, check in enumerate(checks, start=1):
        label = f"improvement check {index}"
        if not isinstance(check, dict):
            errors.append(f"{label} must be an object")
            continue
        check_id = str(check.get("check_id") or "")
        if not FACT_ID_RE.fullmatch(check_id) or check_id in check_ids:
            errors.append(f"{label}.check_id must be unique and stable")
        check_ids.add(check_id)
        if check.get("property") != property_name:
            errors.append(f"{label}.property must match improvement_property")
        if not isinstance(check.get("capable_of_distinguishing"), bool):
            errors.append(f"{label}.capable_of_distinguishing must be true or false")
        capable = capable or check.get("capable_of_distinguishing") is True
        if not isinstance(check.get("observed_difference"), bool):
            errors.append(f"{label}.observed_difference must be true or false")
        if not str(check.get("result") or "").strip():
            errors.append(f"{label}.result is required")
        errors.extend(validate_locator_list(
            check.get("evidence"), root, {"work", "answer"}, f"{label} evidence"
        ))
    if not capable:
        errors.append("at least one improvement check must be capable of distinguishing the designs")

    metadata = audit.get("metadata")
    if not isinstance(metadata, dict):
        errors.append("metadata must be an object")
    else:
        expected = {
            "revision": run["revision"],
            "source_snapshot_sha256": run["source_snapshot_sha256"],
            "language": run["language"],
            "language_standard": run["language_standard"],
            "project_toolchain": run["project_toolchain"],
        }
        for key, value in expected.items():
            if metadata.get(key) != value:
                errors.append(f"metadata.{key} must match the frozen run")
        if not str(metadata.get("fixture_toolchain") or "").strip():
            errors.append("metadata.fixture_toolchain is required")
        commands = metadata.get("commands")
        if not isinstance(commands, list) or not commands or any(
            not isinstance(item, str) or not item.strip() for item in commands
        ):
            errors.append("metadata.commands must be a non-empty list of exact commands")
        errors.extend(validate_locator_list(
            metadata.get("evidence"), root, {"answer", "work"}, "metadata evidence"
        ))
    return errors


def verify_audit(root: Path, run: dict[str, Any]) -> dict[str, Any]:
    frozen = run.get("audit_freeze")
    if not isinstance(frozen, dict):
        raise StudyError("evidence audit has not been frozen")
    path = root / "grader" / "audit.json"
    if not path.is_file() or digest_file(path) != frozen.get("sha256"):
        raise StudyError("evidence audit changed after it was frozen")
    return read_json(path)


def accept_audit(run_path: Path) -> dict[str, Any]:
    root, run = load_run(run_path)
    require_current_schema(run)
    if run["state"] != "revealed":
        raise StudyError(f"accept-audit requires revealed, found {run['state']}")
    verify_sources(root, run)
    verify_discovery(root, run)
    verify_cards(root, run)
    verify_work(root, run)
    path = root / "grader" / "audit.json"
    audit = read_json(path)
    errors = validate_audit(audit, run, root)
    if errors:
        raise StudyError("invalid evidence audit: " + "; ".join(errors))
    run["audit_freeze"] = {
        "path": "grader/audit.json",
        "bytes": path.stat().st_size,
        "sha256": digest_file(path),
        "frozen_at": now_utc(),
    }
    if audit["validity"] == "valid":
        write_text_atomic(root / "grader" / "grade_guidance.md", grade_brief(run, audit))
        write_json_atomic(root / "grader" / "grade.json", grade_template())
    run["state"] = "evidence-audited"
    save_run(root, run)
    return run


def validate_grade(
    grade: dict[str, Any], run: dict[str, Any], audit: dict[str, Any]
) -> list[str]:
    errors: list[str] = []
    if grade.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"grade schema_version must be {SCHEMA_VERSION}")
    if grade.get("grader_relation") not in GRADER_RELATIONS:
        errors.append(f"grader_relation must be one of {sorted(GRADER_RELATIONS)}")
    if (
        run.get("evidence_role") == "held-out-validation"
        and grade.get("grader_relation") != "separate"
    ):
        errors.append("held-out validation requires a separate craft grader")
    for key in ("artifact_quality", "process_validity", "skill_attribution"):
        if grade.get(key) not in SCORES:
            errors.append(f"{key} must be one of {sorted(SCORES)}")
    if grade.get("skill_attribution") != "unproven":
        errors.append("one field test cannot prove skill attribution")
    if grade.get("qualification_result") not in {"pass", "fail"}:
        errors.append("qualification_result must be pass or fail after a valid audit")
    outcome = grade.get("improvement_outcome")
    if outcome not in IMPROVEMENT_OUTCOMES - {"not_tested"}:
        errors.append("a valid study must conclude the improvement comparison")
    observed_difference = any(
        item.get("observed_difference") is True
        for item in audit.get("improvement_checks") or []
        if isinstance(item, dict)
    )
    if outcome == "equivalent" and observed_difference:
        errors.append("equivalent conflicts with an observed improvement-property difference")
    if outcome in {"improved", "human-preferred", "tradeoff"} and not observed_difference:
        errors.append(f"{outcome} requires an observed improvement-property difference")
    if grade.get("next_action") not in NEXT_ACTIONS:
        errors.append("invalid next_action")
    attribution = grade.get("attribution")
    if attribution not in {"none", "skillcard", "application", "human-code"}:
        errors.append("a craft grade must attribute only a craft result")
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
    if actual_text != CRAFT_CRITERIA:
        return errors + ["criteria differ from the canonical craft rubric"]
    results: list[str] = []
    for index, item in enumerate(criteria, start=1):
        result = item.get("result")
        results.append(str(result))
        if result not in {"pass", "fail"}:
            errors.append(f"criterion {index}: result must be pass or fail")
        if not str(item.get("evidence") or "").strip():
            errors.append(f"criterion {index}: evidence is required")
    expected_result = "pass" if all(result == "pass" for result in results) else "fail"
    if grade.get("qualification_result") != expected_result:
        errors.append(f"qualification_result must be {expected_result}")
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
    observations = grade.get("observations")
    if not isinstance(observations, list) or not any(
        isinstance(item, str) and item.strip() for item in observations
    ):
        errors.append("a craft grade requires at least one observation")
    habits = grade.get("habit_candidates")
    if not isinstance(habits, list):
        errors.append("habit_candidates must be a list")
        habits = []
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
    if grade.get("next_action") == "habit-promotion-review" and not habits:
        errors.append("habit-promotion-review requires at least one habit candidate")
    if run["evidence_role"] != "held-out-validation":
        if habits:
            errors.append("non-held-out studies cannot retain habit candidates")
        if grade.get("next_action") in {
            "habit-promotion-review", "card-repair", "language-support"
        }:
            errors.append("non-held-out studies cannot claim promotion or card repair")
    return errors


def candidate_event(
    run: dict[str, Any], audit: dict[str, Any] | None,
    grade: dict[str, Any] | None, event_id: str, task: str, event_date: str,
) -> dict[str, Any]:
    if not event_id.strip() or not task.strip():
        raise StudyError("event_id and task must be non-empty")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", event_date):
        raise StudyError("date must be YYYY-MM-DD")
    if audit is None:
        validity = "invalid"
        invalid_reason = str(run.get("invalid_reason") or "study invalidated")
        observations: list[str] = []
        artifact_quality = "failed"
        process_validity = "failed"
        notes = "Code Apprenticeship study invalidated before qualification."
    elif audit["validity"] == "invalid":
        validity = "invalid"
        invalid_reason = str(audit["invalid_reason"])
        observations = []
        artifact_quality = "unproven"
        process_validity = "failed"
        notes = (
            "Code Apprenticeship evidence audit invalidated the study; "
            f"blocker={audit['blocker_attribution']}."
        )
    else:
        assert grade is not None
        validity = "valid"
        invalid_reason = ""
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
            f"property={audit['improvement_property']}; "
            f"target={audit['improvement_target']}; "
            f"attribution={grade['attribution']}; next={grade['next_action']}; "
            f"auditor={audit['auditor_relation']}; grader={grade['grader_relation']}."
        )
        if str(grade.get("notes") or "").strip():
            notes += " " + str(grade["notes"]).strip()
    notes += (
        f" Subject: {run['review_subject']} at {run['revision']}; "
        f"selection={run['selection_role']}; evidence_role={run['evidence_role']}; "
        f"language={run['language']} {run['language_standard']}; "
        f"project_toolchain={run['project_toolchain']}."
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
    require_current_schema(run)
    if run["state"] not in {"evidence-audited", "invalidated"}:
        raise StudyError(
            f"finalize requires evidence-audited or invalidated, found {run['state']}"
        )
    audit: dict[str, Any] | None = None
    grade: dict[str, Any] | None = None
    if run["state"] == "evidence-audited":
        verify_sources(root, run)
        verify_discovery(root, run)
        verify_cards(root, run)
        verify_work(root, run)
        audit = verify_audit(root, run)
        if audit["validity"] == "valid":
            grade = read_json((grade_path or root / "grader" / "grade.json").resolve())
            errors = validate_grade(grade, run, audit)
            if errors:
                raise StudyError("invalid craft grade: " + "; ".join(errors))
    result = {
        "schema_version": SCHEMA_VERSION,
        "validity": (
            "invalid" if audit is None else audit["validity"]
        ),
        "evidence_role": run["evidence_role"],
        "audit": audit,
        "grade": grade,
        "invalid_reason": (
            run.get("invalid_reason") if audit is None else audit.get("invalid_reason")
        ),
    }
    write_json_atomic(root / "study_result.json", result)
    event: dict[str, Any] | None = None
    if run["evidence_role"] == "held-out-validation":
        event = candidate_event(
            run, audit, grade, event_id, task, event_date or date.today().isoformat()
        )
        write_json_atomic(root / "candidate_training_event.json", event)
    run["state"] = "finalized"
    run["finalized_at"] = now_utc()
    run["candidate_event"] = (
        "candidate_training_event.json" if event is not None else None
    )
    save_run(root, run)
    return event or result


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
    prepare_parser.add_argument("--evidence-role", choices=sorted(EVIDENCE_ROLES), required=True)
    prepare_parser.add_argument("--subject", required=True)
    prepare_parser.add_argument("--revision", required=True)
    prepare_parser.add_argument("--language", required=True)
    prepare_parser.add_argument("--language-standard", required=True)
    prepare_parser.add_argument("--project-toolchain", "--toolchain", dest="toolchain", required=True)
    prepare_parser.add_argument("--decision", required=True)
    prepare_parser.add_argument("--out", type=Path, required=True)

    for name in (
        "freeze-discovery", "open-guidance", "freeze-work", "reveal",
        "accept-audit", "status",
    ):
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
                args.evidence_role, args.language_standard,
            )
            print(f"PREPARED: {args.out.resolve()}")
            print(f"Primary card held private: {run['primary_card_id']}")
            print("Expose only student/; complete discovery before opening guidance.")
        elif args.command == "freeze-discovery":
            run = freeze_discovery(args.run)
            print(
                "DISCOVERY FROZEN: "
                f"{len(run['discovery_freeze']['manifest'])} evidence file(s)"
            )
        elif args.command == "open-guidance":
            run = open_guidance(args.run)
            print("GUIDANCE OPEN: " + ", ".join(run["exposed_card_ids"]))
        elif args.command == "freeze-work":
            run = freeze_work(args.run)
            print(f"WORK FROZEN: {len(run['work_freeze'])} file(s)")
        elif args.command == "reveal":
            reveal(args.run)
            print(f"EVIDENCE AUDIT REVEALED: {args.run.resolve() / 'grader' / 'audit.json'}")
        elif args.command == "accept-audit":
            run = accept_audit(args.run)
            print(f"EVIDENCE AUDIT FROZEN: {run['state']}")
        elif args.command == "invalidate":
            run = invalidate(args.run, args.reason)
            print(f"INVALIDATED: {run['invalid_reason']}")
        elif args.command == "finalize":
            result = finalize(args.run, args.event_id, args.task, args.date, args.grade)
            label = result.get("event_id", "study-only")
            print(f"FINALIZED: {label} ({result['validity']})")
            print("Skillset Memory was not modified.")
        elif args.command == "status":
            root, run = load_run(args.run)
            print(json.dumps({
                "run": str(root),
                "schema_version": run["schema_version"],
                "legacy_read_only": run["schema_version"] != SCHEMA_VERSION,
                "state": run["state"],
                "primary_card_id": run["primary_card_id"],
                "supporting_card_ids": run["supporting_card_ids"],
                "source_files": [item["path"] for item in run["source_files"]],
                "discovery_frozen": bool(run.get("discovery_freeze")),
                "guidance_open": bool(run.get("exposed_cards")),
                "work_frozen": bool(run.get("work_freeze")),
                "evidence_audited": bool(run.get("audit_freeze")),
                "invalid_reason": run.get("invalid_reason"),
                "candidate_event": run.get("candidate_event"),
            }, indent=2, ensure_ascii=False))
        return 0
    except (StudyError, OSError, yaml.YAMLError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
