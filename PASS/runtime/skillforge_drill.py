#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Deterministic administration for portable SkillForge Drills.

The model still supplies the task instance and semantic grading. This helper
owns the enforceable boundary: blind materialization, answer freeze, rubric
reveal, complete criterion accounting, invalidation, and candidate-event export.
It never retries a sitting or writes Skillset Memory.
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
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import yaml


SCHEMA_VERSION = 1
CUTS = {"before-instructions", "before-success-check"}
STATES = {"prepared", "frozen", "revealed", "invalidated", "finalized"}
CRITERION_RESULTS = {"pass", "partial", "fail", "not_tested"}
OVERALL_RESULTS = {"pass", "partial", "fail"}
GRADER_RELATIONS = {"separate", "same-reader", "human"}
SCORES = {"strong", "adequate", "weak", "failed", "unproven"}
STAGES = {"improved", "partial", "unchanged", "failed", "untested"}
FRONTMATTER_RE = re.compile(
    r"\A---\s*\n(?P<front>.*?)\n---\s*\n(?P<body>.*)\Z", re.DOTALL
)
SECTION_RE = re.compile(
    r"^## (?P<name>[^\n]+)\s*$\n(?P<content>.*?)(?=^## |\Z)",
    re.MULTILINE | re.DOTALL,
)
ITEM_RE = re.compile(r"^(?:[-*+] |\d+[.)] )(?P<text>.+)$")


class DrillError(RuntimeError):
    """A fail-closed administration error."""


