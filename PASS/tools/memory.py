#!/usr/bin/env python3
"""Skillset Memory tooling: validate, query, append, link-evidence, review,
add, update, retire, show.

Memory is the portable compact current state of a skill: learned principles are
kept distinct from empirical training results. Training history is the event
record for specific attempts and evaluations. This tool is mechanical: it
validates shape, retrieves a bounded set, appends an event, links evidence, and
reports what needs revalidation. It never decides
whether an artifact was good, never mutates a card, and never invents a training
stage that did not run.

The contract it enforces lives in PASS/docs/MEMORY_SCHEMA.md. Two invariants are
worth naming here because they are the reason the tool exists at all:

    an invalid run never counts as evidence about a capability
    a write is not persisted until the target is reopened and confirmed

Like the card validator, this reads the memory tree and nothing else. It never
looks for a source document, a page, or a record of the conversation that
produced an entry.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import copy
import json
import os
import re
import secrets
import sys
import time
import uuid
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import yaml

from paths import default_memory_root, default_library_root


SCHEMA_VERSION = 2
SUPPORTED_SCHEMA_VERSIONS = {1, 2}
# The legacy claim vocabularies (entry types, scopes, evidence classes,
# statuses, origins, the optional face of the entry keys, file-level keys) live
# with `validate_entry` in `memory_legacy_input.py`, the transient migration
# reader T21 deletes. What stays here serves surviving runtime paths: the
# semantic ladder and failure layers are shared with the v3 path, and
# retrievable status feeds `query`/`review` until T07 and T08 reach them.
# `ENTRY_REQUIRED` below is the one exception — since T05 removed the legacy
# write path, its only reader is the legacy module, which imports it from here.
# It stays put rather than moving so that T21 deletes one module, not two edits.
CONFIDENCE_VALUES = {"provisional", "repeated", "strong"}
RETRIEVABLE_STATUS = {"active", "monitoring"}
FAILURE_LAYERS = {
    "knowledge", "orchestration", "retrieval", "application", "continuity",
    "reference", "tool", "interface", "training",
}
STAGE_RESULTS = {"improved", "partial", "unchanged", "failed", "untested"}
SCORE_VALUES = {"strong", "adequate", "weak", "failed", "unproven"}
VALIDITY_VALUES = {"valid", "invalid"}
EVENT_KIND_VALUES = {"performance", "metadata_correction", "evidence_correction"}
RUN_TYPE_VALUES = {
    "portability-probe", "blind-drill-sitting", "deterministic-regression",
    "comparative-study", "software-card-field-test",
}
TRAINING_STAGE_VALUES = {
    "qualification", "baseline", "practice", "isolation", "retention", "transfer",
}
PROGRAM_PURPOSE_VALUES = {"skillset-improvement"}
EVENT_INTERVENTION_COMPONENT_KEYS = {
    "drill_instructions", "card_ids", "external_material",
}

ENTRY_REQUIRED = {
    "id", "scope_type", "scope_id", "type", "evidence_class", "observation",
    "confidence", "status",
}

EVENT_REQUIRED = {"event_id", "date", "task", "validity"}
EVENT_OPTIONAL = {
    "invalid_reason", "scope_id", "delivery", "observations", "baseline",
    "isolation", "retention", "transfer", "artifact_quality", "process_validity",
    "skill_attribution", "notes", "run_type", "training_stage", "taker",
    "intervention", "program_purpose", "lessons", "event_kind",
    "supersedes_events", "corrections",
}
EVENT_KEYS = EVENT_REQUIRED | EVENT_OPTIONAL
STAGE_KEYS = ("baseline", "isolation", "retention", "transfer")
SCORE_KEYS = ("artifact_quality", "process_validity", "skill_attribution")

# Keys from the authoring vocabulary retired 2026-08-15, plus the session-state
# vocabulary the temporary-state firewall excludes. Memory must not grow either
# back under a new namespace.
FORBIDDEN_KEYS = {
    "source_id", "source_title", "page", "pages", "locator", "hash", "sha256",
    "receipt", "attestation", "provenance", "ledger",
    "session_id", "chat_id", "current_stage", "stage", "unit", "next_unit",
    "unit_map", "candidate_id", "branch", "parent_gen_id", "root_id", "parent_id",
    "active_source", "reading_progress",
}

# An entry that defers its content to a conversation is not self-contained, and
# the conversation will not survive into the runtime that needs the lesson.
NON_SELF_CONTAINED_PHRASES = (
    "see the chat", "see the old chat", "see the earlier chat", "see the project chat",
    "see the conversation", "as discussed in the chat", "refer to the chat",
    "in the original conversation", "see the transcript", "per the earlier session",
)

# Authoring actions are not training events. Recording one would manufacture
# evidence that a capability was exercised when only a file changed.
AUTHORING_TASK_PHRASES = (
    "authored a card", "authored a drill", "authored a pattern", "wrote a card",
    "committed", "commit ", "validated the library", "ran the validator",
    "regenerated indexes", "regenerated the index", "built the release",
    "created an archive", "generated an archive", "packaged the release",
    "read unit", "processed unit", "closed the source", "closed the book",
    "currency update of",
)

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ID_RE = re.compile(r"^[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)*$")
STALE_DAYS = 180


class MemoryError_(Exception):
    """Raised when a store cannot be read at all."""


# ------------------------------------------------- claim identity (schema 3)

# The token a claim id carries for its domain. It is a table rather than a
# derivation because no rule produces all four: `art` keeps its whole name,
# `game-design` and `software-engineering` take initials, and `writing`
# truncates. Deriving it by string manipulation would silently invent a token
# for a domain nobody has decided on, so an unmapped domain is an error.
#
# The token exists for readability and cross-domain diagnosis — so an id read in
# a receipt or a `contradicts` link says which skill holds the claim. It is not
# the source of uniqueness; the tail is.
CLAIM_DOMAIN_TOKENS = {
    "art": "ART",
    "game-design": "GD",
    "software-engineering": "SE",
    "writing": "WRI",
}

# Crockford base32: the digits and uppercase letters less I, L, O and U, which
# are excluded because they misread as 1, 1, 0 and V.
CROCKFORD_ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
CLAIM_ID_TAIL_LENGTH = 26
CLAIM_ID_RE = re.compile(
    r"^(?:%s)_MEM_[%s]{%d}$"
    % ("|".join(sorted(set(CLAIM_DOMAIN_TOKENS.values()))),
       CROCKFORD_ALPHABET,
       CLAIM_ID_TAIL_LENGTH)
)


def claim_domain_token(skillset: str) -> str:
    """The id token for a domain, or an error naming the table."""
    token = CLAIM_DOMAIN_TOKENS.get(str(skillset))
    if token is None:
        known = ", ".join(sorted(CLAIM_DOMAIN_TOKENS))
        raise MemoryError_(
            f"no claim id token for domain '{skillset}'; CLAIM_DOMAIN_TOKENS covers {known}. "
            "Add the domain to the table deliberately rather than deriving a token from its name"
        )
    return token


def _crockford(value: int, length: int) -> str:
    return "".join(
        CROCKFORD_ALPHABET[(value >> (5 * position)) & 31]
        for position in range(length - 1, -1, -1)
    )


def new_claim_id(skillset: str) -> str:
    """A fresh claim id, generated from nothing but this process's randomness.

    128 bits rendered as 26 Crockford base32 characters: 48 bits of millisecond
    timestamp followed by 80 bits from `secrets`. That is ULID's shape, and the
    80 random bits are what make two writers who never meet miss each other.

    Nothing here reads persisted state. No counter, no high-water mark, no
    allocation tombstone, no retired-id list, no `memory_version`, no existing
    claim, no version control, no training history, and no model, machine,
    process or session identity. That is the whole point: retirement deletes a
    claim, so an allocator derived from the surviving claims would hand the same
    id out twice.

    The timestamp is a generator detail and carries no meaning a reader may use.
    Nothing sorts, ranks, or infers recency from an id (the retrieval rule in
    MEMORY_SCHEMA.md); callers treat the whole string as opaque.
    """
    token = claim_domain_token(skillset)
    moment = int(time.time() * 1000) & ((1 << 48) - 1)
    value = (moment << 80) | int.from_bytes(secrets.token_bytes(10), "big")
    return f"{token}_MEM_{_crockford(value, CLAIM_ID_TAIL_LENGTH)}"


def claim_id_problems(claim_id: Any, skillset: str) -> list[str]:
    """Why this is not a valid claim id for this store, or nothing.

    Shape only. No check asserts which library produced a token, because that is
    not knowable from a store; practical uniqueness is a property of the
    generator, and the two things a file can actually prove are duplication
    within a store and across the stores a caller supplied.
    """
    if not isinstance(claim_id, str) or not claim_id:
        return ["id must be a non-empty string"]
    if not CLAIM_ID_RE.fullmatch(claim_id):
        return [
            f"id '{claim_id}' is not <DOMAIN_TOKEN>_MEM_<{CLAIM_ID_TAIL_LENGTH} Crockford base32 "
            "characters>; a legacy sequence number is not a claim id"
        ]
    token = claim_domain_token(skillset)
    if not claim_id.startswith(f"{token}_MEM_"):
        return [f"id '{claim_id}' does not carry this store's domain token '{token}'"]
    return []


def duplicate_claim_ids(ids: list[str]) -> list[str]:
    """Ids appearing more than once in the sequence handed in.

    Called with one store's ids to enforce uniqueness within it, and with
    several stores' ids concatenated to enforce it across whatever the caller
    could actually read. A single-store validation stays complete on its own
    terms; this never claims global uniqueness, which no single file can prove.
    """
    seen: set[str] = set()
    repeated: set[str] = set()
    for claim_id in ids:
        if claim_id in seen:
            repeated.add(claim_id)
        seen.add(claim_id)
    return sorted(repeated)



# ---------------------------------------------------------------- loading


def domain_dirs(memory_root: Path, domain: str | None) -> list[Path]:
    if not memory_root.is_dir():
        raise MemoryError_(f"memory root not found: {memory_root.as_posix()}")
    if domain:
        target = memory_root / domain
        if not target.is_dir():
            raise MemoryError_(f"no memory for domain '{domain}' under {memory_root.as_posix()}")
        return [target]
    return sorted(p for p in memory_root.iterdir() if p.is_dir() and (p / "skill_memory.yaml").is_file())


def load_memory(domain_dir: Path) -> dict[str, Any]:
    path = domain_dir / "skill_memory.yaml"
    if not path.is_file():
        raise MemoryError_(f"missing {path.as_posix()}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data is None:
        data = {}
    if not isinstance(data, dict):
        raise MemoryError_(f"{path.as_posix()}: top level must be a mapping")
    return data


def load_events(domain_dir: Path) -> tuple[list[dict[str, Any]], list[str]]:
    """Return (events, errors). A malformed line is an error, not an exception."""
    path = domain_dir / "training_history.jsonl"
    events: list[dict[str, Any]] = []
    errors: list[str] = []
    if not path.is_file():
        return events, [f"{path.as_posix()}: missing"]
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"training_history.jsonl:{number}: invalid JSON: {exc}")
            continue
        if not isinstance(event, dict):
            errors.append(f"training_history.jsonl:{number}: line must be a JSON object")
            continue
        events.append(event)
    return events, errors


# ---------------------------------------------------------------- validation


def validate_event(
    event: dict[str, Any],
    index: int,
    errors: list[str],
    *,
    quarantined: bool = False,
) -> None:
    label = event.get("event_id") if isinstance(event.get("event_id"), str) else f"event[{index}]"

    missing = sorted(EVENT_REQUIRED - set(event))
    if missing:
        errors.append(f"{label}: missing required keys: {', '.join(missing)}")
    forbidden = sorted(set(event) & FORBIDDEN_KEYS)
    if forbidden:
        errors.append(f"{label}: forbidden key(s) from retired or session vocabulary: {', '.join(forbidden)}")
    extra = sorted(set(event) - EVENT_KEYS - FORBIDDEN_KEYS)
    if extra:
        errors.append(f"{label}: unknown key(s): {', '.join(extra)}")

    validity = event.get("validity")
    if validity is not None and validity not in VALIDITY_VALUES:
        errors.append(f"{label}: validity must be valid or invalid")
    if validity == "invalid" and not str(event.get("invalid_reason", "")).strip():
        errors.append(f"{label}: invalid_reason is required when validity is invalid")
    if validity == "valid" and event.get("invalid_reason"):
        errors.append(f"{label}: invalid_reason must be absent when validity is valid")

    event_kind = event.get("event_kind", "performance")
    if event_kind not in EVENT_KIND_VALUES:
        errors.append(f"{label}: event_kind must be one of {sorted(EVENT_KIND_VALUES)}")
    if event_kind in {"metadata_correction", "evidence_correction"}:
        supersedes = event.get("supersedes_events")
        if not isinstance(supersedes, list) or not supersedes or any(
            not isinstance(item, str) or not item.strip() for item in supersedes
        ):
            errors.append(
                f"{label}: {event_kind} requires non-empty supersedes_events"
            )
        corrections = event.get("corrections")
        if not isinstance(corrections, dict) or not corrections:
            errors.append(f"{label}: {event_kind} requires non-empty corrections")
        prohibited = {
            "observations", "baseline", "isolation", "retention", "transfer",
            "artifact_quality", "process_validity", "skill_attribution",
            "run_type", "training_stage", "taker", "intervention",
            "program_purpose", "lessons",
        }
        present = sorted(prohibited & set(event))
        if present:
            errors.append(
                f"{label}: {event_kind} may not claim performance fields: "
                f"{', '.join(present)}"
            )
        if event_kind == "evidence_correction" and isinstance(corrections, dict):
            if corrections.get("disposition") != "quarantined":
                errors.append(
                    f"{label}: evidence_correction corrections.disposition must be quarantined"
                )
            if not str(corrections.get("reason", "")).strip():
                errors.append(
                    f"{label}: evidence_correction corrections.reason must be non-empty"
                )
            replacement = corrections.get("replacement_outcomes")
            if replacement is not None:
                allowed = {"pass", "fail", "invalid", "not-applicable"}
                if not isinstance(replacement, dict) or any(
                    target not in (supersedes or []) or outcome not in allowed
                    for target, outcome in replacement.items()
                ):
                    errors.append(
                        f"{label}: replacement_outcomes must map superseded events to "
                        f"one of {sorted(allowed)}"
                    )
    elif "supersedes_events" in event or "corrections" in event:
        errors.append(
            f"{label}: supersedes_events and corrections require a correction event_kind"
        )

    if "run_type" in event and event["run_type"] not in RUN_TYPE_VALUES:
        errors.append(f"{label}: run_type must be one of {sorted(RUN_TYPE_VALUES)}")
    if "training_stage" in event and event["training_stage"] not in TRAINING_STAGE_VALUES:
        errors.append(
            f"{label}: training_stage must be one of {sorted(TRAINING_STAGE_VALUES)}"
        )
    if "program_purpose" in event and event["program_purpose"] not in PROGRAM_PURPOSE_VALUES:
        errors.append(
            f"{label}: program_purpose must be one of {sorted(PROGRAM_PURPOSE_VALUES)}"
        )
    taker = event.get("taker")
    if taker is not None:
        if not isinstance(taker, dict):
            errors.append(f"{label}: taker must be a mapping")
        else:
            if not str(taker.get("learner_id", "")).strip():
                errors.append(f"{label}: taker.learner_id must be non-empty")
            learner = taker.get("learner")
            if not isinstance(learner, dict) or learner.get("kind") not in {"human", "ai"}:
                errors.append(f"{label}: taker.learner.kind must be human or ai")
            runtime = taker.get("runtime")
            if not isinstance(runtime, dict) or not str(runtime.get("name", "")).strip():
                errors.append(f"{label}: taker.runtime.name must be non-empty")
            if (
                isinstance(learner, dict)
                and learner.get("kind") == "ai"
                and "model" in taker
            ):
                model = taker.get("model")
                if not isinstance(model, dict) or not str(model.get("name", "")).strip():
                    errors.append(f"{label}: optional AI model metadata requires model.name")
            elif isinstance(learner, dict) and learner.get("kind") == "human" and "model" in taker:
                errors.append(f"{label}: a human taker may not contain model metadata")

    lessons = event.get("lessons")
    if lessons is not None:
        if not isinstance(lessons, list):
            errors.append(f"{label}: lessons must be a list")
        else:
            for lesson_index, lesson in enumerate(lessons, start=1):
                lesson_label = f"{label}: lesson {lesson_index}"
                if not isinstance(lesson, dict):
                    errors.append(f"{lesson_label} must be a mapping")
                    continue
                unknown = sorted(
                    set(lesson)
                    - {
                        "drill_id", "criterion_index", "cause", "object_id",
                        "mistake", "correction", "prevention",
                    }
                )
                if unknown:
                    errors.append(
                        f"{lesson_label} has unknown key(s): {', '.join(unknown)}"
                    )
                if not str(lesson.get("drill_id", "")).strip():
                    errors.append(f"{lesson_label}.drill_id must be non-empty")
                if not isinstance(lesson.get("criterion_index"), int) or isinstance(
                    lesson.get("criterion_index"), bool
                ) or lesson["criterion_index"] < 1:
                    errors.append(f"{lesson_label}.criterion_index must be a positive integer")
                if lesson.get("cause") not in {"application", "drill", "skillcard"}:
                    errors.append(
                        f"{lesson_label}.cause must be application, drill, or skillcard"
                    )
                if lesson.get("cause") in {"drill", "skillcard"}:
                    if not str(lesson.get("object_id", "")).strip():
                        errors.append(f"{lesson_label}.object_id must name the attributed card")
                    elif lesson.get("cause") == "drill" and lesson.get("object_id") != lesson.get("drill_id"):
                        errors.append(f"{lesson_label}: Drill cause must name its Drill")
                    elif lesson.get("cause") == "skillcard":
                        intervention_data = event.get("intervention") or {}
                        component_data = intervention_data.get("components") or {}
                        exposed_cards = component_data.get("card_ids") or []
                        if lesson.get("object_id") not in exposed_cards:
                            errors.append(
                                f"{lesson_label}: skillcard cause must name an exposed card"
                            )
                elif lesson.get("object_id") is not None:
                    errors.append(f"{lesson_label}: application lessons may not name a card")
                for key in ("mistake", "correction", "prevention"):
                    if not str(lesson.get(key, "")).strip():
                        errors.append(f"{lesson_label}.{key} must be non-empty")
                profile = taker if isinstance(taker, dict) else {}
                model = profile.get("model") or {}
                taker_labels = [
                    str(profile.get("learner_id", "")),
                    str(model.get("name", "")),
                ]
                lesson_text = " ".join(
                    str(lesson.get(key, ""))
                    for key in ("mistake", "correction", "prevention")
                ).lower()
                if any(
                    len(taker_label.strip()) >= 3
                    and taker_label.lower() in lesson_text
                    for taker_label in taker_labels
                ):
                    errors.append(
                        f"{lesson_label}: lesson must be transferable, not name the taker"
                    )

    intervention = event.get("intervention")
    if intervention is not None:
        if not isinstance(intervention, dict):
            errors.append(f"{label}: intervention must be a mapping")
        else:
            for key in ("intervention_id", "kind", "description"):
                if not str(intervention.get(key, "")).strip():
                    errors.append(f"{label}: intervention.{key} must be non-empty")
            components = intervention.get("components")
            if not isinstance(components, dict):
                errors.append(f"{label}: intervention.components must be a mapping")
            else:
                unknown = sorted(set(components) - EVENT_INTERVENTION_COMPONENT_KEYS)
                if unknown:
                    errors.append(
                        f"{label}: intervention.components has unknown key(s): "
                        + ", ".join(unknown)
                    )
                for key in ("drill_instructions", "external_material"):
                    if not isinstance(components.get(key, False), bool):
                        errors.append(
                            f"{label}: intervention.components.{key} must be true or false"
                        )
                card_ids = components.get("card_ids", [])
                if not isinstance(card_ids, list) or any(
                    not isinstance(item, str) or not item.strip()
                    for item in card_ids
                ):
                    errors.append(
                        f"{label}: intervention.components.card_ids must contain non-empty Pattern/AP IDs"
                    )
                elif len(card_ids) != len(set(card_ids)):
                    errors.append(
                        f"{label}: intervention.components.card_ids may not contain duplicates"
                    )
                if not (
                    components.get("drill_instructions", False)
                    or card_ids
                    or components.get("external_material", False)
                ):
                    errors.append(
                        f"{label}: intervention must declare at least one teaching component"
                    )

    if "date" in event and not DATE_RE.fullmatch(str(event["date"])):
        errors.append(f"{label}: date must be YYYY-MM-DD")

    task = event.get("task")
    if not isinstance(task, str) or not task.strip():
        errors.append(f"{label}: task must be non-empty text")
    elif event_kind == "performance" and not quarantined:
        lowered = task.lower()
        for phrase in AUTHORING_TASK_PHRASES:
            if phrase in lowered:
                errors.append(f"{label}: task describes an authoring action ('{phrase.strip()}'), not an executed capability")
                break

    for key in STAGE_KEYS:
        if key in event and event[key] not in STAGE_RESULTS and not isinstance(event[key], str):
            errors.append(f"{label}: {key} must be text or one of {sorted(STAGE_RESULTS)}")
    for key in ("isolation", "retention", "transfer"):
        if key in event and isinstance(event[key], str) and event[key] not in STAGE_RESULTS:
            errors.append(f"{label}: {key} '{event[key]}' is not in the closed vocabulary")
    for key in SCORE_KEYS:
        if key in event and event[key] not in SCORE_VALUES:
            errors.append(f"{label}: {key} '{event[key]}' is not in the closed vocabulary")

    if "observations" in event and not isinstance(event["observations"], list):
        errors.append(f"{label}: observations must be a list")


def validate_store(domain_dir: Path) -> tuple[list[str], list[str]]:
    """Load one domain's store and validate it, as `(errors, flags)`.

    History loading differs by version: a v1/v2 store (or an unknown version)
    must have its `training_history.jsonl` — absence is the load error
    `load_events` reports, exactly as before — while beside a v3 store absence
    means "no resolution" (I5), so nothing is loaded and nothing is reported
    missing.
    """
    try:
        memory = load_memory(domain_dir)
    except MemoryError_ as exc:
        return [str(exc)], []
    if memory.get("memory_schema_version") == V3_SCHEMA_VERSION:
        if (domain_dir / "training_history.jsonl").is_file():
            events, event_errors = load_events(domain_dir)
        else:
            events, event_errors = None, None
    else:
        events, event_errors = load_events(domain_dir)
    return validate_contents(domain_dir.name, memory, events, event_errors)


def validate_contents(
    domain: str,
    memory: dict[str, Any],
    events: list[dict[str, Any]] | None,
    event_errors: list[str] | None,
) -> tuple[list[str], list[str]]:
    """Validate a store's contents by its declared schema version (T04).

    The claim side dispatches: schema 3 to `validate_v3_contents`, schemas 1
    and 2 to the transient `memory_legacy_input` module, anything else to the
    existing unknown-version error. The Training History path runs for every
    version — History is not versioned (R2.5 §8.4) — and `events is None`
    means the file is absent beside a v3 store (I5): nothing to validate and
    nothing to report. Returns `(errors, flags)`: errors make the store
    invalid (exit 1); flags leave it valid and are printed as reviewable
    (exit 0).
    """
    errors: list[str] = []
    flags: list[str] = []
    schema_version = memory.get("memory_schema_version")
    if schema_version == V3_SCHEMA_VERSION:
        claim_errors, claim_flags = validate_v3_contents(
            domain, memory, events=events, event_errors=None,
        )
        errors.extend(claim_errors)
        flags.extend(claim_flags)
    elif schema_version in SUPPORTED_SCHEMA_VERSIONS:
        import memory_legacy_input  # transient dispatch dependency; deleted by T21
        errors.extend(
            memory_legacy_input.validate_legacy_contents(domain, memory, events or [])
        )
    else:
        errors.append(
            f"skill_memory.yaml: memory_schema_version must be one of {sorted(SUPPORTED_SCHEMA_VERSIONS)}"
        )

    if events is None:
        return errors, flags
    if event_errors:
        errors.extend(event_errors)
    quarantined = quarantined_event_ids(events)
    for index, event in enumerate(events):
        validate_event(
            event,
            index,
            errors,
            quarantined=str(event.get("event_id")) in quarantined,
        )

    event_ids = [e["event_id"] for e in events if isinstance(e.get("event_id"), str)]
    for duplicate in sorted({i for i in event_ids if event_ids.count(i) > 1}):
        errors.append(f"training_history.jsonl: duplicate event_id '{duplicate}'")

    by_event_id = {e["event_id"]: e for e in events if isinstance(e.get("event_id"), str)}
    event_positions = {
        e["event_id"]: index
        for index, e in enumerate(events)
        if isinstance(e.get("event_id"), str)
    }
    for event in events:
        if event.get("event_kind") not in {"metadata_correction", "evidence_correction"}:
            continue
        label = event.get("event_id", "event")
        for target in event.get("supersedes_events") or []:
            if target not in by_event_id:
                errors.append(f"{label}: supersedes unknown event '{target}'")
            elif event_positions[target] >= event_positions.get(label, -1):
                errors.append(f"{label}: correction target '{target}' must appear earlier")
    return errors, flags


# ------------------------------------------------- claim schema (version 3)
#
# Structural validation for a `memory_schema_version: 3` store, beside the
# legacy validator and sharing none of its vocabulary constants. The split is
# deliberate: FORBIDDEN_KEYS rejects `provenance` on v1/v2 entries and History
# events, while every v3 claim requires it (R2.5 §4.5 L1, SR1), so the two
# rejection lists can never be merged. Since T04, `validate_contents` dispatches
# here for schema 3 — schemas 1 and 2 route to the transient
# `memory_legacy_input` reader that T21 deletes — and this validator is also
# reachable from tests and from an explicit internal call.

V3_SCHEMA_VERSION = 3
CLAIM_CLASSES = {"conduct", "reach"}
CLAIM_KINDS = {"deterministic", "stochastic"}
# CONFIDENCE_VALUES is shared with the legacy path: one semantic ladder.
DELTA_KINDS = {"action", "judgment", "verification", "posture", "application_limit"}
PROVENANCE_VALUES = {
    "human_teaching", "user_feedback", "runtime_self_audit",
    "training_benchmark", "source_study", "regression_failure",
}
CLAIM_REQUIRED = {
    "id", "claim", "claim_class", "claim_kind", "confidence", "delta", "envelope",
    "provenance", "scope", "retrieval_cues", "last_verified",
}
CLAIM_OPTIONAL = {"canon", "evidence", "revalidate_after", "contradicts"}
CLAIM_KEYS = CLAIM_REQUIRED | CLAIM_OPTIONAL

# R2.5 §4.5 L1: the retired authoring vocabulary plus the migration-lineage
# keys, named so the refusal is legible at the moment an implementer is tempted
# to keep traceability inside a claim. Unlike FORBIDDEN_KEYS this list
# deliberately excludes `provenance`, which every v3 claim requires.
CLAIM_FORBIDDEN_KEYS = {
    "source_id", "locator", "page", "hash", "receipt", "attestation", "ledger",
    "session_id", "current_stage", "unit", "next_unit", "parent_gen_id",
    "legacy_id", "migrated_from", "source_entry", "previous_id",
}
V3_FILE_REQUIRED = {"memory_schema_version", "skillset", "memory_version", "claims"}
CLAIM_KEY_ORDER = (
    "id", "claim", "claim_class", "claim_kind", "confidence", "delta", "envelope",
    "provenance", "scope", "retrieval_cues", "last_verified", "canon", "evidence",
    "revalidate_after", "contradicts",
)

# The literal signature of in-place accretion in the live corpus; no single
# legitimate claim uses them, which is why C6 is an ERROR rather than a FLAG.
ACCRETION_CONNECTIVES = (
    "further showed", "also showed", "then showed", "additionally demonstrated",
)

# A `not_shown_in` member that names no region asserts universality, which is
# the overreach the envelope exists to prevent (R2.5 §4.3 E2).
ENVELOPE_SENTINELS = {"n/a", "none", "unknown", "everywhere", "no limits"}

# R2.5 §4.5 L3/L4: model-neutral, learner-neutral prose. A claim that needs to
# name a model or a graded specimen is not yet a skill-level claim.
MODEL_IDENTITY_TOKENS = (
    "claude", "opus", "sonnet", "haiku", "fable", "gpt", "gemini", "qwen",
    "mimo", "longcat", "codex", "llama", "mistral",
)
MODEL_IDENTITY_RE = re.compile(
    r"(?<![a-z0-9])(?:%s)(?![a-z0-9])"
    % "|".join(sorted(MODEL_IDENTITY_TOKENS, key=len, reverse=True))
)
LEARNER_IDENTITY_TOKENS = (
    "the learner", "the taker", "the evaluator", "the user preferred",
)
# A bare specimen grade: signed forms anywhere, unsigned only behind a grading
# verb, so the article at the start of a sentence is not mistaken for one.
GRADE_RE = re.compile(
    r"\b(?:grade[ds]?|earned|scored|rated|received)\s+[ABC][+-]?\b|\b[ABC][+-](?![A-Za-z0-9])"
)

# L2 carries the legacy self-containment phrases plus the three the v3 rule
# names that the legacy list does not.
CONVERSATION_DEFERENCE_PHRASES = NON_SELF_CONTAINED_PHRASES + (
    "as discussed", "in the session above", "earlier in this conversation",
)

# L5: the structural leak (`runtime_scope`) is gone by construction, so what
# remains is prose naming the machine, host, or container it ran on. FLAG,
# never ERROR — a smell a reviewer must look at, not a decidable rule.
LOCAL_STATE_PHRASES = (
    "this machine", "this host", "this laptop", "this workstation",
    "on my machine", "on my laptop", "this server", "this container",
)

# Closed limits from R2.5 §4.2, verified against live data in the A-1 study and
# closed there; a cap reopens only on contradictory evidence from a real
# migration, never on a repeat of that study.
CLAIM_WORD_CAP = 75
DELTA_WORD_CAP = 50
ENVELOPE_WORD_CAP = 40
FUSION_FLAG_WORDS = 50
SCOPE_SLUG_RE = re.compile(r"^[a-z][a-z0-9_]*$")
DELTA_KEYS = {"kinds", "statement"}
ENVELOPE_KEYS = {"holds_in", "not_shown_in", "conditions"}
REACH_DELTA_KINDS = {"posture", "verification"}


def _claim_prose(claim: dict[str, Any]) -> str:
    """The claim and envelope prose the L-rules read (R2.5 §4.5)."""
    parts: list[str] = []
    if isinstance(claim.get("claim"), str):
        parts.append(claim["claim"])
    envelope = claim.get("envelope")
    if isinstance(envelope, dict):
        for key in ("holds_in", "not_shown_in", "conditions"):
            items = envelope.get(key)
            if isinstance(items, list):
                parts.extend(item for item in items if isinstance(item, str))
    return " ".join(parts)


def validate_claim(
    claim: Any,
    index: int,
    errors: list[str],
    flags: list[str],
    skillset: str,
) -> None:
    """One v3 claim against the closed schema (R2.5 §4.1–§4.5).

    Implements S2–S5, S8–S10, C1–C6, E1–E2, R1 and L1–L5. Errors make the
    store invalid; flags leave it valid and mark it for review — T08's `review`
    is what surfaces them. The referential rules I1–I6 are deliberately not
    here: they need the store's History, its Library, and its sibling claims,
    so they run once per store in `validate_v3_references`.
    """
    where = f"claim[{index}]"
    if not isinstance(claim, dict):
        errors.append(f"{where}: must be a mapping")
        return
    label = claim.get("id") if isinstance(claim.get("id"), str) else where

    missing = sorted(CLAIM_REQUIRED - set(claim))
    if missing:
        errors.append(f"{label}: missing required keys: {', '.join(missing)} (S3)")
    forbidden = sorted(set(claim) & CLAIM_FORBIDDEN_KEYS)
    if forbidden:
        errors.append(
            f"{label}: forbidden key(s) from retired authoring or migration lineage "
            f"vocabulary: {', '.join(forbidden)} (L1)"
        )
    extra = sorted(set(claim) - CLAIM_KEYS - CLAIM_FORBIDDEN_KEYS)
    if extra:
        errors.append(f"{label}: unknown key(s): {', '.join(extra)} (S2)")

    if skillset in CLAIM_DOMAIN_TOKENS:
        for problem in claim_id_problems(claim.get("id"), skillset):
            errors.append(f"{label}: {problem} (S5)")
    # An unmapped skillset is already a file-level error naming the table; with
    # no token there is no id shape to check, and calling claim_id_problems
    # would raise instead of collecting.

    for key, allowed in (
        ("claim_class", CLAIM_CLASSES),
        ("claim_kind", CLAIM_KINDS),
        ("confidence", CONFIDENCE_VALUES),
    ):
        if key in claim and claim[key] not in allowed:
            errors.append(f"{label}: {key} '{claim[key]}' is not in the closed vocabulary (S4)")

    text = claim.get("claim")
    if not isinstance(text, str) or not text.strip():
        errors.append(f"{label}: claim must be non-empty text (S3)")
        text = ""
    words = len(text.split())
    if words > CLAIM_WORD_CAP:
        errors.append(f"{label}: claim is {words} words; the cap is {CLAIM_WORD_CAP} (C1)")
    elif words >= FUSION_FLAG_WORDS:
        flags.append(f"{label}: claim is {words} words; at the fusion threshold (C2)")
    lowered = text.lower()
    for connective in ACCRETION_CONNECTIVES:
        if connective in lowered:
            errors.append(f"{label}: claim contains the accretion connective '{connective}' (C6)")
            break

    if "delta" in claim:
        delta = claim.get("delta")
        if not isinstance(delta, dict):
            errors.append(f"{label}: delta must be a mapping (S3)")
        else:
            unknown = sorted(set(delta) - DELTA_KEYS)
            if unknown:
                errors.append(f"{label}: delta has unknown key(s): {', '.join(unknown)} (S2)")
            kinds = delta.get("kinds")
            if not isinstance(kinds, list) or not kinds:
                errors.append(f"{label}: delta.kinds must be a non-empty list (S9)")
            else:
                for kind in kinds:
                    if kind not in DELTA_KINDS:
                        errors.append(
                            f"{label}: delta.kinds '{kind}' is not in the closed vocabulary (S4)"
                        )
                if len(kinds) > 3:
                    errors.append(
                        f"{label}: delta.kinds has {len(kinds)} members; the cap is 3 (S9)"
                    )
                elif len(kinds) == 3:
                    flags.append(f"{label}: delta.kinds carries 3 members; fusion smell (C5)")
                if claim.get("claim_class") == "reach":
                    disallowed = [kind for kind in kinds if kind not in REACH_DELTA_KINDS]
                    if disallowed:
                        errors.append(
                            f"{label}: claim_class reach allows delta.kinds only from "
                            f"posture, verification (R1); found {', '.join(map(str, disallowed))}"
                        )
            statement = delta.get("statement")
            if not isinstance(statement, str) or not statement.strip():
                errors.append(f"{label}: delta.statement must be non-empty text (S3)")
            elif len(statement.split()) > DELTA_WORD_CAP:
                errors.append(
                    f"{label}: delta.statement is {len(statement.split())} words; "
                    f"the cap is {DELTA_WORD_CAP} (C4)"
                )

    if "envelope" in claim:
        envelope = claim.get("envelope")
        if not isinstance(envelope, dict):
            errors.append(f"{label}: envelope must be a mapping (S3)")
        else:
            unknown = sorted(set(envelope) - ENVELOPE_KEYS)
            if unknown:
                errors.append(f"{label}: envelope has unknown key(s): {', '.join(unknown)} (S2)")
            for key in ("holds_in", "not_shown_in"):
                items = envelope.get(key)
                if not isinstance(items, list) or not items:
                    errors.append(f"{label}: envelope.{key} must be a non-empty list (E1)")
            conditions = envelope.get("conditions")
            if conditions is not None and not isinstance(conditions, list):
                errors.append(f"{label}: envelope.conditions must be a list (S2)")
            for key in ("holds_in", "not_shown_in", "conditions"):
                items = envelope.get(key)
                if not isinstance(items, list):
                    continue
                for item in items:
                    if not isinstance(item, str) or not item.strip():
                        errors.append(f"{label}: envelope.{key} items must be non-empty text (E1)")
                        continue
                    count = len(item.split())
                    if count > ENVELOPE_WORD_CAP:
                        errors.append(
                            f"{label}: envelope.{key} item is {count} words; "
                            f"the cap is {ENVELOPE_WORD_CAP} (C3)"
                        )
                    if key == "not_shown_in" and item.strip().lower() in ENVELOPE_SENTINELS:
                        errors.append(
                            f"{label}: envelope.not_shown_in member '{item}' is a "
                            f"sentinel evasion (E2)"
                        )

    if "provenance" in claim:
        provenance = claim.get("provenance")
        if not isinstance(provenance, list) or not provenance:
            errors.append(f"{label}: provenance must be a non-empty list (S3)")
        else:
            for origin in provenance:
                if origin not in PROVENANCE_VALUES:
                    errors.append(
                        f"{label}: provenance '{origin}' is not in the closed vocabulary (S4)"
                    )

    if "scope" in claim:
        scope = claim.get("scope")
        if not isinstance(scope, str) or not SCOPE_SLUG_RE.fullmatch(scope):
            errors.append(f"{label}: scope must match [a-z][a-z0-9_]* (S10)")

    if "retrieval_cues" in claim:
        cues = claim.get("retrieval_cues")
        if (
            not isinstance(cues, list)
            or not cues
            or any(not isinstance(cue, str) or not cue.strip() for cue in cues)
        ):
            errors.append(
                f"{label}: retrieval_cues must be a non-empty list of non-empty strings (S3)"
            )

    verified = claim.get("last_verified")
    if "last_verified" in claim and not (
        isinstance(verified, (str, date)) and DATE_RE.fullmatch(str(verified))
    ):
        errors.append(f"{label}: last_verified must be YYYY-MM-DD (S8)")
    revalidate = claim.get("revalidate_after")
    if revalidate is not None:
        if not (isinstance(revalidate, (str, date)) and DATE_RE.fullmatch(str(revalidate))):
            errors.append(f"{label}: revalidate_after must be YYYY-MM-DD (S8)")
        elif DATE_RE.fullmatch(str(verified or "")) and str(revalidate) < str(verified):
            errors.append(
                f"{label}: revalidate_after {revalidate} is earlier than "
                f"last_verified {verified} (S8)"
            )

    canon = claim.get("canon")
    if canon is not None:
        if not isinstance(canon, list) or not canon:
            errors.append(f"{label}: canon must be a non-empty list when present (S9)")
        elif len(canon) > 5:
            errors.append(f"{label}: canon has {len(canon)} members; the cap is 5 (S9)")
    evidence = claim.get("evidence")
    if evidence is not None:
        if not isinstance(evidence, list) or not evidence:
            errors.append(f"{label}: evidence must be a non-empty list when present (S9)")
        elif len(evidence) > 3:
            errors.append(f"{label}: evidence has {len(evidence)} members; the cap is 3 (S9)")
    contradicts = claim.get("contradicts")
    if contradicts is not None and (not isinstance(contradicts, list) or not contradicts):
        errors.append(f"{label}: contradicts must be a non-empty list when present (S9)")

    prose = _claim_prose(claim)
    lowered_prose = prose.lower()
    for phrase in CONVERSATION_DEFERENCE_PHRASES:
        if phrase in lowered_prose:
            errors.append(
                f"{label}: prose defers to a conversation ('{phrase}'); it must stand alone (L2)"
            )
            break
    model = MODEL_IDENTITY_RE.search(lowered_prose)
    if model:
        errors.append(
            f"{label}: prose names a model or agent ('{model.group(0)}'); "
            "a skill-level claim is model-neutral (L3)"
        )
    for phrase in LEARNER_IDENTITY_TOKENS:
        if phrase in lowered_prose:
            errors.append(
                f"{label}: prose names a learner or evaluator ('{phrase}'); "
                "it must be transferable (L4)"
            )
            break
    grade = GRADE_RE.search(prose)
    if grade:
        errors.append(
            f"{label}: prose carries a bare specimen grade ('{grade.group(0)}'); "
            "specimen grading is not skill-level knowledge (L4)"
        )
    for phrase in LOCAL_STATE_PHRASES:
        if phrase in lowered_prose:
            flags.append(
                f"{label}: prose names local machine or host state ('{phrase}'); "
                "portability smell (L5)"
            )
            break


# ---------------------------------------------- referential integrity (version 3)
#
# R2.5 §4.6 I1–I6. Shape is checked always; resolution happens only against
# files that actually exist beside the store — a Library root for I2, a
# `training_history.jsonl` for I4 — because a v3 store must validate standing
# alone with neither present (I5, §9.1.1). Memory validity never depends on
# library state: an unresolvable canon reference is a FLAG, never an ERROR.

# I1: a canon member is a card object id or a bare package variant id. The
# variant form is the plain lowercase snake token variant ids are written in
# (for example `writing_fiction_variant_anchor_absurdity_in_legible_operating_logic`),
# not a `(PAT|AP|DRILL)_` prefix — a variant is not a card.
CANON_CARD_RE = re.compile(r"^(?:AP|PAT|DRILL)_[a-z0-9_]+$")
CANON_VARIANT_RE = re.compile(r"^[a-z][a-z0-9_]*$")

# I3: the evidence-id family is derived from the store's own History (SR2:
# live prefixes are `ART_EV_`, `GAMEDESIGN_EV_`, `SE_EV_`, `WRITING_EV_`, none
# of which come from CLAIM_DOMAIN_TOKENS, and no event id is ever renumbered to
# match a token). The fallback family applies when there is no History to
# derive from — absent or empty — and is the only shape check I5 lets run.
EVENT_ID_FALLBACK_RE = re.compile(r"^[A-Z][A-Z0-9]*_EV_[0-9]+$")
EVENT_ID_PREFIX_RE = re.compile(r"([A-Z][A-Z0-9]*_EV_)[0-9]+")


def event_id_prefixes(events: list[dict[str, Any]]) -> set[str]:
    """The event-id families this store's History actually uses (I3, SR2)."""
    prefixes: set[str] = set()
    for event in events:
        event_id = event.get("event_id")
        if not isinstance(event_id, str):
            continue
        match = EVENT_ID_PREFIX_RE.fullmatch(event_id)
        if match:
            prefixes.add(match.group(1))
    return prefixes


