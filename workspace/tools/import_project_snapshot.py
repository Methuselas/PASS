#!/usr/bin/env python3
"""Safely preview or import an updated PASS project snapshot ZIP."""

from __future__ import annotations

import argparse
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath


ROOT_FILES = {
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
}
HOST_SKILL_ROOTS = (".agents", ".claude")


class SnapshotImportError(RuntimeError):
    """Raised when an archive cannot be trusted or imported safely."""


@dataclass(frozen=True)
class ArchiveEntry:
    relative: PurePosixPath
    info: zipfile.ZipInfo


@dataclass(frozen=True)
class SnapshotArchive:
    root_name: str
    entries: tuple[ArchiveEntry, ...]


@dataclass(frozen=True)
class Change:
    kind: str
    relative: PurePosixPath
    source: Path
    target: Path


@dataclass(frozen=True)
class ImportPlan:
    changes: tuple[Change, ...]
    unchanged: int


def available_domains(repo: Path) -> list[str]:
    library = repo / "library"
    if not library.is_dir():
        return []
    return sorted(
        path.name
        for path in library.iterdir()
        if path.is_dir() and path.name != "metaskills"
    )


def _member_parts(info: zipfile.ZipInfo) -> tuple[str, ...]:
    name = info.filename
    if not name or "\\" in name or "\0" in name or name.startswith("/"):
        raise SnapshotImportError(f"unsafe ZIP member name: {name!r}")
    parts = name.split("/")
    if info.is_dir() and parts[-1] == "":
        parts.pop()
    if not parts or any(part in {"", ".", ".."} for part in parts):
        raise SnapshotImportError(f"unsafe ZIP member path: {name!r}")
    if ":" in parts[0]:
        raise SnapshotImportError(f"absolute ZIP member path is not allowed: {name!r}")
    return tuple(parts)


def inspect_archive(
    archive_path: Path,
    *,
    max_file_bytes: int,
    max_total_bytes: int,
) -> SnapshotArchive:
    if not archive_path.is_file():
        raise SnapshotImportError(f"archive does not exist: {archive_path}")

    roots: dict[str, str] = {}
    names: dict[str, str] = {}
    entries: list[ArchiveEntry] = []
    total_bytes = 0
    with zipfile.ZipFile(archive_path) as archive:
        for info in archive.infolist():
            parts = _member_parts(info)
            root_key = parts[0].casefold()
            if root_key in roots and roots[root_key] != parts[0]:
                raise SnapshotImportError(
                    "case-colliding project roots are not allowed: "
                    f"{roots[root_key]!r} and {parts[0]!r}"
                )
            roots[root_key] = parts[0]
            if info.is_dir():
                continue
            if len(parts) < 2:
                raise SnapshotImportError(
                    f"file is outside the project root: {info.filename!r}"
                )
            mode = (info.external_attr >> 16) & 0xFFFF
            if stat.S_ISLNK(mode):
                raise SnapshotImportError(
                    f"symbolic links are not allowed: {info.filename!r}"
                )
            if info.flag_bits & 0x1:
                raise SnapshotImportError(
                    f"encrypted ZIP members are not supported: {info.filename!r}"
                )
            if info.file_size > max_file_bytes:
                raise SnapshotImportError(
                    f"ZIP member exceeds the per-file limit: {info.filename!r}"
                )
            total_bytes += info.file_size
            if total_bytes > max_total_bytes:
                raise SnapshotImportError("ZIP contents exceed the total size limit")

            relative = PurePosixPath(*parts[1:])
            key = relative.as_posix().casefold()
            if key in names:
                raise SnapshotImportError(
                    "duplicate or case-colliding ZIP members: "
                    f"{names[key]!r} and {relative.as_posix()!r}"
                )
            names[key] = relative.as_posix()
            entries.append(ArchiveEntry(relative, info))

    if len(roots) != 1:
        found = ", ".join(sorted(roots.values())) or "none"
        raise SnapshotImportError(
            f"archive must contain exactly one project root; found: {found}"
        )
    root_name = next(iter(roots.values()))
    if not root_name.startswith("PASS-project-"):
        raise SnapshotImportError(
            f"project root must start with 'PASS-project-': {root_name}"
        )
    if not entries:
        raise SnapshotImportError("archive contains no files")
    return SnapshotArchive(root_name, tuple(sorted(entries, key=lambda e: e.relative.as_posix())))


def snapshot_domains(snapshot: SnapshotArchive) -> list[str]:
    domains = {
        entry.relative.parts[1]
        for entry in snapshot.entries
        if len(entry.relative.parts) >= 3
        and entry.relative.parts[0] == "library"
        and entry.relative.parts[1] != "metaskills"
    }
    paths = {entry.relative.as_posix() for entry in snapshot.entries}
    if "PASS/SKILL.md" not in paths:
        raise SnapshotImportError("archive is not a PASS project snapshot: PASS/SKILL.md is missing")
    if not any(path.startswith("library/metaskills/") for path in paths):
        raise SnapshotImportError("archive is missing the required metaskills package")
    if not domains:
        raise SnapshotImportError("archive contains no domain library")
    return sorted(domains)


