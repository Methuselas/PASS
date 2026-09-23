#!/usr/bin/env python3
"""Skeleton controller for PASS runs against existing Unreal Niagara effects.

This controller does not inspect Unreal by itself. A future UE automation/plugin
is expected to export the inventory and record whole-system/isolated captures.
The controller owns the durable analysis contract around those artifacts:

    inventory -> capture coverage -> classification -> card extraction -> visual validation

It deliberately does not mutate the canonical library. Candidate cards are
staged inside the run and can be reviewed/imported through the normal repository
workflow after validation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import uuid
from pathlib import Path
from typing import Any, Iterable

SCHEMA_VERSION = 1
PHASES = ("capture", "classification", "extraction", "validation", "finished")
TARGET_KINDS = {"whole_system", "solo_emitter", "solo_component"}
STYLE_VALUES = {"realistic", "stylized", "hybrid", "style_agnostic"}
CONFIDENCE_VALUES = {"low", "medium", "high"}
OBJECT_TYPES = {"pattern", "drill", "ap"}
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
LIBRARY_SEGMENT_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")


class VFXRunError(ValueError):
    pass


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise VFXRunError(f"cannot read JSON {path}: {exc}") from exc


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    temp.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(temp, path)


def _nonempty(value: Any, where: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise VFXRunError(f"{where}: expected a non-empty string")
    return value.strip()


def _repo_root(start: Path) -> Path:
    for candidate in [start.resolve(), *start.resolve().parents]:
        if (candidate / "PASS" / "vfx.py").is_file() and (candidate / "library").is_dir():
            return candidate
    raise VFXRunError("could not locate PASS repository root")


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_inventory(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise VFXRunError("inventory root must be an object")
    required = {"schema_version", "engine_version", "project_name", "system_asset", "emitters"}
    missing = sorted(required - set(data))
    if missing:
        raise VFXRunError("inventory missing: " + ", ".join(missing))
    if data["schema_version"] != SCHEMA_VERSION:
        raise VFXRunError(f"inventory.schema_version must be {SCHEMA_VERSION}")
    engine_version = _nonempty(data["engine_version"], "inventory.engine_version")
    project_name = _nonempty(data["project_name"], "inventory.project_name")
    system_asset = _nonempty(data["system_asset"], "inventory.system_asset")
    emitters_raw = data["emitters"]
    if not isinstance(emitters_raw, list) or not emitters_raw:
        raise VFXRunError("inventory.emitters must be a non-empty list")
    seen: set[str] = set()
    emitters = []
    for index, item in enumerate(emitters_raw):
        if not isinstance(item, dict):
            raise VFXRunError(f"inventory.emitters[{index}] must be an object")
        target_id = _nonempty(item.get("target_id"), f"inventory.emitters[{index}].target_id")
        if not SLUG_RE.fullmatch(target_id) or target_id == "system":
            raise VFXRunError(f"inventory.emitters[{index}].target_id must be a slug other than 'system'")
        if target_id in seen:
            raise VFXRunError(f"duplicate emitter target_id: {target_id}")
        seen.add(target_id)
        emitters.append({
            "target_id": target_id,
            "name": _nonempty(item.get("name"), f"inventory.emitters[{index}].name"),
            "enabled": bool(item.get("enabled", True)),
            "renderer_types": [str(x) for x in item.get("renderer_types", [])],
            "simulation_target": str(item.get("simulation_target", "unknown")),
            "notes": str(item.get("notes", "")),
        })
    duration = data.get("duration_seconds")
    if duration is not None:
        try:
            duration = float(duration)
        except (TypeError, ValueError) as exc:
            raise VFXRunError("inventory.duration_seconds must be numeric or null") from exc
        if duration <= 0:
            raise VFXRunError("inventory.duration_seconds must be greater than zero")
    return {
        "schema_version": SCHEMA_VERSION,
        "engine": "Unreal Engine",
        "engine_version": engine_version,
        "project_name": project_name,
        "system_asset": system_asset,
        "duration_seconds": duration,
        "emitters": emitters,
    }


def capture_plan(inventory: dict[str, Any]) -> dict[str, Any]:
    targets = [{
        "target_id": "system",
        "kind": "whole_system",
        "label": Path(inventory["system_asset"]).name or inventory["system_asset"],
        "required": True,
        "isolation": "all enabled emitters together",
    }]
    for emitter in inventory["emitters"]:
        if not emitter["enabled"]:
            continue
        targets.append({
            "target_id": emitter["target_id"],
            "kind": "solo_emitter",
            "label": emitter["name"],
            "required": True,
            "isolation": f"solo {emitter['name']}; disable other emitters without changing its own settings",
        })
    return {
        "schema_version": SCHEMA_VERSION,
        "capture_preset": "vfx",
        "temporal_sampling": {
            "default_interval_seconds": 0.5,
            "preserve_every_sample": True,
            "purpose": "classify each isolated visual role and compare whole-system timing",
        },
        "targets": targets,
    }


def run_file(root: Path) -> Path:
    return root / "controller" / "run.json"


def load_run(root: Path) -> dict[str, Any]:
    path = run_file(root)
    if not path.is_file():
        raise VFXRunError(f"not a VFX PASS run: {root}")
    data = _read_json(path)
    if not isinstance(data, dict) or data.get("schema_version") != SCHEMA_VERSION:
        raise VFXRunError("run state is missing or incompatible")
    return data


def save_run(root: Path, run: dict[str, Any]) -> None:
    _write_json(run_file(root), run)


def start(repo: Path, inventory_path: Path, task: str) -> Path:
    if not SLUG_RE.fullmatch(task):
        raise VFXRunError("task must be a lowercase slug using letters, digits, _ or -")
    inventory_path = inventory_path.resolve()
    inventory = parse_inventory(_read_json(inventory_path))
    root = repo / "workspace" / "vfx-authoring" / task
    if root.exists() and any(root.iterdir()):
        raise VFXRunError(f"run already exists and is non-empty: {root}")
    root.mkdir(parents=True, exist_ok=True)
    (root / "controller").mkdir(exist_ok=True)
    (root / "evidence").mkdir(exist_ok=True)
    (root / "staging").mkdir(exist_ok=True)
    _write_json(root / "inventory.json", inventory)
    _write_json(root / "capture-plan.json", capture_plan(inventory))
    run = {
        "schema_version": SCHEMA_VERSION,
        "run_type": "unreal-niagara-vfx-pass",
        "task": task,
        "phase": "capture",
        "inventory_sha256": _sha256(root / "inventory.json"),
        "captures_manifest": None,
        "classification": None,
        "extraction": None,
        "validation": None,
    }
    save_run(root, run)
    return root


def parse_capture_manifest(data: Any, expected_targets: set[str]) -> dict[str, Any]:
    if not isinstance(data, dict) or data.get("schema_version") != SCHEMA_VERSION:
        raise VFXRunError("capture manifest must be schema_version 1")
    captures = data.get("captures")
    if not isinstance(captures, list):
        raise VFXRunError("capture manifest captures must be a list")
    by_target = {}
    for index, item in enumerate(captures):
        if not isinstance(item, dict):
            raise VFXRunError(f"captures[{index}] must be an object")
        target_id = _nonempty(item.get("target_id"), f"captures[{index}].target_id")
        kind = _nonempty(item.get("kind"), f"captures[{index}].kind")
        if kind not in TARGET_KINDS:
            raise VFXRunError(f"captures[{index}].kind is invalid")
        bundle = _nonempty(item.get("bundle"), f"captures[{index}].bundle")
        if target_id in by_target:
            raise VFXRunError(f"duplicate capture target: {target_id}")
        by_target[target_id] = {**item, "bundle": bundle}
    missing = sorted(expected_targets - set(by_target))
    if missing:
        raise VFXRunError("capture manifest is missing required targets: " + ", ".join(missing))
    return {"schema_version": SCHEMA_VERSION, "captures": [by_target[k] for k in sorted(by_target)]}


def register_captures(root: Path, manifest_path: Path) -> None:
    run = load_run(root)
    if run["phase"] != "capture":
        raise VFXRunError(f"captures can only be registered in capture phase, not {run['phase']}")
    plan = _read_json(root / "capture-plan.json")
    required = {t["target_id"] for t in plan["targets"] if t.get("required")}
    manifest = parse_capture_manifest(_read_json(manifest_path), required)
    for item in manifest["captures"]:
        bundle = Path(item["bundle"])
        if not bundle.is_absolute():
            bundle = (manifest_path.parent / bundle).resolve()
        if not bundle.is_file():
            raise VFXRunError(f"capture bundle does not exist: {bundle}")
        item["bundle"] = str(bundle)
    copied = root / "evidence" / "vfx-stills-manifest.json"
    _write_json(copied, manifest)
    run["captures_manifest"] = copied.relative_to(root).as_posix()
    run["phase"] = "classification"
    save_run(root, run)


def classification_template(root: Path) -> dict[str, Any]:
    plan = _read_json(root / "capture-plan.json")
    return {
        "schema_version": SCHEMA_VERSION,
        "targets": [{
            "target_id": target["target_id"],
            "effect_family": "",
            "visual_role": "",
            "implementation": {
                "renderer": "",
                "simulation": "",
                "motion_method": "",
            },
            "visual_style": "style_agnostic",
            "confidence": "medium",
            "notes": "",
        } for target in plan["targets"]],
    }


def extraction_template() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "candidates": [{
            "object_type": "pattern",
            "name": "",
            "family_path": ["software-engineering", "unreal-engine", "vfx", "niagara", "recipes", "family"],
            "source_targets": [],
            "staged_path": "staging/library/software-engineering/unreal-engine/vfx/niagara/recipes/family/PAT_example.md",
            "reason": "",
        }],
    }


def validation_template() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "candidates": [{
            "staged_path": "",
            "verdict": "pass",
            "capture_targets": [],
            "checks": [],
            "near_misses_excluded": [],
            "notes": "",
        }],
    }


def submit_classification(root: Path, path: Path) -> None:
    run = load_run(root)
    if run["phase"] != "classification":
        raise VFXRunError(f"classification cannot be submitted in {run['phase']} phase")
    data = _read_json(path)
    if not isinstance(data, dict) or data.get("schema_version") != SCHEMA_VERSION or not isinstance(data.get("targets"), list):
        raise VFXRunError("classification must contain schema_version 1 and targets")
    plan = _read_json(root / "capture-plan.json")
    expected = {t["target_id"] for t in plan["targets"]}
    seen = set()
    cleaned = []
    for i, item in enumerate(data["targets"]):
        if not isinstance(item, dict):
            raise VFXRunError(f"classification.targets[{i}] must be an object")
        target = _nonempty(item.get("target_id"), f"classification.targets[{i}].target_id")
        if target in seen:
            raise VFXRunError(f"duplicate classification target: {target}")
        seen.add(target)
        style = _nonempty(item.get("visual_style"), f"classification.targets[{i}].visual_style")
        if style not in STYLE_VALUES:
            raise VFXRunError(f"invalid visual_style for {target}: {style}")
        confidence = _nonempty(item.get("confidence"), f"classification.targets[{i}].confidence")
        if confidence not in CONFIDENCE_VALUES:
            raise VFXRunError(f"invalid confidence for {target}: {confidence}")
        impl = item.get("implementation")
        if not isinstance(impl, dict):
            raise VFXRunError(f"classification for {target} requires implementation object")
        cleaned.append({
            "target_id": target,
            "effect_family": _nonempty(item.get("effect_family"), f"classification {target}.effect_family"),
            "visual_role": _nonempty(item.get("visual_role"), f"classification {target}.visual_role"),
            "implementation": {
                "renderer": _nonempty(impl.get("renderer"), f"classification {target}.implementation.renderer"),
                "simulation": _nonempty(impl.get("simulation"), f"classification {target}.implementation.simulation"),
                "motion_method": _nonempty(impl.get("motion_method"), f"classification {target}.implementation.motion_method"),
            },
            "visual_style": style,
            "confidence": confidence,
            "notes": str(item.get("notes", "")),
        })
    if seen != expected:
        raise VFXRunError("classification target set does not match capture plan; missing=" + str(sorted(expected-seen)) + ", extra=" + str(sorted(seen-expected)))
    out = root / "classification.json"
    _write_json(out, {"schema_version": SCHEMA_VERSION, "targets": cleaned})
    run["classification"] = out.relative_to(root).as_posix()
    run["phase"] = "extraction"
    save_run(root, run)


def _validate_family_path(parts: Any) -> list[str]:
    if not isinstance(parts, list) or len(parts) < 6:
        raise VFXRunError("family_path must be a recipe library path with a family segment")
    result = [str(x) for x in parts]
    expected = ["software-engineering", "unreal-engine", "vfx", "niagara", "recipes"]
    if result[:5] != expected or not all(LIBRARY_SEGMENT_RE.fullmatch(x) for x in result):
        raise VFXRunError("family_path must begin software-engineering/unreal-engine/vfx/niagara/recipes and contain lowercase path segments")
    return result


def submit_extraction(root: Path, path: Path) -> None:
    run = load_run(root)
    if run["phase"] != "extraction":
        raise VFXRunError(f"extraction cannot be submitted in {run['phase']} phase")
    data = _read_json(path)
    if not isinstance(data, dict) or data.get("schema_version") != SCHEMA_VERSION or not isinstance(data.get("candidates"), list) or not data["candidates"]:
        raise VFXRunError("extraction requires a non-empty candidates list")
    plan_targets = {t["target_id"] for t in _read_json(root / "capture-plan.json")["targets"]}
    cleaned = []
    for i, item in enumerate(data["candidates"]):
        if not isinstance(item, dict):
            raise VFXRunError(f"candidates[{i}] must be an object")
        object_type = _nonempty(item.get("object_type"), f"candidates[{i}].object_type")
        if object_type not in OBJECT_TYPES:
            raise VFXRunError(f"invalid object_type in candidates[{i}]")
        sources = item.get("source_targets")
        if not isinstance(sources, list) or not sources or not set(map(str, sources)) <= plan_targets:
            raise VFXRunError(f"candidates[{i}].source_targets must name one or more capture targets")
        staged = _nonempty(item.get("staged_path"), f"candidates[{i}].staged_path")
        if not staged.startswith("staging/library/") or ".." in Path(staged).parts:
            raise VFXRunError(f"candidates[{i}].staged_path must stay under staging/library")
        staged_abs = root / staged
        if not staged_abs.is_file():
            raise VFXRunError(f"staged candidate does not exist: {staged_abs}")
        cleaned.append({
            "object_type": object_type,
            "name": _nonempty(item.get("name"), f"candidates[{i}].name"),
            "family_path": _validate_family_path(item.get("family_path")),
            "source_targets": [str(x) for x in sources],
            "staged_path": staged,
            "sha256": _sha256(staged_abs),
            "reason": _nonempty(item.get("reason"), f"candidates[{i}].reason"),
        })
    out = root / "extraction.json"
    _write_json(out, {"schema_version": SCHEMA_VERSION, "candidates": cleaned})
    run["extraction"] = out.relative_to(root).as_posix()
    run["phase"] = "validation"
    save_run(root, run)


def submit_validation(root: Path, path: Path) -> None:
    run = load_run(root)
    if run["phase"] != "validation":
        raise VFXRunError(f"validation cannot be submitted in {run['phase']} phase")
    extraction = _read_json(root / str(run["extraction"]))
    expected = {c["staged_path"]: c for c in extraction["candidates"]}
    data = _read_json(path)
    if not isinstance(data, dict) or data.get("schema_version") != SCHEMA_VERSION or not isinstance(data.get("candidates"), list):
        raise VFXRunError("validation requires schema_version 1 and candidates")
    seen = set()
    cleaned = []
    failed = []
    capture_targets = {t["target_id"] for t in _read_json(root / "capture-plan.json")["targets"]}
    for i, item in enumerate(data["candidates"]):
        if not isinstance(item, dict):
            raise VFXRunError(f"validation.candidates[{i}] must be an object")
        staged = _nonempty(item.get("staged_path"), f"validation.candidates[{i}].staged_path")
        if staged not in expected or staged in seen:
            raise VFXRunError(f"validation contains unknown or duplicate staged_path: {staged}")
        seen.add(staged)
        if _sha256(root / staged) != expected[staged]["sha256"]:
            raise VFXRunError(f"staged card changed after extraction submission: {staged}")
        verdict = _nonempty(item.get("verdict"), f"validation {staged}.verdict").lower()
        if verdict not in {"pass", "fail"}:
            raise VFXRunError(f"validation verdict must be pass or fail: {staged}")
        captures = item.get("capture_targets")
        checks = item.get("checks")
        near = item.get("near_misses_excluded")
        if not isinstance(captures, list) or not captures:
            raise VFXRunError(f"validation {staged} requires capture_targets")
        if not set(map(str, captures)) <= capture_targets:
            raise VFXRunError(f"validation {staged} names a capture target outside the run")
        if not isinstance(checks, list) or not checks:
            raise VFXRunError(f"validation {staged} requires observable checks")
        if not isinstance(near, list):
            raise VFXRunError(f"validation {staged}.near_misses_excluded must be a list")
        cleaned.append({
            "staged_path": staged,
            "verdict": verdict,
            "capture_targets": [str(x) for x in captures],
            "checks": [str(x) for x in checks],
            "near_misses_excluded": [str(x) for x in near],
            "notes": str(item.get("notes", "")),
        })
        if verdict == "fail":
            failed.append(staged)
    if seen != set(expected):
        raise VFXRunError("validation must account for every extraction candidate")
    out = root / "validation.json"
    _write_json(out, {"schema_version": SCHEMA_VERSION, "candidates": cleaned})
    run["validation"] = out.relative_to(root).as_posix()
    if failed:
        run["phase"] = "extraction"
        save_run(root, run)
        raise VFXRunError("visual validation failed for: " + ", ".join(failed) + "; revise staged cards/effect evidence, then resubmit extraction")
    run["phase"] = "finished"
    save_run(root, run)


def template(root: Path, phase: str) -> dict[str, Any]:
    run = load_run(root)
    if phase == "classification":
        return classification_template(root)
    if phase == "extraction":
        return extraction_template()
    if phase == "validation":
        return validation_template()
    raise VFXRunError("template phase must be classification, extraction, or validation")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo-root", type=Path)
    sub = p.add_subparsers(dest="command", required=True)
    s = sub.add_parser("start", help="create a VFX PASS workspace from a UE-exported inventory")
    s.add_argument("--inventory", type=Path, required=True)
    s.add_argument("--task", required=True)
    s = sub.add_parser("status", help="show durable run state")
    s.add_argument("--run", type=Path, required=True)
    s = sub.add_parser("register-captures", help="bind whole-system and isolated still bundles")
    s.add_argument("--run", type=Path, required=True)
    s.add_argument("--manifest", type=Path, required=True)
    s = sub.add_parser("template", help="print the JSON contract for the next model-authored phase")
    s.add_argument("--run", type=Path, required=True)
    s.add_argument("--phase", choices=("classification", "extraction", "validation"), required=True)
    s = sub.add_parser("submit", help="validate and record a model-authored phase")
    s.add_argument("--run", type=Path, required=True)
    s.add_argument("--phase", choices=("classification", "extraction", "validation"), required=True)
    s.add_argument("--input", type=Path, required=True)
    s = sub.add_parser("close-run", help="remove controller state only after a finished run")
    s.add_argument("--run", type=Path, required=True)
    return p


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)
    try:
        repo = args.repo_root.resolve() if args.repo_root else _repo_root(Path.cwd())
        if args.command == "start":
            root = start(repo, args.inventory, args.task)
            print(json.dumps({"run": str(root), "phase": "capture", "capture_plan": str(root / 'capture-plan.json')}, indent=2))
            return 0
        root = args.run.resolve()
        if args.command == "status":
            print(json.dumps(load_run(root), indent=2))
        elif args.command == "register-captures":
            register_captures(root, args.manifest)
            print(json.dumps(load_run(root), indent=2))
        elif args.command == "template":
            print(json.dumps(template(root, args.phase), indent=2))
        elif args.command == "submit":
            if args.phase == "classification":
                submit_classification(root, args.input)
            elif args.phase == "extraction":
                submit_extraction(root, args.input)
            else:
                submit_validation(root, args.input)
            print(json.dumps(load_run(root), indent=2))
        elif args.command == "close-run":
            run = load_run(root)
            if run["phase"] != "finished":
                raise VFXRunError("cannot close an unfinished VFX PASS run")
            controller = root / "controller"
            shutil.rmtree(controller)
            print(f"VFX PASS RUN CLOSED: controller state removed; evidence, staged cards, and reports retained at {root}")
        return 0
    except (OSError, VFXRunError) as exc:
        print(f"VFX PASS BLOCKED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
