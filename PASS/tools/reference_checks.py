"""Shared visual-reference validation helpers for PASS library tools."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def sidecar_for(image: Path) -> Path:
    return Path(str(image) + ".meta.json")


def load_sidecar(image: Path) -> dict[str, Any] | None:
    path = sidecar_for(image)
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def reference_failures(record: Any, library_root: Path) -> list[str]:
    references = record.data.get("references") or []
    failures: list[str] = []
    for ref in references:
        if not isinstance(ref, dict):
            continue
        image = library_root.parent / str(ref.get("image_path", ""))
        if not image.is_file():
            failures.append("reference image is missing")
            continue
        meta = load_sidecar(image)
        if meta is None:
            failures.append(f"{ref.get('image_path', '')}: review sidecar is missing or invalid")
            continue
        origin = ref.get("origin")
        if meta.get("origin") != origin or not meta.get("generated_at"):
            failures.append(f"{ref.get('image_path', '')}: sidecar does not establish the declared origin and date")
        if origin == "generated" and not meta.get("generator_model"):
            failures.append(f"{ref.get('image_path', '')}: generated image has no model recorded")
        review = meta.get("review")
        if (
            not isinstance(review, dict)
            or review.get("verdict") != "passed"
            or not review.get("reviewer")
            or not review.get("reviewed_at")
            or not review.get("method")
        ):
            failures.append(f"{ref.get('image_path', '')}: no completed human or vision review record")
    return failures
