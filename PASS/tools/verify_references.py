#!/usr/bin/env python3
"""Fail-closed release gate for PASS visual-card reference assets.

A card that ships an image ships a runtime artifact, so the image must exist and
must carry a completed review record in its `<image>.meta.json` sidecar. Package
scope is real: `--package` scans only that package. Full-library verification is
still the canonical/source-completion gate.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

import yaml

from validate import discover_objects, parse_object
from reference_checks import load_sidecar, reference_failures, sidecar_for
from paths import default_library_root


def repo_root_for(card: Path) -> Path:
    for parent in (card.parent, *card.parents):
        if parent.name == "library":
            return parent.parent
    raise ValueError("card must sit below a library directory")


def record_review(card: Path, reference_index: int, reviewer: str, method: str, note: str) -> int:
    raw = card.read_text(encoding="utf-8")
    front, body = raw.split("---\n", 2)[1:]
    data = yaml.safe_load(front)
    ref = data["references"][reference_index]
    image = repo_root_for(card.resolve()) / ref["image_path"]
    meta = load_sidecar(image)
    if meta is None:
        raise ValueError("reference review sidecar is missing")
    meta["review"] = {
        "verdict": "passed",
        "reviewer": reviewer,
        "reviewed_at": date.today().isoformat(),
        "method": method,
        "note": note,
    }
    sidecar_for(image).write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    ref["review"] = "passed"
    card.write_text("---\n" + yaml.safe_dump(data, sort_keys=False) + "---\n" + body, encoding="utf-8")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--library", type=Path, default=default_library_root())
    parser.add_argument("--package", help="verify only one top-level package")
    parser.add_argument("--record-review", type=Path, help="card to mark passed after a real human or vision review")
    parser.add_argument("--reference-index", type=int, default=0)
    parser.add_argument("--reviewer")
    parser.add_argument("--method", help="for example: human visual inspection")
    parser.add_argument("--note", default="Depicts the card claim; anatomy and construction checked.")
    args = parser.parse_args()
    if args.record_review:
        if not args.reviewer or not args.method:
            parser.error("--record-review requires --reviewer and --method")
        try:
            return record_review(args.record_review, args.reference_index, args.reviewer, args.method, args.note)
        except (ValueError, IndexError, KeyError) as exc:
            print(f"FAIL: {exc}")
            return 1
    if not args.library.is_dir():
        print(f"FAIL: library root not found: {args.library.as_posix()}", file=sys.stderr)
        return 1
    scope = args.library / args.package if args.package else args.library
    if args.package and not scope.is_dir():
        print(f"FAIL: package root not found: {scope.as_posix()}", file=sys.stderr)
        return 1
    failures: list[str] = []
    for path in discover_objects(scope):
        record = parse_object(path, args.library)
        for failure in reference_failures(record, args.library):
            failures.append(f"{record.label}: {failure}")
    if failures:
        print(f"REFERENCE REVIEW FAILED: {len(failures)} issue(s)")
        print("\n".join(f"- {failure}" for failure in failures))
        return 1
    package = f" in package '{args.package}'" if args.package else ""
    print(f"REFERENCE REVIEW OK: every visual reference{package} is present and reviewed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
