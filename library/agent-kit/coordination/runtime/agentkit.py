#!/usr/bin/env python3
"""agent-kit coordination runtime: keeps several agents working in one repository
from stepping on each other.

Canonical live state is a SQLite database, never hand-edited Markdown. Every task
declares the paths and named resources it will touch; a task cannot be claimed
while an open task holds an overlapping scope. Claims are leases renewed by
heartbeat, so a dead worker's task returns to the queue. Human-readable boards are
generated with `status`.

Run it from inside the project being coordinated, using its path in the
installed skill: `python <skill>/library/agent-kit/coordination/runtime/agentkit.py
--help`. It keeps all state in that project and never writes to the skill.
Standard library only.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

VERSION = "1.0.0"
# Bump when the database layout changes. Every agent in a project may run its
# own installed copy; an older copy must refuse a store a newer one has changed.
SCHEMA_VERSION = 1
DEFAULT_LEASE_MINUTES = 30

# States in which a task's scope is held against other tasks. Work that exists
# but has not been merged still owns its files.
HOLDING = ("claimed", "blocked", "review", "rework", "accepted")
CLAIMABLE = ("ready", "rework")
DONE = ("accepted", "closed")
STATES = ("proposed", "ready", "claimed", "blocked", "review", "rework", "accepted", "closed")

EXIT_REFUSED = 1
EXIT_STALE = 3

SCHEMA = """
CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS workers (
    name TEXT PRIMARY KEY,
    role TEXT NOT NULL CHECK (role IN ('lead', 'worker')),
    label TEXT NOT NULL DEFAULT '',
    capabilities TEXT NOT NULL DEFAULT '[]',
    registered_at REAL NOT NULL,
    last_seen REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    seq INTEGER NOT NULL UNIQUE,
    rev INTEGER NOT NULL DEFAULT 1,
    state TEXT NOT NULL,
    priority INTEGER NOT NULL DEFAULT 0,
    spec TEXT NOT NULL,
    owner TEXT,
    last_owner TEXT,
    claimed_rev INTEGER,
    lease_expires REAL,
    attempt INTEGER NOT NULL DEFAULT 0,
    note TEXT NOT NULL DEFAULT '',
    created_by TEXT NOT NULL,
    created_at REAL NOT NULL,
    updated_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS deps (
    task TEXT NOT NULL,
    depends_on TEXT NOT NULL,
    PRIMARY KEY (task, depends_on)
);
CREATE TABLE IF NOT EXISTS evidence (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task TEXT NOT NULL,
    attempt INTEGER NOT NULL,
    actor TEXT NOT NULL,
    at REAL NOT NULL,
    data TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    at REAL NOT NULL,
    actor TEXT NOT NULL,
    task TEXT,
    kind TEXT NOT NULL,
    data TEXT NOT NULL DEFAULT '{}'
);
"""

SOURCES = (
    "user_directive", "imported_issue", "imported_backlog", "failing_test",
    "build_failure", "dependency_requirement", "lead_discovery", "worker_discovery",
)


class Refused(Exception):
    """An operation the protocol does not allow; the message says why."""

    def __init__(self, message: str, code: int = EXIT_REFUSED):
        super().__init__(message)
        self.code = code


# --------------------------------------------------------------------------- paths


def project_home() -> Path:
    """Outside git, the nearest directory at or above the current one that
    already has an `.agent-kit/`; otherwise the current directory."""
    cwd = Path.cwd().resolve()
    for candidate in (cwd, *cwd.parents):
        if (candidate / ".agent-kit").is_dir():
            return candidate
    return cwd


def git(args: list[str], cwd: Path) -> str | None:
    try:
        done = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return done.stdout.rstrip() if done.returncode == 0 else None


def git_ok(args: list[str], cwd: Path) -> bool | None:
    try:
        done = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return done.returncode == 0


def database_path() -> Path:
    """AGENTKIT_DB wins; in git the store sits in the common git dir so every
    worktree shares it and it is never committed; otherwise `.agent-kit/state/`
    in the project (add `.agent-kit/state/` to its ignore rules)."""
    override = os.environ.get("AGENTKIT_DB")
    if override:
        return Path(override)
    common = git(["rev-parse", "--path-format=absolute", "--git-common-dir"], Path.cwd())
    if common:
        return Path(common) / "agent-kit" / "state.db"
    return project_home() / ".agent-kit" / "state" / "state.db"


# ----------------------------------------------------------------------- matching


def norm(path: str) -> str:
    path = path.replace("\\", "/").strip()
    while path.startswith("./"):
        path = path[2:]
    return path.strip("/")


def has_magic(segment: str) -> bool:
    return any(ch in segment for ch in "*?[")


def glob_regex(pattern: str) -> re.Pattern:
    out, i, pattern = [], 0, norm(pattern)
    while i < len(pattern):
        if pattern.startswith("**/", i):
            out.append("(?:.*/)?")
            i += 3
        elif pattern.startswith("**", i):
            out.append(".*")
            i += 2
        elif pattern[i] == "*":
            out.append("[^/]*")
            i += 1
        elif pattern[i] == "?":
            out.append("[^/]")
            i += 1
        else:
            out.append(re.escape(pattern[i]))
            i += 1
    # A literal directory also covers everything below it.
    return re.compile("".join(out) + "(?:/.*)?$", re.IGNORECASE)


def path_matches(path: str, pattern: str) -> bool:
    return bool(glob_regex(pattern).match(norm(path)))


def literal_prefix(pattern: str) -> list[str]:
    parts = []
    for segment in norm(pattern).split("/"):
        if has_magic(segment):
            break
        parts.append(segment.casefold())
    return parts


def globs_overlap(a: str, b: str) -> bool:
    """Conservative: may report an overlap that no real file exhibits, never the
    reverse. Over-reporting costs a queue wait; under-reporting costs a collision."""
    if not has_magic(a):
        return path_matches(a, b) or path_matches(b, a) if not has_magic(b) else path_matches(a, b)
    if not has_magic(b):
        return path_matches(b, a)
    pa, pb = literal_prefix(a), literal_prefix(b)
    shorter = min(len(pa), len(pb))
    return pa[:shorter] == pb[:shorter]


def scope_conflicts(spec_a: dict, spec_b: dict) -> list[str]:
    found = []
    for a in spec_a.get("paths", []):
        for b in spec_b.get("paths", []):
            if globs_overlap(a, b):
                found.append(f"path {a} ~ {b}")
    shared = {r.casefold() for r in spec_a.get("resources", [])} & {r.casefold() for r in spec_b.get("resources", [])}
    found.extend(f"resource {r}" for r in sorted(shared))
    return found


# ---------------------------------------------------------------------- database


class Store:
    def __init__(self, path: Path):
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(str(path), timeout=30, isolation_level=None)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA busy_timeout = 30000")
        self.db.executescript(SCHEMA)
        self.db.execute("INSERT OR IGNORE INTO meta VALUES ('schema', ?)", (str(SCHEMA_VERSION),))
        stored = int(self.db.execute("SELECT value FROM meta WHERE key = 'schema'").fetchone()[0])
        if stored > SCHEMA_VERSION:
            self.db.close()
            raise Refused(f"{path} uses store schema {stored}, but this agentkit {VERSION} understands "
                          f"{SCHEMA_VERSION}; update this agent's installed skill before coordinating")

    def begin(self) -> None:
        # IMMEDIATE takes the write lock before reading, so two claims of the same
        # task serialize and the second one sees the first one's result.
        self.db.execute("BEGIN IMMEDIATE")

    def commit(self) -> None:
        self.db.execute("COMMIT")

    def rollback(self) -> None:
        if self.db.in_transaction:
            self.db.execute("ROLLBACK")

    def event(self, actor: str, task: str | None, kind: str, **data) -> None:
        self.db.execute(
            "INSERT INTO events (at, actor, task, kind, data) VALUES (?, ?, ?, ?, ?)",
            (time.time(), actor, task, kind, json.dumps(data, sort_keys=True)),
        )

    def worker(self, name: str | None) -> sqlite3.Row:
        if not name:
            raise Refused("say who you are: --as <name> (or set AGENTKIT_AS)")
        row = self.db.execute("SELECT * FROM workers WHERE name = ?", (name,)).fetchone()
        if row is None:
            raise Refused(f"{name} is not registered; run: register {name} --role worker --cap ...")
        self.db.execute("UPDATE workers SET last_seen = ? WHERE name = ?", (time.time(), name))
        return row

    def lead(self, name: str | None) -> sqlite3.Row:
        row = self.worker(name)
        if row["role"] != "lead":
            raise Refused(f"{name} is a worker; only a lead may do this")
        return row

    def task(self, task_id: str) -> sqlite3.Row:
        row = self.db.execute("SELECT * FROM tasks WHERE id = ?", (task_id.upper(),)).fetchone()
        if row is None:
            raise Refused(f"no task {task_id}")
        return row

    def deps(self, task_id: str) -> list[str]:
        return [r[0] for r in self.db.execute(
            "SELECT depends_on FROM deps WHERE task = ? ORDER BY depends_on", (task_id,))]

    def reclaim_expired(self, actor: str) -> list[str]:
        now = time.time()
        rows = self.db.execute(
            "SELECT * FROM tasks WHERE state = 'claimed' AND lease_expires IS NOT NULL AND lease_expires < ?",
            (now,),
        ).fetchall()
        for row in rows:
            state = "rework" if row["note"].startswith("rework:") else "ready"
            self.db.execute(
                "UPDATE tasks SET state = ?, owner = NULL, last_owner = ?, lease_expires = NULL, "
                "claimed_rev = NULL, updated_at = ? WHERE id = ?",
                (state, row["owner"], now, row["id"]),
            )
            self.event(actor, row["id"], "lease_expired", owner=row["owner"], expired_at=row["lease_expires"])
        return [row["id"] for row in rows]


# -------------------------------------------------------------------- eligibility


def spec_of(row: sqlite3.Row) -> dict:
    return json.loads(row["spec"])


def blockers(store: Store, row: sqlite3.Row, worker: sqlite3.Row) -> list[str]:
    """Every reason `worker` may not claim `row` right now; empty means eligible."""
    reasons = []
    if row["state"] not in CLAIMABLE:
        reasons.append(f"state is {row['state']}")
    for dep in store.deps(row["id"]):
        dep_state = store.task(dep)["state"]
        if dep_state not in DONE:
            reasons.append(f"depends on {dep} ({dep_state})")
    spec = spec_of(row)
    missing = sorted(set(spec.get("needs", [])) - set(json.loads(worker["capabilities"])))
    if missing:
        reasons.append("needs capabilities " + ", ".join(missing))
    for other in store.db.execute(
        "SELECT * FROM tasks WHERE id != ? AND state IN (%s)" % ",".join("?" * len(HOLDING)),
        (row["id"], *HOLDING),
    ):
        overlap = scope_conflicts(spec, spec_of(other))
        if overlap:
            reasons.append(f"collides with {other['id']} ({other['state']}, {other['owner'] or other['last_owner'] or '-'}): "
                           + "; ".join(overlap))
    return reasons


def base_check(spec: dict, cwd: Path) -> str | None:
    base = spec.get("base")
    if not base:
        return None
    if git(["rev-parse", "--git-dir"], cwd) is None:
        return None  # not a git checkout; the base precondition cannot apply
    if git(["rev-parse", "--verify", "--quiet", base + "^{commit}"], cwd) is None:
        return f"base {base} does not exist in this checkout; fetch it or fix the task"
    if not git_ok(["merge-base", "--is-ancestor", base, "HEAD"], cwd):
        return f"HEAD does not contain base {base}; this checkout would drop its work (rebase or switch first)"
    return None


def changed_files(spec: dict, cwd: Path) -> list[str] | None:
    if git(["rev-parse", "--git-dir"], cwd) is None:
        return None
    files = set()
    status = git(["status", "--porcelain", "--untracked-files=all"], cwd) or ""
    for line in status.splitlines():
        name = line[3:]
        if " -> " in name:
            name = name.split(" -> ", 1)[1]
        files.add(norm(name.strip('"')))
    base = spec.get("base")
    if base:
        committed = git(["diff", "--name-only", f"{base}...HEAD"], cwd)
        files.update(norm(f) for f in (committed or "").splitlines() if f)
    return sorted(f for f in files if f and not f.startswith(".agent-kit/state/"))


# ---------------------------------------------------------------------- rendering


def ts(epoch: float | None) -> str:
    if not epoch:
        return "-"
    return datetime.fromtimestamp(epoch, timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def task_dict(store: Store, row: sqlite3.Row) -> dict:
    return {
        "id": row["id"], "rev": row["rev"], "state": row["state"], "priority": row["priority"],
        "owner": row["owner"], "last_owner": row["last_owner"], "claimed_rev": row["claimed_rev"],
        "lease_expires": ts(row["lease_expires"]), "attempt": row["attempt"], "note": row["note"],
        "depends_on": store.deps(row["id"]), "created_by": row["created_by"], "spec": spec_of(row),
    }


def describe(store: Store, row: sqlite3.Row) -> str:
    spec = spec_of(row)
    lines = [
        f"{row['id']} r{row['rev']} [{row['state']}] {spec['title']}",
        f"  goal: {spec['goal']}",
        f"  source: {spec['source']}   priority: {row['priority']}   created by: {row['created_by']}",
    ]
    if row["owner"] or row["last_owner"]:
        lines.append(f"  owner: {row['owner'] or '-'}   last owner: {row['last_owner'] or '-'}   "
                     f"attempt: {row['attempt']}   lease until: {ts(row['lease_expires'])}")
    if row["owner"] and row["claimed_rev"] and row["claimed_rev"] != row["rev"]:
        lines.append(f"  STALE: claimed at r{row['claimed_rev']}, spec is now r{row['rev']}")
    labels = [("base", "base"), ("paths", "paths"), ("resources", "resources"), ("needs", "needs"),
              ("deliverables", "deliverables"), ("non_scope", "NOT in scope"), ("verify", "verify"),
              ("evidence", "evidence required"), ("danger", "danger zones")]
    for key, label in labels:
        value = spec.get(key)
        if value:
            lines.append(f"  {label}: " + (value if isinstance(value, str) else "; ".join(value)))
    deps = store.deps(row["id"])
    if deps:
        lines.append("  after: " + ", ".join(f"{d} ({store.task(d)['state']})" for d in deps))
    if row["note"]:
        lines.append(f"  note: {row['note']}")
    return "\n".join(lines)


def board(store: Store) -> str:
    now = time.time()
    out = [f"# Agent board", "", f"Generated {ts(now)} by agent-kit {VERSION} from {store.path}. "
           "Do not edit; it is regenerated from the coordination store.", ""]
    rows = store.db.execute("SELECT * FROM tasks ORDER BY seq").fetchall()
    for state in STATES:
        group = [r for r in rows if r["state"] == state]
        if not group or state == "closed":
            continue
        out += [f"## {state} ({len(group)})", "", "| Task | Title | Owner | Scope | After |", "|---|---|---|---|---|"]
        for r in group:
            spec = spec_of(r)
            scope = ", ".join(spec.get("paths", []) + [f"@{x}" for x in spec.get("resources", [])]) or "-"
            owner = r["owner"] or (f"({r['last_owner']})" if r["last_owner"] else "-")
            out.append(f"| {r['id']} r{r['rev']} | {spec['title']} | {owner} | {scope} | {', '.join(store.deps(r['id'])) or '-'} |")
        out.append("")
    closed = sum(1 for r in rows if r["state"] == "closed")
    out += [f"Closed: {closed}", "", "## Workers", "", "| Name | Role | Capabilities | Last seen |", "|---|---|---|---|"]
    for w in store.db.execute("SELECT * FROM workers ORDER BY role, name"):
        label = f"{w['role']} ({w['label']})" if w["label"] else w["role"]
        out.append(f"| {w['name']} | {label} | {', '.join(json.loads(w['capabilities'])) or '-'} | {ts(w['last_seen'])} |")
    return "\n".join(out) + "\n"


# ----------------------------------------------------------------------- commands


def split_list(values: list[str] | None) -> list[str]:
    out = []
    for value in values or []:
        out.extend(v.strip() for v in value.split(",") if v.strip())
    return out


def spec_from(args, base: dict | None = None) -> dict:
    spec = dict(base or {})
    for key in ("title", "goal", "base", "source"):
        value = getattr(args, key, None)
        if value is not None:
            spec[key] = value
    for key, attr in (("paths", "path"), ("resources", "resource"), ("needs", "need"),
                      ("deliverables", "deliverable"), ("non_scope", "non_scope"), ("verify", "verify"),
                      ("evidence", "evidence"), ("danger", "danger")):
        values = getattr(args, attr, None)
        if values is not None:
            spec[key] = [norm(v) for v in values] if key == "paths" else (
                split_list(values) if key in ("needs", "resources", "evidence") else list(values))
    if not spec.get("title") or not spec.get("goal"):
        raise Refused("a task needs --title and --goal")
    if spec.get("source") not in SOURCES:
        raise Refused("--source must be one of: " + ", ".join(SOURCES))
    return spec


def check_deps(store: Store, task_id: str, deps: list[str]) -> list[str]:
    deps = sorted({d.upper() for d in deps})
    for dep in deps:
        store.task(dep)
        if dep == task_id:
            raise Refused(f"{task_id} cannot depend on itself")
    # Reject cycles: walk from each new dependency and look for task_id.
    stack, seen = list(deps), set()
    while stack:
        current = stack.pop()
        if current == task_id:
            raise Refused(f"dependency cycle through {task_id}")
        if current not in seen:
            seen.add(current)
            stack.extend(store.deps(current))
    return deps


def cmd_register(store: Store, args) -> str:
    now = time.time()
    caps = sorted(set(split_list(args.cap)))
    store.db.execute(
        "INSERT INTO workers (name, role, label, capabilities, registered_at, last_seen) VALUES (?, ?, ?, ?, ?, ?) "
        "ON CONFLICT(name) DO UPDATE SET role = excluded.role, label = excluded.label, "
        "capabilities = excluded.capabilities, last_seen = excluded.last_seen",
        (args.name, args.role, args.label or "", json.dumps(caps), now, now),
    )
    store.event(args.name, None, "register", role=args.role, capabilities=caps, label=args.label or "")
    held = store.db.execute("SELECT id, state FROM tasks WHERE owner = ?", (args.name,)).fetchall()
    resume = "".join(f"\n  you hold {r['id']} ({r['state']}) - run: show {r['id']}" for r in held)
    return f"registered {args.name} as {args.role}; capabilities: {', '.join(caps) or '(none)'}{resume}"


def cmd_add(store: Store, args) -> str:
    actor = store.worker(args.actor)
    is_lead = actor["role"] == "lead"
    if args.source is None:
        args.source = "user_directive" if is_lead else "worker_discovery"
    spec = spec_from(args)
    seq = (store.db.execute("SELECT MAX(seq) FROM tasks").fetchone()[0] or 0) + 1
    task_id = f"T{seq:03d}"
    deps = check_deps(store, task_id, args.after or [])
    # Discovery is not permission: only a lead can put work straight into the queue.
    state = "proposed" if (args.proposed or not is_lead) else "ready"
    now = time.time()
    store.db.execute(
        "INSERT INTO tasks (id, seq, state, priority, spec, created_by, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (task_id, seq, state, args.priority or 0, json.dumps(spec, sort_keys=True), args.actor, now, now),
    )
    store.db.executemany("INSERT INTO deps VALUES (?, ?)", [(task_id, d) for d in deps])
    store.event(args.actor, task_id, "add", state=state, spec=spec, after=deps)
    return f"{task_id} added as {state}" + ("" if state == "ready" else " (a lead must approve it)")


def cmd_revise(store: Store, args) -> str:
    store.lead(args.actor)
    row = store.task(args.task)
    if row["state"] == "closed":
        raise Refused(f"{row['id']} is closed")
    spec = spec_from(args, spec_of(row))
    material = spec != spec_of(row)
    rev = row["rev"] + (1 if material else 0)
    priority = row["priority"] if args.priority is None else args.priority
    store.db.execute("UPDATE tasks SET spec = ?, rev = ?, priority = ?, updated_at = ? WHERE id = ?",
                     (json.dumps(spec, sort_keys=True), rev, priority, time.time(), row["id"]))
    if args.after is not None:
        deps = check_deps(store, row["id"], args.after)
        store.db.execute("DELETE FROM deps WHERE task = ?", (row["id"],))
        store.db.executemany("INSERT INTO deps VALUES (?, ?)", [(row["id"], d) for d in deps])
    store.event(args.actor, row["id"], "revise", rev=rev, spec=spec, priority=priority, after=args.after)
    stale = f"; {row['owner']} is now working a stale revision until they ack" if material and row["owner"] else ""
    return f"{row['id']} is r{rev}{stale}"


def cmd_approve(store: Store, args) -> str:
    store.lead(args.actor)
    row = store.task(args.task)
    if row["state"] != "proposed":
        raise Refused(f"{row['id']} is {row['state']}, not proposed")
    store.db.execute("UPDATE tasks SET state = 'ready', updated_at = ? WHERE id = ?", (time.time(), row["id"]))
    store.event(args.actor, row["id"], "approve")
    return f"{row['id']} is ready"


def cmd_next(store: Store, args) -> str:
    worker = store.worker(args.actor)
    store.reclaim_expired(args.actor)
    held = store.db.execute("SELECT id, state FROM tasks WHERE owner = ? AND state IN ('claimed', 'blocked')",
                            (args.actor,)).fetchall()
    rows = store.db.execute("SELECT * FROM tasks WHERE state IN ('ready', 'rework')").fetchall()
    # Your own rejected work first, then priority, then age.
    rows.sort(key=lambda r: (not (r["state"] == "rework" and r["last_owner"] == args.actor), -r["priority"], r["seq"]))
    waiting = []
    for row in rows:
        reasons = blockers(store, row, worker)
        if not reasons:
            if args.claim:
                return claim(store, args.actor, row["id"], args.lease, args.skip_base_check)
            if args.json:
                return json.dumps(task_dict(store, row), indent=2)
            return "next: " + describe(store, row) + f"\n\nclaim it with: claim {row['id']}"
        waiting.append(f"  {row['id']}: " + "; ".join(reasons))
    msg = ["no eligible task"]
    if held:
        msg.append("you already hold: " + ", ".join(f"{r['id']} ({r['state']})" for r in held))
    if waiting:
        msg.append("waiting:\n" + "\n".join(waiting))
    proposed = store.db.execute("SELECT COUNT(*) FROM tasks WHERE state = 'proposed'").fetchone()[0]
    if proposed:
        msg.append(f"{proposed} proposed task(s) await lead approval")
    return "\n".join(msg)


def claim(store: Store, actor: str, task_id: str, lease: float, skip_base: bool) -> str:
    worker = store.worker(actor)
    row = store.task(task_id)
    if row["owner"] == actor and row["state"] == "claimed":
        # Safe to retry after an unknown outcome: the claim already landed.
        return f"{row['id']} is already yours (lease until {ts(row['lease_expires'])})"
    reasons = blockers(store, row, worker)
    if reasons:
        raise Refused(f"cannot claim {row['id']}:\n  " + "\n  ".join(reasons))
    spec = spec_of(row)
    if not skip_base:
        problem = base_check(spec, Path.cwd())
        if problem:
            raise Refused(f"cannot claim {row['id']}: {problem}")
    now = time.time()
    store.db.execute(
        "UPDATE tasks SET state = 'claimed', owner = ?, claimed_rev = rev, lease_expires = ?, "
        "attempt = attempt + 1, updated_at = ? WHERE id = ?",
        (actor, now + lease * 60, now, row["id"]),
    )
    store.event(actor, row["id"], "claim", rev=row["rev"], attempt=row["attempt"] + 1)
    row = store.task(row["id"])
    warn = ""
    changed = changed_files(spec, Path.cwd())
    if changed:
        stray = [f for f in changed if not any(path_matches(f, p) for p in spec.get("paths", []))]
        if stray:
            warn = ("\nwarning: this checkout already has changes outside the task scope; commit or set them "
                    "aside so the task's diff stays reviewable:\n  " + "\n  ".join(stray[:20]))
    return f"claimed {row['id']} (attempt {row['attempt']}, lease until {ts(row['lease_expires'])})\n" + describe(store, row) + warn


def cmd_claim(store: Store, args) -> str:
    store.reclaim_expired(args.actor or "-")
    return claim(store, args.actor, args.task, args.lease, args.skip_base_check)


def owned(store: Store, actor: str, task_id: str, states=("claimed",)) -> sqlite3.Row:
    store.worker(actor)
    row = store.task(task_id)
    if row["owner"] != actor:
        holder = row["owner"] or "nobody"
        why = " (your lease expired and it was reclaimed)" if row["last_owner"] == actor else ""
        raise Refused(f"you do not hold {row['id']}; it is {row['state']} and held by {holder}{why}. "
                      "Inspect with show before doing anything else.")
    if row["state"] not in states:
        raise Refused(f"{row['id']} is {row['state']}; this needs {' or '.join(states)}")
    return row


def stale_note(row: sqlite3.Row) -> str | None:
    if row["claimed_rev"] and row["claimed_rev"] != row["rev"]:
        return (f"{row['id']} was revised to r{row['rev']} after you claimed r{row['claimed_rev']}: "
                f"run show {row['id']}, reconcile your work, then ack {row['id']}")
    return None


def cmd_heartbeat(store: Store, args) -> str:
    store.worker(args.actor)
    rows = store.db.execute("SELECT * FROM tasks WHERE owner = ? AND state = 'claimed'", (args.actor,)).fetchall()
    if args.task:
        rows = [owned(store, args.actor, args.task)]
    if not rows:
        return "no claimed task to renew (you are registered and seen)"
    now, notes, stale = time.time(), [], []
    for row in rows:
        store.db.execute("UPDATE tasks SET lease_expires = ?, updated_at = ? WHERE id = ?",
                         (now + args.lease * 60, now, row["id"]))
        notes.append(f"{row['id']} lease until {ts(now + args.lease * 60)}")
        if stale_note(row):
            stale.append(stale_note(row))
    store.event(args.actor, None, "heartbeat", tasks=[r["id"] for r in rows])
    if stale:
        store.commit()
        raise Refused("\n".join(notes + stale), EXIT_STALE)
    return "\n".join(notes)


def cmd_ack(store: Store, args) -> str:
    row = owned(store, args.actor, args.task, ("claimed", "blocked"))
    store.db.execute("UPDATE tasks SET claimed_rev = rev, updated_at = ? WHERE id = ?", (time.time(), row["id"]))
    store.event(args.actor, row["id"], "ack", rev=row["rev"])
    return f"{row['id']}: working to r{row['rev']}"


def cmd_progress(store: Store, args) -> str:
    row = owned(store, args.actor, args.task)
    store.event(args.actor, row["id"], "progress", message=args.message)
    stale = stale_note(row)
    return f"{row['id']}: noted" + (f"\nwarning: {stale}" if stale else "")


def cmd_block(store: Store, args) -> str:
    row = owned(store, args.actor, args.task)
    store.db.execute("UPDATE tasks SET state = 'blocked', lease_expires = NULL, note = ?, updated_at = ? WHERE id = ?",
                     ("blocked: " + args.reason, time.time(), row["id"]))
    store.event(args.actor, row["id"], "block", reason=args.reason, retry_when=args.retry_when)
    return f"{row['id']} is blocked; you still hold its scope until a lead unblocks or releases it"


def cmd_unblock(store: Store, args) -> str:
    store.lead(args.actor)
    row = store.task(args.task)
    if row["state"] != "blocked":
        raise Refused(f"{row['id']} is {row['state']}, not blocked")
    now = time.time()
    store.db.execute("UPDATE tasks SET state = 'claimed', lease_expires = ?, note = ?, updated_at = ? WHERE id = ?",
                     (now + args.lease * 60, "unblocked: " + args.message, now, row["id"]))
    store.event(args.actor, row["id"], "unblock", message=args.message)
    return f"{row['id']} is back with {row['owner']}"


def parse_evidence(pairs: list[str] | None) -> dict:
    data = {}
    for pair in pairs or []:
        key, sep, value = pair.partition("=")
        if not sep or not key.strip():
            raise Refused(f"evidence must be key=value, got: {pair}")
        data.setdefault(key.strip(), []).append(value.strip())
    return {k: v[0] if len(v) == 1 else v for k, v in data.items()}


def cmd_done(store: Store, args) -> str:
    row = owned(store, args.actor, args.task)
    stale = stale_note(row)
    if stale:
        raise Refused(stale, EXIT_STALE)
    spec = spec_of(row)
    evidence = parse_evidence(args.evidence)
    if args.evidence_file:
        evidence.update(json.loads(Path(args.evidence_file).read_text(encoding="utf-8")))
    missing = [k for k in spec.get("evidence", []) if not evidence.get(k)]
    if missing:
        raise Refused(f"{row['id']} requires evidence: {', '.join(missing)} (add --evidence {missing[0]}=...)")
    changed = changed_files(spec, Path.cwd())
    warning = ""
    if changed is not None:
        evidence.setdefault("changed_files", changed)
        if spec.get("paths"):
            stray = [f for f in changed if not any(path_matches(f, p) for p in spec["paths"])]
            if stray:
                evidence["out_of_scope"] = stray
                warning = "\nwarning: changes outside the task scope were recorded for review:\n  " + "\n  ".join(stray[:20])
    if args.gap:
        evidence["known_gaps"] = args.gap
    now = time.time()
    store.db.execute("INSERT INTO evidence (task, attempt, actor, at, data) VALUES (?, ?, ?, ?, ?)",
                     (row["id"], row["attempt"], args.actor, now, json.dumps(evidence, sort_keys=True)))
    store.db.execute("UPDATE tasks SET state = 'review', lease_expires = NULL, note = '', updated_at = ? WHERE id = ?",
                     (now, row["id"]))
    store.event(args.actor, row["id"], "done", evidence=evidence)
    return f"{row['id']} is in review (the scope stays held until it is closed){warning}\nnext: run next"


def cmd_accept(store: Store, args) -> str:
    store.lead(args.actor)
    row = store.task(args.task)
    if row["state"] != "review":
        raise Refused(f"{row['id']} is {row['state']}, not in review")
    state = "closed" if args.merged else "accepted"
    store.db.execute("UPDATE tasks SET state = ?, owner = NULL, last_owner = ?, note = ?, updated_at = ? WHERE id = ?",
                     (state, row["owner"], args.message or "", time.time(), row["id"]))
    store.event(args.actor, row["id"], "accept", merged=args.merged, message=args.message)
    return f"{row['id']} is {state}" + ("" if args.merged else "; close it once merged: close " + row["id"] + " --merged")


def cmd_reject(store: Store, args) -> str:
    store.lead(args.actor)
    row = store.task(args.task)
    if row["state"] not in ("review", "accepted"):
        raise Refused(f"{row['id']} is {row['state']}; only reviewed work can be rejected")
    store.db.execute("UPDATE tasks SET state = 'rework', owner = NULL, last_owner = ?, lease_expires = NULL, "
                     "claimed_rev = NULL, note = ?, updated_at = ? WHERE id = ?",
                     (row["owner"] or row["last_owner"], "rework: " + args.reason, time.time(), row["id"]))
    store.event(args.actor, row["id"], "reject", reason=args.reason)
    return f"{row['id']} returned for rework; {row['owner'] or row['last_owner']} gets first call on it"


def cmd_release(store: Store, args) -> str:
    actor = store.worker(args.actor)
    row = store.task(args.task)
    if actor["role"] != "lead":
        row = owned(store, args.actor, args.task, ("claimed", "blocked"))
    elif row["state"] not in ("claimed", "blocked"):
        raise Refused(f"{row['id']} is {row['state']}; nothing to release")
    state = "rework" if row["note"].startswith("rework:") else "ready"
    store.db.execute("UPDATE tasks SET state = ?, owner = NULL, last_owner = ?, lease_expires = NULL, "
                     "claimed_rev = NULL, updated_at = ? WHERE id = ?", (state, row["owner"], time.time(), row["id"]))
    store.event(args.actor, row["id"], "release", reason=args.reason)
    return f"{row['id']} is {state} again"


def cmd_close(store: Store, args) -> str:
    store.lead(args.actor)
    row = store.task(args.task)
    if row["state"] == "closed":
        return f"{row['id']} is already closed"
    if not args.merged and not args.reason:
        raise Refused("say why: --merged, or --reason for work that will not land")
    store.db.execute("UPDATE tasks SET state = 'closed', owner = NULL, last_owner = COALESCE(owner, last_owner), "
                     "lease_expires = NULL, note = ?, updated_at = ? WHERE id = ?",
                     ("merged" if args.merged else "closed: " + args.reason, time.time(), row["id"]))
    store.event(args.actor, row["id"], "close", merged=args.merged, reason=args.reason)
    return f"{row['id']} is closed"


def cmd_reclaim(store: Store, args) -> str:
    store.worker(args.actor)
    ids = store.reclaim_expired(args.actor)
    return ("returned expired claims: " + ", ".join(ids)) if ids else "no expired claims"


def cmd_show(store: Store, args) -> str:
    row = store.task(args.task)
    if args.json:
        data = task_dict(store, row)
        data["evidence"] = [dict(r) | {"data": json.loads(r["data"])} for r in store.db.execute(
            "SELECT * FROM evidence WHERE task = ? ORDER BY id", (row["id"],))]
        return json.dumps(data, indent=2, default=str)
    out = [describe(store, row)]
    for ev in store.db.execute("SELECT * FROM evidence WHERE task = ? ORDER BY id", (row["id"],)):
        out.append(f"  evidence (attempt {ev['attempt']}, {ev['actor']}, {ts(ev['at'])}): {ev['data']}")
    out.append("  history:")
    for ev in store.db.execute("SELECT * FROM events WHERE task = ? ORDER BY id DESC LIMIT ?", (row["id"], args.limit)):
        out.append(f"    {ts(ev['at'])} {ev['actor']} {ev['kind']} {ev['data'] if ev['data'] != '{}' else ''}".rstrip())
    return "\n".join(out)


def cmd_status(store: Store, args) -> str:
    store.reclaim_expired("status")
    text = board(store)
    if args.write:
        Path(args.write).write_text(text, encoding="utf-8")
        return f"wrote {args.write}"
    return text


def cmd_check(store: Store, args) -> str:
    row = store.task(args.task)
    spec = spec_of(row)
    changed = changed_files(spec, Path.cwd())
    if changed is None:
        return "not a git checkout; nothing to check"
    stray = [f for f in changed if not any(path_matches(f, p) for p in spec.get("paths", []))]
    if not stray:
        return f"{row['id']}: all {len(changed)} changed file(s) are inside its scope"
    raise Refused(f"{row['id']}: {len(stray)} changed file(s) outside its scope:\n  " + "\n  ".join(stray))


def cmd_log(store: Store, args) -> str:
    query, params = "SELECT * FROM events", []
    if args.task:
        query += " WHERE task = ?"
        params.append(args.task.upper())
    rows = store.db.execute(query + " ORDER BY id DESC LIMIT ?", (*params, args.limit)).fetchall()
    return "\n".join(f"{ts(r['at'])} {r['actor']} {r['task'] or '-'} {r['kind']} {r['data'] if r['data'] != '{}' else ''}".rstrip()
                     for r in reversed(rows)) or "(no events)"


def cmd_workers(store: Store, args) -> str:
    out = []
    for w in store.db.execute("SELECT * FROM workers ORDER BY role, name"):
        held = [r["id"] for r in store.db.execute("SELECT id FROM tasks WHERE owner = ?", (w["name"],))]
        out.append(f"{w['name']} [{w['role']}{'/' + w['label'] if w['label'] else ''}] caps: "
                   f"{', '.join(json.loads(w['capabilities'])) or '-'}; seen {ts(w['last_seen'])}; holds {', '.join(held) or '-'}")
    return "\n".join(out) or "(no workers registered)"


# --------------------------------------------------------------------------- CLI


def build_parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--as", dest="actor", default=os.environ.get("AGENTKIT_AS"),
                        help="your registered name (or set AGENTKIT_AS)")
    lease = argparse.ArgumentParser(add_help=False)
    lease.add_argument("--lease", type=float, default=float(os.environ.get("AGENTKIT_LEASE_MINUTES", DEFAULT_LEASE_MINUTES)),
                       help=f"lease length in minutes (default {DEFAULT_LEASE_MINUTES})")

    parser = argparse.ArgumentParser(prog="agentkit", description=__doc__.split("\n\n")[0])
    parser.add_argument("--version", action="version", version=VERSION)
    sub = parser.add_subparsers(dest="command", required=True)

    def spec_args(p: argparse.ArgumentParser, required: bool) -> None:
        p.add_argument("--title", required=required)
        p.add_argument("--goal", required=required, help="what is true when this lands")
        p.add_argument("--source", choices=SOURCES, help="where the work came from")
        p.add_argument("--path", action="append", help="path or glob this task may change (repeat)")
        p.add_argument("--resource", action="append", help="named non-file resource it owns, e.g. db-schema (repeat)")
        p.add_argument("--after", action="append", help="task that must be accepted first (repeat)")
        p.add_argument("--need", action="append", help="capability a worker must have (repeat or comma list)")
        p.add_argument("--base", help="branch or commit the work must start from")
        p.add_argument("--deliverable", action="append")
        p.add_argument("--non-scope", dest="non_scope", action="append", help="adjacent work that is NOT this task")
        p.add_argument("--verify", action="append", help="check that proves it, e.g. a test command")
        p.add_argument("--evidence", action="append", help="evidence key required at done, e.g. tests,commit")
        p.add_argument("--danger", action="append", help="silent-failure zone to read back after writing")
        p.add_argument("--priority", type=int)

    p = sub.add_parser("register", parents=[common], help="identify yourself (also used to resume)")
    p.add_argument("name")
    p.add_argument("--role", choices=("lead", "worker"), default="worker")
    p.add_argument("--label", help="optional role label: implementer, reviewer, tester, integrator...")
    p.add_argument("--cap", action="append", help="capability you actually have (repeat or comma list)")
    p.set_defaults(func=cmd_register, mutates=True)

    p = sub.add_parser("add", parents=[common], help="create a task (workers can only propose)")
    spec_args(p, True)
    p.add_argument("--proposed", action="store_true", help="lead: record without releasing it")
    p.set_defaults(func=cmd_add, mutates=True)

    p = sub.add_parser("revise", parents=[common], help="lead: change a task spec (bumps its revision)")
    p.add_argument("task")
    spec_args(p, False)
    p.set_defaults(func=cmd_revise, mutates=True)

    for name, func, helptext in (("approve", cmd_approve, "lead: release a proposed task"),):
        p = sub.add_parser(name, parents=[common], help=helptext)
        p.add_argument("task")
        p.set_defaults(func=func, mutates=True)

    p = sub.add_parser("next", parents=[common, lease], help="show (or --claim) the next task you may take")
    p.add_argument("--claim", action="store_true")
    p.add_argument("--json", action="store_true")
    p.add_argument("--skip-base-check", action="store_true")
    p.set_defaults(func=cmd_next, mutates=True)

    p = sub.add_parser("claim", parents=[common, lease], help="claim a task atomically")
    p.add_argument("task")
    p.add_argument("--skip-base-check", action="store_true", help="for tasks whose work is not in this checkout")
    p.set_defaults(func=cmd_claim, mutates=True)

    p = sub.add_parser("heartbeat", parents=[common, lease], help="renew your leases; exits 3 if a spec went stale")
    p.add_argument("task", nargs="?")
    p.set_defaults(func=cmd_heartbeat, mutates=True)

    p = sub.add_parser("ack", parents=[common], help="confirm you are working to the current revision")
    p.add_argument("task")
    p.set_defaults(func=cmd_ack, mutates=True)

    p = sub.add_parser("progress", parents=[common], help="record a checkpoint")
    p.add_argument("task")
    p.add_argument("-m", "--message", required=True)
    p.set_defaults(func=cmd_progress, mutates=True)

    p = sub.add_parser("block", parents=[common], help="stop: you cannot continue without someone else")
    p.add_argument("task")
    p.add_argument("--reason", required=True)
    p.add_argument("--retry-when", help="what must change before anyone retries")
    p.set_defaults(func=cmd_block, mutates=True)

    p = sub.add_parser("unblock", parents=[common, lease], help="lead: hand a blocked task back to its owner")
    p.add_argument("task")
    p.add_argument("-m", "--message", required=True)
    p.set_defaults(func=cmd_unblock, mutates=True)

    p = sub.add_parser("done", parents=[common], help="submit finished work with evidence for review")
    p.add_argument("task")
    p.add_argument("--evidence", action="append", help="key=value, e.g. tests='pytest -q: exit 0' (repeat)")
    p.add_argument("--evidence-file", help="JSON object of additional evidence")
    p.add_argument("--gap", action="append", help="known remaining gap (repeat)")
    p.set_defaults(func=cmd_done, mutates=True)

    p = sub.add_parser("accept", parents=[common], help="lead: accept reviewed work")
    p.add_argument("task")
    p.add_argument("--merged", action="store_true", help="it is already merged; close it")
    p.add_argument("-m", "--message")
    p.set_defaults(func=cmd_accept, mutates=True)

    p = sub.add_parser("reject", parents=[common], help="lead: return reviewed work for rework")
    p.add_argument("task")
    p.add_argument("--reason", required=True)
    p.set_defaults(func=cmd_reject, mutates=True)

    p = sub.add_parser("release", parents=[common], help="give a task back to the queue")
    p.add_argument("task")
    p.add_argument("--reason", default="")
    p.set_defaults(func=cmd_release, mutates=True)

    p = sub.add_parser("close", parents=[common], help="lead: close a task (--merged, or --reason)")
    p.add_argument("task")
    p.add_argument("--merged", action="store_true")
    p.add_argument("--reason")
    p.set_defaults(func=cmd_close, mutates=True)

    p = sub.add_parser("reclaim", parents=[common], help="return claims whose lease expired")
    p.set_defaults(func=cmd_reclaim, mutates=True)

    p = sub.add_parser("show", help="a task's spec, state, evidence and history")
    p.add_argument("task")
    p.add_argument("--json", action="store_true")
    p.add_argument("--limit", type=int, default=20)
    p.set_defaults(func=cmd_show, mutates=False)

    p = sub.add_parser("check", help="are this checkout's changes inside a task's scope? (exit 1 if not)")
    p.add_argument("task")
    p.set_defaults(func=cmd_check, mutates=False)

    p = sub.add_parser("status", help="generated Markdown board")
    p.add_argument("--write", help="also write the board to this file")
    p.set_defaults(func=cmd_status, mutates=True)

    p = sub.add_parser("log", help="append-only event history")
    p.add_argument("task", nargs="?")
    p.add_argument("--limit", type=int, default=50)
    p.set_defaults(func=cmd_log, mutates=False)

    p = sub.add_parser("workers", help="registered workers and what they hold")
    p.set_defaults(func=cmd_workers, mutates=False)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        store = Store(database_path())
    except Refused as exc:
        print(str(exc), file=sys.stderr)
        return exc.code
    try:
        if args.mutates:
            store.begin()
        message = args.func(store, args)
        if store.db.in_transaction:
            store.commit()
        print(message)
        return 0
    except Refused as exc:
        store.rollback()
        print(str(exc), file=sys.stderr)
        return exc.code
    finally:
        store.db.close()


if __name__ == "__main__":
    raise SystemExit(main())
