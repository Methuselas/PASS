"""Contracts for CRQ hierarchical evidence synthesis and run finalization.

`prepare-synthesis` packs the frozen intake's cited events six per leaf batch,
checks every summary against the events under its batch, merges four summaries
per parent until one remains, and never lets a parent erase a contradiction.
`finalize` accepts only a disposition that restates the frozen status, never
accepts an unqualified candidate, writes the report and closes the run. The
synthetic library and memory store come from the candidate-freeze suite.
"""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_candidate_qualification_candidate import (  # noqa: E402
    CONTROLLER, DOMAIN, ENTRY, CandidateFixture, crq, schemas, write_text,
)
from test_candidate_qualification_execution import GOOD, ExecutionFixture  # noqa: E402


def events(count: int) -> list[dict]:
    return [
        {"event_id": f"SE_EV_{n:04d}", "date": "2026-09-20", "task": f"Apply the rule to case {n}",
         "validity": "valid"}
        for n in range(1, count + 1)
    ]


class SynthesisFixture(CandidateFixture):
    def run_with_events(self, count: int, run_id: str = "SE_CRQ_0001") -> Path:
        store = self.memory / DOMAIN
        cited = [event["event_id"] for event in events(count)]
        write_text(store / "skill_memory.yaml", yaml.safe_dump({
            "memory_schema_version": 2, "skillset": DOMAIN, "memory_version": 1,
            "entries": [dict(ENTRY, evidence_events=cited, evidence_count=len(cited))],
        }, sort_keys=False))
        write_text(store / "training_history.jsonl", "".join(json.dumps(e) + "\n" for e in events(count)))
        out, _run = crq.prepare(domain=DOMAIN, memory_entry_id="SE_MEM_0001", out=self.workspace / run_id,
                                library_root=self.library, memory_root=self.memory)
        return out

    def packets(self, out: Path, level: int) -> list[tuple[Path, dict]]:
        root = out / "synthesis" / "levels" / str(level)
        return [(batch, json.loads((batch / "input.json").read_text(encoding="utf-8")))
                for batch in sorted(root.iterdir())]

    def summarize(self, out: Path, level: int, contradict: bool = False) -> None:
        """Write a valid summary for every batch of `level`, keeping contradictions."""
        for batch, packet in self.packets(out, level):
            ids = packet["event_ids"]
            inherited = sorted({
                event_id
                for child in packet["children"]
                for event_id in schemas.summary_event_ids(child["summary"], contradictions_only=True)
            })
            conflicts = ([{"note": "One sitting contradicts the others.", "event_ids": ids[-1:]}]
                         if contradict and level == 0 else [])
            if inherited:
                conflicts.append({"note": "Contradictions carried up from below.", "event_ids": inherited})
            crq.write_json_atomic(batch / "summary.json", {
                "schema_version": 1,
                "claims": [{"claim": "The boundary is repeatedly missed.", "supporting_event_ids": ids,
                            "contradicting_event_ids": []}],
                "persistent_failures": [], "stable_successes": [], "boundary_notes": [],
                "unresolved_conflicts": conflicts,
            })

    def complete(self, out: Path) -> list[int]:
        """Drive synthesis to completion; return the batch count at each level."""
        widths = []
        report = crq.prepare_synthesis(out)
        while not report["complete"]:
            widths.append(report["batches"])
            self.summarize(out, report["level"])
            report = crq.prepare_synthesis(out)
        return widths


