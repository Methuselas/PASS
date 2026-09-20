#!/usr/bin/env python3
"""Tests for extract_video_stills.

Lives beside the tool rather than under tests/ so that the PASS suite never
depends on ffmpeg being installed. Run it directly:

    python workspace/tools/test_extract_video_stills.py

Tests that need ffmpeg build a small synthetic screencast first and skip
themselves if ffmpeg cannot be found.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import zipfile
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "extract_video_stills", Path(__file__).with_name("extract_video_stills.py")
)
vs = importlib.util.module_from_spec(_SPEC)
assert _SPEC.loader is not None
# dataclasses resolves annotations through sys.modules, so register first.
sys.modules["extract_video_stills"] = vs
_SPEC.loader.exec_module(vs)

NO_WINDOW = 0x08000000 if sys.platform == "win32" else 0

# The behaviour this tool shipped with, before presets existed. Guarding these
# as literals is the point: a preset table edit must not move them.
ORIGINAL_DEFAULTS = {
    "capture_point": "middle",
    "min_gap": 0.0,
    "max_width": 1600,
    "image_format": "jpg",
    "quality": 85,
    "dedupe": True,
    "dedupe_threshold": 10,
    "workers": 4,
    "offset": 0.0,
}


# ---------------------------------------------------------------------------
# Synthetic fixture
# ---------------------------------------------------------------------------

FIXTURE: dict = {}

CODE_LINES = [
    "#include <iostream>",
    "using namespace std;",
    "",
    "int main()",
    "{",
    "    int a(1);",
    "    int b = 13;",
    "",
    "    if (b < a)",
    "    {",
    "        cout << \"b is less than a\" << endl;",
    "    }",
    "    else",
    "    {",
    "        cout << \"b is not less than a\" << endl;",
    "    }",
    "",
    "    return 0;",
    "}",
]


def _draw(ffmpeg: Path, lines: list[str], destination: Path, background: str) -> None:
    """Render a block of monospaced text onto a flat background.

    ffmpeg is run from the fixture directory and given relative names, because
    a Windows drive letter inside a filter argument needs escaping that varies
    between shells.
    """
    text_file = destination.with_suffix(".txt")
    text_file.write_text("\n".join(lines), encoding="utf-8")
    draw = (
        f"drawtext=textfile={text_file.name}:fontcolor=0xd4d4d4:"
        f"fontsize=22:x=80:y=60:line_spacing=6"
    )
    if sys.platform == "win32":
        # Copied in beside the text so the filter never sees a drive letter.
        font_source = Path("C:/Windows/Fonts/consola.ttf")
        font_local = destination.parent / "font.ttf"
        if font_source.is_file() and not font_local.exists():
            shutil.copyfile(font_source, font_local)
        if font_local.exists():
            draw += f":fontfile={font_local.name}"
    subprocess.run(
        [str(ffmpeg), "-v", "error", "-f", "lavfi", "-i",
         f"color=c={background}:s=1280x720", "-frames:v", "1", "-vf", draw,
         "-y", destination.name],
        check=True, capture_output=True, creationflags=NO_WINDOW,
        cwd=destination.parent,
    )


def setUpModule() -> None:
    """Build a screencast whose changes are known exactly.

    Six three-second segments. Segments 1/2 are identical, 3 changes one single
    line of the code block, 4 repeats it, 5 replaces the whole screen and 6
    repeats that. So an ideal comparator keeps 1, 3 and 5.
    """
    ffmpeg = vs.find_ffmpeg()
    if ffmpeg is None:
        return

    root = Path(tempfile.mkdtemp(prefix="vs_fixture_"))
    FIXTURE["root"] = root
    FIXTURE["ffmpeg"] = ffmpeg

    edited = list(CODE_LINES)
    edited[6] = "    int b = 42;   // changed one line only"
    other = ["TOTALLY DIFFERENT SCREEN"] + [f"line {n} of something else" for n in range(18)]

    _draw(ffmpeg, CODE_LINES, root / "a.png", "0x1e1e1e")
    _draw(ffmpeg, edited, root / "b.png", "0x1e1e1e")
    _draw(ffmpeg, other, root / "c.png", "0x102030")

    order = ["a", "a", "b", "b", "c", "c"]
    concat = root / "concat.txt"
    concat.write_text(
        "".join(f"file '{name}.png'\nduration 3\n" for name in order)
        + f"file '{order[-1]}.png'\n",
        encoding="utf-8",
    )

    video = root / "fixture.mp4"
    subprocess.run(
        [str(ffmpeg), "-v", "error", "-f", "concat", "-safe", "0", "-i", "concat.txt",
         "-vf", "fps=15,format=yuv420p", "-c:v", "libx264", "-crf", "20",
         "-y", "fixture.mp4"],
        check=True, capture_output=True, creationflags=NO_WINDOW, cwd=root,
    )

    cues = []
    for index in range(6):
        start, end = index * 3, index * 3 + 3
        cues.append(
            f"{index + 1}\n"
            f"00:00:{start:02d},100 --> 00:00:{end:02d},000\n"
            f"segment {index + 1} narration\n"
        )
    subtitles = root / "fixture.srt"
    subtitles.write_text("\n".join(cues), encoding="utf-8")

    FIXTURE["video"] = video
    FIXTURE["subtitles"] = subtitles

    # A miniature archive: nested sections, a lesson whose subtitles are
    # language-tagged, one with no subtitles at all, and one that is not really
    # a video. Between them they cover what a real course throws at a batch.
    tree = root / "archive"
    (tree / "section a" / "part b").mkdir(parents=True)
    shutil.copyfile(video, tree / "top.mp4")
    shutil.copyfile(subtitles, tree / "top.srt")
    shutil.copyfile(video, tree / "section a" / "lesson.mp4")
    shutil.copyfile(subtitles, tree / "section a" / "lesson.en-x-autogen.srt")
    shutil.copyfile(video, tree / "section a" / "part b" / "deep.mp4")
    shutil.copyfile(subtitles, tree / "section a" / "part b" / "deep.en.srt")
    shutil.copyfile(video, tree / "section a" / "orphan.mp4")  # no subtitles
    (tree / "broken.mp4").write_bytes(b"this is not a video" * 200)
    shutil.copyfile(subtitles, tree / "broken.srt")
    FIXTURE["archive"] = tree


def tearDownModule() -> None:
    root = FIXTURE.get("root")
    if root:
        shutil.rmtree(root, ignore_errors=True)


@contextlib.contextmanager
def isolated_config():
    """Keep tests out of the operator's real settings file.

    run_gui loads and saves settings, so a test that clicks Extract would
    otherwise overwrite choices a person made in the actual application.
    """
    root = Path(tempfile.mkdtemp(prefix="vs_cfg_"))
    original = vs.config_path
    vs.config_path = lambda: root / "config.json"
    try:
        yield root
    finally:
        vs.config_path = original
        shutil.rmtree(root, ignore_errors=True)


def set_check(check, widget_root, on: bool) -> None:
    """Put a ttk.Checkbutton into a known state.

    Not a blind invoke(): these settings persist between runs, so a toggle
    lands wherever the saved config happened to leave it.
    """
    selected = "selected" in check.state()
    if selected != on:
        check.invoke()
    assert ("selected" in check.state()) == on


def run_fixture(**overrides) -> tuple[vs.RunReport, Path]:
    """Extract the fixture with the given settings and return the report."""
    settings = vs.Settings(workers=2)
    preset = overrides.pop("preset", None)
    if preset:
        settings.apply_preset(preset)
    for key, value in overrides.items():
        setattr(settings, key, value)
    output = FIXTURE["root"] / f"out_{abs(hash(frozenset(overrides.items())))}.zip"
    report = vs.extract_bundle(
        FIXTURE["video"], FIXTURE["subtitles"], output, settings
    )
    return report, output


# ---------------------------------------------------------------------------
# 1. Backward compatibility
# ---------------------------------------------------------------------------


class TestBackwardCompatibility(unittest.TestCase):
    def test_bare_settings_match_the_original_defaults(self) -> None:
        settings = vs.Settings()
        for field, expected in ORIGINAL_DEFAULTS.items():
            self.assertEqual(getattr(settings, field), expected, field)
        self.assertEqual(settings.dedupe_mode, "visual")
        self.assertEqual(settings.preset, "general")

    def test_general_preset_is_the_original_defaults(self) -> None:
        settings = vs.Settings()
        settings.apply_preset("general")
        for field, expected in ORIGINAL_DEFAULTS.items():
            self.assertEqual(getattr(settings, field), expected, field)

    def test_cli_without_preset_uses_the_original_defaults(self) -> None:
        settings = capture_cli_settings(["video.mp4", "subs.srt"])
        for field, expected in ORIGINAL_DEFAULTS.items():
            self.assertEqual(getattr(settings, field), expected, field)

    def test_no_dedupe_flag_still_disables_comparison(self) -> None:
        settings = capture_cli_settings(["video.mp4", "subs.srt", "--no-dedupe"])
        self.assertEqual(settings.dedupe_mode, "off")
        self.assertFalse(settings.dedupe)

    def test_sensitivity_flag_still_sets_the_visual_threshold(self) -> None:
        settings = capture_cli_settings(["video.mp4", "subs.srt", "--sensitivity", "25"])
        self.assertEqual(settings.dedupe_threshold, 25)
        self.assertEqual(settings.dedupe_mode, "visual")


def capture_cli_settings(argv: list[str]) -> vs.Settings:
    """Run the command line but intercept the settings instead of extracting."""
    seen: dict = {}

    def fake_extract(video, subtitles, output, settings, **kwargs):
        seen["settings"] = settings
        return vs.RunReport(output=output)

    original = vs.extract_bundle
    vs.extract_bundle = fake_extract
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            code = vs.run_cli(argv)
    finally:
        vs.extract_bundle = original
    assert code == 0, f"run_cli exited {code}"
    return seen["settings"]


# ---------------------------------------------------------------------------
# 2-4. Presets
# ---------------------------------------------------------------------------


class TestPresets(unittest.TestCase):
    def test_every_preset_produces_valid_settings(self) -> None:
        for key in vs.PRESETS:
            settings = vs.Settings()
            settings.apply_preset(key)
            settings.validate()
            self.assertEqual(settings.preset, key)

    def test_apply_preset_sets_the_documented_fields(self) -> None:
        settings = vs.Settings()
        settings.apply_preset("blueprints")
        self.assertEqual(settings.capture_point, "end")
        self.assertEqual(settings.image_format, "png")
        self.assertEqual(settings.dedupe_mode, "sensitive")
        self.assertGreaterEqual(settings.max_width, 1920)

    def test_code_preset_keeps_every_frame(self) -> None:
        settings = vs.Settings()
        settings.apply_preset("code")
        self.assertEqual(settings.dedupe_mode, "off")
        self.assertEqual(settings.capture_point, "end")

    def test_apply_preset_leaves_machine_settings_alone(self) -> None:
        settings = vs.Settings(workers=9, offset=1.5, ffmpeg_path="/somewhere/ffmpeg")
        settings.apply_preset("slides")
        self.assertEqual(settings.workers, 9)
        self.assertEqual(settings.offset, 1.5)
        self.assertEqual(settings.ffmpeg_path, "/somewhere/ffmpeg")

    def test_unknown_preset_is_rejected(self) -> None:
        with self.assertRaises(vs.ExtractionError):
            vs.Settings().apply_preset("nonsense")

    def test_cli_preset_selects_the_preset(self) -> None:
        settings = capture_cli_settings(["v.mp4", "s.srt", "--preset", "blueprints"])
        self.assertEqual(settings.preset, "blueprints")
        self.assertEqual(settings.capture_point, "end")
        self.assertEqual(settings.image_format, "png")
        self.assertEqual(settings.dedupe_mode, "sensitive")

    def test_cli_overrides_win_over_the_preset(self) -> None:
        settings = capture_cli_settings([
            "v.mp4", "s.srt", "--preset", "code",
            "--format", "jpg", "--at", "middle", "--dedupe", "sensitive",
            "--tile-threshold", "2.5", "--max-width", "1280",
        ])
        self.assertEqual(settings.preset, "code")
        self.assertEqual(settings.image_format, "jpg")
        self.assertEqual(settings.capture_point, "middle")
        self.assertEqual(settings.dedupe_mode, "sensitive")
        self.assertAlmostEqual(settings.tile_threshold, 2.5)
        self.assertEqual(settings.max_width, 1280)

    def test_no_dedupe_beats_an_explicit_preset_mode(self) -> None:
        settings = capture_cli_settings(
            ["v.mp4", "s.srt", "--preset", "blueprints", "--no-dedupe"]
        )
        self.assertEqual(settings.dedupe_mode, "off")


# ---------------------------------------------------------------------------
# 6-8. Comparison arithmetic, without ffmpeg
# ---------------------------------------------------------------------------


def flat(value: int, width: int, height: int) -> bytes:
    return bytes([value]) * (width * height)


def with_patch(base: bytes, width: int, x: int, y: int, size: int, value: int) -> bytes:
    """Paint a square of a different shade into a thumbnail."""
    buffer = bytearray(base)
    for row in range(y, y + size):
        start = row * width + x
        buffer[start:start + size] = bytes([value]) * size
    return bytes(buffer)


class TestComparison(unittest.TestCase):
    W, H = vs.SENSITIVE_WIDTH, vs.SENSITIVE_HEIGHT

    def test_identical_thumbnails_score_zero(self) -> None:
        base = flat(90, self.W, self.H)
        self.assertEqual(vs.max_tile_difference(base, base), 0.0)

    def test_a_small_bright_patch_scores_far_above_the_default(self) -> None:
        base = flat(40, self.W, self.H)
        # 16x16 is one tile of the 16x9 grid: about 0.7% of the picture.
        changed = with_patch(base, self.W, 32, 48, 16, 220)
        score = vs.max_tile_difference(base, changed)
        self.assertGreater(score, 100.0)

    def test_whole_frame_hash_is_blind_to_that_same_patch(self) -> None:
        # The point of the sensitive mode: a patch this small barely registers
        # once the frame is reduced to 16x16.
        base = flat(40, 16, 16)
        changed = with_patch(base, 16, 2, 3, 1, 220)
        distance = vs.hamming_distance(
            vs.difference_hash(base), vs.difference_hash(changed)
        )
        self.assertLessEqual(distance, 10)

    def test_uniform_low_noise_stays_under_the_threshold(self) -> None:
        base = flat(90, self.W, self.H)
        noisy = bytes((value + (index % 2)) for index, value in enumerate(base))
        score = vs.max_tile_difference(base, noisy)
        self.assertLess(score, vs.PRESETS["blueprints"].tile_threshold)

    def test_wrong_sized_thumbnails_are_refused(self) -> None:
        self.assertIsNone(vs.max_tile_difference(b"short", b"short"))

    def test_hash_constants_agree(self) -> None:
        self.assertEqual(vs.VISUAL_BITS, vs.VISUAL_EDGE * (vs.VISUAL_EDGE - 1))
        self.assertEqual(vs.VISUAL_BITS, 240)
        self.assertEqual(vs.SENSITIVE_WIDTH % vs.SENSITIVE_TILES_X, 0)
        self.assertEqual(vs.SENSITIVE_HEIGHT % vs.SENSITIVE_TILES_Y, 0)

    def test_gui_slider_range_covers_the_visual_threshold_defaults(self) -> None:
        for preset in vs.PRESETS.values():
            if preset.dedupe_mode == "visual":
                self.assertLessEqual(preset.dedupe_threshold, 40)
            if preset.dedupe_mode == "sensitive":
                self.assertLessEqual(preset.tile_threshold, 8.0)


# ---------------------------------------------------------------------------
# 5, 6-10. End to end against the fixture
# ---------------------------------------------------------------------------


class TestEndToEnd(unittest.TestCase):
    def setUp(self) -> None:
        # Checked here rather than as a class decorator: the fixture is built by
        # setUpModule, which runs after the class body is evaluated.
        if "video" not in FIXTURE:
            self.skipTest("ffmpeg not available")

    def test_dedupe_off_keeps_every_planned_capture(self) -> None:
        report, _ = run_fixture(dedupe_mode="off")
        self.assertEqual(report.cue_count, 6)
        self.assertEqual(report.planned, 6)
        self.assertEqual(report.kept, 6)
        self.assertEqual(report.duplicates, 0)
        self.assertEqual(report.failures, [])

    def test_visual_mode_drops_the_repeated_screens(self) -> None:
        report, _ = run_fixture(dedupe_mode="visual")
        # Segments 2, 4 and 6 repeat their predecessor exactly.
        self.assertGreaterEqual(report.duplicates, 3)
        self.assertLessEqual(report.kept, 3)

    def test_sensitive_mode_keeps_the_single_changed_line(self) -> None:
        visual, _ = run_fixture(dedupe_mode="visual")
        sensitive, _ = run_fixture(dedupe_mode="sensitive", tile_threshold=0.8)
        # Segment 3 differs from segment 1 by one line of text. That is the
        # frame the whole-frame hash throws away and this mode must not.
        self.assertGreater(
            sensitive.kept, visual.kept,
            "sensitive mode kept no more than the whole-frame hash",
        )
        self.assertEqual(sensitive.kept, 3)

    def test_manifest_records_the_resolved_settings(self) -> None:
        _, output = run_fixture(preset="blueprints")
        manifest = read_member(output, "manifest.json")
        payload = json.loads(manifest)

        self.assertEqual(payload["settings"]["preset"], "blueprints")
        self.assertEqual(payload["settings"]["capture_point"], "end")
        self.assertEqual(payload["settings"]["image_format"], "png")
        self.assertEqual(payload["settings"]["dedupe_mode"], "sensitive")
        self.assertIn("max_width", payload["settings"])
        self.assertIn("quality", payload["settings"])
        self.assertIn("encoder_arguments", payload["settings"])

        comparison = payload["comparison"]
        self.assertEqual(comparison["mode"], "sensitive")
        self.assertEqual(comparison["method"], vs.SENSITIVE_METHOD)
        self.assertEqual(comparison["thumbnail_width"], vs.SENSITIVE_WIDTH)
        self.assertEqual(comparison["tiles_x"], vs.SENSITIVE_TILES_X)
        self.assertEqual(comparison["threshold"], 0.8)

        # Fields the original manifest carried must still be there.
        for key in ("tool", "video", "subtitles", "counts", "frames", "failures"):
            self.assertIn(key, payload)
        self.assertIn("dedupe", payload["settings"])
        self.assertIn("dedupe_threshold", payload["settings"])

    def test_visual_manifest_describes_the_hash(self) -> None:
        _, output = run_fixture(dedupe_mode="visual")
        comparison = json.loads(read_member(output, "manifest.json"))["comparison"]
        self.assertEqual(comparison["mode"], "visual")
        self.assertEqual(comparison["hash_bits"], vs.VISUAL_BITS)

    def test_off_manifest_says_so(self) -> None:
        _, output = run_fixture(dedupe_mode="off")
        comparison = json.loads(read_member(output, "manifest.json"))["comparison"]
        self.assertEqual(comparison["mode"], "off")

    def test_bundle_structure_is_unchanged(self) -> None:
        _, output = run_fixture(dedupe_mode="visual")
        with zipfile.ZipFile(output) as archive:
            names = archive.namelist()
        stem = "fixture"
        self.assertIn(f"{stem}/transcript.md", names)
        self.assertIn(f"{stem}/manifest.json", names)
        self.assertIn(f"{stem}/fixture.srt", names)
        self.assertTrue(any(name.startswith(f"{stem}/frames/") for name in names))

    def test_transcript_keeps_every_cue_even_when_frames_are_dropped(self) -> None:
        report, output = run_fixture(dedupe_mode="visual")
        transcript = read_member(output, "transcript.md").decode("utf-8")
        self.assertLess(report.kept, 6, "fixture should have dropped something")
        for index in range(1, 7):
            self.assertIn(f"segment {index} narration", transcript)

    def test_manifest_frame_count_matches_the_archive(self) -> None:
        report, output = run_fixture(dedupe_mode="sensitive", tile_threshold=0.8)
        payload = json.loads(read_member(output, "manifest.json"))
        with zipfile.ZipFile(output) as archive:
            frames = [n for n in archive.namelist() if "/frames/" in n]
        self.assertEqual(len(frames), report.kept)
        self.assertEqual(len(payload["frames"]), report.kept)
        self.assertEqual(payload["counts"]["frames"], report.kept)

    def test_capture_point_end_lands_inside_the_cue(self) -> None:
        _, output = run_fixture(capture_point="end", dedupe_mode="off")
        payload = json.loads(read_member(output, "manifest.json"))
        for entry in payload["frames"]:
            self.assertGreater(entry["timestamp_seconds"], 0)

    def test_max_width_never_enlarges_the_source(self) -> None:
        _, output = run_fixture(dedupe_mode="off", max_width=4000, image_format="png")
        with zipfile.ZipFile(output) as archive:
            name = next(n for n in archive.namelist() if "/frames/" in n)
            data = archive.read(name)
        # PNG width lives in bytes 16-20 of the IHDR chunk.
        width = int.from_bytes(data[16:20], "big")
        self.assertEqual(width, 1280)


# ---------------------------------------------------------------------------
# Batch conversion
# ---------------------------------------------------------------------------


class TestSubtitlePairing(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp(prefix="vs_pair_"))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)

    def touch(self, name: str) -> Path:
        path = self.root / name
        path.write_text("x", encoding="utf-8")
        return path

    def test_exact_stem_beats_language_tagged(self) -> None:
        self.touch("lesson.mp4")
        self.touch("lesson.en.srt")
        exact = self.touch("lesson.srt")
        self.assertEqual(vs.guess_subtitles(self.root / "lesson.mp4"), exact)

    def test_srt_beats_vtt(self) -> None:
        self.touch("lesson.mp4")
        self.touch("lesson.en-x-autogen.vtt")
        srt = self.touch("lesson.en-x-autogen.srt")
        self.assertEqual(vs.guess_subtitles(self.root / "lesson.mp4"), srt)

    def test_english_beats_other_languages(self) -> None:
        self.touch("lesson.mp4")
        self.touch("lesson.es.srt")
        english = self.touch("lesson.en.srt")
        self.assertEqual(vs.guess_subtitles(self.root / "lesson.mp4"), english)

    def test_a_different_lesson_sharing_a_prefix_is_not_matched(self) -> None:
        self.touch("lesson.mp4")
        self.touch("lesson 2 extra.srt")
        self.assertIsNone(vs.guess_subtitles(self.root / "lesson.mp4"))

    def test_missing_subtitles_returns_none(self) -> None:
        self.touch("lesson.mp4")
        self.assertIsNone(vs.guess_subtitles(self.root / "lesson.mp4"))

    def test_webvtt_short_timecodes_parse(self) -> None:
        path = self.root / "short.srt"
        path.write_text(
            "1\n00:02.500 --> 00:05.000\nno hours field here\n", encoding="utf-8"
        )
        cues = vs.parse_srt(path)
        self.assertEqual(len(cues), 1)
        self.assertAlmostEqual(cues[0].start, 2.5)
        self.assertAlmostEqual(cues[0].end, 5.0)


class TestBatchDiscovery(unittest.TestCase):
    def setUp(self) -> None:
        if "archive" not in FIXTURE:
            self.skipTest("ffmpeg not available")
        self.source = FIXTURE["archive"]
        self.destination = Path(tempfile.mkdtemp(prefix="vs_out_"))
        self.addCleanup(shutil.rmtree, self.destination, ignore_errors=True)

    def find(self, **kwargs):
        return vs.find_batch_items(self.source, self.destination, **kwargs)

    def test_finds_every_video_recursively(self) -> None:
        names = sorted(item.video.name for item in self.find())
        self.assertEqual(
            names, ["broken.mp4", "deep.mp4", "lesson.mp4", "orphan.mp4", "top.mp4"]
        )

    def test_non_recursive_stays_at_the_top(self) -> None:
        names = sorted(item.video.name for item in self.find(recursive=False))
        self.assertEqual(names, ["broken.mp4", "top.mp4"])

    def test_output_mirrors_the_source_structure(self) -> None:
        items = {item.video.name: item for item in self.find()}
        self.assertEqual(
            items["deep.mp4"].output.relative_to(self.destination),
            Path("section a") / "part b" / "deep.stills.zip",
        )
        self.assertEqual(
            items["top.mp4"].output.relative_to(self.destination),
            Path("top.stills.zip"),
        )

    def test_language_tagged_subtitles_are_paired(self) -> None:
        items = {item.video.name: item for item in self.find()}
        self.assertIsNotNone(items["lesson.mp4"].subtitles)
        self.assertEqual(
            items["lesson.mp4"].subtitles.name, "lesson.en-x-autogen.srt"
        )
        self.assertTrue(items["lesson.mp4"].ready)

    def test_a_video_without_subtitles_is_marked_not_ready(self) -> None:
        items = {item.video.name: item for item in self.find()}
        orphan = items["orphan.mp4"]
        self.assertIsNone(orphan.subtitles)
        self.assertFalse(orphan.ready)
        self.assertIn("subtitle", orphan.skip_reason)

    def test_existing_output_is_skipped_and_can_be_forced(self) -> None:
        items = {item.video.name: item for item in self.find()}
        target = items["top.mp4"].output
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"already here")

        again = {item.video.name: item for item in self.find()}["top.mp4"]
        self.assertFalse(again.ready)
        self.assertEqual(again.skip_reason, "already built")

        forced = {
            item.video.name: item for item in self.find(skip_existing=False)
        }["top.mp4"]
        self.assertTrue(forced.ready)


class TestBatchRun(unittest.TestCase):
    def setUp(self) -> None:
        if "archive" not in FIXTURE:
            self.skipTest("ffmpeg not available")
        self.source = FIXTURE["archive"]
        self.destination = Path(tempfile.mkdtemp(prefix="vs_run_"))
        self.addCleanup(shutil.rmtree, self.destination, ignore_errors=True)
        self.settings = vs.Settings(workers=2)
        self.settings.apply_preset("slides")

    def run_batch(self, **kwargs):
        items = vs.find_batch_items(self.source, self.destination)
        return vs.extract_batch(
            items, self.settings, self.destination, **kwargs
        ), items

    def test_converts_the_ready_items_and_skips_the_rest(self) -> None:
        report, items = self.run_batch()
        self.assertEqual(report.done, 3)  # top, lesson, deep
        self.assertEqual(report.skipped, 1)  # orphan, no subtitles
        self.assertEqual(report.failed, 1)  # broken.mp4
        self.assertGreater(report.frames, 0)

    def test_one_unreadable_video_does_not_stop_the_queue(self) -> None:
        report, _ = self.run_batch()
        statuses = {
            outcome.item.video.name: outcome.status for outcome in report.outcomes
        }
        self.assertEqual(statuses["broken.mp4"], "failed")
        # Alphabetically broken.mp4 comes first, so everything after it ran.
        self.assertEqual(statuses["top.mp4"], "done")
        self.assertEqual(statuses["deep.mp4"], "done")

    def test_bundles_land_in_the_mirrored_structure(self) -> None:
        self.run_batch()
        self.assertTrue((self.destination / "top.stills.zip").is_file())
        self.assertTrue(
            (self.destination / "section a" / "part b" / "deep.stills.zip").is_file()
        )

    def test_report_records_every_item(self) -> None:
        report, _ = self.run_batch()
        path = self.destination / "batch_report.json"
        self.assertTrue(path.is_file())
        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(payload["counts"]["total"], 5)
        self.assertEqual(payload["counts"]["done"], report.done)
        self.assertEqual(payload["settings"]["preset"], "slides")
        self.assertEqual(len(payload["items"]), 5)
        for entry in payload["items"]:
            self.assertIn(entry["status"], {"done", "skipped", "failed"})

    def test_rerunning_skips_finished_work(self) -> None:
        self.run_batch()
        second, _ = self.run_batch()
        self.assertEqual(second.done, 0)
        self.assertGreaterEqual(second.skipped, 3)

    def test_cancelling_stops_the_queue(self) -> None:
        cancel = threading.Event()
        cancel.set()
        items = vs.find_batch_items(self.source, self.destination)
        report = vs.extract_batch(
            items, self.settings, self.destination, cancel=cancel, write_report=False
        )
        self.assertTrue(report.cancelled)
        self.assertEqual(report.outcomes, [])


class TestBatchCli(unittest.TestCase):
    def setUp(self) -> None:
        if "archive" not in FIXTURE:
            self.skipTest("ffmpeg not available")
        self.destination = Path(tempfile.mkdtemp(prefix="vs_cli_"))
        self.addCleanup(shutil.rmtree, self.destination, ignore_errors=True)

    def test_a_directory_argument_dispatches_to_batch(self) -> None:
        seen: dict = {}

        def fake_batch(items, settings, destination, **kwargs):
            seen["items"] = items
            seen["settings"] = settings
            seen["destination"] = destination
            return vs.BatchReport(destination=destination)

        original = vs.extract_batch
        vs.extract_batch = fake_batch
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                code = vs.run_cli([
                    str(FIXTURE["archive"]), "-o", str(self.destination),
                    "--preset", "slides",
                ])
        finally:
            vs.extract_batch = original

        self.assertEqual(code, 0)
        self.assertEqual(seen["destination"], self.destination)
        self.assertEqual(seen["settings"].preset, "slides")
        self.assertEqual(len(seen["items"]), 5)

    def test_dry_run_converts_nothing(self) -> None:
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            code = vs.run_cli([
                str(FIXTURE["archive"]), "-o", str(self.destination), "--dry-run",
            ])
        self.assertEqual(code, 0)
        self.assertIn("convert", buffer.getvalue())
        self.assertFalse(any(self.destination.rglob("*.zip")))

    def test_no_recursive_limits_the_queue(self) -> None:
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            vs.run_cli([
                str(FIXTURE["archive"]), "-o", str(self.destination),
                "--dry-run", "--no-recursive",
            ])
        self.assertIn("2 videos under", buffer.getvalue())


# ---------------------------------------------------------------------------
# Transcription for videos without subtitles
# ---------------------------------------------------------------------------


class TestFilterEscaping(unittest.TestCase):
    """The escaping below is the only reason the whisper filter parses at all.

    ffmpeg unescapes filter options twice, so a Windows drive letter needs the
    value both single-quoted and its colon escaped. Getting this wrong fails at
    runtime with an opaque parser error, so pin the exact form.
    """

    def test_windows_path_is_quoted_and_escaped(self) -> None:
        self.assertEqual(
            vs.escape_filter_path(r"C:\models\ggml-large-v3-turbo.bin"),
            "'C\\:/models/ggml-large-v3-turbo.bin'",
        )

    def test_posix_path_is_quoted(self) -> None:
        self.assertEqual(
            vs.escape_filter_path("/home/x/ggml-base.bin"), "'/home/x/ggml-base.bin'"
        )

    def test_single_quote_in_a_path_is_escaped(self) -> None:
        self.assertEqual(vs.escape_filter_path("/a'b/m.bin"), "'/a\\'b/m.bin'")


class TestModelDiscovery(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp(prefix="vs_models_"))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        original = vs._model_search_dirs
        vs._model_search_dirs = lambda: [self.root]
        self.addCleanup(setattr, vs, "_model_search_dirs", original)

    def put(self, name: str, size: int = 16) -> Path:
        path = self.root / name
        path.write_bytes(b"\0" * size)
        return path

    def test_prefers_the_best_known_model(self) -> None:
        self.put("ggml-base.en.bin")
        best = self.put("ggml-large-v3-turbo.bin")
        self.assertEqual(vs.find_whisper_model(), best)

    def test_falls_back_to_the_largest_unknown_model(self) -> None:
        self.put("ggml-something-odd.bin", size=10)
        big = self.put("ggml-another-odd.bin", size=9000)
        self.assertEqual(vs.find_whisper_model(), big)

    def test_the_vad_model_is_not_mistaken_for_a_speech_model(self) -> None:
        self.put("ggml-silero-v6.2.0.bin", size=9000)
        self.assertIsNone(vs.find_whisper_model())
        self.assertIsNotNone(vs.find_vad_model())

    def test_an_explicit_path_wins(self) -> None:
        self.put("ggml-large-v3-turbo.bin")
        chosen = self.put("my-own.bin")
        self.assertEqual(vs.find_whisper_model(str(chosen)), chosen)

    def test_missing_model_returns_none(self) -> None:
        self.assertIsNone(vs.find_whisper_model())

    def test_doctor_reports_where_it_looked(self) -> None:
        """Exists because a stale build once claimed no model while the file
        was sitting in the directory the message itself named."""
        self.put("ggml-base.en.bin")
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            code = vs.run_cli(["--doctor"])
        report = buffer.getvalue()
        self.assertEqual(code, 0)
        self.assertIn(str(self.root), report)
        self.assertIn("ggml-base.en.bin", report)
        self.assertIn("frozen", report)

    def test_doctor_is_honest_when_nothing_is_found(self) -> None:
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            vs.run_cli(["--doctor"])
        self.assertIn("(not found)", buffer.getvalue())


class TestModelLocations(unittest.TestCase):
    """Kept apart from TestModelDiscovery, which patches the search path.

    These exercise the real search order, so the two must not share a setUp.
    """

    def test_a_model_beside_the_settings_file_is_found(self) -> None:
        """Settings live under Roaming and models under Local. Someone who puts
        the model next to the settings should not be told there isn't one."""
        roaming = Path(tempfile.mkdtemp(prefix="vs_roaming_"))
        self.addCleanup(shutil.rmtree, roaming, ignore_errors=True)
        empty = Path(tempfile.mkdtemp(prefix="vs_local_"))
        self.addCleanup(shutil.rmtree, empty, ignore_errors=True)

        original_config, original_dir = vs.config_path, vs.model_dir
        vs.config_path = lambda: roaming / "config.json"
        vs.model_dir = lambda: empty
        self.addCleanup(setattr, vs, "config_path", original_config)
        self.addCleanup(setattr, vs, "model_dir", original_dir)

        beside_settings = roaming / "models"
        beside_settings.mkdir()
        expected = beside_settings / "ggml-base.en.bin"
        expected.write_bytes(bytes(32))

        self.assertEqual(vs.find_whisper_model(), expected)

    def test_a_model_beside_the_program_wins(self) -> None:
        """Keeps the application self-contained: the copy shipped beside the
        executable beats anything in a per-user directory."""
        beside = Path(tempfile.mkdtemp(prefix="vs_bundle_"))
        elsewhere = Path(tempfile.mkdtemp(prefix="vs_local_"))
        self.addCleanup(shutil.rmtree, beside, ignore_errors=True)
        self.addCleanup(shutil.rmtree, elsewhere, ignore_errors=True)

        original_bundle, original_dir = vs._bundle_dir, vs.model_dir
        vs._bundle_dir = lambda: beside
        vs.model_dir = lambda: elsewhere
        self.addCleanup(setattr, vs, "_bundle_dir", original_bundle)
        self.addCleanup(setattr, vs, "model_dir", original_dir)

        (beside / "models").mkdir()
        shipped = beside / "models" / "ggml-base.en.bin"
        shipped.write_bytes(bytes(32))
        (elsewhere / "ggml-base.en.bin").write_bytes(bytes(32))

        self.assertEqual(vs.find_whisper_model(), shipped)

    def test_the_local_directory_still_wins(self) -> None:
        roaming = Path(tempfile.mkdtemp(prefix="vs_roaming_"))
        local = Path(tempfile.mkdtemp(prefix="vs_local_"))
        self.addCleanup(shutil.rmtree, roaming, ignore_errors=True)
        self.addCleanup(shutil.rmtree, local, ignore_errors=True)

        original_config, original_dir = vs.config_path, vs.model_dir
        vs.config_path = lambda: roaming / "config.json"
        vs.model_dir = lambda: local
        self.addCleanup(setattr, vs, "config_path", original_config)
        self.addCleanup(setattr, vs, "model_dir", original_dir)

        (roaming / "models").mkdir()
        (roaming / "models" / "ggml-base.en.bin").write_bytes(bytes(32))
        preferred = local / "ggml-base.en.bin"
        preferred.write_bytes(bytes(32))

        self.assertEqual(vs.find_whisper_model(), preferred)