def canon_member_well_formed(member: Any) -> bool:
    """I1: a card object id, or a bare package variant id."""
    return isinstance(member, str) and (
        CANON_CARD_RE.fullmatch(member) is not None
        or CANON_VARIANT_RE.fullmatch(member) is not None
    )


def evidence_id_well_formed(member: Any, prefixes: set[str]) -> bool:
    """I3: the id belongs to this store's event-id family.

    With prefixes derived from History the id must be one of them; with none
    derived (History absent, or an id-less History) the generic family is the
    shape. Shape only — existence and admissibility are I4's, and only when
    History is present at all.
    """
    if not isinstance(member, str):
        return False
    if not prefixes:
        return EVENT_ID_FALLBACK_RE.fullmatch(member) is not None
    return any(
        member.startswith(prefix) and member[len(prefix):].isdigit()
        for prefix in prefixes
    )


def quarantined_event_ids(events: list[dict[str, Any]]) -> set[str]:
    """Events a superseding evidence correction removed from capability evidence.

    The single derivation, called from both claim sides since T04: the legacy
    `evidence_events` reader in `memory_legacy_input` and this tool's own
    `validate_event`/v3 paths, so the two cannot drift apart.
    """
    return {
        str(target)
        for event in events
        if event.get("event_kind") == "evidence_correction"
        and (event.get("corrections") or {}).get("disposition") == "quarantined"
        for target in (event.get("supersedes_events") or [])
    }