class PacketTests(SynthesisFixture):
    def test_leaf_batches_hold_every_cited_event_exactly_once(self) -> None:
        out = self.run_with_events(13)
        report = crq.prepare_synthesis(out)
        self.assertEqual(report, {"level": 0, "batches": 3, "complete": False})
        packets = [packet for _batch, packet in self.packets(out, 0)]
        self.assertEqual([len(p["events"]) for p in packets], [6, 6, 1])
        ids = [event_id for packet in packets for event_id in packet["event_ids"]]
        self.assertEqual(ids, [e["event_id"] for e in events(13)])
        self.assertEqual([p["batch_id"] for p in packets], ["L0-B001", "L0-B002", "L0-B003"])
        self.assertEqual(crq.load_run(out)[1]["state"], "prepared", "synthesis never changes state")

    def test_fan_in_terminates_for_one_to_many_batches(self) -> None:
        expected = {1: [1], 2: [2, 1], 3: [3, 1], 4: [4, 1], 5: [5, 2, 1], 17: [17, 5, 2, 1]}
        for number, (batches, widths) in enumerate(expected.items(), start=1):
            with self.subTest(batches=batches):
                out = self.run_with_events(batches * 6, run_id=f"SE_CRQ_{number:04d}")
                self.assertEqual(self.complete(out), widths)
                final = json.loads((out / "synthesis" / "input.json").read_text(encoding="utf-8"))
                self.assertTrue(final["complete"])
                self.assertEqual(final["levels"], len(widths))
                self.assertEqual(len(final["event_ids"]), batches * 6)

    def test_packets_carry_only_cited_memory_events(self) -> None:
        out = self.run_with_events(7)
        self.complete(out)
        final = json.loads((out / "synthesis" / "input.json").read_text(encoding="utf-8"))
        self.assertEqual(final["event_ids"], [e["event_id"] for e in events(7)])
        for _batch, packet in self.packets(out, 0):
            for event in packet["events"]:
                self.assertIn(event["event_id"], final["event_ids"])

    def test_unknown_event_ids_are_refused(self) -> None:
        out = self.run_with_events(8)
        crq.prepare_synthesis(out)
        self.summarize(out, 0)
        batch = out / "synthesis" / "levels" / "0" / "batch-002"
        summary = json.loads((batch / "summary.json").read_text(encoding="utf-8"))
        summary["claims"][0]["supporting_event_ids"].append("SE_EV_0001")
        crq.write_json_atomic(batch / "summary.json", summary)
        with self.assertRaisesRegex(crq.CandidateQualificationError, "SE_EV_0001, which is not an event under this batch"):
            crq.prepare_synthesis(out)
        summary["claims"][0]["supporting_event_ids"] = []
        crq.write_json_atomic(batch / "summary.json", summary)
        with self.assertRaisesRegex(crq.CandidateQualificationError, "must cite at least one event"):
            crq.prepare_synthesis(out)

    def test_missing_summary_blocks_advancing(self) -> None:
        out = self.run_with_events(8)
        crq.prepare_synthesis(out)
        with self.assertRaisesRegex(crq.CandidateQualificationError, "summary.json is missing"):
            crq.prepare_synthesis(out)

    def test_contradictions_survive_every_merge(self) -> None:
        out = self.run_with_events(18)
        crq.prepare_synthesis(out)
        self.summarize(out, 0, contradict=True)
        crq.prepare_synthesis(out)
        (_batch, parent), = self.packets(out, 1)
        self.assertEqual([item["kind"] for item in parent["attention"]], ["unresolved_conflicts"] * 3,
                         "failures and conflicts are surfaced first")
        batch = out / "synthesis" / "levels" / "1" / "batch-001"
        crq.write_json_atomic(batch / "summary.json", {
            "schema_version": 1,
            "claims": [{"claim": "Clean conclusion.", "supporting_event_ids": parent["event_ids"],
                        "contradicting_event_ids": []}],
            "persistent_failures": [], "stable_successes": [], "boundary_notes": [], "unresolved_conflicts": [],
        })
        with self.assertRaisesRegex(crq.CandidateQualificationError, "may not erase a contradiction"):
            crq.prepare_synthesis(out)
        self.summarize(out, 1)
        final = crq.prepare_synthesis(out)
        self.assertTrue(final["complete"])
        summary = json.loads((out / "synthesis" / "input.json").read_text(encoding="utf-8"))
        self.assertEqual(sorted(summary["attention"][0]["event_ids"]), ["SE_EV_0006", "SE_EV_0012", "SE_EV_0018"])

    def test_edited_packet_is_refused(self) -> None:
        out = self.run_with_events(8)
        crq.prepare_synthesis(out)
        self.summarize(out, 0)
        path = out / "synthesis" / "levels" / "0" / "batch-001" / "input.json"
        packet = json.loads(path.read_text(encoding="utf-8"))
        packet["events"] = packet["events"][:1]
        crq.write_json_atomic(path, packet)
        with self.assertRaisesRegex(crq.CandidateQualificationError, "no longer matches"):
            crq.prepare_synthesis(out)

    def test_synthesis_runs_only_before_the_assessment_freezes(self) -> None:
        out = self.make_run()
        with self.assertRaisesRegex(crq.CandidateQualificationError, "runs only in prepared"):
            crq.prepare_synthesis(out)

    def test_summary_shape_is_closed(self) -> None:
        known = {"SE_EV_0001"}
        good = {"schema_version": 1, "claims": [], "persistent_failures": [], "stable_successes": [],
                "boundary_notes": [], "unresolved_conflicts": []}
        self.assertEqual(schemas.validate_summary(good, known), [])
        self.assertTrue(schemas.validate_summary(dict(good, score=1), known))
        self.assertTrue(schemas.validate_summary(dict(good, stable_successes=[{"note": "x"}]), known))
        self.assertTrue(schemas.validate_summary(
            dict(good, boundary_notes=[{"note": "x", "event_ids": ["SE_EV_0009"]}]), known))

    def test_command_line(self) -> None:
        out = self.run_with_events(2)
        run = lambda: subprocess.run([sys.executable, str(CONTROLLER), "prepare-synthesis", "--run", str(out)],
                                     text=True, encoding="utf-8", capture_output=True)
        first = run()
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertIn("SYNTHESIS LEVEL 0: 1 batch(es)", first.stdout)
        self.summarize(out, 0)
        second = run()
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertIn("SYNTHESIS COMPLETE", second.stdout)


