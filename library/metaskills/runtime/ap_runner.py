#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Step an Action Protocol (AP) card one step at a time.

The AP card stays the only source of its method; this helper reads it and never
changes it. It owns the order: only the current step is shown, together with the
full text of every Pattern that step names, and the next step unlocks only after
the current one is accounted for. A step is done with a statement of what was
done, a gate step passes or fails with a verdict and reason, and an ordinary step
may be skipped only with a recorded reason. Nothing is skipped silently.

It cannot see the work. A record says what the caller reports, so a false record
remains possible; omission does not. Run it from the project being worked on, by
its path in the installed skill. State lives in that project (inside the git
directory when there is one), never in the skill.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import uuid

SCHEMA_VERSION = 1
LIBRARY = Path(__file__).resolve().parents[2]
ID_RE = re.compile(r"^AP_[a-z0-9_]+$")
LIST_STEP = re.compile(r"^(\d+)\.\s+(.*)$")
BOLD_STEP = re.compile(r"^\*\*(\d+)(?:\.|\s+[—-])\s+(.*)$")
BOLD_LEAD = re.compile(r"^\*\*([^*]+?)\*\*")
PAT_REF = re.compile(r"`(PAT_[a-z0-9_]+)`")
AP_REF = re.compile(r"`(AP_[a-z0-9_]+)`")


class RunnerError(Exception):
    pass


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# ------------------------------------------------------------------ cards

