#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("extract_vfx_stills", HERE / "extract_vfx_stills.py")
vs = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(vs)


class TestTemporalSampling(unittest.TestCase):
    def test_sample_times_cover_start_middle_and_end(self):
        points = vs.sample_times(2.0, 0.5)
        self.assertGreater(points[0], 0)
        self.assertIn(0.5, points)
        self.assertIn(1.5, points)
        self.assertLess(points[-1], 2.0)
        self.assertGreater(points[-1], 1.9)

    def test_synthetic_srt_has_one_cue_per_point(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "sample.srt"
            points = [0.05, 0.5, 0.95]
            vs.write_synthetic_srt(path, points, 1.0)
            text = path.read_text(encoding="utf-8")
            self.assertEqual(text.count("VFX temporal sample"), 3)
            self.assertIn("00:00:00,", text)


class TestManifest(unittest.TestCase):
    def test_manifest_accepts_whole_system_and_solo_emitter(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "manifest.json"
            path.write_text(json.dumps({
                "schema_version": 1,
                "captures": [
                    {"target_id": "system", "kind": "whole_system", "video": "system.mp4"},
                    {"target_id": "smoke", "kind": "solo_emitter", "video": "smoke.mp4"},
                ],
            }), encoding="utf-8")
            captures = vs.load_manifest(path)
            self.assertEqual([c["target_id"] for c in captures], ["system", "smoke"])

    def test_manifest_rejects_duplicate_target_ids(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "manifest.json"
            path.write_text(json.dumps({
                "schema_version": 1,
                "captures": [
                    {"target_id": "system", "kind": "whole_system", "video": "a.mp4"},
                    {"target_id": "system", "kind": "solo_emitter", "video": "b.mp4"},
                ],
            }), encoding="utf-8")
            with self.assertRaises(vs.ManifestError):
                vs.load_manifest(path)


if __name__ == "__main__":
    unittest.main()
