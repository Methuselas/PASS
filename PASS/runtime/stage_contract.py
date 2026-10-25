#!/usr/bin/env python3
"""Stage Contract v1: the closed model-facing interface for PASS stages.

    free-form model cognition
        -> closed stage output contract
        -> deterministic host validation/rendering

A supported model -- GPT, Codex, Claude, MiMo, a small local model -- may reason
differently and may reach different semantic conclusions. It may not invent a
different output format, rename a field or disposition, choose a filename or a
path, or emit a model-specific structure.

This module owns the host side of that boundary and nothing else. It holds no
pedagogy: Source Prep, Preflight, PASS 1/2/3 and the
NEW/REFINE/REINFORCE/REJECT vocabulary are unchanged, and the canonical card
schema in ``PASS/docs/PASS_SCHEMA.md`` remains the authority for what a finished
card is. What changes here is only how a model hands work to the host.

Three things live here:

* **Enums and payload schemas** for each stage, declared once so no model has to
  infer a vocabulary from an example.
* **The structured card body contract** per object type, plus a deterministic
  renderer. The model supplies semantic content; the host owns headings, heading
  order, section order, IF/THEN/ELSE labels, list markers, indentation,
  whitespace and the final Markdown.
* **Structured validation failures**, so a weak model can repair a malformed
  response without redoing semantic reasoning and without reading PASS source.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import PurePosixPath
import re
from typing import Any, Iterable

CONTRACT_VERSION = 1

# --------------------------------------------------------------------- enums

OBJECT_TYPES = ("pattern", "ap", "drill")
# These reproduce vocabularies the preflight parser already owns. They are
# duplicated rather than imported to keep this module dependency-free, and a test
# asserts the two never drift apart.
CARD_POTENTIAL = ("low", "medium", "high", "mixed")
CONFIDENCE = ("low", "medium", "high")
LANE_FIT = ("teach", "skill", "both")
FOUNDATION_ROLE = ("foundation", "specialization")
ROUTING_CLASS = ("general", "specialized", "teaching")
SPECIALIZATION_AXIS = (
    "none", "language", "tool", "framework", "medium", "style", "genre",
    "tradition", "source", "method", "domain",
)
MODERNIZATION_DISPOSITIONS = ("current", "modernized", "historical", "rejected")
LANDING_BASIS = ("evidence", "user approval")

# The disposition vocabulary is PASS pedagogy and is reproduced, never redefined.
BUCKETS = (
    "NEW_PATTERNS", "REFINE", "REINFORCE", "VARIANTS", "REPLACE",
    "NEW_APS", "NEW_DRILLS", "REJECT",
)
TAXONOMY = ("NEW_SUBCATEGORY", "MOVE", "RENAME", "MERGE")

OBJECT_ID_RE = re.compile(r"^(?:PAT|DRILL|AP)_[a-z0-9][a-z0-9_]*$")
PATH_SEGMENT_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
FLAG_RE = re.compile(r"^[a-z][a-z0-9_]*$")
UNIT_ID_RE = re.compile(r"^u[0-9]{2,3}$")
ACTION_ID_RE = re.compile(r"^[0-9a-f]{64}$")

ID_PREFIX = {"pattern": "PAT_", "ap": "AP_", "drill": "DRILL_"}


# ------------------------------------------------------- structured failures


@dataclass(frozen=True)
class Failure:
    """One machine-readable reason a stage response was refused.

    ``path`` is a JSON pointer-ish locator into the payload so a model can find
    the field without guessing, and ``code`` is a closed vocabulary so a repair
    can be mechanical.
    """

    path: str
    code: str
    message: str
    expected: Any = None
    got: Any = None

    def as_dict(self) -> dict:
        record = {"path": self.path, "code": self.code, "message": self.message}
        if self.expected is not None:
            record["expected"] = self.expected
        if self.got is not None:
            record["got"] = self.got
        return record


FAILURE_CODES = (
    "missing_field",
    "unknown_field",
    "wrong_type",
    "illegal_enum",
    "invalid_object_type_body",
    "unresolved_object_id",
    "stale_action_id",
    "duplicate_value",
    "invalid_identifier",
    "empty_value",
)


class Rejected(Exception):
    """A stage response failed the closed contract. Carries every failure."""

    def __init__(self, failures: list[Failure]):
        self.failures = failures
        super().__init__(f"{len(failures)} contract failure(s)")


@dataclass
class Collector:
    """Accumulates failures so one rejection reports every problem at once.

    Reporting one error per attempt would burn the single correction attempt on
    the first of several defects.
    """

    failures: list[Failure] = field(default_factory=list)

    def add(self, path: str, code: str, message: str, expected: Any = None, got: Any = None) -> None:
        self.failures.append(Failure(path, code, message, expected, got))

    def ok(self) -> bool:
        return not self.failures

    def raise_if_failed(self) -> None:
        if self.failures:
            raise Rejected(self.failures)


# ------------------------------------------------------ primitive validators


def _text(value: Any, path: str, out: Collector) -> str:
    if not isinstance(value, str):
        out.add(path, "wrong_type", "expected a string", "string", type(value).__name__)
        return ""
    if not value.strip():
        out.add(path, "empty_value", "expected non-empty text")
        return ""
    return value.strip()


def _bool(value: Any, path: str, out: Collector) -> bool:
    if type(value) is not bool:
        out.add(path, "wrong_type", "expected true or false", "boolean", type(value).__name__)
        return False
    return value


def _list(value: Any, path: str, out: Collector) -> list:
    if not isinstance(value, list):
        out.add(path, "wrong_type", "expected a list (use [] for none)", "list", type(value).__name__)
        return []
    return value


def _mapping(value: Any, path: str, out: Collector) -> dict:
    if not isinstance(value, dict):
        out.add(path, "wrong_type", "expected an object", "object", type(value).__name__)
        return {}
    return value


def _enum(value: Any, allowed: Iterable[str], path: str, out: Collector) -> str:
    options = list(allowed)
    if not isinstance(value, str) or value not in options:
        out.add(path, "illegal_enum", "value is outside the declared vocabulary", options, value)
        return ""
    return value


def _keys(data: Any, required: Iterable[str], path: str, out: Collector,
          optional: Iterable[str] = ()) -> dict:
    """Closed key set: a missing field and an invented field are both refused."""
    mapping = _mapping(data, path, out)
    if not mapping and not isinstance(data, dict):
        return {}
    required = set(required)
    allowed = required | set(optional)
    for name in sorted(required - set(mapping)):
        out.add(f"{path}.{name}" if path else name, "missing_field", "required field is absent")
    for name in sorted(set(mapping) - allowed):
        out.add(f"{path}.{name}" if path else name, "unknown_field",
                "field is not part of this stage contract", sorted(allowed))
    return mapping


# -------------------------------------------------- structured card contract
#
# Section names and their order are exactly the canonical body contract that
# PASS/tools/validate.py enforces (rule 6). They are reproduced here because the
# host now *renders* them rather than only checking them; if the two ever
# disagree, the schema and validator win and this table is the bug.

PROSE = "prose"
BULLETS = "bullets"
STEPS = "steps"
RULE = "rule"
BLOCKS = "blocks"

CARD_BODY: dict[str, tuple[tuple[str, str], ...]] = {
    "pattern": (
        ("Pattern Rule", RULE),
        ("Do", BULLETS),
        ("Don't", BULLETS),
        ("Checklist", BULLETS),
        ("Notes", BLOCKS),
    ),
    "ap": (
        ("Objective", PROSE),
        ("Steps / Flow", STEPS),
        ("Notes", BLOCKS),
    ),
    "drill": (
        ("Practice Task", PROSE),
        ("Target Skill", PROSE),
        ("Setup", PROSE),
        ("Instructions", STEPS),
        ("Success Check", BULLETS),
        ("Common Failures", BULLETS),
        ("Notes", BLOCKS),
    ),
}

# A section key is the heading lowercased with non-alphanumerics collapsed, so a
# model never has to reproduce "Steps / Flow" or an apostrophe exactly.
def section_key(heading: str) -> str:
    # Apostrophes are dropped rather than collapsed, so "Don't" keys as "dont"
    # and a model never has to reproduce punctuation.
    return re.sub(r"[^a-z0-9]+", "_", heading.lower().replace("'", "")).strip("_")


SECTION_KEYS = {
    object_type: tuple((section_key(heading), heading, kind) for heading, kind in sections)
    for object_type, sections in CARD_BODY.items()
}

BLOCK_TYPES = ("paragraph", "bullets", "code")


def _item(value: Any, path: str, out: Collector) -> dict:
    """A list item: required text plus optional nested bullets.

    Nesting exists because the canonical bodies genuinely use it; the host still
    owns the marker and the indentation.
    """
    if isinstance(value, str):
        return {"text": _text(value, path, out), "children": []}
    mapping = _keys(value, {"text"}, path, out, optional={"children"})
    text = _text(mapping.get("text"), f"{path}.text", out)
    children = []
    for index, child in enumerate(_list(mapping.get("children", []), f"{path}.children", out)):
        children.append(_text(child, f"{path}.children[{index}]", out))
    return {"text": text, "children": children}


def _validate_section(kind: str, value: Any, path: str, out: Collector) -> Any:
    if kind == PROSE:
        return _text(value, path, out)
    if kind == RULE:
        mapping = _keys(value, {"if", "then"}, path, out, optional={"else"})
        rule = {
            "if": _text(mapping.get("if"), f"{path}.if", out),
            "then": _text(mapping.get("then"), f"{path}.then", out),
        }
        if mapping.get("else") not in (None, ""):
            rule["else"] = _text(mapping.get("else"), f"{path}.else", out)
        return rule
    if kind in (BULLETS, STEPS):
        items = _list(value, path, out)
        if not items:
            out.add(path, "empty_value", "expected at least one item")
        return [_item(item, f"{path}[{index}]", out) for index, item in enumerate(items)]
    if kind == BLOCKS:
        blocks = _list(value, path, out)
        if not blocks:
            out.add(path, "empty_value", "expected at least one block")
        result = []
        for index, raw in enumerate(blocks):
            here = f"{path}[{index}]"
            if isinstance(raw, str):
                result.append({"type": "paragraph", "text": _text(raw, here, out)})
                continue
            mapping = _mapping(raw, here, out)
            block_type = _enum(mapping.get("type"), BLOCK_TYPES, f"{here}.type", out)
            if block_type == "paragraph":
                _keys(mapping, {"type", "text"}, here, out)
                result.append({"type": "paragraph", "text": _text(mapping.get("text"), f"{here}.text", out)})
            elif block_type == "bullets":
                _keys(mapping, {"type", "items"}, here, out)
                items = _list(mapping.get("items"), f"{here}.items", out)
                result.append({"type": "bullets",
                               "items": [_item(i, f"{here}.items[{n}]", out) for n, i in enumerate(items)]})
            elif block_type == "code":
                mapping = _keys(mapping, {"type", "text"}, here, out, optional={"language"})
                result.append({"type": "code",
                               "language": mapping.get("language") or "",
                               "text": mapping.get("text") if isinstance(mapping.get("text"), str) else ""})
        return result
    raise AssertionError(f"unknown section kind: {kind}")


def validate_card_body(object_type: str, body: Any, path: str, out: Collector) -> dict:
    """Validate a structured body against its object type's closed contract."""
    if object_type not in CARD_BODY:
        out.add(path, "invalid_object_type_body", "no body contract for this object type",
                list(CARD_BODY), object_type)
        return {}
    spec = SECTION_KEYS[object_type]
    mapping = _keys(body, {key for key, _, _ in spec}, path, out)
    result = {}
    for key, _heading, kind in spec:
        if key in mapping:
            result[key] = _validate_section(kind, mapping[key], f"{path}.{key}", out)
    return result


