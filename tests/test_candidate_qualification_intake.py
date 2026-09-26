"""Contracts for CRQ intake and defect assessment.

Covers `prepare` (a Skillset Memory `card_candidate` resolved through
`memory.py`, owner resolution inside one domain plus metaskills, and the frozen
baseline snapshot) and `freeze-assessment` (disposition routing, owner and
exposure checks, bounded object actions). The library and memory store are
synthetic; no canonical card or memory entry is read or written.
"""

from __future__ import annotations

import importlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "PASS" / "runtime"
CONTROLLER = RUNTIME / "pass_candidate_qualification.py"


def load_package(runtime: Path, name: str = "candidate_qualification"):
    """Load the CRQ package found in `runtime` under `name`; return its controller."""
    if name not in sys.modules:
        package_dir = runtime / "candidate_qualification"
        spec = importlib.util.spec_from_file_location(
            name, package_dir / "__init__.py", submodule_search_locations=[str(package_dir)]
        )
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return importlib.import_module(f"{name}.controller")


crq = load_package(RUNTIME)
schemas = importlib.import_module("candidate_qualification.schemas")
evidence = importlib.import_module("candidate_qualification.evidence")


def write_text(path: Path, text: str) -> None:
    """Write exact bytes: no newline translation, so tests match on every platform."""
    path.write_bytes(text.encode("utf-8"))

DOMAIN = "software-engineering"
CORE = f"{DOMAIN}/core"


def card(object_id: str, object_type: str = "pattern", foundation: str = "none",
         links: tuple[tuple[str, str], ...] = ()) -> str:
    front = {
        "object_id": object_id,
        "object_type": object_type,
        "name": object_id.replace("_", " ").title(),
        "foundation_object_id": foundation,
        "cross_links": [{"rel": rel, "target_object_id": target} for rel, target in links],
    }
    return "---\n" + yaml.safe_dump(front, sort_keys=False) + "---\n\n# body\n"


# object_id -> (package-relative path, card text)
CARDS = {
    "PAT_target": (f"{CORE}/PAT_target.md", card(
        "PAT_target", foundation="PAT_foundation",
        links=(("related_to", "PAT_related"), ("related_to", "PAT_meta_process")),
    )),
    "PAT_foundation": (f"{CORE}/PAT_foundation.md", card("PAT_foundation", foundation="PAT_root")),
    "PAT_root": (f"{CORE}/PAT_root.md", card("PAT_root")),
    "PAT_prereq": (f"{CORE}/PAT_prereq.md", card(
        "PAT_prereq", links=(("prerequisite_for", "PAT_target"),),
    )),
    "PAT_related": (f"{CORE}/PAT_related.md", card("PAT_related", links=(("related_to", "PAT_far"),))),
    "PAT_far": (f"{CORE}/PAT_far.md", card("PAT_far")),
    "PAT_unrelated": (f"{CORE}/PAT_unrelated.md", card("PAT_unrelated")),
    "AP_flow": (f"{CORE}/flows/AP_flow.md", card("AP_flow", "ap", links=(("supports", "PAT_target"),))),
    "PAT_meta_process": ("metaskills/process/PAT_meta_process.md", card("PAT_meta_process")),
    "PAT_art_only": ("art/figure/PAT_art_only.md", card("PAT_art_only")),
}
MODULES = {
    f"{CORE}/MODULE.yaml": "name: software-engineering/core\nrequires: []\n",
    "metaskills/MODULE.yaml": "name: metaskills\nrequires: []\n",
    "art/figure/MODULE.yaml": "name: art/figure\nrequires: []\n",
}


def event(event_id: str, **extra) -> dict:
    return {
        "event_id": event_id, "date": "2026-09-20",
        "task": "Apply the rule to a fresh boundary case", "validity": "valid", **extra,
    }


def exposing(*card_ids: str) -> dict:
    return {"intervention": {
        "intervention_id": "INT_1", "kind": "cards", "description": "exposed cards",
        "components": {"card_ids": list(card_ids)},
    }}


