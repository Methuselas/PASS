#!/usr/bin/env python3
"""Inventory PASS Drills and the evidence their Instructions explicitly request.

The inventory is derived from cards on every invocation. It is navigation for
administering Drills, not a registry and not a source of canonical truth.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path

import yaml


FRONTMATTER_RE = re.compile(
    r"\A---\s*\n(?P<front>.*?)\n---\s*\n(?P<body>.*)\Z", re.DOTALL
)
SECTION_RE = re.compile(
    r"^## (?P<name>[^\n]+)\s*$\n(?P<content>.*?)(?=^## |\Z)",
    re.MULTILINE | re.DOTALL,
)
EXPECTED_COMPILE_FAILURE_RE = re.compile(
    r"(?:does not|doesn't|won't|must not|should not|fails? to) compile|"
    r"compile(?:r|d)? (?:error|failure)|rejected by (?:the )?compiler",
    re.IGNORECASE,
)
SIGNAL_PATTERNS = {
    "compile": re.compile(r"\b(?:compile|compiler|build)\b", re.IGNORECASE),
    "run": re.compile(r"\b(?:run|execute|benchmark|profile)\b", re.IGNORECASE),
    "test": re.compile(r"\b(?:test|tests|testing)\b", re.IGNORECASE),
    "code": re.compile(
        r"\b(?:code|implement|write|refactor|redesign|modify|replace|class|function)\b",
        re.IGNORECASE,
    ),
}


@dataclass(frozen=True)
class DrillInventoryItem:
    object_id: str
    name: str
    target_skill: str
    module: str
    path: str
    administration_class: str
    machine_evidence: tuple[str, ...]


def read_drill(path: Path, library: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    if not match:
        raise ValueError(f"{path.relative_to(library)} lacks valid frontmatter")
    data = yaml.safe_load(match.group("front"))
    if not isinstance(data, dict):
        raise ValueError(f"{path.relative_to(library)} frontmatter is not a mapping")
    return data, match.group("body")


def sections(body: str) -> dict[str, str]:
    return {
        match.group("name").strip(): match.group("content").strip()
        for match in SECTION_RE.finditer(body)
    }


def classify(instructions: str) -> tuple[str, tuple[str, ...]]:
    evidence: list[str] = []
    if EXPECTED_COMPILE_FAILURE_RE.search(instructions):
        evidence.append("expected_compile_failure")
    evidence.extend(
        name for name, pattern in SIGNAL_PATTERNS.items()
        if name != "code" and pattern.search(instructions)
    )

    if "expected_compile_failure" in evidence:
        primary = "expected-compile-failure"
    elif "compile" in evidence:
        primary = "compile-or-build"
    elif any(name in evidence for name in ("run", "test")):
        primary = "runtime-or-test"
    elif SIGNAL_PATTERNS["code"].search(instructions):
        primary = "code-production"
    else:
        primary = "analysis-or-review"
    return primary, tuple(evidence)


def owning_module(path: Path, library: Path, package_root: Path) -> str | None:
    current = path.parent
    while current == package_root or package_root in current.parents:
        if (current / "MODULE.yaml").is_file():
            return current.relative_to(library).as_posix()
        current = current.parent
    return None


def inventory(library: Path, package: str) -> tuple[list[DrillInventoryItem], list[str]]:
    library = library.resolve()
    package_root = (library / package).resolve()
    if package_root.parent != library or not package_root.is_dir():
        raise ValueError(f"unknown package: {package}")

    items: list[DrillInventoryItem] = []
    problems: list[str] = []
    seen_ids: set[str] = set()
    for path in sorted(package_root.rglob("DRILL_*.md")):
        data, body = read_drill(path, library)
        relative = path.relative_to(library).as_posix()
        card_sections = sections(body)
        for field in ("object_id", "name", "target_skill"):
            if not str(data.get(field, "")).strip():
                problems.append(f"{relative}: missing {field}")
        for heading in ("Practice Task", "Instructions", "Success Check"):
            if not card_sections.get(heading):
                problems.append(f"{relative}: missing ## {heading}")

        object_id = str(data.get("object_id", ""))
        if object_id in seen_ids:
            problems.append(f"{relative}: duplicate object_id {object_id}")
        seen_ids.add(object_id)

        primary, evidence = classify(card_sections.get("Instructions", ""))
        module = owning_module(path, library, package_root)
        if module is None:
            problems.append(f"{relative}: no owning MODULE.yaml")
            module = package
        items.append(
            DrillInventoryItem(
                object_id=object_id,
                name=str(data.get("name", "")),
                target_skill=str(data.get("target_skill", "")),
                module=module,
                path=relative,
                administration_class=primary,
                machine_evidence=evidence,
            )
        )
    return items, problems


def print_summary(items: list[DrillInventoryItem], package: str) -> None:
    print(f"{package}: {len(items)} Drills")
    counts = Counter(item.administration_class for item in items)
    for name in (
        "expected-compile-failure",
        "compile-or-build",
        "runtime-or-test",
        "code-production",
        "analysis-or-review",
    ):
        print(f"  {name:<25} {counts[name]:>3}")


def print_markdown(items: list[DrillInventoryItem], package: str) -> None:
    print(f"# {package} Drill inventory\n")
    print("Derived from the current cards; regenerate instead of editing this output.\n")
    print("| Drill | Class | Machine evidence | Module |")
    print("| --- | --- | --- | --- |")
    for item in items:
        evidence = ", ".join(item.machine_evidence) or "none declared"
        print(
            f"| `{item.object_id}` — {item.name} | {item.administration_class} | "
            f"{evidence} | `{item.module}` |"
        )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Derive a Drill administration inventory from one PASS package.",
        epilog="Classification reports explicit Instruction signals; it does not grade a Drill.",
    )
    parser.add_argument("--package", required=True, help="One package under library/.")
    parser.add_argument(
        "--library", type=Path,
        default=Path(__file__).resolve().parents[2] / "library",
        help="Library root (default: this repository's library/).",
    )
    parser.add_argument(
        "--format", choices=("summary", "json", "markdown"), default="summary",
        help="Output format (default: summary).",
    )
    parser.add_argument(
        "--check", action="store_true",
        help="Fail when a Drill lacks required identity or administration sections.",
    )
    args = parser.parse_args()

    try:
        items, problems = inventory(args.library, args.package)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        parser.error(str(exc))

    if args.format == "json":
        print(json.dumps([asdict(item) for item in items], indent=2, ensure_ascii=False))
    elif args.format == "markdown":
        print_markdown(items, args.package)
    else:
        print_summary(items, args.package)

    if problems:
        for problem in problems:
            print(f"ERROR: {problem}", file=sys.stderr)
        return 1
    if args.check and args.format != "json":
        print(f"PASS: {len(items)} Drills have complete administration sections")
    return 0


if __name__ == "__main__":
    sys.exit(main())