# ------------------------------------------------------------- card renderer


def _render_items(items: list[dict], ordered: bool) -> list[str]:
    """One line per item, host-owned markers and indentation.

    A child of a numbered step is indented three spaces and a child of a bullet
    two, which is both correct Markdown nesting and what the canonical bodies
    already use.
    """
    lines = []
    indent = "   " if ordered else "  "
    for index, item in enumerate(items, start=1):
        marker = f"{index}." if ordered else "-"
        lines.append(f"{marker} {item['text']}")
        for child in item.get("children", []):
            lines.append(f"{indent}- {child}")
    return lines


def render_card_body(object_type: str, body: dict) -> str:
    """Render a validated structured body to canonical Markdown, deterministically.

    Every structural character here is host-owned: the headings, their order, the
    IF/THEN/ELSE labels, the list markers, the nesting indent and the blank lines.
    Equivalent payloads therefore render byte-identically regardless of which
    model produced them.
    """
    chunks: list[str] = []
    for key, heading, kind in SECTION_KEYS[object_type]:
        value = body.get(key)
        lines = [f"## {heading}"]
        if kind == PROSE:
            lines.append(str(value))
        elif kind == RULE:
            lines.append(f"**IF** {value['if']}")
            lines.append(f"**THEN** {value['then']}")
            if value.get("else"):
                lines.append(f"**ELSE** {value['else']}")
        elif kind in (BULLETS, STEPS):
            lines.extend(_render_items(value, ordered=kind == STEPS))
        elif kind == BLOCKS:
            rendered: list[str] = []
            for block in value:
                if rendered:
                    rendered.append("")
                if block["type"] == "paragraph":
                    rendered.append(block["text"])
                elif block["type"] == "bullets":
                    rendered.extend(_render_items(block["items"], ordered=False))
                elif block["type"] == "code":
                    rendered.append(f"```{block['language']}".rstrip())
                    rendered.extend(block["text"].rstrip("\n").split("\n"))
                    rendered.append("```")
            lines.extend(rendered)
        chunks.append("\n".join(lines))
    return "\n\n".join(chunks)


