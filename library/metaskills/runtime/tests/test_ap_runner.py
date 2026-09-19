"""The AP runner shows one step at a time and never lets a step go unaccounted."""

import io
import json
import os
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

RUNTIME = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RUNTIME))
import ap_runner as runner  # noqa: E402


def card(path: Path, object_id: str, object_type: str, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\nobject_id: {object_id}\nobject_type: {object_type}\n---\n\n{body}", encoding="utf-8")


LIST_AP = """# Draw a Test Map

## Objective
Carry a map from framework to finish.

## Steps / Flow
1. **Block the framework.** Place land and water first.
2. **Pass the framework gate.** The large arrangement must work before detail.
3. **Refine the coast.** Apply `PAT_refine_the_coast` and `PAT_absent_owner`.
4. **Add color when color is required.** Broad fields first.

## Notes
Order is dependency-based.
"""

BOLD_AP = """# Split Work

## Objective
Split work for parallel execution.

## Steps / Flow

**Entry state.** A working sequential algorithm exists.

**1. Split finely.** Choose the axis first.

*Gate.* If the pieces equal the processors, go back.

**2 — Place the groups.** Map groups to processors.

**Completion.** Every group has a processor.

## Notes
A note.
"""


class RunnerTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.library = self.base / "library"
        card(self.library / "art/maps/AP_draw_a_test_map.md", "AP_draw_a_test_map", "ap", LIST_AP)
        card(self.library / "software/AP_split_work.md", "AP_split_work", "ap", BOLD_AP)
        card(self.library / "art/maps/PAT_refine_the_coast.md", "PAT_refine_the_coast", "pattern",
             "# Refine the Coast\n\n## Pattern Rule\nKeep the broad boundary authoritative.\n")
        environment = patch.dict(os.environ, {"SKILLFORGE_AP_STATE": str(self.base / "state")})
        environment.start()
        self.addCleanup(environment.stop)

    def cli(self, *arguments):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = runner.main(["--library", str(self.library), *arguments])
        return code, out.getvalue(), err.getvalue()

    def begin(self, ap="AP_draw_a_test_map", task="island map"):
        code, out, _ = self.cli("start", "--ap", ap, "--task", task)
        self.assertEqual(code, 0)
        return runner.open_runs()[-1]["run_id"], out

    def state(self, run_id):
        return (self.base / "state" / f"{run_id}.json").read_bytes()

    def test_start_shows_only_the_first_step(self):
        _, out = self.begin()
        self.assertIn("STEP 1", out)
        self.assertIn("Place land and water first", out)
        self.assertNotIn("Refine the coast", out)
        self.assertNotIn("framework gate", out)

    def test_a_later_step_cannot_be_done_first(self):
        run_id, _ = self.begin()
        before = self.state(run_id)
        code, _, err = self.cli("done", "--run", run_id, "--step", "3", "--did", "Refined the coast.")
        self.assertEqual(code, 1)
        self.assertIn("step 1 is the current step", err)
        self.assertEqual(self.state(run_id), before)

    def test_an_empty_account_is_refused(self):
        run_id, _ = self.begin()
        code, _, err = self.cli("done", "--run", run_id, "--step", "1", "--did", "   ")
        self.assertEqual(code, 1)
        self.assertIn("cannot be empty", err)

    def test_a_gate_needs_a_verdict_and_a_fail_keeps_it_current(self):
        run_id, _ = self.begin()
        self.cli("done", "--run", run_id, "--step", "1", "--did", "Blocked land and sea.")
        for command in (("done", "--did", "Looked fine."), ("skip", "--reason", "Not needed.")):
            code, _, err = self.cli(command[0], "--run", run_id, "--step", "2", *command[1:])
            self.assertEqual(code, 1)
            self.assertIn("is a gate", err)
        code, out, _ = self.cli("gate", "--run", run_id, "--step", "2", "--verdict", "fail", "--reason", "The north coast crowds the legend.")
        self.assertEqual(code, 0)
        self.assertIn("failed and stays current", out)
        self.assertEqual(runner.read_run(run_id)["cursor"], 2)
        code, out, _ = self.cli("gate", "--run", run_id, "--step", "2", "--verdict", "pass", "--reason", "Legend space is clear.")
        self.assertIn("STEP 3", out)

    def test_step_shows_the_patterns_it_names(self):
        run_id, _ = self.begin()
        self.cli("done", "--run", run_id, "--step", "1", "--did", "Blocked it.")
        _, out, _ = self.cli("gate", "--run", run_id, "--step", "2", "--verdict", "pass", "--reason", "Works.")
        self.assertIn("--- PAT_refine_the_coast ---", out)
        self.assertIn("Keep the broad boundary authoritative.", out)
        self.assertIn("PAT_absent_owner (not in this installation)", out)

    def test_skip_is_recorded_and_finish_produces_the_record(self):
        run_id, _ = self.begin()
        self.cli("done", "--run", run_id, "--step", "1", "--did", "Blocked it.")
        self.cli("gate", "--run", run_id, "--step", "2", "--verdict", "pass", "--reason", "Works.")
        self.cli("done", "--run", run_id, "--step", "3", "--did", "Refined the coast.")
        code, out, _ = self.cli("skip", "--run", run_id, "--step", "4", "--reason", "Ink-only finish; no color.")
        self.assertEqual(code, 0)
        self.assertIn("finished: every step is accounted for", out)
        _, out, _ = self.cli("record", "--run", run_id)
        record = json.loads(out)
        self.assertTrue(record["complete"])
        self.assertEqual(record["skipped"], [4])
        self.assertEqual([s["outcome"] for s in record["steps"]], ["done", "passed", "done", "skipped"])
        code, _, err = self.cli("done", "--run", run_id, "--step", "4", "--did", "More.")
        self.assertEqual(code, 1)
        self.assertIn("finished", err)

    def test_back_reopens_an_earlier_step(self):
        run_id, _ = self.begin()
        self.cli("done", "--run", run_id, "--step", "1", "--did", "First framework.")
        code, out, _ = self.cli("back", "--run", run_id, "--to", "1", "--reason", "The gate showed the framework cannot hold the legend.")
        self.assertEqual(code, 0)
        self.assertIn("STEP 1", out)
        run = runner.read_run(run_id)
        self.assertEqual(run["cursor"], 1)
        self.assertIsNone(runner.latest(run, 1))

    def test_a_changed_card_stops_the_run(self):
        run_id, _ = self.begin()
        path = self.library / "art/maps/AP_draw_a_test_map.md"
        path.write_text(path.read_text(encoding="utf-8").replace("Place land", "Place all land"), encoding="utf-8")
        code, _, err = self.cli("done", "--run", run_id, "--step", "1", "--did", "Blocked it.")
        self.assertEqual(code, 1)
        self.assertIn("changed since run", err)

    def test_a_fresh_process_resumes_at_the_same_step(self):
        run_id, _ = self.begin()
        self.cli("done", "--run", run_id, "--step", "1", "--did", "Blocked it.")
        code, out, _ = self.cli("current")
        self.assertEqual(code, 0)
        self.assertIn("step 2 of 4  [GATE]", out)

    def test_several_active_runs_must_be_named(self):
        self.begin()
        self.begin("AP_split_work", "parallel sort")
        code, _, err = self.cli("current")
        self.assertEqual(code, 1)
        self.assertIn("name one with --run", err)

    def test_the_same_ap_and_task_cannot_start_twice(self):
        self.begin()
        code, _, err = self.cli("start", "--ap", "AP_draw_a_test_map", "--task", "island map")
        self.assertEqual(code, 1)
        self.assertIn("already stepping", err)

    def test_bold_numbered_steps_with_entry_gate_and_completion(self):
        ap = runner.load_ap(self.library, "AP_split_work")
        self.assertEqual([(s["number"], s["title"], s["gate"]) for s in ap["steps"]],
                         [(1, "Split finely", True), (2, "Place the groups", False)])
        self.assertIn("Entry state", ap["entry"])
        self.assertIn("Every group has a processor", ap["closing"])
        self.assertNotIn("Completion", ap["steps"][1]["text"])

    def test_misnumbered_steps_are_refused(self):
        card(self.library / "x/AP_bad.md", "AP_bad", "ap", LIST_AP.replace("3. **Refine", "5. **Refine"))
        with self.assertRaisesRegex(runner.RunnerError, "numbered 1..N"):
            runner.load_ap(self.library, "AP_bad")

    def test_a_legacy_console_code_page_does_not_break_output(self):
        card(self.library / "x/AP_arrows.md", "AP_arrows", "ap",
             LIST_AP.replace("Place land and water first.", "Framework → detail — never the reverse ≠ polish."))
        raw = io.BytesIO()
        console = io.TextIOWrapper(raw, encoding="cp1252")
        with patch.object(sys, "stdout", console):
            code = runner.main(["--library", str(self.library), "start", "--ap", "AP_arrows"])
            console.flush()
        self.assertEqual(code, 0)
        self.assertIn("Framework → detail — never the reverse ≠ polish.", raw.getvalue().decode("utf-8"))

    def test_every_installed_ap_can_be_stepped(self):
        # Runs against the library this runtime ships in, so a release cannot
        # carry an AP the runner would refuse.
        problems = []
        for path in sorted(runner.LIBRARY.rglob("AP_*.md")):
            try:
                runner.load_ap(runner.LIBRARY, path.stem)
            except runner.RunnerError as exc:
                problems.append(f"{path.stem}: {exc}")
        self.assertEqual(problems, [])


if __name__ == "__main__":
    unittest.main()