def evidence_admissibility_problem(
    label: str,
    field: str,
    event_id: str,
    event: dict[str, Any] | None,
    quarantined: set[str],
) -> str | None:
    """Why this event may not be cited as capability evidence, or None.

    One implementation for both claim sides (T04): the legacy path passes field
    `evidence_events`, the v3 path passes `evidence`, and each caller tags the
    message its way — "(I4)" belongs to the v3 rule ids, the legacy messages
    stay exactly as they read before the extraction. `event is None` is an
    unknown citation: nothing validates a run that is not there. The checks run
    in the order the legacy block stated them — invalid run (the invariant this
    whole tool exists to hold), both correction kinds, quarantine — then the
    performance-kind requirement of R2.5 §3.5, which only the v3 path used to
    state.
    """
    if event is None:
        return f"{label}: {field} cites unknown event '{event_id}'"
    if event.get("validity") == "invalid":
        return (
            f"{label}: {field} cites invalid event '{event_id}' "
            f"({event.get('invalid_reason', 'no reason recorded')}); "
            "an invalid run is never evidence about a capability"
        )
    kind = event.get("event_kind", "performance")
    if kind == "metadata_correction":
        return (
            f"{label}: {field} cites metadata correction '{event_id}'; "
            "a correction is not capability evidence"
        )
    if kind == "evidence_correction":
        return (
            f"{label}: {field} cites evidence correction '{event_id}'; "
            "a correction is not capability evidence"
        )
    if event_id in quarantined:
        return (
            f"{label}: {field} cites quarantined event '{event_id}'; "
            "a superseding evidence correction removed it from capability evidence"
        )
    if kind != "performance":
        return (
            f"{label}: {field} cites '{event_id}' of kind '{kind}'; "
            "only a performance event is capability evidence"
        )
    return None


