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

VERSION = "1.1.1"
# Bump when the database layout changes. Every agent in a project may run its
# own installed copy; an older copy must refuse a store a newer one has changed.
SCHEMA_VERSION = 2
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
    updated_at REAL NOT NULL,
    claim_head TEXT,
    reviewer TEXT
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
CREATE TABLE IF NOT EXISTS holds (
    resource TEXT PRIMARY KEY,
    holder TEXT NOT NULL,
    until REAL NOT NULL,
    reason TEXT NOT NULL
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


def segments_disjoint(a: str, b: str) -> bool:
    """True only when no name can match both one-segment patterns: their literal
    starts or literal ends disagree. Anything undecidable counts as overlapping."""
    a, b = a.casefold(), b.casefold()
    if "[" in a or "[" in b:
        return False
    if not has_magic(a) and not has_magic(b):
        return a != b
    start_a, start_b = re.split(r"[*?]", a)[0], re.split(r"[*?]", b)[0]
    end_a, end_b = re.split(r"[*?]", a)[-1], re.split(r"[*?]", b)[-1]
    return (not (start_a.startswith(start_b) or start_b.startswith(start_a))
            or not (end_a.endswith(end_b) or end_b.endswith(end_a)))


def globs_overlap(a: str, b: str) -> bool:
    """Conservative: may report an overlap that no real file exhibits, never the
    reverse. Over-reporting costs a queue wait; under-reporting costs a collision.

    Segments are compared pairwise up to the shorter pattern (a pattern also
    covers everything below what it matches) or up to the first `**`, after
    which anything may follow."""
    if not has_magic(a):
        return path_matches(a, b) or path_matches(b, a) if not has_magic(b) else path_matches(a, b)
    if not has_magic(b):
        return path_matches(b, a)
    for seg_a, seg_b in zip(norm(a).split("/"), norm(b).split("/")):
        if "**" in seg_a or "**" in seg_b:
            return True
        if segments_disjoint(seg_a, seg_b):
            return False
    return True


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
        if stored < SCHEMA_VERSION:
            self.migrate()

    def migrate(self) -> None:
        """Bring an older store forward in place. Columns are only ever added,
        so every existing task, claim and event keeps its meaning."""
        self.begin()
        try:
            columns = {row[1] for row in self.db.execute("PRAGMA table_info(tasks)")}
            for column in ("claim_head", "reviewer"):
                if column not in columns:
                    self.db.execute(f"ALTER TABLE tasks ADD COLUMN {column} TEXT")
            self.db.execute("UPDATE meta SET value = ? WHERE key = 'schema'", (str(SCHEMA_VERSION),))
            self.event("agentkit", None, "migrate", to_schema=SCHEMA_VERSION, runtime=VERSION)
            self.commit()
        except BaseException:
            self.rollback()
            raise

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
    for resource in spec.get("resources", []):
        hold = active_hold(store, resource)
        if hold and hold["holder"] != worker["name"]:
            reasons.append(f"resource {resource} is held by {hold['holder']} until {ts(hold['until'])} ({hold['reason']})")
    return reasons


def active_hold(store: Store, resource: str) -> sqlite3.Row | None:
    return store.db.execute("SELECT * FROM holds WHERE resource = ? AND until > ?",
                            (resource.casefold(), time.time())).fetchone()


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


def working_tree_files(cwd: Path) -> list[str] | None:
    """Uncommitted changes in this checkout, whoever made them; None outside git."""
    if git(["rev-parse", "--git-dir"], cwd) is None:
        return None
    files = set()
    status = git(["status", "--porcelain", "--untracked-files=all"], cwd) or ""
    for line in status.splitlines():
        name = line[3:]
        if " -> " in name:
            name = name.split(" -> ", 1)[1]
        files.add(norm(name.strip('"')))
    return sorted(f for f in files if f and not f.startswith(".agent-kit/state/"))


def task_commits(store: "Store", row: sqlite3.Row, named: list[str], cwd: Path) -> list[str]:
    """The task's own commits: those named as evidence, plus every commit since
    the claim whose message mentions the task ID. A shared checkout interleaves
    several agents' commits, so position alone cannot attribute them."""
    commits = []
    for ref in named:
        sha = git(["rev-parse", "--verify", "--quiet", ref + "^{commit}"], cwd)
        if sha:
            commits.append(sha)
    # The subject line names the task a commit does; a body that merely
    # mentions a task (a report about it, a reference) does not make it the
    # task's work.
    subject = re.compile(f"(^|[^A-Za-z0-9]){re.escape(row['id'])}([^A-Za-z0-9]|$)", re.IGNORECASE)
    search = ["log", "--format=%H%x1f%s"]
    start = row["claim_head"]
    if start and git(["rev-parse", "--verify", "--quiet", start + "^{commit}"], cwd):
        found = git([*search, f"{start}..HEAD"], cwd)
    else:
        # Claimed before claims recorded their commit (or in another clone):
        # fall back to commits made since the first claim.
        claimed = store.db.execute("SELECT MIN(at) FROM events WHERE task = ? AND kind = 'claim'",
                                   (row["id"],)).fetchone()[0]
        found = git([*search, f"--since=@{int(claimed)}", "HEAD"], cwd) if claimed else None
    for line in (found or "").splitlines():
        sha, _, title = line.partition("\x1f")
        if subject.search(title):
            commits.append(sha)
    return list(dict.fromkeys(commits))


def commit_files(commits: list[str], cwd: Path) -> list[str]:
    files = set()
    for sha in commits:
        listed = git(["diff-tree", "--no-commit-id", "--name-only", "-r", "--root", sha], cwd) or ""
        files.update(norm(f) for f in listed.splitlines() if f)
    return sorted(files)


def evidence_commits(evidence: dict) -> list[str]:
    value = evidence.get("commit") or evidence.get("commits") or []
    values = value if isinstance(value, list) else [value]
    return [ref for item in values for ref in re.split(r"[\s,]+", str(item)) if ref]


def audit(store: Store, row: sqlite3.Row, cwd: Path, named: list[str] | None = None) -> dict | None:
    """What this checkout shows about a task's changes.

    - `changed_files`: files in the task's own commits, plus uncommitted files in
      its scope.
    - `out_of_scope`: files the task's own commits changed outside its scope.
    - `other_tasks`: uncommitted files inside another open task's scope. In a
      shared checkout that is the other agent's work, not a finding.
    - `unclaimed`: uncommitted files inside no open task's scope. Nobody claimed
      them, so somebody edited without a claim.
    """
    tree = working_tree_files(cwd)
    if tree is None:
        return None
    spec = spec_of(row)
    paths = spec.get("paths", [])
    mine = lambda f: any(path_matches(f, p) for p in paths)  # noqa: E731
    commits = task_commits(store, row, named or [], cwd)
    committed = commit_files(commits, cwd)
    others = [r for r in store.db.execute(
        "SELECT * FROM tasks WHERE id != ? AND state IN (%s)" % ",".join("?" * len(HOLDING)), (row["id"], *HOLDING))]
    other_tasks, unclaimed = {}, []
    for f in tree:
        if mine(f):
            continue
        holder = next((r for r in others if any(path_matches(f, p) for p in spec_of(r).get("paths", []))), None)
        if holder is not None:
            other_tasks[f] = f"{holder['id']} ({holder['owner'] or holder['last_owner'] or '-'})"
        else:
            unclaimed.append(f)
    return {
        "commits": commits,
        "changed_files": sorted(set(committed) | {f for f in tree if mine(f)}),
        "out_of_scope": [f for f in committed if not mine(f)],
        "other_tasks": other_tasks,
        "unclaimed": unclaimed,
    }


def audit_report(result: dict) -> list[str]:
    lines = []
    if result["out_of_scope"]:
        lines.append("this task's commits changed files outside its scope:\n  " + "\n  ".join(result["out_of_scope"][:20]))
    if result["unclaimed"]:
        lines.append("uncommitted changes no open task claims (someone edited without a claim):\n  "
                     + "\n  ".join(result["unclaimed"][:20]))
    if result["other_tasks"]:
        lines.append("uncommitted changes belonging to other open tasks (not yours; left alone):\n  "
                     + "\n  ".join(f"{f}  <- {t}" for f, t in list(result["other_tasks"].items())[:20]))
    return lines


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
    if row["reviewer"]:
        lines.append(f"  reviewer: {row['reviewer']}")
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
        if state in CLAIMABLE or state == "proposed":
            group.sort(key=lambda r: (-r["priority"], r["seq"]))  # the order next offers them
        out += [f"## {state} ({len(group)})", "", "| Task | P | Title | Owner | Scope | After |", "|---|---|---|---|---|---|"]
        for r in group:
            spec = spec_of(r)
            scope = ", ".join(spec.get("paths", []) + [f"@{x}" for x in spec.get("resources", [])]) or "-"
            owner = r["owner"] or (f"({r['last_owner']})" if r["last_owner"] else "-")
            out.append(f"| {r['id']} r{r['rev']} | {r['priority']} | {spec['title']} | {owner} | {scope} | {', '.join(store.deps(r['id'])) or '-'} |")
        out.append("")
    closed = sum(1 for r in rows if r["state"] == "closed")
    out += [f"Closed: {closed}", ""]
    holds = store.db.execute("SELECT * FROM holds WHERE until > ? ORDER BY resource", (now,)).fetchall()
    if holds:
        out += ["## Short holds", "", "| Resource | Holder | Until | Reason |", "|---|---|---|---|"]
        out += [f"| {h['resource']} | {h['holder']} | {ts(h['until'])} | {h['reason']} |" for h in holds]
        out.append("")
    out += [ "## Workers", "", "| Name | Role | Capabilities | Last seen |", "|---|---|---|---|"]
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
    reviewer = set_reviewer(store, task_id, args.reviewer) if args.reviewer else None
    store.event(args.actor, task_id, "add", state=state, spec=spec, after=deps, reviewer=reviewer)
    return f"{task_id} added as {state}" + ("" if state == "ready" else " (a lead must approve it)")


def set_reviewer(store: Store, task_id: str, name: str) -> str | None:
    """Name who must review the task; `none` clears it. The reviewer is an
    assignment, not part of the spec, so changing it never makes work stale."""
    reviewer = None if name.casefold() == "none" else store.worker(name)["name"]
    store.db.execute("UPDATE tasks SET reviewer = ? WHERE id = ?", (reviewer, task_id))
    return reviewer


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
    if args.reviewer is not None:
        set_reviewer(store, row["id"], args.reviewer)
    store.event(args.actor, row["id"], "revise", rev=rev, spec=spec, priority=priority, after=args.after,
                reviewer=args.reviewer)
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
    # Where this attempt starts: its commits are the ones after this point that
    # name the task, however other agents' commits interleave with them.
    head = git(["rev-parse", "HEAD"], Path.cwd())
    store.db.execute(
        "UPDATE tasks SET state = 'claimed', owner = ?, claimed_rev = rev, lease_expires = ?, "
        "attempt = attempt + 1, claim_head = ?, updated_at = ? WHERE id = ?",
        (actor, now + lease * 60, head, now, row["id"]),
    )
    store.event(actor, row["id"], "claim", rev=row["rev"], attempt=row["attempt"] + 1, head=head)
    row = store.task(row["id"])
    warn = ""
    result = audit(store, row, Path.cwd())
    if result and result["unclaimed"]:
        warn = ("\nwarning: this checkout has uncommitted changes no open task claims; find their owner "
                "before they end up in this task's commits:\n  " + "\n  ".join(result["unclaimed"][:20]))
    return (f"claimed {row['id']} (attempt {row['attempt']}, lease until {ts(row['lease_expires'])})\n"
            + describe(store, row) + f"\nname {row['id']} in each commit message so its commits can be attributed" + warn)


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
    result = audit(store, row, Path.cwd(), evidence_commits(evidence))
    warning = ""
    if result is not None:
        evidence.setdefault("changed_files", result["changed_files"])
        evidence["attributed_commits"] = result["commits"]
        for key in ("out_of_scope", "unclaimed"):
            if result[key]:
                evidence[key] = result[key]
        lines = [line for line in audit_report(result) if not line.startswith("uncommitted changes belonging")]
        if result["other_tasks"]:
            # A test run in this checkout measured their work too; say so beside
            # the evidence rather than let it describe a state no commit holds.
            evidence["uncommitted_other_tasks"] = result["other_tasks"]
            lines.append("other tasks' uncommitted files were present, so evidence gathered in this checkout "
                         "may include their work; rerun it on a clean worktree at your commit "
                         "(git worktree add --detach <dir> <sha>) and resubmit if it matters:\n  "
                         + "\n  ".join(f"{f}  <- {t}" for f, t in list(result["other_tasks"].items())[:20]))
        if not result["changed_files"]:
            lines.append(f"no change is attributed to {row['id']}: name it in its commit messages or pass "
                         "--evidence commit=<sha>, so review has a file list")
        if lines:
            warning = "\nwarning: " + "\nwarning: ".join(lines)
    if args.gap:
        evidence["known_gaps"] = args.gap
    now = time.time()
    store.db.execute("INSERT INTO evidence (task, attempt, actor, at, data) VALUES (?, ?, ?, ?, ?)",
                     (row["id"], row["attempt"], args.actor, now, json.dumps(evidence, sort_keys=True)))
    store.db.execute("UPDATE tasks SET state = 'review', lease_expires = NULL, note = '', updated_at = ? WHERE id = ?",
                     (now, row["id"]))
    store.event(args.actor, row["id"], "done", evidence=evidence)
    return f"{row['id']} is in review (the scope stays held until it is closed){warning}\nnext: run next"


def latest_verdict(store: Store, row: sqlite3.Row) -> sqlite3.Row | None:
    for event in store.db.execute("SELECT * FROM events WHERE task = ? AND kind = 'review' ORDER BY id DESC", (row["id"],)):
        if json.loads(event["data"]).get("attempt") == row["attempt"]:
            return event
    return None


def cmd_accept(store: Store, args) -> str:
    store.lead(args.actor)
    row = store.task(args.task)
    if row["state"] != "review":
        raise Refused(f"{row['id']} is {row['state']}, not in review")
    if args.actor == row["owner"]:
        raise Refused(f"{args.actor} did {row['id']} and cannot also accept it")
    if row["reviewer"] and not args.override_review:
        verdict = latest_verdict(store, row)
        if verdict is None or verdict["actor"] != row["reviewer"]:
            raise Refused(f"{row['id']} awaits review by {row['reviewer']}; accept after their verdict, "
                          "or record why not with --override-review")
        if json.loads(verdict["data"])["verdict"] != "accept":
            raise Refused(f"{row['reviewer']} rejected {row['id']}: {json.loads(verdict['data']).get('message', '')}; "
                          "reject it for rework, or record why you accept anyway with --override-review")
    state = "closed" if args.merged else "accepted"
    store.db.execute("UPDATE tasks SET state = ?, owner = NULL, last_owner = ?, note = ?, updated_at = ? WHERE id = ?",
                     (state, row["owner"], args.message or "", time.time(), row["id"]))
    store.event(args.actor, row["id"], "accept", merged=args.merged, message=args.message,
                override_review=args.override_review)
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
    """Exit 1 when the task's own commits leave its scope or when changes exist
    that no open task claims; other tasks' uncommitted work is listed, not failed."""
    row = store.task(args.task)
    result = audit(store, row, Path.cwd())
    if result is None:
        return "not a git checkout; nothing to check"
    lines = audit_report(result)
    summary = (f"{row['id']}: {len(result['changed_files'])} file(s) attributed to it "
               f"({len(result['commits'])} commit(s) naming it, plus uncommitted files in its scope)")
    if result["out_of_scope"] or result["unclaimed"]:
        raise Refused("\n".join([summary, *lines]))
    return "\n".join([summary + "; all inside its scope", *lines])


def cmd_note(store: Store, args) -> str:
    store.worker(args.actor)
    row = store.task(args.task)
    if row["state"] == "closed":
        raise Refused(f"{row['id']} is closed")
    store.event(args.actor, row["id"], "note", message=args.message)
    return f"{row['id']}: note recorded"


def cmd_review(store: Store, args) -> str:
    store.worker(args.actor)
    row = store.task(args.task)
    if row["state"] != "review":
        raise Refused(f"{row['id']} is {row['state']}, not in review")
    if args.actor in (row["owner"], row["last_owner"]):
        raise Refused(f"{args.actor} did {row['id']} and cannot review it")
    if row["reviewer"] and args.actor != row["reviewer"]:
        raise Refused(f"{row['id']}'s reviewer is {row['reviewer']}; add your view with note instead")
    store.event(args.actor, row["id"], "review", verdict=args.verdict, message=args.message, attempt=row["attempt"])
    return f"{row['id']}: review recorded ({args.verdict}); the lead decides with accept or reject"


def cmd_hold(store: Store, args) -> str:
    store.worker(args.actor)
    key, now = args.resource.casefold(), time.time()
    current = active_hold(store, key)
    if current and current["holder"] != args.actor:
        raise Refused(f"{args.resource} is held by {current['holder']} until {ts(current['until'])} ({current['reason']})")
    for task in store.db.execute("SELECT * FROM tasks WHERE state IN (%s)" % ",".join("?" * len(HOLDING)), HOLDING):
        holder = task["owner"] or task["last_owner"]
        if holder != args.actor and key in {r.casefold() for r in spec_of(task).get("resources", [])}:
            raise Refused(f"{args.resource} is in the scope of {task['id']} ({task['state']}, {holder or '-'})")
    until = now + args.minutes * 60
    store.db.execute("INSERT INTO holds VALUES (?, ?, ?, ?) ON CONFLICT(resource) DO UPDATE SET "
                     "holder = excluded.holder, until = excluded.until, reason = excluded.reason",
                     (key, args.actor, until, args.reason))
    store.event(args.actor, None, "hold", resource=key, until=until, reason=args.reason)
    return f"holding {args.resource} until {ts(until)}; release it with unhold as soon as you are done"


def cmd_unhold(store: Store, args) -> str:
    actor = store.worker(args.actor)
    key = args.resource.casefold()
    current = active_hold(store, key)
    if current is None:
        return f"{args.resource} is not held"
    if current["holder"] != args.actor and actor["role"] != "lead":
        raise Refused(f"{args.resource} is held by {current['holder']}; only they or a lead may release it")
    store.db.execute("DELETE FROM holds WHERE resource = ?", (key,))
    store.event(args.actor, None, "unhold", resource=key, holder=current["holder"])
    return f"released {args.resource}"


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
        p.add_argument("--priority", type=int, help="higher runs first (default 0)")
        p.add_argument("--reviewer", help="registered agent who must review it before a lead accepts (none clears)")

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

    p = sub.add_parser("note", parents=[common], help="attach a note to any open task (anyone registered)")
    p.add_argument("task")
    p.add_argument("-m", "--message", required=True)
    p.set_defaults(func=cmd_note, mutates=True)

    p = sub.add_parser("review", parents=[common], help="record a review verdict on work in review")
    p.add_argument("task")
    p.add_argument("--verdict", choices=("accept", "reject"), required=True)
    p.add_argument("-m", "--message", required=True, help="what you checked and found")
    p.set_defaults(func=cmd_review, mutates=True)

    p = sub.add_parser("hold", parents=[common], help="hold a shared resource briefly (an editor, a build)")
    p.add_argument("resource")
    p.add_argument("--for", dest="minutes", type=float, default=15, help="minutes (default 15)")
    p.add_argument("--reason", required=True)
    p.set_defaults(func=cmd_hold, mutates=True)

    p = sub.add_parser("unhold", parents=[common], help="release a short hold")
    p.add_argument("resource")
    p.set_defaults(func=cmd_unhold, mutates=True)

    p = sub.add_parser("accept", parents=[common], help="lead: accept reviewed work")
    p.add_argument("task")
    p.add_argument("--override-review", help="accept without the named reviewer's approval, and say why")
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

    p = sub.add_parser("show", parents=[common], help="a task's spec, state, evidence and history")
    p.add_argument("task")
    p.add_argument("--json", action="store_true")
    p.add_argument("--limit", type=int, default=20)
    p.set_defaults(func=cmd_show, mutates=False)

    p = sub.add_parser("check", parents=[common], help="are this checkout's changes inside a task's scope? (exit 1 if not)")
    p.add_argument("task")
    p.set_defaults(func=cmd_check, mutates=False)

    p = sub.add_parser("status", parents=[common], help="generated Markdown board")
    p.add_argument("--write", help="also write the board to this file")
    p.set_defaults(func=cmd_status, mutates=True)

    p = sub.add_parser("log", parents=[common], help="append-only event history")
    p.add_argument("task", nargs="?")
    p.add_argument("--limit", type=int, default=50)
    p.set_defaults(func=cmd_log, mutates=False)

    p = sub.add_parser("workers", parents=[common], help="registered workers and what they hold")
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