EVENTS = [
    event("SE_EV_0001", **exposing("PAT_target", "AP_flow")),
    event("SE_EV_0002"),
    event("SE_EV_0003", validity="invalid", invalid_reason="the fixture never ran"),
    event("SE_EV_0004"),
    {
        "event_id": "SE_EV_0005", "date": "2026-09-21", "task": "Quarantine an earlier sitting",
        "validity": "valid", "event_kind": "evidence_correction", "supersedes_events": ["SE_EV_0004"],
        "corrections": {"disposition": "quarantined", "reason": "the cards under test were not exposed"},
    },
    event("SE_EV_0006"),
]


def entry(entry_id: str, **overrides) -> dict:
    base = {
        "id": entry_id, "scope_type": "pattern", "scope_id": "PAT_target",
        "type": "card_candidate", "evidence_class": "stochastic_performance",
        "observation": "The rule omits a boundary condition that reusable decisions need.",
        "confidence": "repeated", "status": "active",
        "diagnosis": {"failure_layer": "knowledge", "hypothesis": "The IF clause is too narrow."},
        "evidence_count": 2, "evidence_events": ["SE_EV_0001", "SE_EV_0002"],
        "likely_owners": ["PAT_target", "PAT_meta_process", "the boundary handling guidance"],
    }
    base.update(overrides)
    if "evidence_events" in overrides:
        base["evidence_count"] = len(overrides["evidence_events"]) or 1
        if not overrides["evidence_events"]:
            base.pop("evidence_events")
            base.pop("evidence_count")
    return base


ENTRIES = [
    entry("SE_MEM_0001"),
    entry("SE_MEM_0002", type="learned_principle"),
    entry("SE_MEM_0003", status="resolved"),
    entry("SE_MEM_0004", evidence_events=[]),
    entry("SE_MEM_0005", likely_owners=["PAT_art_only"]),
    entry("SE_MEM_0006", likely_owners=["PAT_missing"]),
    entry("SE_MEM_0007", likely_owners=["Build the Target Rule", "PAT_meta_process"]),
    entry("SE_MEM_0008", status="monitoring", evidence_events=["SE_EV_0006"]),
]


class IntakeFixture(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name)
        self.library = self.base / "library"
        self.memory = self.base / "memory"
        self.workspace = self.base / "workspace" / "candidate-qualification" / DOMAIN
        for relative, text in [*CARDS.values(), *MODULES.items()]:
            path = self.library / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            write_text(path, text)
        self.write_memory(ENTRIES, EVENTS)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write_memory(self, entries: list[dict], events: list[dict]) -> None:
        store = self.memory / DOMAIN
        store.mkdir(parents=True, exist_ok=True)
        write_text((store / "skill_memory.yaml"), yaml.safe_dump({
            "memory_schema_version": 2, "skillset": DOMAIN, "memory_version": 1,
            "entries": entries,
        }, sort_keys=False))
        write_text((store / "training_history.jsonl"),
            "".join(json.dumps(item) + "\n" for item in events))

    def canon_bytes(self) -> dict[Path, bytes]:
        return {
            path: path.read_bytes()
            for root in (self.library, self.memory) for path in root.rglob("*") if path.is_file()
        }

    def prepare(self, entry_id: str = "SE_MEM_0001", run_id: str = "SE_CRQ_0001", **options):
        return crq.prepare(
            domain=DOMAIN, memory_entry_id=entry_id, out=self.workspace / run_id,
            library_root=self.library, memory_root=self.memory, **options,
        )


