#!/usr/bin/env python3
"""Turn a video plus its subtitle track into a still-frame study bundle.

This is factory tooling, not PASS state. It reads a video and an SRT, captures
one frame per subtitle cue through ffmpeg, drops frames that look the same as
the one before them, and writes a zip holding the frames, the original
subtitles, and an interleaved transcript for a reading session. The output is a
convenience copy of a source and must never become card provenance or a release
dependency.

Run with no arguments for the GUI, or with arguments for the command line:

    python extract_video_stills.py                      # GUI
    python extract_video_stills.py VIDEO SRT -o OUT.zip # command line
    python extract_video_stills.py --doctor             # what can it find?

Packaged with PyInstaller into a self-contained folder:

    PASS-VIDEO-STILLS/
        pass-video-stills.exe
        models/ggml-large-v3-turbo.bin      (optional, for transcription)

That models folder is searched before anything else, so the application can be
moved or copied whole and the speech model travels with it.

Delete the PyInstaller work directory between builds. Reusing it has produced
an executable that did not match this file.

    rm -rf build/ && python -m PyInstaller --noconfirm --onefile --windowed \
        --name pass-video-stills --distpath ../builds/PASS-VIDEO-STILLS \
        extract_video_stills.py

Run --doctor, or the ? beside ffmpeg in the window, whenever the program and
something else disagree about what exists.
"""

from __future__ import annotations

import argparse
import atexit
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable, Sequence

APP_NAME = "PASS Video Stills"
CONFIG_DIR_NAME = "pass-video-stills"

# Windows spawns a console window for every child process unless told not to.
# The GUI build has no console of its own, so an unguarded ffmpeg call would
# flash one window per frame.
_NO_WINDOW = 0x08000000 if os.name == "nt" else 0

VIDEO_SUFFIXES = (
    ".mp4", ".mkv", ".mov", ".avi", ".webm", ".m4v", ".wmv", ".flv", ".mpg",
    ".mpeg", ".ts", ".m2ts", ".ogv", ".3gp",
)

CAPTURE_POINTS = ("start", "middle", "end")
IMAGE_FORMATS = ("jpg", "png", "webp")
DEDUPE_MODES = ("visual", "sensitive", "off")

# "visual" comparison. A 16x16 grayscale thumbnail yields a 240-bit difference
# hash: 15 horizontal comparisons across each of 16 rows. Cheap, and reliable
# when consecutive frames differ over most of the picture.
VISUAL_EDGE = 16
VISUAL_BITS = VISUAL_EDGE * (VISUAL_EDGE - 1)

# "sensitive" comparison. The whole-frame hash above is blind to an edit that
# occupies a small part of the screen: a node rewired in a corner of a Blueprint
# graph moves almost no global bits. This mode instead keeps a larger grayscale
# thumbnail, splits it into tiles, and asks how much the worst single tile
# changed, so a local edit is judged against its own neighbourhood rather than
# diluted across the picture.
#
# The geometry below was chosen by measurement, not taste. Across real Unreal
# editor and Visual Studio capture, 256x144 split 16x9 gave the widest margin
# between "nothing happened" and "something small happened" (~22x and ~18x) of
# the geometries tried, and at a smaller buffer than the 320x180 grids that
# scored the same. Static frames land near 0.15-0.25; the smallest real edits
# observed land near 3.0-4.6. See SENSITIVE_METHOD for the units.
SENSITIVE_WIDTH = 256
SENSITIVE_HEIGHT = 144
SENSITIVE_TILES_X = 16
SENSITIVE_TILES_Y = 9
SENSITIVE_METHOD = "tiled-mean-absolute-difference"

FRAME_TIMEOUT_SECONDS = 180

# Every ffmpeg this process starts is registered here. A child process is not
# killed when its parent exits, so closing the window mid-transcription would
# otherwise orphan an ffmpeg that holds the speech model - well over a gigabyte
# - in memory until it finished the audio on its own.
_ACTIVE_LOCK = threading.Lock()
_ACTIVE_PROCESSES: set = set()


def _track(process) -> None:
    with _ACTIVE_LOCK:
        _ACTIVE_PROCESSES.add(process)


def _untrack(process) -> None:
    with _ACTIVE_LOCK:
        _ACTIVE_PROCESSES.discard(process)


def terminate_active_processes(timeout: float = 5.0) -> int:
    """Kill every ffmpeg this process started and wait for it to go.

    Returns how many were still running. Safe to call more than once, and safe
    to call when nothing is running.
    """
    with _ACTIVE_LOCK:
        processes = list(_ACTIVE_PROCESSES)

    killed = 0
    for process in processes:
        try:
            if process.poll() is None:
                process.kill()
                killed += 1
        except OSError:
            pass

    deadline = time.monotonic() + timeout
    for process in processes:
        try:
            process.wait(timeout=max(0.0, deadline - time.monotonic()))
        except (subprocess.TimeoutExpired, OSError):
            pass
        _untrack(process)
    return killed


# A backstop for the command line, where Ctrl+C unwinds past the normal paths.
atexit.register(terminate_active_processes)


class ExtractionCancelled(Exception):
    """Raised when the operator stops a run that is already under way."""


class ExtractionError(Exception):
    """Raised for a condition the operator can correct and retry."""


# ---------------------------------------------------------------------------
# Content presets
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Preset:
    """A starting point for one kind of source material.

    A preset only fills the ordinary controls in. Nothing downstream reads the
    preset to decide behaviour, so an operator who changes a field afterwards
    gets exactly what the fields say.
    """

    key: str
    label: str
    summary: str
    capture_point: str
    max_width: int
    image_format: str
    quality: int
    dedupe_mode: str
    dedupe_threshold: int
    tile_threshold: float
    min_gap: float


PRESETS: dict[str, Preset] = {
    # Byte-for-byte the defaults this tool shipped with, so an operator who
    # never touches the control sees no change in behaviour.
    "general": Preset(
        key="general",
        label="General (current defaults)",
        summary=(
            "The original behaviour: mid-cue capture, 1600px JPEG, whole-frame "
            "comparison. A safe starting point for material you have not "
            "classified yet."
        ),
        capture_point="middle", max_width=1600, image_format="jpg", quality=85,
        dedupe_mode="visual", dedupe_threshold=10, tile_threshold=1.0, min_gap=0.0,
    ),
    "vfx": Preset(
        key="vfx",
        label="VFX / Visual",
        summary=(
            "Niagara, particle systems, materials and art demonstrations. The "
            "picture changes over most of its area between cues, so whole-frame "
            "comparison is both correct and cheap. Full 1920px so panel values "
            "stay readable."
        ),
        capture_point="middle", max_width=1920, image_format="jpg", quality=90,
        dedupe_mode="visual", dedupe_threshold=10, tile_threshold=1.0, min_gap=0.0,
    ),
    "blueprints": Preset(
        key="blueprints",
        label="Blueprints / Node graphs",
        summary=(
            "Node graphs, pin wiring and property panels. Captures at the end of "
            "each cue, because the instructor usually finishes the wiring being "
            "described while still describing it. Lossless PNG keeps thin wires "
            "and small pin labels intact, and tile comparison keeps a frame when "
            "one corner of the graph changes."
        ),
        capture_point="end", max_width=2560, image_format="png", quality=95,
        dedupe_mode="sensitive", dedupe_threshold=10, tile_threshold=0.8, min_gap=0.0,
    ),
    "code": Preset(
        key="code",
        label="Code / IDE",
        summary=(
            "Source code, shaders and IDE walkthroughs. Comparison is off by "
            "default: a single changed character survives downscaling so poorly "
            "that no cheap perceptual test can tell it from compression noise, so "
            "every planned frame is kept rather than risk losing an edit. "
            "Captures at the end of each cue, since code is usually finished "
            "while it is being explained."
        ),
        capture_point="end", max_width=2560, image_format="png", quality=95,
        dedupe_mode="off", dedupe_threshold=10, tile_threshold=0.5, min_gap=0.0,
    ),
    "slides": Preset(
        key="slides",
        label="Slides / Lecture",
        summary=(
            "Presentation decks and talking-head lecture. One slide holds for "
            "many cues, so whole-frame comparison runs deliberately eager to drop "
            "repeats and the bundle stays small."
        ),
        capture_point="middle", max_width=1600, image_format="jpg", quality=85,
        dedupe_mode="visual", dedupe_threshold=16, tile_threshold=1.0, min_gap=0.0,
    ),
    "software": Preset(
        key="software",
        label="Software walkthrough / UI",
        summary=(
            "Tool and application walkthroughs. Tile comparison so an opened "
            "dialog, a changed setting or a menu state is kept even though it "
            "covers little of the screen, at a slightly calmer threshold than "
            "Blueprints because UI elements are larger."
        ),
        capture_point="middle", max_width=1920, image_format="jpg", quality=92,
        dedupe_mode="sensitive", dedupe_threshold=10, tile_threshold=1.2, min_gap=0.0,
    ),
}

DEFAULT_PRESET = "general"


# ---------------------------------------------------------------------------
# Subtitle parsing
# ---------------------------------------------------------------------------

# The hours field is optional because WebVTT often omits it, and a batch run
# must not die on one oddly written cue.
_STAMP = r"(?:\d{1,3}:)?\d{1,2}:\d{2}[,.]\d{1,3}"
TIMING_RE = re.compile(rf"(?P<start>{_STAMP})\s*-->\s*(?P<end>{_STAMP})")

TAG_RE = re.compile(r"</?[a-zA-Z][^>]*>")


@dataclass(frozen=True)
class Cue:
    """One subtitle entry, with times in seconds from the start of the video."""

    index: int
    start: float
    end: float
    text: str

    @property
    def duration(self) -> float:
        return max(0.0, self.end - self.start)

    def capture_time(self, point: str, offset: float) -> float:
        if point == "start":
            base = self.start
        elif point == "end":
            base = self.end
        else:
            base = self.start + self.duration / 2.0
        return max(0.0, base + offset)


def parse_timecode(text: str) -> float:
    """Return seconds for an ``HH:MM:SS,mmm`` or ``MM:SS.mmm`` timecode."""
    fields = text.strip().split(":")
    if len(fields) == 2:
        fields = ["0", *fields]
    hours, minutes, rest = fields
    parts = re.split(r"[,.]", rest.strip(), maxsplit=1)
    millis = (parts[1] if len(parts) > 1 else "0").ljust(3, "0")[:3]
    return int(hours) * 3600 + int(minutes) * 60 + int(parts[0]) + int(millis) / 1000.0


def clean_cue_text(lines: Sequence[str]) -> str:
    """Collapse a cue's lines into one string with markup and cruft removed."""
    joined = " ".join(line.strip() for line in lines if line.strip())
    joined = TAG_RE.sub("", joined)
    joined = joined.replace("{\\an8}", "").replace("\u200b", "")
    return re.sub(r"\s+", " ", joined).strip()


def parse_srt(path: Path) -> list[Cue]:
    """Parse an SRT file into cues, tolerating BOMs, CRLFs and missing indexes."""
    raw = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            text = raw.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:  # pragma: no cover - latin-1 decodes any byte string
        raise ExtractionError(f"Could not decode {path.name} as text.")

    text = text.replace("\r\n", "\n").replace("\r", "\n")

    cues: list[Cue] = []
    pending_lines: list[str] = []
    timing: tuple[float, float] | None = None

    def flush() -> None:
        nonlocal timing, pending_lines
        if timing is not None:
            body = clean_cue_text(pending_lines)
            if body:
                cues.append(Cue(len(cues) + 1, timing[0], timing[1], body))
        timing = None
        pending_lines = []

    for line in text.split("\n"):
        match = TIMING_RE.search(line)
        if match:
            flush()
            timing = (
                parse_timecode(match.group("start")),
                parse_timecode(match.group("end")),
            )
            continue
        if timing is None:
            continue
        if not line.strip():
            flush()
            continue
        pending_lines.append(line)

    flush()

    if not cues:
        raise ExtractionError(f"No subtitle cues found in {path.name}.")
    return cues