def library_reference_ids(package_root: Path) -> set[str]:
    """Ids a `canon` member may resolve to inside one package (I2).

    Every card `object_id` — the scan `review_store` already uses — plus the
    variant ids I1 admits: variant ids live under a card's `variants:` list in
    front matter, so the object scan alone would flag every variant reference
    that actually exists. Package ownership itself is unchanged: the package
    is the directory under `library/`.
    """
    ids = library_object_ids(package_root)
    if not package_root.is_dir():
        return ids
    for path in package_root.rglob("*.md"):
        if path.name in {"README.md", "INDEX.md"}:
            continue
        ids.update(
            match.group(1)
            for match in re.finditer(
                r"(?m)^\s*-?\s*variant_id:\s*(\S+)\s*$", path.read_text(encoding="utf-8")
            )
        )
    return ids


def validate_v3_references(
    claims: list[Any],
    *,
    events: list[dict[str, Any]] | None,
    library_ids: set[str] | None,
) -> tuple[list[str], list[str]]:
    """I1–I6 over one store's claims (R2.5 §4.6), as `(errors, flags)`.

    `events=None` means `training_history.jsonl` is absent: evidence members
    are shape-checked against the fallback family and never resolved — an
    unresolvable evidence target is not invalid (I5). `library_ids=None`
    means no Library root exists: canon members are shape-checked only, and
    no flag is raised either (I2 has nothing to resolve against).
    Contradictions resolve against this store alone (I6); they need no file
    outside it, and co-return is a later ticket's retrieval behavior, not
    something checked here beyond symmetry.
    """
    errors: list[str] = []
    flags: list[str] = []

    # Each claim id mapped to the contradictions it names, so symmetry can be
    # checked from either side of a pair in one pass over the store.
    known_claims: dict[str, set[str]] = {}
    for claim in claims:
        if not isinstance(claim, dict) or not isinstance(claim.get("id"), str):
            continue
        named = known_claims.setdefault(claim["id"], set())
        if isinstance(claim.get("contradicts"), list):
            named.update(
                str(target) for target in claim["contradicts"] if isinstance(target, str)
            )

    history_present = events is not None
    events = events or []
    prefixes = event_id_prefixes(events)
    quarantined = quarantined_event_ids(events) if history_present else set()
    by_event_id = {
        str(event.get("event_id")): event
        for event in events
        if isinstance(event.get("event_id"), str)
    }

    for index, claim in enumerate(claims):
        if not isinstance(claim, dict):
            continue
        label = claim.get("id") if isinstance(claim.get("id"), str) else f"claim[{index}]"

        canon = claim.get("canon")
        if isinstance(canon, list):
            for member in canon:
                if not canon_member_well_formed(member):
                    errors.append(
                        f"{label}: canon member '{member}' is neither an object id "
                        "nor a package variant id (I1)"
                    )
                elif library_ids is not None and member not in library_ids:
                    flags.append(
                        f"{label}: canon member '{member}' does not resolve in this "
                        "package or metaskills (I2)"
                    )

        evidence = claim.get("evidence")
        if isinstance(evidence, list):
            for member in evidence:
                if not evidence_id_well_formed(member, prefixes):
                    errors.append(
                        f"{label}: evidence member '{member}' does not match this "
                        "store's event-id family (I3)"
                    )
                    continue
                if not history_present:
                    continue  # I5: absent History means no resolution, not invalidity
                problem = evidence_admissibility_problem(
                    label, "evidence", str(member), by_event_id.get(str(member)), quarantined,
                )
                if problem:
                    errors.append(f"{problem} (I4)")

        contradicts = claim.get("contradicts")
        if isinstance(contradicts, list):
            own_id = claim.get("id") if isinstance(claim.get("id"), str) else None
            for target in contradicts:
                if not isinstance(target, str) or target not in known_claims:
                    errors.append(
                        f"{label}: contradicts target '{target}' does not resolve to a "
                        "claim in this store (I6)"
                    )
                elif target == own_id:
                    errors.append(f"{label}: contradicts itself (I6)")
                elif own_id is not None and own_id not in known_claims.get(target, ()):
                    errors.append(
                        f"{label}: contradiction with '{target}' is one-sided; "
                        f"'{target}' must also name '{label}' (I6)"
                    )

    return errors, flags


