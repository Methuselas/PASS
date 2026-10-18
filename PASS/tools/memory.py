#!/usr/bin/env python3
"""Skillset Memory tooling: validate, query, append, compact, review, entry.

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
LEGACY_V1_ENTRY_TYPES = {
    "learned_principle",
    "recurring_failure",
    "successful_tendency",
    "known_boundary",
    "training_result",
}

SCOPE_TYPES = {"skillset", "ap", "pattern", "drill", "training", "topic", "runtime"}
ENTRY_TYPES = LEGACY_V1_ENTRY_TYPES | {
    "specialization_profile",
    "card_candidate",
}
EVIDENCE_CLASSES = {"stochastic_performance", "deterministic_contract"}
CONFIDENCE_VALUES = {"provisional", "repeated", "strong"}
STATUS_VALUES = {"active", "monitoring", "resolved", "superseded", "obsolete"}
RETRIEVABLE_STATUS = {"active", "monitoring"}
EVIDENCE_ORIGINS = {
    "runtime_self_audit", "user_feedback", "human_teaching", "training_benchmark",
    "regression_failure", "book_close_training", "cross_model_test",
}
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
ENTRY_OPTIONAL = {
    "diagnosis", "boundary", "evidence_count", "evidence_events", "evidence_origin",
    "likely_owners", "interventions", "retrieval_cues", "runtime_scope",
    "superseded_by", "last_verified",
}
ENTRY_KEYS = ENTRY_REQUIRED | ENTRY_OPTIONAL
DIAGNOSIS_KEYS = {"failure_layer", "hypothesis"}
INTERVENTION_KEYS = {
    "training", "drill", "isolation_result", "retention_result", "transfer_result",
}
FILE_REQUIRED = {"memory_schema_version", "skillset", "memory_version", "entries"}

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


def validate_entry(entry: Any, index: int, errors: list[str]) -> None:
    where = f"entry[{index}]"
    if not isinstance(entry, dict):
        errors.append(f"{where}: must be a mapping")
        return
    label = entry.get("id") if isinstance(entry.get("id"), str) else where

    missing = sorted(ENTRY_REQUIRED - set(entry))
    if missing:
        errors.append(f"{label}: missing required keys: {', '.join(missing)}")
    forbidden = sorted(set(entry) & FORBIDDEN_KEYS)
    if forbidden:
        errors.append(f"{label}: forbidden key(s) from retired or session vocabulary: {', '.join(forbidden)}")
    extra = sorted(set(entry) - ENTRY_KEYS - FORBIDDEN_KEYS)
    if extra:
        errors.append(f"{label}: unknown key(s): {', '.join(extra)}")

    if isinstance(entry.get("id"), str) and not ID_RE.fullmatch(entry["id"]):
        errors.append(f"{label}: id must be uppercase alphanumeric with underscores")

    for key, allowed in (
        ("scope_type", SCOPE_TYPES),
        ("type", ENTRY_TYPES),
        ("evidence_class", EVIDENCE_CLASSES),
        ("confidence", CONFIDENCE_VALUES),
        ("status", STATUS_VALUES),
    ):
        if key in entry and entry[key] not in allowed:
            errors.append(f"{label}: {key} '{entry[key]}' is not in the closed vocabulary")

    observation = entry.get("observation")
    if not isinstance(observation, str) or not observation.strip():
        errors.append(f"{label}: observation must be non-empty text")
    else:
        lowered = observation.lower()
        for phrase in NON_SELF_CONTAINED_PHRASES:
            if phrase in lowered:
                errors.append(f"{label}: observation defers to a conversation ('{phrase}'); it must stand alone")
                break

    if "scope_id" in entry and (not isinstance(entry["scope_id"], str) or not entry["scope_id"].strip()):
        errors.append(f"{label}: scope_id must be a non-empty string")

    diagnosis = entry.get("diagnosis")
    if diagnosis is not None:
        if not isinstance(diagnosis, dict):
            errors.append(f"{label}: diagnosis must be a mapping")
        else:
            unknown = sorted(set(diagnosis) - DIAGNOSIS_KEYS)
            if unknown:
                errors.append(f"{label}: diagnosis has unknown key(s): {', '.join(unknown)}")
            layer = diagnosis.get("failure_layer")
            if layer is not None and layer not in FAILURE_LAYERS:
                errors.append(f"{label}: diagnosis.failure_layer '{layer}' is not in the closed vocabulary")

    origins = entry.get("evidence_origin")
    if origins is not None:
        if not isinstance(origins, list):
            errors.append(f"{label}: evidence_origin must be a list")
        else:
            for origin in origins:
                if origin not in EVIDENCE_ORIGINS:
                    errors.append(f"{label}: evidence_origin '{origin}' is not in the closed vocabulary")

    count = entry.get("evidence_count")
    if count is not None and (not isinstance(count, int) or isinstance(count, bool) or count < 1):
        errors.append(f"{label}: evidence_count must be an integer >= 1")

    for key in ("evidence_events", "likely_owners", "retrieval_cues"):
        if key in entry and not isinstance(entry[key], list):
            errors.append(f"{label}: {key} must be a list")

    interventions = entry.get("interventions")
    if interventions is not None:
        if not isinstance(interventions, list):
            errors.append(f"{label}: interventions must be a list")
        else:
            for item in interventions:
                if not isinstance(item, dict):
                    errors.append(f"{label}: each intervention must be a mapping")
                    continue
                unknown = sorted(set(item) - INTERVENTION_KEYS)
                if unknown:
                    errors.append(f"{label}: intervention has unknown key(s): {', '.join(unknown)}")
                for result_key in ("isolation_result", "retention_result", "transfer_result"):
                    if result_key in item and item[result_key] not in STAGE_RESULTS:
                        errors.append(f"{label}: intervention {result_key} '{item[result_key]}' is not in the closed vocabulary")

    verified = entry.get("last_verified")
    if verified is not None and not (isinstance(verified, (str, date)) and DATE_RE.fullmatch(str(verified))):
        errors.append(f"{label}: last_verified must be YYYY-MM-DD")


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


def validate_store(domain_dir: Path) -> list[str]:
    try:
        memory = load_memory(domain_dir)
    except MemoryError_ as exc:
        return [str(exc)]
    events, event_errors = load_events(domain_dir)
    return validate_contents(domain_dir.name, memory, events, event_errors)


def validate_contents(
    domain: str,
    memory: dict[str, Any],
    events: list[dict[str, Any]],
    event_errors: list[str],
) -> list[str]:
    """Validate a store's contents, so a proposed write is checked before it lands."""
    errors: list[str] = []
    missing = sorted(FILE_REQUIRED - set(memory))
    if missing:
        errors.append(f"skill_memory.yaml: missing file-level keys: {', '.join(missing)}")
    schema_version = memory.get("memory_schema_version")
    if schema_version not in SUPPORTED_SCHEMA_VERSIONS:
        errors.append(
            f"skill_memory.yaml: memory_schema_version must be one of {sorted(SUPPORTED_SCHEMA_VERSIONS)}"
        )
    if memory.get("skillset") != domain:
        errors.append(f"skill_memory.yaml: skillset '{memory.get('skillset')}' does not match directory '{domain}'")

    entries = memory.get("entries")
    if entries is None:
        entries = []
    if not isinstance(entries, list):
        errors.append("skill_memory.yaml: entries must be a list")
        entries = []

    if schema_version == 1:
        for index, entry in enumerate(entries):
            if isinstance(entry, dict) and entry.get("type") in {"specialization_profile", "card_candidate"}:
                label = entry.get("id", f"entry[{index}]")
                errors.append(
                    f"{label}: type '{entry.get('type')}' requires memory_schema_version 2"
                )

    for index, entry in enumerate(entries):
        validate_entry(entry, index, errors)

    ids = [e["id"] for e in entries if isinstance(e, dict) and isinstance(e.get("id"), str)]
    for duplicate in sorted({i for i in ids if ids.count(i) > 1}):
        errors.append(f"skill_memory.yaml: duplicate entry id '{duplicate}'")

    errors.extend(event_errors)
    quarantined = {
        str(target)
        for event in events
        if event.get("event_kind") == "evidence_correction"
        and (event.get("corrections") or {}).get("disposition") == "quarantined"
        for target in (event.get("supersedes_events") or [])
    }
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
    known_ids = set(ids)

    for entry in entries:
        if not isinstance(entry, dict):
            continue
        label = entry.get("id", "entry")
        superseded_by = entry.get("superseded_by")
        if superseded_by is not None and superseded_by not in known_ids:
            errors.append(f"{label}: superseded_by '{superseded_by}' does not resolve to an entry")
        if entry.get("status") == "superseded" and not superseded_by:
            errors.append(f"{label}: status superseded requires superseded_by")

        cited = entry.get("evidence_events")
        if not isinstance(cited, list):
            continue
        for event_id in cited:
            event = by_event_id.get(event_id)
            if event is None:
                errors.append(f"{label}: evidence_events cites unknown event '{event_id}'")
                continue
            # The invariant this whole tool exists to hold.
            if event.get("validity") == "invalid":
                errors.append(
                    f"{label}: evidence_events cites invalid event '{event_id}' "
                    f"({event.get('invalid_reason', 'no reason recorded')}); "
                    "an invalid run is never evidence about a capability"
                )
            elif event.get("event_kind") == "metadata_correction":
                errors.append(
                    f"{label}: evidence_events cites metadata correction '{event_id}'; "
                    "a correction is not capability evidence"
                )
            elif event.get("event_kind") == "evidence_correction":
                errors.append(
                    f"{label}: evidence_events cites evidence correction '{event_id}'; "
                    "a correction is not capability evidence"
                )
            elif event_id in quarantined:
                errors.append(
                    f"{label}: evidence_events cites quarantined event '{event_id}'; "
                    "a superseding evidence correction removed it from capability evidence"
                )
        count = entry.get("evidence_count")
        if isinstance(count, int) and not isinstance(count, bool) and cited and count != len(cited):
            errors.append(f"{label}: evidence_count {count} does not match {len(cited)} cited evidence_events")

    return errors