def format_timestamp(seconds: float, *, for_filename: bool = False) -> str:
    """Render seconds as ``HH:MM:SS.mmm``, or a filename-safe variant."""
    total_ms = int(round(max(0.0, seconds) * 1000))
    hours, remainder = divmod(total_ms, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, millis = divmod(remainder, 1000)
    sep = "-" if for_filename else ":"
    return f"{hours:02d}{sep}{minutes:02d}{sep}{secs:02d}.{millis:03d}"


# ---------------------------------------------------------------------------
# ffmpeg discovery and probing
# ---------------------------------------------------------------------------


def _bundle_dir() -> Path:
    """Return the directory holding the running script or frozen executable."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent


def candidate_ffmpeg_paths() -> Iterable[Path]:
    """Yield plausible ffmpeg locations, nearest first."""
    exe = "ffmpeg.exe" if os.name == "nt" else "ffmpeg"
    bundle = _bundle_dir()
    yield bundle / exe
    yield bundle / "ffmpeg" / exe
    yield bundle / "bin" / exe

    found = shutil.which("ffmpeg")
    if found:
        yield Path(found)

    if os.name == "nt":
        for root in (
            Path("C:/ffmpeg/bin"),
            Path("C:/Program Files/ffmpeg/bin"),
            Path("C:/ProgramData/chocolatey/bin"),
            Path(os.environ.get("LOCALAPPDATA", "C:/")) / "Microsoft" / "WinGet" / "Links",
        ):
            yield root / exe
    else:
        for root in (Path("/usr/bin"), Path("/usr/local/bin"), Path("/opt/homebrew/bin")):
            yield root / exe


def find_ffmpeg(preferred: str | os.PathLike[str] | None = None) -> Path | None:
    """Return a usable ffmpeg binary, preferring an operator-supplied path."""
    if preferred:
        candidate = Path(preferred).expanduser()
        if candidate.is_file():
            return candidate
    for candidate in candidate_ffmpeg_paths():
        try:
            if candidate.is_file():
                return candidate
        except OSError:
            continue
    return None


def sibling_ffprobe(ffmpeg: Path) -> Path | None:
    """Return the ffprobe that ships beside a given ffmpeg, if there is one."""
    name = "ffprobe.exe" if os.name == "nt" else "ffprobe"
    candidate = ffmpeg.with_name(name)
    if candidate.is_file():
        return candidate
    found = shutil.which("ffprobe")
    return Path(found) if found else None


def _run(cmd: Sequence[object], *, timeout: int = 60) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        [str(part) for part in cmd],
        capture_output=True,
        timeout=timeout,
        creationflags=_NO_WINDOW,
    )


def ffmpeg_version(ffmpeg: Path) -> str:
    """Return the first line of ffmpeg's banner, for display in the interface."""
    try:
        result = _run([ffmpeg, "-hide_banner", "-version"], timeout=20)
    except (OSError, subprocess.SubprocessError) as exc:
        raise ExtractionError(f"Could not run {ffmpeg}: {exc}") from exc
    lines = result.stdout.decode("utf-8", "replace").splitlines()
    return lines[0].strip() if lines else "ffmpeg"


@dataclass
class VideoInfo:
    width: int = 0
    height: int = 0
    duration: float = 0.0
    codec: str = ""

    @property
    def summary(self) -> str:
        if not self.width:
            return "unknown video properties"
        return f"{self.width}x{self.height} {self.codec} ({format_timestamp(self.duration)})"


def probe_video(ffprobe: Path | None, video: Path) -> VideoInfo:
    """Read width, height, codec and duration, returning blanks on failure."""
    if ffprobe is None:
        return VideoInfo()
    cmd = [
        ffprobe, "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height,codec_name",
        "-show_entries", "format=duration",
        "-of", "json", video,
    ]
    try:
        result = _run(cmd, timeout=60)
        payload = json.loads(result.stdout.decode("utf-8", "replace") or "{}")
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError):
        return VideoInfo()

    streams = payload.get("streams") or [{}]
    stream = streams[0]
    try:
        duration = float((payload.get("format") or {}).get("duration") or 0.0)
    except (TypeError, ValueError):
        duration = 0.0
    return VideoInfo(
        width=int(stream.get("width") or 0),
        height=int(stream.get("height") or 0),
        duration=duration,
        codec=str(stream.get("codec_name") or ""),
    )


# ---------------------------------------------------------------------------
# Transcription for videos that arrive without subtitles
# ---------------------------------------------------------------------------

# ffmpeg builds that report --enable-whisper carry whisper.cpp inside them, so
# generating subtitles needs a weights file but no new dependency. Model names
# are listed best-first for discovery.
WHISPER_MODEL_NAMES = (
    "ggml-large-v3-turbo.bin",
    "ggml-large-v3.bin",
    "ggml-large-v2.bin",
    "ggml-medium.en.bin",
    "ggml-medium.bin",
    "ggml-small.en.bin",
    "ggml-small.bin",
    "ggml-base.en.bin",
    "ggml-base.bin",
)

# Voice-activity detection is supported but off by default. It sounds like it
# should help - this tool captures one frame per cue, so cue granularity matters
# - but measured on real tutorial audio it cost roughly 100x the runtime and did
# not produce finer cues than the window setting already gives. Left available
# for audio where silence trimming genuinely helps.
VAD_MODEL_GLOB = "ggml-silero*.bin"


def model_dir() -> Path:
    """Where this tool keeps downloaded speech models."""
    if os.name == "nt":
        root = Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local")
    else:
        root = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache")
    return root / CONFIG_DIR_NAME / "models"


def _model_search_dirs() -> Iterable[Path]:
    bundle = _bundle_dir()
    # The program's own folder comes first. A model sitting beside the
    # executable is the one this copy was given, it keeps the whole thing
    # portable - move the folder and the model moves with it - and it is
    # somewhere an operator can actually see, which a per-user application
    # data directory is not always.
    yield bundle / "models"
    yield bundle
    yield model_dir()
    # Settings live under Roaming while models default to Local, which is right
    # for a file of this size but leaves two identically named folders in two
    # places. Looking beside the settings as well costs nothing.
    yield config_path().parent / "models"
    yield config_path().parent
    if os.name == "nt":
        # Subtitle Edit ships whisper.cpp and its VAD model; reuse rather than
        # ask for a second copy of the same weights.
        appdata = os.environ.get("APPDATA")
        if appdata:
            yield Path(appdata) / "Subtitle Edit" / "SpeechToText" / "Cpp"


def find_whisper_model(preferred: str | os.PathLike[str] | None = None) -> Path | None:
    """Return a whisper.cpp model file, preferring an operator-supplied path."""
    if preferred:
        candidate = Path(preferred).expanduser()
        if candidate.is_file():
            return candidate
    for directory in _model_search_dirs():
        for name in WHISPER_MODEL_NAMES:
            candidate = directory / name
            try:
                if candidate.is_file():
                    return candidate
            except OSError:
                continue
    # Anything else that looks like a whisper model, largest first: a bigger
    # file is the better model within this family.
    for directory in _model_search_dirs():
        try:
            found = [
                path
                for path in directory.glob("ggml-*.bin")
                if path.is_file() and "silero" not in path.name.lower()
            ]
        except OSError:
            continue
        if found:
            return max(found, key=lambda path: path.stat().st_size)
    return None


def find_vad_model(preferred: str | os.PathLike[str] | None = None) -> Path | None:
    """Return a Silero VAD model if one is available."""
    if preferred:
        candidate = Path(preferred).expanduser()
        if candidate.is_file():
            return candidate
    for directory in _model_search_dirs():
        try:
            found = sorted(directory.glob(VAD_MODEL_GLOB))
        except OSError:
            continue
        if found:
            return found[0]
    return None


def diagnostics_report(ffmpeg_hint: str = "", model_hint: str = "") -> str:
    """Describe what this program can and cannot find, from where it is running.

    Shared by --doctor and the interface, because the packaged program has no
    console: without this, a disagreement between the app and a file manager
    leaves nobody able to say which one is right.
    """
    lines = [
        f"{APP_NAME}",
        f"  frozen            {bool(getattr(sys, 'frozen', False))}",
        f"  program directory {_bundle_dir()}",
        f"  LOCALAPPDATA      {os.environ.get('LOCALAPPDATA', '(unset)')}",
        f"  settings file     {config_path()}",
    ]
    ffmpeg = find_ffmpeg(ffmpeg_hint)
    lines.append(f"  ffmpeg            {ffmpeg or '(not found)'}")
    if ffmpeg is not None:
        lines.append(f"  ffprobe           {sibling_ffprobe(ffmpeg) or '(not found)'}")
    lines.append(f"  model directory   {model_dir()}")
    lines.append("  searched for speech models in:")
    for directory in _model_search_dirs():
        try:
            exists = directory.is_dir()
        except OSError as exc:
            lines.append(f"    {directory}  [error: {exc}]")
            continue
        lines.append(f"    {directory}  {'exists' if exists else 'missing'}")
        if not exists:
            continue
        try:
            for entry in sorted(directory.glob("ggml-*.bin")):
                lines.append(f"      found {entry.name}  {entry.stat().st_size} bytes")
        except OSError as exc:
            lines.append(f"      [cannot list: {exc}]")
    lines.append(f"  speech model      {find_whisper_model(model_hint) or '(not found)'}")
    lines.append(f"  voice detection   {find_vad_model() or '(not found)'}")
    return "\n".join(lines)


def escape_filter_path(path: str | os.PathLike[str]) -> str:
    """Quote a path for use inside an ffmpeg filter argument.

    Filter options are split on ':', which every Windows drive letter contains.
    ffmpeg unescapes in two passes, so escaping the colon alone is not enough
    and neither is quoting alone: the value has to be single-quoted *and* the
    colon escaped. Tested against ffmpeg 8.0; the returned value already
    includes its quotes.
    """
    text = str(path).replace("\\", "/")
    text = text.replace("'", r"\'").replace(":", r"\:")
    return f"'{text}'"


def transcribe_subtitles(
    ffmpeg: Path,
    video: Path,
    destination: Path,
    settings: Settings,
    *,
    live_processes: set,
    cancel: threading.Event,
    log: Callable[[str], None] = lambda _message: None,
) -> Path:
    """Write an SRT for ``video`` using ffmpeg's built-in whisper filter."""
    model = find_whisper_model(settings.whisper_model)
    if model is None:
        raise ExtractionError(
            "No speech model found. Put a whisper.cpp ggml-*.bin file in a "
            f"models folder beside the program ({_bundle_dir() / 'models'}), "
            "or set the model path. Run --doctor to see every directory "
            "searched."
        )

    options = [
        f"model={escape_filter_path(model)}",
        f"language={settings.whisper_language or 'auto'}",
        "format=srt",
        f"destination={escape_filter_path(destination)}",
        f"queue={settings.whisper_queue}",
        f"use_gpu={'1' if settings.whisper_gpu else '0'}",
    ]
    vad = find_vad_model(settings.whisper_vad) if settings.whisper_vad_enabled else None
    if vad is not None:
        options.append(f"vad_model={escape_filter_path(vad)}")

    cmd = [
        str(ffmpeg), "-nostdin", "-v", "error",
        "-i", str(video),
        "-vn", "-af", "whisper=" + ":".join(options),
        "-f", "null", "-",
    ]

    log(f"Transcribing with {model.name}{' + VAD' if vad else ''}...")
    destination.parent.mkdir(parents=True, exist_ok=True)

    if cancel.is_set():
        raise ExtractionCancelled
    try:
        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=_NO_WINDOW
        )
    except OSError as exc:
        raise ExtractionError(f"Could not start ffmpeg for transcription: {exc}") from exc

    live_processes.add(process)
    _track(process)
    try:
        # Polled rather than waited on: transcription can run for minutes and
        # a blocking wait would ignore Cancel and the window closing.
        while True:
            try:
                _stdout, stderr = process.communicate(timeout=0.5)
                break
            except subprocess.TimeoutExpired:
                if cancel.is_set():
                    process.kill()
                    process.communicate()
                    raise ExtractionCancelled
    finally:
        live_processes.discard(process)
        _untrack(process)

    if cancel.is_set():
        raise ExtractionCancelled
    if process.returncode != 0 or not destination.is_file():
        detail = stderr.decode("utf-8", "replace").strip().splitlines()
        raise ExtractionError(
            f"Transcription failed: {detail[-1] if detail else process.returncode}"
        )
    return destination


# ---------------------------------------------------------------------------
# Frame capture
# ---------------------------------------------------------------------------


def difference_hash(gray: bytes) -> int | None:
    """Return a 240-bit difference hash for a 16x16 grayscale thumbnail."""
    if len(gray) < VISUAL_EDGE * VISUAL_EDGE:
        return None
    bits = 0
    position = 0
    for row in range(VISUAL_EDGE):
        offset = row * VISUAL_EDGE
        for column in range(VISUAL_EDGE - 1):
            if gray[offset + column] > gray[offset + column + 1]:
                bits |= 1 << position
            position += 1
    return bits


