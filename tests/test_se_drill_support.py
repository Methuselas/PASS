"""Contracts for Software Engineering Drill administration support."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
LIBRARY = ROOT / "library"
INVENTORY = ROOT / "PASS/tools/drill_inventory.py"
FIXTURES = ROOT / "tests/fixtures/software_engineering_drills"
PILOT = FIXTURES / "cpp/templatized-base-name-access"
PROFILE = ROOT / "PASS/runtime/profiles/software-engineering.yaml"
RECIPE = ROOT / "workspace/release-recipes/SkillForge_Software_Engineering.yaml"
FIELD_TESTS = ROOT / "PASS/docs/SOFTWARE_CARD_FIELD_TESTS.md"
FIELD_TEST_CONTEXT = ROOT / "PASS/templates/SOFTWARE_FIELD_TEST_CONTEXT_TEMPLATE.md"


class DrillInventoryTests(unittest.TestCase):
    def run_inventory(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(INVENTORY),
                "--package", "software-engineering",
                "--library", str(LIBRARY),
                *args,
            ],
            text=True,
            capture_output=True,
            cwd=ROOT,
        )

    def test_inventory_covers_every_software_engineering_drill(self) -> None:
        result = self.run_inventory("--format", "json", "--check")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        cards = sorted((LIBRARY / "software-engineering").rglob("DRILL_*.md"))
        self.assertEqual(len(payload), len(cards))
        self.assertEqual({item["object_id"] for item in payload}, {path.stem for path in cards})
        self.assertEqual(
            {item["module"] for item in payload},
            {"software-engineering/core", "software-engineering/languages/cpp"},
        )

    def test_every_drill_has_one_known_administration_class(self) -> None:
        result = self.run_inventory("--format", "json")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        known = {
            "expected-compile-failure",
            "compile-or-build",
            "runtime-or-test",
            "code-production",
            "analysis-or-review",
        }
        self.assertTrue(payload)
        self.assertTrue(all(item["administration_class"] in known for item in payload))


class CppPilotPacketTests(unittest.TestCase):
    def test_taker_packet_does_not_expose_the_grader(self) -> None:
        taker_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted((PILOT / "taker").rglob("*"))
            if path.is_file()
        )
        self.assertNotIn("## Success Check", taker_text)
        self.assertFalse((PILOT / "taker/grader").exists())
        self.assertTrue((PILOT / "grader/SUCCESS_CHECK.md").is_file())

    def test_reference_answers_cover_the_declared_compilation_cases(self) -> None:
        reference = PILOT / "grader/reference"
        expected = {
            "this_prefix.cpp",
            "using_declaration.cpp",
            "explicit_qualification.cpp",
            "missing_specialization.cpp",
            "RANKING.md",
        }
        self.assertEqual({path.name for path in reference.iterdir()}, expected)
        packet = (PILOT / "PACKET.md").read_text(encoding="utf-8")
        self.assertIn("Maximum concurrent sub-agents: 1", packet)
        self.assertIn("Automatic repetitions: 0", packet)


class SoftwareEngineeringReleaseProfileTests(unittest.TestCase):
    def test_release_uses_the_software_engineering_profile(self) -> None:
        recipe = yaml.safe_load(RECIPE.read_text(encoding="utf-8"))
        self.assertEqual(recipe["runtime_profile"], "software-engineering")
        profile = yaml.safe_load(PROFILE.read_text(encoding="utf-8"))
        instructions = "\n".join(profile.get("consumer_instructions") or [])
        self.assertIn("one primary card, one coherent source slice", instructions)
        self.assertIn("ranking catalog", instructions)
        self.assertIn("at most two concurrent sub-agents", instructions)
        self.assertIn("Confirmed contamination", instructions)
        self.assertIn("never triggers an automatic retry", instructions)

    def test_field_test_protocol_distinguishes_source_roles_and_stops(self) -> None:
        protocol = FIELD_TESTS.read_text(encoding="utf-8")
        self.assertIn("Neutral external corpus", protocol)
        self.assertIn("Project-relevant reference", protocol)
        self.assertIn("Interest-led investigation", protocol)
        self.assertIn("Ready for a project trial", protocol)
        self.assertIn("one reviewer and no automatic repetitions", protocol)
        self.assertIn("The user does not need a catalog", protocol)
        self.assertIn("ask one plain-language question", protocol)
        self.assertIn("Qualification is not ordinary use", protocol)
        self.assertIn("evidence **in that language only**", protocol)
        self.assertIn("Finding a human defect", protocol)
        self.assertIn("Keep exactly one canonical core card", protocol)
        self.assertIn("Do not copy the core library", protocol)
        self.assertNotIn("AROS", protocol)
        self.assertNotIn("game repositories", protocol)
        context = FIELD_TEST_CONTEXT.read_text(encoding="utf-8")
        self.assertIn("model-maintained working file", context)
        self.assertIn("Neutral external corpus", context)
        self.assertIn("Project-relevant reference", context)
        self.assertIn("Interest-led investigation", context)


if __name__ == "__main__":
    unittest.main()
