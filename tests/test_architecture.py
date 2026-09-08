"""Architecture tests for the PASS authoring environment and SkillForge releases.

These encode the invariants the 2026-08-15 cleanup restored: a finished skill
library is valid on its own, each domain stands alone, and nothing here needs a
source PDF, an authoring ledger, a workspace, or a provenance receipt.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
LIBRARY = ROOT / "library"
MEMORY = ROOT / "memory"
BUILDER = ROOT / "PASS/tools/build_release.py"
RUNTIME = ROOT / "PASS/runtime/skillforge_runtime.py"
VALIDATOR = ROOT / "PASS/tools/validate.py"
RECIPES = ROOT / "workspace/release-recipes"
CANONICAL_RECIPES = tuple(sorted(RECIPES.glob("SkillForge_*.yaml")))
ART_RECIPE = RECIPES / "SkillForge_Art.yaml"
SOFTWARE_ENGINEERING_RECIPE = RECIPES / "SkillForge_Software_Engineering.yaml"
SHARED_PACKAGE = "metaskills"
# Discovered, not hardcoded: a lane may be absent or empty while it is being
# rebuilt, and the invariant is about the domains that exist, not a fixed list.
DOMAINS = tuple(
    sorted(
        path.name
        for path in LIBRARY.iterdir()
        if path.is_dir()
        and path.name != SHARED_PACKAGE
        and any(p.name != "INDEX.md" for p in path.rglob("*.md"))
    )
)
RETIRED_STATE = ("workspace", "sources", "ledger", "provenance", "renders", "tmp")


RULE_LEAD_RE = re.compile(r"^\s*(?:[-*]|\d+\.)\s+\*\*(.+?)\*\*", re.MULTILINE | re.DOTALL)


def agent_rule_leads(filename: str, heading: str) -> set[str]:
    """Bold lead sentences of the rules under `heading`, normalized for comparison.

    Whitespace and line wrapping differ between the two files; the wording must
    not. Normalizing newlines lets each file wrap to its own width.
    """
    text = (ROOT / filename).read_text(encoding="utf-8")
    start = text.index(heading) + len(heading)
    rest = text[start:]
    end = rest.find("\n## ")
    section = rest if end == -1 else rest[:end]
    return {" ".join(lead.split()) for lead in RULE_LEAD_RE.findall(section)}


def run(*args: object) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(BUILDER), *map(str, args)],
        text=True, capture_output=True, cwd=ROOT,
    )


def validate(*args: object) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), *map(str, args)],
        text=True, capture_output=True, cwd=ROOT,
    )


def cards(library: Path) -> list[Path]:
    return [
        path for path in library.rglob("*.md")
        if path.name not in {"README.md", "INDEX.md"}
    ]


def frontmatter(card: Path) -> dict:
    raw = card.read_text(encoding="utf-8")
    return yaml.safe_load(raw.split("---\n", 2)[1])


def isolated_library() -> tempfile.TemporaryDirectory:
    """A checkout containing the library and tools and nothing else.

    Everything the retired architecture used to require — source payloads, the
    authoring ledger, workspace state, provenance receipts — is simply absent.
    """
    tmp = tempfile.TemporaryDirectory()
    root = Path(tmp.name)
    shutil.copytree(LIBRARY, root / "library")
    shutil.copytree(ROOT / "PASS", root / "PASS", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(RECIPES, root / "recipes")
    shutil.copytree(ROOT / "LICENSES", root / "LICENSES")
    for name in (
        "CHANGELOG.md", "CONTRIBUTING.md", "LICENSE.md", "NOTICE.md",
        "TRADEMARKS.md", "VERSION",
    ):
        shutil.copy2(ROOT / name, root / name)
    return tmp


def write_fixture_pattern(
    source: Path,
    target: Path,
    object_id: str,
    library_path: list[str],
    *,
    cross_links: list[dict[str, str]] | None = None,
    references: list[dict[str, str]] | None = None,
) -> None:
    _empty, front, body = source.read_text(encoding="utf-8").split("---\n", 2)
    data = yaml.safe_load(front)
    data["object_id"] = object_id
    name = object_id.replace("PAT_", "").replace("_", " ").title()
    data["name"] = name
    data["library_path"] = library_path
    data["foundation_object_id"] = "none"
    data["cross_links"] = cross_links or []
    data["references"] = references or []
    data["variants"] = []
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "---\n"
        + yaml.safe_dump(data, sort_keys=False)
        + "---\n"
        + re.sub(r"(?m)^# .+$", f"# {name}", body, count=1),
        encoding="utf-8",
    )


def write_authority_manifest(
    path: Path,
    skill_name: str,
    *,
    owned_domains: list[str] | None = None,
    object_ids: list[str] | None = None,
    fallback_digest: str | None = None,
) -> None:
    auxiliary_groups = []
    files_sha256 = {}
    if fallback_digest is not None:
        object_path = "library/writing/PAT_fixture_shared.md"
        auxiliary_groups.append(
            {
                "domain": "writing",
                "entry_object_ids": ["PAT_fixture_shared"],
                "object_ids": ["PAT_fixture_shared"],
                "owner_modules": ["writing/foundations"],
                "object_paths": {"PAT_fixture_shared": object_path},
                "files": [object_path],
            }
        )
        files_sha256[object_path] = fallback_digest
    path.write_text(
        json.dumps(
            {
                "schema_version": 2,
                "pass_version": "1.0.0-beta.5",
                "skill_name": skill_name,
                "owned_domains": owned_domains or [],
                "object_ids": object_ids or [],
                "auxiliary_groups": auxiliary_groups,
                "files_sha256": files_sha256,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


class SourceAndStateIndependenceTests(unittest.TestCase):
    """1-3, 12: the library is valid with no research state of any kind."""

    def test_library_validates_with_no_sources_ledger_or_workspace(self) -> None:
        with isolated_library() as tmp:
            root = Path(tmp)
            for name in RETIRED_STATE:
                self.assertFalse((root / name).exists(), f"{name} leaked into a clean checkout")
            result = subprocess.run(
                [sys.executable, str(root / "PASS/tools/validate.py"), "--library", str(root / "library")],
                text=True, capture_output=True, cwd=root,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("PASS:", result.stdout)

    def test_release_builds_with_no_sources_ledger_or_workspace(self) -> None:
        # The builder refuses to write inside its own checkout, so the release
        # lands in a separate directory outside the isolated tree.
        with isolated_library() as tmp, tempfile.TemporaryDirectory() as dest:
            root = Path(tmp)
            out = Path(dest) / "release"
            result = subprocess.run(
                [
                    sys.executable, str(root / "PASS/tools/build_release.py"), "build",
                    str(root / "recipes/SkillForge_Software_Engineering.yaml"), str(out),
                    "--library", str(root / "library"),
                ],
                text=True, capture_output=True, cwd=root,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            manifest = json.loads(
                (out / "RELEASE_MANIFEST.json").read_text(encoding="utf-8")
            )
            gates = manifest["quality_gates"]
            self.assertEqual(gates["schema_validation"], "passed")
            self.assertEqual(gates["visual_reference_verification"], "passed")
            self.assertEqual(
                manifest["pass_version"],
                (ROOT / "VERSION").read_text(encoding="utf-8").strip(),
            )

    def test_deleting_temporary_research_state_does_not_change_validity(self) -> None:
        before = validate("--library", str(LIBRARY))
        with isolated_library() as tmp:
            root = Path(tmp)
            after = subprocess.run(
                [sys.executable, str(root / "PASS/tools/validate.py"), "--library", str(root / "library")],
                text=True, capture_output=True, cwd=root,
            )
        self.assertEqual(before.returncode, 0, before.stdout)
        self.assertEqual(before.stdout.strip(), after.stdout.strip())


class DomainIndependenceTests(unittest.TestCase):
    """4-7, 10: each domain validates, builds, and links on its own."""

    def test_each_domain_validates_independently(self) -> None:
        for domain in DOMAINS:
            with self.subTest(domain=domain):
                result = validate("--library", str(LIBRARY), "--package", domain)
                self.assertEqual(result.returncode, 0, result.stdout)

    def test_no_card_depends_on_another_domain(self) -> None:
        owner = {}
        for card in cards(LIBRARY):
            data = frontmatter(card)
            if data.get("object_id"):
                owner[data["object_id"]] = card.relative_to(LIBRARY).parts[0]
        for card in cards(LIBRARY):
            data = frontmatter(card)
            if not data.get("object_id"):
                continue
            package = card.relative_to(LIBRARY).parts[0]
            targets = [link["target_object_id"] for link in data.get("cross_links") or []]
            foundation = data.get("foundation_object_id")
            if foundation and foundation != "none":
                targets.append(foundation)
            for target in targets:
                # `metaskills` is a shared foundation every release bundles, not a
                # peer domain. Any other cross-package edge couples two lanes.
                self.assertIn(
                    owner.get(target), {package, "metaskills"},
                    f"{data['object_id']} ({package}) depends on {target} ({owner.get(target)})",
                )

    def test_domain_release_excludes_unrelated_domains(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "release"
            self.assertEqual(run("build", SOFTWARE_ENGINEERING_RECIPE, out).returncode, 0)
            modules = json.loads((out / "RELEASE_MANIFEST.json").read_text(encoding="utf-8"))["modules"]
            self.assertIn("software-engineering/languages/cpp", modules)
            for foreign in ("art", "writing", "teaching"):
                self.assertFalse(
                    any(name == foreign or name.startswith(f"{foreign}/") for name in modules),
                    f"C++ release pulled in {foreign}",
                )

    def test_teaching_is_not_required_by_any_domain(self) -> None:
        self.assertFalse((LIBRARY / "teaching").exists(), "teaching is quarantined out of library/")
        for recipe in CANONICAL_RECIPES:
            modules = yaml.safe_load(recipe.read_text(encoding="utf-8"))["modules"]
            with self.subTest(recipe=recipe.name):
                self.assertFalse(any(str(name).startswith("teaching") for name in modules))
        for domain in DOMAINS:
            with self.subTest(domain=domain):
                self.assertEqual(validate("--library", str(LIBRARY), "--package", domain).returncode, 0)


class CardContractTests(unittest.TestCase):
    """8, 9: identity and variants hold without any source record."""

    def test_card_ids_are_globally_unique(self) -> None:
        seen: dict[str, Path] = {}
        for card in cards(LIBRARY):
            data = frontmatter(card)
            object_id = data.get("object_id")
            if not object_id:
                continue
            self.assertNotIn(object_id, seen, f"{object_id} duplicated in {card} and {seen.get(object_id)}")
            seen[object_id] = card
        self.assertGreater(len(seen), 0)

    def test_variants_resolve_to_their_owner_card(self) -> None:
        found = 0
        for card in cards(LIBRARY):
            data = frontmatter(card)
            notes = card.read_text(encoding="utf-8").split("## Notes", 1)[-1]
            for variant in data.get("variants") or []:
                found += 1
                # A variant is executable through the card it lives in: no source,
                # no locator, no owner in another domain.
                self.assertEqual(set(variant), {
                    "variant_id", "variant_name", "variant_basis",
                    "difference_from_foundation", "when_to_use", "when_not_to_use",
                    "absorbed_from_object_id",
                }, f"{card}: variant carries retired fields")
                self.assertIn(variant["variant_id"], notes)
        self.assertGreater(found, 0, "corpus has no variants to check")

    def test_no_card_carries_retired_source_provenance(self) -> None:
        retired = {"source_id", "locator", "page", "page_range", "source_hash", "evidence_type"}
        for card in cards(LIBRARY):
            data = frontmatter(card)
            with self.subTest(card=card.name):
                self.assertFalse(retired & set(data), f"{card}: retired root key")
                reference = data.get("reference")
                if reference is not None:
                    self.assertTrue(
                        set(reference) <= {"source_title", "author"},
                        f"{card}: reference carries retired provenance fields",
                    )


class ReleaseIntegrityTests(unittest.TestCase):
    """11: releases package knowledge; the remaining gates are real."""

    def test_named_skillforge_recipes_cover_every_domain_module(self) -> None:
        recipe_names = {
            "art": "SkillForge_Art.yaml",
            "game-design": "SkillForge_Game_Design.yaml",
            "software-engineering": "SkillForge_Software_Engineering.yaml",
            "writing": "SkillForge_Writing.yaml",
        }
        self.assertEqual(set(DOMAINS), set(recipe_names))
        for domain, filename in recipe_names.items():
            with self.subTest(domain=domain):
                recipe_path = RECIPES / filename
                self.assertTrue(recipe_path.is_file(), filename)
                recipe = yaml.safe_load(recipe_path.read_text(encoding="utf-8"))
                selected = set(recipe.get("modules") or [])
                available = {
                    path.parent.relative_to(LIBRARY).as_posix()
                    for path in (LIBRARY / domain).rglob("MODULE.yaml")
                }
                self.assertEqual(selected, available)
                self.assertEqual(recipe.get("name"), "SkillForge " + domain.replace("-", " ").title())
                self.assertTrue(str(recipe.get("skill_name", "")).startswith("skillforge-"))

    def test_every_recipe_builds_and_checks(self) -> None:
        for recipe in CANONICAL_RECIPES:
            with self.subTest(recipe=recipe.name), tempfile.TemporaryDirectory() as tmp:
                out = Path(tmp) / "release"
                result = run("build", recipe, out)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertTrue((out / "library/metaskills/MODULE.yaml").is_file())
                skill_path = out / "SKILL.md"
                skill_text = skill_path.read_text(encoding="utf-8")
                front = yaml.safe_load(skill_text.split("---\n", 2)[1])
                self.assertTrue(front.get("name") and front.get("description"))
                self.assertLessEqual(skill_path.stat().st_size, 8 * 1024)
                for notice in (
                    "CONTRIBUTING.md",
                    "LICENSE.md",
                    "NOTICE.md",
                    "TRADEMARKS.md",
                    "LICENSES/AGPL-3.0.txt",
                    "LICENSES/CC-BY-SA-4.0.txt",
                ):
                    self.assertTrue((out / notice).is_file(), notice)
                profile = yaml.safe_load(
                    (out / "runtime/profile.yaml").read_text(encoding="utf-8")
                )
                consumer_instructions = profile.get("consumer_instructions") or []
                if consumer_instructions:
                    barriers = out / "references/execution-barriers.md"
                    self.assertTrue(barriers.is_file())
                    barrier_text = barriers.read_text(encoding="utf-8")
                    self.assertIn("references/execution-barriers.md", skill_text)
                    for instruction in consumer_instructions:
                        self.assertIn(instruction.strip(), barrier_text)
                self.assertEqual(run("check", out).returncode, 0)

    def test_release_check_detects_a_missing_license_notice(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "release"
            self.assertEqual(run("build", SOFTWARE_ENGINEERING_RECIPE, out).returncode, 0)
            (out / "NOTICE.md").unlink()
            check = run("check", out)
            self.assertNotEqual(check.returncode, 0)
            self.assertIn("missing release licensing file: NOTICE.md", check.stderr)

    def test_release_check_detects_a_changed_card(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "release"
            self.assertEqual(run("build", SOFTWARE_ENGINEERING_RECIPE, out).returncode, 0)
            card = next((out / "library/software-engineering/languages/cpp").rglob("PAT_*.md"))
            card.write_text(card.read_text(encoding="utf-8") + "\nmutation\n", encoding="utf-8")
            check = run("check", out)
            self.assertNotEqual(check.returncode, 0)
            self.assertIn("changed release file", check.stderr)

    def test_release_check_detects_a_missing_declared_asset(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "release"
            self.assertEqual(run("build", ART_RECIPE, out).returncode, 0)
            next(out.rglob("broken_gate_stage1_canonical_scene_skeleton.png")).unlink()
            check = run("check", out)
            self.assertNotEqual(check.returncode, 0)
            self.assertIn("missing image_path", check.stderr)

    def test_release_check_detects_a_deleted_module(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "release"
            self.assertEqual(run("build", SOFTWARE_ENGINEERING_RECIPE, out).returncode, 0)
            shutil.rmtree(out / "library/software-engineering/languages/cpp")
            check = run("check", out)
            self.assertNotEqual(check.returncode, 0)
            self.assertIn("missing declared module", check.stderr)

    def test_missing_module_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            recipe = Path(tmp) / "bad.yaml"
            recipe.write_text("name: bad\nmodules: [does/not/exist]\n", encoding="utf-8")
            self.assertNotEqual(run("build", recipe, Path(tmp) / "out").returncode, 0)

    def test_output_refuses_the_repository(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            zip_out = ROOT / "library/do-not-overwrite.zip"
            result = run("build", SOFTWARE_ENGINEERING_RECIPE, Path(tmp) / "release", "--zip", zip_out)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("zip output path inside or above the repository", result.stderr)
            self.assertFalse(zip_out.exists())
            self.assertNotEqual(run("build", SOFTWARE_ENGINEERING_RECIPE, ROOT / "sub").returncode, 0)


class AuxiliaryReleaseTests(unittest.TestCase):
    """Cross-skill release composition stays bounded and fail-closed."""

    def test_auxiliary_release_materializes_exact_card_asset_and_relationship_closure(self) -> None:
        with isolated_library() as tmp, tempfile.TemporaryDirectory() as dest:
            root = Path(tmp)
            library = root / "library"
            primary = library / "fixture-primary"
            auxiliary = library / "fixture-aux/test"
            primary.mkdir()
            auxiliary.mkdir(parents=True)
            (primary / "MODULE.yaml").write_text(
                "name: fixture-primary\nrequires: []\n", encoding="utf-8"
            )
            (auxiliary / "MODULE.yaml").write_text(
                "name: fixture-aux/test\nrequires: []\n", encoding="utf-8"
            )

            source_card = (
                library
                / "art/foundations/form-construction/PAT_build_gesture_into_clear_masses.md"
            )
            source_data = frontmatter(source_card)
            source_reference = dict(source_data["references"][0])
            source_asset = root / source_reference["image_path"]
            fixture_asset = auxiliary / "assets/fixture.png"
            fixture_asset.parent.mkdir(parents=True)
            shutil.copy2(source_asset, fixture_asset)
            shutil.copy2(
                Path(str(source_asset) + ".meta.json"),
                Path(str(fixture_asset) + ".meta.json"),
            )
            source_reference["image_path"] = "library/fixture-aux/test/assets/fixture.png"

            entry = auxiliary / "PAT_fixture_aux_entry.md"
            prerequisite = auxiliary / "PAT_fixture_aux_prerequisite.md"
            write_fixture_pattern(
                source_card,
                entry,
                "PAT_fixture_aux_entry",
                ["fixture-aux", "test"],
                references=[source_reference],
            )
            write_fixture_pattern(
                source_card,
                prerequisite,
                "PAT_fixture_aux_prerequisite",
                ["fixture-aux", "test"],
                cross_links=[
                    {"rel": "prerequisite_for", "target_object_id": "PAT_fixture_aux_entry"}
                ],
            )
            (root / "memory/fixture-aux").mkdir(parents=True)
            (root / "memory/fixture-aux/skill_memory.yaml").write_text(
                "this would be invalid if packaged: true\n", encoding="utf-8"
            )
            recipe = root / "recipes/Auxiliary_Fixture.yaml"
            recipe.write_text(
                yaml.safe_dump(
                    {
                        "name": "Auxiliary Fixture",
                        "skill_name": "auxiliary-fixture",
                        "modules": ["fixture-primary"],
                        "runtime_profile": "generic",
                        "auxiliary": [
                            {"domain": "fixture-aux", "objects": ["PAT_fixture_aux_entry"]}
                        ],
                    },
                    sort_keys=False,
                ),
                encoding="utf-8",
            )

            out = Path(dest) / "release"
            build = subprocess.run(
                [
                    sys.executable,
                    str(root / "PASS/tools/build_release.py"),
                    "build",
                    str(recipe),
                    str(out),
                    "--library",
                    str(library),
                    "--memory",
                    str(root / "memory"),
                ],
                text=True,
                capture_output=True,
                cwd=root,
            )
            self.assertEqual(build.returncode, 0, build.stdout + build.stderr)
            manifest = json.loads((out / "RELEASE_MANIFEST.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["schema_version"], 2)
            self.assertEqual(manifest["owned_domains"], ["fixture-primary"])
            self.assertEqual(len(manifest["auxiliary_groups"]), 1)
            group = manifest["auxiliary_groups"][0]
            self.assertEqual(group["domain"], "fixture-aux")
            self.assertEqual(group["entry_object_ids"], ["PAT_fixture_aux_entry"])
            self.assertEqual(
                group["object_ids"],
                ["PAT_fixture_aux_entry", "PAT_fixture_aux_prerequisite"],
            )
            self.assertEqual((out / group["object_paths"]["PAT_fixture_aux_entry"]).read_bytes(), entry.read_bytes())
            self.assertEqual(
                (out / "library/fixture-aux/test/assets/fixture.png").read_bytes(),
                fixture_asset.read_bytes(),
            )
            self.assertTrue((out / "library/fixture-aux/test/assets/fixture.png.meta.json").is_file())
            self.assertFalse((out / "library/fixture-aux/test/MODULE.yaml").exists())
            self.assertFalse((out / "memory/fixture-aux").exists())
            index = (out / "library/fixture-aux/test/INDEX.md").read_text(encoding="utf-8")
            self.assertIn("PAT_fixture_aux_entry.md", index)
            self.assertIn("PAT_fixture_aux_prerequisite.md", index)
            skill = out / "SKILL.md"
            self.assertIn("## Auxiliary fallbacks", skill.read_text(encoding="utf-8"))
            self.assertLessEqual(skill.stat().st_size, 8 * 1024)
            self.assertEqual(
                subprocess.run(
                    [sys.executable, str(root / "PASS/tools/build_release.py"), "check", str(out)],
                    text=True,
                    capture_output=True,
                    cwd=root,
                ).returncode,
                0,
            )
            authority = subprocess.run(
                [sys.executable, str(out / "scripts/skillforge_runtime.py"), "authority"],
                text=True,
                capture_output=True,
                cwd=out,
            )
            self.assertEqual(authority.returncode, 0, authority.stderr)
            self.assertEqual(json.loads(authority.stdout)["decisions"][0]["authority"], "auxiliary")

            manifest["auxiliary_groups"][0]["object_ids"].pop()
            (out / "RELEASE_MANIFEST.json").write_text(
                json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
            )
            broken = subprocess.run(
                [sys.executable, str(root / "PASS/tools/build_release.py"), "check", str(out)],
                text=True,
                capture_output=True,
                cwd=root,
            )
            self.assertNotEqual(broken.returncode, 0)
            self.assertIn("object_paths does not match object_ids", broken.stderr)

    def test_auxiliary_recipe_rejects_an_object_from_the_wrong_domain(self) -> None:
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as dest:
            recipe = Path(tmp) / "bad.yaml"
            recipe.write_text(
                "name: bad\nmodules: [game-design/adventures]\n"
                "auxiliary:\n  - domain: art\n"
                "    objects: [writing_choose_diction_to_serve_purpose_and_tone]\n",
                encoding="utf-8",
            )
            result = run("build", recipe, Path(dest) / "out")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("belongs to writing, not art", result.stderr)

            recipe.write_text(
                "name: bad\nmodules: [game-design/adventures]\nauxiliary: {}\n",
                encoding="utf-8",
            )
            malformed = run("build", recipe, Path(dest) / "out-two")
            self.assertNotEqual(malformed.returncode, 0)
            self.assertIn("release recipe auxiliary must be a list", malformed.stderr)

    def test_authority_prefers_one_complete_owner_and_falls_back_from_an_incomplete_one(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fallback = root / "fallback.json"
            owner = root / "owner.json"
            write_authority_manifest(fallback, "game-design", fallback_digest="a" * 64)
            write_authority_manifest(
                owner,
                "writing",
                owned_domains=["writing"],
                object_ids=["PAT_fixture_shared"],
            )
            result = subprocess.run(
                [sys.executable, str(RUNTIME), "authority", "--manifest", str(fallback), "--manifest", str(owner)],
                text=True,
                capture_output=True,
                cwd=ROOT,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            decision = json.loads(result.stdout)["decisions"][0]
            self.assertEqual((decision["authority"], decision["provider_skill"]), ("owner", "writing"))

            write_authority_manifest(owner, "writing", owned_domains=["writing"])
            result = subprocess.run(
                [sys.executable, str(RUNTIME), "authority", "--manifest", str(fallback), "--manifest", str(owner)],
                text=True,
                capture_output=True,
                cwd=ROOT,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["decisions"][0]["authority"], "auxiliary")

    def test_authority_coalesces_identical_fallbacks_and_rejects_different_revisions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = root / "first.json"
            second = root / "second.json"
            write_authority_manifest(first, "game-design", fallback_digest="a" * 64)
            write_authority_manifest(second, "worldbuilding", fallback_digest="a" * 64)
            command = [
                sys.executable,
                str(RUNTIME),
                "authority",
                "--manifest",
                str(first),
                "--manifest",
                str(second),
            ]
            same = subprocess.run(command, text=True, capture_output=True, cwd=ROOT)
            self.assertEqual(same.returncode, 0, same.stderr)
            self.assertEqual(len(json.loads(same.stdout)["decisions"]), 2)

            write_authority_manifest(second, "worldbuilding", fallback_digest="b" * 64)
            different = subprocess.run(command, text=True, capture_output=True, cwd=ROOT)
            self.assertNotEqual(different.returncode, 0)
            self.assertIn("conflicting auxiliary fallback", different.stderr)

    def test_authority_rejects_multiple_active_owners(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = root / "first.json"
            second = root / "second.json"
            write_authority_manifest(first, "writing-one", owned_domains=["writing"])
            write_authority_manifest(second, "writing-two", owned_domains=["writing"])
            result = subprocess.run(
                [sys.executable, str(RUNTIME), "authority", "--manifest", str(first), "--manifest", str(second)],
                text=True,
                capture_output=True,
                cwd=ROOT,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("multiple active owner providers", result.stderr)


class ValidatorScopeTests(unittest.TestCase):
    """The validator checks cards, and refuses to grow research-history checks."""

    def test_validator_rejects_a_cross_domain_dependency(self) -> None:
        with isolated_library() as tmp:
            root = Path(tmp)
            # Point a card from another lane at a C++ card: a coupling the
            # validator must catch. Any non-SE lane will do.
            card = next(
                path
                for path in (root / "library").rglob("PAT_*.md")
                if path.relative_to(root / "library").parts[0]
                not in ("software-engineering", SHARED_PACKAGE)
            )
            _, front, body = card.read_text(encoding="utf-8").split("---\n", 2)
            data = yaml.safe_load(front)
            data["cross_links"] = [
                {"rel": "related_to", "target_object_id": "PAT_wrap_virtuals_with_nvi_idiom"}
            ]
            card.write_text(
                "---\n" + yaml.safe_dump(data, sort_keys=False) + "---\n" + body,
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(root / "PASS/tools/validate.py"), "--library", str(root / "library")],
                text=True, capture_output=True, cwd=root,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("rule 26", result.stdout)

    def test_validator_rejects_a_cross_domain_reference_in_prose(self) -> None:
        with isolated_library() as tmp:
            root = Path(tmp)
            # A body that names another package's card is the same coupling as a
            # cross_link, and ships as an unresolvable identifier in any release
            # that carries one package without the other.
            card = next(
                path
                for path in (root / "library").rglob("PAT_*.md")
                if path.relative_to(root / "library").parts[0]
                not in ("software-engineering", SHARED_PACKAGE)
            )
            card.write_text(
                card.read_text(encoding="utf-8")
                + "\nSee `PAT_wrap_virtuals_with_nvi_idiom` for the other case.\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(root / "PASS/tools/validate.py"), "--library", str(root / "library")],
                text=True, capture_output=True, cwd=root,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("rule 26", result.stdout)
            self.assertIn("PAT_wrap_virtuals_with_nvi_idiom", result.stdout)

    def test_validator_rejects_a_language_module_that_drops_core(self) -> None:
        # A language package is a layer on its domain's agnostic foundation, and
        # the requirement is one hand-written line per module. Dropped, the build
        # still succeeds and ships a release whose cards assume a foundation that
        # is not in the package.
        with isolated_library() as tmp:
            root = Path(tmp)
            manifest = next(
                path
                for path in (root / "library").rglob("MODULE.yaml")
                if "languages" in path.parent.relative_to(root / "library").parts[1:]
            )
            module = manifest.parent.relative_to(root / "library").as_posix()
            core = f"{module.split('/')[0]}/core"
            data = yaml.safe_load(manifest.read_text(encoding="utf-8"))
            data["requires"] = [name for name in data.get("requires") or [] if name != core]
            manifest.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(root / "PASS/tools/validate.py"), "--library", str(root / "library")],
                text=True, capture_output=True, cwd=root,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(f"module {module}: a language module must require {core}", result.stdout)

    def test_validator_rejects_a_requirement_that_names_no_module(self) -> None:
        # A mistyped requirement resolves to nothing. Caught here it is a typo;
        # caught at build time it is a ValueError out of the resolver.
        with isolated_library() as tmp:
            root = Path(tmp)
            manifest = next((root / "library").rglob("MODULE.yaml"))
            module = manifest.parent.relative_to(root / "library").as_posix()
            data = yaml.safe_load(manifest.read_text(encoding="utf-8"))
            data["requires"] = [*(data.get("requires") or []), "software-engineering/coer"]
            manifest.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(root / "PASS/tools/validate.py"), "--library", str(root / "library")],
                text=True, capture_output=True, cwd=root,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                f"module {module}: requires a module that does not exist: software-engineering/coer",
                result.stdout,
            )

    def test_relation_contract_rejects_an_illegal_pairing(self) -> None:
        # PASS_SCHEMA.md 1a types every relation. Before it existed, `supports`
        # ran in every direction between every pair of object types, which left
        # an authority edge indistinguishable from an adjacency one.
        with isolated_library() as tmp:
            root = Path(tmp)
            card = next((root / "library").rglob("PAT_*.md"))
            _, front, rest = card.read_text(encoding="utf-8").split("---\n", 2)
            data = yaml.safe_load(front)
            drill = frontmatter(next((root / "library").rglob("DRILL_*.md")))["object_id"]
            data["cross_links"] = [{"rel": "supports", "target_object_id": drill}]
            card.write_text(
                "---\n" + yaml.safe_dump(data, sort_keys=False) + "---\n" + rest,
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(root / "PASS/tools/validate.py"),
                 "--relations", "--library", str(root / "library")],
                text=True, capture_output=True, cwd=root,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(f"pattern --supports--> drill {drill} is not a legal pairing", result.stdout)

    def test_relation_contract_is_reported_separately_from_card_validation(self) -> None:
        # The library predates the contract, so the check cannot gate the default
        # run until every package has reconciled. Card validation must not see it.
        result = validate()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertNotIn("relation contract", result.stdout)

    def test_validator_takes_no_ledger_or_provenance_arguments(self) -> None:
        result = validate("--help")
        self.assertEqual(result.returncode, 0)
        for retired in ("--ledger", "--provenance", "--scope-ledger-to-library"):
            self.assertNotIn(retired, result.stdout)

    def test_indexes_are_generated_and_current(self) -> None:
        # Indexes are derived navigation. A stale one silently hides cards from
        # any agent that follows a skill's documented load order.
        result = subprocess.run(
            [sys.executable, str(ROOT / "PASS/tools/build_index.py"), "--check"],
            text=True, capture_output=True, cwd=ROOT,
        )
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_every_index_lists_the_cards_beside_it(self) -> None:
        for index in sorted(LIBRARY.rglob("INDEX.md")):
            listed = set(re.findall(r"\(((?:PAT|DRILL|AP)_[a-z0-9_]+\.md)\)", index.read_text(encoding="utf-8")))
            beside = {p.name for p in index.parent.glob("*.md") if p.name not in {"INDEX.md", "README.md"}}
            with self.subTest(index=index.relative_to(LIBRARY).as_posix()):
                self.assertEqual(beside - listed, set(), "cards missing from their own index")

    def test_no_tool_imports_retired_provenance_modules(self) -> None:
        retired = ("provenance", "quality_attestation", "source_provenance", "stage_source", "verify_grounding")
        for tool in sorted((ROOT / "PASS/tools").glob("*.py")):
            text = tool.read_text(encoding="utf-8")
            for name in retired:
                with self.subTest(tool=tool.name, module=name):
                    self.assertNotIn(f"import {name}", text)
                    self.assertNotIn(f"from {name}", text)


class RepositoryShapeTests(unittest.TestCase):
    def test_repo_agent_skill_discovery_folders_are_present(self) -> None:
        for folder in (".claude/skills", ".agents/skills"):
            self.assertTrue((ROOT / folder).is_dir(), folder)

    def test_cold_start_instructions_are_bounded_and_route_before_loading(self) -> None:
        budget = 8 * 1024
        for filename in ("AGENTS.md", "CLAUDE.md"):
            path = ROOT / filename
            content = path.read_bytes()
            text = content.decode("utf-8")
            with self.subTest(file=filename):
                self.assertLessEqual(
                    len(content), budget,
                    f"{filename} exceeds the {budget}-byte cold-start budget",
                )
                self.assertIn("## Route before reading", text)
                self.assertIn("Do not preload", text)

    def test_repo_skill_entrypoints_fit_the_context_budget(self) -> None:
        budget = 8 * 1024
        for path in sorted((ROOT / ".claude/skills").glob("*/SKILL.md")):
            with self.subTest(skill=path.parent.name):
                self.assertLessEqual(
                    path.stat().st_size, budget,
                    f"{path.relative_to(ROOT)} exceeds the {budget}-byte entrypoint budget; "
                    "move conditional detail into a routed reference",
                )

    def test_repo_agent_skill_markdown_is_mirrored(self) -> None:
        claude_root = ROOT / ".claude/skills"
        agents_root = ROOT / ".agents/skills"
        claude = {
            path.relative_to(claude_root).as_posix(): path
            for path in claude_root.rglob("*.md")
        }
        agents = {
            path.relative_to(agents_root).as_posix(): path
            for path in agents_root.rglob("*.md")
        }

        self.assertEqual(claude.keys(), agents.keys())
        for relative_path in sorted(claude):
            with self.subTest(skill_file=relative_path):
                self.assertEqual(
                    claude[relative_path].read_text(encoding="utf-8"),
                    agents[relative_path].read_text(encoding="utf-8"),
                )

    def test_pass_dependency_manifest_exists(self) -> None:
        self.assertTrue((ROOT / "PASS/requirements.txt").is_file())

    def test_agent_instruction_files_state_the_same_hard_rules(self) -> None:
        # CLAUDE.md and AGENTS.md are the same contract written for different
        # agents. Checking that keywords merely appear in both is too weak: one
        # file could contradict the other and still pass, because the word it
        # contradicts is present either way. Instead each rule leads with a bold
        # sentence that is shared verbatim, and the two sets must match exactly.
        # A rule added, dropped, or reworded on one side alone fails here.
        claude = agent_rule_leads("CLAUDE.md", "## Hard rules")
        agents = agent_rule_leads("AGENTS.md", "## Non-negotiable boundaries")

        self.assertTrue(claude, "no bold rule leads found in CLAUDE.md")
        self.assertGreaterEqual(len(claude), 10, "hard-rule list looks truncated")

        only_claude = sorted(claude - agents)
        only_agents = sorted(agents - claude)
        self.assertEqual(
            (only_claude, only_agents),
            ([], []),
            "CLAUDE.md and AGENTS.md state different rules.\n"
            f"  only in CLAUDE.md: {only_claude}\n"
            f"  only in AGENTS.md: {only_agents}",
        )

    def test_retired_authoring_infrastructure_is_gone(self) -> None:
        for path in (
            "PASS/tools/provenance.py",
            "PASS/tools/source_provenance.py",
            "PASS/tools/quality_attestation.py",
            "PASS/tools/publish_provenance.py",
            "PASS/tools/stage_source.py",
            "PASS/tools/verify_grounding.py",
            "PASS/tools/preflight_pdf.py",
            "PASS/tools/render_pdf.py",
            "PASS/tools/cleanup_authoring_cache.py",
            "PASS/docs/PASS_LEDGER.md",
            "PASS/docs/PASS_GROUNDING.md",
            "PASS/templates/SOURCE_TEMPLATE.md",
            "PASS/templates/UNITS_TEMPLATE.md",
            "PASS/templates/UNIT_LEDGER_TEMPLATE.md",
            "workspace/provenance",
        ):
            with self.subTest(path=path):
                self.assertFalse((ROOT / path).exists(), f"{path} survived the cleanup")


class ReleaseMemoryTests(unittest.TestCase):
    """20: a release carries its own domains' empirical record, frozen.

    Memory ships beside the canon rather than inside it, so packaging it cannot
    turn an observation into a card. It ships read-only because the package is
    not the store's persistence target: new events belong to the library that
    owns it.
    """

    ART_STORE = MEMORY / "art" / "skill_memory.yaml"

    @unittest.skipUnless(ART_STORE.is_file(), "no Art memory store in this checkout")
    def test_release_ships_the_memory_of_the_domains_it_bundles(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "release"
            self.assertEqual(run("build", ART_RECIPE, out).returncode, 0)
            manifest = json.loads((out / "RELEASE_MANIFEST.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["memory_domains"], ["art"])
            self.assertTrue((out / "memory/art/skill_memory.yaml").is_file())
            self.assertTrue((out / "memory/art/training_history.jsonl").is_file())
            self.assertEqual(manifest["quality_gates"]["memory_validation"], "passed")
            self.assertIn("## Skillset Memory", (out / "SKILL.md").read_text(encoding="utf-8"))
            self.assertEqual(run("check", out).returncode, 0)

    @unittest.skipUnless(ART_STORE.is_file(), "no Art memory store in this checkout")
    def test_shipped_memory_is_read_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "release"
            self.assertEqual(run("build", ART_RECIPE, out).returncode, 0)
            for shipped in (out / "memory").rglob("*"):
                if shipped.is_file():
                    with self.subTest(file=shipped.name):
                        self.assertFalse(
                            os.access(shipped, os.W_OK),
                            f"{shipped.name} shipped writable",
                        )

    def test_release_ships_no_other_domain_memory(self) -> None:
        """Memory is domain-scoped exactly as the library is."""
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "release"
            self.assertEqual(run("build", SOFTWARE_ENGINEERING_RECIPE, out).returncode, 0)
            manifest = json.loads((out / "RELEASE_MANIFEST.json").read_text(encoding="utf-8"))
            self.assertNotIn("art", manifest["memory_domains"])
            self.assertFalse((out / "memory/art").exists())

    def test_release_builds_with_the_memory_tree_absent(self) -> None:
        """Deleting the store never breaks a build; memory is not a dependency."""
        with isolated_library() as tmp, tempfile.TemporaryDirectory() as dest:
            root = Path(tmp)
            self.assertFalse((root / "memory").exists())
            out = Path(dest) / "release"
            result = subprocess.run(
                [
                    sys.executable, str(root / "PASS/tools/build_release.py"), "build",
                    str(root / "recipes/SkillForge_Art.yaml"), str(out),
                    "--library", str(root / "library"),
                ],
                text=True, capture_output=True, cwd=root,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            manifest = json.loads((out / "RELEASE_MANIFEST.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["memory_domains"], [])
            self.assertNotIn("## Skillset Memory", (out / "SKILL.md").read_text(encoding="utf-8"))

    @unittest.skipUnless(ART_STORE.is_file(), "no Art memory store in this checkout")
    def test_release_check_detects_a_deleted_memory_store(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "release"
            self.assertEqual(run("build", ART_RECIPE, out).returncode, 0)
            store = out / "memory/art/skill_memory.yaml"
            store.chmod(0o600)
            store.unlink()
            check = run("check", out)
            self.assertNotEqual(check.returncode, 0)
            self.assertIn("missing declared memory domain: art", check.stderr)

    @unittest.skipUnless(ART_STORE.is_file(), "no Art memory store in this checkout")
    def test_shipped_memory_validates_on_its_own(self) -> None:
        """The packaged store is portable: the memory tool reads it and nothing else."""
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "release"
            self.assertEqual(run("build", ART_RECIPE, out).returncode, 0)
            result = subprocess.run(
                [
                    sys.executable, str(ROOT / "PASS/tools/memory.py"), "validate",
                    "--memory", str(out / "memory"),
                ],
                text=True, capture_output=True, cwd=ROOT,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
