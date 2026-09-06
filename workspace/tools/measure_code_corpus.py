#!/usr/bin/env python3
"""Measure structural properties of a source corpus.

Why this exists
---------------
Skillset Memory entries about *coding* need evidence, and the person who owns this
repository is not a C++ programmer. For Art, the owner's own eye is the ground
truth. For code there is no equivalent judgement available — so the evidence has
to be mechanical, reproducible, and runnable by someone who cannot read the code
being measured.

That is all this does. It counts a few things and prints them. It makes no
judgements, and a number here is not a verdict.

Usage
-----
    python workspace/tools/measure_code_corpus.py PATH [PATH ...] --label NAME

    # several corpora side by side, one --label per path:
    python workspace/tools/measure_code_corpus.py \
        path/to/corpus-a path/to/corpus-b \
        --label "human 2001" --label "agent"

The language of each corpus is detected from the files present and printed in the
`lang` column. Override it with --lang when a tree is mixed and you want one
language measured, or when detection picks the wrong one.

What the numbers mean
---------------------
asserts/kloc     Assertions per thousand non-blank, non-comment lines. An
                 assertion states that something must never be false and stops
                 the program when it is. Low numbers mean broken assumptions
                 travel silently instead of reporting themselves.
guards/kloc      Early-return checks (`if (!x) return ...`). These handle a
                 condition rather than forbidding it. High guards with low
                 asserts is the shape worth noticing.
attr/kloc        Uses of the language's "do not ignore this result" attribute:
                 [[nodiscard]] in C++, #[must_use] in Rust. Printed as `-` where
                 the language has no equivalent, which is not the same as zero.
com/code         Comment lines per code line.
median file      Median file length in lines.

Adding a language
-----------------
Add an entry to LANGUAGES. A language module under
`library/software-engineering/languages/<name>/` should have a profile here with
the same name, so a corpus in that language can be measured against the cards
written for it.

Known limits — read these before quoting a number
-------------------------------------------------
* The counts come from regular expressions, not a parser. A project-specific
  assertion macro with an unusual name may be missed; pass --assert-pattern.
* Comment ratio is inflated by house styles that mandate a file prolog.
* Python docstrings count as code, not comment. Telling a docstring from any
  other string expression needs a parser, and this is not one.
* Era matters. A 2001 codebase with a cheap project-wide assert macro will
  assert more than a modern one that has to include a header first, and that is
  a fact about the infrastructure as much as about the author.
* Headers are measured by default for C and C++. Excluding them undersamples any
  codebase that keeps logic in headers, which modern C++ often does — in one
  corpus measured here, implementation files held under a tenth of the code.
* Test files are excluded by default, because assertion density inside a test
  suite measures the suite rather than the code under test. In one Go corpus the
  testify calls outnumbered every other assertion form by two orders of
  magnitude and lived almost entirely in `_test.go`. Pass --include-tests to
  measure them. The C++ baselines already recorded in Skillset Memory were taken
  before this option existed, with tests included; re-measure before comparing
  a new number against them.
* Rust and Go inline their unit tests inside ordinary files (`#[cfg(test)]`,
  `TestXxx` funcs). Only whole test *files* are excluded, so inline tests are
  still counted, and for Rust that dominates the figure rather than nudging it:
  in one corpus measured here, 86 per cent of all assertions sat in files
  carrying a `#[cfg(test)]` module, giving an assertion rate roughly thirty times
  the C++ corpora beside it. Read a Rust assert figure as "asserts plus unit
  tests" until someone teaches this tool to see block scope.
* One corpus is one sample. Two corpora that agree are two samples.
"""

from __future__ import annotations

import argparse
import os
import re
import statistics
import sys

SKIP_DIR_MARKERS = ("3rdparty", "3rd_party", "third_party", "external",
                    "vcpkg", "_deps", "build", "node_modules", ".git",
                    "vendor", "site-packages", "target/debug", "target/release")

C_FAMILY_ASSERT = r"\b[A-Za-z_]*(?:ASSERT|Assert|assert)\s*\("
C_FAMILY_GUARD = r"if\s*\(\s*!?\w+(?:\s*(?:==|!=)\s*(?:nullptr|NULL|0))?\s*\)\s*\n?\s*\{?\s*\n?\s*return"

