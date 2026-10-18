#!/usr/bin/env python3
"""Migration-input reader for v1/v2 Skillset Memory stores: no runtime path may
grow a dependency on it, and ticket T21 deletes this module once every domain
store has migrated to schema 3.

Everything here is the claim side of the legacy `memory.py` validator, moved
verbatim by T04: the v1/v2 entry vocabularies, `validate_entry`, and the whole
store-level check from file-level keys through evidence admissibility. It is a
reader for migration and mixed-state validation only — the dispatch inside
`PASS/tools/memory.py` is its sole importer (the migrator of T13 becomes the
second), which `tests/test_memory.py::SchemaDispatch` enforces as text. It must
never be re-exported, wrapped, or reached from `entry`, `query`, `append`,
`compact`, `review`, or any other command.

Shared names come from `memory` rather than being duplicated: the semantic
ladder (`CONFIDENCE_VALUES`), the failure layers, the forbidden legacy
vocabulary, the date/id shapes, `ENTRY_REQUIRED` (which stays in `memory.py`
because the runtime write path reads it), and the one admissibility
implementation both claim sides call. The event path — `validate_event`, its
constants, duplicate event ids, correction ordering — stays in `memory.py`,
because Training History is not versioned (R2.5 §8.4) and validates for every
store version.
"""

from __future__ import annotations

from datetime import date
from typing import Any

from memory import (
    CONFIDENCE_VALUES,
    DATE_RE,
    ENTRY_REQUIRED,
    FAILURE_LAYERS,
    FORBIDDEN_KEYS,
    ID_RE,
    NON_SELF_CONTAINED_PHRASES,
    STAGE_RESULTS,
    SUPPORTED_SCHEMA_VERSIONS,
    evidence_admissibility_problem,
    quarantined_event_ids,
)

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
STATUS_VALUES = {"active", "monitoring", "resolved", "superseded", "obsolete"}
EVIDENCE_ORIGINS = {
    "runtime_self_audit", "user_feedback", "human_teaching", "training_benchmark",
    "regression_failure", "book_close_training", "cross_model_test",
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


def validate_legacy_contents(
    domain: str,
    memory: dict[str, Any],
    events: list[dict[str, Any]],
) -> list[str]:
    """The claim side of one v1/v2 store, as plain errors.

    Verbatim from the pre-T04 `validate_contents`: file-level keys, the version
    guard, the v1/v2 entry-type rule, `validate_entry` over every entry,
    duplicate ids, `superseded_by` resolution, and evidence admissibility — the
    last through the shared `evidence_admissibility_problem`, field
    `evidence_events`, so the legacy and v3 paths cannot drift apart. The event
    path (parse errors, `validate_event`, duplicate event ids, correction
    ordering) stays in `memory.py` and runs for every store version after this
    returns.
    """
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

    by_event_id = {e["event_id"]: e for e in events if isinstance(e.get("event_id"), str)}
    quarantined = quarantined_event_ids(events)
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
            problem = evidence_admissibility_problem(
                label, "evidence_events", event_id, by_event_id.get(event_id), quarantined,
            )
            if problem:
                errors.append(problem)
        count = entry.get("evidence_count")
        if isinstance(count, int) and not isinstance(count, bool) and cited and count != len(cited):
            errors.append(f"{label}: evidence_count {count} does not match {len(cited)} cited evidence_events")

    return errors