def split_card(text: str) -> tuple[dict[str, str], str]:
    """Front matter scalars and the body. Only flat `key: value` lines are read."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end < 0:
        return {}, text
    meta = {}
    for line in text[3:end].splitlines():
        match = re.match(r"^([a-z_]+):\s*(.*)$", line)
        if match:
            meta[match.group(1)] = match.group(2).strip().strip("'\"")
    return meta, text[end + 4:].lstrip("\n")


def find_card(library: Path, object_id: str) -> Path | None:
    matches = [p for p in library.rglob(f"{object_id}.md") if "runtime" not in p.relative_to(library).parts]
    return matches[0] if len(matches) == 1 else None


def section(body: str, name: str) -> str:
    match = re.search(rf"(?ms)^## {re.escape(name)}[ \t]*\n(.*?)(?=^## |\Z)", body)
    return match.group(1).strip() if match else ""


def parse_steps(flow: str) -> tuple[str, list[dict], str]:
    """Entry text, ordered steps and closing text from a Steps / Flow section.

    Accepts a numbered list (`1. ...`) or bold-numbered paragraphs (`**1. ...**`,
    `**1 — ...**`). Numbering must run 1..N without gaps.
    """
    lines = flow.splitlines()
    marks = []
    for index, line in enumerate(lines):
        match = LIST_STEP.match(line) or BOLD_STEP.match(line)
        if match:
            marks.append((index, int(match.group(1))))
    if not marks:
        raise RunnerError("the AP's Steps / Flow section has no numbered steps")
    if [number for _, number in marks] != list(range(1, len(marks) + 1)):
        raise RunnerError("the AP's steps are not numbered 1..N in order")
    entry = "\n".join(lines[:marks[0][0]]).strip()
    closing = ""
    steps = []
    for position, (start, number) in enumerate(marks):
        stop = marks[position + 1][0] if position + 1 < len(marks) else len(lines)
        chunk = lines[start:stop]
        if position + 1 == len(marks):
            # A trailing unindented bold paragraph such as **Completion.** closes the AP.
            for offset, line in enumerate(chunk[1:], 1):
                if BOLD_LEAD.match(line) and not BOLD_STEP.match(line) and chunk[offset - 1].strip() == "":
                    closing = "\n".join(chunk[offset:]).strip()
                    chunk = chunk[:offset]
                    break
        text = "\n".join(chunk).strip()
        first = LIST_STEP.sub(r"\2", chunk[0]) if LIST_STEP.match(chunk[0]) else chunk[0]
        lead = BOLD_LEAD.match(first.strip()) or BOLD_LEAD.match(chunk[0])
        title = re.sub(r"^\d+(?:\.|\s+[—-])\s+", "", lead.group(1)).strip() if lead else first.strip()[:80]
        gate = bool(re.search(r"\bgate\b", title, re.I)) or bool(re.search(r"(?m)^\s*\*{1,2}Gate[.:]", text))
        steps.append({"number": number, "title": title.rstrip("."), "text": text, "gate": gate})
    return entry, steps, closing


def load_ap(library: Path, object_id: str) -> dict:
    if not ID_RE.fullmatch(object_id):
        raise RunnerError(f"not an AP object ID: {object_id}")
    path = find_card(library, object_id)
    if path is None:
        raise RunnerError(f"{object_id} is not in this installation's library")
    raw = path.read_bytes()
    meta, body = split_card(normalized(raw.decode("utf-8")))
    if meta.get("object_id") != object_id or meta.get("object_type") != "ap":
        raise RunnerError(f"{path.name} does not declare object_id {object_id} with object_type ap")
    title = next((line[2:].strip() for line in body.splitlines() if line.startswith("# ")), object_id)
    entry, steps, closing = parse_steps(section(body, "Steps / Flow"))
    return {
        "object_id": object_id, "path": path.relative_to(library).as_posix(), "sha256": sha256(raw),
        "title": title, "objective": section(body, "Objective"), "entry": entry, "steps": steps, "closing": closing,
    }


def card_body(library: Path, object_id: str) -> str | None:
    path = find_card(library, object_id)
    if path is None:
        return None
    return split_card(normalized(path.read_text(encoding="utf-8")))[1].strip()


def normalized(text: str) -> str:
    """Cards may be checked out with Windows line endings."""
    return "\n".join(text.splitlines())


# ------------------------------------------------------------------ state

def state_dir() -> Path:
    override = os.environ.get("SKILLFORGE_AP_STATE")
    if override:
        return Path(override)
    try:
        done = subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
                              capture_output=True, text=True, timeout=30)
        if done.returncode == 0 and done.stdout.strip():
            return Path(done.stdout.strip()) / "skillforge" / "ap-runs"
    except (OSError, subprocess.SubprocessError):
        pass
    return Path.cwd() / ".skillforge" / "ap-runs"


def run_path(run_id: str) -> Path:
    if not re.fullmatch(r"[a-z0-9_-]+", run_id):
        raise RunnerError(f"invalid run id: {run_id}")
    return state_dir() / f"{run_id}.json"


def read_run(run_id: str) -> dict:
    path = run_path(run_id)
    if not path.is_file():
        raise RunnerError(f"no AP run named {run_id}")
    return json.loads(path.read_text(encoding="utf-8"))


def write_run(run: dict) -> None:
    path = run_path(run["run_id"])
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    temporary.write_text(json.dumps(run, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(temporary, path)


@contextmanager
def locked(run_id: str):
    path = run_path(run_id).with_suffix(".lock")
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        raise RunnerError(f"another command is updating {run_id}; if none is running, delete {path}") from exc
    os.close(descriptor)
    try:
        yield
    finally:
        path.unlink(missing_ok=True)


def all_runs() -> list[dict]:
    folder = state_dir()
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(folder.glob("*.json"))] if folder.is_dir() else []


def open_runs() -> list[dict]:
    return [run for run in all_runs() if run["status"] == "active"]


def select(run_id: str | None) -> dict:
    if run_id:
        return read_run(run_id)
    active = open_runs()
    if len(active) == 1:
        return active[0]
    if not active:
        raise RunnerError("no active AP run; start one with `start --ap <AP_id>`")
    listing = ", ".join(f"{r['run_id']} ({r['ap']['object_id']})" for r in active)
    raise RunnerError(f"several AP runs are active; name one with --run: {listing}")


def verified_ap(library: Path, run: dict) -> dict:
    """The run's AP, refusing if the card changed since the run began."""
    ap = load_ap(library, run["ap"]["object_id"])
    if ap["sha256"] != run["ap"]["sha256"]:
        raise RunnerError(f"{ap['object_id']} changed since run {run['run_id']} began; abandon this run and start a new one")
    return ap