def render_card(object_type: str, name: str, frontmatter_yaml: str, body: dict) -> str:
    """The complete card file: frontmatter, H1 equal to name, then the body."""
    front = frontmatter_yaml.strip("\n")
    return f"---\n{front}\n---\n\n# {name}\n\n{render_card_body(object_type, body)}\n"


ARTIFACT_KINDS = ("recipe", "module", "asset")
ASSET_SUFFIXES = (".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", ".json")
RECIPE_NAME_RE = re.compile(r"^SkillForge_[A-Za-z_]+$")
ASSET_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


def validate_artifact(artifact: Any, domain: str, path: str, out: Collector) -> dict:
    """Validate one non-card staged artifact and keep its path host-derived."""
    mapping = _mapping(artifact, path, out)
    kind = _enum(mapping.get("kind"), ARTIFACT_KINDS, f"{path}.kind", out)
    if kind == "recipe":
        fields = _keys(mapping, {"kind", "recipe", "modules"}, path, out)
        name = fields.get("recipe")
        if not isinstance(name, str) or not RECIPE_NAME_RE.fullmatch(name):
            out.add(f"{path}.recipe", "invalid_identifier",
                    "name the owned release recipe, without a path or extension",
                    RECIPE_NAME_RE.pattern, name)
            name = ""
        modules = [m for m in _list(fields.get("modules"), f"{path}.modules", out)
                   if isinstance(m, str)]
        return {"kind": kind, "recipe": name, "modules": modules}
    if kind == "module":
        fields = _keys(mapping, {"kind", "library_path", "requires"}, path, out)
        segments = _library_path(fields.get("library_path"), domain, f"{path}.library_path", out)
        requires = [m for m in _list(fields.get("requires"), f"{path}.requires", out)
                    if isinstance(m, str)]
        return {"kind": kind, "library_path": segments, "requires": requires}
    if kind == "asset":
        fields = _keys(mapping, {"kind", "library_path", "filename"}, path, out)
        segments = _library_path(fields.get("library_path"), domain, f"{path}.library_path", out)
        filename = fields.get("filename")
        if not isinstance(filename, str) or not ASSET_NAME_RE.fullmatch(filename):
            out.add(f"{path}.filename", "invalid_identifier",
                    "an asset leaf name only; the host owns the directory",
                    ASSET_NAME_RE.pattern, filename)
            filename = ""
        elif PurePosixPath(filename).suffix.lower() not in ASSET_SUFFIXES:
            out.add(f"{path}.filename", "illegal_enum", "unsupported asset type",
                    list(ASSET_SUFFIXES), PurePosixPath(filename).suffix)
        return {"kind": kind, "library_path": segments, "filename": filename}
    return {"kind": kind}


