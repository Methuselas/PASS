#!/usr/bin/env python3
"""Deterministic pre-preflight source preparation for ordinary PASS runs.

The prepared package is model-facing working input, not card provenance. It is
kept inside the active skill-staging run so continuation archives are sufficient
for provider/model switches after preparation.

Source Prep deliberately keeps two conceptual layers:

* a deterministic extraction floor under ``controller/source-prep-raw``; and
* semantic, model-facing Markdown under ``prepared-source``.

The floor is used to verify preservation and diagnose extraction uncertainty. It
is scratch evidence, not downstream model input and not card provenance.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Iterable, Any

from . import pass_authoring_run as preflight
from .pass_authoring_workflow import Run, RunError, atomic_write, digest, inside

PREP_SCHEMA = 3
SUPPORTED_TEXT = {".txt", ".md", ".markdown"}
PAGE_RE = re.compile(r"(?:pdf\s+|source\s+)?(?:pp?\.?\s*)?(\d+)\s*(?:[-–—]|to)\s*(\d+)", re.I)
SINGLE_PAGE_RE = re.compile(r"(?:pdf\s+|source\s+)?(?:p(?:age)?\.?\s*)(\d+)", re.I)
FIGURE_RE = re.compile(r"^\s*(Figure|Fig\.)\s+([A-Za-z0-9._-]+)\s*(?:[–—:-]\s*)?(.*)$", re.I)
LIST_RE = re.compile(r"^\s*([•●▪◦‣]|[-*])\s+(.*)$")
ORDERED_RE = re.compile(r"^\s*(\d+)[.)]\s+(.*)$")
PURE_PAGE_NUMBER_RE = re.compile(r"^\s*(?:\d+|[ivxlcdm]+)\s*$", re.I)
CODE_HINT_RE = re.compile(
    r"(?:#include\b|#pragma\b|\b(?:class|struct|enum|namespace|return|if|else|for|while|switch|case|public|private|protected|void|int|float|double|bool|auto)\b|::|->|[{};]|\bstd::|>>>\s|\.\.\.\s)",
    re.I,
)
PYTHON_CODE_START_RE = re.compile(
    r"^(?:"
    r">>>\s|\.\.\.\s|"
    r"(?:async\s+)?def\s+[A-Za-z_]\w*\s*\(|"
    r"class\s+[A-Za-z_]\w*(?:\s*\([^)]*\))?\s*:|"
    r"(?:if|elif|for|while|with|except)\b.*:\s*(?:#.*)?$|"
    r"(?:else|try|finally)\s*:\s*(?:#.*)?$|"
    r"(?:return|yield|raise|assert|break|continue|pass|global|nonlocal|del)\b|"
    r"(?:from\s+[A-Za-z_][\w.]*\s+import\b|import\s+[A-Za-z_][\w.]*)|"
    r"[A-Za-z_]\w*(?:\[[^\]]+\]|\.[A-Za-z_]\w*)*\s*(?::=|[+\-*/%&|^]?=)\s*\S+|"
    r"#!\s*/[A-Za-z0-9_./ -]+$|"
    r"\$\s+\S+"
    r")",
)
GENERIC_CODE_START_RE = re.compile(
    r"^(?:#include\b|#pragma\b|(?:public|private|protected)\s*:|"
    r"(?:class|struct|enum|namespace)\s+\w+|(?:if|for|while|switch)\s*\(|"
    r"(?:return|break|continue)\b|"
    r"(?:const\s+)?(?:unsigned\s+)?(?:void|int|float|double|bool|char|short|long|auto|std::\w+|[UAFST][A-Z]\w*(?:<[^>]+>)?[*&]?)"
    r"\s+[*&]?[A-Za-z_]\w*\s*(?:[=(;]))",
)
MONO_FONT_RE = re.compile(r"(?:courier|mono|consolas|code|sourcecode|menlo)", re.I)
BOLD_FONT_RE = re.compile(r"(?:bold|semibold|demi|black)", re.I)
VERSION_PATTERNS = [
    ("Unreal Engine", re.compile(r"\b(?:Unreal Engine|UE)\s*(5(?:\.\d+){0,2})\b", re.I)),
    ("Visual Studio", re.compile(r"\bVisual Studio\s*(20\d{2})\b", re.I)),
    ("Python", re.compile(r"\bPython\s*(3(?:\.\d+){0,2})\b", re.I)),
]


def _nfc(text: str) -> str:
    return unicodedata.normalize("NFC", text or "").replace("\r\n", "\n").replace("\r", "\n")


def normalize_code_line(line: str) -> str:
    """Preserve indentation and interior spacing in preformatted/code content."""
    line = _nfc(line).replace("\u00ad", "")
    # PDF code fonts often encode indentation as narrow/non-breaking spaces.
    line = line.replace("\u202f", " ").replace("\u00a0", " ")
    return line.rstrip()


def normalize_prose_line(line: str) -> str:
    """Normalize prose without touching leading semantics in code blocks."""
    line = _nfc(line).replace("\u00ad", "").replace("\u202f", " ").replace("\u00a0", " ")
    return re.sub(r"[ \t]+", " ", line).strip()


def _join_prose_lines(lines: list[str]) -> str:
    """Reflow PDF line wraps conservatively.

    A printed hyphen at a line boundary is preserved. This intentionally favors
    a visible possible line-break artifact (``develop-ment``) over silently
    deleting a real hyphen (``real-world`` -> ``realworld``).
    """
    out = ""
    for raw in lines:
        line = normalize_prose_line(raw)
        if not line:
            continue
        if not out:
            out = line
            continue
        if out.endswith("-") and re.match(r"^[a-z]", line):
            out += line
        else:
            out += " " + line
    return out.strip()


def normalize_text(text: str) -> str:
    """Compatibility helper for plain-text sources.

    Unlike beta.78, this never collapses leading whitespace globally and never
    removes an ambiguous printed hyphen at a line break.
    """
    text = _nfc(text).replace("\u00ad", "")
    lines = text.split("\n")
    out: list[str] = []
    for line in lines:
        if line.startswith(("    ", "\t")) or CODE_HINT_RE.search(line):
            out.append(normalize_code_line(line))
        else:
            out.append(normalize_prose_line(line))
    return re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip()


def package_root(run: Run) -> Path:
    return inside(run.root, "prepared-source")


def manifest_path(run: Run) -> Path:
    return inside(run.root, "prepared-source/source.json")


def index_path(run: Run) -> Path:
    return inside(run.root, "prepared-source/INDEX.md")


def raw_root(run: Run) -> Path:
    return inside(run.root, "controller/source-prep-raw")


def package_files(run: Run) -> dict[str, str]:
    root = package_root(run)
    result: dict[str, str] = {}
    if not root.is_dir():
        return result
    for path in sorted(root.rglob("*")):
        if path.is_file() and path != manifest_path(run):
            result[path.relative_to(root).as_posix()] = digest(path)
    return result


def package_digest(files: dict[str, str]) -> str:
    blob = json.dumps(files, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(blob).hexdigest()


def _plain_for_integrity(text: str) -> str:
    text = _nfc(text).casefold().replace("\u00ad", "")
    # Formatting punctuation/whitespace are intentionally ignored by the gate.
    return re.sub(r"[^\w]+", "", text, flags=re.UNICODE)


def _integrity_metrics(raw_text: str, prepared_text: str, code_fragments: list[str]) -> dict[str, Any]:
    raw_plain = _plain_for_integrity(raw_text)
    prepared_plain = _plain_for_integrity(prepared_text)
    # This is a conservative floor check, not semantic equivalence. Running
    # furniture and duplicated figure/table text may be intentionally removed.
    coverage = (len(prepared_plain) / len(raw_plain)) if raw_plain else 1.0
    code_checks = []
    for fragment in code_fragments:
        src = "\n".join(normalize_code_line(x) for x in fragment.splitlines()).strip()
        ok = bool(src) and src in prepared_text
        code_checks.append({"sha256": "sha256:" + hashlib.sha256(src.encode()).hexdigest(), "preserved": ok})
    return {
        "raw_nonformat_chars": len(raw_plain),
        "prepared_nonformat_chars": len(prepared_plain),
        "coverage_ratio": round(coverage, 4),
        "code_blocks": len(code_checks),
        "code_blocks_preserved": sum(1 for x in code_checks if x["preserved"]),
        "code_checks": code_checks,
    }


def _table_to_markdown(rows: list[list[str | None]]) -> str | None:
    # Markdown tables are excellent for prose/reference matrices, but they are
    # a poor carrier for indentation-sensitive code. Route code-bearing tables
    # to CSV instead so embedded newlines/leading whitespace survive.
    for row in rows:
        for cell in row:
            raw = _nfc(cell or "")
            if re.search(r"(?:^|\n)[ \t]{2,}\S", raw) or re.search(r"(?:^|\n)\s*(?:>>>|\.\.\.)\s", raw):
                return None
    cleaned = [[normalize_prose_line(cell or "").replace("\n", "<br>") for cell in row] for row in rows]
    if len(cleaned) < 2:
        return None
    cols = max((len(r) for r in cleaned), default=0)
    if cols < 2:
        return None
    cleaned = [r + [""] * (cols - len(r)) for r in cleaned]
    if sum(bool(c) for r in cleaned for c in r) < 4:
        return None
    def esc(v: str) -> str:
        return v.replace("|", "\\|")
    lines = ["| " + " | ".join(esc(c) for c in cleaned[0]) + " |", "| " + " | ".join(["---"] * cols) + " |"]
    lines.extend("| " + " | ".join(esc(c) for c in row) + " |" for row in cleaned[1:])
    return "\n".join(lines)


def _write_csv(path: Path, rows: list[list[str | None]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    buf = io.StringIO(newline="")
    writer = csv.writer(buf)
    for row in rows:
        writer.writerow([_nfc(cell or "").replace("\u00ad", "") for cell in row])
    path.write_text(buf.getvalue(), encoding="utf-8", newline="")


def _bbox_overlap(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> float:
    x0, y0 = max(a[0], b[0]), max(a[1], b[1])
    x1, y1 = min(a[2], b[2]), min(a[3], b[3])
    if x1 <= x0 or y1 <= y0:
        return 0.0
    inter = (x1 - x0) * (y1 - y0)
    area = max(1.0, (a[2] - a[0]) * (a[3] - a[1]))
    return inter / area


def _line_text(line: dict) -> str:
    return "".join(span.get("text", "") for span in line.get("spans", []))


def _line_fonts(line: dict) -> list[str]:
    return [span.get("font", "") for span in line.get("spans", []) if span.get("text", "").strip()]


def _line_sizes(line: dict) -> list[float]:
    return [float(span.get("size", 0.0)) for span in line.get("spans", []) if span.get("text", "").strip()]


def _is_mono_line(line: dict) -> bool:
    spans = [s for s in line.get("spans", []) if s.get("text", "").strip()]
    if not spans:
        return False
    total = sum(len(s.get("text", "")) for s in spans)
    mono = sum(len(s.get("text", "")) for s in spans if MONO_FONT_RE.search(s.get("font", "")))
    text = normalize_prose_line(_line_text(line))
    ratio = mono / max(total, 1)
    # Publishers often typeset URLs, filenames and paths in a mono face inside
    # ordinary prose. Do not fence those solely because of the font.
    urlish = bool(re.search(r"(?:https?://|www\.|[A-Za-z0-9.-]+/[A-Za-z0-9._/-]+)", text))
    strong_syntax = bool(re.search(r"(?:[{};]|::|->|#include|#pragma|^>>>\s|^\.\.\.\s|^\s*(?:def|class|return|if|else|for|while|switch)\b)", text))
    if urlish and not strong_syntax:
        return False
    return (total and ratio >= 0.70 and (strong_syntax or len(text.split()) <= 8)) or bool(CODE_HINT_RE.search(text) and ratio >= 0.30)



def _leading_space_count(text: str) -> int:
    """Return semantic leading indentation after normalizing PDF space glyphs."""
    text = _nfc(text).replace("\u202f", " ").replace("\u00a0", " ")
    expanded = text.expandtabs(4)
    return len(expanded) - len(expanded.lstrip(" "))


def _looks_like_code_line(text: str) -> bool:
    """Broad syntax/content detector independent of typography.

    This deliberately does not require a mono font: many programming books use
    the body font for code and express code only through indentation and layout.
    """
    raw = _nfc(text).replace("\u202f", " ").replace("\u00a0", " ")
    stripped = raw.strip()
    if not stripped:
        return False
    # A long body-font line that mixes assignment/call syntax with explanatory
    # prose is more safely retained as prose than fenced as trustworthy code.
    # Explicit prompts and preformatted indentation bypass this guard.
    if len(stripped.split()) > 16 and not stripped.startswith((">>>", "...", "$ ")) and _leading_space_count(raw) < 2:
        return False
    if PYTHON_CODE_START_RE.search(stripped) or GENERIC_CODE_START_RE.search(stripped):
        return True
    if stripped.startswith((">>>", "...", "$ ")):
        return True
    # Obvious function/method calls, standalone string/docstring literals and
    # indexing expressions are useful signals when isolated as example lines,
    # but prose with parentheses should not be promoted merely because it names
    # a function.
    if re.match(r"^(?:[rubfRUBF]{0,2})(?:\"\"\"|\'\'\').*(?:\"\"\"|\'\'\')$", stripped):
        return True
    if len(stripped.split()) <= 14 and re.match(r"^[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*\s*\(.*\)\s*$", stripped):
        return True
    if len(stripped.split()) <= 10 and re.match(r"^[A-Za-z_]\w*(?:\[[^\]]+\]|\.[A-Za-z_]\w*)+\s*$", stripped):
        return True
    return False


def _looks_like_code_output(lines: list[dict], body_size: float) -> bool:
    """Recognize compact REPL/program output following a detected code region."""
    if not lines:
        return False
    texts = [normalize_code_line(_line_text(line)).strip() for line in lines]
    if any(not text for text in texts):
        texts = [text for text in texts if text]
    if not texts:
        return False
    # Do not swallow a real heading after a code example.
    if any(_heading_level(line, body_size) for line in lines):
        return False
    for text in texts:
        words = text.split()
        if len(words) > 10 or len(text) > 120:
            return False
        # Instructional transitions are not console output even when they are
        # short and sit immediately below a REPL prompt.
        if len(words) >= 3 and re.match(r"^(?:To|The|This|If|For|Now|Here|When|Once|Using|Hence|Assuming|Take|Next|Following|Again)\b", text):
            return False
        # Sentence-like prose is unlikely to be console output. Short reprs,
        # numbers, collection displays, quoted strings and terse words are fine.
        if len(words) >= 6 and re.search(r"[.!?:]\s*$", text):
            return False
    return True


def _raw_code_signal_count(page_dict: dict, page_height: float, repeated: set[str]) -> int:
    """Independent sanity signal used by the integrity gate.

    This is intentionally broader than the actual code renderer so a detector
    regression cannot report a clean PASS simply because it detected nothing.
    """
    signals = 0
    for block in page_dict.get("blocks", []):
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            if _is_furniture(line, page_height, repeated):
                continue
            raw = _line_text(line)
            stripped = raw.strip()
            if not stripped:
                continue
            if _looks_like_code_line(raw) or stripped.startswith((">>>", "...", "$ ", "#!")):
                signals += 1
                continue
            # Leading whitespace is only a broad signal here. The renderer
            # still requires context before treating arbitrary indented prose as
            # code, but the integrity gate should notice that preformatted text
            # exists even if classification later fails.
            if _leading_space_count(raw) >= 3:
                signals += 1
    return signals


def _rebuild_code_lines(run_lines: list[dict], fallback_bbox: tuple[float, float, float, float]) -> str:
    """Reconstruct code indentation from explicit spaces and geometric x-offset."""
    text_lines = [normalize_code_line(_line_text(line)) for line in run_lines]
    x0s = [float(line.get("bbox", fallback_bbox)[0]) for line in run_lines]
    base = min(x0s) if x0s else fallback_bbox[0]
    sizes = [s for line in run_lines for s in _line_sizes(line)]
    em = (sum(sizes) / len(sizes)) * 0.60 if sizes else 5.4
    rebuilt: list[str] = []
    for line, x0, txt in zip(run_lines, x0s, text_lines):
        explicit = _leading_space_count(txt)
        geometric = max(0, round((x0 - base) / max(em, 1.0)))
        indent = max(explicit, geometric)
        rebuilt.append(" " * indent + txt.lstrip(" \t"))
    return "\n".join(rebuilt).rstrip()


def _line_is_code_candidate(line: dict, in_code_run: bool = False) -> bool:
    raw = _line_text(line)
    if _is_mono_line(line) or _looks_like_code_line(raw):
        return True
    if in_code_run and _leading_space_count(raw) >= 2:
        return True
    # A visibly indented line is likely preformatted/code when it is not a long
    # prose sentence. This catches books that encode Python indentation in the
    # text itself while retaining the same serif font as body copy.
    if _leading_space_count(raw) >= 3 and len(raw.strip().split()) <= 14:
        return True
    return False


def _heading_level(line: dict, body_size: float) -> int | None:
    text = normalize_prose_line(_line_text(line))
    if not text or len(text) > 140:
        return None
    sizes = _line_sizes(line)
    fonts = _line_fonts(line)
    if not sizes:
        return None
    max_size = max(sizes)
    spans = [sp for sp in line.get("spans", []) if sp.get("text", "").strip()]
    total_chars = sum(len(sp.get("text", "")) for sp in spans)
    bold_chars = sum(len(sp.get("text", "")) for sp in spans if BOLD_FONT_RE.search(sp.get("font", "")))
    bold = bool(total_chars and bold_chars / total_chars >= 0.65)
    if max_size >= body_size * 2.0:
        return 1
    if max_size >= body_size * 1.35:
        return 2
    if max_size >= body_size * 1.16:
        return 3
    if bold and len(text) <= 90 and not re.search(r"[.!?;:]$", text):
        return 3
    return None


def _furniture_key(text: str) -> str:
    text = normalize_prose_line(text).casefold()
    text = re.sub(r"\b\d+\b", "#", text)
    text = re.sub(r"\b[ivxlcdm]+\b", "#", text)
    return text


def _collect_repeated_furniture(doc) -> set[str]:
    counts: Counter[str] = Counter()
    for page in doc:
        h = page.rect.height
        for block in page.get_text("dict", sort=True).get("blocks", []):
            if block.get("type") != 0:
                continue
            for line in block.get("lines", []):
                y0, y1 = line.get("bbox", (0, 0, 0, 0))[1], line.get("bbox", (0, 0, 0, 0))[3]
                if y0 <= 52 or y1 >= h - 42:
                    text = normalize_prose_line(_line_text(line))
                    if text and len(text) <= 100:
                        counts[_furniture_key(text)] += 1
    threshold = max(3, min(8, len(doc) // 10 or 3))
    return {k for k, n in counts.items() if n >= threshold and k}


def _is_furniture(line: dict, page_height: float, repeated: set[str]) -> bool:
    text = normalize_prose_line(_line_text(line))
    if not text:
        return True
    y0, y1 = line.get("bbox", (0, 0, 0, 0))[1], line.get("bbox", (0, 0, 0, 0))[3]
    at_margin = y0 <= 52 or y1 >= page_height - 42
    if at_margin and PURE_PAGE_NUMBER_RE.fullmatch(text):
        return True
    return at_margin and _furniture_key(text) in repeated


def _body_font_size(page_dict: dict, page_height: float) -> float:
    weighted: Counter[float] = Counter()
    for block in page_dict.get("blocks", []):
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            y0, y1 = line.get("bbox", (0, 0, 0, 0))[1], line.get("bbox", (0, 0, 0, 0))[3]
            if y0 <= 45 or y1 >= page_height - 35:
                continue
            for span in line.get("spans", []):
                text = span.get("text", "")
                if text.strip() and not MONO_FONT_RE.search(span.get("font", "")):
                    weighted[round(float(span.get("size", 0.0)), 1)] += len(text)
    return weighted.most_common(1)[0][0] if weighted else 10.0


def _extract_tables(plumber_page, assets_root: Path, page_no: int) -> tuple[list[dict], list[tuple[float, float, float, float]]]:
    entries: list[dict] = []
    bboxes: list[tuple[float, float, float, float]] = []
    try:
        tables = plumber_page.find_tables()
    except Exception:
        tables = []
    count = 0
    for table in tables:
        try:
            rows = table.extract() or []
        except Exception:
            continue
        cols = max((len(r) for r in rows), default=0)
        if len(rows) < 2 or cols < 2:
            continue
        # Avoid treating bordered code examples as tables.
        if sum(1 for row in rows for cell in row if normalize_prose_line(cell or "")) < 4:
            continue
        count += 1
        bbox = tuple(float(v) for v in table.bbox)
        bboxes.append(bbox)
        total_chars = sum(len(cell or "") for row in rows for cell in row)
        md = _table_to_markdown(rows) if cols <= 5 and total_chars <= 2200 else None
        if md:
            entries.append({"y": bbox[1], "bbox": bbox, "kind": "table_markdown", "content": md, "rows": len(rows), "columns": cols})
        else:
            rel = f"assets/P{page_no:04d}/table_{count:02d}.csv"
            _write_csv(assets_root.parent / rel, rows)
            entries.append({"y": bbox[1], "bbox": bbox, "kind": "table_csv", "file": rel, "rows": len(rows), "columns": cols})
    return entries, bboxes


def _extract_visuals(page, page_dict: dict, root: Path, page_no: int) -> tuple[list[dict], list[dict]]:
    lines: list[tuple[float, str]] = []
    for block in page_dict.get("blocks", []):
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            text = normalize_prose_line(_line_text(line))
            if text:
                lines.append((line.get("bbox", (0, 0, 0, 0))[1], text))
    visuals: list[dict] = []
    events: list[dict] = []
    counter = 0
    page_area = page.rect.width * page.rect.height
    for block in page_dict.get("blocks", []):
        if block.get("type") != 1:
            continue
        bbox = tuple(float(v) for v in block.get("bbox", (0, 0, 0, 0)))
        area = max(0.0, (bbox[2] - bbox[0]) * (bbox[3] - bbox[1]))
        width, height = int(block.get("width", 0)), int(block.get("height", 0))
        if width < 120 or height < 80 or area / max(page_area, 1) < 0.025:
            continue
        counter += 1
        below = [(y, t) for y, t in lines if bbox[3] <= y <= bbox[3] + 70]
        caption = next((t for _, t in sorted(below) if FIGURE_RE.match(t)), "")
        ext = str(block.get("ext") or "png").lower()
        if ext not in {"png", "jpg", "jpeg", "webp"}:
            ext = "png"
        rel = f"assets/P{page_no:04d}/visual_{counter:02d}.{ext}"
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        data = block.get("image")
        if isinstance(data, (bytes, bytearray)):
            path.write_bytes(bytes(data))
        else:
            continue
        record = {
            "page": page_no,
            "file": rel,
            "bbox": [round(v, 2) for v in bbox],
            "pixel_size": [width, height],
            "caption": caption or None,
            "retention": "retained-on-demand",
            "reason": "significant embedded visual; downstream model opens only when text is insufficient",
            "sha256": digest(path),
        }
        visuals.append(record)
        label = caption or f"visual {counter} on source page {page_no}"
        events.append({"y": bbox[1], "kind": "visual", "content": f"[Visual asset — {label}](../{rel})"})
    return visuals, events


def _render_text_events(page_dict: dict, page_height: float, body_size: float, repeated: set[str], table_bboxes: list[tuple[float, float, float, float]]) -> tuple[list[dict], list[str]]:
    events: list[dict] = []
    code_fragments: list[str] = []
    recent_code_end: float | None = None
    recent_code_expects_output = False

    for block in page_dict.get("blocks", []):
        if block.get("type") != 0:
            continue
        bbox = tuple(float(v) for v in block.get("bbox", (0, 0, 0, 0)))
        if any(_bbox_overlap(bbox, tb) >= 0.55 for tb in table_bboxes):
            recent_code_end = None
            recent_code_expects_output = False
            continue
        lines = [line for line in block.get("lines", []) if not _is_furniture(line, page_height, repeated)]
        if not lines:
            continue

        # PDF list numbers are often extracted as a separate line inside the
        # same text block. Coalesce that block before heading detection so a
        # bold filename inside an instruction does not become a false heading.
        first_text = normalize_prose_line(_line_text(lines[0]))
        if len(lines) >= 2 and not recent_code_expects_output and re.fullmatch(r"\d+[.)]?", first_text):
            number = re.sub(r"[^0-9]", "", first_text)
            rest = _join_prose_lines([_line_text(line) for line in lines[1:]])
            if rest:
                following_level = _heading_level(lines[1], body_size)
                if following_level and following_level <= 2:
                    events.append({"y": bbox[1], "y_end": bbox[3], "kind": "heading", "content": f"# Chapter {number} — {rest}"})
                else:
                    events.append({"y": bbox[1], "y_end": bbox[3], "kind": "list", "content": f"{number}. {rest}"})
                recent_code_end = None
                recent_code_expects_output = False
                continue

        # A compact block immediately following code may be REPL/program output
        # even when it contains no syntax of its own (True, 0/1/2, list items,
        # repr strings, etc.). Typography is intentionally irrelevant here.
        has_explicit_code_candidate = any(_line_is_code_candidate(line, in_code_run=False) for line in lines)
        continuation_output = (
            recent_code_end is not None
            and recent_code_expects_output
            and not has_explicit_code_candidate
            and bbox[1] - recent_code_end <= 24
            and _looks_like_code_output(lines, body_size)
        )

        # Split each text block into code/prose runs using typography *or*
        # content/layout. This is the beta.80 fix for programming books that use
        # the same serif body font for code and prose.
        runs: list[tuple[bool, list[dict]]] = []
        in_code = continuation_output
        inline_expects_output = recent_code_expects_output
        consumed_inline_output = continuation_output
        for line in lines:
            candidate = _line_is_code_candidate(line, in_code_run=in_code)
            is_inline_output = (
                not candidate
                and in_code
                and inline_expects_output
                and _looks_like_code_output([line], body_size)
            )
            is_code = continuation_output or candidate or is_inline_output
            if runs and runs[-1][0] == is_code:
                runs[-1][1].append(line)
            else:
                runs.append((is_code, [line]))
            if is_code:
                raw_line = _line_text(line)
                if re.match(r"^\s*(?:>>>|\.\.\.|\$\s)", raw_line):
                    inline_expects_output = True
                elif is_inline_output:
                    consumed_inline_output = True
            else:
                inline_expects_output = False
            in_code = is_code

        block_ended_in_code = False
        for is_code, run_lines in runs:
            y = float(run_lines[0].get("bbox", bbox)[1])
            y_end = float(run_lines[-1].get("bbox", bbox)[3])
            if is_code:
                content = _rebuild_code_lines(run_lines, bbox)
                if content:
                    code_fragments.append(content)
                    events.append({"y": y, "y_end": y_end, "kind": "code", "content": "```text\n" + content + "\n```"})
                    had_prompt = bool(re.search(r"(?m)^\s*(?:>>>|\.\.\.|\$\s)", content))
                    # REPL/shell prompts can be followed by a compact output
                    # block. Keep that expectation across a directly indented
                    # continuation block, but consume it after actual output.
                    if continuation_output or consumed_inline_output:
                        recent_code_expects_output = False
                    elif had_prompt:
                        recent_code_expects_output = True
                    elif recent_code_expects_output and any(_leading_space_count(_line_text(line)) >= 2 for line in run_lines):
                        recent_code_expects_output = True
                    else:
                        recent_code_expects_output = False
                    recent_code_end = y_end
                    block_ended_in_code = True
                continue

            block_ended_in_code = False
            recent_code_end = None
            recent_code_expects_output = False

            # If a whole run is a single prominent line, expose it as Markdown.
            if len(run_lines) == 1:
                level = _heading_level(run_lines[0], body_size)
                txt = normalize_prose_line(_line_text(run_lines[0]))
                if level and txt:
                    events.append({"y": y, "y_end": y_end, "kind": "heading", "content": "#" * level + " " + txt})
                    continue
                m = LIST_RE.match(txt)
                if m:
                    events.append({"y": y, "y_end": y_end, "kind": "list", "content": "- " + m.group(2).strip()})
                    continue
                m = ORDERED_RE.match(txt)
                if m:
                    events.append({"y": y, "y_end": y_end, "kind": "list", "content": f"{m.group(1)}. {m.group(2).strip()}"})
                    continue

            # Preserve list structure when a block contains multiple list lines.
            rendered_lines: list[str] = []
            ordinary: list[str] = []

            def flush_ordinary() -> None:
                if ordinary:
                    paragraph = _join_prose_lines(ordinary)
                    if paragraph:
                        rendered_lines.append(paragraph)
                    ordinary.clear()

            for line in run_lines:
                txt = normalize_prose_line(_line_text(line))
                if not txt:
                    continue
                level = _heading_level(line, body_size)
                if level:
                    flush_ordinary()
                    rendered_lines.append("#" * level + " " + txt)
                    continue
                m = LIST_RE.match(txt)
                if m:
                    flush_ordinary(); rendered_lines.append("- " + m.group(2).strip()); continue
                m = ORDERED_RE.match(txt)
                if m:
                    flush_ordinary(); rendered_lines.append(f"{m.group(1)}. {m.group(2).strip()}"); continue
                ordinary.append(txt)
            flush_ordinary()
            if rendered_lines:
                compact: list[str] = []
                for item in rendered_lines:
                    if compact and item.startswith("#") and compact[-1].startswith("#"):
                        a = re.match(r"^(#+)\s+(.*)$", compact[-1], re.S)
                        b = re.match(r"^(#+)\s+(.*)$", item, re.S)
                        if a and b and len(a.group(1)) == len(b.group(1)):
                            compact[-1] = a.group(1) + " " + a.group(2).rstrip() + " " + b.group(2).lstrip()
                            continue
                    compact.append(item)
                events.append({"y": y, "y_end": y_end, "kind": "prose", "content": "\n\n".join(compact)})

        if not block_ended_in_code and runs and not runs[-1][0]:
            recent_code_end = None
            recent_code_expects_output = False

    return events, code_fragments

def _coalesce_events(events: list[dict]) -> list[dict]:
    merged: list[dict] = []
    for event in events:
        if merged and event.get("kind") == "heading" and merged[-1].get("kind") == "heading":
            prev, cur = merged[-1], event
            prev_prefix = re.match(r"^(#+)\s+", prev.get("content", ""))
            cur_prefix = re.match(r"^(#+)\s+", cur.get("content", ""))
            if prev_prefix and cur_prefix and len(prev_prefix.group(1)) == len(cur_prefix.group(1)) and float(cur.get("y", 0)) - float(prev.get("y", 0)) <= 28:
                prev["content"] = prev["content"].rstrip() + " " + cur_prefix.string[cur_prefix.end():].strip()
                continue
        if merged and event.get("kind") == "code" and merged[-1].get("kind") == "code" and float(event.get("y", 0)) - float(merged[-1].get("y_end", merged[-1].get("y", 0))) <= 24:
            a = merged[-1]["content"].removeprefix("```text\n").removesuffix("\n```")
            b = event["content"].removeprefix("```text\n").removesuffix("\n```")
            merged[-1]["content"] = "```text\n" + a.rstrip() + "\n" + b.rstrip() + "\n```"
            merged[-1]["y_end"] = event.get("y_end", event.get("y", merged[-1].get("y_end")))
            continue
        merged.append(dict(event))
    return merged


def _semantic_pdf_page(page, plumber_page, root: Path, page_no: int, repeated: set[str]) -> tuple[str, dict[str, Any]]:
    page_dict = page.get_text("dict", sort=True)
    body_size = _body_font_size(page_dict, page.rect.height)
    table_events, table_bboxes = _extract_tables(plumber_page, root / "assets", page_no)
    visual_records, visual_events = _extract_visuals(page, page_dict, root, page_no)
    text_events, code_fragments = _render_text_events(page_dict, page.rect.height, body_size, repeated, table_bboxes)

    events = text_events + table_events + visual_events
    order = {"heading": 0, "prose": 1, "list": 1, "code": 1, "table_markdown": 1, "table_csv": 1, "visual": 2}
    events.sort(key=lambda e: (float(e.get("y", 0)), order.get(e.get("kind", ""), 1)))
    events = _coalesce_events(events)
    chunks = [f"<!-- source-page: {page_no} -->", ""]
    for event in events:
        if event["kind"] == "table_csv":
            content = f"[Structured table: {event['rows']} rows × {event['columns']} columns](../{event['file']})"
        else:
            content = event.get("content", "")
        if content:
            chunks.extend([content.rstrip(), ""])
    prepared = "\n".join(chunks).rstrip() + "\n"
    raw_text = page.get_text("text", sort=True) or ""
    integrity_payload = prepared
    for event in table_events:
        if event.get("kind") == "table_csv" and event.get("file"):
            csv_path = root / event["file"]
            if csv_path.is_file():
                integrity_payload += "\n" + csv_path.read_text(encoding="utf-8")
    metrics = _integrity_metrics(raw_text, integrity_payload, code_fragments)
    metrics["raw_code_signal_lines"] = _raw_code_signal_count(page_dict, page.rect.height, repeated)
    return prepared, {
        "body_font_size": body_size,
        "tables": [{k: v for k, v in e.items() if k != "content"} for e in table_events],
        "visuals": visual_records,
        "integrity": metrics,
    }


def _compatibility_baseline(text: str) -> list[str]:
    found: set[str] = set()
    for label, pattern in VERSION_PATTERNS:
        for match in pattern.finditer(text):
            found.add(f"{label} {match.group(1)}")
    # Some books state the exact engine version as "5.03 ... engine editor"
    # rather than prefixing it with "UE". Capture that only when the same
    # source line explicitly names Unreal/UE/engine context.
    for line in text.splitlines():
        if re.search(r"\b(?:unreal|UE5?|engine)\b", line, re.I):
            for match in re.finditer(r"\b(5\.\d{1,2}(?:\.\d{1,2})?)\b", line):
                found.add(f"Unreal Engine {match.group(1)}")
    return sorted(found)


def render_index(source_name: str, rows: list[dict], compatibility: list[str]) -> str:
    lines = [
        f"# Prepared source: {source_name}", "",
        "This is model-facing PASS working input. The original source remains the archival truth.", "",
    ]
    if compatibility:
        lines += ["**Detected compatibility/version baseline:** " + "; ".join(compatibility), ""]
    lines += [
        "| Segment | PDF/source page | Nonspace chars | Est. tokens | Low text | Tables | Visuals | Integrity |",
        "|---|---:|---:|---:|---|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| [{row['file']}]({row['file']}) | {row['page']} | {row['chars']} | {row['tokens']} | "
            f"{'yes' if row['low_text'] else 'no'} | {row.get('tables', 0)} | {row.get('visuals', 0)} | "
            f"{row.get('integrity_ratio', 1.0):.2f} |"
        )
    return "\n".join(lines) + "\n"


def prepare(run: Run, min_text_chars: int = 80, force: bool = False) -> dict:
    if run.state["phase"] != "source_prep":
        raise RunError(f"source preparation is available only in source_prep; current phase is {run.state['phase']}")
    source = run.source_file(required=True)
    root = package_root(run)
    raw = raw_root(run)
    if root.exists() and not force:
        raise RunError("prepared-source already exists; verify/finalize it or use --force to regenerate deterministically")
    if force:
        import shutil
        shutil.rmtree(root, ignore_errors=True)
        shutil.rmtree(raw, ignore_errors=True)
    root.mkdir(parents=True, exist_ok=True)
    raw.mkdir(parents=True, exist_ok=True)

    rows: list[dict] = []
    page_manifest: list[dict] = []
    full_prepared_text: list[str] = []
    suffix = source.suffix.casefold()
    if suffix == ".pdf":
        try:
            import fitz  # PyMuPDF
            import pdfplumber
        except ImportError as exc:
            raise RunError("PyMuPDF and pdfplumber are required for semantic PDF Source Prep") from exc
        doc = fitz.open(source)
        repeated = _collect_repeated_furniture(doc)
        pages = root / "pages"
        raw_pages = raw / "pages"
        pages.mkdir()
        raw_pages.mkdir()
        with pdfplumber.open(source) as plumber:
            for index, page in enumerate(doc, 1):
                try:
                    raw_text = page.get_text("text", sort=True) or ""
                    prepared, detail = _semantic_pdf_page(page, plumber.pages[index - 1], root, index, repeated)
                except Exception as exc:
                    raise RunError(f"PDF semantic extraction failed on page {index}: {exc}") from exc
                raw_file = raw_pages / f"P{index:04d}.txt"
                raw_file.write_text(raw_text, encoding="utf-8", newline="\n")
                out = pages / f"P{index:04d}.md"
                out.write_text(prepared, encoding="utf-8", newline="\n")
                full_prepared_text.append(prepared)
                chars = len(re.sub(r"\s+", "", prepared))
                ratio = float(detail["integrity"]["coverage_ratio"])
                code_ok = detail["integrity"]["code_blocks"] == detail["integrity"]["code_blocks_preserved"]
                warnings: list[str] = []
                if ratio < 0.62:
                    warnings.append("low lexical coverage; inspect layout/tables/visual dependence")
                if not code_ok:
                    warnings.append("one or more detected code blocks failed exact prepared-text preservation")
                raw_code_signals = int(detail["integrity"].get("raw_code_signal_lines", 0))
                if raw_code_signals >= 2 and detail["integrity"]["code_blocks"] == 0 and not detail.get("tables"):
                    warnings.append("code-like/preformatted source lines detected but no code block or structured table was classified")
                row = {
                    "page": index,
                    "file": f"pages/{out.name}",
                    "chars": chars,
                    "tokens": max(1, round(len(prepared) / 4)) if prepared else 0,
                    "low_text": chars < min_text_chars,
                    "tables": len(detail["tables"]),
                    "visuals": len(detail["visuals"]),
                    "integrity_ratio": ratio,
                }
                rows.append(row)
                page_manifest.append({
                    **row,
                    "sha256": digest(out),
                    "raw_sha256": digest(raw_file),
                    "body_font_size": detail["body_font_size"],
                    "table_inventory": detail["tables"],
                    "visual_inventory": detail["visuals"],
                    "integrity": detail["integrity"],
                    "warnings": warnings,
                })
        doc.close()
        backend = "pymupdf+pdfplumber"
        source_kind = "pdf"
    elif suffix in SUPPORTED_TEXT:
        raw_text = source.read_text(encoding="utf-8", errors="strict")
        normalized = normalize_text(raw_text)
        raw_file = raw / "source.txt"
        raw_file.write_text(raw_text, encoding="utf-8", newline="\n")
        out = root / "source.md"
        out.write_text(normalized + "\n", encoding="utf-8", newline="\n")
        full_prepared_text.append(normalized)
        chars = len(re.sub(r"\s+", "", normalized))
        metrics = _integrity_metrics(raw_text, normalized, [])
        rows.append({"page": 1, "file": "source.md", "chars": chars, "tokens": max(1, round(len(normalized)/4)) if normalized else 0, "low_text": False, "tables": 0, "visuals": 0, "integrity_ratio": metrics["coverage_ratio"]})
        page_manifest.append({**rows[0], "sha256": digest(out), "raw_sha256": digest(raw_file), "table_inventory": [], "visual_inventory": [], "integrity": metrics, "warnings": []})
        backend = "utf8-text"
        source_kind = "text"
    else:
        raise RunError(
            f"deterministic source prep does not yet support {source.suffix or 'extensionless files'}; "
            "convert/extract it to PDF, Markdown, or text before finalizing source prep"
        )

    compatibility = _compatibility_baseline("\n".join(full_prepared_text))
    atomic_write(index_path(run), render_index(source.name, rows, compatibility).encode("utf-8"))
    files = package_files(run)
    identity = run.source_identity()
    aggregate_warnings = [
        {"page": seg["page"], "warning": warning}
        for seg in page_manifest for warning in seg.get("warnings", [])
    ]
    total_code_signals = sum(int((seg.get("integrity") or {}).get("raw_code_signal_lines", 0)) for seg in page_manifest)
    total_code_blocks = sum(int((seg.get("integrity") or {}).get("code_blocks", 0)) for seg in page_manifest)
    if total_code_signals >= 5 and total_code_blocks == 0:
        aggregate_warnings.append({
            "page": None,
            "warning": f"source-wide code sanity check: {total_code_signals} code-like/preformatted lines but zero detected code blocks",
        })
    manifest = {
        "schema_version": PREP_SCHEMA,
        "source": {"name": identity["name"], "size": identity["size"], "sha256": identity["sha256"]},
        "source_kind": source_kind,
        "extractor": backend,
        "normalization": "semantic Markdown; code/preformatted whitespace preserved; conservative printed-hyphen handling; tables structured; visuals inventoried and retained on demand",
        "preservation_contract": "no summarization, paraphrase, author correction, or silent ambiguous dehyphenation",
        "low_text_threshold": min_text_chars,
        "compatibility_baseline": compatibility,
        "integrity_gate": {
            "status": "warning" if aggregate_warnings else "pass",
            "warnings": aggregate_warnings,
            "policy": "code blocks must be exactly preserved in prepared Markdown; code-like source signals are independently sanity-checked; low lexical coverage is surfaced for inspection rather than silently repaired",
            "raw_code_signal_lines": total_code_signals,
            "detected_code_blocks": total_code_blocks,
        },
        "segments": page_manifest,
        "unit_files": {},
        "files": files,
        "package_sha256": package_digest(files),
    }
    atomic_write(manifest_path(run), (json.dumps(manifest, indent=2) + "\n").encode("utf-8"))
    return manifest


def verify(run: Run) -> dict:
    path = manifest_path(run)
    if not path.is_file():
        raise RunError("prepared-source/source.json is missing; run deterministic source preparation first")
    data = preflight._read_json(str(path))
    required = {"schema_version", "source", "source_kind", "extractor", "normalization", "preservation_contract", "low_text_threshold", "compatibility_baseline", "integrity_gate", "segments", "unit_files", "files", "package_sha256"}
    if set(data) != required or data["schema_version"] != PREP_SCHEMA:
        raise RunError("unsupported or malformed prepared source manifest")
    identity = run.source_identity()
    if data["source"].get("sha256") != identity["sha256"] or data["source"].get("size") != identity["size"]:
        raise RunError("prepared source belongs to different source bytes")
    actual = package_files(run)
    if actual != data["files"] or package_digest(actual) != data["package_sha256"]:
        raise RunError("prepared source files changed after manifest creation; regenerate/finalize the package")
    for segment in data["segments"]:
        file = inside(package_root(run), segment["file"])
        if not file.is_file() or digest(file) != segment["sha256"]:
            raise RunError(f"prepared source segment failed verification: {segment.get('file')}")
        integrity = segment.get("integrity") or {}
        if integrity.get("code_blocks") != integrity.get("code_blocks_preserved"):
            raise RunError(f"prepared source code-preservation gate failed: {segment.get('file')}")
    return data


def locator_pages(locator: str, page_count: int) -> list[int] | None:
    match = PAGE_RE.search(locator)
    if match:
        start, end = int(match.group(1)), int(match.group(2))
        if 1 <= start <= end <= page_count:
            return list(range(start, end + 1))
    single = SINGLE_PAGE_RE.search(locator)
    if single:
        page = int(single.group(1))
        if 1 <= page <= page_count:
            return [page]
    return None


def _locator_label(locator: str) -> str:
    # Existing beta.78 records often say simply "pp. 1-18". Materialized unit
    # files make the coordinate system explicit without mutating the accepted
    # preflight record.
    if re.match(r"^\s*(?:pp?\.)", locator, re.I):
        return "PDF/source " + locator.strip()
    return locator.strip()


def materialize_units(run: Run) -> dict[str, str]:
    """Build unit Markdown from accepted page locators when deterministic."""
    if not run.state.get("plan"):
        return {}
    manifest = verify(run)
    if manifest["source_kind"] != "pdf":
        return {}
    page_count = len(manifest["segments"])
    units_dir = package_root(run) / "units"
    units_dir.mkdir(exist_ok=True)
    unit_files: dict[str, str] = {}
    for unit in run.state["plan"]["units"]:
        pages = locator_pages(unit["locator"], page_count)
        if not pages:
            continue
        parts = [f"# {unit['unit_id'].upper()} — {unit['material']}", "", f"Source locator: {_locator_label(unit['locator'])}", ""]
        if manifest.get("compatibility_baseline"):
            parts += ["Compatibility/version signals detected in source: " + "; ".join(manifest["compatibility_baseline"]), ""]
        for page in pages:
            p = package_root(run) / "pages" / f"P{page:04d}.md"
            parts.append(p.read_text(encoding="utf-8").rstrip())
            parts.append("")
        out = units_dir / f"{unit['unit_id'].upper()}.md"
        out.write_text("\n".join(parts).rstrip() + "\n", encoding="utf-8", newline="\n")
        unit_files[unit["unit_id"]] = out.relative_to(package_root(run)).as_posix()
    # Unit files are routing derivatives; refresh the package manifest atomically.
    manifest["unit_files"] = unit_files
    files = package_files(run)
    manifest["files"] = files
    manifest["package_sha256"] = package_digest(files)
    atomic_write(manifest_path(run), (json.dumps(manifest, indent=2) + "\n").encode("utf-8"))
    return unit_files


def finalize(run: Run) -> str:
    manifest = verify(run)
    run.state["source_prep"] = {
        "status": "verified",
        "package": "prepared-source",
        "package_sha256": manifest["package_sha256"],
        "segments": len(manifest["segments"]),
        "extractor": manifest["extractor"],
        "integrity": manifest["integrity_gate"]["status"],
        "compatibility_baseline": manifest.get("compatibility_baseline", []),
    }
    run.state["phase"] = "preflight"
    if run.state.get("stop_after") == "source_prep":
        run.state["stop_reached"] = True
    run.save()
    suffix = " (stop target reached)" if run.state.get("stop_reached") else ""
    warning = " — review Source Prep warnings before preflight" if manifest["integrity_gate"]["status"] == "warning" else ""
    return "SOURCE PREP: verified" + warning + " — preflight is next" + suffix


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path)
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("prepare", "verify", "finalize"):
        p = sub.add_parser(command)
        p.add_argument("--run", type=Path, required=True)
        if command == "prepare":
            p.add_argument("--min-text-chars", type=int, default=80)
            p.add_argument("--force", action="store_true")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)
    try:
        repo = args.repo_root.resolve() if args.repo_root else preflight.find_repo_root(Path.cwd())
        run = Run(repo, args.run)
        if args.command == "verify":
            print(json.dumps(verify(run), indent=2))
            return 0
        with run.locked():
            if args.command == "prepare":
                result = prepare(run, args.min_text_chars, args.force)
                # Preparation itself is a recoverable accepted transaction even
                # before finalization; record its current package in state.
                run.state["source_prep"] = {
                    "status": "prepared",
                    "package": "prepared-source",
                    "package_sha256": result["package_sha256"],
                    "segments": len(result["segments"]),
                    "extractor": result["extractor"],
                    "integrity": result["integrity_gate"]["status"],
                    "compatibility_baseline": result.get("compatibility_baseline", []),
                }
                run.save()
                print(json.dumps(run.state["source_prep"], indent=2))
            elif args.command == "finalize":
                print(finalize(run))
        return 0
    except (OSError, RunError, preflight.PreflightError) as exc:
        print(f"SOURCE PREP BLOCKED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