class TestTranscriptionWiring(unittest.TestCase):
    def test_transcript_warns_when_the_words_are_machine_made(self) -> None:
        cues = [vs.Cue(1, 0.0, 1.0, "spoken words")]
        text = vs.build_transcript(
            "x", vs.VideoInfo(), vs.Settings(), cues, {}, transcribed=True
        )
        self.assertIn("machine transcription", text.lower())
        self.assertIn("spoken words", text)

    def test_transcript_says_nothing_when_subtitles_were_supplied(self) -> None:
        cues = [vs.Cue(1, 0.0, 1.0, "spoken words")]
        text = vs.build_transcript("x", vs.VideoInfo(), vs.Settings(), cues, {})
        self.assertNotIn("machine transcription", text.lower())

    def test_missing_subtitles_without_transcription_is_a_clear_error(self) -> None:
        if "archive" not in FIXTURE:
            self.skipTest("ffmpeg not available")
        orphan = FIXTURE["archive"] / "section a" / "orphan.mp4"
        destination = FIXTURE["root"] / "orphan.zip"
        with self.assertRaises(vs.ExtractionError) as caught:
            vs.extract_bundle(orphan, None, destination, vs.Settings())
        self.assertIn("No subtitles", str(caught.exception))

    def test_batch_queues_unsubtitled_videos_when_transcribing(self) -> None:
        if "archive" not in FIXTURE:
            self.skipTest("ffmpeg not available")
        destination = Path(tempfile.mkdtemp(prefix="vs_tr_"))
        self.addCleanup(shutil.rmtree, destination, ignore_errors=True)

        without = {
            item.video.name: item
            for item in vs.find_batch_items(FIXTURE["archive"], destination)
        }
        self.assertFalse(without["orphan.mp4"].ready)

        with_speech = {
            item.video.name: item
            for item in vs.find_batch_items(
                FIXTURE["archive"], destination, transcribe=True
            )
        }
        self.assertTrue(with_speech["orphan.mp4"].ready)
        self.assertIsNone(with_speech["orphan.mp4"].subtitles)

    def test_cli_transcribe_flags(self) -> None:
        settings = capture_cli_settings([
            "v.mp4", "s.srt", "--transcribe", "--language", "en",
            "--whisper-window", "45", "--no-gpu",
        ])
        self.assertTrue(settings.transcribe)
        self.assertEqual(settings.whisper_language, "en")
        self.assertEqual(settings.whisper_queue, 45)
        self.assertFalse(settings.whisper_gpu)

    def test_transcription_is_off_unless_asked_for(self) -> None:
        settings = capture_cli_settings(["v.mp4", "s.srt"])
        self.assertFalse(settings.transcribe)

    def test_window_default_favours_cue_count(self) -> None:
        # Measured: window 3 gave 44 cues in 6.1s against window 30's 26 in
        # 4.9s. One frame per cue makes the extra cues worth the time.
        self.assertEqual(vs.Settings().whisper_queue, 3)

    def test_a_zero_window_is_rejected(self) -> None:
        with self.assertRaises(vs.ExtractionError):
            vs.Settings(whisper_queue=0).validate()

    def test_voice_detection_is_off_unless_asked_for(self) -> None:
        # Measured at roughly 100x the runtime for no gain in cue granularity.
        self.assertFalse(vs.Settings().whisper_vad_enabled)
        self.assertTrue(capture_cli_settings(
            ["v.mp4", "s.srt", "--transcribe", "--vad"]
        ).whisper_vad_enabled)

    def test_gpu_is_on_by_default(self) -> None:
        # The whisper build in ffmpeg does use the GPU; measured 16x faster
        # than use_gpu=0 on the same audio.
        self.assertTrue(vs.Settings().whisper_gpu)