def _library_path(value: Any, domain: str, path: str, out: Collector) -> list[str]:
    segments = _list(value, path, out)
    clean: list[str] = []
    for index, segment in enumerate(segments):
        if not isinstance(segment, str) or not PATH_SEGMENT_RE.fullmatch(segment):
            out.add(f"{path}[{index}]", "invalid_identifier",
                    "library_path segments must be lowercase library slugs",
                    PATH_SEGMENT_RE.pattern, segment)
        else:
            clean.append(segment)
    if not clean:
        out.add(path, "empty_value", "library_path is required")
    elif clean[0] != domain:
        out.add(f"{path}[0]", "illegal_enum",
                "library_path must start with the run's authorized domain", [domain], clean[0])
    return clean


# ------------------------------------------------------------ path ownership


def card_path(domain: str, library_path: list[str], object_id: str) -> str:
    """The one place a card's repository path is decided.

    Derived from the model's two semantic fields and nothing else. The audit
    behind Stage Contract v1 verified this is lossless: across all 2,388 cards in
    the library, object_id equals the filename stem and library_path equals the
    directory, with no exceptions. A model never names a file or a directory.
    """
    if not library_path or library_path[0] != domain:
        raise ValueError(f"library_path must start with the run's domain: {domain}")
    segments = "/".join(library_path)
    return f"library/{segments}/{object_id}.md"