# ------------------------------------------------- claim schema (version 3)
#
# Structural validation for a `memory_schema_version: 3` store, beside the
# legacy validator and sharing none of its vocabulary constants. The split is
# deliberate: FORBIDDEN_KEYS rejects `provenance` on v1/v2 entries and History
# events, while every v3 claim requires it (R2.5 §4.5 L1, SR1), so the two
# rejection lists can never be merged. Dispatch is T04's job; nothing routes a
# live store here yet — this validator is reachable from tests and from an
# explicit internal call only.

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

    The same derivation the legacy path applies inline (`validate_contents`);
    T04 folds both into one helper so the two cannot drift apart.
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
    event_id: str,
    event: dict[str, Any],
    quarantined: set[str],
) -> str | None:
    """I4: why this event may not be cited as capability evidence, or None.

    The legacy path's admissibility block — invalid run, both correction
    kinds, quarantine ("the invariant this whole tool exists to hold") — plus
    the performance-kind requirement of R2.5 §3.5, phrased for this path's
    field name. T04 extracts one helper both paths call; until then these two
    implementations state the same semantics, and a change to one belongs in
    the other.
    """
    if event.get("validity") == "invalid":
        return (
            f"{label}: evidence cites invalid event '{event_id}' "
            f"({event.get('invalid_reason', 'no reason recorded')}); "
            "an invalid run is never evidence about a capability (I4)"
        )
    kind = event.get("event_kind", "performance")
    if kind == "metadata_correction":
        return (
            f"{label}: evidence cites metadata correction '{event_id}'; "
            "a correction is not capability evidence (I4)"
        )
    if kind == "evidence_correction":
        return (
            f"{label}: evidence cites evidence correction '{event_id}'; "
            "a correction is not capability evidence (I4)"
        )
    if event_id in quarantined:
        return (
            f"{label}: evidence cites quarantined event '{event_id}'; "
            "a superseding evidence correction removed it from capability evidence (I4)"
        )
    if kind != "performance":
        return (
            f"{label}: evidence cites '{event_id}' of kind '{kind}'; "
            "only a performance event is capability evidence (I4)"
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
                event = by_event_id.get(str(member))
                if event is None:
                    errors.append(f"{label}: evidence cites unknown event '{member}' (I4)")
                    continue
                problem = evidence_admissibility_problem(label, str(member), event, quarantined)
                if problem:
                    errors.append(problem)

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


# ---------------------------------------------------------------- compact


def dump(data: Any) -> str:
    return yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=88)