class PrepareTests(IntakeFixture):
    def test_valid_candidate_prepares_a_run_without_touching_canon_or_memory(self) -> None:
        before = self.canon_bytes()
        out, run = self.prepare()
        self.assertEqual(run["state"], "prepared")
        self.assertEqual(run["memory_entry_id"], "SE_MEM_0001")
        self.assertEqual(sorted(run["freezes"]), ["intake"])
        self.assertEqual(self.canon_bytes(), before)
        self.assertEqual(crq.status_report(out)["baseline"]["status"], "clean")
        self.assertEqual(crq.status_report(out)["assessment"], "draft")
        self.assertEqual([path.name for path in self.workspace.iterdir()], ["SE_CRQ_0001"])

    def test_baseline_holds_targets_bounded_support_and_module_manifests(self) -> None:
        out, run = self.prepare()
        manifest = crq.load_baseline_manifest(out, run)
        roles = {entry["relative_path"]: entry["role"] for entry in manifest["entries"]}
        path = {object_id: relative for object_id, (relative, _text) in CARDS.items()}
        self.assertEqual(roles[path["PAT_target"]], "target")
        for support in ("PAT_foundation", "PAT_root", "PAT_prereq", "PAT_related", "PAT_meta_process"):
            self.assertEqual(roles[path[support]], "support", support)
        for outside in ("PAT_far", "PAT_unrelated", "AP_flow", "PAT_art_only"):
            self.assertNotIn(path[outside], roles, f"{outside} is outside the bounded closure")
        self.assertEqual(roles[f"{CORE}/MODULE.yaml"], "module-manifest")
        self.assertEqual(roles["metaskills/MODULE.yaml"], "module-manifest")
        self.assertNotIn("art/figure/MODULE.yaml", roles)

    def test_baseline_freezes_exact_bytes(self) -> None:
        target = self.library / CARDS["PAT_target"][0]
        target.write_bytes(target.read_bytes().replace(b"\n", b"\r\n"))
        out, run = self.prepare()
        snapshot = out / "baseline" / "cards" / CARDS["PAT_target"][0]
        self.assertEqual(snapshot.read_bytes(), target.read_bytes())
        entry = next(e for e in crq.load_baseline_manifest(out, run)["entries"] if e["object_id"] == "PAT_target")
        self.assertEqual(entry["sha256"], crq.digest_bytes(target.read_bytes()))

    def test_intake_freezes_the_entry_events_and_owner_resolution(self) -> None:
        out, run = self.prepare()
        intake = crq.load_intake(out, run)
        self.assertEqual(intake["memory_entry"]["id"], "SE_MEM_0001")
        self.assertEqual([e["event_id"] for e in intake["events"]], ["SE_EV_0001", "SE_EV_0002"])
        self.assertEqual(
            [(o["label"], o["resolution"]) for o in intake["owners"]],
            [("PAT_target", "target"), ("PAT_meta_process", "metaskills"),
             ("the boundary handling guidance", "label")],
        )
        write_text((out / "controller" / "intake.json"), "{}\n")
        with self.assertRaisesRegex(crq.CandidateQualificationError, "intake"):
            crq.freeze_assessment(out)

    def test_monitoring_candidate_is_accepted(self) -> None:
        _out, run = self.prepare("SE_MEM_0008")
        self.assertEqual(run["state"], "prepared")

    def test_refusals_leave_nothing_behind(self) -> None:
        cases = {
            "SE_MEM_0099": "does not exist",
            "SE_MEM_0002": "not card_candidate",
            "SE_MEM_0003": "resolved",
            "SE_MEM_0004": "cites no evidence",
            "SE_MEM_0005": "not a card in software-engineering or metaskills",
            "SE_MEM_0006": "not a card in software-engineering or metaskills",
            "SE_MEM_0007": "names no likely owner that is a card in software-engineering",
        }
        for entry_id, message in cases.items():
            with self.subTest(entry=entry_id):
                with self.assertRaisesRegex(crq.CandidateQualificationError, message):
                    self.prepare(entry_id)
                self.assertFalse(self.workspace.exists() and any(self.workspace.iterdir()))

    def test_invalid_or_quarantined_evidence_fails_memory_validation(self) -> None:
        for cited, reason in (("SE_EV_0003", "invalid event"), ("SE_EV_0004", "quarantined event"),
                              ("SE_EV_0005", "evidence correction"), ("SE_EV_0404", "unknown event")):
            with self.subTest(cited=cited):
                self.write_memory([entry("SE_MEM_0001", evidence_events=["SE_EV_0001", cited])], EVENTS)
                with self.assertRaisesRegex(crq.CandidateQualificationError, f"memory.py validate.*{reason}"):
                    self.prepare()

    def test_domain_mismatch_and_missing_store_fail(self) -> None:
        store = self.memory / DOMAIN / "skill_memory.yaml"
        data = yaml.safe_load(store.read_text(encoding="utf-8"))
        write_text(store, yaml.safe_dump(dict(data, skillset="art"), sort_keys=False))
        with self.assertRaisesRegex(crq.CandidateQualificationError, "does not match directory"):
            self.prepare()
        with self.assertRaisesRegex(crq.CandidateQualificationError, "no Skillset Memory store"):
            crq.prepare(domain="art", memory_entry_id="SE_MEM_0001",
                        out=self.base / "workspace" / "candidate-qualification" / "art" / "ART_CRQ_0001",
                        library_root=self.library, memory_root=self.memory)

    def test_run_location_is_checked(self) -> None:
        for out, message in (
            (self.base / "elsewhere" / "SE_CRQ_0001", "candidate-qualification"),
            (self.workspace / "crq-1", "run id"),
            (self.library / "candidate-qualification" / DOMAIN / "SE_CRQ_0001", "inside"),
        ):
            with self.subTest(out=out):
                with self.assertRaisesRegex(crq.CandidateQualificationError, message):
                    crq.prepare(domain=DOMAIN, memory_entry_id="SE_MEM_0001", out=out,
                                library_root=self.library, memory_root=self.memory)
        self.prepare()
        with self.assertRaisesRegex(crq.CandidateQualificationError, "overwrite"):
            self.prepare()

    def test_next_run_id_scans_only_this_domain_folder(self) -> None:
        self.assertEqual(crq.run_id_prefix(DOMAIN, "SE_MEM_0042"), "SE")
        self.assertEqual(crq.run_id_prefix("game-design", "custom"), "GAME_DESIGN")
        self.assertEqual(crq.next_run_id(self.workspace, "SE"), "SE_CRQ_0001")
        for name in ("SE_CRQ_0001", "SE_CRQ_0007", "ART_CRQ_0009", ".SE_CRQ_0010.tmp"):
            (self.workspace / name).mkdir(parents=True)
        self.assertEqual(crq.next_run_id(self.workspace, "SE"), "SE_CRQ_0008")

    def test_scope_override_is_recorded(self) -> None:
        with self.assertRaisesRegex(crq.CandidateQualificationError, "override_reason"):
            self.prepare(max_changed_cards=4)
        _out, run = self.prepare(max_changed_cards=4, override_reason="one coupled family")
        self.assertEqual(run["scope_limits"]["override_reason"], "one coupled family")

    def test_drift_in_support_blocks_but_out_of_closure_change_does_not(self) -> None:
        out, _run = self.prepare()
        write_text((self.library / CARDS["PAT_far"][0]), card("PAT_far") + "edited\n")
        write_text((self.library / CARDS["PAT_unrelated"][0]), card("PAT_unrelated") + "x\n")
        self.assertEqual(crq.status_report(out)["baseline"]["status"], "clean")
        write_text((self.library / CARDS["PAT_prereq"][0]), card("PAT_prereq") + "edited\n")
        with self.assertRaises(crq.BaselineDriftError):
            crq.apply_transition(out, "freeze-assessment")

    def test_memory_tool_is_loaded_without_leaking_its_imports(self) -> None:
        evidence._TOOLS.clear()
        sys.modules.pop("paths", None)
        path_before = list(sys.path)
        memory = crq.load_pass_tool("memory")
        self.assertTrue(hasattr(memory, "validate_store"))
        self.assertEqual(sys.path, path_before)
        self.assertNotIn("paths", sys.modules)