# ------------------------------------------------------- stage payload specs
#
# One authoritative declaration per stage. ``template`` skeletons and the JSON
# Schema are both generated from this table, so a model never has to decide
# whether "", false or [] is a literal value, a default or a placeholder: the
# schema says which fields are required and what they may contain, and the
# skeleton is only a convenience derived from it.


@dataclass(frozen=True)
class Field:
    name: str
    kind: str                      # text | bool | list | map | cards
    required: bool = True
    enum: tuple[str, ...] | None = None
    item_keys: tuple[str, ...] | None = None
    note: str = ""


# PASS pedagogy is unchanged; only the serialized interface is closed here.
STAGE_FIELDS: dict[str, tuple[Field, ...]] = {
    "preflight": (
        Field("title", "text", note="the title the source gives itself"),
        Field("author", "text", note="author or source credit"),
        Field("extent", "text", note="how much source there is"),
        # Free text upstream, so the contract does not invent a vocabulary for it.
        Field("text_quality", "text"),
        Field("subject", "text",
              note="what the instructional body teaches the practitioner to do"),
        # overlap_object_ids stays: it is validated against the library, printed in
        # the human-facing preflight packet, and counted in the verification
        # summary. Only PASS 1's same-named field is retired in v1.
        Field("units", "list", item_keys=("unit_id", "material", "locator", "source_pages",
                                          "printed_pages", "overlap_object_ids",
                                          "card_potential")),
        Field("no_extract", "list", required=False, note="regions deliberately not mined"),
        Field("language_policy", "map", required=False,
              note="required only when the domain declares a programming-language policy"),
    ),
    "pass1": (
        Field("full_read", "bool", note="the entire bounded unit was read"),
        Field("cards", "cards", note="drafted cards; the host owns their filenames and paths"),
        Field("secondary_subject_flags", "list", item_keys=("flag_id", "subject")),
        Field("questions", "list", item_keys=("question_id", "question")),
        Field("version_sensitive_flags", "list", required=False,
              item_keys=("flag_id", "source_claim", "reason")),
    ),
    "checkpoint": (
        Field("answers", "list", item_keys=("question_id", "resolution")),
    ),
    "pass2": (
        Field("full_reread", "bool", note="a complete cold reread of the same unit"),
        Field("flag_resolutions", "list", item_keys=("flag_id", "reason")),
        Field("buckets", "map", enum=BUCKETS, item_keys=("object_id", "reason")),
        Field("taxonomy", "map", enum=TAXONOMY, item_keys=("library_path", "reason")),
        Field("cards", "cards", required=False,
              note="cards created or refined by this pass"),
        Field("artifacts", "list", required=False,
              note="non-card staged items: an owned recipe, a MODULE.yaml, or an asset"),
        Field("removals", "list", required=False, note="object_ids to retire"),
        Field("approval_required", "bool"),
        Field("owner_reconciliation", "list", required=False),
        Field("metadata_classification", "list", required=False),
        Field("language_modernization", "map", required=False),
    ),
    "pass3": (
        Field("card_only_review", "bool",
              note="reviewed the cards themselves, source and reading notes closed"),
        Field("checks", "map", note="every declared semantic check, each true or false"),
    ),
}

# Closure stages reuse their PASS 2/3 payloads plus the closure audit block.
CLOSURE_AUDITS = ("ap_synthesis", "drill_synthesis", "cross_library_reconciliation",
                  "metadata_classification")

STAGES = ("preflight", "pass1", "checkpoint", "pass2", "pass3",
          "closure_pass2", "closure_pass3")