def spliced_store(current: str, memory: dict[str, Any]) -> str | None:
    """The new store text with every unchanged entry kept byte for byte.

    Re-serializing a whole store re-wraps every hand-wrapped observation, so a
    one-field change would rewrite hundreds of lines. Instead the file is cut at
    its top-level `- id:` entries, unchanged entries keep their text, and only
    changed or new entries (plus `memory_version`) are dumped. None means the file
    is not in that shape; the caller then writes a full dump.
    """
    text = current.replace("\r\n", "\n")
    starts = [m.start() for m in re.finditer(r"(?m)^- id:", text)]
    if not starts:
        return None
    header, bodies = text[:starts[0]], [text[a:b] for a, b in zip(starts, starts[1:] + [len(text)])]
    try:
        old_header = yaml.safe_load(header + " []\n") if header.rstrip().endswith("entries:") else None
        old_entries = [yaml.safe_load(body)[0] for body in bodies]
    except (yaml.YAMLError, TypeError, KeyError, IndexError):
        return None
    new_header = {k: v for k, v in memory.items() if k != "entries"}
    if not isinstance(old_header, dict) or {k: v for k, v in old_header.items() if k not in {"entries", "memory_version"}} != {
        k: v for k, v in new_header.items() if k != "memory_version"
    }:
        return None
    header = re.sub(r"(?m)^memory_version:.*$", f"memory_version: {memory['memory_version']}", header, count=1)
    kept = {entry.get("id"): body for entry, body in zip(old_entries, bodies) if isinstance(entry, dict)}
    unchanged = {entry.get("id"): entry for entry in old_entries if isinstance(entry, dict)}
    parts = []
    for entry in memory.get("entries") or []:
        key = entry.get("id") if isinstance(entry, dict) else None
        body = kept.get(key) if unchanged.get(key) == entry else None
        parts.append(body if body is not None else dump([entry]))
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


