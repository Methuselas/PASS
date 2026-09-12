"""Tests for the public PASS Semantic Versioning contract."""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "PASS/tools"
sys.path.insert(0, str(TOOLS))

import build_release  # noqa: E402


SEMVER_RE = re.compile(
    r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-((?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*)"
    r"(?:\.(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*))*))?"
    r"(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
)


def compare_semver(left: str, right: str) -> int:
    left_match = SEMVER_RE.fullmatch(left)
    right_match = SEMVER_RE.fullmatch(right)
    if left_match is None or right_match is None:
        raise ValueError("compare_semver requires valid Semantic Versions")

    left_core = tuple(int(left_match.group(index)) for index in range(1, 4))
    right_core = tuple(int(right_match.group(index)) for index in range(1, 4))
    if left_core != right_core:
        return 1 if left_core > right_core else -1

    left_pre = left_match.group(4)
    right_pre = right_match.group(4)
    if left_pre is None or right_pre is None:
        if left_pre == right_pre:
            return 0
        return 1 if left_pre is None else -1

    left_parts = left_pre.split(".")
    right_parts = right_pre.split(".")
    for left_part, right_part in zip(left_parts, right_parts):
        if left_part == right_part:
            continue
        left_numeric = left_part.isdigit()
        right_numeric = right_part.isdigit()
        if left_numeric and right_numeric:
            return 1 if int(left_part) > int(right_part) else -1
        if left_numeric != right_numeric:
            return -1 if left_numeric else 1
        return 1 if left_part > right_part else -1
    if len(left_parts) == len(right_parts):
        return 0
    return 1 if len(left_parts) > len(right_parts) else -1


class VersioningContractTests(unittest.TestCase):
    def test_version_is_semver_and_documented(self) -> None:
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        self.assertIsNotNone(SEMVER_RE.fullmatch(version))
        self.assertIn(version, (ROOT / "README.md").read_text(encoding="utf-8"))
        self.assertIn(
            f"## {version}",
            (ROOT / "CHANGELOG.md").read_text(encoding="utf-8"),
        )

    def test_semver_precedence(self) -> None:
        self.assertLess(compare_semver("1.0.0-beta.9", "1.0.0-beta.10"), 0)
        self.assertLess(compare_semver("1.0.0-beta.10", "1.0.0"), 0)
        self.assertLess(compare_semver("1.0.0", "1.0.1"), 0)
        self.assertEqual(compare_semver("1.0.0+one", "1.0.0+two"), 0)

    def test_working_or_committed_version_advances(self) -> None:
        inside = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if inside.returncode or inside.stdout.strip() != "true":
            self.skipTest("exported tree has no Git ancestry")

        current = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        head = subprocess.run(
            ["git", "show", "HEAD:VERSION"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        ).stdout.strip()
        if current != head:
            self.assertGreater(
                compare_semver(current, head),
                0,
                f"working VERSION {current} must advance beyond HEAD {head}",
            )
            return

        parent = subprocess.run(
            ["git", "show", "HEAD^:VERSION"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if parent.returncode:
            self.skipTest("initial commit has no parent VERSION")
        parent_version = parent.stdout.strip()
        self.assertGreater(
            compare_semver(current, parent_version),
            0,
            f"committed VERSION {current} must advance beyond first parent {parent_version}",
        )

    def test_publishable_version_rejects_unreleased_notes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "VERSION").write_text("1.2.3\n", encoding="utf-8")
            (root / "README.md").write_text(
                "Current version `1.2.3`.\n",
                encoding="utf-8",
            )
            (root / "CHANGELOG.md").write_text(
                "# Changelog\n\n## Unreleased\n\n- Pending.\n\n"
                "## 1.2.3 - 2026-09-11\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "substantive Unreleased notes"):
                build_release.read_publishable_pass_version(root)

    def test_current_version_is_publishable(self) -> None:
        self.assertEqual(
            build_release.read_publishable_pass_version(ROOT),
            (ROOT / "VERSION").read_text(encoding="utf-8").strip(),
        )


if __name__ == "__main__":
    unittest.main()