def hamming_distance(left: int, right: int) -> int:
    return (left ^ right).bit_count()


def max_tile_difference(
    previous: bytes,
    current: bytes,
    *,
    width: int = SENSITIVE_WIDTH,
    height: int = SENSITIVE_HEIGHT,
    tiles_x: int = SENSITIVE_TILES_X,
    tiles_y: int = SENSITIVE_TILES_Y,
) -> float | None:
    """Return how much the worst single tile changed between two thumbnails.

    The score is the mean absolute 8-bit difference over the pixels of the
    busiest tile, so it answers "did anywhere on screen change" rather than
    "did the screen as a whole change". Returns None when either thumbnail is
    the wrong size to compare.
    """
    expected = width * height
    if len(previous) < expected or len(current) < expected:
        return None

    tile_width = width // tiles_x
    tile_height = height // tiles_y
    if tile_width < 1 or tile_height < 1:
        return None
    pixels_per_tile = tile_width * tile_height

    worst = 0.0
    for tile_row in range(tiles_y):
        top = tile_row * tile_height
        for tile_column in range(tiles_x):
            left = tile_column * tile_width
            total = 0
            for row in range(top, top + tile_height):
                start = row * width + left
                stop = start + tile_width
                # sum/map run in C; this is the hot loop of the whole mode.
                total += sum(
                    map(abs, map(int.__sub__, previous[start:stop], current[start:stop]))
                )
            score = total / pixels_per_tile
            if score > worst:
                worst = score
    return worst


@dataclass
class Settings:
    """Everything that controls a run, shared by the interface and command line."""

    preset: str = DEFAULT_PRESET
    capture_point: str = "middle"
    offset: float = 0.0
    min_gap: float = 0.0
    max_width: int = 1600
    image_format: str = "jpg"
    quality: int = 85
    dedupe_mode: str = "visual"
    dedupe_threshold: int = 10
    tile_threshold: float = 1.0
    workers: int = 4
    ffmpeg_path: str = ""

    # Speech-to-text for videos that arrive without subtitles. Off unless asked
    # for: a machine transcript is a guess, and this tool's whole output is read
    # downstream as if it were what the instructor said.
    transcribe: bool = False
    whisper_model: str = ""
    whisper_language: str = "auto"
    whisper_vad: str = ""
    # Off by default on measurement, not principle: on this machine enabling
    # voice-activity detection cost 106x the runtime (0.22x realtime against
    # 23x) and did not produce finer cues than the window already gives.
    whisper_vad_enabled: bool = False
    whisper_gpu: bool = True
    # Whisper encodes a 30-second window whatever you feed it, so a small value
    # here repeats that work - but measured on a GPU the repetition is nearly
    # free and the cues are what matter. Over 120s of tutorial audio: window 3
    # gave 44 cues in 6.1s, window 30 gave 26 cues in 4.9s. This tool captures
    # one frame per cue, so 69% more stills for 24% more time is a good trade,
    # and 3 also lands closest to the density of hand-written subtitles.
    whisper_queue: int = 3

    @property
    def dedupe(self) -> bool:
        """Whether any comparison runs at all."""
        return self.dedupe_mode != "off"

    def apply_preset(self, key: str) -> None:
        """Overwrite the preset-owned fields, leaving the rest alone.

        Offset, workers and the ffmpeg path are deliberately untouched: they
        describe the operator's machine and intent, not the material.
        """
        preset = PRESETS.get(key)
        if preset is None:
            raise ExtractionError(f"Unknown preset: {key}")
        self.preset = preset.key
        self.capture_point = preset.capture_point
        self.max_width = preset.max_width
        self.image_format = preset.image_format
        self.quality = preset.quality
        self.dedupe_mode = preset.dedupe_mode
        self.dedupe_threshold = preset.dedupe_threshold
        self.tile_threshold = preset.tile_threshold
        self.min_gap = preset.min_gap

    def validate(self) -> None:
        if self.preset not in PRESETS:
            raise ExtractionError(f"Unknown preset: {self.preset}")
        if self.capture_point not in CAPTURE_POINTS:
            raise ExtractionError(f"Unknown capture point: {self.capture_point}")
        if self.image_format not in IMAGE_FORMATS:
            raise ExtractionError(f"Unknown image format: {self.image_format}")
        if self.dedupe_mode not in DEDUPE_MODES:
            raise ExtractionError(f"Unknown dedupe mode: {self.dedupe_mode}")
        if not 1 <= self.quality <= 100:
            raise ExtractionError("Quality must be between 1 and 100.")
        if self.max_width < 160:
            raise ExtractionError("Maximum width must be at least 160 pixels.")
        if not 0 <= self.dedupe_threshold <= VISUAL_BITS:
            raise ExtractionError(f"Visual threshold must be between 0 and {VISUAL_BITS}.")
        if self.tile_threshold < 0:
            raise ExtractionError("Tile threshold cannot be negative.")
        if not 1 <= self.workers <= 32:
            raise ExtractionError("Workers must be between 1 and 32.")
        if self.min_gap < 0:
            raise ExtractionError("Minimum gap cannot be negative.")
        if self.whisper_queue < 1:
            raise ExtractionError("Transcription window must be at least 1 second.")

    def comparison_details(self) -> dict:
        """Describe, for the manifest, exactly how frames were compared."""
        if self.dedupe_mode == "off":
            return {"mode": "off"}
        if self.dedupe_mode == "sensitive":
            return {
                "mode": "sensitive",
                "method": SENSITIVE_METHOD,
                "thumbnail_width": SENSITIVE_WIDTH,
                "thumbnail_height": SENSITIVE_HEIGHT,
                "tiles_x": SENSITIVE_TILES_X,
                "tiles_y": SENSITIVE_TILES_Y,
                "threshold": self.tile_threshold,
                "units": "mean absolute 8-bit difference of the worst tile",
                "rule": "a frame is dropped when its score is at or below the threshold",
            }
        return {
            "mode": "visual",
            "method": "whole-frame-difference-hash",
            "thumbnail_width": VISUAL_EDGE,
            "thumbnail_height": VISUAL_EDGE,
            "hash_bits": VISUAL_BITS,
            "threshold": self.dedupe_threshold,
            "units": f"hamming distance out of {VISUAL_BITS} bits",
            "rule": "a frame is dropped when its distance is at or below the threshold",
        }


def encoder_arguments(settings: Settings) -> list[str]:
    """Return the ffmpeg codec flags for the chosen image format and quality."""
    if settings.image_format == "jpg":
        # ffmpeg's JPEG qscale runs 2 (best) to 31 (worst), the opposite
        # direction from the percentage the operator sets.
        qscale = round(31 - (settings.quality / 100.0) * 29)
        return ["-q:v", str(max(2, min(31, qscale)))]
    if settings.image_format == "webp":
        # Quality 100 means "give me the pixels back", which for WebP is a
        # distinct mode rather than the top of the lossy scale. It lands about
        # a quarter smaller than the equivalent PNG.
        if settings.quality >= 100:
            return ["-lossless", "1"]
        return ["-quality", str(settings.quality)]
    return ["-compression_level", "6"]


@dataclass
class FrameResult:
    cue: Cue
    timestamp: float
    path: Path | None = None
    phash: int | None = None
    gray: bytes | None = None
    error: str = ""