# ---------------------------------------------------------------- entries

# The order the schema documents; new and edited entries are written in it so
# diffs stay small and every entry reads the same way.
ENTRY_KEY_ORDER = (
    "id", "scope_type", "scope_id", "type", "evidence_class", "observation", "confidence",
    "status", "diagnosis", "boundary", "evidence_count", "evidence_events", "evidence_origin",
    "likely_owners", "interventions", "retrieval_cues", "runtime_scope", "superseded_by",
    "last_verified",
)


def ordered_entry(entry: dict[str, Any]) -> dict[str, Any]:
    known = {key: entry[key] for key in ENTRY_KEY_ORDER if key in entry}
    verified = known.get("last_verified")
    if isinstance(verified, str) and DATE_RE.fullmatch(verified):
        known["last_verified"] = date.fromisoformat(verified)
    return {**known, **{key: value for key, value in entry.items() if key not in known}}


def next_entry_id(entries: list[dict[str, Any]]) -> str:
    numbered = [re.fullmatch(r"(.*_)(\d+)", str(e.get("id", ""))) for e in entries]
    numbered = [m for m in numbered if m]
    if not numbered:
        raise MemoryError_("this store has no numbered entry ids to continue; give the new entry an explicit id")
    prefix = max(numbered, key=lambda m: int(m.group(2))).group(1)
    width = max(len(m.group(2)) for m in numbered)
    number = max(int(m.group(2)) for m in numbered if m.group(1) == prefix) + 1
    return f"{prefix}{number:0{width}d}"


def change_entries(domain_dir: Path, change) -> tuple[bool, list[str], dict[str, Any]]:
    """Apply `change(entries)` to a copy of the store, validate the whole result,
    then write it atomically and confirm it on readback. Nothing is written when
    the change or the resulting store is invalid."""
    with store_lock(domain_dir):
        memory = load_memory(domain_dir)
        events, event_errors = load_events(domain_dir)
        before = validate_contents(domain_dir.name, memory, events, event_errors)
        if before:
            return False, ["the store is already invalid; repair it before writing:", *before], {}
        candidate = copy.deepcopy(memory)
        entries = candidate.get("entries") or []
        candidate["entries"] = entries
        problems = change(entries)
        if problems:
            return False, problems, {}
        # Normalize only what this write touched, so untouched entries keep their bytes.
        original = {e.get("id"): e for e in memory.get("entries") or [] if isinstance(e, dict)}
        candidate["entries"] = [
            ordered_entry(e) if isinstance(e, dict) and original.get(e.get("id")) != e else e
            for e in entries
        ]
        after = validate_contents(domain_dir.name, candidate, events, event_errors)
        if after:
            return False, after, {}
        candidate["memory_version"] = int(candidate.get("memory_version", 0)) + 1
        write_memory(domain_dir, candidate)
        reread = load_memory(domain_dir)
        if reread != candidate:
            return False, ["readback failed: the store does not contain what was written"], {}
    return True, [], candidate