def validate_v3_contents(
    domain: str,
    memory: dict[str, Any],
    *,
    events: list[dict[str, Any]] | None = None,
    event_errors: list[str] | None = None,
    library_root: Path | None = None,
) -> tuple[list[str], list[str]]:
    """A schema-3 store's structural contract (R2.5 §2, §4.1 S1–S3, S5a, S6,
    S7) plus its referential integrity (§4.6 I1–I6).

    Returns `(errors, flags)`. Errors make the store invalid; flags leave it
    valid and mark it for review. `events=None` means History is absent, so
    evidence is shape-checked but never resolved (I5); `event_errors` carries
    the parse failures of a History file that is present. `library_root=None`,
    or a root that does not exist, skips canon resolution (I2), and the only
    thing a present root can produce is a flag — Memory validity never depends
    on library state. Nothing here writes.
    """
    errors: list[str] = []
    flags: list[str] = []
    if not isinstance(memory, dict):
        return ["skill_memory.yaml: top level must be a mapping"], flags

    missing = sorted(V3_FILE_REQUIRED - set(memory))
    if missing:
        errors.append(f"skill_memory.yaml: missing file-level keys: {', '.join(missing)} (S3)")
    extra = sorted(set(memory) - V3_FILE_REQUIRED)
    if extra:
        errors.append(f"skill_memory.yaml: unknown key(s): {', '.join(extra)} (S2)")
    if memory.get("memory_schema_version") != V3_SCHEMA_VERSION:
        errors.append("skill_memory.yaml: memory_schema_version must be exactly 3 (S1)")
    skillset = memory.get("skillset")
    if skillset != domain:
        errors.append(
            f"skill_memory.yaml: skillset '{skillset}' does not match directory '{domain}' (S6)"
        )
    memory_version = memory.get("memory_version")
    if not isinstance(memory_version, int) or isinstance(memory_version, bool) or memory_version < 1:
        errors.append("skill_memory.yaml: memory_version must be a positive integer (S7)")
    # The token table is checked before any claim id, so an unmapped domain
    # becomes a collected error here rather than an exception raised from
    # inside claim_id_problems while iterating the claims.
    if skillset is not None and skillset not in CLAIM_DOMAIN_TOKENS:
        known = ", ".join(sorted(CLAIM_DOMAIN_TOKENS))
        errors.append(
            f"skill_memory.yaml: no claim id token for domain '{skillset}'; "
            f"CLAIM_DOMAIN_TOKENS covers {known} (S5)"
        )

    claims = memory.get("claims")
    if claims is None:
        claims = []
    if not isinstance(claims, list):
        errors.append("skill_memory.yaml: claims must be a list")
        claims = []
    for index, claim in enumerate(claims):
        validate_claim(
            claim, index, errors, flags, skillset if isinstance(skillset, str) else "",
        )
    ids = [
        claim["id"] for claim in claims
        if isinstance(claim, dict) and isinstance(claim.get("id"), str)
    ]
    for duplicate in duplicate_claim_ids(ids):
        errors.append(f"skill_memory.yaml: duplicate claim id '{duplicate}' (S5a)")

    if event_errors:
        errors.extend(event_errors)
    library_ids = None
    if library_root is not None and library_root.is_dir():
        library_ids = library_reference_ids(library_root / domain) | library_reference_ids(
            library_root / "metaskills"
        )
    ref_errors, ref_flags = validate_v3_references(
        claims, events=events, library_ids=library_ids
    )
    errors.extend(ref_errors)
    flags.extend(ref_flags)
    return errors, flags


def validate_v3_store(
    domain_dir: Path, *, library_root: Path | None = None
) -> tuple[list[str], list[str]]:
    """Load one domain's v3 store and validate it, resolving references against
    the History and Library that actually sit beside it. Either may be absent:
    that changes what is checked, never whether the store is valid — no
    `training_history.jsonl` means no evidence resolution (I5), no Library root
    means no canon resolution and no flags (I2).

    S5b across several stores is the caller's job: gather each store's claim
    ids and hand them to `duplicate_claim_ids`, which is the same check over
    whatever the caller could actually read."""
    try:
        memory = load_memory(domain_dir)
    except MemoryError_ as exc:
        return [str(exc)], []
    events: list[dict[str, Any]] | None = None
    event_errors: list[str] | None = None
    if (domain_dir / "training_history.jsonl").is_file():
        events, event_errors = load_events(domain_dir)
    return validate_v3_contents(
        domain_dir.name,
        memory,
        events=events,
        event_errors=event_errors,
        library_root=library_root,
    )


# ---------------------------------------------------------------- query


def score_entry(entry: dict[str, Any], scope_id: str | None, cues: list[str]) -> tuple[bool, int]:
    """Return (matched, score).

    `matched` is what bounds retrieval. Specificity and confidence only rank
    entries that already matched the request; without that separation a broad
    tendency would score points on every task and the bounded set would quietly
    become the whole file.
    """
    matched = False
    score = 0
    if scope_id and entry.get("scope_id") == scope_id:
        matched = True
        score += 100
    entry_cues = [str(c).lower() for c in entry.get("retrieval_cues", []) if isinstance(c, str)]
    haystack = " ".join(entry_cues + [str(entry.get("scope_id", "")).lower()])
    for cue in cues:
        if cue and cue.lower() in haystack:
            matched = True
            score += 10
    # More specific scope outranks broader tendency when both matched.
    score += {"ap": 5, "pattern": 5, "drill": 5, "training": 5, "topic": 3, "runtime": 2, "skillset": 1}.get(
        str(entry.get("scope_type")), 0
    )
    score += {"strong": 3, "repeated": 2, "provisional": 1}.get(str(entry.get("confidence")), 0)
    if entry.get("status") == "active":
        score += 1
    return matched, score


def query_store(domain_dir: Path, scope_id: str | None, cues: list[str], limit: int) -> list[dict[str, Any]]:
    memory = load_memory(domain_dir)
    entries = [e for e in memory.get("entries") or [] if isinstance(e, dict)]
    # Resolved history stays in the file and stops biasing the runtime.
    candidates = [e for e in entries if e.get("status") in RETRIEVABLE_STATUS]
    if scope_id or cues:
        scored = [(score_entry(e, scope_id, cues), e) for e in candidates]
        hits = [(score, entry) for (matched, score), entry in scored if matched]
        hits.sort(key=lambda pair: (-pair[0], str(pair[1].get("id"))))
        candidates = [entry for _, entry in hits]
    else:
        candidates.sort(key=lambda e: str(e.get("id")))
    return candidates[:limit]