def capture_frame(
    ffmpeg: Path,
    video: Path,
    timestamp: float,
    destination: Path,
    settings: Settings,
    live_processes: set,
    cancel: threading.Event,
) -> tuple[Path | None, int | None, bytes | None, str]:
    """Write one frame and return it with whatever the dedupe mode compares.

    A single ffmpeg invocation produces both outputs from one decode: the frame
    itself, and a small grayscale thumbnail on stdout used only to compare this
    frame against the previous one. Visual mode wants a 16x16 thumbnail it can
    reduce to a hash; sensitive mode wants the larger tiled thumbnail kept whole.
    """
    scale = f"scale='min({settings.max_width},iw)':-2:flags=lanczos"
    cmd = [
        str(ffmpeg), "-nostdin", "-v", "error",
        "-ss", f"{timestamp:.3f}", "-i", str(video),
        "-frames:v", "1", "-vf", scale, *encoder_arguments(settings),
        "-y", str(destination),
    ]
    if settings.dedupe_mode == "sensitive":
        thumbnail = f"{SENSITIVE_WIDTH}:{SENSITIVE_HEIGHT}"
    elif settings.dedupe_mode == "visual":
        thumbnail = f"{VISUAL_EDGE}:{VISUAL_EDGE}"
    else:
        thumbnail = ""
    if thumbnail:
        cmd += [
            "-frames:v", "1",
            "-vf", f"scale={thumbnail}:flags=area,format=gray",
            "-pix_fmt", "gray", "-f", "rawvideo", "-y", "-",
        ]

    if cancel.is_set():
        raise ExtractionCancelled

    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=_NO_WINDOW,
        )
    except OSError as exc:
        return None, None, None, f"could not start ffmpeg: {exc}"

    live_processes.add(process)
    _track(process)
    try:
        stdout, stderr = process.communicate(timeout=FRAME_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        process.kill()
        process.communicate()
        return None, None, None, "ffmpeg timed out"
    finally:
        live_processes.discard(process)
        _untrack(process)

    if cancel.is_set():
        raise ExtractionCancelled

    if process.returncode != 0 or not destination.exists():
        detail = stderr.decode("utf-8", "replace").strip().splitlines()
        message = detail[-1] if detail else f"ffmpeg exited {process.returncode}"
        return None, None, None, message

    if settings.dedupe_mode == "visual":
        return destination, difference_hash(stdout), None, ""
    if settings.dedupe_mode == "sensitive":
        return destination, None, stdout, ""
    return destination, None, None, ""


# ---------------------------------------------------------------------------
# Bundle assembly
# ---------------------------------------------------------------------------


@dataclass
class RunReport:
    output: Path
    cue_count: int = 0
    planned: int = 0
    kept: int = 0
    duplicates: int = 0
    failures: list[str] = field(default_factory=list)


def plan_captures(
    cues: Sequence[Cue], settings: Settings, info: VideoInfo
) -> list[tuple[Cue, float]]:
    """Choose which cues get a frame, honouring the minimum gap and duration."""
    limit = info.duration - 0.05 if info.duration > 0.1 else None
    planned: list[tuple[Cue, float]] = []
    last_kept: float | None = None
    for cue in cues:
        timestamp = cue.capture_time(settings.capture_point, settings.offset)
        if limit is not None:
            timestamp = min(timestamp, limit)
        if last_kept is not None and timestamp - last_kept < settings.min_gap:
            continue
        planned.append((cue, timestamp))
        last_kept = timestamp
    return planned


def build_transcript(
    title: str,
    info: VideoInfo,
    settings: Settings,
    cues: Sequence[Cue],
    frame_for_cue: dict[int, str],
    *,
    transcribed: bool = False,
) -> str:
    """Render the interleaved transcript that a reading session actually reads."""
    offset_note = f", offset {settings.offset:+.2f}s" if settings.offset else ""
    lines = [
        f"# {title}",
        "",
        f"Source video: `{title}` — {info.summary}",
        f"Frames captured at the {settings.capture_point} of each subtitle cue{offset_note}.",
        f"Preset: {PRESETS[settings.preset].label if settings.preset in PRESETS else settings.preset}"
        f" · comparison: {settings.dedupe_mode}",
        "",
        "Every spoken line is kept below. A frame appears whenever the picture",
        "changed enough to be worth looking at; the lines under it were spoken",
        "while that frame was on screen.",
        "",
    ]
    if transcribed:
        lines += [
            "> **The words below are a machine transcription.** This video had no",
            "> subtitles, so the speech was recognised automatically. Treat the text",
            "> as an approximation, especially for names, APIs and technical terms;",
            "> the pictures are exact, the words are not.",
            "",
        ]
    lines.append("---")

    current_frame: str | None = None
    for cue in cues:
        frame = frame_for_cue.get(cue.index)
        if frame and frame != current_frame:
            current_frame = frame
            lines += [
                "",
                f"## {format_timestamp(cue.start)} — {Path(frame).name}",
                "",
                f"![{format_timestamp(cue.start)}]({frame})",
                "",
            ]
        stamp = f"{format_timestamp(cue.start)} → {format_timestamp(cue.end)}"
        lines.append(f"- `{stamp}` {cue.text}")

    lines.append("")
    return "\n".join(lines)


def extract_bundle(
    video: Path,
    subtitles: Path | None,
    output: Path,
    settings: Settings,
    *,
    log: Callable[[str], None] = lambda _message: None,
    progress: Callable[[int, int], None] = lambda _done, _total: None,
    cancel: threading.Event | None = None,
) -> RunReport:
    """Capture frames for every cue and write the study bundle to ``output``."""
    cancel = cancel or threading.Event()
    settings.validate()

    if not video.is_file():
        raise ExtractionError(f"Video not found: {video}")

    ffmpeg = find_ffmpeg(settings.ffmpeg_path)
    if ffmpeg is None:
        raise ExtractionError(
            "ffmpeg was not found. Install it, or point the tool at ffmpeg.exe."
        )
    ffmpeg_banner = ffmpeg_version(ffmpeg)
    log(f"Using {ffmpeg_banner}")

    live: set = set()
    transcribed = False
    if subtitles is None or not subtitles.is_file():
        if not settings.transcribe:
            raise ExtractionError(
                f"Subtitle file not found: {subtitles}"
                if subtitles is not None
                else f"No subtitles found for {video.name}."
            )
        # Kept beside the bundle rather than beside the source video: the
        # archive is the operator's, and a rerun can reuse this without paying
        # for the transcription again.
        generated = output.with_name(f"{output.stem}.srt")
        if generated.is_file():
            log(f"Reusing generated subtitles: {generated.name}")
        else:
            transcribe_subtitles(
                ffmpeg, video, generated, settings,
                live_processes=live, cancel=cancel, log=log,
            )
        subtitles = generated
        transcribed = True

    info = probe_video(sibling_ffprobe(ffmpeg), video)
    log(f"Video: {info.summary}")

    cues = parse_srt(subtitles)
    log(f"Subtitles: {len(cues)} cues")

    planned = plan_captures(cues, settings, info)
    if settings.min_gap:
        log(f"Minimum gap of {settings.min_gap:g}s leaves {len(planned)} capture points")

    report = RunReport(output=output, cue_count=len(cues), planned=len(planned))

    stem = re.sub(r"[^\w\-. ]+", "_", video.stem).strip() or "video"
    staging = output.parent / f".{output.stem}.frames.tmp"
    if staging.exists():
        shutil.rmtree(staging, ignore_errors=True)
    staging.mkdir(parents=True, exist_ok=True)

    results: list[FrameResult] = []

    def work(item: tuple[int, tuple[Cue, float]]) -> FrameResult:
        position, (cue, timestamp) = item
        name = (
            f"{position + 1:04d}_"
            f"{format_timestamp(timestamp, for_filename=True)}.{settings.image_format}"
        )
        path, phash, gray, error = capture_frame(
            ffmpeg, video, timestamp, staging / name, settings, live, cancel
        )
        return FrameResult(
            cue=cue, timestamp=timestamp, path=path, phash=phash, gray=gray, error=error
        )

    try:
        progress(0, len(planned))
        with ThreadPoolExecutor(max_workers=settings.workers) as pool:
            try:
                for done, result in enumerate(pool.map(work, enumerate(planned)), start=1):
                    results.append(result)
                    if result.error:
                        report.failures.append(
                            f"{format_timestamp(result.timestamp)}: {result.error}"
                        )
                    progress(done, len(planned))
            except ExtractionCancelled:
                for process in list(live):
                    process.kill()
                raise

        if cancel.is_set():
            raise ExtractionCancelled

        # Deduplication runs in cue order, so "the same as the one before" means
        # the previous kept frame rather than whichever worker finished first.
        kept: list[FrameResult] = []
        previous_hash: int | None = None
        previous_gray: bytes | None = None
        for result in results:
            if result.path is None:
                continue
            if settings.dedupe_mode == "visual":
                if previous_hash is not None and result.phash is not None:
                    distance = hamming_distance(previous_hash, result.phash)
                    if distance <= settings.dedupe_threshold:
                        report.duplicates += 1
                        continue
            elif settings.dedupe_mode == "sensitive":
                if previous_gray is not None and result.gray is not None:
                    score = max_tile_difference(previous_gray, result.gray)
                    if score is not None and score <= settings.tile_threshold:
                        report.duplicates += 1
                        continue
            if result.phash is not None:
                previous_hash = result.phash
            if result.gray is not None:
                previous_gray = result.gray
            kept.append(result)

        # The thumbnails existed only for the comparison above; a long video
        # holds a lot of them.
        for result in results:
            result.gray = None

        report.kept = len(kept)
        if settings.dedupe:
            log(
                f"Kept {len(kept)} frames, dropped {report.duplicates} near-duplicates "
                f"({settings.dedupe_mode} comparison)"
            )

        frame_for_cue = {
            result.cue.index: f"frames/{result.path.name}"
            for result in kept
            if result.path
        }
        transcript = build_transcript(
            video.stem, info, settings, cues, frame_for_cue, transcribed=transcribed
        )
        manifest = {
            "tool": APP_NAME,
            "ffmpeg": ffmpeg_banner,
            "video": {
                "name": video.name,
                "width": info.width,
                "height": info.height,
                "codec": info.codec,
                "duration_seconds": round(info.duration, 3),
            },
            "subtitles": {
                "name": subtitles.name,
                "cue_count": len(cues),
                # Flagged because everything downstream reads this text as if
                # it were what the instructor said. A machine transcript is a
                # guess, and a reader deserves to know which one it has.
                "machine_generated": transcribed,
                "transcribed_with": (
                    getattr(find_whisper_model(settings.whisper_model), "name", "")
                    if transcribed
                    else ""
                ),
            },
            "settings": {
                "preset": settings.preset,
                "capture_point": settings.capture_point,
                "offset_seconds": settings.offset,
                "min_gap_seconds": settings.min_gap,
                "max_width": settings.max_width,
                "image_format": settings.image_format,
                "quality": settings.quality,
                "encoder_arguments": encoder_arguments(settings),
                "dedupe": settings.dedupe,
                "dedupe_mode": settings.dedupe_mode,
                "dedupe_threshold": settings.dedupe_threshold,
                "tile_threshold": settings.tile_threshold,
            },
            "comparison": settings.comparison_details(),
            "counts": {
                "cues": len(cues),
                "planned": len(planned),
                "frames": len(kept),
                "near_duplicates_dropped": report.duplicates,
                "failures": len(report.failures),
            },
            "frames": [
                {
                    "file": f"frames/{result.path.name}",
                    "timestamp": format_timestamp(result.timestamp),
                    "timestamp_seconds": round(result.timestamp, 3),
                    "cue_index": result.cue.index,
                    "cue_start": format_timestamp(result.cue.start),
                    "cue_end": format_timestamp(result.cue.end),
                    "text": result.cue.text,
                }
                for result in kept
                if result.path
            ],
            "failures": report.failures,
        }

        output.parent.mkdir(parents=True, exist_ok=True)
        log(f"Writing {output.name}")
        with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
            for result in kept:
                if result.path is None:
                    continue
                # Images are already compressed; storing them is faster and the
                # same size.
                archive.write(
                    result.path,
                    f"{stem}/frames/{result.path.name}",
                    compress_type=zipfile.ZIP_STORED,
                )
            archive.writestr(f"{stem}/{subtitles.name}", subtitles.read_bytes())
            archive.writestr(f"{stem}/transcript.md", transcript)
            archive.writestr(
                f"{stem}/manifest.json",
                json.dumps(manifest, indent=2, ensure_ascii=False),
            )
    finally:
        shutil.rmtree(staging, ignore_errors=True)

    return report


# ---------------------------------------------------------------------------
# Settings persistence
# ---------------------------------------------------------------------------


def config_path() -> Path:
    if os.name == "nt":
        root = Path(os.environ.get("APPDATA") or Path.home() / "AppData" / "Roaming")
    else:
        root = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
    return root / CONFIG_DIR_NAME / "config.json"


def load_config() -> dict:
    try:
        return json.loads(config_path().read_text("utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def save_config(data: dict) -> None:
    path = config_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2), "utf-8")
    except OSError:
        pass


def subtitle_candidates(video: Path) -> list[Path]:
    """Return every subtitle file that could belong to this video, best first.

    Archives name these inconsistently: `lesson.srt`, `lesson.en.srt` and
    `lesson.en-x-autogen.srt` all occur, sometimes with a .vtt beside them. The
    ordering below is what makes an unattended batch pick the same file a person
    would: an exact stem beats a language-tagged one, SubRip beats WebVTT, and
    English beats whatever else is lying around.
    """
    stem = video.stem
    found: list[Path] = []
    try:
        siblings = sorted(video.parent.iterdir())
    except OSError:
        return []

    for path in siblings:
        if not path.is_file() or path.suffix.lower() not in (".srt", ".vtt"):
            continue
        name = path.name
        if not name.lower().startswith(stem.lower()):
            continue
        # The part between the video's stem and the extension, e.g. ".en".
        middle = name[len(stem):-len(path.suffix)].lower()
        if middle and not middle.startswith("."):
            continue  # a different lesson that merely shares a prefix
        found.append(path)

    def rank(path: Path) -> tuple:
        middle = path.name[len(stem):-len(path.suffix)].lower()
        return (
            0 if path.suffix.lower() == ".srt" else 1,
            0 if middle == "" else (1 if middle.startswith(".en") else 2),
            len(middle),
            path.name.lower(),
        )

    return sorted(found, key=rank)


def guess_subtitles(video: Path) -> Path | None:
    """Return the subtitle file sitting beside a video, if there is one."""
    candidates = subtitle_candidates(video)
    return candidates[0] if candidates else None


def default_output(video: Path) -> Path:
    return video.parent / f"{video.stem}.stills.zip"


# ---------------------------------------------------------------------------
# Batch runs
# ---------------------------------------------------------------------------


@dataclass
class BatchItem:
    """One video queued for conversion, and where its bundle will land."""

    video: Path
    subtitles: Path | None
    output: Path
    skip_reason: str = ""

    @property
    def ready(self) -> bool:
        # Missing subtitles only disqualify an item when transcription is off;
        # find_batch_items records that in skip_reason.
        return not self.skip_reason


@dataclass
class BatchOutcome:
    item: BatchItem
    status: str  # done | skipped | failed
    detail: str = ""
    cues: int = 0
    frames: int = 0
    duplicates: int = 0


@dataclass
class BatchReport:
    destination: Path
    outcomes: list[BatchOutcome] = field(default_factory=list)
    cancelled: bool = False

    def _count(self, status: str) -> int:
        return sum(1 for outcome in self.outcomes if outcome.status == status)

    @property
    def done(self) -> int:
        return self._count("done")

    @property
    def skipped(self) -> int:
        return self._count("skipped")

    @property
    def failed(self) -> int:
        return self._count("failed")

    @property
    def frames(self) -> int:
        return sum(outcome.frames for outcome in self.outcomes)

    def summary(self) -> str:
        parts = [f"{self.done} converted"]
        if self.skipped:
            parts.append(f"{self.skipped} skipped")
        if self.failed:
            parts.append(f"{self.failed} failed")
        parts.append(f"{self.frames} frames in total")
        return ", ".join(parts)


def batch_destination(source: Path, chosen: Path) -> Path:
    """Where a batch of videos under ``source`` actually writes its bundles.

    A chosen folder gains the source folder's own name, so "D:/Exports" for a
    course called "C++ Multiplayer Shooter" writes to
    "D:/Exports/C++ Multiplayer Shooter/..." and the export folder can take
    course after course without the sections of one landing among another's.

    A destination already inside the source keeps the name off, because there
    it would only repeat the folder it sits in.
    """
    source = source.expanduser()
    chosen = chosen.expanduser()
    try:
        chosen.resolve().relative_to(source.resolve())
    except (ValueError, OSError):
        return chosen / source.name
    return chosen


def find_batch_items(
    source: Path,
    destination: Path,
    *,
    recursive: bool = True,
    skip_existing: bool = True,
    transcribe: bool = False,
) -> list[BatchItem]:
    """List every video under ``source`` with the bundle it would produce.

    The destination mirrors the source's folder structure, because course
    archives reuse names like "1. Introduction" in every section and a flat
    output directory would have them overwrite each other.
    """
    source = source.expanduser()
    destination = destination.expanduser()

    videos = [
        path
        for path in (source.rglob("*") if recursive else source.glob("*"))
        if path.is_file() and path.suffix.lower() in VIDEO_SUFFIXES
    ]
    videos.sort()

    items: list[BatchItem] = []
    for video in videos:
        try:
            relative = video.parent.relative_to(source)
        except ValueError:
            relative = Path()
        output = destination / relative / f"{video.stem}.stills.zip"
        subtitles = guess_subtitles(video)
        if skip_existing and output.exists():
            reason = "already built"
        elif subtitles is None and not transcribe:
            reason = "no subtitles alongside it"
        else:
            reason = ""
        items.append(BatchItem(video, subtitles, output, reason))
    return items


def extract_batch(
    items: Sequence[BatchItem],
    settings: Settings,
    destination: Path,
    *,
    log: Callable[[str], None] = lambda _message: None,
    on_item: Callable[[int, int, BatchItem], None] = lambda _i, _n, _item: None,
    progress: Callable[[int, int], None] = lambda _done, _total: None,
    cancel: threading.Event | None = None,
    write_report: bool = True,
) -> BatchReport:
    """Convert every ready item, surviving anything one bad file can do.

    A batch is worth little if a single unreadable video ends the run, so each
    item's failure is recorded and the queue continues. Cancellation is the one
    thing that stops it.
    """
    cancel = cancel or threading.Event()
    settings.validate()
    report = BatchReport(destination=destination)
    total = len(items)

    for index, item in enumerate(items, start=1):
        if cancel.is_set():
            report.cancelled = True
            break

        on_item(index, total, item)

        if not item.ready:
            report.outcomes.append(
                BatchOutcome(item=item, status="skipped", detail=item.skip_reason)
            )
            log(f"[{index}/{total}] skipped {item.video.name} - {item.skip_reason}")
            continue

        try:
            item.output.parent.mkdir(parents=True, exist_ok=True)
            result = extract_bundle(
                item.video,
                item.subtitles,
                item.output,
                settings,
                log=lambda message: None,  # per-frame chatter would drown the queue
                progress=progress,
                cancel=cancel,
            )
        except ExtractionCancelled:
            report.cancelled = True
            break
        except ExtractionError as exc:
            report.outcomes.append(
                BatchOutcome(item=item, status="failed", detail=str(exc))
            )
            log(f"[{index}/{total}] FAILED {item.video.name} - {exc}")
            continue
        except Exception as exc:  # one broken file must not end the queue
            report.outcomes.append(
                BatchOutcome(item=item, status="failed", detail=repr(exc))
            )
            log(f"[{index}/{total}] FAILED {item.video.name} - {exc!r}")
            continue

        # An unreadable video does not raise: every capture fails individually
        # and an empty bundle gets written. In a queue of hundreds that would
        # pass by unnoticed, so call it what it is.
        empty = result.kept == 0 and bool(result.failures)
        report.outcomes.append(
            BatchOutcome(
                item=item,
                status="failed" if empty else "done",
                detail=f"no frames captured ({result.failures[0]})" if empty else "",
                cues=result.cue_count,
                frames=result.kept,
                duplicates=result.duplicates,
            )
        )
        if empty:
            log(f"[{index}/{total}] FAILED {item.video.name} - no frames captured")
        else:
            log(
                f"[{index}/{total}] {item.video.name} - {result.kept} frames "
                f"from {result.cue_count} cues"
            )

    if write_report:
        write_batch_report(report, settings)
    return report


def write_batch_report(report: BatchReport, settings: Settings) -> Path | None:
    """Record what the batch did, beside its output."""
    payload = {
        "tool": APP_NAME,
        "destination": str(report.destination),
        "cancelled": report.cancelled,
        "settings": {
            "preset": settings.preset,
            "capture_point": settings.capture_point,
            "offset_seconds": settings.offset,
            "min_gap_seconds": settings.min_gap,
            "max_width": settings.max_width,
            "image_format": settings.image_format,
            "quality": settings.quality,
            "dedupe_mode": settings.dedupe_mode,
            "dedupe_threshold": settings.dedupe_threshold,
            "tile_threshold": settings.tile_threshold,
        },
        "comparison": settings.comparison_details(),
        "counts": {
            "total": len(report.outcomes),
            "done": report.done,
            "skipped": report.skipped,
            "failed": report.failed,
            "frames": report.frames,
        },
        "items": [
            {
                "video": str(outcome.item.video),
                "subtitles": str(outcome.item.subtitles) if outcome.item.subtitles else None,
                "output": str(outcome.item.output),
                "status": outcome.status,
                "detail": outcome.detail,
                "cues": outcome.cues,
                "frames": outcome.frames,
                "near_duplicates_dropped": outcome.duplicates,
            }
            for outcome in report.outcomes
        ],
    }
    path = report.destination / "batch_report.json"
    try:
        report.destination.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), "utf-8")
    except OSError:
        return None
    return path


