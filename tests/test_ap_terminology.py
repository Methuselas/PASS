"""AP always expands to Action Protocol.

Models keep expanding AP as "Action Pattern", "Action Procedure", "action plan"
and similar. Each of those names a different idea, and a wrong expansion in a
card, doc, memory entry or changelog teaches the next reader the wrong object
type. This test scans the repository's prose for them.

Text inside double quotes or backticks is exempt, so a changelog entry may
quote a wrong form while recording its repair.
"""

from __future__ import annotations

import os
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
THIS_FILE = Path(__file__).resolve()

SKIPPED_DIRS = {".git", "workspace", "archive", "node_modules", "__pycache__"}
SCANNED_SUFFIXES = {".md", ".yaml", ".yml", ".json", ".jsonl", ".txt", ".py"}

# "action" followed by a P-word that is not "protocol". Wrapped prose is
# handled by matching across any whitespace, including line breaks.
WRONG_EXPANSION = re.compile(
    r"\baction[\s-]+(?:pattern|procedure|plan|program|programme|playbook|pipeline|primitive)s?\b",
    re.IGNORECASE,
)
# "AP (Action ...)" or "APs (action ...)" whose expansion is not Protocol.
WRONG_PAREN = re.compile(
    r"\bAPs?\s*\(\s*action\s+(?!protocols?\b)\w+",
    re.IGNORECASE,
)
# Quoted spans are exempt; bounded so one stray quote cannot hide a file.
QUOTED = re.compile(r'"[^"]{0,160}"|`[^`]{0,160}`|“[^”]{0,160}”')


def iter_scanned_files():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        # Prune skipped trees before descending; workspace/ alone holds
        # hundreds of megabytes of prepared sources.
        dirnames[:] = [name for name in dirnames if name not in SKIPPED_DIRS]
        for filename in filenames:
            path = Path(dirpath) / filename
            if path.suffix.lower() not in SCANNED_SUFFIXES or path.resolve() == THIS_FILE:
                continue
            yield path, path.relative_to(ROOT)


def wrong_expansions(text: str) -> list[str]:
    flattened = re.sub(r"\s+", " ", text)
    unquoted = QUOTED.sub(" ", flattened)
    found = [match.group(0) for match in WRONG_EXPANSION.finditer(unquoted)]
    found += [match.group(0) for match in WRONG_PAREN.finditer(unquoted)]
    return found


class ApTerminologyTests(unittest.TestCase):
    def test_detector_flags_wrong_expansions(self) -> None:
        for text in (
            "15 Action Procedures",
            "an Action Pattern owns the order",
            "the naming action\n  plan",
            "AP (Action Pattern)",
            "APs (action procedures)",
        ):
            with self.subTest(text=text):
                self.assertTrue(wrong_expansions(text))

    def test_detector_allows_correct_and_quoted_forms(self) -> None:
        for text in (
            "15 Action Protocols",
            "AP (Action Protocol)",
            'README said "ordered action procedures" and was repaired',
            "the old name `Action Pattern` is retired",
            "an action path through the body",
            "the action line carries the gesture",
        ):
            with self.subTest(text=text):
                self.assertEqual(wrong_expansions(text), [])

    def test_repository_never_misexpands_ap(self) -> None:
        offenders = []
        for path, relative in iter_scanned_files():
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for phrase in wrong_expansions(text):
                offenders.append(f"{relative.as_posix()}: {phrase!r}")
        self.assertEqual(
            offenders,
            [],
            "AP means Action Protocol. Fix these, or quote a wrong form when recording a repair:\n"
            + "\n".join(offenders),
        )


if __name__ == "__main__":
    unittest.main()
