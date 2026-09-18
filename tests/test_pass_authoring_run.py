import copy
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "PASS" / "runtime" / "pass_authoring_run.py"
spec = importlib.util.spec_from_file_location("pass_authoring_run", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)


class PreflightGateTests(unittest.TestCase):
    def base_record(self):
        return {
            "schema_version": 1,
            "phase": "preflight",
            "title": "Fixture Source",
            "author": "Fixture Author",
            "domain": "writing",
            "extent": "10 pages",
            "text_quality": "readable",
            "subject": "Write a runnable introductory adventure.",
            "mode": "unit ingestion",
            "units": [
                {
                    "unit_id": "u01",
                    "material": "Introductory adventure instruction",
                    "locator": "pp. 1-10",
                    "overlap_object_ids": [
                        "AP_write_introductory_adventure_module_as_runnable_apprenticeship"
                    ],
                    "card_potential": "medium",
                }
            ],
            "no_extract": [],
        }

    def test_valid_record_resolves_live_card(self):
        record = mod.parse_preflight(self.base_record())
        cards = mod.validate_against_library(record, ROOT)
        self.assertIn(
            "AP_write_introductory_adventure_module_as_runnable_apprenticeship", cards
        )
        rendered = mod.render_preflight(record, cards)
        self.assertIn("Write an Introductory Adventure Module as a Runnable Apprenticeship", rendered)
        self.assertIn("| **U01** |", rendered)

    def test_unknown_overlap_fails(self):
        data = self.base_record()
        data["units"][0]["overlap_object_ids"] = ["PAT_does_not_exist"]
        record = mod.parse_preflight(data)
        with self.assertRaises(mod.PreflightError):
            mod.validate_against_library(record, ROOT)

    def test_invalid_potential_fails(self):
        data = self.base_record()
        data["units"][0]["card_potential"] = "maybe"
        with self.assertRaises(mod.PreflightError):
            mod.parse_preflight(data)

    def test_noncontiguous_unit_ids_fail(self):
        data = self.base_record()
        data["units"].append(copy.deepcopy(data["units"][0]))
        data["units"][1]["unit_id"] = "u03"
        with self.assertRaises(mod.PreflightError):
            mod.parse_preflight(data)

    def test_missing_required_field_fails(self):
        data = self.base_record()
        del data["units"][0]["overlap_object_ids"]
        with self.assertRaises(mod.PreflightError):
            mod.parse_preflight(data)

    def test_unexpected_field_fails(self):
        data = self.base_record()
        data["units"][0]["model_commentary"] = "looks good"
        with self.assertRaises(mod.PreflightError):
            mod.parse_preflight(data)

    def test_empty_overlap_is_valid(self):
        data = self.base_record()
        data["units"][0]["overlap_object_ids"] = []
        record = mod.parse_preflight(data)
        cards = mod.validate_against_library(record, ROOT)
        self.assertIn("None identified", mod.render_preflight(record, cards))

    def test_schema_version_requires_integer(self):
        for value in (True, 1.0, "1", 2):
            with self.subTest(value=value):
                data = self.base_record()
                data["schema_version"] = value
                with self.assertRaises(mod.PreflightError):
                    mod.parse_preflight(data)

    def test_domain_cannot_escape_active_package(self):
        for domain in ("../writing", "writing/..", "D:/Repos/PASS/library/writing"):
            with self.subTest(domain=domain):
                data = self.base_record()
                data["domain"] = domain
                with self.assertRaises(mod.PreflightError):
                    mod.parse_preflight(data)
                with self.assertRaises(mod.PreflightError):
                    mod.load_domain_cards(ROOT, domain)

    def test_foreign_domain_overlap_fails(self):
        data = self.base_record()
        data["domain"] = "art"
        with self.assertRaises(mod.PreflightError):
            mod.validate_against_library(mod.parse_preflight(data), ROOT)

    def test_invalid_card_yaml_reports_gate_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            domain = root / "library/writing"
            domain.mkdir(parents=True)
            (domain / "PAT_invalid.md").write_text(
                "---\nobject_id: [\n---\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(mod.PreflightError, "invalid YAML"):
                mod.load_domain_cards(root, "writing")


if __name__ == "__main__":
    unittest.main()