def find_entry(entries: list[dict[str, Any]], entry_id: str) -> dict[str, Any] | None:
    return next((e for e in entries if isinstance(e, dict) and e.get("id") == entry_id), None)


def add_entry(domain_dir: Path, entry: dict[str, Any]) -> tuple[bool, list[str], str]:
    if not isinstance(entry, dict):
        return False, ["the entry must be a JSON object"], ""
    entry = dict(entry)
    added: list[str] = []

    def change(entries: list[dict[str, Any]]) -> list[str]:
        entry.setdefault("id", next_entry_id(entries))
        if find_entry(entries, entry["id"]):
            return [f"entry '{entry['id']}' already exists; use `entry update`"]
        entries.append(entry)
        added.append(entry["id"])
        return []

    ok, problems, _ = change_entries(domain_dir, change)
    return ok, problems, added[0] if added else ""


def update_entry(domain_dir: Path, entry_id: str, patch: dict[str, Any]) -> tuple[bool, list[str]]:
    """Merge `patch` into one entry; a null value removes an optional key."""
    if not isinstance(patch, dict) or not patch:
        return False, ["the update must be a non-empty JSON object"]
    if "id" in patch:
        return False, ["an entry id never changes; add a new entry and supersede this one instead"]
    removed_required = sorted(k for k, v in patch.items() if v is None and k in ENTRY_REQUIRED)
    if removed_required:
        return False, [f"required key(s) cannot be removed: {', '.join(removed_required)}"]

    def change(entries: list[dict[str, Any]]) -> list[str]:
        entry = find_entry(entries, entry_id)
        if entry is None:
            return [f"no entry '{entry_id}'"]
        if patch.get("status") == "superseded":
            return ["mark an entry superseded with `entry supersede`, which names its replacement"]
        for key, value in patch.items():
            if value is None:
                entry.pop(key, None)
            else:
                entry[key] = value
        return []

    ok, problems, _ = change_entries(domain_dir, change)
    return ok, problems


def supersede_entry(
    domain_dir: Path, entry_id: str, replacement_id: str | None, replacement: dict[str, Any] | None,
) -> tuple[bool, list[str], str]:
    """Retire one entry in favour of another, optionally adding the replacement in
    the same write so the store is never left pointing at nothing."""
    chosen: list[str] = []

    def change(entries: list[dict[str, Any]]) -> list[str]:
        old = find_entry(entries, entry_id)
        if old is None:
            return [f"no entry '{entry_id}'"]
        if old.get("status") == "superseded":
            return [f"'{entry_id}' is already superseded by '{old.get('superseded_by')}'"]
        target = replacement_id
        if replacement is not None:
            new = dict(replacement)
            new.setdefault("id", next_entry_id(entries))
            if find_entry(entries, new["id"]):
                return [f"entry '{new['id']}' already exists; pass it with --by instead"]
            entries.append(new)
            target = new["id"]
        if not target or find_entry(entries, target) is None:
            return [f"replacement entry '{target}' does not exist"]
        if target == entry_id:
            return ["an entry cannot supersede itself"]
        old["status"] = "superseded"
        old["superseded_by"] = target
        chosen.append(target)
        return []

    ok, problems, _ = change_entries(domain_dir, change)
    return ok, problems, chosen[0] if chosen else ""


def compact_link(domain_dir: Path, entry_id: str, event_ids: list[str], allow_drop: bool = False) -> tuple[bool, list[str]]:
    with store_lock(domain_dir):
        return _compact_link(domain_dir, entry_id, event_ids, allow_drop)