# ---------------------------------------------------------------- append


def next_event_id(events: list[dict[str, Any]], domain: str) -> str:
    # The prefix belongs to the store, not to how the caller spelled the domain.
    # Deriving it from the argument lets "se" and "software-engineering" open two
    # id series in one file, and the second one restarts at 0001 because the scan
    # below only sees ids carrying its own prefix.
    prefix = f"{domain[:3].upper()}_EV_"
    for event in events:
        match = re.match(r"([A-Z]+_EV_)\d+$", str(event.get("event_id", "")))
        if match:
            prefix = match.group(1)
            break
    highest = 0
    for event in events:
        event_id = str(event.get("event_id", ""))
        if event_id.startswith(prefix):
            tail = event_id[len(prefix):]
            if tail.isdigit():
                highest = max(highest, int(tail))
    return f"{prefix}{highest + 1:04d}"


def append_event(domain_dir: Path, event: dict[str, Any]) -> tuple[bool, list[str]]:
    with store_lock(domain_dir):
        return _append_event(domain_dir, event)


def _append_event(domain_dir: Path, event: dict[str, Any]) -> tuple[bool, list[str]]:
    """Append one event, then reopen the file and confirm it is there.

    The readback is the point. A write that was attempted is not a write that
    landed, and this tool must not report persistence it has not confirmed.
    """
    errors: list[str] = []
    validate_event(event, 0, errors)
    if errors:
        return False, errors

    path = domain_dir / "training_history.jsonl"
    existing, load_errors = load_events(domain_dir)
    if load_errors and not path.is_file():
        return False, load_errors
    if any(e.get("event_id") == event["event_id"] for e in existing):
        return False, [f"event_id '{event['event_id']}' already exists"]

    line = json.dumps(event, ensure_ascii=False, sort_keys=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(line + "\n")

    reread, reread_errors = load_events(domain_dir)
    if reread_errors:
        return False, [f"readback failed: {problem}" for problem in reread_errors]
    if not any(e.get("event_id") == event["event_id"] for e in reread):
        return False, [f"readback failed: '{event['event_id']}' is not present after write"]
    return True, []


# ----------------------------------------------------------- persistence


def dump(data: Any) -> str:
    return yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=88)


def spliced_store(current: str, memory: dict[str, Any]) -> str | None:
    """The new store text with every unchanged member kept byte for byte.

    Re-serializing a whole store re-wraps every hand-wrapped sentence, so a
    one-field change would rewrite hundreds of lines. Instead the file is cut at
    its top-level `- id:` members, unchanged members keep their text, and only
    changed or new ones (plus `memory_version`) are dumped. None means the file
    is not in that shape; the caller then writes a full dump.

    The collection key is read from the store being written: `claims` for schema
    3, `entries` for a legacy store this still has to read back. R2.0 is explicit
    that byte-splicing is implementation rather than contract — it survives here
    because one key name was the whole cost of keeping it.
    """
    collection = "claims" if "claims" in memory else "entries"
    text = current.replace("\r\n", "\n")
    starts = [m.start() for m in re.finditer(r"(?m)^- id:", text)]
    if not starts:
        return None
    header, bodies = text[:starts[0]], [text[a:b] for a, b in zip(starts, starts[1:] + [len(text)])]
    try:
        old_header = (
            yaml.safe_load(header + " []\n")
            if header.rstrip().endswith(f"{collection}:")
            else None
        )
        old_members = [yaml.safe_load(body)[0] for body in bodies]
    except (yaml.YAMLError, TypeError, KeyError, IndexError):
        return None
    new_header = {k: v for k, v in memory.items() if k != collection}
    if not isinstance(old_header, dict) or {k: v for k, v in old_header.items() if k not in {collection, "memory_version"}} != {
        k: v for k, v in new_header.items() if k != "memory_version"
    }:
        return None
    header = re.sub(r"(?m)^memory_version:.*$", f"memory_version: {memory['memory_version']}", header, count=1)
    kept = {member.get("id"): body for member, body in zip(old_members, bodies) if isinstance(member, dict)}
    unchanged = {member.get("id"): member for member in old_members if isinstance(member, dict)}
    parts = []
    for member in memory.get(collection) or []:
        key = member.get("id") if isinstance(member, dict) else None
        body = kept.get(key) if unchanged.get(key) == member else None
        parts.append(body if body is not None else dump([member]))
    return header + "".join(part if part.endswith("\n") else part + "\n" for part in parts)


def write_memory(domain_dir: Path, memory: dict[str, Any]) -> None:
    """Replace the store atomically: a crash leaves the old file or the new one, never half."""
    path = domain_dir / "skill_memory.yaml"
    current = path.read_bytes().decode("utf-8") if path.is_file() else ""
    text = spliced_store(current, memory) if current else None
    if text is None or yaml.safe_load(text) != memory:
        text = dump(memory)
    # Keep the checkout's line endings; a text-mode write would convert them on Windows.
    newline = "\r\n" if "\r\n" in current else "\n"
    temporary = domain_dir / f".skill_memory.{os.getpid()}.{uuid.uuid4().hex}.tmp"
    try:
        temporary.write_bytes(text.replace("\n", newline).encode("utf-8"))
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


@contextmanager
def store_lock(domain_dir: Path):
    """One writer per domain store. The lock sits outside the store folder, which
    releases and project snapshots copy whole."""
    folder = domain_dir.parent / ".locks"
    folder.mkdir(exist_ok=True)
    path = folder / f"{domain_dir.name}.lock"
    try:
        descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        raise MemoryError_(
            f"another memory.py write holds {path.as_posix()}; if no memory.py process is running, "
            "a write was interrupted: run `memory.py validate`, then delete the lock"
        ) from exc
    try:
        os.write(descriptor, json.dumps({"pid": os.getpid(), "acquired_at": datetime.now().isoformat(timespec="seconds")}).encode("utf-8"))
    finally:
        os.close(descriptor)
    try:
        yield
    finally:
        path.unlink(missing_ok=True)


# ---------------------------------------------------------------- claims

# R2.5 §9.4: the question a claim-admitting write asks, verbatim from the R2.4
# admission rule and its Canon-only qualifier. It is printed, never evaluated.
# Whether a stated delta is real is a semantic judgment, and a validator that
# answered it would have exceeded its authority; what the tool can do is put the
# question in front of whoever is writing, at the moment of the write, rather
# than leave it to be inferred afterwards.
ADMISSION_QUESTION = (
    "Relative to this skill with Canon and no Memory, what does the next relevant\n"
    "task do differently because this is remembered?"
)
CANON_ONLY_BASELINE = (
    "Canon-only baseline: the comparison baseline is this skill + Canon + no Memory.\n"
    "Canon-as-written sits at the baseline. Therefore merely confirming that Canon\n"
    "worked is not a Memory delta.\n"
    "  - A restatement of a card, in the card's own terms, is not Memory.\n"
    "  - A delta that exists only because the skill failed to read available Canon is\n"
    "    a retrieval failure, not learned craft knowledge.\n"
    "  - A delta that would disappear if Canon were simply applied as written belongs\n"
    "    to the Canon-quality conversation, not to Memory."
)
# The keys whose change re-opens admission: the claim itself, and the behavioral
# delta that is the reason for keeping it. Editing an envelope, a cue, a canon
# link or a date does not re-ask the question.
ADMITTING_KEYS = ("claim", "delta")

# The write contract, stated once and attached to each writing subcommand's
# --help so the rules sit where an operator reads them.
WRITE_DISCIPLINE = (
    "Every write validates the whole resulting store first, replaces the file atomically "
    "under a per-domain lock, raises memory_version by exactly one, and confirms the "
    "result on readback; a refused write changes nothing. Currentness is presence: a "
    "claim that is no longer current leaves the store through `retire`, which writes no "
    "tombstone and no lineage. A replacement is `retire` then `add`, with a freshly "
    "generated id and independently re-derived confidence; nothing is inherited. Writing "
    "requires memory_schema_version 3."
)


def print_admission_prompt(stream: Any = None) -> None:
    """Put the admission question in front of the operator before the write."""
    stream = sys.stdout if stream is None else stream
    # Deliberately ASCII, like every other line this tool prints: the Windows
    # console encoding is not UTF-8, and a section sign here would arrive as a
    # decode error in whatever reads the transcript.
    print(
        "ADMISSION (R2.5, section 9.4) - a prompt, not a gate: this tool validates "
        "the shape of `delta` and never judges whether the delta is real.",
        file=stream,
    )
    print(ADMISSION_QUESTION, file=stream)
    print(CANON_ONLY_BASELINE, file=stream)


def ordered_claim(claim: dict[str, Any]) -> dict[str, Any]:
    """One claim in the order §3 documents, so every diff reads the same way.

    Dates become `date` objects, which YAML writes unquoted and reads back as
    dates - the readback comparison in `change_claims` is only meaningful if what
    was written round-trips to what was built.
    """
    known = {key: claim[key] for key in CLAIM_KEY_ORDER if key in claim}
    for key in ("last_verified", "revalidate_after"):
        value = known.get(key)
        if isinstance(value, str) and DATE_RE.fullmatch(value):
            known[key] = date.fromisoformat(value)
    return {**known, **{key: value for key, value in claim.items() if key not in known}}


def find_claim(claims: list[dict[str, Any]], claim_id: str) -> dict[str, Any] | None:
    return next((c for c in claims if isinstance(c, dict) and c.get("id") == claim_id), None)


def change_claims(domain_dir: Path, change) -> tuple[bool, list[str], dict[str, Any]]:
    """Apply `change(claims)` to a copy of the store, validate the whole result,
    then write it atomically and confirm it on readback. Nothing is written when
    the store was already invalid, the change reports a problem, the resulting
    store is invalid, or the readback disagrees.

    Those safety properties are inherited unchanged from the legacy writer this
    replaces; what changed is the collection it edits (`claims`), the validator
    the result is checked against, and the refusal of any store that is not
    schema 3. Writing is v3-only deliberately (R2.5 §9.1): a legacy store stays
    readable until its domain migrates, and the way to change one is to migrate
    it, not to keep a second writer alive behind it.

    History is loaded only when it sits beside the store, because beside a v3
    store its absence means "no evidence resolution" (I5) rather than a missing
    file.
    """
    with store_lock(domain_dir):
        memory = load_memory(domain_dir)
        declared = memory.get("memory_schema_version")
        if declared != V3_SCHEMA_VERSION:
            return False, [
                f"this store declares memory_schema_version {declared!r}; memory.py writes "
                f"schema {V3_SCHEMA_VERSION} only. Migrate the domain before writing to it"
            ], {}
        if (domain_dir / "training_history.jsonl").is_file():
            events, event_errors = load_events(domain_dir)
        else:
            events, event_errors = None, None
        before, _flags = validate_contents(domain_dir.name, memory, events, event_errors)
        if before:
            return False, ["the store is already invalid; repair it before writing:", *before], {}
        candidate = copy.deepcopy(memory)
        claims = candidate.get("claims") or []
        candidate["claims"] = claims
        problems = change(claims)
        if problems:
            return False, problems, {}
        # Normalize only what this write touched, so untouched claims keep their bytes.
        original = {c.get("id"): c for c in memory.get("claims") or [] if isinstance(c, dict)}
        candidate["claims"] = [
            ordered_claim(c) if isinstance(c, dict) and original.get(c.get("id")) != c else c
            for c in claims
        ]
        after, _flags = validate_contents(domain_dir.name, candidate, events, event_errors)
        if after:
            return False, after, {}
        candidate["memory_version"] = int(candidate.get("memory_version", 0)) + 1
        write_memory(domain_dir, candidate)
        reread = load_memory(domain_dir)
        if reread != candidate:
            return False, ["readback failed: the store does not contain what was written"], {}
    return True, [], candidate