# One entry per language. `attr` is (column meaning, regex) or None where the
# language has no "result must not be ignored" marker.
LANGUAGES: dict[str, dict] = {
    "c": {
        "impl": (".c",),
        "detect": (".c",),
        "headers": (".h",),
        "line_comment": "//",
        "block_comment": ("/*", "*/"),
        "assert": C_FAMILY_ASSERT,
        "guard": C_FAMILY_GUARD,
        "attr": None,
        "test_files": (r"_test\.c$", r"^test_.*\.c$"),
    },
    "cpp": {
        "impl": (".cpp", ".cc", ".cxx", ".c"),
        "detect": (".cpp", ".cc", ".cxx"),
        "headers": (".h", ".hpp", ".hxx", ".inl"),
        "line_comment": "//",
        "block_comment": ("/*", "*/"),
        "assert": C_FAMILY_ASSERT,
        "guard": C_FAMILY_GUARD,
        "attr": ("[[nodiscard]]", r"nodiscard"),
        "test_files": (r"_test\.(cpp|cc|cxx)$", r"^test_.*\.(cpp|cc|cxx)$"),
    },
    "go": {
        "impl": (".go",),
        "detect": (".go",),
        "headers": (),
        "line_comment": "//",
        "block_comment": ("/*", "*/"),
        # Go has no assert statement; panic is the nearest "this must not happen".
        "assert": r"\bpanic\s*\(",
        "guard": r"if\s+[^\n{]*!=\s*nil\s*\{\s*\n?\s*return",
        "attr": None,
        "test_files": (r"_test\.go$",),
    },
    "python": {
        "impl": (".py",),
        "detect": (".py",),
        "headers": (),
        "line_comment": "#",
        "block_comment": None,
        "assert": r"^\s*assert\s",
        "guard": r"if\s+[^\n:]+:\s*\n?\s*return",
        "attr": None,
        "test_files": (r"^test_.*\.py$", r"_test\.py$", r"^conftest\.py$"),
    },
    "rust": {
        "impl": (".rs",),
        "detect": (".rs",),
        "headers": (),
        "line_comment": "//",
        "block_comment": ("/*", "*/"),
        "assert": r"\b(?:debug_)?assert(?:_eq|_ne)?!",
        "guard": r"if\s+[^\n{]*\.is_none\(\)\s*\{\s*\n?\s*return",
        "attr": ("#[must_use]", r"must_use"),
        "test_files": (r"^tests?\.rs$",),
    },
}


def is_test_file(name: str, profile: dict) -> bool:
    return any(re.search(p, name) for p in profile["test_files"])


def collect_sources(root: str, profile: dict, include_headers: bool,
                    include_tests: bool) -> list[str]:
    suffixes = profile["impl"] + (profile["headers"] if include_headers else ())
    if not suffixes:
        return []
    found: list[str] = []
    for current, dirs, files in os.walk(root):
        lowered = current.lower().replace("\\", "/")
        if any(marker in lowered for marker in SKIP_DIR_MARKERS):
            dirs[:] = []
            continue
        in_test_dir = "/tests/" in lowered + "/" or lowered.endswith("/tests")
        for name in files:
            if not name.endswith(suffixes):
                continue
            if not include_tests and (in_test_dir or is_test_file(name, profile)):
                continue
            found.append(os.path.join(current, name))
    return sorted(found)


def detect_language(root: str) -> str | None:
    """Pick the language with the most distinctive source files under root.

    Detection counts only each language's distinctive suffixes, which is not the
    same set it measures: a C++ corpus routinely vendors .c files and they belong
    in its numbers, but a tree holding nothing but .c is C.
    """
    counts: dict[str, int] = {name: 0 for name in LANGUAGES}
    for current, dirs, files in os.walk(root):
        lowered = current.lower().replace("\\", "/")
        if any(marker in lowered for marker in SKIP_DIR_MARKERS):
            dirs[:] = []
            continue
        for name in files:
            for lang, profile in LANGUAGES.items():
                if name.endswith(profile["detect"]):
                    counts[lang] += 1
    best = max(counts, key=lambda n: counts[n])
    return best if counts[best] else None


