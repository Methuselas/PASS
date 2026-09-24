#!/usr/bin/env python3
"""Stateless preflight parsing and live-domain overlap validation.

PASS/pass.py owns ordinary source-authoring progression and reuses this helper.
The standalone preflight command validates a forecast only; it never authorizes
source ingestion, advances a run, or writes research state.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

try:
    import yaml
except ImportError as exc:  # pragma: no cover - environment contract
    raise SystemExit("PyYAML is required; install PASS/requirements.txt") from exc


SCHEMA_VERSION = 2
SUPPORTED_SCHEMA_VERSIONS = {1, 2}
PHASE = "preflight"
MODES = {"unit ingestion", "curriculum audit"}
CARD_POTENTIALS = {"low", "medium", "high", "mixed"}
OBJECT_ID_RE = re.compile(r"^(?:PAT|DRILL|AP)_[a-z0-9_]+$")
UNIT_ID_RE = re.compile(r"^u(\d{2,})$")
DOMAIN_RE = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")


class PreflightError(ValueError):
    """Raised when a preflight record cannot pass the gate."""


@dataclass(frozen=True)
class CardRef:
    object_id: str
    name: str
    path: Path


@dataclass(frozen=True)
class PageSpan:
    start: int
    end: int


@dataclass(frozen=True)
class PreflightUnit:
    unit_id: str
    material: str
    locator: str
    source_pages: PageSpan | None
    printed_pages: str | None
    overlap_object_ids: tuple[str, ...]
    card_potential: str


@dataclass(frozen=True)
class NoExtractSpan:
    material: str
    locator: str


@dataclass(frozen=True)
class PreflightRecord:
    schema_version: int
    phase: str
    title: str
    author: str
    domain: str
    extent: str
    text_quality: str
    subject: str
    mode: str
    units: tuple[PreflightUnit, ...]
    no_extract: tuple[NoExtractSpan, ...]


TOP_LEVEL_KEYS = {
    "schema_version",
    "phase",
    "title",
    "author",
    "domain",
    "extent",
    "text_quality",
    "subject",
    "mode",
    "units",
    "no_extract",
}
UNIT_KEYS_V1 = {
    "unit_id",
    "material",
    "locator",
    "overlap_object_ids",
    "card_potential",
}
UNIT_KEYS_V2 = UNIT_KEYS_V1 | {"source_pages", "printed_pages"}
NO_EXTRACT_KEYS = {"material", "locator"}


def _require_exact_keys(obj: dict[str, Any], expected: set[str], where: str) -> None:
    actual = set(obj)
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    if missing or extra:
        parts: list[str] = []
        if missing:
            parts.append("missing " + ", ".join(missing))
        if extra:
            parts.append("unexpected " + ", ".join(extra))
        raise PreflightError(f"{where}: " + "; ".join(parts))


def _nonempty_string(value: Any, where: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PreflightError(f"{where}: expected a non-empty string")
    return value.strip()


def _optional_string(value: Any, where: str) -> str | None:
    if value is None:
        return None
    return _nonempty_string(value, where)


def _page_span(value: Any, where: str) -> PageSpan | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        raise PreflightError(f"{where}: expected null or an object with integer start/end")
    _require_exact_keys(value, {"start", "end"}, where)
    start, end = value["start"], value["end"]
    if type(start) is not int or type(end) is not int or start < 1 or end < start:
        raise PreflightError(f"{where}: expected 1 <= start <= end integer page coordinates")
    return PageSpan(start=start, end=end)


def _read_json(path: str) -> dict[str, Any]:
    if path == "-":
        raw = sys.stdin.read()
    else:
        raw = Path(path).read_text(encoding="utf-8")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise PreflightError(f"invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise PreflightError("record root must be a JSON object")
    return data


def parse_preflight(data: dict[str, Any]) -> PreflightRecord:
    _require_exact_keys(data, TOP_LEVEL_KEYS, "preflight")

    schema_version = data["schema_version"]
    if type(schema_version) is not int or schema_version not in SUPPORTED_SCHEMA_VERSIONS:
        raise PreflightError(
            f"preflight.schema_version: expected one of {sorted(SUPPORTED_SCHEMA_VERSIONS)}, got {schema_version!r}"
        )
    phase = _nonempty_string(data["phase"], "preflight.phase")
    if phase != PHASE:
        raise PreflightError(f"preflight.phase: expected {PHASE!r}, got {phase!r}")

    mode = _nonempty_string(data["mode"], "preflight.mode").lower()
    if mode not in MODES:
        raise PreflightError(
            "preflight.mode: expected one of " + ", ".join(sorted(MODES))
        )

    units_raw = data["units"]
    if not isinstance(units_raw, list) or not units_raw:
        raise PreflightError("preflight.units: expected a non-empty list")
    units: list[PreflightUnit] = []
    seen_ids: set[str] = set()
    for index, item in enumerate(units_raw, 1):
        where = f"preflight.units[{index - 1}]"
        if not isinstance(item, dict):
            raise PreflightError(f"{where}: expected an object")
        _require_exact_keys(item, UNIT_KEYS_V2 if schema_version >= 2 else UNIT_KEYS_V1, where)
        unit_id = _nonempty_string(item["unit_id"], f"{where}.unit_id").lower()
        match = UNIT_ID_RE.fullmatch(unit_id)
        if not match:
            raise PreflightError(f"{where}.unit_id: expected u01/u02/... form")
        expected_id = f"u{index:02d}"
        if unit_id != expected_id:
            raise PreflightError(
                f"{where}.unit_id: expected contiguous {expected_id!r}, got {unit_id!r}"
            )
        if unit_id in seen_ids:
            raise PreflightError(f"{where}.unit_id: duplicate {unit_id}")
        seen_ids.add(unit_id)

        overlap_raw = item["overlap_object_ids"]
        if not isinstance(overlap_raw, list):
            raise PreflightError(f"{where}.overlap_object_ids: expected a list")
        overlap: list[str] = []
        overlap_seen: set[str] = set()
        for ref_index, value in enumerate(overlap_raw):
            oid = _nonempty_string(
                value, f"{where}.overlap_object_ids[{ref_index}]"
            )
            if not OBJECT_ID_RE.fullmatch(oid):
                raise PreflightError(
                    f"{where}.overlap_object_ids[{ref_index}]: invalid PASS object id {oid!r}"
                )
            if oid in overlap_seen:
                raise PreflightError(f"{where}.overlap_object_ids: duplicate {oid}")
            overlap_seen.add(oid)
            overlap.append(oid)

        potential = _nonempty_string(
            item["card_potential"], f"{where}.card_potential"
        ).lower()
        if potential not in CARD_POTENTIALS:
            raise PreflightError(
                f"{where}.card_potential: expected one of "
                + ", ".join(sorted(CARD_POTENTIALS))
            )

        units.append(
            PreflightUnit(
                unit_id=unit_id,
                material=_nonempty_string(item["material"], f"{where}.material"),
                locator=_nonempty_string(item["locator"], f"{where}.locator"),
                source_pages=_page_span(item.get("source_pages"), f"{where}.source_pages") if schema_version >= 2 else None,
                printed_pages=_optional_string(item.get("printed_pages"), f"{where}.printed_pages") if schema_version >= 2 else None,
                overlap_object_ids=tuple(overlap),
                card_potential=potential,
            )
        )

    no_extract_raw = data["no_extract"]
    if not isinstance(no_extract_raw, list):
        raise PreflightError("preflight.no_extract: expected a list")
    no_extract: list[NoExtractSpan] = []
    for index, item in enumerate(no_extract_raw):
        where = f"preflight.no_extract[{index}]"
        if not isinstance(item, dict):
            raise PreflightError(f"{where}: expected an object")
        _require_exact_keys(item, NO_EXTRACT_KEYS, where)
        no_extract.append(
            NoExtractSpan(
                material=_nonempty_string(item["material"], f"{where}.material"),
                locator=_nonempty_string(item["locator"], f"{where}.locator"),
            )
        )

    domain = _nonempty_string(data["domain"], "preflight.domain").lower()
    if not DOMAIN_RE.fullmatch(domain):
        raise PreflightError("preflight.domain: expected a single domain package name")

    return PreflightRecord(
        schema_version=schema_version,
        phase=phase,
        title=_nonempty_string(data["title"], "preflight.title"),
        author=_nonempty_string(data["author"], "preflight.author"),
        domain=domain,
        extent=_nonempty_string(data["extent"], "preflight.extent"),
        text_quality=_nonempty_string(data["text_quality"], "preflight.text_quality"),
        subject=_nonempty_string(data["subject"], "preflight.subject"),
        mode=mode,
        units=tuple(units),
        no_extract=tuple(no_extract),
    )


def _frontmatter(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise PreflightError(f"card has no YAML frontmatter: {path}")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise PreflightError(f"card has malformed YAML frontmatter: {path}")
    try:
        data = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError as exc:
        raise PreflightError(f"card has invalid YAML frontmatter: {path}") from exc
    if not isinstance(data, dict):
        raise PreflightError(f"card frontmatter is not an object: {path}")
    return data


def load_domain_cards(repo_root: Path, domain: str) -> dict[str, CardRef]:
    if not DOMAIN_RE.fullmatch(domain):
        raise PreflightError("expected a single domain package name")
    library_root = (repo_root / "library").resolve()
    domain_root = (library_root / domain).resolve()
    if domain_root.parent != library_root:
        raise PreflightError("domain library must stay inside library/")
    if not domain_root.is_dir():
        raise PreflightError(f"domain library does not exist: library/{domain}")

    cards: dict[str, CardRef] = {}
    for path in sorted(domain_root.rglob("*.md")):
        if path.name in {"INDEX.md", "README.md"}:
            continue
        if not path.resolve().is_relative_to(domain_root):
            raise PreflightError(f"card must stay inside library/{domain}: {path}")
        data = _frontmatter(path)
        oid = data.get("object_id")
        name = data.get("name")
        if not isinstance(oid, str) or not oid:
            continue
        if not isinstance(name, str) or not name.strip():
            raise PreflightError(f"card {oid} has no canonical name: {path}")
        if oid in cards:
            raise PreflightError(f"duplicate object_id in library/{domain}: {oid}")
        cards[oid] = CardRef(object_id=oid, name=name.strip(), path=path)
    return cards


def validate_against_library(
    record: PreflightRecord, repo_root: Path
) -> dict[str, CardRef]:
    cards = load_domain_cards(repo_root, record.domain)
    missing: list[str] = []
    for unit in record.units:
        for oid in unit.overlap_object_ids:
            if oid not in cards:
                missing.append(f"{unit.unit_id}: {oid}")
    if missing:
        raise PreflightError(
            "preflight overlap references must resolve inside the active domain; missing: "
            + "; ".join(missing)
        )
    return cards


def _escape_table(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


def _display_unit_id(unit_id: str) -> str:
    return "U" + unit_id[1:]


def render_preflight(record: PreflightRecord, cards: dict[str, CardRef]) -> str:
    lines = [
        f"## Preflight — *{record.title}*",
        "",
        f"**Author:** {record.author}",
        f"**Domain:** {record.domain.title()}",
        f"**Extent:** {record.extent}",
        f"**Text:** {record.text_quality}",
        f"**Subject:** {record.subject}",
        f"**Mode:** {record.mode} — provisional",
        f"**Provisional units:** **{len(record.units)}**",
        "",
        "| Unit | Material | Likely existing-card overlap | Card potential |",
        "|---|---|---|---|",
    ]
    for unit in record.units:
        if unit.source_pages is not None:
            source_label = f"PDF/source pp. {unit.source_pages.start}-{unit.source_pages.end}"
            printed_label = f"; printed pp. {unit.printed_pages}" if unit.printed_pages else ""
            locator = f"{unit.locator}; {source_label}{printed_label}"
        else:
            locator = unit.locator
            # Legacy v1 plans may carry both printed-book and PDF/source ranges
            # in one free-form string. Keep them visibly distinct.
            has_explicit_source = bool(
                re.search(r"(?:\bpdf(?:\s*/\s*source)?|\bsource(?:\s+pages?)?)\s*(?:pp?\.?\s*)?\d+", locator, re.I)
            )
            if not has_explicit_source and re.match(r"^\s*(?:pp?\.)", locator, re.I):
                locator = "PDF/source " + locator.strip()
        material = f"{unit.material}, {locator}"
        if unit.overlap_object_ids:
            overlap = "; ".join(cards[oid].name for oid in unit.overlap_object_ids)
        else:
            overlap = "None identified"
        lines.append(
            "| **{}** | {} | {} | **{}** |".format(
                _display_unit_id(unit.unit_id),
                _escape_table(material),
                _escape_table(overlap),
                unit.card_potential.title(),
            )
        )

    lines.append("")
    if record.no_extract:
        spans = "; ".join(
            f"{span.material} ({span.locator})" for span in record.no_extract
        )
        lines.append(f"**No-extract:** {spans}")
    else:
        lines.append("**No-extract:** none")
    return "\n".join(lines)


def template_record() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "phase": PHASE,
        "title": "SOURCE TITLE",
        "author": "AUTHOR OR SOURCE CREDIT",
        "domain": "writing",
        "extent": "SOURCE EXTENT",
        "text_quality": "TEXT QUALITY",
        "subject": "WHAT THE INSTRUCTIONAL BODY TEACHES THE PRACTITIONER TO DO",
        "mode": "unit ingestion",
        "units": [
            {
                "unit_id": "u01",
                "material": "UNIT LABEL",
                "locator": "CHAPTER/SECTION OR OTHER HUMAN LOCATOR",
                "source_pages": {"start": 1, "end": 10},
                "printed_pages": None,
                "overlap_object_ids": [],
                "card_potential": "medium",
            }
        ],
        "no_extract": [],
    }


def find_repo_root(start: Path) -> Path:
    start = start.resolve()
    for candidate in (start, *start.parents):
        if (candidate / "PASS" / "docs" / "PASS_RUN.md").is_file() and (
            candidate / "library"
        ).is_dir():
            return candidate
    raise PreflightError(
        "could not locate PASS repository root; pass --repo-root explicitly"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Scripted PASS authoring phase gates (preflight implemented first)."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="PASS project root; auto-detected from the current directory by default",
    )
    sub = parser.add_subparsers(dest="phase_command", required=True)

    preflight = sub.add_parser("preflight", help="run the stateless preflight gate")
    pre_sub = preflight.add_subparsers(dest="preflight_command", required=True)

    gate = pre_sub.add_parser(
        "gate", help="validate structure and live-library overlap, then render"
    )
    gate.add_argument("--input", required=True, help="JSON record path or '-' for stdin")
    gate.add_argument(
        "--validate-only", action="store_true", help="validate without rendering"
    )

    pre_sub.add_parser("template", help="print the canonical preflight JSON template")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        if args.phase_command == "preflight" and args.preflight_command == "template":
            print(json.dumps(template_record(), indent=2))
            return 0

        repo_root = (
            args.repo_root.resolve()
            if args.repo_root is not None
            else find_repo_root(Path.cwd())
        )
        if args.phase_command == "preflight" and args.preflight_command == "gate":
            record = parse_preflight(_read_json(args.input))
            cards = validate_against_library(record, repo_root)
            if args.validate_only:
                print(
                    f"PREFLIGHT PASS: {len(record.units)} units; "
                    f"{sum(len(u.overlap_object_ids) for u in record.units)} overlap references verified"
                )
            else:
                print(render_preflight(record, cards))
            return 0
        parser.error("unsupported command")
    except (OSError, PreflightError) as exc:
        print(f"PREFLIGHT FAIL: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