# ------------------------------------------------------------------ views

def show_step(library: Path, run: dict, ap: dict) -> str:
    if run["status"] != "active":
        return f"Run {run['run_id']} is {run['status']}. Use `record --run {run['run_id']}` for its completion record."
    step = ap["steps"][run["cursor"] - 1]
    total = len(ap["steps"])
    out = [f"{ap['object_id']} — {ap['title']}", f"Run {run['run_id']}: step {step['number']} of {total}"
           + ("  [GATE]" if step["gate"] else "")]
    if run.get("task"):
        out.append(f"Task: {run['task']}")
    if step["number"] == 1:
        out += ["", "OBJECTIVE", ap["objective"]]
        if ap["entry"]:
            out += ["", "ENTRY", ap["entry"]]
    if ap["closing"] and step["number"] in {1, total}:
        # Text after the last step is a completion check or a branch for another
        # situation; either can decide how the run should be approached.
        out += ["", "AFTER THE STEPS", ap["closing"]]
    out += ["", f"STEP {step['number']}", step["text"]]
    for object_id in dict.fromkeys(PAT_REF.findall(step["text"])):
        body = card_body(library, object_id)
        out += ["", f"--- {object_id} " + ("---" if body else "(not in this installation) ---")]
        if body:
            out.append(body)
    for object_id in dict.fromkeys(AP_REF.findall(step["text"])):
        if object_id != ap["object_id"]:
            out += ["", f"This step names {object_id}: run it with `start --ap {object_id}` and finish it before this step is done."]
    out.append("")
    if step["gate"]:
        out.append(f"This is a gate. Judge it, then: gate --run {run['run_id']} --step {step['number']} --verdict pass|fail --reason \"<evidence>\"")
    else:
        out.append(f"When the work is done: done --run {run['run_id']} --step {step['number']} --did \"<what you did>\" [--artifact <path>]")
        out.append(f"If the step genuinely does not apply: skip --run {run['run_id']} --step {step['number']} --reason \"<why>\"")
    out.append("Later steps stay hidden until this one is accounted for.")
    return "\n".join(out)


def progress(run: dict) -> str:
    total = len(run["ap"]["steps"])
    marks = []
    for step in run["ap"]["steps"]:
        entry = latest(run, step["number"])
        marks.append(f"{step['number']}:{entry['outcome'] if entry else ('current' if step['number'] == run['cursor'] and run['status'] == 'active' else 'pending')}")
    return f"{run['run_id']} {run['ap']['object_id']} [{run['status']}] {min(run['cursor'], total)}/{total} — " + " ".join(marks)


def latest(run: dict, number: int) -> dict | None:
    entries = [e for e in run["records"] if e["step"] == number and not e.get("superseded")]
    return entries[-1] if entries else None


# ------------------------------------------------------------------ commands

def start(library: Path, object_id: str, task: str | None) -> dict:
    ap = load_ap(library, object_id)
    for run in open_runs():
        if run["ap"]["object_id"] == object_id and run.get("task") == task:
            raise RunnerError(f"run {run['run_id']} is already stepping {object_id} for this task; continue it with `current --run {run['run_id']}`")
    run_id = f"{object_id[3:][:40].rstrip('_').replace('_', '-')}-{uuid.uuid4().hex[:6]}"
    run = {
        "schema_version": SCHEMA_VERSION, "run_id": run_id, "task": task, "status": "active", "cursor": 1,
        "started_at": now(), "finished_at": None,
        "ap": {"object_id": object_id, "path": ap["path"], "sha256": ap["sha256"],
               "steps": [{"number": s["number"], "title": s["title"], "gate": s["gate"]} for s in ap["steps"]]},
        "records": [],
    }
    write_run(run)
    return run


