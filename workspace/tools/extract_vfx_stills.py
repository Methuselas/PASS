#!/usr/bin/env python3
"""Capture uniform temporal stills for whole and isolated VFX recordings.

This is a thin VFX adapter over extract_video_stills.py. It accepts a manifest
of recordings (whole system plus solo emitters/components), generates synthetic
subtitle cues at uniform timestamps, and lets the existing stills engine build
one bundle per target using the VFX preset. Every planned time sample is kept by
default so temporal behavior can be reviewed instead of deduplicated away.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterable

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
import extract_video_stills as stills

SCHEMA_VERSION = 1
TARGET_KINDS = {"whole_system", "solo_emitter", "solo_component"}
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")


class ManifestError(ValueError):
    pass


def _stamp(seconds: float) -> str:
    milliseconds = max(0, int(round(seconds * 1000.0)))
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, ms = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}"


def sample_times(duration: float, interval: float) -> list[float]:
    if duration <= 0:
        raise ManifestError("video duration must be greater than zero")
    if interval <= 0:
        raise ManifestError("interval must be greater than zero")
    # Start just after frame zero, then include the final visible moment. Exact
    # zero and exact EOF are fragile seek targets in compressed video.
    epsilon = min(0.05, duration / 20.0)
    end = max(epsilon, duration - epsilon)
    result = [epsilon]
    n = 1
    while n * interval < end:
        result.append(n * interval)
        n += 1
    if end - result[-1] > 0.05:
        result.append(end)
    return [round(value, 3) for value in result]


def write_synthetic_srt(path: Path, times: list[float], duration: float) -> None:
    lines = []
    for index, point in enumerate(times, 1):
        half = min(0.04, max(0.005, duration / 1000.0))
        start = max(0.0, point - half)
        end = min(duration, point + half)
        if end <= start:
            end = min(duration, start + 0.01)
        lines.extend([
            str(index),
            f"{_stamp(start)} --> {_stamp(end)}",
            f"VFX temporal sample {index} at {point:.3f}s",
            "",
        ])
    path.write_text("\n".join(lines), encoding="utf-8")


def load_manifest(path: Path) -> list[dict[str, Any]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ManifestError(f"cannot read manifest: {exc}") from exc
    if not isinstance(data, dict) or data.get("schema_version") != SCHEMA_VERSION:
        raise ManifestError("manifest root must declare schema_version 1")
    captures = data.get("captures")
    if not isinstance(captures, list) or not captures:
        raise ManifestError("manifest.captures must be a non-empty list")
    seen = set()
    result = []
    for i, item in enumerate(captures):
        if not isinstance(item, dict):
            raise ManifestError(f"captures[{i}] must be an object")
        target = str(item.get("target_id", "")).strip()
        kind = str(item.get("kind", "")).strip()
        video = str(item.get("video", "")).strip()
        if not SLUG_RE.fullmatch(target):
            raise ManifestError(f"captures[{i}].target_id must be a lowercase slug")
        if target in seen:
            raise ManifestError(f"duplicate target_id: {target}")
        seen.add(target)
        if kind not in TARGET_KINDS:
            raise ManifestError(f"captures[{i}].kind must be one of {sorted(TARGET_KINDS)}")
        if not video:
            raise ManifestError(f"captures[{i}].video is required")
        result.append({"target_id": target, "kind": kind, "video": video, "label": str(item.get("label", target))})
    return result


def run(manifest: Path, output: Path, interval: float, ffmpeg_path: str = "") -> Path:
    captures = load_manifest(manifest)
    output.mkdir(parents=True, exist_ok=True)
    settings = stills.Settings(workers=4, ffmpeg_path=ffmpeg_path)
    settings.apply_preset("vfx")
    settings.dedupe_mode = "off"
    settings.capture_point = "middle"
    settings.validate()
    ffmpeg = stills.find_ffmpeg(ffmpeg_path)
    if ffmpeg is None:
        raise ManifestError("ffmpeg was not found")
    ffprobe = stills.sibling_ffprobe(ffmpeg)
    report_items = []
    for index, item in enumerate(captures, 1):
        video = Path(item["video"])
        if not video.is_absolute():
            video = (manifest.parent / video).resolve()
        if not video.is_file():
            raise ManifestError(f"video not found for {item['target_id']}: {video}")
        info = stills.probe_video(ffprobe, video)
        if info.duration <= 0:
            raise ManifestError(f"could not determine duration for {video}")
        times = sample_times(info.duration, interval)
        bundle = output / f"{item['target_id']}.stills.zip"
        with tempfile.TemporaryDirectory(prefix="pass_vfx_srt_") as temp:
            srt = Path(temp) / f"{item['target_id']}.srt"
            write_synthetic_srt(srt, times, info.duration)
            result = stills.extract_bundle(video, srt, bundle, settings)
        report_items.append({
            "target_id": item["target_id"],
            "kind": item["kind"],
            "label": item["label"],
            "video": str(video),
            "duration_seconds": round(info.duration, 3),
            "sample_interval_seconds": interval,
            "planned_samples": len(times),
            "kept_frames": result.kept,
            "bundle": str(bundle.resolve()),
        })
        print(f"[{index}/{len(captures)}] {item['target_id']}: {result.kept} frames -> {bundle}")
    result_manifest = output / "vfx-stills-manifest.json"
    result_manifest.write_text(json.dumps({"schema_version": 1, "captures": report_items}, indent=2) + "\n", encoding="utf-8")
    return result_manifest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="JSON manifest of whole-system and isolated VFX recordings")
    parser.add_argument("-o", "--output", type=Path, required=True)
    parser.add_argument("--interval", type=float, default=0.5, help="seconds between temporal samples (default: 0.5)")
    parser.add_argument("--ffmpeg", default="", help="optional path to ffmpeg")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)
    try:
        manifest = run(args.manifest.resolve(), args.output.resolve(), args.interval, args.ffmpeg)
        print(f"Manifest: {manifest}")
        return 0
    except (ManifestError, stills.ExtractionError, OSError) as exc:
        print(f"VFX STILLS BLOCKED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
