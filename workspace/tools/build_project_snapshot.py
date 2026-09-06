#!/usr/bin/env python3
"""Build a pruned, domain-scoped PASS folder or archive for a Project chat."""

from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path


ROOT_FILES = (
    "AGENTS.md",
    "CHANGELOG.md",
    "CLAUDE.md",
    "ARCHITECTURE.md",
    "CONTRIBUTING.md",
    "README.md",
    "LICENSE",
    "LICENSE.md",
    "NOTICE.md",
    "TRADEMARKS.md",
    "VERSION",
)
SKIP_DIRECTORY_NAMES = {
    ".git",
    ".pytest_cache",
    "__pycache__",
    "archive",
    "releases",
    "sources",
    "tmp",
}
SKIP_SUFFIXES = {".pdf", ".zip", ".pyc"}


def available_domains(repo: Path) -> list[str]:
    library = repo / "library"
    return sorted(
        path.name
        for path in library.iterdir()
        if path.is_dir() and path.name != "metaskills"
    )


def iter_files(root: Path) -> list[Path]:
    if root.is_file():
        return [root]
    if not root.is_dir():
        return []

    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file() or path.is_symlink():
            continue
        relative_parts = path.relative_to(root).parts
        if any(part in SKIP_DIRECTORY_NAMES for part in relative_parts[:-1]):
            continue
        if path.suffix.casefold() in SKIP_SUFFIXES:
            continue
        files.append(path)
    return files


def skill_targets_domain(skill_root: Path, domain: str) -> bool:
    if skill_root.name == domain:
        return True

    skill_file = skill_root / "SKILL.md"
    if not skill_file.is_file():
        return False
    content = skill_file.read_text(encoding="utf-8")
    markers = (
        f"--package {domain}",
        f"library/{domain}/",
        f"memory/{domain}/",
    )
    return any(marker in content for marker in markers)


def matching_skill_roots(repo: Path, host: str, domain: str) -> list[Path]:
    skills = repo / host / "skills"
    if not skills.is_dir():
        return []
    return [
        path
        for path in sorted(skills.iterdir())
        if path.is_dir()
        and path.name != "pass-authoring"
        and skill_targets_domain(path, domain)
    ]


def canonical_recipe_files(repo: Path) -> list[Path]:
    recipes = repo / "workspace/release-recipes"
    if not recipes.is_dir():
        return []
    return [
        path
        for path in sorted(recipes.iterdir())
        if path.is_file()
        and not path.is_symlink()
        and path.name.startswith("SkillForge_")
        and path.suffix == ".yaml"
    ]


def snapshot_roots(
    repo: Path,
    domains: list[str],
    include_tests: bool = False,
    include_recipes: bool = False,
) -> list[Path]:
    roots = [repo / name for name in ROOT_FILES if (repo / name).is_file()]
    roots.extend(
        (
            repo / "PASS",
            repo / "LICENSES",
            repo / "docs",
            repo / "library/metaskills",
            repo / "workspace/tools",
        )
    )

    for domain in domains:
        roots.extend((repo / "library" / domain, repo / "memory" / domain))
        for host in (".claude", ".agents"):
            roots.extend(matching_skill_roots(repo, host, domain))

    for host in (".claude", ".agents"):
        roots.append(repo / host / "skills/pass-authoring")
    if include_tests:
        roots.append(repo / "tests")
    if include_recipes:
        roots.extend(canonical_recipe_files(repo))
    return roots


def collect_snapshot_files(
    repo: Path,
    domains: list[str],
    include_tests: bool = False,
    include_recipes: bool = False,
) -> list[Path]:
    selected: dict[str, Path] = {}
    for root in snapshot_roots(repo, domains, include_tests, include_recipes):
        for path in iter_files(root):
            relative = path.relative_to(repo).as_posix()
            selected[relative] = path
    return [selected[name] for name in sorted(selected)]


def source_input_name(root_name: str, path: Path) -> str:
    return (Path(root_name) / "SOURCE_INPUT" / path.name).as_posix()


def write_snapshot_archive(
    output: Path,
    repo: Path,
    root_name: str,
    files: list[Path],
    source_inputs: list[Path],
) -> int:
    total_bytes = 0
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            relative = path.relative_to(repo)
            archive.write(path, (Path(root_name) / relative).as_posix())
            total_bytes += path.stat().st_size
        for path in source_inputs:
            archive.write(path, source_input_name(root_name, path))
            total_bytes += path.stat().st_size
    return total_bytes