def stage_fields(stage: str) -> tuple[Field, ...]:
    if stage == "closure_pass2":
        # Source-wide synthesis, not a unit reread: there is no full_reread and
        # no PASS 1 flag set to resolve at closure.
        dropped = {"full_reread", "flag_resolutions"}
        return tuple(spec for spec in STAGE_FIELDS["pass2"] if spec.name not in dropped) + (
            Field("closure_audits", "map", enum=CLOSURE_AUDITS),)
    if stage == "closure_pass3":
        return STAGE_FIELDS["pass3"]
    if stage not in STAGE_FIELDS:
        raise ValueError(f"no stage contract for {stage}")
    return STAGE_FIELDS[stage]


def skeleton(stage: str, semantic_checks: Iterable[str] = (),
             include_optional: Iterable[str] = ()) -> dict:
    """A fillable payload skeleton generated from the schema, never hand-written."""
    optional = set(include_optional)
    payload: dict[str, Any] = {}
    for spec in stage_fields(stage):
        if not spec.required and spec.name not in optional:
            continue
        if spec.kind == "bool":
            payload[spec.name] = False
        elif spec.kind == "text":
            payload[spec.name] = ""
        elif spec.kind in ("list", "cards"):
            payload[spec.name] = []
        elif spec.kind == "map":
            if spec.name == "checks":
                payload[spec.name] = {name: False for name in semantic_checks}
            elif spec.name == "closure_audits":
                payload[spec.name] = {name: False for name in spec.enum or ()}
            elif spec.enum:
                payload[spec.name] = {name: [] for name in spec.enum}
            else:
                payload[spec.name] = {}
    return payload


def card_skeleton(object_type: str) -> dict:
    """The structured shape of one drafted card, for the model to fill."""
    body: dict[str, Any] = {}
    for key, _heading, kind in SECTION_KEYS[object_type]:
        if kind == PROSE:
            body[key] = ""
        elif kind == RULE:
            body[key] = {"if": "", "then": ""}
        elif kind in (BULLETS, STEPS):
            body[key] = [{"text": ""}]
        elif kind == BLOCKS:
            body[key] = [{"type": "paragraph", "text": ""}]
    return {"object_id": "", "object_type": object_type, "library_path": [],
            "name": "", "frontmatter": {}, "body": body}


def json_schema(stage: str, semantic_checks: Iterable[str] = ()) -> dict:
    """A machine-readable schema for the stage envelope, for structured output."""
    properties: dict[str, Any] = {}
    required: list[str] = []
    for spec in stage_fields(stage):
        node: dict[str, Any] = {}
        if spec.kind == "bool":
            node = {"type": "boolean"}
        elif spec.kind == "text":
            node = ({"type": "string", "enum": list(spec.enum)} if spec.enum
                    else {"type": "string", "minLength": 1})
        elif spec.kind == "list":
            item: dict[str, Any] = {"type": "object"}
            if spec.name == "removals":
                # A removal names a live object_id, never a path: the runtime
                # validator accepts strings only, so the schema declares the
                # same language. Schema and validator must not disagree.
                item = {"type": "string", "pattern": OBJECT_ID_RE.pattern}
            elif spec.item_keys:
                item = {"type": "object", "required": list(spec.item_keys),
                        "additionalProperties": False,
                        "properties": {key: {} for key in spec.item_keys}}
            node = {"type": "array", "items": item}
        elif spec.kind == "cards":
            node = {"type": "array", "items": {"$ref": "#/$defs/card"}}
        elif spec.kind == "map":
            if spec.name == "checks":
                node = {"type": "object", "additionalProperties": False,
                        "required": list(semantic_checks),
                        "properties": {name: {"type": "boolean"} for name in semantic_checks}}
            elif spec.enum:
                node = {"type": "object", "additionalProperties": False,
                        "required": list(spec.enum),
                        "properties": {name: {} for name in spec.enum}}
            else:
                node = {"type": "object"}
        if spec.note:
            node["description"] = spec.note
        properties[spec.name] = node
        if spec.required:
            required.append(spec.name)
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": f"PASS Stage Contract v{CONTRACT_VERSION}: {stage}",
        "type": "object",
        "additionalProperties": False,
        "required": ["action_id", "payload"],
        "properties": {
            "action_id": {
                "type": "string", "pattern": ACTION_ID_RE.pattern,
                "description": "echo the host-issued token exactly; the host owns run, unit "
                               "and stage identity",
            },
            "payload": {"type": "object", "additionalProperties": False,
                        "required": required, "properties": properties},
        },
        "$defs": {"card": card_json_schema()},
    }