@dataclass(frozen=True)
class Drill:
    object_id: str
    name: str
    target_skill: str
    domain: str
    module: str
    relative_path: str
    text: str
    sections: dict[str, str]


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DrillError(f"cannot read JSON from {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise DrillError(f"{path} must contain a JSON object")
    return value


def write_text_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def write_json_atomic(path: Path, value: dict[str, Any]) -> None:
    write_text_atomic(path, json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def card_sections(body: str) -> dict[str, str]:
    return {
        match.group("name").strip(): match.group("content").strip()
        for match in SECTION_RE.finditer(body)
    }


def owning_module(path: Path, library: Path, domain_root: Path) -> str:
    current = path.parent
    while current == domain_root or domain_root in current.parents:
        if (current / "MODULE.yaml").is_file():
            return current.relative_to(library).as_posix()
        current = current.parent
    raise DrillError(f"{path.relative_to(library).as_posix()}: no owning MODULE.yaml")


def parse_drill(path: Path, library: Path) -> Drill:
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    if not match:
        raise DrillError(f"{path.relative_to(library).as_posix()}: invalid frontmatter")
    front = yaml.safe_load(match.group("front"))
    if not isinstance(front, dict) or front.get("object_type") != "drill":
        raise DrillError(f"{path.relative_to(library).as_posix()}: not a Drill")
    sections = card_sections(match.group("body"))
    missing = [
        heading
        for heading in ("Practice Task", "Setup", "Instructions", "Success Check")
        if not sections.get(heading)
    ]
    for field in ("object_id", "name", "target_skill"):
        if not str(front.get(field, "")).strip():
            missing.append(field)
    if missing:
        raise DrillError(
            f"{path.relative_to(library).as_posix()}: missing {', '.join(missing)}"
        )
    relative = path.relative_to(library)
    domain = relative.parts[0]
    return Drill(
        object_id=str(front["object_id"]),
        name=str(front["name"]),
        target_skill=str(front["target_skill"]),
        domain=domain,
        module=owning_module(path, library, library / domain),
        relative_path=relative.as_posix(),
        text=text,
        sections=sections,
    )


def discover(library: Path, domain: str | None = None) -> list[Drill]:
    library = library.resolve()
    root = library if domain is None else (library / domain).resolve()
    if domain is not None and (root.parent != library or not root.is_dir()):
        raise DrillError(f"unknown domain: {domain}")
    if not root.is_dir():
        raise DrillError(f"library does not exist: {library}")
    cards = [parse_drill(path, library) for path in sorted(root.rglob("DRILL_*.md"))]
    ids = [card.object_id for card in cards]
    duplicates = sorted({item for item in ids if ids.count(item) > 1})
    if duplicates:
        raise DrillError(f"duplicate Drill IDs: {', '.join(duplicates)}")
    return cards


def select_drills(library: Path, drill_ids: Iterable[str]) -> list[Drill]:
    requested = list(drill_ids)
    if len(requested) != len(set(requested)):
        raise DrillError("a chain may name each Drill only once")
    by_id = {card.object_id: card for card in discover(library)}
    missing = [item for item in requested if item not in by_id]
    if missing:
        raise DrillError(f"unknown Drill(s): {', '.join(missing)}")
    cards = [by_id[item] for item in requested]
    if len({card.domain for card in cards}) != 1:
        raise DrillError("one sitting may chain Drills from only one domain")
    return cards


def success_criteria(section: str) -> list[str]:
    result: list[str] = []
    current: list[str] = []
    for line in section.splitlines():
        match = ITEM_RE.match(line)
        if match:
            if current:
                result.append(" ".join(current).strip())
            current = [match.group("text").strip()]
        elif current and line.strip():
            current.append(line.strip())
    if current:
        result.append(" ".join(current).strip())
    if not result:
        raise DrillError("Success Check must contain a top-level list")
    return result


def render_student(cards: list[Drill], cut: str, scenario: str) -> str:
    lines = [
        "# SkillForge Blind Drill Sitting",
        "",
        f"Administration cut: `{cut}`",
        "",
        "Only this student directory belongs in the taker's environment.",
        "",
        "## Produce, do not describe",
        "",
        "When an instruction asks you to execute, observe, record, mark, compile, run,",
        "or exercise something, produce that evidence. Prose saying what would happen",
        "does not satisfy the instruction.",
    ]
    for card in cards:
        lines += [
            "",
            f"# {card.name}",
            "",
            "## Practice Task",
            "",
            card.sections["Practice Task"],
            "",
            "## Target Skill",
            "",
            card.target_skill,
            "",
            "## Setup",
            "",
            card.sections["Setup"],
        ]
        if cut == "before-success-check":
            lines += ["", "## Instructions", "", card.sections["Instructions"]]
    lines += ["", "# Controller-Supplied Scenario", "", scenario.strip(), ""]
    return "\n".join(lines)


def render_key(cards: list[Drill], cut: str) -> str:
    lines = [
        "# Private Drill Key",
        "",
        "Do not expose this file or controller/ to the taker before freeze.",
        "",
        f"Administration cut: `{cut}`",
    ]
    for card in cards:
        lines += [
            "",
            f"# {card.object_id} — {card.name}",
            "",
            "## Instructions",
            "",
            card.sections["Instructions"],
            "",
            "## Success Check",
            "",
            card.sections["Success Check"],
        ]
        if card.sections.get("Common Failures"):
            lines += ["", "## Common Failures", "", card.sections["Common Failures"]]
    return "\n".join(lines) + "\n"


def prepare(
    library: Path, drill_ids: Iterable[str], cut: str, scenario_path: Path, out: Path
) -> dict[str, Any]:
    if cut not in CUTS:
        raise DrillError(f"unsupported cut: {cut}")
    out = out.resolve()
    if out.exists():
        raise DrillError(f"refusing to overwrite existing run directory: {out}")
    scenario_path = scenario_path.resolve()
    if not scenario_path.is_file():
        raise DrillError(f"scenario does not exist: {scenario_path}")
    scenario = scenario_path.read_text(encoding="utf-8")
    if not scenario.strip():
        raise DrillError("scenario is empty")
    cards = select_drills(library, drill_ids)
    rubric = {
        "schema_version": SCHEMA_VERSION,
        "drills": [
            {
                "drill_id": card.object_id,
                "name": card.name,
                "criteria": success_criteria(card.sections["Success Check"]),
            }
            for card in cards
        ],
    }
    run = {
        "schema_version": SCHEMA_VERSION,
        "state": "prepared",
        "revision": 1,
        "created_at": now_utc(),
        "domain": cards[0].domain,
        "cut": cut,
        "drills": [
            {
                "drill_id": card.object_id,
                "name": card.name,
                "target_skill": card.target_skill,
                "module": card.module,
                "card_path": card.relative_path,
                "card_sha256": digest_bytes(card.text.encode("utf-8")),
            }
            for card in cards
        ],
        "scenario_sha256": digest_bytes(scenario.encode("utf-8")),
        "answer_freeze": None,
        "invalid_reason": None,
        "automatic_repetitions": 0,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=f".{out.name}.", dir=out.parent))
    try:
        (temporary / "controller").mkdir()
        (temporary / "student").mkdir()
        (temporary / "student" / "task.md").write_text(
            render_student(cards, cut, scenario), encoding="utf-8", newline="\n"
        )
        (temporary / "student" / "answer.md").write_text("", encoding="utf-8")
        (temporary / "controller" / "key.md").write_text(
            render_key(cards, cut), encoding="utf-8", newline="\n"
        )
        (temporary / "controller" / "rubric.json").write_text(
            json.dumps(rubric, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        (temporary / "controller" / "run.json").write_text(
            json.dumps(run, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        os.replace(temporary, out)
    except BaseException:
        if temporary.exists():
            shutil.rmtree(temporary)
        raise
    return run


def load_run(run_path: Path) -> tuple[Path, dict[str, Any]]:
    root = run_path.resolve()
    run_file = root / "controller" / "run.json"
    if not run_file.is_file():
        raise DrillError(f"not a SkillForge Drill run: {root}")
    run = read_json(run_file)
    if run.get("schema_version") != SCHEMA_VERSION or run.get("state") not in STATES:
        raise DrillError("unsupported or malformed run metadata")
    return root, run


def save_run(root: Path, run: dict[str, Any]) -> None:
    run["revision"] = int(run.get("revision", 0)) + 1
    write_json_atomic(root / "controller" / "run.json", run)


def require_inside(path: Path, parent: Path, label: str) -> None:
    try:
        path.relative_to(parent)
    except ValueError as exc:
        raise DrillError(f"{label} must stay inside {parent}") from exc


def make_freeze(root: Path, answer_path: Path) -> dict[str, Any]:
    answer = answer_path.resolve()
    student = (root / "student").resolve()
    require_inside(answer, student, "answer")
    if answer == student:
        raise DrillError("answer must be a file or subdirectory, not the student packet")
    if not answer.exists() or answer.is_symlink():
        raise DrillError(f"answer is missing or is a symbolic link: {answer}")
    files = [answer] if answer.is_file() else sorted(
        item for item in answer.rglob("*") if item.is_file()
    )
    if not files:
        raise DrillError("answer contains no files")
    entries: list[dict[str, Any]] = []
    for item in files:
        if item.is_symlink():
            raise DrillError(f"answer contains a symbolic link: {item}")
        resolved = item.resolve()
        require_inside(resolved, student, "answer artifact")
        entries.append(
            {
                "path": resolved.relative_to(root).as_posix(),
                "size": resolved.stat().st_size,
                "sha256": digest_file(resolved),
            }
        )
    if sum(item["size"] for item in entries) == 0:
        raise DrillError("answer is empty")
    canonical = json.dumps(entries, sort_keys=True, separators=(",", ":")).encode()
    return {
        "answer_root": answer.relative_to(root).as_posix(),
        "files": entries,
        "aggregate_sha256": digest_bytes(canonical),
        "frozen_at": now_utc(),
    }


def verify_freeze(root: Path, freeze: dict[str, Any]) -> None:
    if not isinstance(freeze.get("answer_root"), str) or not isinstance(
        freeze.get("files"), list
    ):
        raise DrillError("malformed answer-freeze metadata")
    fresh = make_freeze(root, root / freeze["answer_root"])
    if (
        fresh["files"] != freeze["files"]
        or fresh["aggregate_sha256"] != freeze.get("aggregate_sha256")
    ):
        raise DrillError("frozen answer changed after freeze")


def invalidate(run_path: Path, reason: str) -> dict[str, Any]:
    if not reason.strip():
        raise DrillError("invalid_reason must be non-empty")
    root, run = load_run(run_path)
    if run["state"] == "finalized":
        raise DrillError("a finalized run cannot be invalidated")
    run["state"] = "invalidated"
    run["invalid_reason"] = reason.strip()
    run["invalidated_at"] = now_utc()
    save_run(root, run)
    return run


def freeze(run_path: Path, answer_path: Path | None = None) -> dict[str, Any]:
    root, run = load_run(run_path)
    if run["state"] != "prepared":
        raise DrillError(f"freeze requires prepared, found {run['state']}")
    if (root / "grader").exists():
        invalidate(root, "grader material existed before freeze")
        raise DrillError("contamination: grader material existed before freeze")
    run["answer_freeze"] = make_freeze(
        root, answer_path or (root / "student" / "answer.md")
    )
    run["state"] = "frozen"
    save_run(root, run)
    return run


def grade_template(rubric: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "validity": "pending",
        "invalid_reason": None,
        "grader_relation": "pending",
        "artifact_quality": "unproven",
        "process_validity": "unproven",
        "skill_attribution": "unproven",
        "baseline": "untested",
        "isolation": "untested",
        "retention": "untested",
        "transfer": "untested",
        "observations": [],
        "notes": "",
        "drills": [
            {
                "drill_id": item["drill_id"],
                "overall": "pending",
                "criteria": [
                    {"criterion": criterion, "result": "pending", "evidence": ""}
                    for criterion in item["criteria"]
                ],
            }
            for item in rubric["drills"]
        ],
    }


def reveal(run_path: Path) -> dict[str, Any]:
    root, run = load_run(run_path)
    if run["state"] != "frozen":
        raise DrillError(f"reveal requires frozen, found {run['state']}")
    if (root / "grader").exists():
        invalidate(root, "grader material existed before a valid reveal")
        raise DrillError("contamination: grader material already exists")
    try:
        verify_freeze(root, run.get("answer_freeze") or {})
    except DrillError as exc:
        invalidate(root, str(exc))
        raise
    rubric = read_json(root / "controller" / "rubric.json")
    key = (root / "controller" / "key.md").read_text(encoding="utf-8")
    temporary = Path(tempfile.mkdtemp(prefix=".grader.", dir=root))
    try:
        (temporary / "rubric.md").write_text(key, encoding="utf-8", newline="\n")
        (temporary / "grade.json").write_text(
            json.dumps(grade_template(rubric), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        os.replace(temporary, root / "grader")
    except BaseException:
        if temporary.exists():
            shutil.rmtree(temporary)
        raise
    run["state"] = "revealed"
    run["revealed_at"] = now_utc()
    save_run(root, run)
    return run


def validate_grade(grade: dict[str, Any], rubric: dict[str, Any]) -> list[str]:
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
    for key in ("baseline", "isolation", "retention", "transfer"):
        if grade.get(key) not in STAGES:
            errors.append(f"{key} must be one of {sorted(STAGES)}")
    observations = grade.get("observations")
    if not isinstance(observations, list) or any(
        not isinstance(item, str) for item in observations
    ):
        errors.append("observations must be a list of strings")
    elif validity == "valid" and not any(item.strip() for item in observations):
        errors.append("a valid run requires an observation")
    expected = {item["drill_id"]: item for item in rubric.get("drills") or []}
    actual = grade.get("drills")
    if not isinstance(actual, list):
        return errors + ["drills must be a list"]
    ids = [item.get("drill_id") for item in actual if isinstance(item, dict)]
    if len(ids) != len(set(ids)) or set(ids) != set(expected):
        errors.append("grade must contain every prepared Drill exactly once")
    for item in actual:
        if not isinstance(item, dict) or item.get("drill_id") not in expected:
            continue
        drill_id = item["drill_id"]
        allowed_overall = OVERALL_RESULTS if validity == "valid" else (
            OVERALL_RESULTS | {"not_tested"}
        )
        if item.get("overall") not in allowed_overall:
            errors.append(f"{drill_id}: invalid overall result")
        criteria = item.get("criteria")
        if not isinstance(criteria, list):
            errors.append(f"{drill_id}: criteria must be a list")
            continue
        expected_text = expected[drill_id]["criteria"]
        actual_text = [
            criterion.get("criterion") for criterion in criteria
            if isinstance(criterion, dict)
        ]
        if actual_text != expected_text:
            errors.append(f"{drill_id}: criteria differ from the canonical rubric")
            continue
        for index, criterion in enumerate(criteria, start=1):
            if criterion.get("result") not in CRITERION_RESULTS:
                errors.append(f"{drill_id} criterion {index}: invalid result")
            if not str(criterion.get("evidence") or "").strip():
                errors.append(f"{drill_id} criterion {index}: evidence is required")
    return errors


def candidate_event(
    run: dict[str, Any],
    grade: dict[str, Any] | None,
    event_id: str,
    task: str,
    event_date: str,
) -> dict[str, Any]:
    if not event_id.strip() or not task.strip():
        raise DrillError("event_id and task must be non-empty")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", event_date):
        raise DrillError("date must be YYYY-MM-DD")
    drill_ids = [item["drill_id"] for item in run["drills"]]
    if run["state"] == "invalidated":
        return {
            "event_id": event_id.strip(),
            "date": event_date,
            "task": task.strip(),
            "validity": "invalid",
            "invalid_reason": str(run.get("invalid_reason") or "invalidated run"),
            "scope_id": " + ".join(drill_ids),
            "delivery": f"blind-drill-harness:{run['cut']}",
            "notes": "The Drill controller invalidated this sitting before completion.",
        }
    assert grade is not None
    outcomes = ", ".join(
        f"{item['drill_id']}={item['overall']}" for item in grade["drills"]
    )
    notes = (
        f"Blind Drill sitting; grader relation: {grade['grader_relation']}; "
        f"criterion outcomes: {outcomes}."
    )
    if str(grade.get("notes") or "").strip():
        notes += " " + str(grade["notes"]).strip()
    event: dict[str, Any] = {
        "event_id": event_id.strip(),
        "date": event_date,
        "task": task.strip(),
        "validity": grade["validity"],
        "scope_id": " + ".join(drill_ids),
        "delivery": f"blind-drill-harness:{run['cut']}; grader={grade['grader_relation']}",
        "observations": [item.strip() for item in grade["observations"] if item.strip()],
        "baseline": grade["baseline"],
        "isolation": grade["isolation"],
        "retention": grade["retention"],
        "transfer": grade["transfer"],
        "artifact_quality": grade["artifact_quality"],
        "process_validity": grade["process_validity"],
        "skill_attribution": grade["skill_attribution"],
        "notes": notes,
    }
    if grade["validity"] == "invalid":
        event["invalid_reason"] = str(grade["invalid_reason"]).strip()
    return event


def finalize(
    run_path: Path,
    event_id: str,
    task: str,
    event_date: str | None = None,
    grade_path: Path | None = None,
    event_out: Path | None = None,
) -> dict[str, Any]:
    root, run = load_run(run_path)
    if run["state"] not in {"revealed", "invalidated"}:
        raise DrillError(f"finalize requires revealed or invalidated, found {run['state']}")
    grade: dict[str, Any] | None = None
    if run["state"] == "revealed":
        try:
            verify_freeze(root, run.get("answer_freeze") or {})
        except DrillError as exc:
            invalidate(root, str(exc))
            raise
        rubric = read_json(root / "controller" / "rubric.json")
        grade = read_json((grade_path or root / "grader" / "grade.json").resolve())
        errors = validate_grade(grade, rubric)
        if errors:
            raise DrillError("invalid grade: " + "; ".join(errors))
    event = candidate_event(
        run, grade, event_id, task, event_date or date.today().isoformat()
    )
    destination = (event_out or root / "candidate_training_event.json").resolve()
    require_inside(destination, root, "candidate event")
    if destination.exists():
        if read_json(destination) != event:
            raise DrillError(f"refusing to overwrite a different event: {destination}")
    else:
        write_json_atomic(destination, event)
    run["state"] = "finalized"
    run["finalized_at"] = now_utc()
    run["candidate_event"] = destination.relative_to(root).as_posix()
    save_run(root, run)
    return event


def default_library(script: Path) -> Path:
    """Locate library/ in either the authoring repo or a portable release."""
    # Vendored release: <release>/scripts/skillforge_drill.py
    if script.parent.name == "scripts" and (script.parent.parent / "library").is_dir():
        return script.parent.parent / "library"
    # Canonical authoring: <repo>/PASS/runtime/skillforge_drill.py
    return script.resolve().parents[2] / "library"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--library",
        type=Path,
        default=default_library(Path(__file__).resolve()),
    )
    commands = parser.add_subparsers(dest="command", required=True)
    listing = commands.add_parser("list")
    listing.add_argument("--domain")
    listing.add_argument("--format", choices=("summary", "json"), default="summary")
    show = commands.add_parser("show")
    show.add_argument("drill_id")
    prep = commands.add_parser("prepare")
    prep.add_argument("--drill", action="append", required=True)
    prep.add_argument("--cut", choices=sorted(CUTS), required=True)
    prep.add_argument("--scenario", type=Path, required=True)
    prep.add_argument("--out", type=Path, required=True)
    freezing = commands.add_parser("freeze")
    freezing.add_argument("--run", type=Path, required=True)
    freezing.add_argument("--answer", type=Path)
    revealing = commands.add_parser("reveal")
    revealing.add_argument("--run", type=Path, required=True)
    invalidating = commands.add_parser("invalidate")
    invalidating.add_argument("--run", type=Path, required=True)
    invalidating.add_argument("--reason", required=True)
    final = commands.add_parser("finalize")
    final.add_argument("--run", type=Path, required=True)
    final.add_argument("--grade", type=Path)
    final.add_argument("--event-id", required=True)
    final.add_argument("--task", required=True)
    final.add_argument("--date")
    final.add_argument("--event-out", type=Path)
    status = commands.add_parser("status")
    status.add_argument("--run", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "list":
            cards = discover(args.library, args.domain)
            if args.format == "json":
                print(json.dumps([
                    {
                        "object_id": card.object_id,
                        "name": card.name,
                        "target_skill": card.target_skill,
                        "domain": card.domain,
                        "module": card.module,
                        "path": card.relative_path,
                    }
                    for card in cards
                ], indent=2, ensure_ascii=False))
            else:
                label = args.domain or "all domains"
                print(f"{label}: {len(cards)} Drills")
                for card in cards:
                    print(f"  {card.object_id} — {card.name}")
        elif args.command == "show":
            card = select_drills(args.library, [args.drill_id])[0]
            print(card.text, end="" if card.text.endswith("\n") else "\n")
        elif args.command == "prepare":
            run = prepare(args.library, args.drill, args.cut, args.scenario, args.out)
            print(f"PREPARED: {args.out.resolve()}")
            print(f"Drills: {', '.join(item['drill_id'] for item in run['drills'])}")
            print("Expose only student/ to the taker. Automatic repetitions: 0.")
        elif args.command == "freeze":
            run = freeze(args.run, args.answer)
            print(f"FROZEN: {run['answer_freeze']['aggregate_sha256']}")
        elif args.command == "reveal":
            reveal(args.run)
            print(f"REVEALED: {args.run.resolve() / 'grader'}")
        elif args.command == "invalidate":
            run = invalidate(args.run, args.reason)
            print(f"INVALIDATED: {run['invalid_reason']}")
        elif args.command == "finalize":
            event = finalize(
                args.run, args.event_id, args.task, args.date, args.grade, args.event_out
            )
            print(f"FINALIZED: {event['event_id']} ({event['validity']})")
            print("Skillset Memory was not modified.")
        elif args.command == "status":
            root, run = load_run(args.run)
            print(json.dumps({
                "run": str(root),
                "state": run["state"],
                "revision": run["revision"],
                "domain": run["domain"],
                "cut": run["cut"],
                "drills": [item["drill_id"] for item in run["drills"]],
                "answer_frozen": bool(run.get("answer_freeze")),
                "invalid_reason": run.get("invalid_reason"),
                "candidate_event": run.get("candidate_event"),
            }, indent=2, ensure_ascii=False))
        return 0
    except (DrillError, OSError, yaml.YAMLError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
