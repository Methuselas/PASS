#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_PATH = ROOT / "PASS" / "runtime" / "pass_vfx.py"
SPEC = importlib.util.spec_from_file_location("pass_vfx", RUNTIME_PATH)
assert SPEC and SPEC.loader
pv = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pv)


class TestInventoryAndPlan(unittest.TestCase):
    def sample_inventory(self):
        return {
            "schema_version": 1,
            "engine_version": "5.3.2",
            "project_name": "TestProject",
            "system_asset": "/Game/VFX/NS_Test",
            "duration_seconds": 6.0,
            "emitters": [
                {"target_id": "smoke", "name": "Smoke", "enabled": True, "renderer_types": ["sprite"], "simulation_target": "GPU"},
                {"target_id": "flash", "name": "Flash", "enabled": False},
            ],
        }

    def test_capture_plan_contains_whole_system_and_enabled_emitters(self):
        inv = pv.parse_inventory(self.sample_inventory())
        plan = pv.capture_plan(inv)
        self.assertEqual([x["target_id"] for x in plan["targets"]], ["system", "smoke"])
        self.assertTrue(plan["temporal_sampling"]["preserve_every_sample"])

    def test_inventory_rejects_system_as_emitter_id(self):
        data = self.sample_inventory()
        data["emitters"][0]["target_id"] = "system"
        with self.assertRaises(pv.VFXRunError):
            pv.parse_inventory(data)


class TestStateMachine(unittest.TestCase):
    def test_start_and_capture_registration_advance_to_classification(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            (repo / "workspace").mkdir()
            inv = repo / "inventory.json"
            inv.write_text(json.dumps({
                "schema_version": 1,
                "engine_version": "5.3.2",
                "project_name": "TestProject",
                "system_asset": "/Game/VFX/NS_Test",
                "emitters": [{"target_id": "smoke", "name": "Smoke", "enabled": True}],
            }), encoding="utf-8")
            root = pv.start(repo, inv, "test-vfx")
            self.assertEqual(pv.load_run(root)["phase"], "capture")
            system_bundle = repo / "system.zip"; system_bundle.write_bytes(b"system")
            smoke_bundle = repo / "smoke.zip"; smoke_bundle.write_bytes(b"smoke")
            manifest = repo / "captures.json"
            manifest.write_text(json.dumps({
                "schema_version": 1,
                "captures": [
                    {"target_id": "system", "kind": "whole_system", "bundle": str(system_bundle)},
                    {"target_id": "smoke", "kind": "solo_emitter", "bundle": str(smoke_bundle)},
                ],
            }), encoding="utf-8")
            pv.register_captures(root, manifest)
            self.assertEqual(pv.load_run(root)["phase"], "classification")

    def test_capture_registration_requires_every_enabled_target(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            (repo / "workspace").mkdir()
            inv = repo / "inventory.json"
            inv.write_text(json.dumps({
                "schema_version": 1,
                "engine_version": "5.3.2",
                "project_name": "TestProject",
                "system_asset": "/Game/VFX/NS_Test",
                "emitters": [{"target_id": "smoke", "name": "Smoke", "enabled": True}],
            }), encoding="utf-8")
            root = pv.start(repo, inv, "test-vfx")
            system_bundle = repo / "system.zip"; system_bundle.write_bytes(b"system")
            manifest = repo / "captures.json"
            manifest.write_text(json.dumps({
                "schema_version": 1,
                "captures": [{"target_id": "system", "kind": "whole_system", "bundle": str(system_bundle)}],
            }), encoding="utf-8")
            with self.assertRaises(pv.VFXRunError):
                pv.register_captures(root, manifest)


if __name__ == "__main__":
    unittest.main()