class TestProcessCleanup(unittest.TestCase):
    """Closing the app must not leave ffmpeg holding the speech model.

    A child process outlives the Python interpreter that started it, so this is
    the difference between quitting and leaking well over a gigabyte.
    """

    def setUp(self) -> None:
        if "video" not in FIXTURE:
            self.skipTest("ffmpeg not available")

    def spawn_long_ffmpeg(self):
        return subprocess.Popen(
            [str(FIXTURE["ffmpeg"]), "-nostdin", "-v", "error",
             "-f", "lavfi", "-i", "sine=f=440:d=120", "-f", "null", "-"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=NO_WINDOW,
        )

    def test_tracked_processes_are_killed(self) -> None:
        process = self.spawn_long_ffmpeg()
        self.addCleanup(lambda: process.poll() is None and process.kill())
        vs._track(process)
        self.assertIsNone(process.poll(), "fixture process should still be running")

        killed = vs.terminate_active_processes(timeout=10)

        self.assertGreaterEqual(killed, 1)
        self.assertIsNotNone(process.poll(), "process survived termination")
        self.assertNotIn(process, vs._ACTIVE_PROCESSES)

    def test_terminating_twice_is_harmless(self) -> None:
        process = self.spawn_long_ffmpeg()
        self.addCleanup(lambda: process.poll() is None and process.kill())
        vs._track(process)
        vs.terminate_active_processes(timeout=10)
        self.assertEqual(vs.terminate_active_processes(timeout=5), 0)

    def test_terminating_with_nothing_running_is_harmless(self) -> None:
        vs.terminate_active_processes(timeout=1)
        self.assertEqual(vs.terminate_active_processes(timeout=1), 0)

    def test_frame_capture_untracks_when_it_finishes(self) -> None:
        # A completed run must not leave entries behind, or a later close would
        # walk a list of dead processes.
        before = len(vs._ACTIVE_PROCESSES)
        run_fixture(dedupe_mode="off")
        self.assertEqual(len(vs._ACTIVE_PROCESSES), before)

    def test_single_file_can_transcribe_without_a_subtitle_file(self) -> None:
        """Extract used to refuse unless a subtitle path was filled in.

        Dialogs are intercepted rather than displayed: a modal warning in a test
        run hangs the suite instead of failing it.
        """
        import tkinter as tk
        from tkinter import messagebox, ttk

        try:
            probe = tk.Tk()
            probe.destroy()
        except tk.TclError:
            self.skipTest("no display available")

        popups: list = []
        started: list = []
        saved = (
            messagebox.showwarning, messagebox.showerror, vs.extract_bundle
        )
        messagebox.showwarning = lambda *a, **k: popups.append(("warn", a))
        messagebox.showerror = lambda *a, **k: popups.append(("error", a))

        def fake_extract(video, subtitles, output, settings, **kwargs):
            started.append((video, subtitles, settings.transcribe))
            return vs.RunReport(output=output)

        vs.extract_bundle = fake_extract
        original_mainloop = tk.Misc.mainloop

        def fake_mainloop(self, n: int = 0) -> None:
            root = self.winfo_toplevel()
            root.update()
            entries, buttons, checks = [], [], []

            def walk(widget) -> None:
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Entry):
                        entries.append(child)
                    elif isinstance(child, ttk.Button):
                        buttons.append(child)
                    elif isinstance(child, ttk.Checkbutton):
                        checks.append(child)
                    walk(child)

            walk(root)
            entries[0].insert(0, str(FIXTURE["video"]))            # video
            entries[2].insert(0, str(FIXTURE["root"] / "gui.zip"))  # output
            for check in checks:
                if "Transcribe" in str(check.cget("text")):
                    set_check(check, root, True)
            root.update()
            next(b for b in buttons if str(b.cget("text")) == "Extract").invoke()
            for _ in range(40):
                root.update()
                if started:
                    break
                time.sleep(0.05)
            root.tk.call(root.protocol("WM_DELETE_WINDOW"))

        tk.Misc.mainloop = fake_mainloop
        try:
            with isolated_config():
                vs.run_gui()
        finally:
            tk.Misc.mainloop = original_mainloop
            messagebox.showwarning, messagebox.showerror, vs.extract_bundle = saved

        self.assertEqual(popups, [], f"Extract was refused: {popups}")
        self.assertTrue(started, "Extract did not start any work")
        _video, subtitles, transcribe = started[0]
        self.assertIsNone(subtitles, "no subtitle file should have been invented")
        self.assertTrue(transcribe)

    def test_closing_the_window_terminates_running_ffmpeg(self) -> None:
        """The user's actual complaint, tested against the close handler.

        Deliberately not tested by letting a real interpreter exit: under a test
        runner the child is usually inside a job object that reaps it anyway, so
        that version of the test passes whether or not the cleanup exists. This
        drives the window's own WM_DELETE_WINDOW handler instead.
        """
        import tkinter as tk

        try:
            probe = tk.Tk()
            probe.destroy()
        except tk.TclError:
            self.skipTest("no display available")

        calls: list[int] = []
        real_terminate = vs.terminate_active_processes

        def recording_terminate(timeout: float = 5.0) -> int:
            calls.append(1)
            return real_terminate(timeout)

        process = self.spawn_long_ffmpeg()
        self.addCleanup(lambda: process.poll() is None and process.kill())
        vs._track(process)

        original_mainloop = tk.Misc.mainloop

        def fake_mainloop(self, n: int = 0) -> None:
            root = self.winfo_toplevel()
            root.update_idletasks()
            handler = root.protocol("WM_DELETE_WINDOW")
            assert handler, "the window registered no close handler"
            root.tk.call(handler)  # exactly what the X button does

        vs.terminate_active_processes = recording_terminate
        tk.Misc.mainloop = fake_mainloop
        try:
            with isolated_config():
                vs.run_gui()
        finally:
            tk.Misc.mainloop = original_mainloop
            vs.terminate_active_processes = real_terminate

        self.assertEqual(len(calls), 1, "closing the window did not clean up")
        self.assertIsNotNone(process.poll(), "ffmpeg survived the window closing")