# ---------------------------------------------------------------------------
# Command line
# ---------------------------------------------------------------------------


def run_cli(argv: Sequence[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="extract_video_stills",
        description="Capture one frame per subtitle cue and zip them with the transcript.",
    )
    parser.add_argument("video", nargs="?", type=Path)
    parser.add_argument("subtitles", nargs="?", type=Path)
    parser.add_argument("-o", "--output", type=Path)
    # Every preset-owned option defaults to None so that "not given" can be told
    # from "given". The preset fills the blanks and explicit flags win, which
    # keeps a command line with no --preset identical to the original defaults.
    parser.add_argument(
        "--preset",
        choices=tuple(PRESETS),
        default=DEFAULT_PRESET,
        help="starting point for the frame settings; explicit flags override it",
    )
    parser.add_argument("--at", choices=CAPTURE_POINTS, default=None)
    parser.add_argument("--offset", type=float, default=0.0, metavar="SECONDS")
    parser.add_argument("--min-gap", type=float, default=None, metavar="SECONDS")
    parser.add_argument("--max-width", type=int, default=None, metavar="PIXELS")
    parser.add_argument(
        "--format", choices=IMAGE_FORMATS, default=None, dest="image_format"
    )
    parser.add_argument("--quality", type=int, default=None, metavar="1-100")
    parser.add_argument(
        "--dedupe",
        choices=DEDUPE_MODES,
        default=None,
        dest="dedupe_mode",
        help=(
            "visual: compare whole frames, good when most of the picture moves. "
            "sensitive: compare screen tiles, keeps a frame when one region "
            "changes. off: keep every capture."
        ),
    )
    parser.add_argument(
        "--no-dedupe", action="store_true", help="shorthand for --dedupe off"
    )
    parser.add_argument(
        "--sensitivity",
        type=int,
        default=None,
        metavar="BITS",
        help=(
            f"visual-mode threshold, 0-{VISUAL_BITS} hamming bits; "
            "higher drops more frames"
        ),
    )
    parser.add_argument(
        "--tile-threshold",
        type=float,
        default=None,
        metavar="SCORE",
        help=(
            "sensitive-mode threshold as mean absolute difference of the worst "
            "tile; static frames score near 0.2 and small real edits near 3"
        ),
    )
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--ffmpeg", default="", metavar="PATH")
    parser.add_argument(
        "--list-presets", action="store_true", help="describe the presets and exit"
    )
    parser.add_argument(
        "--doctor",
        action="store_true",
        help="report what the tool can and cannot find, then exit",
    )

    batch = parser.add_argument_group(
        "batch", "used when VIDEO is a folder rather than a file"
    )
    batch.add_argument(
        "--no-recursive", action="store_true", help="do not descend into subfolders"
    )
    batch.add_argument(
        "--redo",
        action="store_true",
        help="rebuild bundles that already exist instead of skipping them",
    )
    batch.add_argument(
        "--dry-run",
        action="store_true",
        help="list what would be converted, then stop",
    )

    speech = parser.add_argument_group(
        "speech", "for videos that arrive without subtitles"
    )
    speech.add_argument(
        "--transcribe",
        action="store_true",
        help="generate subtitles with ffmpeg's built-in whisper filter",
    )
    speech.add_argument(
        "--whisper-model", default=None, metavar="PATH",
        help="a whisper.cpp ggml-*.bin file; found automatically if not given",
    )
    speech.add_argument(
        "--language", default=None, metavar="CODE",
        help="spoken language, e.g. 'en'; 'auto' to detect (default auto)",
    )
    speech.add_argument(
        "--whisper-window", type=int, default=None, metavar="SECONDS",
        help="audio processed per pass; whisper always encodes 30s, so small "
             "values cost far more time for the same audio",
    )
    speech.add_argument(
        "--no-gpu", action="store_true", help="transcribe on the CPU"
    )
    speech.add_argument(
        "--vad",
        action="store_true",
        help="enable voice-activity detection; far slower, rarely worth it",
    )
    args = parser.parse_args(list(argv))

    if args.doctor:
        print(diagnostics_report(args.ffmpeg, args.whisper_model or ""))
        return 0

    if args.list_presets:
        for preset in PRESETS.values():
            print(f"{preset.key:<11} {preset.label}")
            print(f"            {preset.summary}")
            print(
                f"            capture={preset.capture_point} width={preset.max_width} "
                f"format={preset.image_format} quality={preset.quality} "
                f"dedupe={preset.dedupe_mode} "
                f"threshold={preset.dedupe_threshold if preset.dedupe_mode == 'visual' else preset.tile_threshold}"
            )
        return 0

    # Cue text and filenames routinely carry characters the Windows console
    # codepage cannot encode, and a traceback there would lose a finished run.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError, ValueError):
            pass

    if args.video is None:
        parser.error("the following arguments are required: video")

    source = args.video.expanduser()

    settings = Settings(
        offset=args.offset, workers=args.workers, ffmpeg_path=args.ffmpeg
    )
    settings.apply_preset(args.preset)
    for attribute, value in (
        ("capture_point", args.at),
        ("min_gap", args.min_gap),
        ("max_width", args.max_width),
        ("image_format", args.image_format),
        ("quality", args.quality),
        ("dedupe_mode", args.dedupe_mode),
        ("dedupe_threshold", args.sensitivity),
        ("tile_threshold", args.tile_threshold),
    ):
        if value is not None:
            setattr(settings, attribute, value)
    if args.no_dedupe:
        settings.dedupe_mode = "off"
    for attribute, value in (
        ("whisper_model", args.whisper_model),
        ("whisper_language", args.language),
        ("whisper_queue", args.whisper_window),
    ):
        if value is not None:
            setattr(settings, attribute, value)
    if args.transcribe:
        settings.transcribe = True
    if args.no_gpu:
        settings.whisper_gpu = False
    if args.vad:
        settings.whisper_vad_enabled = True

    if source.is_dir():
        return _run_batch_cli(source, args, settings)
    return _run_single_cli(source, args, settings, parser)


def _run_single_cli(video: Path, args, settings: Settings, parser) -> int:
    subtitles = args.subtitles.expanduser() if args.subtitles else guess_subtitles(video)
    if subtitles is None:
        parser.error("No subtitle file given and none found beside the video.")
    output = (args.output or default_output(video)).expanduser()

    live = bool(getattr(sys.stdout, "isatty", lambda: False)())

    def show_progress(done: int, total: int) -> None:
        if total and live:
            print(f"\r  {done}/{total} frames", end="", flush=True)
            if done == total:
                print()

    try:
        report = extract_bundle(
            video, subtitles, output, settings, log=print, progress=show_progress
        )
    except ExtractionError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(
        f"Wrote {report.output} "
        f"({report.kept} frames from {report.cue_count} cues, "
        f"{report.duplicates} near-duplicates dropped)"
    )
    for failure in report.failures:
        print(f"  failed: {failure}", file=sys.stderr)
    return 0


def _run_batch_cli(source: Path, args, settings: Settings) -> int:
    chosen = (args.output or source / "_stills").expanduser()
    destination = batch_destination(source, chosen)
    items = find_batch_items(
        source,
        destination,
        recursive=not args.no_recursive,
        skip_existing=not args.redo,
        transcribe=settings.transcribe,
    )
    if not items:
        print(f"No video files found under {source}", file=sys.stderr)
        return 2

    ready = sum(1 for item in items if item.ready)
    print(f"{len(items)} videos under {source}")
    print(f"  {ready} to convert, {len(items) - ready} skipped")
    print(f"  preset {settings.preset}, output {destination}")

    if args.dry_run:
        for item in items:
            mark = "convert" if item.ready else f"skip: {item.skip_reason}"
            try:
                shown = item.video.relative_to(source)
            except ValueError:
                shown = item.video
            print(f"  [{mark}] {shown}")
        return 0

    if not ready:
        print("Nothing to do.")
        return 0

    # Carriage-return progress is for a terminal. Redirected to a file or a log
    # it just produces thousands of useless lines, so it is suppressed there.
    live = bool(getattr(sys.stdout, "isatty", lambda: False)())

    def emit(message: str) -> None:
        # Clear the transient frame counter before writing a permanent line.
        print(("\r" + " " * 64 + "\r" if live else "") + message, flush=True)

    def show_progress(done: int, total: int) -> None:
        if total and live:
            print(f"\r    frames {done}/{total}", end="", flush=True)

    try:
        report = extract_batch(
            items, settings, destination,
            log=emit, progress=show_progress,
        )
    except ExtractionError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    emit(report.summary() + (" (cancelled)" if report.cancelled else ""))
    for outcome in report.outcomes:
        if outcome.status == "failed":
            print(f"  failed: {outcome.item.video.name}: {outcome.detail}", file=sys.stderr)
    print(f"Report: {destination / 'batch_report.json'}")
    return 1 if report.failed else 0


# ---------------------------------------------------------------------------
# Graphical interface
# ---------------------------------------------------------------------------


def run_gui() -> int:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk

    config = load_config()

    root = tk.Tk()
    root.title(APP_NAME)
    root.minsize(760, 800)
    try:
        # Enough sections have accumulated that 1.3 pushed the log off a 1080p
        # screen; this keeps the whole form visible with room left to read it.
        root.call("tk", "scaling", 1.15)
    except tk.TclError:
        pass

    video_var = tk.StringVar()
    subtitle_var = tk.StringVar()
    output_var = tk.StringVar()
    ffmpeg_var = tk.StringVar(value=config.get("ffmpeg_path", ""))
    ffmpeg_status = tk.StringVar(value="Looking for ffmpeg...")

    # A config written by an earlier build stored dedupe as a plain on/off flag.
    stored_mode = config.get("dedupe_mode")
    if stored_mode not in DEDUPE_MODES:
        stored_mode = "visual" if config.get("dedupe", True) else "off"

    preset_var = tk.StringVar()
    preset_summary = tk.StringVar()
    capture_var = tk.StringVar(value=config.get("capture_point", "middle"))
    offset_var = tk.DoubleVar(value=config.get("offset", 0.0))
    gap_var = tk.DoubleVar(value=config.get("min_gap", 0.0))
    width_var = tk.IntVar(value=config.get("max_width", 1600))
    format_var = tk.StringVar(value=config.get("image_format", "jpg"))
    quality_var = tk.IntVar(value=config.get("quality", 85))
    dedupe_mode_var = tk.StringVar(value=stored_mode)
    sensitivity_var = tk.IntVar(value=config.get("dedupe_threshold", 10))
    tile_var = tk.DoubleVar(value=config.get("tile_threshold", 1.0))
    workers_var = tk.IntVar(value=config.get("workers", 4))

    batch_source_var = tk.StringVar(value=config.get("last_batch_source", ""))
    batch_output_var = tk.StringVar(value=config.get("last_batch_output", ""))
    recursive_var = tk.BooleanVar(value=config.get("batch_recursive", True))
    skip_existing_var = tk.BooleanVar(value=config.get("batch_skip_existing", True))
    batch_summary = tk.StringVar(value="Choose a folder and scan it.")

    transcribe_var = tk.BooleanVar(value=config.get("transcribe", False))
    whisper_model_var = tk.StringVar(value=config.get("whisper_model", ""))
    language_var = tk.StringVar(value=config.get("whisper_language", "auto"))
    whisper_status = tk.StringVar(value="")

    status_var = tk.StringVar(value="Choose a video and its subtitles.")
    cancel_event = threading.Event()
    worker: threading.Thread | None = None
    running_batch = [False]

    frame = ttk.Frame(root, padding=12)
    frame.pack(fill="both", expand=True)
    frame.columnconfigure(0, weight=1)

    HELP = {
        "Input": (
            "Single file - pick a video and the subtitle file that goes with "
            "it. Choosing a video fills in a matching .srt sitting beside it "
            "and a default name for the output zip, if it can find them.\n\n"
            "Batch folder - point at a folder and convert everything under it "
            "in one run, using the settings below for every video. Scan reports "
            "what it found before you commit to it. The bundles go into a "
            "folder named after the source, inside the one you pick, holding a "
            "copy of its subfolder structure: pick D:/Exports for a course "
            "called 'C++ Multiplayer Shooter' and everything lands under "
            "D:/Exports/C++ Multiplayer Shooter. The structure is copied because "
            "courses reuse names like '1. Introduction' in every section and a "
            "flat folder would have them overwrite each other; the source is "
            "named so one export folder can hold course after course. Leave the "
            "output folder empty and it writes to a _stills folder inside the "
            "source instead.\n\n"
            "A video with no subtitle file beside it is skipped and named in "
            "the log; it does not stop the run, and neither does a file that "
            "fails to decode. 'Skip already built' lets you stop a long run and "
            "resume it later without redoing finished work. A batch_report.json "
            "in the output folder lists every video, its status and its frame "
            "count.\n\n"
            "Each zip contains the captured frames, your original subtitle file "
            "untouched, a transcript.md with the frames and the speech "
            "interleaved in order, and a manifest.json recording exactly which "
            "settings produced it.\n\n"
            "Nothing here alters the source files."
        ),
        "Content preset": (
            "A starting point for the settings below, chosen to match the kind "
            "of material you are capturing.\n\n"
            "The presets differ mainly in how hard they try to avoid keeping two "
            "frames that show the same thing. A VFX shot changes across the whole "
            "screen between cues, so a cheap whole-picture comparison works. A "
            "Blueprint graph or an IDE changes in one small corner, which that "
            "same comparison cannot see at all.\n\n"
            "Choosing a preset only fills the controls in. Change anything you "
            "like afterwards and your change is what runs; the preset is not "
            "consulted again."
        ),
        "Frames": (
            "Capture at - which moment inside each subtitle cue to grab. "
            "'middle' is safest for visual material because it avoids landing on "
            "a cut. 'end' suits code and node graphs, where the instructor "
            "usually finishes the edit while still describing it.\n\n"
            "Offset - shifts every capture by this many seconds. Negative values "
            "capture earlier.\n\n"
            "Min gap - skips a cue when its capture would fall less than this "
            "many seconds after the previous one. Useful for rapid-fire "
            "subtitles. The skipped cue's words still appear in the transcript.\n\n"
            "Max width - frames are never enlarged, so this only takes effect on "
            "sources wider than the value. Text has to survive this downscale to "
            "be readable later, which is why the code and Blueprint presets set "
            "it high.\n\n"
            "Format and quality - PNG is lossless and best for small text and "
            "thin wires. JPEG is much smaller and fine for photographic or "
            "heavily shaded material. Quality is ignored for PNG.\n\n"
            "Parallel workers - how many ffmpeg processes run at once."
        ),
        "Comparison": (
            "How the tool decides that a frame shows nothing new and can be "
            "dropped. Each frame is compared against the last frame that was "
            "kept, never against one that was already discarded.\n\n"
            "visual - reduces the whole frame to a 16x16 grayscale thumbnail and "
            "compares it as a 240-bit hash. Cheap and reliable when most of the "
            "picture changes. It is effectively blind to a small local edit.\n\n"
            "sensitive - keeps a 256x144 grayscale thumbnail, splits it into a "
            "16x9 grid, and asks how much the single most-changed tile moved. A "
            "rewired node or an opened dialog is judged against its own corner of "
            "the screen instead of being averaged away. On real Unreal and Visual "
            "Studio capture, an unchanged screen scores about 0.2 and the "
            "smallest genuine edits score about 3, so the default sits between.\n\n"
            "off - keeps every frame that was captured successfully.\n\n"
            "Neither mode reads text. A change of a single character does not "
            "survive the downscale that makes this fast, which is why the Code "
            "preset turns comparison off rather than risk discarding an edit."
        ),
        "ffmpeg": (
            "ffmpeg does the decoding, so the tool needs to find it.\n\n"
            "It looks beside this program first, then on PATH, then in the usual "
            "install locations. Use Locate... to point at ffmpeg.exe yourself; "
            "the choice is remembered.\n\n"
            "ffprobe, which normally sits beside ffmpeg, is used to read the "
            "video's size and duration. Without it the run still works.\n\n"
            "TRANSCRIBING\n\n"
            "Some videos have no subtitle file. If your ffmpeg reports "
            "--enable-whisper, it can recognise the speech itself and write the "
            "SRT, which is why this lives here rather than being a separate "
            "program: it is an ffmpeg filter. You supply the model weights, a "
            "whisper.cpp ggml-*.bin file.\n\n"
            "Keep it in a 'models' folder beside this program. That folder is "
            "searched first, so the application stays self-contained: move the "
            "folder somewhere else and the model goes with it. Per-user "
            "application data directories are searched too, but they are harder "
            "to find and easier to lose.\n\n"
            "The result is a guess. Names, APIs and technical vocabulary are "
            "where it goes wrong, so the generated transcript.md carries a "
            "notice saying so and the manifest records which model produced "
            "it.\n\n"
            "Speed depends on two settings more than anything else. The window "
            "governs how much audio each pass covers; whisper always encodes 30 "
            "seconds regardless, so a small window repeats that work. Voice-"
            "activity detection is off by default because measured here it cost "
            "around a hundred times the runtime without improving the cues.\n\n"
            "The generated .srt is written next to the bundle and reused on a "
            "later run, so you only pay for it once. A video that already has "
            "subtitles is never re-transcribed."
        ),
    }

    # The packaged program has no console, so the one place an operator can
    # read what it actually resolved is this dialog.
    _ffmpeg_help = HELP["ffmpeg"]
    HELP["ffmpeg"] = lambda: (
        _ffmpeg_help
        + "\n\nWHAT IT FINDS RIGHT NOW\n\n"
        + diagnostics_report(ffmpeg_var.get(), whisper_model_var.get())
    )

    def titled_box(title: str, row: int) -> ttk.LabelFrame:
        """A labelled section with a ? button explaining it next to the title."""
        header = ttk.Frame(frame)
        ttk.Label(header, text=title).pack(side="left")
        ttk.Button(
            header,
            text="?",
            width=2,
            command=lambda: messagebox.showinfo(
                f"{title} - {APP_NAME}",
                HELP[title]() if callable(HELP[title]) else HELP[title],
            ),
        ).pack(side="left", padx=(6, 0))
        box = ttk.LabelFrame(frame, labelwidget=header, padding=10)
        box.grid(row=row, column=0, sticky="ew", pady=(0 if row == 0 else 10, 0))
        return box

    # -- input files --------------------------------------------------------
    files = titled_box("Input", 0)
    files.columnconfigure(0, weight=1)

    tabs = ttk.Notebook(files)
    tabs.grid(row=0, column=0, sticky="ew")
    single_tab = ttk.Frame(tabs, padding=8)
    batch_tab = ttk.Frame(tabs, padding=8)
    tabs.add(single_tab, text="Single file")
    tabs.add(batch_tab, text="Batch folder")
    single_tab.columnconfigure(1, weight=1)
    batch_tab.columnconfigure(1, weight=1)

    def batch_selected() -> bool:
        return tabs.index(tabs.select()) == 1

    def add_row(parent, row: int, label: str, variable: tk.StringVar, command) -> None:
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=3)
        ttk.Entry(parent, textvariable=variable).grid(
            row=row, column=1, sticky="ew", padx=6, pady=3
        )
        ttk.Button(parent, text="Browse...", command=command, width=11).grid(
            row=row, column=2, pady=3
        )

    def pick_video() -> None:
        path = filedialog.askopenfilename(
            title="Choose a video",
            initialdir=config.get("last_video_dir", ""),
            filetypes=[
                ("Video files", " ".join(f"*{suffix}" for suffix in VIDEO_SUFFIXES)),
                ("All files", "*.*"),
            ],
        )
        if not path:
            return
        video = Path(path)
        video_var.set(str(video))
        config["last_video_dir"] = str(video.parent)
        if not subtitle_var.get():
            guess = guess_subtitles(video)
            if guess:
                subtitle_var.set(str(guess))
        if not output_var.get():
            output_var.set(str(default_output(video)))
        describe_video(video)

    def pick_subtitles() -> None:
        path = filedialog.askopenfilename(
            title="Choose a subtitle file",
            initialdir=config.get("last_video_dir", ""),
            filetypes=[("Subtitles", "*.srt *.vtt"), ("All files", "*.*")],
        )
        if path:
            subtitle_var.set(path)
            describe_subtitles(Path(path))

    def pick_output() -> None:
        current = Path(output_var.get()) if output_var.get() else None
        path = filedialog.asksaveasfilename(
            title="Save the bundle as",
            defaultextension=".zip",
            initialfile=current.name if current else "stills.zip",
            initialdir=str(current.parent) if current else config.get("last_video_dir", ""),
            filetypes=[("Zip archive", "*.zip")],
        )
        if path:
            output_var.set(path)

    add_row(single_tab, 0, "Video", video_var, pick_video)
    add_row(single_tab, 1, "Subtitles", subtitle_var, pick_subtitles)
    add_row(single_tab, 2, "Output zip", output_var, pick_output)

    # -- batch folder -------------------------------------------------------
    def pick_batch_source() -> None:
        path = filedialog.askdirectory(
            title="Choose a folder of videos",
            initialdir=batch_source_var.get() or config.get("last_video_dir", ""),
        )
        if not path:
            return
        batch_source_var.set(path)
        if not batch_output_var.get():
            batch_output_var.set(str(Path(path) / "_stills"))
        scan_batch()

    def pick_batch_output() -> None:
        path = filedialog.askdirectory(
            title="Choose where the bundles go", initialdir=batch_output_var.get() or ""
        )
        if path:
            batch_output_var.set(path)

    add_row(batch_tab, 0, "Source folder", batch_source_var, pick_batch_source)
    add_row(batch_tab, 1, "Output folder", batch_output_var, pick_batch_output)

    batch_options = ttk.Frame(batch_tab)
    batch_options.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(6, 0))
    ttk.Checkbutton(
        batch_options, text="Include subfolders", variable=recursive_var
    ).pack(side="left")
    ttk.Checkbutton(
        batch_options, text="Skip already built", variable=skip_existing_var
    ).pack(side="left", padx=(12, 0))
    ttk.Button(
        batch_options, text="Scan", width=8, command=lambda: scan_batch()
    ).pack(side="right")

    ttk.Label(
        batch_tab, textvariable=batch_summary, foreground="#555555",
        wraplength=600, justify="left",
    ).grid(row=3, column=0, columnspan=3, sticky="w", pady=(6, 0))

    def scan_batch() -> None:
        """Count the work without blocking the window; big archives are slow."""
        source = Path(batch_source_var.get() or "")
        if not source.is_dir():
            messagebox.showwarning(APP_NAME, "Choose a source folder first.")
            return
        # The variable keeps the folder the user chose; the name of the
        # source is added below it, and must not be added again on a rescan.
        chosen = Path(batch_output_var.get() or (source / "_stills"))
        batch_output_var.set(str(chosen))
        destination = batch_destination(source, chosen)
        batch_summary.set("Scanning...")

        def work() -> None:
            try:
                items = find_batch_items(
                    source, destination,
                    recursive=bool(recursive_var.get()),
                    skip_existing=bool(skip_existing_var.get()),
                    transcribe=bool(transcribe_var.get()),
                )
            except OSError as exc:
                root.after(0, batch_summary.set, f"Could not scan: {exc}")
                return

            def apply() -> None:
                ready = sum(1 for item in items if item.ready)
                missing = sum(1 for item in items if item.subtitles is None)
                already = sum(1 for item in items if item.skip_reason == "already built")
                batch_summary.set(
                    f"{len(items)} videos found: {ready} to convert, "
                    f"{missing} without subtitles, {already} already built.\n"
                    f"Writing to {destination}"
                )

            root.after(0, apply)

        threading.Thread(target=work, daemon=True).start()

    # -- content preset -----------------------------------------------------
    preset_box = titled_box("Content preset", 1)
    preset_box.columnconfigure(1, weight=1)

    label_for_key = {preset.key: preset.label for preset in PRESETS.values()}
    key_for_label = {preset.label: preset.key for preset in PRESETS.values()}
    stored_preset = config.get("preset", DEFAULT_PRESET)
    if stored_preset not in PRESETS:
        stored_preset = DEFAULT_PRESET
    preset_var.set(label_for_key[stored_preset])
    preset_summary.set(PRESETS[stored_preset].summary)

    ttk.Label(preset_box, text="Material").grid(row=0, column=0, sticky="w")
    preset_combo = ttk.Combobox(
        preset_box, textvariable=preset_var, values=list(key_for_label),
        state="readonly",
    )
    preset_combo.grid(row=0, column=1, sticky="ew", padx=6)
    ttk.Label(
        preset_box, textvariable=preset_summary, wraplength=620, justify="left",
        foreground="#555555",
    ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(8, 0))

    # -- capture settings ---------------------------------------------------
    options = titled_box("Frames", 2)
    for column in (1, 3):
        options.columnconfigure(column, weight=1)

    ttk.Label(options, text="Capture at").grid(row=0, column=0, sticky="w", pady=3)
    ttk.Combobox(
        options, textvariable=capture_var, values=list(CAPTURE_POINTS),
        state="readonly", width=10,
    ).grid(row=0, column=1, sticky="w", padx=6)

    ttk.Label(options, text="Offset (s)").grid(row=0, column=2, sticky="e", pady=3)
    ttk.Spinbox(
        options, textvariable=offset_var, from_=-30.0, to=30.0, increment=0.25, width=8
    ).grid(row=0, column=3, sticky="w", padx=6)

    ttk.Label(options, text="Min gap (s)").grid(row=1, column=0, sticky="w", pady=3)
    ttk.Spinbox(
        options, textvariable=gap_var, from_=0.0, to=600.0, increment=0.5, width=8
    ).grid(row=1, column=1, sticky="w", padx=6)

    ttk.Label(options, text="Max width (px)").grid(row=1, column=2, sticky="e", pady=3)
    ttk.Spinbox(
        options, textvariable=width_var, from_=160, to=7680, increment=160, width=8
    ).grid(row=1, column=3, sticky="w", padx=6)

    ttk.Label(options, text="Format").grid(row=2, column=0, sticky="w", pady=3)
    ttk.Combobox(
        options, textvariable=format_var, values=list(IMAGE_FORMATS),
        state="readonly", width=10,
    ).grid(row=2, column=1, sticky="w", padx=6)

    quality_label = ttk.Label(options, text=f"Quality {quality_var.get()}")
    quality_label.grid(row=2, column=2, sticky="e", pady=3)

    def refresh_quality_label() -> None:
        quality_label.config(text=f"Quality {int(float(quality_var.get()))}")

    ttk.Scale(
        options, from_=1, to=100, variable=quality_var, orient="horizontal",
        command=lambda _value: refresh_quality_label(),
    ).grid(row=2, column=3, sticky="ew", padx=6)

    ttk.Label(options, text="Parallel workers").grid(row=3, column=0, sticky="w", pady=3)
    ttk.Spinbox(
        options, textvariable=workers_var, from_=1, to=32, increment=1, width=8
    ).grid(row=3, column=1, sticky="w", padx=6)

    # -- duplicate comparison -----------------------------------------------
    compare = titled_box("Comparison", 3)
    compare.columnconfigure(3, weight=1)

    ttk.Label(compare, text="Mode").grid(row=0, column=0, sticky="w", pady=3)
    ttk.Combobox(
        compare, textvariable=dedupe_mode_var, values=list(DEDUPE_MODES),
        state="readonly", width=12,
    ).grid(row=0, column=1, sticky="w", padx=6)

    threshold_label = ttk.Label(compare, text="")
    threshold_label.grid(row=0, column=2, sticky="e", pady=3)

    # Two scales share one cell because the modes measure different quantities:
    # hamming bits out of 240, against mean tile difference on a 0-8 scale.
    visual_scale = ttk.Scale(
        compare, from_=0, to=40, variable=sensitivity_var, orient="horizontal",
        command=lambda _value: refresh_threshold_label(),
    )
    tile_scale = ttk.Scale(
        compare, from_=0.0, to=8.0, variable=tile_var, orient="horizontal",
        command=lambda _value: refresh_threshold_label(),
    )

    threshold_hint = ttk.Label(
        compare, text="", wraplength=620, justify="left", foreground="#555555"
    )
    threshold_hint.grid(row=1, column=0, columnspan=4, sticky="w", pady=(8, 0))

    def refresh_threshold_label() -> None:
        mode = dedupe_mode_var.get()
        if mode == "visual":
            threshold_label.config(
                text=f"Threshold {int(float(sensitivity_var.get()))} bits"
            )
        elif mode == "sensitive":
            threshold_label.config(text=f"Threshold {float(tile_var.get()):.2f}")
        else:
            threshold_label.config(text="")

    def refresh_threshold_controls(*_args) -> None:
        mode = dedupe_mode_var.get()
        visual_scale.grid_remove()
        tile_scale.grid_remove()
        if mode == "visual":
            visual_scale.grid(row=0, column=3, sticky="ew", padx=6)
            threshold_hint.config(
                text=(
                    f"Whole-frame hash, 0-{VISUAL_BITS} bits. Higher drops more. "
                    "Blind to an edit confined to a small part of the screen."
                )
            )
        elif mode == "sensitive":
            tile_scale.grid(row=0, column=3, sticky="ew", padx=6)
            threshold_hint.config(
                text=(
                    f"Worst tile of a {SENSITIVE_TILES_X}x{SENSITIVE_TILES_Y} grid. "
                    "An unchanged screen scores about 0.2; the smallest real edits "
                    "score about 3. Higher drops more."
                )
            )
        else:
            threshold_hint.config(text="Every frame that captures successfully is kept.")
        refresh_threshold_label()

    dedupe_mode_var.trace_add("write", refresh_threshold_controls)

    # -- ffmpeg -------------------------------------------------------------
    tools = titled_box("ffmpeg", 4)
    tools.columnconfigure(0, weight=1)
    ttk.Label(tools, textvariable=ffmpeg_status, wraplength=560, justify="left").grid(
        row=0, column=0, sticky="w"
    )

    def locate_ffmpeg() -> None:
        path = filedialog.askopenfilename(
            title="Locate ffmpeg",
            filetypes=[("ffmpeg", "ffmpeg.exe ffmpeg"), ("All files", "*.*")],
        )
        if path:
            ffmpeg_var.set(path)
            refresh_ffmpeg()

    ttk.Button(tools, text="Locate...", command=locate_ffmpeg, width=11).grid(
        row=0, column=1, padx=6
    )

    speech_row = ttk.Frame(tools)
    speech_row.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))
    ttk.Checkbutton(
        speech_row,
        text="Transcribe videos that have no subtitles",
        variable=transcribe_var,
    ).pack(side="left")
    ttk.Label(speech_row, text="Language").pack(side="left", padx=(12, 4))
    ttk.Combobox(
        speech_row, textvariable=language_var, values=["auto", "en"], width=6
    ).pack(side="left")

    def locate_model() -> None:
        path = filedialog.askopenfilename(
            title="Choose a whisper.cpp model",
            initialdir=str(model_dir()),
            filetypes=[("whisper model", "ggml-*.bin"), ("All files", "*.*")],
        )
        if path:
            whisper_model_var.set(path)
            refresh_whisper()

    ttk.Button(speech_row, text="Model...", command=locate_model, width=9).pack(
        side="right"
    )

    ttk.Label(
        tools, textvariable=whisper_status, wraplength=620, justify="left",
        foreground="#555555",
    ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(6, 0))

    def refresh_whisper() -> None:
        model = find_whisper_model(whisper_model_var.get())
        if model is None:
            whisper_status.set(
                "No speech model found. Put a whisper.cpp ggml-*.bin in a "
                f"models folder beside this program ({_bundle_dir() / 'models'}), "
                "or use Model... to point at it. The ? above lists everywhere "
                "it looked."
            )
            return
        whisper_status.set(
            f"{model.name}. Speech is recognised by ffmpeg itself; the text is a "
            "good guess but not exact, so the transcript says so."
        )

    # -- progress and log ---------------------------------------------------
    ttk.Label(frame, textvariable=status_var).grid(row=5, column=0, sticky="w", pady=(10, 2))
    bars = ttk.Frame(frame)
    bars.grid(row=6, column=0, sticky="ew")
    bars.columnconfigure(0, weight=1)
    # Queue position on top, frames within the current video underneath.
    queue_bar = ttk.Progressbar(bars, mode="determinate")
    queue_bar.grid(row=0, column=0, sticky="ew")
    queue_bar.grid_remove()
    bar = ttk.Progressbar(bars, mode="determinate")
    bar.grid(row=1, column=0, sticky="ew", pady=(3, 0))

    log_box = tk.Text(frame, height=6, wrap="word", state="disabled")
    log_box.grid(row=7, column=0, sticky="nsew", pady=(8, 0))
    frame.rowconfigure(7, weight=1)
    scrollbar = ttk.Scrollbar(frame, command=log_box.yview)
    scrollbar.grid(row=7, column=1, sticky="ns", pady=(8, 0))
    log_box.configure(yscrollcommand=scrollbar.set)

    buttons = ttk.Frame(frame)
    buttons.grid(row=8, column=0, sticky="ew", pady=(10, 0))
    start_button = ttk.Button(buttons, text="Extract")
    start_button.pack(side="left")
    cancel_button = ttk.Button(buttons, text="Cancel", state="disabled")
    cancel_button.pack(side="left", padx=6)
    reveal_button = ttk.Button(buttons, text="Open output folder", state="disabled")
    reveal_button.pack(side="left")

    def append_log(message: str) -> None:
        log_box.configure(state="normal")
        log_box.insert("end", message + "\n")
        log_box.see("end")
        log_box.configure(state="disabled")

    def refresh_ffmpeg() -> None:
        found = find_ffmpeg(ffmpeg_var.get())
        if found is None:
            ffmpeg_status.set(
                "ffmpeg not found. Install it and add it to PATH, or use Locate..."
            )
            return
        try:
            ffmpeg_status.set(f"{found}\n{ffmpeg_version(found)}")
        except ExtractionError as exc:
            ffmpeg_status.set(str(exc))

    def describe_video(video: Path) -> None:
        found = find_ffmpeg(ffmpeg_var.get())
        if found is None:
            return
        info = probe_video(sibling_ffprobe(found), video)
        append_log(f"{video.name}: {info.summary}")

    def describe_subtitles(path: Path) -> None:
        try:
            cues = parse_srt(path)
        except ExtractionError as exc:
            append_log(str(exc))
            return
        append_log(f"{path.name}: {len(cues)} cues, last at {format_timestamp(cues[-1].end)}")

    def set_running(running: bool) -> None:
        start_button.configure(state="disabled" if running else "normal")
        cancel_button.configure(state="normal" if running else "disabled")

    def collect_settings() -> Settings:
        # Read straight from the controls. The preset name is recorded for the
        # manifest but is never re-applied here, so a field the operator changed
        # after picking a preset is the field that runs.
        return Settings(
            preset=key_for_label.get(preset_var.get(), DEFAULT_PRESET),
            capture_point=capture_var.get(),
            offset=float(offset_var.get()),
            min_gap=float(gap_var.get()),
            max_width=int(width_var.get()),
            image_format=format_var.get(),
            quality=int(float(quality_var.get())),
            dedupe_mode=dedupe_mode_var.get(),
            dedupe_threshold=int(float(sensitivity_var.get())),
            tile_threshold=float(tile_var.get()),
            workers=int(workers_var.get()),
            ffmpeg_path=ffmpeg_var.get(),
            transcribe=bool(transcribe_var.get()),
            whisper_model=whisper_model_var.get(),
            whisper_language=language_var.get() or "auto",
        )

    def remember(settings: Settings) -> None:
        config.update(
            {
                "preset": settings.preset,
                "capture_point": settings.capture_point,
                "offset": settings.offset,
                "min_gap": settings.min_gap,
                "max_width": settings.max_width,
                "image_format": settings.image_format,
                "quality": settings.quality,
                "dedupe": settings.dedupe,
                "dedupe_mode": settings.dedupe_mode,
                "dedupe_threshold": settings.dedupe_threshold,
                "tile_threshold": settings.tile_threshold,
                "workers": settings.workers,
                "ffmpeg_path": settings.ffmpeg_path,
                "last_batch_source": batch_source_var.get(),
                "last_batch_output": batch_output_var.get(),
                "batch_recursive": bool(recursive_var.get()),
                "batch_skip_existing": bool(skip_existing_var.get()),
                "transcribe": settings.transcribe,
                "whisper_model": settings.whisper_model,
                "whisper_language": settings.whisper_language,
            }
        )
        save_config(config)

    def on_log(message: str) -> None:
        root.after(0, append_log, message)

    def on_progress(done: int, total: int) -> None:
        def apply() -> None:
            bar.configure(maximum=max(1, total), value=done)
            if not running_batch[0]:
                status_var.set(f"Capturing frames: {done} of {total}")

        root.after(0, apply)

    def finish(message: str, ok: bool, folder: Path | None) -> None:
        set_running(False)
        status_var.set(message)
        append_log(message)
        if folder is not None:
            reveal_button.configure(state="normal", command=lambda: open_folder(folder))
        if not ok:
            messagebox.showerror(APP_NAME, message)

    def validated_settings() -> Settings | None:
        try:
            settings = collect_settings()
            settings.validate()
        except (ExtractionError, tk.TclError, ValueError) as exc:
            messagebox.showerror(APP_NAME, str(exc))
            return None
        remember(settings)
        return settings

    def begin(header: str) -> None:
        cancel_event.clear()
        set_running(True)
        reveal_button.configure(state="disabled")
        bar.configure(value=0, maximum=1)
        append_log("")
        append_log(header)

    def start_single() -> None:
        nonlocal worker
        if not video_var.get():
            messagebox.showwarning(APP_NAME, "Choose a video first.")
            return
        if not subtitle_var.get() and not transcribe_var.get():
            messagebox.showwarning(
                APP_NAME,
                "Choose a subtitle file, or turn on transcription to generate one.",
            )
            return
        output = Path(output_var.get() or default_output(Path(video_var.get())))
        output_var.set(str(output))

        settings = validated_settings()
        if settings is None:
            return

        running_batch[0] = False
        queue_bar.grid_remove()
        begin(f"--- {output.name} ---")

        # Read on the main thread: Tk variables belong to the thread that owns
        # the interpreter, and touching them from the worker is a race that
        # usually gets away with it.
        video_path = Path(video_var.get())
        subtitle_path = Path(subtitle_var.get()) if subtitle_var.get() else None

        def job() -> None:
            try:
                report = extract_bundle(
                    video_path,
                    subtitle_path,
                    output,
                    settings,
                    log=on_log,
                    progress=on_progress,
                    cancel=cancel_event,
                )
            except ExtractionCancelled:
                root.after(0, finish, "Cancelled.", True, None)
                return
            except ExtractionError as exc:
                root.after(0, finish, str(exc), False, None)
                return
            except Exception as exc:  # unexpected, but must not kill the window
                root.after(0, finish, f"Unexpected failure: {exc}", False, None)
                return

            summary = (
                f"Done: {report.kept} frames from {report.cue_count} cues, "
                f"{report.duplicates} near-duplicates dropped"
                f"{f', {len(report.failures)} failed' if report.failures else ''}."
            )
            for failure in report.failures[:20]:
                root.after(0, append_log, f"  failed: {failure}")
            root.after(0, finish, summary, True, report.output.parent)

        worker = threading.Thread(target=job, daemon=True)
        worker.start()

    def start_batch() -> None:
        nonlocal worker
        source = Path(batch_source_var.get() or "")
        if not source.is_dir():
            messagebox.showwarning(APP_NAME, "Choose a source folder first.")
            return
        # The variable keeps the folder the user chose; the name of the
        # source is added below it, and must not be added again on a rescan.
        chosen = Path(batch_output_var.get() or (source / "_stills"))
        batch_output_var.set(str(chosen))
        destination = batch_destination(source, chosen)

        settings = validated_settings()
        if settings is None:
            return

        running_batch[0] = True
        queue_bar.grid()
        begin(f"--- batch: {source} -> {destination} ---")

        # Same reason as start_single: sampled here, on the main thread.
        recursive = bool(recursive_var.get())
        skip_existing = bool(skip_existing_var.get())
        want_speech = bool(transcribe_var.get())

        def on_item(index: int, total: int, item: BatchItem) -> None:
            def apply() -> None:
                queue_bar.configure(maximum=max(1, total), value=index - 1)
                status_var.set(f"[{index}/{total}] {item.video.name}")

            root.after(0, apply)

        def job() -> None:
            # Rescanned here rather than reusing the Scan result, so that a
            # folder changed after scanning cannot convert the wrong tree.
            items = find_batch_items(
                source,
                destination,
                recursive=recursive,
                skip_existing=skip_existing,
                transcribe=want_speech,
            )
            if not items:
                root.after(0, finish, f"No videos found under {source}", False, None)
                return
            try:
                report = extract_batch(
                    items,
                    settings,
                    destination,
                    log=on_log,
                    on_item=on_item,
                    progress=on_progress,
                    cancel=cancel_event,
                )
            except ExtractionError as exc:
                root.after(0, finish, str(exc), False, None)
                return
            except Exception as exc:  # unexpected, but must not kill the window
                root.after(0, finish, f"Unexpected failure: {exc}", False, None)
                return

            message = report.summary() + (" (cancelled)" if report.cancelled else "")

            def done() -> None:
                queue_bar.configure(value=queue_bar.cget("maximum"))
                finish(message, True, destination)

            root.after(0, done)

        worker = threading.Thread(target=job, daemon=True)
        worker.start()

    def start() -> None:
        if batch_selected():
            start_batch()
        else:
            start_single()

    def stop() -> None:
        cancel_event.set()
        status_var.set("Cancelling...")
        # Killing the child is what actually stops a transcription. Waiting for
        # it to notice the flag could take the rest of the audio.
        threading.Thread(target=terminate_active_processes, daemon=True).start()

    def open_folder(folder: Path) -> None:
        try:
            if os.name == "nt":
                os.startfile(folder)  # noqa: S606 - opening the operator's own output
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(folder)])
            else:
                subprocess.Popen(["xdg-open", str(folder)])
        except OSError as exc:
            messagebox.showerror(APP_NAME, f"Could not open {folder}: {exc}")

    start_button.configure(command=start)
    cancel_button.configure(command=stop)

    def on_preset_selected(_event=None) -> None:
        """Fill the controls from the chosen preset, then get out of the way."""
        preset = PRESETS[key_for_label.get(preset_var.get(), DEFAULT_PRESET)]
        capture_var.set(preset.capture_point)
        gap_var.set(preset.min_gap)
        width_var.set(preset.max_width)
        format_var.set(preset.image_format)
        quality_var.set(preset.quality)
        sensitivity_var.set(preset.dedupe_threshold)
        tile_var.set(preset.tile_threshold)
        dedupe_mode_var.set(preset.dedupe_mode)
        preset_summary.set(preset.summary)
        refresh_quality_label()
        refresh_threshold_controls()
        append_log(f"Preset: {preset.label}")

    def on_tab_changed(_event=None) -> None:
        if worker is not None and worker.is_alive():
            return  # a run is talking; leave its status alone
        status_var.set(
            "Choose a folder, scan it, then Extract."
            if batch_selected()
            else "Choose a video and its subtitles."
        )

    tabs.bind("<<NotebookTabChanged>>", on_tab_changed)
    preset_combo.bind("<<ComboboxSelected>>", on_preset_selected)
    refresh_quality_label()
    refresh_threshold_controls()
    refresh_whisper()

    def on_close() -> None:
        # Closing the window must take the speech model down with it. Python
        # daemon threads die with the interpreter, but the ffmpeg processes
        # they started do not, so they are killed here before the window goes.
        cancel_event.set()
        status_var.set("Stopping...")
        root.update_idletasks()
        terminate_active_processes()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    refresh_ffmpeg()
    # The window has grown section by section; cap it to the screen and let the
    # log, which is the only row with weight, absorb the difference.
    root.update_idletasks()
    root.geometry(
        f"{root.winfo_reqwidth()}x"
        f"{min(root.winfo_reqheight(), root.winfo_screenheight() - 140)}"
    )
    root.mainloop()
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv:
        return run_cli(argv)
    return run_gui()


if __name__ == "__main__":
    raise SystemExit(main())