def measure(root: str, profile: dict, assert_pattern: str | None,
            include_headers: bool, include_tests: bool) -> dict | None:
    sources = collect_sources(root, profile, include_headers, include_tests)
    if not sources:
        return None

    assert_re = re.compile(assert_pattern or profile["assert"], re.MULTILINE)
    guard_re = re.compile(profile["guard"])
    attr_re = re.compile(profile["attr"][1]) if profile["attr"] else None
    line_token = profile["line_comment"]
    block = profile["block_comment"]

    code = comment = blank = 0
    asserts = guards = attrs = 0
    lengths: list[int] = []

    for path in sources:
        try:
            text = open(path, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue

        lines = text.split("\n")
        lengths.append(len(lines))

        in_block = False
        for raw in lines:
            line = raw.strip()
            if not line:
                blank += 1
                continue
            if in_block:
                comment += 1
                if block and block[1] in line:
                    in_block = False
                continue
            if line.startswith(line_token):
                comment += 1
                continue
            if block and line.startswith(block[0]):
                comment += 1
                if block[1] not in line:
                    in_block = True
                continue
            code += 1

        asserts += len(assert_re.findall(text))
        guards += len(guard_re.findall(text))
        if attr_re:
            attrs += len(attr_re.findall(text))

    per_kloc = lambda n: (n / code * 1000) if code else 0.0
    return {
        "files": len(sources),
        "code": code,
        "comment_ratio": (comment / code) if code else 0.0,
        "blank_ratio": (blank / (code + comment + blank)) if (code + comment + blank) else 0.0,
        "asserts_kloc": per_kloc(asserts),
        "guards_kloc": per_kloc(guards),
        "attr_kloc": per_kloc(attrs) if attr_re else None,
        "median_file": int(statistics.median(lengths)) if lengths else 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Measure structural properties of one or more source corpora.",
        epilog="Numbers are evidence, not verdicts. See the header of this file for limits.",
    )
    parser.add_argument("paths", nargs="+", help="Directory roots to measure.")
    parser.add_argument("--label", action="append", default=[],
                        help="Label for the corresponding path. Repeat once per path.")
    parser.add_argument("--lang", action="append", default=[],
                        choices=sorted(LANGUAGES),
                        help="Force the language for the corresponding path. "
                             "Detected from the files present when omitted.")
    parser.add_argument("--impl-only", action="store_true",
                        help="Measure only implementation files. Off by default: modern C++ "
                             "puts real logic in headers, and skipping them undersamples such "
                             "code badly. No effect on languages without headers.")
    parser.add_argument("--include-tests", action="store_true",
                        help="Count test files too. Off by default: assertion density inside a "
                             "test suite measures the suite, not the code under test.")
    parser.add_argument("--assert-pattern", default=None,
                        help="Regex for this project's assertion macro, if it has an unusual "
                             "name. Applies to every path in the run.")
    args = parser.parse_args()

    labels = list(args.label)
    while len(labels) < len(args.paths):
        labels.append(os.path.basename(os.path.normpath(args.paths[len(labels)])))

    langs = list(args.lang)
    while len(langs) < len(args.paths):
        langs.append(None)

    header = (f"{'corpus':<22}{'lang':>8}{'files':>7}{'code':>9}{'com/code':>10}"
              f"{'asserts/kloc':>14}{'guards/kloc':>13}{'attr/kloc':>11}{'med file':>10}")
    print(header)
    print("-" * len(header))

    missing = False
    for path, label, forced in zip(args.paths, labels, langs):
        if not os.path.isdir(path):
            print(f"{label:<22}  no such directory: {path}")
            missing = True
            continue
        lang = forced or detect_language(path)
        if lang is None:
            print(f"{label:<22}  no sources of any known language found under {path}")
            missing = True
            continue
        result = measure(path, LANGUAGES[lang], args.assert_pattern,
                         not args.impl_only, args.include_tests)
        if result is None:
            print(f"{label:<22}  no {lang} sources found under {path}")
            missing = True
            continue
        attr = "-" if result["attr_kloc"] is None else f"{result['attr_kloc']:.1f}"
        print(f"{label:<22}{lang:>8}{result['files']:>7}{result['code']:>9}"
              f"{result['comment_ratio']:>10.3f}{result['asserts_kloc']:>14.1f}"
              f"{result['guards_kloc']:>13.1f}{attr:>11}"
              f"{result['median_file']:>10}")

    print()
    print("attr/kloc is [[nodiscard]] in C++ and #[must_use] in Rust; `-` means the language")
    print("has no equivalent, which is not the same as zero. Counts come from regular")
    print("expressions, not a parser. Comment ratio is inflated by mandatory file prologs.")
    print("Test files are excluded unless --include-tests. One corpus is one sample.")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