def extract_archive(
    archive_path: Path, snapshot: SnapshotArchive, destination: Path
) -> Path:
    root = destination / snapshot.root_name
    with zipfile.ZipFile(archive_path) as archive:
        for entry in snapshot.entries:
            target = root.joinpath(*entry.relative.parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(entry.info) as source, target.open("wb") as output:
                shutil.copyfileobj(source, output)
    return root


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


def allowed_skill_names(repo: Path, host: str, domains: list[str]) -> set[str]:
    names = {"pass-authoring"}
    root = repo / host / "skills"
    if not root.is_dir():
        return names
    for skill_root in root.iterdir():
        if skill_root.is_dir() and any(
            skill_targets_domain(skill_root, domain) for domain in domains
        ):
            names.add(skill_root.name)
    return names


def is_domain_file(relative: PurePosixPath, domains: set[str]) -> bool:
    parts = relative.parts
    return (
        len(parts) >= 3
        and parts[0] in {"library", "memory"}
        and parts[1] in domains
    )


def is_all_project_file(
    relative: PurePosixPath,
    repo: Path,
    domains: list[str],
) -> bool:
    if is_domain_file(relative, set(domains)):
        return True
    parts = relative.parts
    if len(parts) == 1 and parts[0] in ROOT_FILES:
        return True
    if parts[0] in {"PASS", "LICENSES", "docs", "tests"}:
        return True
    if len(parts) >= 3 and parts[:2] == ("library", "metaskills"):
        return True
    if len(parts) >= 3 and parts[:2] == ("workspace", "tools"):
        return True
    if len(parts) == 3 and parts[:2] == ("workspace", "release-recipes"):
        return parts[2].startswith("SkillForge_") and parts[2].endswith(".yaml")
    if len(parts) >= 4 and parts[0] in HOST_SKILL_ROOTS and parts[1] == "skills":
        return parts[2] in allowed_skill_names(repo, parts[0], domains)
    return False


def select_entries(
    snapshot: SnapshotArchive,
    repo: Path,
    domains: list[str],
    *,
    all_project_files: bool,
) -> tuple[ArchiveEntry, ...]:
    selected = []
    domain_set = set(domains)
    for entry in snapshot.entries:
        if entry.relative.parts[0] == "SOURCE_INPUT":
            continue
        if is_domain_file(entry.relative, domain_set) or (
            all_project_files
            and is_all_project_file(entry.relative, repo, domains)
        ):
            selected.append(entry)
    if not selected:
        raise SnapshotImportError("the selected import scope contains no files")
    return tuple(selected)


def _run_validation(label: str, command: list[str], cwd: Path) -> str:
    completed = subprocess.run(
        command,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    output = completed.stdout.strip()
    if completed.returncode:
        raise SnapshotImportError(
            f"{label} failed before import:\n{output or '(no output)'}"
        )
    return output.splitlines()[-1] if output else "passed"


def validate_snapshot(snapshot_root: Path, repo: Path) -> list[tuple[str, str]]:
    tools = repo / "PASS" / "tools"
    commands = [
        (
            "card validation",
            [
                sys.executable,
                str(tools / "validate.py"),
                "--library",
                str(snapshot_root / "library"),
            ],
        ),
        (
            "visual references",
            [
                sys.executable,
                str(tools / "verify_references.py"),
                "--library",
                str(snapshot_root / "library"),
            ],
        ),
        (
            "generated indexes",
            [
                sys.executable,
                str(tools / "build_index.py"),
                "--library",
                str(snapshot_root / "library"),
                "--check",
            ],
        ),
    ]
    if (snapshot_root / "memory").is_dir():
        commands.append(
            (
                "skillset memory",
                [
                    sys.executable,
                    str(tools / "memory.py"),
                    "validate",
                    "--memory",
                    str(snapshot_root / "memory"),
                ],
            )
        )
    return [
        (label, _run_validation(label, command, snapshot_root))
        for label, command in commands
    ]


def _safe_target(repo: Path, relative: PurePosixPath) -> Path:
    target = repo.joinpath(*relative.parts)
    resolved = target.resolve(strict=False)
    if resolved != repo and repo not in resolved.parents:
        raise SnapshotImportError(f"import target escapes the repository: {relative}")
    cursor = repo
    for part in relative.parts:
        cursor /= part
        if cursor.is_symlink():
            raise SnapshotImportError(f"import target passes through a link: {relative}")
    return target


def _files_equal(left: Path, right: Path) -> bool:
    if left.stat().st_size != right.stat().st_size:
        return False
    with left.open("rb") as first, right.open("rb") as second:
        while True:
            first_chunk = first.read(1024 * 1024)
            second_chunk = second.read(1024 * 1024)
            if first_chunk != second_chunk:
                return False
            if not first_chunk:
                return True


def plan_changes(
    snapshot_root: Path,
    repo: Path,
    entries: tuple[ArchiveEntry, ...],
) -> ImportPlan:
    changes: list[Change] = []
    unchanged = 0
    for entry in entries:
        source = snapshot_root.joinpath(*entry.relative.parts)
        target = _safe_target(repo, entry.relative)
        if target.exists() and not target.is_file():
            raise SnapshotImportError(f"import target is not a file: {entry.relative}")
        if target.is_file() and _files_equal(source, target):
            unchanged += 1
            continue
        kind = "UPDATE" if target.is_file() else "ADD"
        changes.append(Change(kind, entry.relative, source, target))
    return ImportPlan(tuple(changes), unchanged)


def _atomic_copy(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{target.name}.pass-import-", dir=target.parent
    )
    os.close(descriptor)
    temporary = Path(temporary_name)
    try:
        shutil.copy2(source, temporary)
        os.replace(temporary, target)
    finally:
        temporary.unlink(missing_ok=True)


def apply_changes(repo: Path, plan: ImportPlan) -> None:
    with tempfile.TemporaryDirectory(prefix="pass-import-backup-") as backup_dir:
        backup_root = Path(backup_dir)
        for change in plan.changes:
            if change.target.is_file():
                backup = backup_root.joinpath(*change.relative.parts)
                backup.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(change.target, backup)

        completed: list[Change] = []
        try:
            for change in plan.changes:
                _atomic_copy(change.source, change.target)
                completed.append(change)
        except BaseException:
            for change in reversed(completed):
                backup = backup_root.joinpath(*change.relative.parts)
                if backup.is_file():
                    _atomic_copy(backup, change.target)
                else:
                    change.target.unlink(missing_ok=True)
            raise


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate and preview an updated PASS project ZIP, then import it only "
            "when --apply is explicit."
        ),
        epilog=(
            "The default scope is the archived domain library and domain memory. "
            "Use --all-project-files to include shared PASS files, tests, tools, "
            "matching host skills, and canonical SkillForge recipes. SOURCE_INPUT "
            "is never imported, and absent files never delete repository files."
        ),
    )
    parser.add_argument("archive", type=Path, help="Updated PASS-project-*.zip archive.")
    parser.add_argument(
        "--repo",
        type=Path,
        default=Path(__file__).resolve().parents[2],
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--all-project-files",
        action="store_true",
        help="Also import the shared files the project builder is allowed to export.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply the displayed additions and updates after validation passes.",
    )
    parser.add_argument(
        "--max-file-mb",
        type=float,
        default=25.0,
        help="Maximum uncompressed size of one archive member (default: 25).",
    )
    parser.add_argument(
        "--max-total-mb",
        type=float,
        default=500.0,
        help="Maximum total uncompressed archive size (default: 500).",
    )
    args = parser.parse_args()

    if args.max_file_mb <= 0 or args.max_total_mb <= 0:
        parser.error("archive size limits must be greater than zero")
    repo = args.repo.resolve()
    if not (repo / "PASS" / "tools").is_dir() or not (repo / "library").is_dir():
        parser.error(f"not a PASS repository: {repo}")

    try:
        snapshot = inspect_archive(
            args.archive.resolve(),
            max_file_bytes=int(args.max_file_mb * 1024 * 1024),
            max_total_bytes=int(args.max_total_mb * 1024 * 1024),
        )
        domains = snapshot_domains(snapshot)
        unknown = sorted(set(domains) - set(available_domains(repo)))
        if unknown:
            raise SnapshotImportError(
                "archive contains domain(s) not present in this repository: "
                + ", ".join(unknown)
            )
        selected = select_entries(
            snapshot,
            repo,
            domains,
            all_project_files=args.all_project_files,
        )
        with tempfile.TemporaryDirectory(prefix="pass-project-import-") as temp_dir:
            snapshot_root = extract_archive(args.archive.resolve(), snapshot, Path(temp_dir))
            validation = validate_snapshot(snapshot_root, repo)
            plan = plan_changes(snapshot_root, repo, selected)

            print(f"project root: {snapshot.root_name}")
            print(f"domain(s): {', '.join(domains)}")
            print(
                "scope: "
                + ("all project files" if args.all_project_files else "domain library and memory")
            )
            for label, result in validation:
                print(f"validated {label}: {result}")
            for change in plan.changes:
                print(f"{change.kind:6} {change.relative.as_posix()}")
            print(
                f"plan: {len(plan.changes)} change(s), {plan.unchanged} unchanged, "
                "0 deletions"
            )

            if not args.apply:
                print("dry run only; run again with --apply to import this plan")
                return 0
            apply_changes(repo, plan)
            print(f"applied {len(plan.changes)} change(s); no files were deleted")
            return 0
    except (OSError, SnapshotImportError, zipfile.BadZipFile) as exc:
        print(f"IMPORT FAILED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