def add_claim(domain_dir: Path, claim: dict[str, Any]) -> tuple[bool, list[str], str]:
    """Add one claim under an id this process generates (R2.5 §3.4, §9.3).

    The caller never supplies the id. There is no allocator to consult and
    nothing to continue from: retirement physically removes a claim, so a number
    derived from the surviving claims would be handed out twice. A supplied id is
    refused rather than honoured, because the id a caller is most likely to have
    in hand is the one that just left the store.

    `confidence` is whatever the caller stated. Nothing here reads the `evidence`
    list, counts events, looks at a date, or consults a claim that was retired, in
    order to produce, suggest or adjust it (F1, F4).
    """
    if not isinstance(claim, dict):
        return False, ["the claim must be a JSON object"], ""
    if "id" in claim:
        return False, [
            "a claim id is generated by `add` and never supplied: drop the `id` key. "
            "A retired claim's id is never reissued, so there is nothing to carry over"
        ], ""
    claim = dict(claim)
    claim["id"] = new_claim_id(domain_dir.name)

    def change(claims: list[dict[str, Any]]) -> list[str]:
        if find_claim(claims, claim["id"]):
            present = claim["id"]
            return [f"generated id '{present}' is already in this store; run `add` again"]
        claims.append(claim)
        return []

    ok, problems, _ = change_claims(domain_dir, change)
    return ok, problems, claim["id"] if ok else ""


def update_claim(domain_dir: Path, claim_id: str, patch: dict[str, Any]) -> tuple[bool, list[str]]:
    """Merge `patch` into one claim; a null value removes an optional key.

    Identity is not updatable, and no patch may reach it. A claim whose subject
    has moved far enough to want a different id is a different claim: retire this
    one and add that one.
    """
    if not isinstance(patch, dict) or not patch:
        return False, ["the update must be a non-empty JSON object"]
    if "id" in patch:
        return False, [
            "a claim id never changes; a claim that needs a different id is a different "
            "claim: `retire` this one and `add` the replacement, with a freshly generated "
            "id and independently re-derived confidence"
        ]
    removed_required = sorted(k for k, v in patch.items() if v is None and k in CLAIM_REQUIRED)
    if removed_required:
        return False, [f"required key(s) cannot be removed: {', '.join(removed_required)}"]

    def change(claims: list[dict[str, Any]]) -> list[str]:
        claim = find_claim(claims, claim_id)
        if claim is None:
            return [f"no claim '{claim_id}'"]
        for key, value in patch.items():
            if value is None:
                claim.pop(key, None)
            else:
                claim[key] = value
        return []

    ok, problems, _ = change_claims(domain_dir, change)
    return ok, problems


def retire_claim(domain_dir: Path, claim_id: str, reason: str | None) -> tuple[bool, list[str]]:
    """Remove one claim. Currentness is presence, so retirement is removal
    (R2.5 §1.4-§1.5).

    `reason` is required and operator-facing at the moment of the write. It is
    deliberately written nowhere: a retired claim's reason is lineage, and lineage
    is portable history-side, never a tombstone, a retired-id list, a sidecar, or
    a surviving field. The store left behind is a complete and correct statement
    of current learned state, with nothing missing from it.

    A claim another claim declares a contradiction with cannot leave on its own:
    the whole-store validation that follows fails I6 and the write is refused.
    That refusal is deliberate - R2.5 §4.8 forbids automatic erasure of a
    contradiction marker, so `retire` may not quietly strip the surviving side to
    let itself through. It also means a contradicted pair is currently stuck:
    resolving one needs a single write touching both claims, and that operation
    is not on the §8.3 surface. T08 sees the pair as a review item.
    """
    if not isinstance(reason, str) or not reason.strip():
        return False, [
            "retiring a claim requires an explicit reason; it is operator-facing at the "
            "moment of the write and is deliberately not persisted anywhere"
        ]

    def change(claims: list[dict[str, Any]]) -> list[str]:
        claim = find_claim(claims, claim_id)
        if claim is None:
            return [f"no claim '{claim_id}'"]
        claims.remove(claim)
        return []

    ok, problems, _ = change_claims(domain_dir, change)
    return ok, problems


# R2.5 §3.5: representative evidence is illustrative, never a measure of
# support, so the writer links at most three ids, refuses a count field, and
# never lets the number of linked ids become an output of its own.
LINK_EVIDENCE_CAP = 3


def link_evidence(
    domain_dir: Path,
    claim_id: str,
    event_ids: list[str],
    replace: bool = False,
) -> tuple[bool, list[str], list[str]]:
    """Make `event_ids` (one to three) a claim's complete `evidence`, today's date its `last_verified`.

    Returns `(ok, problems, dropped)`. `event_ids` replaces the claim's
    evidence rather than adding to it - a contract that reads like "add these"
    and loses a citation just as easily, so a call that would silently drop an
    id the claim already cites is refused unless `replace` says the loss is
    intended, and when it is intended the dropped ids come back to the caller
    to report honestly. Dropping a citation is sometimes right (an event later
    found invalid, or attributed to the wrong claim), which is why this is a
    confirmation rather than a prohibition.

    Admissibility is the shared helper T03 owns, called by both claim sides -
    not a private copy: unknown, invalid, correction, quarantined and
    non-performance events are refused here exactly as `validate` would refuse
    them in the store. Answering that question needs History beside the store,
    so a store with no `training_history.jsonl` refuses rather than linking
    evidence it cannot verify.

    `confidence` is never read, written, or suggested (F1), and no count field
    is ever written (R2.5 §3.5): how many events are linked is not a measure of
    support and nothing here presents it as one. The cap is enforced here so a
    fourth id is refused before it can reach the store; S9 holds the same bound
    for a claim written any other way.
    """
    ids = [str(event_id) for event_id in event_ids] if isinstance(event_ids, list) else []
    problems: list[str] = []
    if not ids:
        problems.append("linking evidence requires at least one event id")
    elif len(ids) > LINK_EVIDENCE_CAP:
        problems.append(
            f"refusing {len(ids)} event ids; representative evidence is capped at "
            f"{LINK_EVIDENCE_CAP} members (S9): evidence is illustrative, never a measure"
        )
    if len(set(ids)) != len(ids):
        problems.append("evidence members are distinct; the same event id is named twice")
    if problems:
        return False, problems, []

    events, load_errors = load_events(domain_dir)
    if load_errors:
        return False, load_errors, []
    by_id = {str(event.get("event_id")): event for event in events}
    quarantined = quarantined_event_ids(events)
    refused: list[str] = []
    for event_id in ids:
        problem = evidence_admissibility_problem(
            claim_id, "evidence", event_id, by_id.get(event_id), quarantined,
        )
        if problem:
            refused.append(problem)
    if refused:
        return False, refused, []

    dropped: list[str] = []

    def change(claims: list[dict[str, Any]]) -> list[str]:
        claim = find_claim(claims, claim_id)
        if claim is None:
            return [f"no claim '{claim_id}'"]
        already_cited = [str(member) for member in claim.get("evidence") or []]
        lost = [member for member in already_cited if member not in ids]
        if lost and not replace:
            return [
                f"'{claim_id}' already cites {', '.join(lost)}, which this call would "
                "remove: pass every event the claim should end up citing, or --replace "
                "if the loss is intended"
            ]
        dropped.extend(lost)
        claim["evidence"] = list(ids)
        claim["last_verified"] = date.today()
        return []

    ok, problems, _ = change_claims(domain_dir, change)
    # `dropped` is only reported for a write that actually landed; a change
    # refused by validation never removed anything.
    return (ok, problems, dropped) if ok else (False, problems, [])


def uncited_valid_events(domain_dir: Path) -> list[str]:
    """Valid performance events no claim and no legacy entry cites.

    Informational only (R2.5 §8.4): with representative evidence capped at
    three, this list is a view of History nothing has linked yet - not a
    backlog to drain, not a queue of pending work, and not a measure of
    support.
    """
    memory = load_memory(domain_dir)
    cited: set[str] = set()
    for entry in memory.get("entries") or []:
        if isinstance(entry, dict) and isinstance(entry.get("evidence_events"), list):
            cited.update(str(e) for e in entry["evidence_events"])
    for claim in memory.get("claims") or []:
        if isinstance(claim, dict) and isinstance(claim.get("evidence"), list):
            cited.update(str(member) for member in claim["evidence"])
    events, _ = load_events(domain_dir)
    quarantined = {
        str(target)
        for event in events
        if event.get("event_kind") == "evidence_correction"
        and (event.get("corrections") or {}).get("disposition") == "quarantined"
        for target in (event.get("supersedes_events") or [])
    }
    return [
        str(e.get("event_id"))
        for e in events
        if e.get("validity") == "valid"
        and e.get("event_kind", "performance") == "performance"
        and str(e.get("event_id")) not in cited
        and str(e.get("event_id")) not in quarantined
    ]


# ---------------------------------------------------------------- review


def library_object_ids(library_root: Path) -> set[str]:
    ids: set[str] = set()
    if not library_root.is_dir():
        return ids
    for path in library_root.rglob("*.md"):
        if path.name in {"README.md", "INDEX.md"}:
            continue
        head = path.read_text(encoding="utf-8")[:2000]
        match = re.search(r"(?m)^object_id:\s*(\S+)\s*$", head)
        if match:
            ids.add(match.group(1))
    return ids


def review_store(domain_dir: Path, library_root: Path | None) -> list[str]:
    notes: list[str] = []
    memory = load_memory(domain_dir)
    entries = [e for e in memory.get("entries") or [] if isinstance(e, dict)]
    known = library_object_ids(library_root) if library_root else set()
    cutoff = datetime.now().date() - timedelta(days=STALE_DAYS)

    for entry in entries:
        label = entry.get("id", "entry")
        status = entry.get("status")
        if status not in RETRIEVABLE_STATUS:
            continue
        verified = entry.get("last_verified")
        if not verified:
            notes.append(f"{label}: active with no last_verified")
        elif DATE_RE.fullmatch(str(verified)) and date.fromisoformat(str(verified)) < cutoff:
            notes.append(f"{label}: last verified {verified}, older than {STALE_DAYS} days")
        if entry.get("confidence") == "strong" and int(entry.get("evidence_count", 0) or 0) <= 1:
            notes.append(f"{label}: confidence strong on {entry.get('evidence_count', 0)} event(s)")
        if entry.get("evidence_class") == "deterministic_contract" and status == "active":
            notes.append(
                f"{label}: deterministic_contract still active: if the fix landed, "
                "move it to resolved and let the test hold it"
            )
        if known:
            for owner in entry.get("likely_owners") or []:
                owner = str(owner)
                if re.fullmatch(r"(?:PAT|DRILL|AP)_[a-z0-9_]+", owner) and owner not in known:
                    notes.append(f"{label}: likely_owner '{owner}' no longer exists in the library")
    uncited = uncited_valid_events(domain_dir)
    if uncited:
        notes.append(
            f"{len(uncited)} valid event(s) are not cited by any claim or entry: "
            f"{', '.join(uncited[:8])} - informational only, not a backlog: under the "
            "cap of three representative events this is not a measure of support"
        )
    return notes


