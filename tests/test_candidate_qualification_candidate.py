"""Contracts for CRQ planning, candidate staging and candidate freezing.

Covers `freeze-plan` (case roles, origins, evaluator relations, event
admissibility, fixtures and the protection gap), `stage-candidate` (non-canon
refusal, byte-exact staging, a brief that withholds held-out cases) and
`freeze-candidate` (mutation accounting, the scope ceilings, evidence-free
cards, and the ordinary validators run with `--library` on a temporary overlay).
The library and memory store are synthetic and every card in them passes the
ordinary validator; no canonical card or memory entry is read or written.
"""

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml


ROOT = Path(__file__).resolve().parents[1]
CONTROLLER = ROOT / "PASS" / "runtime" / "pass_candidate_qualification.py"


def load_controller():
    spec = importlib.util.spec_from_file_location("pass_candidate_qualification", CONTROLLER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


crq = load_controller()

DOMAIN = "software-engineering"
CORE = f"{DOMAIN}/core"
TARGET = f"{CORE}/PAT_target.md"
NEW_CARD = f"{CORE}/PAT_new_boundary.md"


def valid_card(relative: str, object_id: str, object_type: str = "pattern",
               foundation: str = "none", links: tuple[tuple[str, str], ...] = (),
               extra: str = "") -> str:
    """A card that passes the ordinary PASS validator."""
    slug = object_id.split("_", 1)[1].replace("_", " ")
    name = f"Decide {slug.title()} Wisely"
    front = {
        "object_id": object_id, "object_type": object_type, "name": name,
        "library_path": relative.split("/")[:-1], "stage_binding": "2 block",
        "lane_fit": "both", "foundation_role": "foundation", "routing_class": "general",
        "specialization_axis": "none", "foundation_object_id": foundation,
        "tags": ["synthetic"],
        "cross_links": [{"rel": rel, "target_object_id": target} for rel, target in links],
        "confidence": "medium", "references": [], "variants": [],
    }
    if object_type == "pattern":
        body = (
            f"## Pattern Rule\n**IF** the {slug} condition appears in a request\n"
            f"**THEN** weigh {slug} consequences before choosing.\n**ELSE** keep the {slug} default.\n\n"
            f"## Do\n- Record {slug} evidence first.\n- Compare {slug} alternatives openly.\n\n"
            f"## Don't\n- Ignore {slug} warnings.\n\n## Checklist\n- The {slug} choice is written down.\n\n"
            f"## Notes\nBackground for {slug} appears here.{extra}\n"
        )
    else:
        body = (
            f"## Objective\nDeliver a {slug} outcome.\n\n## Steps / Flow\n1. Gather {slug} inputs.\n"
            f"2. Apply the {slug} steps.\n\n## Notes\nFlow notes for {slug}.{extra}\n"
        )
    return "---\n" + yaml.safe_dump(front, sort_keys=False) + "---\n\n" + f"# {name}\n\n" + body


CARDS = {
    TARGET: ("PAT_target", "pattern", "PAT_foundation", (("related_to", "PAT_meta_process"),)),
    f"{CORE}/PAT_foundation.md": ("PAT_foundation", "pattern", "none", ()),
    f"{CORE}/PAT_unrelated.md": ("PAT_unrelated", "pattern", "none", ()),
    f"{CORE}/flows/AP_flow.md": ("AP_flow", "ap", "none", (("supports", "PAT_target"),)),
    "metaskills/process/PAT_meta_process.md": ("PAT_meta_process", "pattern", "none", ()),
    "art/figure/PAT_art_only.md": ("PAT_art_only", "pattern", "none", ()),
}
MODULES = {
    f"{CORE}/MODULE.yaml": "software-engineering/core",
    "metaskills/MODULE.yaml": "metaskills",
    "art/figure/MODULE.yaml": "art/figure",
}


def event(event_id: str, **extra) -> dict:
    return {"event_id": event_id, "date": "2026-09-20",
            "task": "Apply the rule to a fresh boundary case", "validity": "valid", **extra}


EVENTS = [
    event("SE_EV_0001", intervention={
        "intervention_id": "INT_1", "kind": "cards", "description": "exposed cards",
        "components": {"card_ids": ["PAT_target", "AP_flow"]},
    }),
    event("SE_EV_0002"),
    event("SE_EV_0003", validity="invalid", invalid_reason="the fixture never ran"),
    event("SE_EV_0004"),
    {"event_id": "SE_EV_0005", "date": "2026-09-21", "task": "Quarantine an earlier sitting",
     "validity": "valid", "event_kind": "evidence_correction", "supersedes_events": ["SE_EV_0004"],
     "corrections": {"disposition": "quarantined", "reason": "cards not exposed"}},
]
ENTRY = {
    "id": "SE_MEM_0001", "scope_type": "pattern", "scope_id": "PAT_target",
    "type": "card_candidate", "evidence_class": "stochastic_performance",
    "observation": "The rule omits a boundary condition that reusable decisions need.",
    "confidence": "repeated", "status": "active",
    "diagnosis": {"failure_layer": "knowledge"},
    "evidence_count": 1, "evidence_events": ["SE_EV_0001"], "likely_owners": ["PAT_target"],
}

TARGET_TASK = "Decide how the service handles a borrowed buffer that outlives its owner."
HELD_OUT_TASK = "Review a pooled allocator whose views are returned across a thread boundary."
STRESS_TASK = "Handle the same borrowed buffer when the owner is released twice."


def plan_entry(case_id: str, **overrides) -> dict:
    entry = {
        "case_id": case_id, "role": "target", "origin": "empirical",
        "evaluation_mode": "semantic", "visibility": "author-visible", "required": True,
        "positive_qualification_eligible": True, "evaluator_relation": "separate",
        "source_event_ids": ["SE_EV_0001"], "purpose": "Reproduce the missing boundary.",
    }
    entry.update(overrides)
    return entry


def default_plan_entries() -> list[dict]:
    return [
        plan_entry("TARGET_001"),
        plan_entry("PROTECT_001", role="protected", visibility="held-out",
                   positive_qualification_eligible=False, source_event_ids=["SE_EV_0002"],
                   purpose="Protect the ordinary owned-lifetime behavior."),
        plan_entry("STRESS_001", role="protected", origin="synthetic", visibility="held-out",
                   positive_qualification_eligible=False, source_event_ids=[],
                   purpose="Probe a nearby lifetime boundary.",
                   in_scope_reason="Double release stays inside the rule's ownership condition."),
        plan_entry("DET_001", origin="deterministic", evaluation_mode="deterministic",
                   evaluator_relation="deterministic", source_event_ids=[],
                   purpose="The regression test for the boundary passes."),
    ]


TASKS = {"TARGET_001": TARGET_TASK, "PROTECT_001": HELD_OUT_TASK, "STRESS_001": STRESS_TASK,
         "DET_001": "Run the boundary regression test."}


def edited(text: str, marker: str = "- Stop when the owner is gone before the view.\n") -> str:
    return text.replace("## Don't\n", marker + "\n## Don't\n", 1)


class CandidateFixture(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name)
        self.library = self.base / "library"
        self.memory = self.base / "memory"
        self.workspace = self.base / "workspace" / "candidate-qualification" / DOMAIN
        for relative, (object_id, object_type, foundation, links) in CARDS.items():
            path = self.library / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(valid_card(relative, object_id, object_type, foundation, links), encoding="utf-8")
        for relative, name in MODULES.items():
            (self.library / relative).write_text(f"name: {name}\nrequires: []\n", encoding="utf-8")
        store = self.memory / DOMAIN
        store.mkdir(parents=True)
        (store / "skill_memory.yaml").write_text(yaml.safe_dump({
            "memory_schema_version": 2, "skillset": DOMAIN, "memory_version": 1, "entries": [ENTRY],
        }, sort_keys=False), encoding="utf-8")
        (store / "training_history.jsonl").write_text(
            "".join(json.dumps(item) + "\n" for item in EVENTS), encoding="utf-8")
        self.overlay_temp = self.base / "tmp"
        self.overlay_temp.mkdir()
        patcher = mock.patch.object(crq.tempfile, "tempdir", str(self.overlay_temp))
        patcher.start()
        self.addCleanup(patcher.stop)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def library_bytes(self) -> dict[Path, bytes]:
        return {p: p.read_bytes() for p in self.library.rglob("*") if p.is_file()}

    def assessment(self, run: dict, disposition: str = "canon-candidate", create: bool = False) -> dict:
        actions = [{"action": "revise", "object_id": "PAT_target", "object_type": "pattern",
                    "reason": "The reusable condition is underspecified."}]
        if create:
            actions.append({"action": "create", "object_id": "PAT_new_boundary", "object_type": "pattern",
                            "relative_path": NEW_CARD, "reason": "A distinct reusable decision."})
        canon = disposition == "canon-candidate"
        return {
            "schema_version": 1, "run_id": run["run_id"], "memory_entry_id": "SE_MEM_0001",
            "candidate_disposition": disposition,
            "failure_layer": "knowledge" if canon else "application",
            "primary_attribution": "skillcard" if canon else "application",
            "owner_object_ids": ["PAT_target"],
            "proposed_object_actions": actions if canon else [],
            "noncanon_failures_considered": [{"kind": "application", "disposition": "not-supported",
                                              "reason": "The card lacks the condition."}],
            "rationale": "The exposed Pattern owns the decision and omits the boundary.",
            "unresolved_questions": [],
        }

    def make_run(self, run_id: str = "SE_CRQ_0001", **options) -> Path:
        disposition = options.pop("disposition", "canon-candidate")
        create = options.pop("create", False)
        out, run = crq.prepare(domain=DOMAIN, memory_entry_id="SE_MEM_0001", out=self.workspace / run_id,
                               library_root=self.library, memory_root=self.memory, **options)
        crq.write_json_atomic(out / "controller" / "assessment.json", self.assessment(run, disposition, create))
        crq.freeze_assessment(out)
        return out

    def write_plan(self, out: Path, entries: list[dict] | None = None, gap: str | None = None,
                   tasks: dict[str, str] | None = None) -> None:
        entries = default_plan_entries() if entries is None else entries
        run = crq.load_run(out)[1]
        crq.write_json_atomic(out / "controller" / "qualification_plan.json", {
            "schema_version": 1, "run_id": run["run_id"], "cases": entries, "protected_case_gap": gap,
        })
        for entry in entries:
            case_dir = out / "cases" / entry["case_id"]
            case_dir.mkdir(parents=True, exist_ok=True)
            fixtures = []
            if entry["evaluation_mode"] == "deterministic":
                fixture = case_dir / "fixture" / "test_boundary.py"
                fixture.parent.mkdir(exist_ok=True)
                fixture.write_text("assert True\n", encoding="utf-8")
                fixtures.append({"path": "fixture/test_boundary.py", "sha256": crq.digest_file(fixture)})
            case = {key: entry[key] for key in crq.CASE_METADATA}
            case.update({
                "schema_version": 1, "case_id": entry["case_id"],
                "task": (tasks or TASKS).get(entry["case_id"], f"Exercise {entry['case_id']}."),
                "success_contract": ["The owner outlives every view."],
                "constraints": ["Same toolchain in both arms."],
                "fixture_manifest": fixtures, "notes": "",
            })
            crq.write_json_atomic(case_dir / "case.json", case)

    def planned_run(self, run_id: str = "SE_CRQ_0001", **options) -> Path:
        out = self.make_run(run_id, **options)
        self.write_plan(out)
        crq.freeze_plan(out)
        return out

    def staged_run(self, run_id: str = "SE_CRQ_0001", **options) -> Path:
        out = self.planned_run(run_id, **options)
        crq.stage_candidate(out)
        return out

    def fill_rationale(self, out: Path) -> None:
        path = out / "controller" / "candidate_manifest.json"
        manifest = json.loads(path.read_text(encoding="utf-8"))
        for change in manifest["changes"]:
            change["rationale"] = "Adds the missing ownership boundary."
        crq.write_json_atomic(path, manifest)

    def candidate(self, out: Path, relative: str = TARGET) -> Path:
        return out / "candidate" / "cards" / relative

    def author(self, out: Path) -> None:
        path = self.candidate(out)
        path.write_text(edited(path.read_text(encoding="utf-8")), encoding="utf-8")
        self.fill_rationale(out)

    def state(self, out: Path) -> str:
        return crq.load_run(out)[1]["state"]


class PlanTests(CandidateFixture):
    def assert_plan_refused(self, entries: list[dict], message: str, gap: str | None = None) -> None:
        shutil.rmtree(self.workspace, ignore_errors=True)
        out = self.make_run()
        self.write_plan(out, entries, gap)
        with self.assertRaisesRegex(crq.CandidateQualificationError, message):
            crq.freeze_plan(out)
        self.assertEqual(self.state(out), "assessment-frozen")
        self.assertFalse((out / "controller" / "plan.freeze.json").exists())

    def test_freeze_assessment_writes_a_plan_template(self) -> None:
        out = self.make_run()
        plan = json.loads((out / "controller" / "qualification_plan.json").read_text(encoding="utf-8"))
        self.assertEqual(plan["cases"], [])
        with self.assertRaisesRegex(crq.CandidateQualificationError, "at least one case"):
            crq.freeze_plan(out)

    def test_valid_plan_freezes_every_case_and_fixture(self) -> None:
        out = self.planned_run()
        run = crq.load_run(out)[1]
        self.assertEqual(run["state"], "plan-frozen")
        record = json.loads((out / "controller" / "plan.freeze.json").read_text(encoding="utf-8"))
        self.assertEqual(sorted(item["path"] for item in record["files"]), sorted([
            "controller/qualification_plan.json", "cases/DET_001/case.json",
            "cases/DET_001/fixture/test_boundary.py", "cases/PROTECT_001/case.json",
            "cases/STRESS_001/case.json", "cases/TARGET_001/case.json",
        ]))
        status = crq.status_report(out)
        self.assertEqual(status["cases"]["by_role"], {"target": 2, "protected": 2})

    def test_frozen_case_or_fixture_edits_block_staging(self) -> None:
        for number, relative in enumerate(("cases/PROTECT_001/case.json", "cases/DET_001/fixture/test_boundary.py"), 1):
            with self.subTest(file=relative):
                out = self.planned_run(f"SE_CRQ_{number:04d}")
                (out / relative).write_text((out / relative).read_text(encoding="utf-8") + " ", encoding="utf-8")
                with self.assertRaisesRegex(crq.CandidateQualificationError, "changed after it was frozen"):
                    crq.stage_candidate(out)
                self.assertEqual(self.state(out), "plan-frozen")

    def test_plan_requires_an_eligible_real_target(self) -> None:
        protect = default_plan_entries()[1]
        self.assert_plan_refused([protect], "required target case")
        self.assert_plan_refused(
            [plan_entry("TARGET_001", positive_qualification_eligible=False), protect],
            "eligible for positive qualification")
        self.assert_plan_refused([plan_entry("TARGET_001", required=False), protect], "required target")

    def test_protection_gap_must_be_recorded_exactly_when_it_exists(self) -> None:
        target, protect, stress = default_plan_entries()[:3]
        self.assert_plan_refused([target, stress], "record protected_case_gap")
        self.assert_plan_refused([target, protect], "protected_case_gap must be null", gap="none available")
        self.assert_plan_refused([target, dict(protect, required=False)], "record protected_case_gap")
        shutil.rmtree(self.workspace)
        out = self.make_run()
        self.write_plan(out, [target, stress], gap="No established independent protected case is available.")
        self.assertEqual(crq.freeze_plan(out)["state"], "plan-frozen")

    def test_synthetic_cases_are_protected_stress_probes_only(self) -> None:
        target, protect, stress = default_plan_entries()[:3]
        for changes, message in (
            ({"positive_qualification_eligible": True}, "never provides positive qualification"),
            ({"role": "target"}, "may only be protected"),
            ({"source_event_ids": ["SE_EV_0002"]}, "cites no empirical event"),
            ({"in_scope_reason": " "}, "in_scope_reason"),
        ):
            with self.subTest(changes=changes):
                self.assert_plan_refused([target, protect, dict(stress, **changes)], message)
                without_reason = {k: v for k, v in stress.items() if k != "in_scope_reason"}
        self.assert_plan_refused([target, protect, without_reason], "in_scope_reason")
        self.assert_plan_refused([dict(target, in_scope_reason="x"), protect], "only to a synthetic case")

    def test_only_targets_provide_positive_qualification(self) -> None:
        target, protect = default_plan_entries()[:2]
        self.assert_plan_refused([target, dict(protect, positive_qualification_eligible=True)],
                                 "only a target case can provide positive qualification")

    def test_evaluator_relation_matches_the_mode(self) -> None:
        target, protect = default_plan_entries()[:2]
        self.assert_plan_refused([target, dict(protect, evaluator_relation="same-reader")],
                                 "required semantic case must be graded by a separate evaluator")
        self.assert_plan_refused([target, protect, dict(default_plan_entries()[3], evaluator_relation="separate")],
                                 "checked deterministically")
        self.assert_plan_refused([target, dict(protect, evaluator_relation="deterministic")],
                                 "separate or same-reader")
        shutil.rmtree(self.workspace)
        out = self.make_run()
        diagnostic = plan_entry("DIAG_001", role="protected", required=False, evaluator_relation="same-reader",
                                positive_qualification_eligible=False, source_event_ids=["SE_EV_0002"])
        self.write_plan(out, [target, protect, diagnostic])
        self.assertEqual(crq.freeze_plan(out)["state"], "plan-frozen")

    def test_empirical_cases_cite_admissible_events(self) -> None:
        target, protect = default_plan_entries()[:2]
        for events, message in (
            ([], "cites the events it comes from"),
            (["SE_EV_0003"], "SE_EV_0003 is not a valid"),
            (["SE_EV_0004"], "SE_EV_0004 is not a valid"),
            (["SE_EV_0005"], "SE_EV_0005 is not a valid"),
            (["SE_EV_0404"], "SE_EV_0404 is not a valid"),
        ):
            with self.subTest(events=events):
                self.assert_plan_refused([target, dict(protect, source_event_ids=events)], message)
        
    def test_closed_vocabularies_and_identity(self) -> None:
        target, protect = default_plan_entries()[:2]
        for changes, message in (
            ({"role": "support"}, "role must be one of"),
            ({"origin": "dream"}, "origin must be one of"),
            ({"visibility": "hidden"}, "visibility must be one of"),
            ({"required": "yes"}, "required must be true or false"),
            ({"case_id": "protect-1"}, "case_id must look like"),
            ({"purpose": ""}, "purpose"),
            ({"score": 1}, "must have"),
        ):
            with self.subTest(changes=changes):
                self.assert_plan_refused([target, dict(protect, **changes)], message)
                self.assert_plan_refused([target, dict(target)], "repeats")

    def test_case_files_must_agree_with_the_plan(self) -> None:
        out = self.make_run()
        self.write_plan(out)
        case_path = out / "cases" / "PROTECT_001" / "case.json"
        pristine = json.loads(case_path.read_text(encoding="utf-8"))
        for changes, message in (
            ({"visibility": "author-visible"}, "visibility disagrees with the plan"),
            ({"task": " "}, "task must be"),
            ({"success_contract": []}, "at least one observable criterion"),
            ({"success_contract": ["a", "a"]}, "may not repeat"),
            ({"constraints": "none"}, "constraints must be a list"),
            ({"case_id": "OTHER_001"}, "different case"),
            ({"verdict": "pass"}, "must have exactly"),
        ):
            with self.subTest(changes=changes):
                crq.write_json_atomic(case_path, dict(pristine, **changes))
                with self.assertRaisesRegex(crq.CandidateQualificationError, message):
                    crq.freeze_plan(out)
        crq.write_json_atomic(case_path, pristine)
        self.assertEqual(crq.freeze_plan(out)["state"], "plan-frozen")

    def test_case_directories_are_accounted_for(self) -> None:
        cases = (
            (lambda out: (out / "cases" / "EXTRA_001").mkdir(), "cases/EXTRA_001 is not a planned case"),
            (lambda out: (out / "cases" / "TARGET_001" / "case.json").unlink(), "case.json is missing"),
            (lambda out: (out / "cases" / "TARGET_001" / "baseline").mkdir(), "unexpected cases/TARGET_001/baseline"),
            (lambda out: (out / "cases" / "DET_001" / "fixture" / "extra.txt").write_text("x"), "not in fixture_manifest"),
            (lambda out: (out / "cases" / "DET_001" / "fixture" / "test_boundary.py").write_text("changed"), "does not match its sha256"),
        )
        for number, (damage, message) in enumerate(cases, start=1):
            with self.subTest(message=message):
                out = self.make_run(f"SE_CRQ_{number:04d}")
                self.write_plan(out)
                damage(out)
                with self.assertRaisesRegex(crq.CandidateQualificationError, message):
                    crq.freeze_plan(out)

    def test_fixture_paths_are_bounded(self) -> None:
        out = self.make_run()
        self.write_plan(out)
        case_path = out / "cases" / "DET_001" / "case.json"
        case = json.loads(case_path.read_text(encoding="utf-8"))
        for path, message in (("../TARGET_001/case.json", "bounded"), ("case.json", "under fixture/"),
                              ("fixture/missing.py", "does not exist")):
            with self.subTest(path=path):
                crq.write_json_atomic(case_path, dict(case, fixture_manifest=[{"path": path, "sha256": "0" * 64}]))
                with self.assertRaisesRegex(crq.CandidateQualificationError, message):
                    crq.freeze_plan(out)


class StagingTests(CandidateFixture):
    def test_noncanon_assessment_is_never_staged(self) -> None:
        # Fixture C: an application lapse freezes for the record and stops there.
        out = self.make_run(disposition="memory-only")
        self.write_plan(out)
        crq.freeze_plan(out)
        with self.assertRaisesRegex(crq.CandidateQualificationError, "routes this candidate to memory-only"):
            crq.stage_candidate(out)
        self.assertEqual(self.state(out), "plan-frozen")
        self.assertFalse((out / "candidate").exists())
        self.assertEqual(crq.abandon(out, "application lapse; lesson kept in memory")["state"], "abandoned")

    def test_staging_copies_revisions_and_prepares_new_card_folders(self) -> None:
        out = self.staged_run(create=True)
        self.assertEqual(self.state(out), "candidate-staged")
        self.assertEqual(self.candidate(out).read_bytes(), (out / "baseline" / "cards" / TARGET).read_bytes())
        self.assertTrue(self.candidate(out, NEW_CARD).parent.is_dir())
        self.assertFalse(self.candidate(out, NEW_CARD).exists(), "Python never writes card content")
        files = sorted(p.relative_to(out / "candidate" / "cards").as_posix()
                       for p in (out / "candidate" / "cards").rglob("*") if p.is_file())
        self.assertEqual(files, [TARGET], "support cards are never staged for editing")
        manifest = json.loads((out / "controller" / "candidate_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual([(c["action"], c["object_id"], c["rationale"]) for c in manifest["changes"]],
                         [("revise", "PAT_target", ""), ("create", "PAT_new_boundary", "")])

    def test_author_brief_withholds_held_out_cases(self) -> None:
        out = self.staged_run()
        brief = (out / "README.md").read_text(encoding="utf-8")
        self.assertIn(TARGET_TASK, brief)
        self.assertIn("Run the boundary regression test.", brief)
        self.assertIn("2 held-out case(s) are intentionally withheld", brief)
        for hidden in (HELD_OUT_TASK, STRESS_TASK, "PROTECT_001", "STRESS_001"):
            self.assertNotIn(hidden, brief)
        for rule in ("Never edit `library/`", "never names this run", "revise pattern `PAT_target`"):
            self.assertIn(rule, brief)

    def test_leftover_candidate_folder_is_refused(self) -> None:
        out = self.planned_run()
        (out / "candidate").mkdir()
        with self.assertRaisesRegex(crq.CandidateQualificationError, "already exists"):
            crq.stage_candidate(out)
        self.assertEqual(self.state(out), "plan-frozen")


class FreezeCandidateTests(CandidateFixture):
    def assert_refused(self, out: Path, message: str) -> None:
        before = (out / "controller" / "run.json").read_bytes()
        with self.assertRaisesRegex(crq.CandidateQualificationError, message):
            crq.freeze_candidate(out)
        self.assertEqual((out / "controller" / "run.json").read_bytes(), before)
        self.assertFalse((out / "controller" / "candidate.freeze.json").exists())
        self.assertEqual(list(self.overlay_temp.iterdir()), [], "the overlay is always removed")

    def test_valid_candidate_freezes_with_full_accounting(self) -> None:
        library_before = self.library_bytes()
        out = self.staged_run()
        self.author(out)
        run = crq.freeze_candidate(out)
        self.assertEqual(run["state"], "candidate-frozen")
        self.assertEqual(self.library_bytes(), library_before, "canon is never written")
        self.assertEqual(list(self.overlay_temp.iterdir()), [], "the overlay is removed after success")
        manifest = json.loads((out / "controller" / "candidate_manifest.json").read_text(encoding="utf-8"))
        change = manifest["changes"][0]
        self.assertEqual(change["accounting"], "applied-to-candidate")
        self.assertEqual(change["changed_sections"], ["Do"])
        self.assertEqual(change["baseline_sha256"], crq.digest_file(out / "baseline" / "cards" / TARGET))
        self.assertEqual(change["candidate_sha256"], crq.digest_file(self.candidate(out)))
        self.assertEqual(change["rationale"], "Adds the missing ownership boundary.")
        self.assertEqual(manifest["unmatched_actions"], [])
        self.assertEqual(manifest["scope"], {
            "changed_existing_cards": 1, "new_cards": 0, "deleted_cards": 0,
            "renamed_object_ids": 0, "moved_existing_cards": 0,
        })
        self.assertEqual(crq.status_report(out)["candidate_mutations"]["changed_existing_cards"], 1)

    def test_new_card_is_accounted_and_validated(self) -> None:
        out = self.staged_run(create=True)
        self.author(out)
        self.candidate(out, NEW_CARD).write_text(
            valid_card(NEW_CARD, "PAT_new_boundary", links=(("related_to", "PAT_target"),)), encoding="utf-8")
        crq.freeze_candidate(out)
        manifest = json.loads((out / "controller" / "candidate_manifest.json").read_text(encoding="utf-8"))
        created = next(c for c in manifest["changes"] if c["action"] == "create")
        self.assertIsNone(created["baseline_sha256"])
        self.assertEqual(manifest["scope"]["new_cards"], 1)

    def test_candidate_edit_after_freeze_blocks_execution(self) -> None:
        out = self.staged_run()
        self.author(out)
        crq.freeze_candidate(out)
        self.candidate(out).write_text(edited(self.candidate(out).read_text(encoding="utf-8"), "- Later.\n"),
                                       encoding="utf-8")
        with self.assertRaisesRegex(crq.CandidateQualificationError, "changed after it was frozen"):
            crq.apply_transition(out, "open-execution")

    def test_unmatched_actions_block_the_freeze(self) -> None:
        def unchanged(out: Path) -> None:
            self.fill_rationale(out)

        def whitespace(out: Path) -> None:
            path = self.candidate(out)
            path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))
            self.fill_rationale(out)

        def deleted(out: Path) -> None:
            self.candidate(out).unlink()
            self.fill_rationale(out)

        def renamed(out: Path) -> None:
            path = self.candidate(out)
            path.write_text(edited(path.read_text(encoding="utf-8")).replace(
                "object_id: PAT_target", "object_id: PAT_target_renamed"), encoding="utf-8")
            self.fill_rationale(out)

        def retyped(out: Path) -> None:
            path = self.candidate(out)
            path.write_text(edited(path.read_text(encoding="utf-8")).replace(
                "object_type: pattern", "object_type: drill"), encoding="utf-8")
            self.fill_rationale(out)

        def unauthorized(out: Path) -> None:
            self.author(out)
            extra = self.candidate(out, f"{CORE}/PAT_extra.md")
            extra.write_text(valid_card(f"{CORE}/PAT_extra.md", "PAT_extra"), encoding="utf-8")

        def support_changed(out: Path) -> None:
            self.author(out)
            support = self.candidate(out, f"{CORE}/PAT_foundation.md")
            support.write_text(edited((self.library / CORE / "PAT_foundation.md").read_text(encoding="utf-8")),
                               encoding="utf-8")

        def moved(out: Path) -> None:
            source = self.candidate(out)
            destination = self.candidate(out, f"{CORE}/moved/PAT_target.md")
            destination.parent.mkdir()
            destination.write_text(edited(source.read_text(encoding="utf-8")), encoding="utf-8")
            source.unlink()
            self.fill_rationale(out)

        cases = (
            (unchanged, "byte-identical to the baseline"),
            (whitespace, "only whitespace or line endings changed"),
            (deleted, "deleting a card is never allowed"),
            (renamed, "renaming is never allowed"),
            (retyped, "object_type is 'drill'"),
            (unauthorized, "never authorized by the frozen assessment"),
            (support_changed, "copy of existing card PAT_foundation"),
            (moved, "copy of existing card PAT_target"),
        )
        for number, (damage, message) in enumerate(cases, start=1):
            with self.subTest(case=damage.__name__):
                out = self.staged_run(f"SE_CRQ_{number:04d}")
                damage(out)
                self.assert_refused(out, message)

    def test_missing_new_card_is_unmatched(self) -> None:
        out = self.staged_run(create=True)
        self.author(out)
        self.assert_refused(out, "created no card")

    def test_manifest_template_is_checked(self) -> None:
        out = self.staged_run()
        path = self.candidate(out)
        path.write_text(edited(path.read_text(encoding="utf-8")), encoding="utf-8")
        self.assert_refused(out, "rationale must explain")
        manifest_path = out / "controller" / "candidate_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["changes"][0].update(rationale="ok", object_id="PAT_unrelated")
        crq.write_json_atomic(manifest_path, manifest)
        self.assert_refused(out, "exactly the frozen assessment's actions")

    def test_cards_may_not_name_run_evidence(self) -> None:
        for number, token in enumerate(("SE_CRQ_0001", "SE_MEM_0001", "SE_EV_0001", "TARGET_001",
                                        "workspace/candidate-qualification/x", "ART_EV_0042"), start=1):
            with self.subTest(token=token):
                out = self.staged_run(f"SE_CRQ_{number:04d}")
                path = self.candidate(out)
                path.write_text(edited(path.read_text(encoding="utf-8"), f"- Learned from {token} evidence.\n"),
                                encoding="utf-8")
                self.fill_rationale(out)
                self.assert_refused(out, "names run evidence")

    def test_overlay_runs_the_ordinary_validators(self) -> None:
        def missing_key(text: str) -> str:
            return edited(text).replace("confidence: medium\n", "")

        def dangling(text: str) -> str:
            return edited(text).replace("target_object_id: PAT_meta_process", "target_object_id: PAT_nowhere")

        def cross_domain(text: str) -> str:
            return edited(text).replace("target_object_id: PAT_meta_process", "target_object_id: PAT_art_only")

        def placeholder(text: str) -> str:
            return edited(text, "- Replace <this token> later.\n")

        for number, (damage, message) in enumerate((
            (missing_key, "rule 2: missing keys: confidence"),
            (dangling, "unresolved cross_link target PAT_nowhere"),
            (cross_domain, "rule 26"),
            (placeholder, "rule 8"),
        ), start=1):
            with self.subTest(case=damage.__name__):
                out = self.staged_run(f"SE_CRQ_{number:04d}")
                path = self.candidate(out)
                path.write_text(damage(path.read_text(encoding="utf-8")), encoding="utf-8")
                self.fill_rationale(out)
                self.assert_refused(out, "validate.py --library <overlay> failed(.|\\n)*" + message)

    def test_new_card_identity_and_destination_are_checked(self) -> None:
        out = self.staged_run(create=True)
        self.author(out)
        manifest = out / "controller" / "candidate_manifest.json"
        self.candidate(out, NEW_CARD).write_text(
            valid_card(NEW_CARD, "PAT_new_boundary").replace("object_id: PAT_new_boundary", "object_id: PAT_art_only"),
            encoding="utf-8")
        self.assert_refused(out, "renaming is never allowed")
        self.assertTrue(manifest.is_file())
        self.candidate(out, NEW_CARD).unlink()
        run = crq.load_run(out)[1]
        (self.library / CORE / "PAT_new_boundary.md").write_text("occupied\n", encoding="utf-8")
        self.candidate(out, NEW_CARD).write_text(valid_card(NEW_CARD, "PAT_new_boundary"), encoding="utf-8")
        self.assert_refused(out, "now exists in the library")
        self.assertEqual(run["state"], "candidate-staged")

    def test_overlay_refuses_a_duplicate_id_from_a_domain_the_run_never_reads(self) -> None:
        cards = self.base / "cards"
        duplicate = cards / NEW_CARD
        duplicate.parent.mkdir(parents=True)
        duplicate.write_text(valid_card(NEW_CARD, "PAT_new_boundary").replace(
            "object_id: PAT_new_boundary", "object_id: PAT_art_only"), encoding="utf-8")
        problems = crq.overlay_problems(self.library, cards, [NEW_CARD])
        self.assertTrue(problems and "duplicate object_id PAT_art_only" in problems[0], problems)
        self.assertEqual(crq.overlay_problems(self.library, cards, []), [])
        self.assertEqual(list(self.overlay_temp.iterdir()), [])

    def test_tools_run_in_process_without_leaking(self) -> None:
        def tool_modules() -> set[str]:
            return {
                name for name, module in list(sys.modules.items())
                if not name.startswith("_pass_crq_tool_")
                and Path(getattr(module, "__file__", None) or "").parent == crq.TOOLS_DIR
            }

        crq._TOOLS.clear()
        path_before, modules_before = list(sys.path), tool_modules()
        code, output = crq.run_tool_cli("validate", ["--library", str(self.library)])
        self.assertEqual(code, 0, output)
        self.assertIn("PASS", output)
        self.assertEqual(sys.path, path_before)
        self.assertEqual(tool_modules(), modules_before, "no PASS/tools module leaks under its own name")


class CommandLineTests(CandidateFixture):
    def cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, str(CONTROLLER), *args],
                              text=True, encoding="utf-8", capture_output=True)

    def test_plan_stage_and_freeze_commands(self) -> None:
        out = self.make_run()
        self.write_plan(out)
        for command, expected in (("freeze-plan", "PLAN FROZEN"), ("stage-candidate", "CANDIDATE STAGED")):
            result = self.cli(command, "--run", str(out))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(expected, result.stdout)
        failed = self.cli("freeze-candidate", "--run", str(out))
        self.assertEqual(failed.returncode, 2)
        self.assertIn("candidate cannot be frozen", failed.stderr)
        self.author(out)
        result = self.cli("freeze-candidate", "--run", str(out))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("CANDIDATE FROZEN", result.stdout)
        self.assertEqual(self.state(out), "candidate-frozen")


if __name__ == "__main__":
    unittest.main()