def _compact_link(
    domain_dir: Path,
    entry_id: str,
    event_ids: list[str],
    allow_drop: bool = False,
) -> tuple[bool, list[str]]:
    """Link an entry to the valid events that support it, then read it back.

    This is deliberately mechanical. It does not write the observation prose —
    consolidating five events into one honest sentence is a judgment, and a
    script that guessed at it would be inventing empirical claims.

    `event_ids` is the entry's complete evidence after the call, not an
    addition to it. That is a reasonable contract and an easy one to misread as
    "add these", so a call that would drop an event already cited is refused
    unless `allow_drop` says the loss is intended. The readback below cannot
    catch this on its own: it compares the stored list against what was passed,
    so it confirms the overwrite rather than noticing what the overwrite
    removed. Dropping a citation is sometimes right — an event later found
    invalid, or attributed to the wrong entry — which is why this is a
    confirmation rather than a prohibition.
    """
    memory = load_memory(domain_dir)
    entries = [e for e in memory.get("entries") or [] if isinstance(e, dict)]
    entry = next((e for e in entries if e.get("id") == entry_id), None)
    if entry is None:
        return False, [f"no entry '{entry_id}' in {domain_dir.name}"]

    events, load_errors = load_events(domain_dir)
    if load_errors:
        return False, load_errors
    by_id = {e.get("event_id"): e for e in events}
    quarantined = {
        str(target)
        for event in events
        if event.get("event_kind") == "evidence_correction"
        and (event.get("corrections") or {}).get("disposition") == "quarantined"
        for target in (event.get("supersedes_events") or [])
    }

    problems: list[str] = []
    for event_id in event_ids:
        event = by_id.get(event_id)
        if event is None:
            problems.append(f"unknown event '{event_id}'")
        elif event.get("validity") == "invalid":
            problems.append(
                f"refusing invalid event '{event_id}' "
                f"({event.get('invalid_reason', 'no reason recorded')})"
            )
        elif event.get("event_kind") in {"metadata_correction", "evidence_correction"}:
            problems.append(
                f"refusing correction '{event_id}'; a correction is not capability evidence"
            )
        elif event_id in quarantined:
            problems.append(
                f"refusing quarantined event '{event_id}'; a superseding evidence correction "
                "removed it from capability evidence"
            )
    if problems:
        return False, problems

    already_cited = [str(e) for e in entry.get("evidence_events") or []]
    dropped = [e for e in already_cited if e not in event_ids]
    if dropped and not allow_drop:
        return False, [
            f"'{entry_id}' already cites {', '.join(dropped)}, which this call would remove: "
            f"pass every event the entry should end up citing, or --replace if the loss is intended"
        ]

    entry["evidence_events"] = list(event_ids)
    entry["evidence_count"] = len(event_ids)
    entry["last_verified"] = date.today()
    memory["memory_version"] = int(memory.get("memory_version", 0)) + 1
    write_memory(domain_dir, memory)

    reread = load_memory(domain_dir)
    fresh = next((e for e in reread.get("entries") or [] if isinstance(e, dict) and e.get("id") == entry_id), None)
    if fresh is None or fresh.get("evidence_events") != list(event_ids):
        return False, [f"readback failed: '{entry_id}' does not carry the expected evidence after write"]
    return True, []


def uncited_valid_events(domain_dir: Path) -> list[str]:
    memory = load_memory(domain_dir)
    cited: set[str] = set()
    for entry in memory.get("entries") or []:
        if isinstance(entry, dict) and isinstance(entry.get("evidence_events"), list):
            cited.update(str(e) for e in entry["evidence_events"])
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
        notes.append(f"{len(uncited)} valid event(s) not yet cited by any entry: {', '.join(uncited[:8])}")
    return notes


# ---------------------------------------------------------------- CLI


def cmd_validate(args: argparse.Namespace) -> int:
    dirs = domain_dirs(args.memory, args.domain)
    if not dirs:
        print(f"No domain memory found under {args.memory.as_posix()}.")
        return 0
    total = 0
    for domain_dir in dirs:
        errors = validate_store(domain_dir)
        for error in errors:
            print(f"{domain_dir.name}: {error}")
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