def require_text(value: str | None, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RunnerError(f"{label} is required and cannot be empty")
    return value.strip()


def account(library: Path, run_id: str | None, number: int, outcome: str, text: str, artifacts: list[str] | None = None) -> dict:
    run = select(run_id)
    with locked(run["run_id"]):
        run = read_run(run["run_id"])
        if run["status"] != "active":
            raise RunnerError(f"run {run['run_id']} is {run['status']}")
        ap = verified_ap(library, run)
        step = ap["steps"][run["cursor"] - 1]
        if number != step["number"]:
            raise RunnerError(f"step {step['number']} is the current step; step {number} cannot be accounted for now")
        if outcome in {"done", "skipped"} and step["gate"]:
            raise RunnerError(f"step {number} is a gate; it needs `gate --verdict pass|fail --reason`, and a gate cannot be skipped")
        if outcome in {"passed", "failed"} and not step["gate"]:
            raise RunnerError(f"step {number} is not a gate; use `done` or `skip`")
        entry = {"step": number, "outcome": outcome, "at": now(),
                 ("did" if outcome == "done" else "reason"): require_text(text, "--did" if outcome == "done" else "--reason")}
        if artifacts:
            missing = [a for a in artifacts if not Path(a).exists()]
            if missing:
                raise RunnerError(f"artifact not found: {', '.join(missing)}")
            entry["artifacts"] = [{"path": a, "sha256": sha256(Path(a).read_bytes()) if Path(a).is_file() else None} for a in artifacts]
        run["records"].append(entry)
        if outcome != "failed":
            run["cursor"] += 1
            if run["cursor"] > len(ap["steps"]):
                run["status"], run["finished_at"] = "finished", now()
        write_run(run)
    return run


def back(library: Path, run_id: str | None, target: int, reason: str) -> dict:
    run = select(run_id)
    with locked(run["run_id"]):
        run = read_run(run["run_id"])
        if run["status"] != "active":
            raise RunnerError(f"run {run['run_id']} is {run['status']}")
        verified_ap(library, run)
        if not 1 <= target <= run["cursor"]:
            raise RunnerError(f"can only return to a step from 1 to the current step {run['cursor']}")
        reason = require_text(reason, "--reason")
        for entry in run["records"]:
            if entry["step"] >= target:
                entry["superseded"] = True
        run["records"].append({"step": target, "outcome": "reopened", "reason": reason, "at": now(), "superseded": True})
        run["cursor"] = target
        write_run(run)
    return run


def abandon(run_id: str, reason: str) -> dict:
    with locked(run_id):
        run = read_run(run_id)
        if run["status"] != "active":
            raise RunnerError(f"run {run_id} is already {run['status']}")
        run.update(status="abandoned", finished_at=now(), abandon_reason=require_text(reason, "--reason"))
        write_run(run)
    return run


def completion_record(run: dict) -> dict:
    steps = []
    for step in run["ap"]["steps"]:
        entry = latest(run, step["number"])
        steps.append({"step": step["number"], "title": step["title"], "gate": step["gate"],
                      **({k: v for k, v in entry.items() if k not in {"step", "superseded"}} if entry else {"outcome": "pending"})})
    return {
        "schema_version": SCHEMA_VERSION, "run_id": run["run_id"], "ap": run["ap"]["object_id"],
        "card_sha256": run["ap"]["sha256"], "task": run.get("task"), "status": run["status"],
        "complete": run["status"] == "finished", "started_at": run["started_at"], "finished_at": run["finished_at"],
        "skipped": [s["step"] for s in steps if s["outcome"] == "skipped"],
        "failed_gate_attempts": sum(1 for e in run["records"] if e["outcome"] == "failed"),
        "reopened": [e for e in run["records"] if e["outcome"] == "reopened"],
        "steps": steps,
    }


# ------------------------------------------------------------------ CLI

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--library", type=Path, default=LIBRARY, help=argparse.SUPPRESS)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("start", help="begin stepping an AP; shows step 1 only")
    p.add_argument("--ap", required=True, help="AP object ID, e.g. AP_design_a_parallel_decomposition")
    p.add_argument("--task", help="one line naming the task this run serves")
    for name, text in (("current", "show the current step and the Patterns it names"),
                       ("status", "one-line progress of a run (or every run with --all)"),
                       ("record", "the run's completion record as JSON")):
        p = sub.add_parser(name, help=text)
        p.add_argument("--run")
        if name == "status":
            p.add_argument("--all", action="store_true")
    p = sub.add_parser("done", help="account for the current step and unlock the next")
    p.add_argument("--run")
    p.add_argument("--step", type=int, required=True)
    p.add_argument("--did", required=True, help="what was actually done in this step")
    p.add_argument("--artifact", action="append", help="a file this step produced (repeatable)")
    p = sub.add_parser("gate", help="judge a gate step; a fail keeps it current")
    p.add_argument("--run")
    p.add_argument("--step", type=int, required=True)
    p.add_argument("--verdict", choices=("pass", "fail"), required=True)
    p.add_argument("--reason", required=True, help="the evidence for the verdict")
    p = sub.add_parser("skip", help="record that a non-gate step does not apply")
    p.add_argument("--run")
    p.add_argument("--step", type=int, required=True)
    p.add_argument("--reason", required=True)
    p = sub.add_parser("back", help="reopen an earlier step when a gate or discovery requires revision")
    p.add_argument("--run")
    p.add_argument("--to", type=int, required=True)
    p.add_argument("--reason", required=True)
    p = sub.add_parser("abandon", help="stop a run on explicit instruction")
    p.add_argument("--run", required=True)
    p.add_argument("--reason", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    # Cards carry dashes and arrows; a Windows console code page must not crash
    # or garble the step a model is about to act on.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    args = build_parser().parse_args(argv)
    library = args.library.resolve()
    try:
        if args.command == "start":
            run = start(library, args.ap, args.task)
            print(show_step(library, run, verified_ap(library, run)))
        elif args.command == "current":
            run = select(args.run)
            print(show_step(library, run, verified_ap(library, run)) if run["status"] == "active" else progress(run))
        elif args.command == "status":
            runs = all_runs() if args.all else [select(args.run)]
            print("\n".join(progress(r) for r in runs) or "no AP runs")
        elif args.command == "record":
            print(json.dumps(completion_record(select(args.run)), indent=2, ensure_ascii=False))
        elif args.command in {"done", "gate", "skip"}:
            outcome = {"done": "done", "skip": "skipped"}.get(args.command) or ("passed" if args.verdict == "pass" else "failed")
            text = args.did if args.command == "done" else args.reason
            run = account(library, args.run, args.step, outcome, text, getattr(args, "artifact", None))
            if outcome == "failed":
                print(f"Gate {args.step} failed and stays current. Revise the work (use `back --to <step>` to reopen an "
                      f"earlier step), then judge the gate again.\n")
            ap = verified_ap(library, run)
            print(show_step(library, run, ap) if run["status"] == "active"
                  else f"{ap['object_id']} finished: every step is accounted for.\n{ap['closing']}\n"
                       f"Completion record: record --run {run['run_id']}".replace("\n\n", "\n"))
        elif args.command == "back":
            run = back(library, args.run, args.to, args.reason)
            print(show_step(library, run, verified_ap(library, run)))
        elif args.command == "abandon":
            print(progress(abandon(args.run, args.reason)))
        return 0
    except (RunnerError, OSError, ValueError, UnicodeDecodeError) as exc:
        print(f"AP RUNNER BLOCKED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
