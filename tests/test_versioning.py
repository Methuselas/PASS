"""Tests for the public PASS Semantic Versioning contract."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEMVER_RE = re.compile(
    r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-((?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*)"
    r"(?:\.(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*))*))?"
    r"(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
)


class VersioningContractTests(unittest.TestCase):
    def test_version_is_semver_and_documented(self) -> None:
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        self.assertIsNotNone(SEMVER_RE.fullmatch(version))
        self.assertIn(version, (ROOT / "README.md").read_text(encoding="utf-8"))
        self.assertIn(
            f"## {version}",
            (ROOT / "CHANGELOG.md").read_text(encoding="utf-8"),
        )


if __name__ == "__main__":
    unittest.main()
