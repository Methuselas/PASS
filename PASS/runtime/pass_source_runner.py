#!/usr/bin/env python3
"""Bounded unattended orchestration for one ordinary PASS source run.

The host/model still performs substantive reading and adjudication, but this
module is the authoritative dispatcher for an unattended source run. It issues
one persisted action lease at a time, refuses unsupported phase jumps, consumes
deterministic gates, derives progress only from controller state, and records
completion only after final source verification.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Iterable

from . import pass_authoring_run as preflight
from .pass_authoring_workflow import Run, RunError, atomic_write, digest, exact, inside, string


AUTH_SCHEMA = 1
AUDIT_SCHEMA = 1
COMPLETION_SCHEMA = 1
ACTION_SCHEMA = 1
REPORT_SCHEMA = 1



def action_path(run: Run) -> Path:
    return run.unattended_action_path()


def action_instruction(run: Run) -> str:
    phase = run.state["phase"]
    if phase == "preflight":
        return "Perform the one structural source-wide preflight, write the canonical preflight JSON, then submit phase=preflight through PASS/pass.py."
    if phase == "pass1":
        return f"Read the complete bounded unit {run.unit()['unit_id']} from the source, create only working drafts/notes allowed by PASS 1, then submit phase=pass1 through PASS/pass.py."
    if phase == "checkpoint":
        return "Resolve every checkpoint question only from source/library evidence. If any answer requires practitioner judgment, stop and report the human-required question instead of guessing; otherwise submit phase=checkpoint through PASS/pass.py."
    if phase == "pass2":
        return f"Cold-reread the complete bounded unit {run.unit()['unit_id']}, adjudicate the exact delta/taxonomy, stage all declared changes, then submit phase=pass2 through PASS/pass.py."
    if phase == "pass3":
        return f"Close the source/reading notes, perform card-only PASS 3 for {run.unit()['unit_id']}, repair/rescan until clean, then submit phase=pass3 with hashes through PASS/pass.py."
    raise RunError(f"phase {phase} is deterministic or not dispatchable as a host action")


def issue_action(run: Run) -> dict[str, Any]:
    phase = run.state["phase"]
    if phase not in {"preflight", "pass1", "checkpoint", "pass2", "pass3"}:
        raise RunError(f"cannot issue substantive action for phase: {phase}")
    unit_id = None if phase == "preflight" else run.unit()["unit_id"]
    state_sha = digest(run.state_path)
    seed = f"{run.source_identity()['sha256']}|{phase}|{run.state['unit_index']}|{unit_id or '-'}|{state_sha}"
    import hashlib
    action_id = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    record = {
        "schema_version": ACTION_SCHEMA,
        "action_id": action_id,
        "phase": phase,
        "unit_index": run.state["unit_index"],
        "unit_id": unit_id,
        "state_sha256": state_sha,
        "instruction": action_instruction(run),
    }
    path = action_path(run)
    if path.is_file():
        current = preflight._read_json(str(path))
        if current == record:
            return record
        # A stale lease means state moved without source.py reconciling it. Preserve
        # the evidence rather than overwriting silently.
        stale = inside(run.root, f"controller/action-history/stale-{current.get('action_id','unknown')}.json")
        stale.parent.mkdir(parents=True, exist_ok=True)
        atomic_write(stale, (json.dumps(current, indent=2) + "\n").encode("utf-8"))
    atomic_write(path, (json.dumps(record, indent=2) + "\n").encode("utf-8"))
    append_event(run, {"event": "host_action_issued", "action_id": action_id, "phase": phase, "unit_index": run.state["unit_index"], "unit_id": unit_id})
    return record


def progress_report(run: Run) -> dict[str, Any]:
    identity = run.source_identity() if run.source_identity_path().is_file() else None
    plan = run.state["plan"]
    count = len(plan["units"]) if plan else None
    closed = run.state["unit_index"] if plan else 0
    completed_ids = [u["unit_id"] for u in plan["units"][:closed]] if plan else []
    completion = None
    cpath = completion_path(run)
    if cpath.is_file():
        completion = preflight._read_json(str(cpath))
    active = None
    if plan and run.state["phase"] != "finished" and closed < len(plan["units"]):
        active = plan["units"][closed]["unit_id"]
    if not plan:
        statement = f"No preflight plan accepted; current phase={run.state['phase']}."
    elif completion:
        statement = f"Source complete: {closed}/{count} units landed and final source validation recorded."
    else:
        prefix = f"{closed}/{count} units landed"
        statement = prefix + (f"; current={active}/{run.state['phase']}; source not complete." if active else f"; phase={run.state['phase']}; source not complete.")
    return {
        "schema_version": REPORT_SCHEMA,
        "authoritative": True,
        "source_sha256": identity["sha256"] if identity else None,
        "phase": run.state["phase"],
        "unit_count": count,
        "units_completed": closed,
        "completed_unit_ids": completed_ids,
        "active_unit_id": active,
        "source_complete": completion is not None,
        "final_validation_recorded": completion is not None,
        "statement": statement,
    }


def drive(run: Run) -> dict[str, Any]:
    """Advance all deterministic gates, then issue exactly one verified host action.

    Repeated calls are idempotent. A caller must execute the returned action and
    call ``drive`` again. No progress statement is authoritative unless it comes
    from ``progress_report``.
    """
    run.unattended_authorization(required=True)
    for _ in range(100):
        phase = run.state["phase"]
        if phase in {"preflight_accept", "land", "finished"}:
            result = advance(run)
            run.reload()
            if result.get("outcome") in {"blocked_human_required", "source_complete"}:
                return {**result, "report": progress_report(run)}
            continue
        if phase in {"preflight", "pass1", "checkpoint", "pass2", "pass3"}:
            action = issue_action(run)
            return {"outcome": "host_action_required", "action": action, "report": progress_report(run)}
        if phase == "load":
            return {
                "outcome": "load_required",
                "reason": "LOAD is intentionally outside unattended authorization; read required canonical documents and submit LOAD before authorizing/drive.",
                "report": {"schema_version": REPORT_SCHEMA, "authoritative": True, "phase": "load", "statement": "LOAD not yet completed; no PASS progress may be claimed."},
            }
        raise RunError(f"unknown phase: {phase}")
    raise RunError("source drive exceeded deterministic transition limit")

def audit_dir(run: Run) -> Path:
    path = inside(run.root, "controller/audit")
    path.mkdir(parents=True, exist_ok=True)
    return path


def audit_events_path(run: Run) -> Path:
    return inside(run.root, "controller/audit/events.jsonl")


def append_event(run: Run, event: dict[str, Any]) -> None:
    event = {"schema_version": AUDIT_SCHEMA, **event}
    path = audit_events_path(run)
    existing: list[dict[str, Any]] = []
    if path.is_file():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    value = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise RunError("unattended audit log is malformed") from exc
                if not isinstance(value, dict):
                    raise RunError("unattended audit log contains a non-object event")
                existing.append(value)
    # Retried deterministic gates should not create duplicate history records.
    if event in existing:
        return
    content = "".join(json.dumps(item, sort_keys=True) + "\n" for item in [*existing, event])
    atomic_write(path, content.encode("utf-8"))


def write_packet(run: Run, name: str, packet: str, sha256: str) -> Path:
    directory = audit_dir(run)
    path = inside(directory, f"{name}.md")
    atomic_write(path, packet.encode("utf-8"))
    marker = {"schema_version": AUDIT_SCHEMA, "sha256": sha256, "bytes": len(packet.encode("utf-8"))}
    atomic_write(inside(directory, f"{name}.json"), (json.dumps(marker, indent=2) + "\n").encode("utf-8"))
    if digest(path) != sha256:
        raise RunError("audit packet verification failed")
    return path


def authorization_record(run: Run, reason: str) -> dict[str, Any]:
    run.source_file(required=True)
    identity = run.source_identity()
    return {
        "schema_version": AUTH_SCHEMA,
        "mode": "unattended",
        "scope": "source_completion",
        "authorized_by": "user",
        "domain": run.domain,
        "source_sha256": identity["sha256"],
        "reason": string(reason, "unattended authorization reason"),
    }


def authorize(run: Run, reason: str) -> str:
    if run.state["phase"] == "load":
        raise RunError("complete the LOAD gate first; source identity is captured only after canonical instructions are declared read")
    if run.state["phase"] == "finished":
        raise RunError("source is already finished; unattended authorization is no longer needed")
    record = authorization_record(run, reason)
    path = run.unattended_authorization_path()
    if path.is_file():
        current = run.unattended_authorization(required=True)
        if current == record:
            return "UNATTENDED AUTHORIZATION: already active for this source through completion"
    atomic_write(path, (json.dumps(record, indent=2) + "\n").encode("utf-8"))
    append_event(run, {"event": "authorization_recorded", "scope": "source_completion", "source_sha256": record["source_sha256"]})
    return "UNATTENDED AUTHORIZATION: active for this source through completion"


def revoke(run: Run) -> str:
    path = run.unattended_authorization_path()
    if not path.is_file():
        return "UNATTENDED AUTHORIZATION: already inactive"
    path.unlink()
    append_event(run, {"event": "authorization_revoked"})
    return "UNATTENDED AUTHORIZATION: revoked; interactive gates restored"


def source_verified(run: Run) -> tuple[bool, str | None]:
    if run.state["phase"] == "load" and not run.source_identity_path().is_file():
        path = Path(run.state["source"]).resolve()
        return (path.is_file(), None if path.is_file() else f"source does not exist: {path}")
    try:
        run.source_file(required=True)
        return True, None
    except RunError as exc:
        return False, str(exc)


def next_action(run: Run, authorized: bool, source_ok: bool) -> str:
    if not source_ok:
        return "Rebind the identical source bytes with source.py rebind-source before continuing."
    phase = run.state["phase"]
    if phase == "load":
        return "Host reads the canonical required documents and submits LOAD through pass.py."
    if phase == "preflight":
        return "Host performs the one structural source-wide preflight and submits it through pass.py."
    if phase == "preflight_accept":
        return "Run source.py advance to archive and accept preflight." if authorized else "Interactive preflight presentation/confirmation is required."
    if phase == "pass1":
        return "Host performs the complete bounded unit PASS 1 and submits it through pass.py."
    if phase == "checkpoint":
        return (
            "Host resolves only evidence-settled questions autonomously. If any question depends on practitioner judgment, stop and wait; "
            "otherwise submit all checkpoint answers through pass.py."
        )
    if phase == "pass2":
        return "Host performs the full cold PASS 2 reread and submits the exact delta through pass.py."
    if phase == "pass3":
        return "Host performs card-only PASS 3, repairs until clean, and submits reviewed hashes through pass.py."
    if phase == "land":
        if not authorized:
            return "Interactive landing presentation and decision are required."
        if run.state["pass2"]["approval_required"]:
            return "Run source.py advance to archive the packet; it will stop for practitioner approval."
        return "Run source.py advance to archive and auto-land the routine delta."
    if phase == "finished":
        return "Run source.py advance once more to execute final source verification and record completion."
    raise RunError(f"unknown phase: {phase}")


def status(run: Run) -> dict[str, Any]:
    ok, source_error = source_verified(run)
    authorization = None
    try:
        authorization = run.unattended_authorization(required=False) if ok else None
    except RunError as exc:
        source_error = str(exc)
        ok = False
    phase = run.state["phase"]
    identity = run.source_identity() if run.source_identity_path().is_file() else None
    result: dict[str, Any] = {
        "run": str(run.root),
        "mode": "unattended" if authorization else "interactive",
        "authorized": authorization is not None,
        "authorized_scope": authorization["scope"] if authorization else None,
        "domain": run.domain,
        "source": run.state["source"],
        "source_sha256": identity["sha256"] if identity else None,
        "source_identity": "verified" if identity and ok else ("pending_load" if phase == "load" else "unverified"),
        "source_verified": ok,
        "phase": phase,
        "next_action": next_action(run, authorization is not None, ok),
    }
    if source_error:
        result["source_error"] = source_error
    if run.state["plan"] is not None:
        result["unit_count"] = len(run.state["plan"]["units"])
        result["units_closed"] = run.state["unit_index"]
    if phase not in {"load", "preflight", "preflight_accept", "finished"}:
        result["unit_id"] = run.unit()["unit_id"]
        result["material"] = run.unit()["material"]
    if phase == "checkpoint":
        result["questions"] = run.state["pass1"]["questions"]
        result["human_required_if"] = "any answer depends on practitioner judgment rather than source/library evidence"
    if phase == "land":
        result["approval_required"] = run.state["pass2"]["approval_required"]
    return result


def run_tool(repo: Path, name: str) -> str:
    result = subprocess.run(
        [sys.executable, str(repo / "PASS" / "tools" / name), "--library", str(repo / "library")],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode:
        raise RunError(f"final {name} failed:\n{result.stdout}\n{result.stderr}")
    return (result.stdout + result.stderr).strip()


def completion_path(run: Run) -> Path:
    return inside(run.root, "controller/source-completion.json")


def verify_finished(run: Run) -> dict[str, Any]:
    if run.state["phase"] != "finished":
        raise RunError("final source verification is available only after every unit has landed")
    run.source_file(required=True)
    validate_output = run_tool(run.repo, "validate.py")
    reference_output = run_tool(run.repo, "verify_references.py")
    directory = audit_dir(run)
    atomic_write(inside(directory, "final-validate.txt"), (validate_output + "\n").encode("utf-8"))
    atomic_write(inside(directory, "final-verify-references.txt"), (reference_output + "\n").encode("utf-8"))
    record = {
        "schema_version": COMPLETION_SCHEMA,
        "source_sha256": run.source_identity()["sha256"],
        "domain": run.domain,
        "unit_count": len(run.state["plan"]["units"]),
        "validate": "pass",
        "verify_references": "pass",
    }
    atomic_write(completion_path(run), (json.dumps(record, indent=2) + "\n").encode("utf-8"))
    append_event(run, {"event": "source_verified_complete", "unit_count": record["unit_count"], "source_sha256": record["source_sha256"]})
    return {"outcome": "source_complete", "verification": record, "audit": str(directory)}


def advance(run: Run) -> dict[str, Any]:
    authorization = run.unattended_authorization(required=True)
    phase = run.state["phase"]
    if phase == "preflight_accept":
        packet = run.present()
        marker = run.preflight_presentation_marker(required=True)
        path = write_packet(run, "preflight", packet, marker["sha256"])
        append_event(run, {"event": "preflight_packet_archived", "sha256": marker["sha256"], "path": path.relative_to(run.root).as_posix()})
        decision = {
            "schema_version": 1,
            "presentation_sha256": marker["sha256"],
            "subject": run.state["plan"]["subject"],
            "basis": "unattended authorization",
            "reason": "User authorized this source to continue unattended through completion; the full preflight packet was rendered and archived.",
        }
        message = run.accept_preflight(decision)
        append_event(run, {"event": "preflight_autoaccepted", "sha256": marker["sha256"], "basis": "unattended authorization"})
        return {"outcome": "advanced", "message": message, "audit_packet": str(path), "next": status(run)["next_action"]}
    if phase == "land":
        packet = run.present()
        marker = run.presentation_marker(required=True)
        unit = run.unit()["unit_id"]
        path = write_packet(run, f"{unit}-landing", packet, marker["sha256"])
        append_event(run, {"event": "landing_packet_archived", "unit_id": unit, "sha256": marker["sha256"], "path": path.relative_to(run.root).as_posix()})
        if run.state["pass2"]["approval_required"]:
            append_event(run, {"event": "human_gate_reached", "unit_id": unit, "kind": "approval_required", "sha256": marker["sha256"]})
            return {
                "outcome": "blocked_human_required",
                "unit_id": unit,
                "reason": "PASS 2 marked this delta approval_required; unattended authorization may not consume practitioner approval.",
                "audit_packet": str(path),
            }
        decision = {
            "schema_version": 1,
            "unit_id": unit,
            "presentation_sha256": marker["sha256"],
            "basis": "unattended authorization",
            "reason": "Routine delta auto-landed under the user's source-scoped unattended authorization after complete packet render and audit capture.",
        }
        message = run.land(decision)
        append_event(run, {"event": "unit_auto_landed", "unit_id": unit, "sha256": marker["sha256"], "basis": "unattended authorization"})
        return {"outcome": "advanced", "message": message, "audit_packet": str(path), "next": status(run)["next_action"]}
    if phase == "finished":
        return verify_finished(run)
    return {
        "outcome": "host_action_required",
        "phase": phase,
        "reason": "This phase requires substantive reading/adjudication by the host; the unattended runner does not fabricate PASS work.",
        "next": next_action(run, authorization is not None, True),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, help="auto-detected from the current project by default")
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("authorize", "status", "drive", "report", "advance", "revoke", "rebind-source"):
        p = sub.add_parser(command)
        p.add_argument("--run", type=Path, required=True)
        if command == "authorize":
            p.add_argument("--reason", required=True, help="record the user's explicit bounded unattended instruction")
        elif command == "rebind-source":
            p.add_argument("--source", type=Path, required=True, help="new path to the identical source bytes")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)
    try:
        repo = args.repo_root.resolve() if args.repo_root else preflight.find_repo_root(Path.cwd())
        run = Run(repo, args.run)
        if args.command == "status":
            print(json.dumps(status(run), indent=2))
            return 0
        if args.command == "report":
            print(json.dumps(progress_report(run), indent=2))
            return 0
        with run.locked():
            if args.command == "authorize":
                result: Any = authorize(run, args.reason)
            elif args.command == "revoke":
                result = revoke(run)
            elif args.command == "rebind-source":
                result = run.rebind_source(args.source)
            elif args.command == "drive":
                result = drive(run)
            elif args.command == "advance":
                result = advance(run)
            else:
                raise RunError(f"unsupported source-runner command: {args.command}")
        if isinstance(result, str):
            print(result)
            print(json.dumps(status(run), indent=2))
        else:
            print(json.dumps(result, indent=2))
        return 0
    except (OSError, preflight.PreflightError, preflight.yaml.YAMLError) as exc:
        print(f"PASS SOURCE RUN BLOCKED: {exc}", file=sys.stderr)
        return 1