def card_json_schema() -> dict:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["object_id", "object_type", "library_path", "name", "frontmatter", "body"],
        "properties": {
            "object_id": {"type": "string", "pattern": OBJECT_ID_RE.pattern},
            "object_type": {"type": "string", "enum": list(OBJECT_TYPES)},
            "library_path": {
                "type": "array", "minItems": 2,
                "items": {"type": "string", "pattern": PATH_SEGMENT_RE.pattern},
                "description": "the host derives the filename and path from object_id "
                               "and library_path; a model never names a file",
            },
            "name": {"type": "string", "minLength": 1},
            "frontmatter": {"type": "object"},
            "body": {
                "type": "object",
                "description": "object-type-specific closed body; the host renders every "
                               "heading, label, marker and whitespace character",
            },
        },
    }


# ------------------------------------------------------------------ envelope


def unwrap_envelope(data: Any, expected_action_id: str) -> dict:
    """Split the response into its binding token and its payload.

    The model echoes one opaque token and nothing else about identity. Run id,
    unit id, stage name, state hashes, filenames and paths stay host-owned, so a
    stale or cross-unit response is refused here rather than being validated as
    if it belonged to the pending action.
    """
    out = Collector()
    mapping = _keys(data, {"action_id", "payload"}, "", out)
    out.raise_if_failed()
    token = mapping.get("action_id")
    if not isinstance(token, str) or not ACTION_ID_RE.fullmatch(token):
        raise Rejected([Failure("action_id", "invalid_identifier",
                                "action_id must be the host-issued 64-character token",
                                expected_action_id, token)])
    if token != expected_action_id:
        raise Rejected([Failure("action_id", "stale_action_id",
                                "this response belongs to a different pending action; request "
                                "the current action and resubmit",
                                expected_action_id, token)])
    payload = mapping.get("payload")
    if not isinstance(payload, dict):
        raise Rejected([Failure("payload", "wrong_type", "payload must be an object",
                                "object", type(payload).__name__)])
    return payload


# ------------------------------------------------------------- card validation


def validate_card(card: Any, domain: str, path: str, out: Collector) -> dict:
    """Validate one drafted card and derive its host-owned repository path."""
    mapping = _keys(card, {"object_id", "object_type", "library_path", "name",
                           "frontmatter", "body"}, path, out)
    object_type = _enum(mapping.get("object_type"), OBJECT_TYPES, f"{path}.object_type", out)
    object_id = mapping.get("object_id")
    if not isinstance(object_id, str) or not OBJECT_ID_RE.fullmatch(object_id):
        out.add(f"{path}.object_id", "invalid_identifier",
                "object_id must match the canonical identifier shape",
                OBJECT_ID_RE.pattern, object_id)
        object_id = ""
    elif object_type and not object_id.startswith(ID_PREFIX[object_type]):
        out.add(f"{path}.object_id", "invalid_identifier",
                "object_id prefix does not match object_type",
                ID_PREFIX[object_type], object_id)
    segments = _list(mapping.get("library_path"), f"{path}.library_path", out)
    clean: list[str] = []
    for index, segment in enumerate(segments):
        if not isinstance(segment, str) or not PATH_SEGMENT_RE.fullmatch(segment):
            out.add(f"{path}.library_path[{index}]", "invalid_identifier",
                    "library_path segments must be lowercase library slugs",
                    PATH_SEGMENT_RE.pattern, segment)
        else:
            clean.append(segment)
    if len(clean) < 2:
        out.add(f"{path}.library_path", "wrong_type",
                "library_path needs at least the domain and one category", "2+ segments", clean)
    elif clean[0] != domain:
        out.add(f"{path}.library_path[0]", "illegal_enum",
                "library_path must start with the run's authorized domain", [domain], clean[0])
    name = _text(mapping.get("name"), f"{path}.name", out)
    frontmatter = _mapping(mapping.get("frontmatter"), f"{path}.frontmatter", out)
    body = validate_card_body(object_type, mapping.get("body"), f"{path}.body", out) if object_type else {}
    return {"object_id": object_id, "object_type": object_type, "library_path": clean,
            "name": name, "frontmatter": frontmatter, "body": body}
