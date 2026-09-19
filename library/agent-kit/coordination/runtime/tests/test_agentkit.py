"""Protocol tests for the agent-kit runtime, one per coordination failure it exists to stop."""

import contextlib
import io
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

RUNTIME = Path(__file__).resolve().parents[1] / "agentkit.py"
sys.path.insert(0, str(RUNTIME.parent))
import agentkit  # noqa: E402


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.db = self.dir / "state.db"
        self.env = {k: os.environ.get(k) for k in ("AGENTKIT_DB", "AGENTKIT_AS")}
        os.environ["AGENTKIT_DB"] = str(self.db)
        os.environ.pop("AGENTKIT_AS", None)
        self.cwd = os.getcwd()
        os.chdir(self.dir)
        self.ok("register", "lead", "--role", "lead")
        self.ok("register", "ann", "--cap", "code_edit,tests,git")
        self.ok("register", "bob", "--cap", "code_edit,tests,git")

    def tearDown(self):
        os.chdir(self.cwd)
        for key, value in self.env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        self.tmp.cleanup()

    def run_cli(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = agentkit.main(list(argv))
        return code, out.getvalue() + err.getvalue()

    def ok(self, *argv):
        code, text = self.run_cli(*argv)
        self.assertEqual(code, 0, text)
        return text

    def refused(self, *argv, code=1):
        got, text = self.run_cli(*argv)
        self.assertEqual(got, code, text)
        return text

    def add(self, *extra, actor="lead"):
        text = self.ok("add", "--as", actor, "--title", "t", "--goal", "g", *extra)
        return text.split()[0]

    def state(self, task):
        return json.loads(self.ok("show", task, "--json"))

    def expire(self, task):
        with contextlib.closing(sqlite3.connect(self.db)) as db, db:
            db.execute("UPDATE tasks SET lease_expires = ? WHERE id = ?", (time.time() - 1, task))


class ProtocolTests(Base):
    def test_two_workers_race_for_one_task_and_exactly_one_wins(self):
        task = self.add("--path", "src/a.py")
        env = dict(os.environ)
        procs = [subprocess.Popen([sys.executable, str(RUNTIME), "claim", task, "--as", name],
                                  cwd=self.dir, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                 for name in ("ann", "bob") * 3]
        codes = [p.wait(timeout=60) for p in procs]
        winner = self.state(task)["owner"]
        self.assertIn(winner, ("ann", "bob"))
        # The winner's retries are idempotent successes; every loser is refused.
        expected = [0 if name == winner else 1 for name in ("ann", "bob") * 3]
        self.assertEqual(codes, expected)
        self.assertEqual(self.state(task)["attempt"], 1)

    def test_overlapping_scope_cannot_be_claimed_until_the_holder_closes(self):
        first = self.add("--path", "src/render/**")
        second = self.add("--path", "src/render/mesh.cpp")
        third = self.add("--path", "src/audio/**", "--resource", "db-schema")
        fourth = self.add("--resource", "DB-Schema")
        self.ok("claim", first, "--as", "ann")
        self.assertIn(f"collides with {first}", self.refused("claim", second, "--as", "bob"))
        self.ok("claim", third, "--as", "bob")
        self.assertIn("resource db-schema", self.refused("claim", fourth, "--as", "bob"))
        self.ok("done", first, "--as", "ann")
        self.refused("claim", second, "--as", "bob")  # review still holds the files
        self.ok("accept", first, "--as", "lead", "--merged")
        self.ok("claim", second, "--as", "bob")

    def test_dependency_must_be_accepted_first(self):
        first = self.add()
        second = self.add("--after", first)
        self.assertIn(f"depends on {first}", self.refused("claim", second, "--as", "bob"))
        self.ok("claim", first, "--as", "ann")
        self.ok("done", first, "--as", "ann")
        self.refused("claim", second, "--as", "bob")
        self.ok("accept", first, "--as", "lead")
        self.ok("claim", second, "--as", "bob")

    def test_dependency_cycles_are_rejected(self):
        first = self.add()
        second = self.add("--after", first)
        self.assertIn("cycle", self.refused("revise", first, "--as", "lead", "--after", second))

    def test_worker_without_the_capability_is_not_offered_the_task(self):
        self.ok("register", "chat", "--cap", "research,review")
        task = self.add("--need", "code_edit")
        self.assertIn("needs capabilities code_edit", self.refused("claim", task, "--as", "chat"))
        self.assertIn("no eligible task", self.ok("next", "--as", "chat"))
        self.assertIn(task, self.ok("next", "--as", "ann"))

    def test_worker_discovery_is_only_a_proposal(self):
        task = self.add("--path", "src/x.py", actor="bob")
        self.assertEqual(self.state(task)["state"], "proposed")
        self.assertEqual(self.state(task)["spec"]["source"], "worker_discovery")
        self.refused("claim", task, "--as", "bob")
        self.refused("approve", task, "--as", "bob")
        self.ok("approve", task, "--as", "lead")
        self.ok("claim", task, "--as", "bob")

    def test_stale_revision_blocks_completion_until_acknowledged(self):
        task = self.add("--path", "src/a.py")
        self.ok("claim", task, "--as", "ann")
        self.assertIn("r2", self.ok("revise", task, "--as", "lead", "--goal", "a different goal"))
        self.assertIn("revised to r2", self.refused("heartbeat", "--as", "ann", code=3))
        self.refused("done", task, "--as", "ann", code=3)
        self.ok("ack", task, "--as", "ann")
        self.ok("done", task, "--as", "ann")
        # Priority alone is not a material change.
        other = self.add()
        self.assertIn("r1", self.ok("revise", other, "--as", "lead", "--priority", "5"))

    def test_dead_worker_lease_expires_and_task_returns(self):
        task = self.add()
        self.ok("claim", task, "--as", "ann")
        self.expire(task)
        self.ok("claim", task, "--as", "bob")
        text = self.refused("done", task, "--as", "ann")
        self.assertIn("reclaimed", text)
        self.assertEqual(self.state(task)["attempt"], 2)

    def test_reconnect_resumes_a_live_claim(self):
        task = self.add()
        self.ok("claim", task, "--as", "ann")
        self.assertIn(f"you hold {task}", self.ok("register", "ann", "--cap", "code_edit,tests,git"))
        self.assertIn("already yours", self.ok("claim", task, "--as", "ann"))
        self.ok("heartbeat", "--as", "ann")
        self.ok("progress", task, "--as", "ann", "-m", "halfway")

    def test_required_evidence_is_enforced(self):
        task = self.add("--evidence", "tests,commit")
        self.ok("claim", task, "--as", "ann")
        self.assertIn("tests, commit", self.refused("done", task, "--as", "ann"))
        self.ok("done", task, "--as", "ann", "--evidence", "tests=pytest: exit 0", "--evidence", "commit=abc123")
        evidence = self.state(task)
        self.assertEqual(evidence["state"], "review")

    def test_rejected_work_goes_back_to_its_owner_first(self):
        early = self.add()
        task = self.add()
        self.ok("claim", task, "--as", "ann")
        self.ok("done", task, "--as", "ann")
        self.ok("reject", task, "--as", "lead", "--reason", "no test for the edge case")
        self.assertEqual(self.state(task)["state"], "rework")
        self.assertIn(f"next: {task}", self.ok("next", "--as", "ann"))
        self.assertIn(f"next: {early}", self.ok("next", "--as", "bob"))
        self.ok("next", "--as", "ann", "--claim")
        self.assertEqual(self.state(task)["attempt"], 2)

    def test_blocked_task_keeps_its_scope(self):
        task = self.add("--path", "lib/**")
        other = self.add("--path", "lib/util.c")
        self.ok("claim", task, "--as", "ann")
        self.ok("block", task, "--as", "ann", "--reason", "needs an API key", "--retry-when", "key issued")
        self.refused("claim", other, "--as", "bob")
        self.ok("unblock", task, "--as", "lead", "-m", "key issued")
        self.assertEqual(self.state(task)["state"], "claimed")

    def test_finished_worker_asks_for_the_next_task(self):
        first, second = self.add(), self.add()
        self.ok("next", "--as", "ann", "--claim")
        self.ok("done", first, "--as", "ann")
        self.assertIn(f"claimed {second}", self.ok("next", "--as", "ann", "--claim"))
        self.assertIn("no eligible task", self.ok("next", "--as", "bob"))

    def test_only_a_lead_directs_work(self):
        task = self.add()
        self.ok("claim", task, "--as", "ann")
        self.ok("done", task, "--as", "ann")
        self.refused("accept", task, "--as", "ann")
        self.refused("close", task, "--as", "lead")  # a close needs --merged or --reason
        self.refused("claim", task, "--as", "nobody")
        self.refused("claim", task)

    def test_older_runtime_refuses_a_newer_store(self):
        with contextlib.closing(sqlite3.connect(self.db)) as db, db:
            db.execute("UPDATE meta SET value = '99' WHERE key = 'schema'")
        self.assertIn("update this agent's installed skill", self.refused("workers"))

    def test_every_command_accepts_as(self):
        task = self.add()
        for argv in (("show", task), ("status",), ("log",), ("workers",), ("check", task)):
            self.ok(*argv, "--as", "ann")

    def test_named_reviewer_gates_acceptance(self):
        task = self.add("--reviewer", "bob")
        self.ok("claim", task, "--as", "ann")
        self.ok("done", task, "--as", "ann")
        self.assertIn("awaits review by bob", self.refused("accept", task, "--as", "lead"))
        self.assertIn("cannot review", self.refused("review", task, "--as", "ann", "--verdict", "accept", "-m", "mine"))
        self.ok("register", "cat", "--cap", "code_edit")
        self.assertIn("reviewer is bob", self.refused("review", task, "--as", "cat", "--verdict", "accept", "-m", "x"))
        self.ok("review", task, "--as", "bob", "--verdict", "reject", "-m", "edge case untested")
        self.assertIn("bob rejected", self.refused("accept", task, "--as", "lead"))
        self.ok("reject", task, "--as", "lead", "--reason", "per bob")
        self.ok("claim", task, "--as", "ann")
        self.ok("done", task, "--as", "ann")
        self.refused("accept", task, "--as", "lead")  # the old verdict belongs to attempt 1
        self.ok("review", task, "--as", "bob", "--verdict", "accept", "-m", "edge case covered")
        self.ok("accept", task, "--as", "lead")
        other = self.add("--reviewer", "bob")
        self.ok("claim", other, "--as", "ann")
        self.ok("done", other, "--as", "ann")
        self.ok("accept", other, "--as", "lead", "--override-review", "bob unavailable; user approved")

    def test_a_lead_that_did_the_work_cannot_accept_it(self):
        self.ok("register", "boss", "--role", "lead", "--cap", "code_edit")
        task = self.add()
        self.ok("claim", task, "--as", "boss")
        self.ok("done", task, "--as", "boss")
        self.assertIn("cannot also accept", self.refused("accept", task, "--as", "boss"))
        self.ok("accept", task, "--as", "lead")

    def test_anyone_can_note_any_open_task(self):
        task = self.add()
        self.ok("note", task, "--as", "bob", "-m", "found while reading")
        self.ok("claim", task, "--as", "ann")
        self.ok("done", task, "--as", "ann")
        self.ok("note", task, "--as", "ann", "-m", "review requested from bob")
        self.assertIn("review requested", self.ok("show", task))

    def test_short_holds_on_shared_resources(self):
        build = self.add("--resource", "ue-build")
        self.ok("hold", "UE-Editor", "--as", "ann", "--for", "10", "--reason", "restarting for a build")
        self.assertIn("held by ann", self.refused("hold", "ue-editor", "--as", "bob", "--reason", "verify"))
        self.assertIn("ue-editor", self.ok("status"))
        self.refused("unhold", "ue-editor", "--as", "bob")
        self.ok("unhold", "ue-editor", "--as", "ann")
        self.ok("hold", "ue-editor", "--as", "bob", "--reason", "verify")
        self.ok("hold", "ue-build", "--as", "bob", "--reason", "compile")
        self.assertIn("held by bob", self.refused("claim", build, "--as", "ann"))
        with contextlib.closing(sqlite3.connect(self.db)) as db, db:
            db.execute("UPDATE holds SET until = ?", (time.time() - 1,))
        self.ok("claim", build, "--as", "ann")
        self.assertIn(f"scope of {build}", self.refused("hold", "ue-build", "--as", "bob", "--reason", "again"))

    def test_version_one_store_is_migrated_in_place(self):
        os.environ["AGENTKIT_DB"] = str(self.dir / "old.db")
        old_schema = (agentkit.SCHEMA.replace(",\n    claim_head TEXT,\n    reviewer TEXT\n", "\n")
                      .split("CREATE TABLE IF NOT EXISTS holds")[0])
        with contextlib.closing(sqlite3.connect(self.dir / "old.db")) as db, db:
            db.executescript(old_schema)
            db.execute("INSERT INTO meta VALUES ('schema', '1')")
            db.execute("INSERT INTO workers VALUES ('ann', 'worker', '', '[]', 0, 0)")
            db.execute("INSERT INTO tasks (id, seq, state, spec, created_by, created_at, updated_at) VALUES "
                       "('T001', 1, 'ready', '{\"title\": \"t\", \"goal\": \"g\", \"source\": \"user_directive\"}', 'lead', 0, 0)")
        self.ok("claim", "T001", "--as", "ann")
        with contextlib.closing(sqlite3.connect(self.dir / "old.db")) as db:
            self.assertEqual(db.execute("SELECT value FROM meta WHERE key = 'schema'").fetchone()[0], "2")
        self.assertIn("migrate", self.ok("log"))

    def test_status_board_is_generated_from_state(self):
        task = self.add("--path", "src/**")
        self.ok("claim", task, "--as", "ann")
        board = self.ok("status")
        self.assertIn("## claimed (1)", board)
        self.assertIn("| ann |", board)
        self.assertIn("Do not edit", board)


class GlobTests(unittest.TestCase):
    def test_overlap(self):
        o = agentkit.globs_overlap
        self.assertTrue(o("src/**", "src/a/b.py"))
        self.assertTrue(o("src/a", "src/a/b.py"))
        self.assertTrue(o("src/*.py", "src/a.py"))
        self.assertTrue(o("src/**/*.py", "src/x/*.h"))  # conservative
        self.assertTrue(o("**", "anything"))
        self.assertFalse(o("src/a/**", "src/b/**"))
        self.assertFalse(o("src/*.py", "src/a.h"))
        self.assertFalse(o("src/a.py", "src/ab.py"))
        self.assertFalse(o("a/authoring*.py", "a/basic*.py"))
        self.assertFalse(o("Tests/test_authoring*.py", "Tests/test_inspection*.py"))
        self.assertFalse(o("a/*.py", "a/*.h"))
        self.assertTrue(o("a/x*.py", "a/*.py"))
        self.assertTrue(o("a/x*", "a/xy*"))
        self.assertTrue(o("a/*/c.py", "a/b*/c.py"))
        self.assertFalse(o("a/*/c.py", "a/*/d.py"))
        self.assertTrue(o("a/x*", "a/xy/b.c"))  # a pattern covers what lies below it
        self.assertTrue(o("a/[ab]*.py", "a/c*.py"))  # undecidable counts as overlapping


def git(cwd, *args):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


class GitTests(Base):
    def setUp(self):
        super().setUp()
        git(self.dir, "init", "-q", "-b", "main")
        git(self.dir, "config", "user.email", "t@example.com")
        git(self.dir, "config", "user.name", "t")
        (self.dir / "src").mkdir()
        (self.dir / "src" / "a.py").write_text("a\n")
        (self.dir / "state.db").touch()
        (self.dir / ".gitignore").write_text("state.db*\n")
        git(self.dir, "add", ".")
        git(self.dir, "commit", "-q", "-m", "base")

    def test_wrong_base_refuses_the_claim(self):
        git(self.dir, "checkout", "-q", "-b", "feature")
        (self.dir / "src" / "b.py").write_text("b\n")
        git(self.dir, "add", ".")
        git(self.dir, "commit", "-q", "-m", "feature work")
        task = self.add("--base", "feature")
        git(self.dir, "checkout", "-q", "main")
        self.assertIn("does not contain base feature", self.refused("claim", task, "--as", "ann"))
        self.assertIn("does not exist", self.refused("claim", self.add("--base", "nope"), "--as", "ann"))
        git(self.dir, "checkout", "-q", "feature")
        self.ok("claim", task, "--as", "ann")

    def commit(self, message, **files):
        for name, text in files.items():
            # src__a_py -> src/a.py
            path = self.dir / ".".join(name.replace("__", "/").rsplit("_", 1))
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
        git(self.dir, "add", ".")
        git(self.dir, "commit", "-q", "-m", message)

    def test_unclaimed_changes_are_flagged(self):
        (self.dir / "notes.txt").write_text("stray\n")
        task = self.add("--path", "src/**", "--base", "main")
        self.assertIn("no open task claims", self.ok("claim", task, "--as", "ann"))
        (self.dir / "src" / "a.py").write_text("changed\n")
        self.assertIn("notes.txt", self.refused("check", task, "--as", "ann"))
        self.assertIn("notes.txt", self.ok("done", task, "--as", "ann"))
        evidence = self.state(task)["evidence"][0]["data"]
        self.assertEqual(evidence["unclaimed"], ["notes.txt"])
        self.assertEqual(evidence["changed_files"], ["src/a.py"])
        (self.dir / "notes.txt").unlink()
        self.ok("check", task)

    def test_work_committed_on_the_base_branch_is_attributed(self):
        task = self.add("--path", "src/**", "--base", "main")
        self.ok("claim", task, "--as", "ann")
        self.commit(f"Batch uploads ({task})", src__a_py="new\n", src__b_py="b\n")
        self.commit("Unrelated work by someone else", docs__x_md="x\n")
        self.commit(f"Report about the task\n\nMentions {task} only in the body", notes__r_md="r\n")
        self.ok("done", task, "--as", "ann")
        evidence = self.state(task)["evidence"][0]["data"]
        self.assertEqual(evidence["changed_files"], ["src/a.py", "src/b.py"])
        self.assertNotIn("out_of_scope", evidence)
        self.assertEqual(len(evidence["attributed_commits"]), 1)

    def test_commit_named_as_evidence_is_attributed_and_audited(self):
        task = self.add("--path", "src/**", "--base", "main")
        self.ok("claim", task, "--as", "ann")
        self.commit("forgot the task id", src__a_py="x\n", README_md="r\n")
        sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=self.dir, capture_output=True, text=True).stdout.strip()
        self.assertIn("0 file(s) attributed", self.ok("check", task))
        text = self.ok("done", task, "--as", "ann", "--evidence", f"commit={sha[:7]}")
        self.assertIn("README.md", text)
        self.assertEqual(self.state(task)["evidence"][0]["data"]["out_of_scope"], ["README.md"])

    def test_nothing_attributed_is_warned_at_done(self):
        task = self.add("--path", "src/**", "--base", "main")
        self.ok("claim", task, "--as", "ann")
        self.assertIn("no change is attributed", self.ok("done", task, "--as", "ann"))

    def test_shared_checkout_separates_other_tasks_work(self):
        mine = self.add("--path", "src/**", "--base", "main")
        theirs = self.add("--path", "docs/**", "--base", "main")
        self.ok("claim", mine, "--as", "ann")
        self.ok("claim", theirs, "--as", "bob")
        (self.dir / "docs").mkdir()
        (self.dir / "docs" / "guide.md").write_text("bob's draft\n")
        (self.dir / "src" / "a.py").write_text("ann's work\n")
        text = self.ok("check", mine, "--as", "ann")
        self.assertIn(f"docs/guide.md  <- {theirs} (bob)", text)
        self.ok("check", theirs, "--as", "bob")
        self.ok("done", mine, "--as", "ann")
        self.assertNotIn("unclaimed", self.state(mine)["evidence"][0]["data"])

    def test_default_store_is_shared_by_every_worktree(self):
        # The runtime runs from wherever the skill is installed; the project it
        # is run in owns the state.
        os.environ.pop("AGENTKIT_DB")
        other = self.dir.parent / (self.dir.name + "-wt")
        git(self.dir, "worktree", "add", "-q", str(other), "-b", "wt")
        try:
            run = lambda cwd, *a: subprocess.run([sys.executable, str(RUNTIME), *a], cwd=cwd,
                                                 capture_output=True, text=True, env=dict(os.environ))
            self.assertEqual(run(self.dir, "register", "lead", "--role", "lead").returncode, 0)
            added = run(self.dir, "add", "--as", "lead", "--title", "t", "--goal", "g")
            self.assertEqual(added.returncode, 0, added.stderr)
            seen = run(other, "show", "T001")
            self.assertEqual(seen.returncode, 0, seen.stderr)
            self.assertTrue((self.dir / ".git" / "agent-kit" / "state.db").is_file())
            self.assertEqual(run(self.dir, "status").stdout.count("state.db"), 1)
            self.assertNotIn("agent-kit/state", subprocess.run(["git", "status", "--porcelain"], cwd=self.dir,
                                                               capture_output=True, text=True).stdout)
        finally:
            git(self.dir, "worktree", "remove", "--force", str(other))


if __name__ == "__main__":
    unittest.main()