def write_snapshot_directory(
    output: Path,
    repo: Path,
    files: list[Path],
    source_inputs: list[Path],
) -> int:
    """Create a new project directory without exposing a partially copied tree."""
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(
        tempfile.mkdtemp(prefix=f".{output.name}.tmp-", dir=output.parent)
    )
    total_bytes = 0
    try:
        for path in files:
            target = temporary / path.relative_to(repo)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
            total_bytes += path.stat().st_size
        for path in source_inputs:
            target = temporary / "SOURCE_INPUT" / path.name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
            total_bytes += path.stat().st_size
        temporary.replace(output)
    except BaseException:
        shutil.rmtree(temporary, ignore_errors=True)
        raise
    return total_bytes


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Build a pruned PASS folder or ZIP archive for one or more "
            "Project-chat domains."
        ),
        epilog=(
            "PASS, metaskills, selected domain cards, domain memory, and matching "
            "host skills and reusable workspace tools are included. Source PDFs, "
            "nested ZIPs, .git, archive, and workspace scratch are excluded. "
            "Explicit text inputs are transient."
        ),
    )
    parser.add_argument(
        "output",
        type=Path,
        help="Destination .zip path or new project-directory path.",
    )
    parser.add_argument(
        "--domain", action="append", required=True,
        help="Domain package to include. Repeat to include more than one.",
    )
    parser.add_argument(
        "--include-tests", action="store_true",
        help="Include repository tests for engineering-oriented Project chats.",
    )
    parser.add_argument(
        "--include-recipes", action="store_true",
        help="Include canonical SkillForge_*.yaml workspace release recipes.",
    )
    parser.add_argument(
        "--source-text", action="append", type=Path, default=[],
        help=(
            "Put an extracted .txt or .md source at top-level SOURCE_INPUT/. "
            "Repeat for multiple inputs; the files are not copied into the repo."
        ),
    )
    parser.add_argument(
        "--max-file-mb", type=float, default=25.0,
        help="Skip individual files larger than this many MiB (default: 25).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing ZIP file. Existing directories are never replaced.",
    )
    args = parser.parse_args()

    repo = Path(__file__).resolve().parents[2]
    known = available_domains(repo)
    domains = sorted(set(args.domain))
    unknown = sorted(set(domains) - set(known))
    if unknown:
        parser.error(
            f"unknown domain(s): {', '.join(unknown)}; available: {', '.join(known)}"
        )
    archive_output = args.output.suffix.casefold() == ".zip"
    if args.output.exists():
        if args.output.is_dir():
            parser.error(
                f"project directory already exists: {args.output}; "
                "choose a new destination"
            )
        if not archive_output:
            parser.error(f"directory output path is an existing file: {args.output}")
        if not args.force:
            parser.error(
                f"output already exists: {args.output} (use --force to replace it)"
            )
    if args.max_file_mb <= 0:
        parser.error("--max-file-mb must be greater than zero")
    source_inputs: list[Path] = []
    source_names: set[str] = set()
    for path in args.source_text:
        if not path.is_file():
            parser.error(f"source text does not exist: {path}")
        if path.suffix.casefold() not in {".txt", ".md"}:
            parser.error(f"source text must be .txt or .md, not: {path}")
        if path.name.casefold() in source_names:
            parser.error(f"source text filenames must be unique: {path.name}")
        source_names.add(path.name.casefold())
        source_inputs.append(path)

    files = collect_snapshot_files(
        repo,
        domains,
        include_tests=args.include_tests,
        include_recipes=args.include_recipes,
    )
    output = args.output.resolve()
    files = [path for path in files if path.resolve() != output]
    maximum_bytes = int(args.max_file_mb * 1024 * 1024)
    oversized = [path for path in files if path.stat().st_size > maximum_bytes]
    files = [path for path in files if path.stat().st_size <= maximum_bytes]
    oversized_sources = [
        path for path in source_inputs if path.stat().st_size > maximum_bytes
    ]
    if oversized_sources:
        parser.error(
            "source text exceeds --max-file-mb: "
            + ", ".join(str(path) for path in oversized_sources)
        )
    if not files:
        parser.error("the snapshot selection is empty")

    root_name = "PASS-project-" + "-".join(domains)
    if archive_output:
        output.parent.mkdir(parents=True, exist_ok=True)
        total_bytes = write_snapshot_archive(
            output, repo, root_name, files, source_inputs
        )
        destination_size = output.stat().st_size
        destination_kind = "ZIP archive"
    else:
        total_bytes = write_snapshot_directory(
            output, repo, files, source_inputs
        )
        destination_size = total_bytes
        destination_kind = "project directory"

    print(
        f"wrote {len(files)} repo file(s) and {len(source_inputs)} source input(s), "
        f"{total_bytes} source bytes, to {destination_kind} {output} "
        f"({destination_size} bytes)"
    )
    if oversized:
        print(f"skipped {len(oversized)} file(s) above {args.max_file_mb:g} MiB:")
        for path in oversized:
            print(f"  {path.relative_to(repo).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