class FinalizeTests(ExecutionFixture):
    def evaluated(self, verdicts: dict | None = None, run_id: str = "SE_CRQ_0001") -> Path:
        out = self.open_run(run_id)
        self.grade(out, verdicts or GOOD)
        crq.freeze_execution(out)
        crq.evaluate(out)
        return out

    def disposition(self, out: Path, **changes) -> None:
        path = out / "synthesis" / "disposition.json"
        disposition = json.loads(path.read_text(encoding="utf-8"))
        disposition.update({"synthesis_decision": "accept-canonical-delta",
                            "memory_action": "keep-monitoring",
                            "reason": "The Pattern owns the decision; land it and retest on fresh cases."})
        disposition.update(changes)
        crq.write_json_atomic(path, disposition)

    def assert_refused(self, out: Path, message: str) -> None:
        with self.assertRaisesRegex(crq.CandidateQualificationError, message):
            crq.finalize(out)
        self.assertEqual(crq.load_run(out)[1]["state"], "evaluated")

    def test_evaluate_writes_a_disposition_template_and_review_brief(self) -> None:
        out = self.evaluated()
        disposition = json.loads((out / "synthesis" / "disposition.json").read_text(encoding="utf-8"))
        self.assertEqual(disposition["qualification_status"], "qualified-for-synthesis-review")
        self.assertIsNone(disposition["synthesis_decision"])
        brief = (out / "README.md").read_text(encoding="utf-8")
        self.assertIn("synthesis review", brief)
        self.assertIn("memory.py entry", brief)
        self.assert_refused(out, "synthesis_decision must be one of")

    def test_finalize_writes_the_report_and_closes_read_only(self) -> None:
        library_before = self.library_bytes()
        memory_before = {p: p.read_bytes() for p in self.memory.rglob("*") if p.is_file()}
        out = self.evaluated()
        self.disposition(out)
        run = crq.finalize(out)
        self.assertEqual(run["state"], "finalized")
        self.assertIn("synthesis", run["freezes"])
        report = (out / "synthesis" / "report.md").read_text(encoding="utf-8")
        for heading in ("# Candidate Qualification Report", "## Candidate", "## Why it was proposed",
                        "## Canon ownership assessment", "## Changed cards", "## Target cases",
                        "## Protected cases", "## Synthetic stress cases", "## Baseline vs candidate deltas",
                        "## Regressions", "## Invalid or unresolved evidence", "## Qualification status",
                        "## Recommended synthesis disposition", "## Memory disposition recommendation"):
            self.assertIn(heading, report)
        self.assertIn("qualified-for-synthesis-review", report)
        self.assertIn("accept-canonical-delta", report)
        self.assertEqual(self.library_bytes(), library_before)
        self.assertEqual({p: p.read_bytes() for p in self.memory.rglob("*") if p.is_file()}, memory_before)
        with self.assertRaisesRegex(crq.CandidateQualificationError, "read-only"):
            crq.finalize(out)
        self.assertEqual(crq.status_report(out)["state"], "finalized")

    def test_only_a_qualified_candidate_can_be_accepted(self) -> None:
        out = self.evaluated(dict(GOOD, PROTECT_001=("pass", "fail")))
        self.disposition(out, qualification_status="rejected-regression")
        self.assert_refused(out, "cannot be accepted as a canonical delta")
        self.disposition(out, qualification_status="rejected-regression", synthesis_decision="revise-in-fresh-run",
                         memory_action="keep-monitoring", reason="Fixed the target but broke protection.")
        self.assertEqual(crq.finalize(out)["state"], "finalized")

    def test_disposition_restates_the_frozen_status(self) -> None:
        out = self.evaluated()
        self.disposition(out, qualification_status="invalid")
        self.assert_refused(out, "restate the frozen qualification status")

    def test_memory_action_rules(self) -> None:
        out = self.evaluated()
        self.disposition(out, synthesis_decision="retain-in-memory", memory_action="resolve-after-canon-fix")
        self.assert_refused(out, "resolve-after-canon-fix needs")
        self.disposition(out, memory_action="rewrite-memory")
        self.assert_refused(out, "memory_action must be one of")
        self.disposition(out, reason=" ")
        self.assert_refused(out, "reason must explain")

    def test_edited_disposition_after_finalize_is_detected(self) -> None:
        out = self.evaluated()
        self.disposition(out)
        crq.finalize(out)
        write_text(out / "synthesis" / "report.md", "rewritten\n")
        self.assertEqual(crq.status_report(out)["frozen_files"]["status"], "changed")

    def test_command_line(self) -> None:
        out = self.evaluated()
        self.disposition(out)
        result = subprocess.run([sys.executable, str(CONTROLLER), "finalize", "--run", str(out)],
                                text=True, encoding="utf-8", capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("FINALIZED", result.stdout)


if __name__ == "__main__":
    unittest.main()