# ---------------------------------------------------------------------------
# 2. Preset wiring inside the real window
# ---------------------------------------------------------------------------


class TestGuiPresetWiring(unittest.TestCase):
    """Drive the actual widget tree, because the GUI keeps its own copy of the
    preset-to-control mapping and a typo there would not show up anywhere else.
    """

    def _drive(self, preset_key: str) -> dict[str, str]:
        import tkinter as tk
        from tkinter import ttk

        try:
            probe = tk.Tk()
            probe.destroy()
        except tk.TclError:
            self.skipTest("no display available")

        seen: dict[str, str] = {}
        original = tk.Misc.mainloop

        def fake_mainloop(self, n: int = 0) -> None:
            root = self.winfo_toplevel()
            root.update_idletasks()

            combos: list[ttk.Combobox] = []

            def walk(widget) -> None:
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Combobox):
                        combos.append(child)
                    walk(child)

            walk(root)

            def values_of(combo) -> tuple[str, ...]:
                return tuple(str(v) for v in root.tk.splitlist(combo.cget("values")))

            def find(predicate):
                return next(c for c in combos if predicate(values_of(c)))

            preset_combo = find(lambda v: PRESET_LABEL_GENERAL in v)
            capture_combo = find(lambda v: v == tuple(vs.CAPTURE_POINTS))
            format_combo = find(lambda v: v == tuple(vs.IMAGE_FORMATS))
            mode_combo = find(lambda v: v == tuple(vs.DEDUPE_MODES))

            preset_combo.set(vs.PRESETS[preset_key].label)
            preset_combo.event_generate("<<ComboboxSelected>>")
            root.update()

            seen["capture"] = capture_combo.get()
            seen["format"] = format_combo.get()
            seen["mode"] = mode_combo.get()
            root.destroy()

        tk.Misc.mainloop = fake_mainloop
        try:
            with isolated_config():
                vs.run_gui()
        finally:
            tk.Misc.mainloop = original
        return seen

    def test_blueprints_preset_updates_the_controls(self) -> None:
        seen = self._drive("blueprints")
        self.assertEqual(seen["capture"], "end")
        self.assertEqual(seen["format"], "png")
        self.assertEqual(seen["mode"], "sensitive")

    def test_slides_preset_updates_the_controls(self) -> None:
        seen = self._drive("slides")
        self.assertEqual(seen["capture"], "middle")
        self.assertEqual(seen["format"], "jpg")
        self.assertEqual(seen["mode"], "visual")

    def test_code_preset_turns_comparison_off(self) -> None:
        seen = self._drive("code")
        self.assertEqual(seen["mode"], "off")


PRESET_LABEL_GENERAL = vs.PRESETS["general"].label


def read_member(archive_path: Path, suffix: str) -> bytes:
    with zipfile.ZipFile(archive_path) as archive:
        name = next(n for n in archive.namelist() if n.endswith(suffix))
        return archive.read(name)


if __name__ == "__main__":
    unittest.main(verbosity=2)