# ---------------------------------------------------------------- CLI


def _schema_version_label(domain_dir: Path) -> str:
    """The store's declared schema version, as the validate summary prints it."""
    try:
        version = load_memory(domain_dir).get("memory_schema_version")
    except MemoryError_:
        return "unreadable"
    return "absent" if version is None else str(version)


def cmd_validate(args: argparse.Namespace) -> int:
    dirs = domain_dirs(args.memory, args.domain)
    if not dirs:
        print(f"No domain memory found under {args.memory.as_posix()}.")
        return 0
    total = 0
    for domain_dir in dirs:
        # Which schema version this store declares, so a mixed-state corpus is
        # legible while domains migrate (T04).
        print(f"{domain_dir.name}: memory_schema_version {_schema_version_label(domain_dir)}")
        errors, flags = validate_store(domain_dir)
        for error in errors:
            print(f"{domain_dir.name}: {error}")
        for flag in flags:
            print(f"{domain_dir.name}: FLAG: {flag}")
        total += len(errors)
    if total:
        print(f"FAIL: {total} issue(s) across {len(dirs)} memory store(s)")
        return 1
    entries = sum(len(load_memory(d).get("entries") or []) for d in dirs)
    events = sum(len(load_events(d)[0]) for d in dirs)
    print(f"PASS: {len(dirs)} store(s), {entries} entr(ies), {events} event(s) validated")
    return 0


def cmd_query(args: argparse.Namespace) -> int:
    dirs = domain_dirs(args.memory, args.domain)
    cues = [c.strip() for c in (args.cues or "").split(",") if c.strip()]
    returned: list[str] = []
    for domain_dir in dirs:
        results = query_store(domain_dir, args.scope_id, cues, args.limit)
        for entry in results:
            returned.append(str(entry.get("id")))
            print(f"[{entry.get('id')}] {entry.get('scope_type')}:{entry.get('scope_id')} "
                  f"({entry.get('type')}, {entry.get('confidence')}, {entry.get('status')})")
            print(f"    {' '.join(str(entry.get('observation', '')).split())}")
            if entry.get("boundary"):
                print(f"    boundary: {' '.join(str(entry['boundary']).split())}")
    # A retrieval receipt. Consultation cannot be proven by a memory file
    # existing; it can be recorded by naming what was actually returned.
    print(f"retrieved: {', '.join(returned) if returned else '(none)'}")
    return 0


def cmd_append(args: argparse.Namespace) -> int:
    dirs = domain_dirs(args.memory, args.domain)
    if len(dirs) != 1:
        print("FAIL: append requires exactly one --domain", file=sys.stderr)
        return 1
    domain_dir = dirs[0]
    if args.json:
        event = read_json_argument(args.json)
        if not isinstance(event, dict):
            print("FAIL: --json must be a JSON object describing one event", file=sys.stderr)
            return 1
    else:
        event = {"task": args.task, "validity": args.validity, "date": args.date or date.today().isoformat()}
        if args.invalid_reason:
            event["invalid_reason"] = args.invalid_reason
        if args.scope_id:
            event["scope_id"] = args.scope_id
        if args.delivery:
            event["delivery"] = args.delivery
        if args.note:
            event["notes"] = args.note
    events, _ = load_events(domain_dir)
    event.setdefault("event_id", next_event_id(events, domain_dir.name))
    event.setdefault("date", date.today().isoformat())

    ok, problems = append_event(domain_dir, event)
    if not ok:
        for problem in problems:
            print(f"{domain_dir.name}: {problem}", file=sys.stderr)
        print("FAIL: event not appended", file=sys.stderr)
        return 1
    print(f"PASS: appended {event['event_id']} and confirmed it on readback")
    return 0


def cmd_link_evidence(args: argparse.Namespace) -> int:
    """`link-evidence`: one to three admissible events behind one claim."""
    dirs = domain_dirs(args.memory, args.domain)
    if not args.domain or len(dirs) != 1:
        print("FAIL: link-evidence requires exactly one --domain", file=sys.stderr)
        return 1
    domain_dir = dirs[0]
    event_ids = [e.strip() for e in (args.events or "").split(",") if e.strip()]
    if not event_ids:
        print("FAIL: --events is required with --claim", file=sys.stderr)
        return 1
    ok, problems, dropped = link_evidence(
        domain_dir, args.claim, event_ids, replace=args.replace,
    )
    if not ok:
        for problem in problems:
            print(f"{domain_dir.name}: {problem}", file=sys.stderr)
        print("FAIL: memory unchanged", file=sys.stderr)
        return 1
    print(f"PASS: {args.claim} now cites {', '.join(event_ids)}; confirmed on readback")
    if dropped:
        print(f"dropped by --replace: {', '.join(dropped)}")
    return 0


def read_json_argument(value: str | None) -> Any:
    """Parse `--json`: a literal JSON object or array, or a path to a JSON file.

    A value whose first non-space character is `{` or `[` is literal JSON and is
    never treated as a path. Probing it as one fails on long input (a filename
    over the platform limit raises ENAMETOOLONG on Linux) and could silently read
    an unrelated file whose name happens to match the text.
    """
    if value is None:
        return None
    if value.lstrip().startswith(("{", "[")):
        text = value
    else:
        try:
            text = Path(value).read_text(encoding="utf-8")
        except OSError as exc:
            raise MemoryError_(
                f"--json must be a literal JSON object or a readable JSON file: {exc}"
            ) from exc
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise MemoryError_(f"--json is not valid JSON: {exc}") from exc


def cmd_claim(args: argparse.Namespace) -> int:
    """`add`, `update`, `retire` and `show` against one domain's v3 store.

    The admission prompt is printed before `add` and before any `update` that
    touches a key in `ADMITTING_KEYS`, whatever the write then turns out to be:
    it asks the operator a question, so it would be useless printed only after
    the tool had already agreed to the write.
    """
    dirs = domain_dirs(args.memory, args.domain)
    if not args.domain or len(dirs) != 1:
        print(f"FAIL: {args.command} requires exactly one --domain", file=sys.stderr)
        return 1
    domain_dir = dirs[0]
    if args.command == "show":
        claim = find_claim(load_memory(domain_dir).get("claims") or [], args.id)
        if claim is None:
            print(f"FAIL: no claim '{args.id}'", file=sys.stderr)
            return 1
        print(yaml.safe_dump(claim, sort_keys=False, allow_unicode=True, width=88), end="")
        return 0
    if args.command == "retire":
        ok, problems = retire_claim(domain_dir, args.id, args.reason)
        done = f"retired {args.id}; its reason stays with you and was written nowhere"
    elif args.command == "add":
        data = read_json_argument(args.json)
        print_admission_prompt()
        ok, problems, claim_id = add_claim(domain_dir, data)
        done = f"added {claim_id}"
    else:
        data = read_json_argument(args.json)
        if isinstance(data, dict) and any(key in data for key in ADMITTING_KEYS):
            print_admission_prompt()
        ok, problems = update_claim(domain_dir, args.id, data)
        done = f"updated {args.id}"
    if not ok:
        for problem in problems:
            print(f"{domain_dir.name}: {problem}", file=sys.stderr)
        print("FAIL: memory unchanged", file=sys.stderr)
        return 1
    print(f"PASS: {done}; the whole store validated and was confirmed on readback")
    return 0


def cmd_review(args: argparse.Namespace) -> int:
    dirs = domain_dirs(args.memory, args.domain)
    library = args.library if args.library and args.library.is_dir() else None
    total = 0
    for domain_dir in dirs:
        notes = review_store(domain_dir, library)
        for note in notes:
            print(f"{domain_dir.name}: {note}")
        total += len(notes)
    print(f"{total} item(s) suggested for review")
    return 0


def main() -> int:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--memory", type=Path, default=default_memory_root())
    common.add_argument("--domain", default=None, help="Limit to one domain (e.g. art).")

    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser(
        "validate", parents=[common],
        help="Check shape, closed vocabularies, and evidence admissibility.",
    )

    query = sub.add_parser("query", parents=[common], help="Retrieve a bounded set of active entries.")
    query.add_argument("--scope-id", default=None)
    query.add_argument("--cues", default=None, help="Comma-separated retrieval cues.")
    query.add_argument("--limit", type=int, default=5)

    append = sub.add_parser("append", parents=[common], help="Append one high-signal event, verified by readback.")
    append.add_argument("--task")
    append.add_argument("--validity", choices=sorted(VALIDITY_VALUES), default="valid")
    append.add_argument("--invalid-reason", default=None)
    append.add_argument("--scope-id", default=None)
    append.add_argument("--delivery", default=None)
    append.add_argument("--date", default=None)
    append.add_argument("--note", default=None)
    append.add_argument("--json", default=None, help="Path to, or literal, JSON event.")

    link = sub.add_parser(
        "link-evidence", parents=[common],
        help="Link one to three admissible events behind a claim.",
        description=(
            "`--events` is the claim's complete evidence after the call: one to three "
            "admissible events replace it and `last_verified` becomes today. A cited id "
            "the new list omits is refused unless `--replace` confirms the loss, and the "
            "dropped ids are reported. The number of linked ids is representative only - "
            "never a count field, never a measure of support, and never a confidence."
        ),
    )
    link.add_argument("--claim", required=True, help="The claim id to link evidence behind.")
    link.add_argument(
        "--events", required=True,
        help="Comma-separated event ids; one to three, each one admissible.",
    )
    link.add_argument(
        "--replace",
        action="store_true",
        help="Confirm that events the claim already cites and --events omits should be dropped.",
    )

    review = sub.add_parser("review", parents=[common], help="List entries that need revalidation.")
    review.add_argument("--library", type=Path, default=default_library_root())

    add = sub.add_parser(
        "add", parents=[common], description=WRITE_DISCIPLINE,
        help="Add one claim under a generated id; the caller never supplies one.",
    )
    add.add_argument("--json", required=True, help="Path to, or literal, JSON claim.")

    update = sub.add_parser(
        "update", parents=[common], description=WRITE_DISCIPLINE,
        help="Merge fields into one claim; null removes an optional key. The id never changes.",
    )
    update.add_argument("--id", required=True)
    update.add_argument("--json", required=True, help="Path to, or literal, JSON object of changed fields.")

    retire = sub.add_parser(
        "retire", parents=[common], description=WRITE_DISCIPLINE,
        help="Remove one claim; a replacement is `retire` then `add`, with a fresh id and "
             "independently re-derived confidence.",
    )
    retire.add_argument("--id", required=True)
    retire.add_argument(
        "--reason", required=True,
        help="Why this is no longer current. Operator-facing at the moment of the write; "
             "never persisted into Memory, History, or anything beside them.",
    )

    show = sub.add_parser("show", parents=[common], help="Print one claim.")
    show.add_argument("--id", required=True)

    args = parser.parse_args()
    handlers = {
        "validate": cmd_validate, "query": cmd_query, "append": cmd_append,
        "link-evidence": cmd_link_evidence, "review": cmd_review,
        "add": cmd_claim, "update": cmd_claim, "retire": cmd_claim, "show": cmd_claim,
    }
    try:
        return handlers[args.command](args)
    except MemoryError_ as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