def valid_assessment(run: dict, **overrides) -> dict:
    assessment = {
        "schema_version": 1,
        "run_id": run["run_id"],
        "memory_entry_id": run["memory_entry_id"],
        "candidate_disposition": "canon-candidate",
        "failure_layer": "knowledge",
        "primary_attribution": "skillcard",
        "owner_object_ids": ["PAT_target"],
        "proposed_object_actions": [{
            "action": "revise", "object_id": "PAT_target", "object_type": "pattern",
            "reason": "The reusable condition is underspecified for the demonstrated case.",
        }],
        "noncanon_failures_considered": [{
            "kind": "application", "disposition": "not-supported",
            "reason": "The exposed card lacks the condition, so following it could not help.",
        }],
        "rationale": "The exposed Pattern owns the decision and omits the boundary.",
        "unresolved_questions": [],
    }
    assessment.update(overrides)
    return assessment


class AssessmentTests(IntakeFixture):
    def setUp(self) -> None:
        super().setUp()
        self.out, self.run_record = self.prepare()

    def write(self, assessment: dict) -> None:
        crq.write_json_atomic(self.out / "controller" / "assessment.json", assessment)

    def assert_refused(self, assessment: dict, message: str) -> None:
        self.write(assessment)
        before = (self.out / "controller" / "run.json").read_bytes()
        with self.assertRaisesRegex(crq.CandidateQualificationError, message):
            crq.freeze_assessment(self.out)
        self.assertEqual((self.out / "controller" / "run.json").read_bytes(), before)
        self.assertFalse((self.out / "controller" / "assessment.freeze.json").exists())

    def with_action(self, **changes) -> dict:
        assessment = valid_assessment(self.run_record)
        assessment["proposed_object_actions"][0].update(changes)
        return assessment

    def test_valid_canon_candidate_freezes(self) -> None:
        self.write(valid_assessment(self.run_record))
        run = crq.freeze_assessment(self.out)
        self.assertEqual(run["state"], "assessment-frozen")
        self.assertEqual(sorted(run["freezes"]), ["assessment", "intake"])
        self.assertEqual(crq.status_report(self.out)["assessment"], "frozen")

    def test_frozen_assessment_cannot_be_edited_or_refrozen(self) -> None:
        self.write(valid_assessment(self.run_record))
        crq.freeze_assessment(self.out)
        with self.assertRaisesRegex(crq.CandidateQualificationError, "requires state"):
            crq.freeze_assessment(self.out)
        self.write(valid_assessment(self.run_record, rationale="changed after freezing"))
        with self.assertRaisesRegex(crq.CandidateQualificationError, "changed after it was frozen"):
            crq.apply_transition(self.out, "freeze-plan")

    def test_blank_template_is_refused(self) -> None:
        with self.assertRaisesRegex(crq.CandidateQualificationError, "candidate_disposition"):
            crq.freeze_assessment(self.out)
        self.assertEqual(crq.load_run(self.out)[1]["state"], "prepared")

    def test_noncanon_dispositions_freeze_for_the_record(self) -> None:
        # Fixture C: an application lapse routes away from canon.
        for number, disposition in enumerate(crq.CANDIDATE_DISPOSITIONS[1:], start=2):
            with self.subTest(disposition=disposition):
                out, run = self.prepare(run_id=f"SE_CRQ_{number:04d}")
                self.out = out
                self.write(valid_assessment(
                    run, candidate_disposition=disposition, failure_layer="application",
                    primary_attribution="application", proposed_object_actions=[],
                    unresolved_questions=[{"question": "Was the card read?", "decides_ownership": True}],
                ))
                self.assertEqual(crq.freeze_assessment(out)["state"], "assessment-frozen")

    def test_noncanon_disposition_may_not_propose_actions(self) -> None:
        self.assert_refused(valid_assessment(self.run_record, candidate_disposition="memory-only"),
                            "only a canon-candidate may propose")

    def test_canon_candidate_requires_an_action(self) -> None:
        self.assert_refused(valid_assessment(self.run_record, proposed_object_actions=[]),
                            "at least one object action")

    def test_canon_candidate_requires_a_canon_failure_layer_and_skillcard(self) -> None:
        for layer in ("retrieval", "application", "continuity", "reference", "tool", "interface"):
            with self.subTest(layer=layer):
                self.assert_refused(valid_assessment(self.run_record, failure_layer=layer),
                                    "cannot justify a card change")
        self.assert_refused(valid_assessment(self.run_record, failure_layer="bogus"), "failure_layer")
        self.assert_refused(valid_assessment(self.run_record, primary_attribution="fixture"),
                            "attributed to skillcard")

    def test_ownership_questions_and_unresolved_causes_block_canon(self) -> None:
        self.assert_refused(valid_assessment(self.run_record, unresolved_questions=[
            {"question": "Is the AP or the Pattern the owner?", "decides_ownership": True}]),
            "decides ownership")
        self.assert_refused(valid_assessment(self.run_record, noncanon_failures_considered=[
            {"kind": "retrieval", "disposition": "unresolved", "reason": "unclear whether read"}]),
            "unresolved")
        self.assert_refused(valid_assessment(self.run_record, noncanon_failures_considered=[]),
                            "non-canon causes it considered")
        self.write(valid_assessment(self.run_record, unresolved_questions=[
            {"question": "Does a Variant read better than a rule change?", "decides_ownership": False}]))
        self.assertEqual(crq.freeze_assessment(self.out)["state"], "assessment-frozen")

    def test_invalid_action_types_are_rejected(self) -> None:
        for action in ("delete", "rename", "move", "modify"):
            with self.subTest(action=action):
                self.assert_refused(self.with_action(action=action), "never delete, rename or move")

    def test_owner_must_exist_in_the_baseline(self) -> None:
        self.assert_refused(valid_assessment(self.run_record, owner_object_ids=["PAT_target", "PAT_far"]),
                            "PAT_far is not a card in the frozen baseline")
        self.assert_refused(self.with_action(object_id="PAT_unrelated"), "not in the frozen baseline")

    def test_metaskills_card_cannot_be_revised(self) -> None:
        assessment = valid_assessment(self.run_record, owner_object_ids=["PAT_meta_process"])
        assessment["proposed_object_actions"][0]["object_id"] = "PAT_meta_process"
        self.write(assessment)
        with self.assertRaisesRegex(crq.CandidateQualificationError, "modifies only software-engineering"):
            crq.freeze_assessment(self.out)

    def test_redirect_to_a_support_card_still_needs_exposure(self) -> None:
        assessment = valid_assessment(self.run_record, owner_object_ids=["PAT_foundation"])
        assessment["proposed_object_actions"][0]["object_id"] = "PAT_foundation"
        self.write(assessment)
        with self.assertRaisesRegex(crq.CandidateQualificationError, "was not exposed"):
            crq.freeze_assessment(self.out)

    def test_exposure_check_applies_only_when_evidence_records_it(self) -> None:
        out, run = self.prepare("SE_MEM_0008", run_id="SE_CRQ_0002")
        self.out = out
        assessment = valid_assessment(run, owner_object_ids=["PAT_foundation"])
        assessment["proposed_object_actions"][0]["object_id"] = "PAT_foundation"
        self.write(assessment)
        self.assertEqual(crq.freeze_assessment(out)["state"], "assessment-frozen")

    def test_action_type_must_match_the_card(self) -> None:
        self.assert_refused(self.with_action(object_type="ap"), "ap ids start with AP_")
        self.assert_refused(self.with_action(object_type="drill", object_id="DRILL_x"), "not in the frozen baseline")

    def test_revised_card_must_be_an_owner(self) -> None:
        self.assert_refused(valid_assessment(self.run_record, owner_object_ids=["PAT_prereq"]),
                            "a revised card must be listed in owner_object_ids")

    def test_routing_against_the_layer_needs_a_reason(self) -> None:
        orchestration = valid_assessment(self.run_record, failure_layer="orchestration")
        self.assert_refused(orchestration, "orchestration defect normally belongs to a ap")
        orchestration["proposed_object_actions"][0]["routing_reason"] = (
            "The Pattern itself sequences the check and is defective."
        )
        self.write(orchestration)
        self.assertEqual(crq.freeze_assessment(self.out)["state"], "assessment-frozen")

    def test_knowledge_defect_routed_to_an_ap_needs_a_reason(self) -> None:
        assessment = valid_assessment(self.run_record, owner_object_ids=["PAT_target"])
        assessment["proposed_object_actions"] = [{
            "action": "create", "object_id": "AP_new_flow", "object_type": "ap",
            "relative_path": f"{CORE}/AP_new_flow.md", "reason": "Compose the checks.",
        }]
        self.assert_refused(assessment, "knowledge defect normally belongs to a pattern")

    def test_create_action_is_bounded_to_a_new_card_in_the_domain(self) -> None:
        def create(**changes) -> dict:
            action = {
                "action": "create", "object_id": "PAT_new_boundary", "object_type": "pattern",
                "relative_path": f"{CORE}/PAT_new_boundary.md", "reason": "A distinct decision.",
            }
            action.update(changes)
            return valid_assessment(self.run_record, proposed_object_actions=[
                valid_assessment(self.run_record)["proposed_object_actions"][0], action])

        for changes, message in (
            ({"relative_path": "metaskills/process/PAT_new_boundary.md"}, "module folder"),
            ({"relative_path": f"{CORE}/PAT_other.md"}, "named PAT_new_boundary.md"),
            ({"relative_path": "../PAT_new_boundary.md"}, "bounded"),
            ({"object_id": "PAT_far", "relative_path": f"{CORE}/PAT_far.md"}, "already exists"),
            ({"object_id": "PAT_unrelated", "relative_path": f"{CORE}/x/PAT_unrelated.md"}, "already exists"),
        ):
            with self.subTest(changes=changes):
                self.assert_refused(create(**changes), message)
        self.write(create())
        self.assertEqual(crq.freeze_assessment(self.out)["state"], "assessment-frozen")

    def test_scope_ceilings_are_enforced(self) -> None:
        out, run = self.prepare(run_id="SE_CRQ_0002", max_new_cards=0)
        self.out = out
        assessment = valid_assessment(run)
        assessment["proposed_object_actions"].append({
            "action": "create", "object_id": "PAT_new_boundary", "object_type": "pattern",
            "relative_path": f"{CORE}/PAT_new_boundary.md", "reason": "A distinct decision.",
        })
        self.assert_refused(assessment, "exceed max_new_cards 0")
        out, run = self.prepare(run_id="SE_CRQ_0003", max_changed_cards=0)
        self.out = out
        self.assert_refused(valid_assessment(run), "exceed max_changed_cards 0")

    def test_identity_and_shape_are_checked(self) -> None:
        self.assert_refused(valid_assessment(self.run_record, run_id="SE_CRQ_0099"), "different run")
        self.assert_refused(valid_assessment(self.run_record, memory_entry_id="SE_MEM_0002"),
                            "different memory entry")
        self.assert_refused(dict(valid_assessment(self.run_record), score=0.9), "unknown assessment key")
        self.assert_refused(self.with_action(reason=" "), "reason must be non-empty")
        self.assert_refused(self.with_action(relative_path=CARDS["PAT_target"][0]), "path from the baseline")
        duplicated = valid_assessment(self.run_record)
        duplicated["proposed_object_actions"] *= 2
        self.assert_refused(duplicated, "more than one action")

    def test_validate_assessment_reports_every_problem_at_once(self) -> None:
        errors = crq.validate_assessment(
            {}, run=self.run_record, baseline={}, exposed=None,
            failure_layers={"knowledge"}, library_root=self.library,
        )
        self.assertGreater(len(errors), 4)

    def test_brief_carries_routing_guidance_and_the_candidate(self) -> None:
        brief = (self.out / "README.md").read_text(encoding="utf-8")
        for text in ("knowledge: a missing or wrong reusable decision belongs to a Pattern",
                     "orchestration: a missing or wrong goal-directed flow belongs to an AP",
                     "never justify a card change", "SE_EV_0001", "Do not", "library/",
                     "PAT_meta_process", "never modified by this run"):
            self.assertIn(text, brief)