def cmd_compact(args: argparse.Namespace) -> int:
    dirs = domain_dirs(args.memory, args.domain)
    if args.entry:
        if len(dirs) != 1:
            print("FAIL: linking evidence requires exactly one --domain", file=sys.stderr)
            return 1
        event_ids = [e.strip() for e in (args.events or "").split(",") if e.strip()]
        if not event_ids:
            print("FAIL: --events is required with --entry", file=sys.stderr)
            return 1
        ok, problems = compact_link(dirs[0], args.entry, event_ids, allow_drop=args.replace)
        if not ok:
            for problem in problems:
                print(f"{dirs[0].name}: {problem}", file=sys.stderr)
            print("FAIL: evidence not linked", file=sys.stderr)
            return 1
        print(
            f"PASS: {args.entry} now cites {', '.join(event_ids)} "
            f"({len(event_ids)} event(s)), confirmed on readback"
        )
        return 0
    for domain_dir in dirs:
        uncited = uncited_valid_events(domain_dir)
        if uncited:
            print(f"{domain_dir.name}: {len(uncited)} valid event(s) awaiting consolidation:")
            for event_id in uncited:
                print(f"    {event_id}")
        else:
            print(f"{domain_dir.name}: no valid events awaiting consolidation")
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


def cmd_entry(args: argparse.Namespace) -> int:
    dirs = domain_dirs(args.memory, args.domain)
    if not args.domain or len(dirs) != 1:
        print("FAIL: entry commands require exactly one --domain", file=sys.stderr)
        return 1
    domain_dir = dirs[0]
    if args.action == "show":
        entry = find_entry(load_memory(domain_dir).get("entries") or [], args.id)
        if entry is None:
            print(f"FAIL: no entry '{args.id}'", file=sys.stderr)
            return 1
        print(yaml.safe_dump(entry, sort_keys=False, allow_unicode=True, width=88), end="")
        return 0
    data = read_json_argument(args.json)
    if args.action == "add":
        ok, problems, entry_id = add_entry(domain_dir, data)
        done = f"added {entry_id}"
    elif args.action == "update":
        ok, problems = update_entry(domain_dir, args.id, data)
        done = f"updated {args.id}"
    else:
        if (args.by is None) == (data is None):
            print("FAIL: supersede needs exactly one of --by <existing id> or --json <new entry>", file=sys.stderr)
            return 1
        ok, problems, entry_id = supersede_entry(domain_dir, args.id, args.by, data)
        done = f"{args.id} superseded by {entry_id}"
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

    compact = sub.add_parser("compact", parents=[common], help="Report or link the evidence behind an entry.")
    compact.add_argument("--entry", default=None)
    compact.add_argument("--events", default=None, help="Comma-separated event ids.")
    compact.add_argument(
        "--replace",
        action="store_true",
        help="Confirm that events the entry already cites and --events omits should be dropped.",
    )

    review = sub.add_parser("review", parents=[common], help="List entries that need revalidation.")
    review.add_argument("--library", type=Path, default=default_library_root())

    entry = sub.add_parser(
        "entry",
        help="Add, update, supersede or show one skill_memory.yaml entry; the supported way to change entries.",
        description=(
            "Every write validates the whole resulting store first, replaces the file atomically "
            "under a per-domain lock, and confirms it on readback; a refused write changes nothing. "
            "There is no delete: evidence is never deleted, so retire an entry by status "
            "(resolved, obsolete) or supersede it."
        ),
    )
    actions = entry.add_subparsers(dest="action", required=True)
    add = actions.add_parser("add", parents=[common], help="Add an entry; the id is assigned when omitted.")
    add.add_argument("--json", required=True, help="Path to, or literal, JSON entry.")
    update = actions.add_parser("update", parents=[common], help="Merge fields into an entry; null removes an optional key.")
    update.add_argument("--id", required=True)
    update.add_argument("--json", required=True, help="Path to, or literal, JSON object of changed fields.")
    supersede = actions.add_parser("supersede", parents=[common], help="Retire an entry in favour of a replacement.")
    supersede.add_argument("--id", required=True)
    supersede.add_argument("--by", default=None, help="An existing replacement entry id.")
    supersede.add_argument("--json", default=None, help="A new replacement entry, added in the same write.")
    show = actions.add_parser("show", parents=[common], help="Print one entry, whatever its status.")
    show.add_argument("--id", required=True)

    args = parser.parse_args()
    handlers = {
        "validate": cmd_validate, "query": cmd_query, "append": cmd_append,
        "compact": cmd_compact, "review": cmd_review, "entry": cmd_entry,
    }
    try:
        return handlers[args.command](args)
    except MemoryError_ as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
