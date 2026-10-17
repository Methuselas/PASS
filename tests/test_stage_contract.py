"""Stage Contract v1: cross-model conformance, host ownership and fail-close.

    free-form model cognition
        -> closed stage output contract
        -> deterministic host validation/rendering

These tests fix the boundary, not the pedagogy. Semantic content is allowed to
differ between models; structure, schema, enums and the files the host writes are
not.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "PASS"))
from runtime import pass_authoring_run as preflight          # noqa: E402
from runtime import pass_authoring_workflow as workflow      # noqa: E402
from runtime import pass_source_prep                         # noqa: E402
from runtime import pass_source_runner as runner             # noqa: E402
from runtime import stage_contract as contract               # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_pass_authoring_workflow import card, card_payload   # noqa: E402


# --------------------------------------------------------------------- rendering


class CardRenderingTests(unittest.TestCase):
    """The host renders every structural character; the model supplies meaning."""

    def body(self, object_type):
        bodies = {
            "pattern": {
                "pattern_rule": {"if": "the decision moment arrives",
                                 "then": "take the specific action",
                                 "else": "keep the working state"},
                "do": [{"text": "One concrete move."},
                       {"text": "A move with detail.", "children": ["A nested qualifier."]}],
                "dont": [{"text": "One concrete anti-move."}],
                "checklist": [{"text": "Was the effect observable?"}],
                "notes": [{"type": "paragraph", "text": "Why this boundary holds."}],
            },
            "ap": {
                "objective": "Transform the input into the finished artifact.",
                "steps_flow": [{"text": "**Open.** Read the whole thing."},
                               {"text": "**Act.** Do the work.", "children": ["Check the seam."]}],
                "notes": [{"type": "paragraph", "text": "Generalized from the worked case."}],
            },
            "drill": {
                "practice_task": "Do the bounded thing once.",
                "target_skill": "The judgment being exercised.",
                "setup": "No special setup required.",
                "instructions": [{"text": "First do this."}, {"text": "Then do that."}],
                "success_check": [{"text": "The observable result is present."}],
                "common_failures": [{"text": "Substituting description for production."}],
                "notes": [{"type": "paragraph", "text": "What this actually drills."}],
            },
        }
        return bodies[object_type]

    def test_rendering_matches_the_canonical_body_contract(self):
        """Headings, order and labels equal what validate.py requires."""
        sys.path.insert(0, str(ROOT / "PASS/tools"))
        import validate          # the authority on canonical body headings
        for object_type in contract.OBJECT_TYPES:
            with self.subTest(object_type=object_type):
                rendered = contract.render_card_body(object_type, self.body(object_type))
                headings = [line[3:] for line in rendered.split("\n") if line.startswith("## ")]
                self.assertEqual(headings, validate.HEADINGS[object_type])
                self.assertEqual(headings, [h for h, _ in contract.CARD_BODY[object_type]])

    def test_pattern_rule_labels_and_list_markers_are_host_owned(self):
        rendered = contract.render_card_body("pattern", self.body("pattern"))
        self.assertIn("**IF** the decision moment arrives", rendered)
        self.assertIn("**THEN** take the specific action", rendered)
        self.assertIn("**ELSE** keep the working state", rendered)
        self.assertIn("\n- One concrete move.", rendered)
        self.assertIn("\n  - A nested qualifier.", rendered)

    def test_steps_are_numbered_by_the_host_not_the_model(self):
        rendered = contract.render_card_body("ap", self.body("ap"))
        self.assertIn("\n1. **Open.**", rendered)
        self.assertIn("\n2. **Act.**", rendered)

    def test_an_optional_else_is_simply_absent(self):
        body = copy.deepcopy(self.body("pattern"))
        del body["pattern_rule"]["else"]
        out = contract.Collector()
        validated = contract.validate_card_body("pattern", body, "body", out)
        self.assertEqual(out.failures, [])
        self.assertNotIn("**ELSE**", contract.render_card_body("pattern", validated))

    def test_equivalent_payloads_render_identically_across_models(self):
        """Same meaning, different emission order and whitespace: same bytes out."""
        base = self.body("pattern")
        gpt_style = copy.deepcopy(base)
        mimo_style = {key: gpt_style[key] for key in reversed(list(gpt_style))}
        mimo_style["do"] = [
            {"text": "  One concrete move.  "},
            {"text": "A move with detail.", "children": ["  A nested qualifier."]},
        ]
        small_local = copy.deepcopy(base)
        small_local["do"] = ["One concrete move.",
                             {"text": "A move with detail.", "children": ["A nested qualifier."]}]
        rendered = set()
        for payload in (gpt_style, mimo_style, small_local):
            out = contract.Collector()
            validated = contract.validate_card_body("pattern", payload, "body", out)
            self.assertEqual([f.as_dict() for f in out.failures], [])
            rendered.add(contract.render_card_body("pattern", validated))
        self.assertEqual(len(rendered), 1, "equivalent payloads must render byte-identically")

    def test_a_wrong_object_type_body_is_refused(self):
        out = contract.Collector()
        contract.validate_card_body("drill", self.body("pattern"), "body", out)
        codes = {failure.code for failure in out.failures}
        self.assertIn("missing_field", codes)
        self.assertIn("unknown_field", codes)


# ------------------------------------------------------------------ path ownership


class PathOwnershipTests(unittest.TestCase):
    def test_path_is_derived_from_object_id_and_library_path(self):
        self.assertEqual(
            contract.card_path("writing", ["writing", "poetry", "sound"], "PAT_hear_the_line"),
            "library/writing/poetry/sound/PAT_hear_the_line.md",
        )

    def test_library_path_must_start_with_the_domain(self):
        with self.assertRaises(ValueError):
            contract.card_path("writing", ["art", "poetry"], "PAT_x")

    def test_the_card_contract_has_no_filename_or_path_field(self):
        """Decision 2/4: a model cannot name a file even if it tries."""
        properties = contract.card_json_schema()["properties"]
        for forbidden in ("filename", "path", "staged_path", "file", "target"):
            self.assertNotIn(forbidden, properties)
        for stage in contract.STAGES:
            payload = contract.json_schema(stage, ("x",))["properties"]["payload"]["properties"]
            for forbidden in ("filename", "path", "staged_path", "changes", "reviewed_sha256",
                              "schema_version", "unit_id", "run_id", "stage", "mode"):
                self.assertNotIn(forbidden, payload, f"{stage} must not accept {forbidden}")


# ------------------------------------------------- live run: ownership and failure


class StageTransactionTests(unittest.TestCase):
    """Behaviour against a real run on a real filesystem."""

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.repo = Path(self.temporary.name).resolve()
        shutil.copytree(ROOT / "PASS/tools", self.repo / "PASS/tools",
                        ignore=shutil.ignore_patterns("__pycache__"))
        for name in workflow.required_documents(ROOT):
            target = self.repo / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("Fixture canonical instructions\n", encoding="utf-8")
        for module in ("writing/craft", "metaskills"):
            path = self.repo / "library" / module / "MODULE.yaml"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"name: {module}\nrequires: []\n", encoding="utf-8")
        self.live = self.repo / "library/writing/craft/PAT_review_revision_effect.md"
        card(self.live, self.live.stem)
        (self.repo / "workspace/release-recipes").mkdir(parents=True)
        (self.repo / "workspace/release-recipes/SkillForge_Writing.yaml").write_text(
            "modules: [writing/craft]\n", encoding="utf-8")
        self.source = self.repo / "Original Book.txt"
        self.source.write_text("Original user input remains untouched.\n", encoding="utf-8")
        self.root = workflow.start(self.repo, self.source, "writing")
        self.run = workflow.Run(self.repo, self.root)

    def reach_pass1(self):
        self.run.submit("load", self.run.template())
        pass_source_prep.prepare(self.run)
        pass_source_prep.finalize(self.run)
        record = self.run.template()
        record["payload"].update(
            title="Original Book", author="Fixture Author", extent="20 pages",
            text_quality="readable", subject="Revise prose for an observable reader effect.",
            no_extract=[],
            units=[dict(unit_id="u01", material="Instructional unit 1", locator="chapter 1",
                        source_pages=None, printed_pages=None,
                        overlap_object_ids=[self.live.stem], card_potential="medium")])
        self.run.submit("preflight", record)
        packet = self.run.present()
        import hashlib
        self.run.accept_preflight(dict(
            schema_version=1,
            presentation_sha256=hashlib.sha256(packet.encode("utf-8")).hexdigest(),
            subject=self.run.state["plan"]["subject"], basis="user confirmation",
            reason="The practitioner confirmed the presented subject and unit plan."))
        self.assertEqual(self.run.state["phase"], "pass1")

    def snapshot(self):
        return {path.relative_to(self.root).as_posix(): path.read_bytes()
                for path in sorted(self.root.rglob("*")) if path.is_file()}

    # ------------------------------------------------------------- ownership

    def test_host_writes_the_card_at_a_path_the_model_never_named(self):
        self.reach_pass1()
        drafted = card_payload("PAT_choose_the_observable_effect")
        record = self.run.template()
        record["payload"].update(full_read=True, cards=[drafted])
        self.run.submit("pass1", record)
        staged = self.root / "drafts/craft/PAT_choose_the_observable_effect.md"
        self.assertTrue(staged.is_file(), "the host derived and wrote the path")
        self.assertEqual(self.run.state["pass1"]["working_drafts"],
                         ["drafts/craft/PAT_choose_the_observable_effect.md"])
        front = yaml.safe_load(staged.read_text(encoding="utf-8").split("---\n")[1])
        self.assertEqual(front["object_id"], "PAT_choose_the_observable_effect")
        self.assertEqual(front["library_path"], ["writing", "craft"])

    def test_a_model_supplied_filename_is_refused_as_an_unknown_field(self):
        self.reach_pass1()
        drafted = dict(card_payload("PAT_x_y"), filename="drafts/anywhere/PAT_x_y.md")
        record = self.run.template()
        record["payload"].update(full_read=True, cards=[drafted])
        with self.assertRaisesRegex(workflow.RunError, "unknown_field"):
            self.run.submit("pass1", record)

    def test_a_card_outside_the_authorized_domain_is_refused(self):
        self.reach_pass1()
        drafted = card_payload("PAT_x_y", placement=("art", "foundations"))
        record = self.run.template()
        record["payload"].update(full_read=True, cards=[drafted])
        with self.assertRaisesRegex(workflow.RunError, "illegal_enum"):
            self.run.submit("pass1", record)

    # ------------------------------------------------------- nothing is written

    def test_an_invalid_response_writes_nothing_and_does_not_advance(self):
        self.reach_pass1()
        before_files, before_phase = self.snapshot(), self.run.state["phase"]
        record = self.run.template()
        record["payload"].update(full_read=True,
                                 cards=[dict(card_payload("PAT_ok"), object_id="NOPE")])
        with self.assertRaises(workflow.RunError):
            self.run.submit("pass1", record)
        after = self.snapshot()
        # Only the structured rejection is added; no card, no state change.
        self.assertEqual(set(after) - set(before_files), {workflow.STAGE_REJECTION})
        for name, content in before_files.items():
            self.assertEqual(after[name], content, f"{name} must not change")
        self.assertEqual(self.run.state["phase"], before_phase)
        self.assertIsNone(self.run.state["pass1"])

    def test_a_stale_action_id_writes_nothing(self):
        self.reach_pass1()
        record = self.run.template()
        record["payload"].update(full_read=True, cards=[card_payload("PAT_stale_check")])
        record["action_id"] = "f" * 64
        before = self.snapshot()
        with self.assertRaisesRegex(workflow.RunError, "stale_action_id"):
            self.run.submit("pass1", record)
        self.assertFalse((self.root / "drafts/craft/PAT_stale_check.md").exists())
        self.assertEqual(set(self.snapshot()) - set(before), {workflow.STAGE_REJECTION})
        self.assertEqual(self.run.state["phase"], "pass1")

    # --------------------------------------------- one correction, then fail-close

    def malformed(self):
        record = self.run.template()
        record["payload"]["nonsense_field"] = True
        return record

    def test_first_malformed_response_produces_a_structured_rejection(self):
        self.reach_pass1()
        with self.assertRaises(workflow.RunError):
            self.run.submit("pass1", self.malformed())
        rejection = self.run.stage_rejection()
        self.assertEqual(rejection["stage"], "pass1")
        self.assertEqual(rejection["attempt"], 1)
        self.assertTrue(rejection["correction_allowed"])
        self.assertFalse(rejection["fail_closed"])
        self.assertEqual(rejection["action_id"], self.run.stage_action_id())
        codes = {failure["code"] for failure in rejection["failures"]}
        self.assertEqual(codes, {"unknown_field"})
        for failure in rejection["failures"]:
            self.assertIn("path", failure)
            self.assertIn("message", failure)
            self.assertIn(failure["code"], contract.FAILURE_CODES)

    def test_a_correction_after_one_rejection_is_accepted(self):
        self.reach_pass1()
        with self.assertRaises(workflow.RunError):
            self.run.submit("pass1", self.malformed())
        record = self.run.template()
        record["payload"]["full_read"] = True
        self.run.submit("pass1", record)
        self.assertEqual(self.run.state["phase"], "pass2")
        self.assertIsNone(self.run.stage_rejection(), "a clean response clears the rejection")

    def test_second_malformed_response_fails_closed(self):
        self.reach_pass1()
        action_id = self.run.stage_action_id()
        for attempt in (1, 2):
            with self.assertRaises(workflow.RunError):
                self.run.submit("pass1", self.malformed())
            self.assertEqual(self.run.stage_rejection()["attempt"], attempt)
        rejection = self.run.stage_rejection()
        self.assertTrue(rejection["fail_closed"])
        self.assertFalse(rejection["correction_allowed"])
        # Even a valid response is now refused for this action, and the last
        # completed boundary is preserved.
        record = self.run.template()
        record["payload"]["full_read"] = True
        with self.assertRaisesRegex(workflow.RunError, "FAIL-CLOSED"):
            self.run.submit("pass1", record)
        self.assertEqual(self.run.state["phase"], "pass1")
        self.assertEqual(self.run.stage_action_id(), action_id)

    def test_an_infrastructure_failure_does_not_consume_the_correction(self):
        self.reach_pass1()
        record = self.run.template()
        record["payload"]["full_read"] = True
        with patch.object(workflow.Run, "write_stage_cards",
                          side_effect=OSError("disk gone")):
            with self.assertRaises(OSError):
                self.run.submit("pass1", record)
        self.assertIsNone(self.run.stage_rejection(),
                          "an infrastructure error is not a contract failure")
        fresh = self.run.template()
        fresh["payload"]["full_read"] = True
        self.run.submit("pass1", fresh)
        self.assertEqual(self.run.state["phase"], "pass2")

    def test_a_semantic_failure_does_not_consume_the_correction(self):
        self.reach_pass1()
        # An honest false attestation is a semantic outcome, not malformed output.
        record = self.run.template()
        record["payload"]["full_read"] = False
        with self.assertRaisesRegex(workflow.RunError, "full read"):
            self.run.submit("pass1", record)
        self.assertIsNone(self.run.stage_rejection())
        # And a legitimate no-card result is accepted.
        clean = self.run.template()
        clean["payload"]["full_read"] = True
        self.run.submit("pass1", clean)
        self.assertEqual(self.run.state["phase"], "pass2")
        self.assertEqual(self.run.state["pass1"]["working_drafts"], [])

    def test_an_honest_false_semantic_check_is_not_a_contract_failure(self):
        self.reach_pass1()
        record = self.run.template()
        record["payload"]["full_read"] = True
        self.run.submit("pass1", record)
        second = self.run.template()
        second["payload"].update(full_reread=True, approval_required=False)
        second["payload"]["buckets"]["REINFORCE"] = [
            {"object_id": self.live.stem, "reason": "The existing owner covers the unit."}]
        self.run.submit("pass2", second)
        third = self.run.template()
        third["payload"].update(
            card_only_review=True,
            checks={name: name != "source_independence"
                    for name in workflow.SEMANTIC_CHECKS})
        with self.assertRaisesRegex(workflow.RunError, "semantic/identity defect"):
            self.run.submit("pass3", third)
        self.assertIsNone(self.run.stage_rejection())

    # ------------------------------------------------------------ automated mode

    def test_automated_mode_cannot_reissue_malformed_work_indefinitely(self):
        self.reach_pass1()
        runner.authorize(self.run, "User asked this one source to continue unattended.")
        issued = runner.drive(self.run)
        self.assertEqual(issued["outcome"], "host_action_required")
        for _ in range(2):
            with self.assertRaises(workflow.RunError):
                self.run.submit("pass1", self.malformed())
        blocked = runner.drive(self.run)
        self.assertEqual(blocked["outcome"], "blocked_human_required")
        self.assertIn("closed to further automatic correction", blocked["reason"])
        self.assertTrue(blocked["stage_rejection"]["fail_closed"])
        # Still blocked on a second call: no unbounded loop.
        self.assertEqual(runner.drive(self.run)["outcome"], "blocked_human_required")

    def test_both_modes_bind_a_response_with_the_same_token(self):
        self.reach_pass1()
        runner.authorize(self.run, "User asked this one source to continue unattended.")
        issued = runner.drive(self.run)["action"]
        self.assertEqual(issued["action_id"], self.run.stage_action_id())
        self.assertEqual(self.run.template()["action_id"], issued["action_id"])

    # ------------------------------------------------------- resume and recover

    def test_resume_and_recover_remain_valid_under_the_contract(self):
        self.reach_pass1()
        record = self.run.template()
        record["payload"].update(full_read=True, cards=[card_payload("PAT_resume_probe")])
        with self.run.locked():
            self.run.submit("pass1", record)
        staged = self.root / "drafts/craft/PAT_resume_probe.md"
        self.assertTrue(staged.is_file())
        result = workflow.resume(self.repo, self.root)
        self.assertEqual(result["outcome"], "resume")
        # Lose a staged card and drift the state, then recover it.
        staged.unlink()
        state = json.loads(self.run.state_path.read_text(encoding="utf-8"))
        state["stop_reached"] = not state["stop_reached"]
        workflow.atomic_write(self.run.state_path,
                              (json.dumps(state, indent=2) + "\n").encode("utf-8"))
        self.run.reload()
        self.assertIn("RECOVERED", self.run.recover())
        self.assertTrue(staged.is_file(), "the staged card came back from the checkpoint")

    # ------------------------------------- removals: schema and validator agree

    def removals_node(self):
        return contract.json_schema("pass2")["properties"]["payload"]["properties"]["removals"]

    def schema_accepts_removals(self, value):
        """Evaluate a removals list against the published PASS 2 schema node."""
        node = self.removals_node()
        if node.get("type") != "array":
            return False
        items = node.get("items") or {}
        for entry in value:
            if items.get("type") != "string":
                return False
            if not isinstance(entry, str) or not re.fullmatch(items.get("pattern", "$^"), entry):
                return False
        return True

    def runtime_verdict_on_removals(self, removals):
        """The contract layer's real verdict, through the live run's validator."""
        payload = copy.deepcopy(self.run.template()["payload"])
        payload["removals"] = removals
        try:
            translated = self.run.translate_stage_payload("pass2", payload)
        except contract.Rejected as rejected:
            return False, {failure.code for failure in rejected.failures}
        return True, translated["removals"]

    def test_pass2_removals_schema_and_validator_agree(self):
        """The published schema's item language is exactly what the runtime accepts.

        The schema is the contract's authority artifact; a schema-conforming
        model response must never be refused by the validator, and a refused
        shape must never be schema-conforming.
        """
        node = self.removals_node()
        self.assertEqual(node["type"], "array")
        self.assertEqual(node["items"]["type"], "string")
        self.assertEqual(node["items"]["pattern"], contract.OBJECT_ID_RE.pattern)

        self.reach_pass1()
        record = self.run.template()
        record["payload"].update(full_read=True, cards=[])
        self.run.submit("pass1", record)

        cases = [
            ([self.live.stem], True),                      # valid live object_id
            ([{"object_id": self.live.stem}], False),      # invalid type
            (["NOPE"], False),                             # invalid object_id shape
            ([], True),                                    # empty stays valid
        ]
        for removals, expected in cases:
            with self.subTest(removals=removals):
                schema_ok = self.schema_accepts_removals(removals)
                runtime_ok, detail = self.runtime_verdict_on_removals(removals)
                self.assertEqual(schema_ok, expected, "published schema verdict")
                self.assertEqual(runtime_ok, expected, f"runtime validator verdict: {detail}")
                self.assertEqual(schema_ok, runtime_ok, "schema and validator must agree")


# --------------------------------------------------- preflight schema independence


class PreflightSchemaIndependenceTests(unittest.TestCase):
    def test_preflight_schema_version_is_not_the_contract_version(self):
        self.assertNotEqual(preflight.SCHEMA_VERSION, contract.CONTRACT_VERSION)
        self.assertEqual(contract.CONTRACT_VERSION, 1)
        self.assertEqual(preflight.SCHEMA_VERSION, 3)
        # The stage payload never carries either number.
        payload = contract.json_schema("preflight")["properties"]["payload"]["properties"]
        self.assertNotIn("schema_version", payload)
        self.assertNotIn("contract_version", payload)

    def test_previously_accepted_preflight_documents_still_load(self):
        for schema_version in sorted(preflight.SUPPORTED_SCHEMA_VERSIONS):
            with self.subTest(schema_version=schema_version):
                plan = preflight.template_record("writing")
                plan.update(schema_version=schema_version, title="Legacy Source",
                            author="Legacy Author", extent="10 pages",
                            text_quality="clean", subject="Do the thing the body teaches.",
                            no_extract=[])
                unit = dict(plan["units"][0])
                unit["card_potential"] = "medium"
                if schema_version < 2:
                    unit.pop("source_pages", None)
                    unit.pop("printed_pages", None)
                if schema_version < 3:
                    plan.pop("language_policy", None)
                plan["units"] = [unit]
                record = preflight.parse_preflight(plan)
                self.assertEqual(record.schema_version, schema_version)
                self.assertEqual(
                    preflight.parse_preflight(preflight.serialize_preflight(record)), record)

    def test_contract_enums_do_not_drift_from_their_authority(self):
        self.assertEqual(set(contract.CARD_POTENTIAL), preflight.CARD_POTENTIALS)
        self.assertEqual(set(contract.BUCKETS), set(workflow.BUCKETS))
        self.assertEqual(set(contract.TAXONOMY), set(workflow.TAXONOMY))
        self.assertEqual(set(contract.MODERNIZATION_DISPOSITIONS),
                         workflow.MODERNIZATION_DISPOSITIONS)


# ------------------------------------------------------- cross-model conformance


class CrossModelConformanceTests(unittest.TestCase):
    """STRUCTURE / SCHEMA / ENUMS / FILES match; semantics may differ.

    The fixtures stand in for GPT, Codex, Claude, MiMo and a small local model
    responding to the same PASS 1 action. They disagree about what the unit
    teaches, which is allowed, and agree on everything the host owns.
    """

    def responses(self):
        return {
            "gpt": {"full_read": True, "secondary_subject_flags": [], "questions": [],
                    "cards": [card_payload("PAT_name_the_effect_first")]},
            "codex": {"full_read": True, "questions": [], "secondary_subject_flags": [],
                      "cards": [card_payload("PAT_name_the_effect_first",
                                             note="A different reading of the same unit.")]},
            "claude": {"full_read": True, "secondary_subject_flags": [],
                       "questions": [{"question_id": "scope",
                                      "question": "Which reading is authorized?"}],
                       "cards": [card_payload("PAT_name_the_effect_first")]},
            "mimo": {"cards": [card_payload("PAT_name_the_effect_first")],
                     "questions": [], "secondary_subject_flags": [], "full_read": True},
            "small_local": {"full_read": True, "secondary_subject_flags": [], "questions": [],
                            "cards": [dict(card_payload("PAT_name_the_effect_first"),
                                           body=card_payload("PAT_name_the_effect_first")["body"])]},
        }

    def test_structure_schema_enums_and_files_match_across_models(self):
        structures, files, enums = set(), set(), set()
        for model, payload in self.responses().items():
            with self.subTest(model=model):
                out = contract.Collector()
                fields = {spec.name for spec in contract.stage_fields("pass1")}
                required = {spec.name for spec in contract.stage_fields("pass1") if spec.required}
                contract._keys(payload, required, "payload", out, optional=fields - required)
                cards = [contract.validate_card(c, "writing", "payload.cards[0]", out)
                         for c in payload["cards"]]
                self.assertEqual([f.as_dict() for f in out.failures], [])
                structures.add(tuple(sorted(payload)))
                files.add(tuple(contract.card_path("writing", c["library_path"], c["object_id"])
                                for c in cards))
                enums.add(tuple(c["object_type"] for c in cards))
        self.assertEqual(len(structures), 1, "STRUCTURE must match across models")
        self.assertEqual(len(files), 1, "FILES must match across models")
        self.assertEqual(len(enums), 1, "ENUMS must match across models")

    def test_semantic_content_is_allowed_to_differ(self):
        notes = set()
        for payload in self.responses().values():
            body = payload["cards"][0]["body"]
            notes.add(body["notes"][0]["text"])
        self.assertGreater(len(notes), 1, "models may reach different semantic conclusions")


if __name__ == "__main__":
    unittest.main()