class CommandLineTests(IntakeFixture):
    def cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(CONTROLLER), *args],
            text=True, encoding="utf-8", capture_output=True,
        )

    def test_prepare_and_freeze_assessment_commands(self) -> None:
        out = self.workspace / "SE_CRQ_0001"
        result = self.cli("prepare", "--domain", DOMAIN, "--memory-entry", "SE_MEM_0001",
                          "--out", str(out), "--library", str(self.library),
                          "--memory-root", str(self.memory))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PREPARED: SE_CRQ_0001", result.stdout)
        self.assertIn("1 target", result.stdout)
        failed = self.cli("freeze-assessment", "--run", str(out))
        self.assertEqual(failed.returncode, 2)
        self.assertIn("assessment cannot be frozen", failed.stderr)
        run = crq.load_run(out)[1]
        crq.write_json_atomic(out / "controller" / "assessment.json", valid_assessment(run))
        result = self.cli("freeze-assessment", "--run", str(out))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("ASSESSMENT FROZEN", result.stdout)

    def test_prepare_refusal_exits_cleanly(self) -> None:
        result = self.cli("prepare", "--domain", DOMAIN, "--memory-entry", "SE_MEM_0003",
                          "--out", str(self.workspace / "SE_CRQ_0001"),
                          "--library", str(self.library), "--memory-root", str(self.memory))
        self.assertEqual(result.returncode, 2)
        self.assertIn("resolved", result.stderr)


if __name__ == "__main__":
    unittest.main()
