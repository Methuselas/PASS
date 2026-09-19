"""Module-owned runtime assets: the one place PASS decides what executable code a
module may carry and how a release proves it works.

A module that ships helpers declares them in its `MODULE.yaml`:

    runtime:
      entrypoints:
        - runtime/agentkit.py
      tests: runtime/tests

Everything executable lives under that module's `runtime/` directory, uses only
the Python standard library, and is tested by the declared tests before a release
ships it. Code anywhere else in the library is a validation failure, declared or
not. A runtime keeps its state in the project it serves, never in the installed
skill: releases are frozen.
"""

from __future__ import annotations

import ast
import os
import subprocess
import sys
from pathlib import Path, PurePosixPath

import yaml

MODULE_MANIFEST = "MODULE.yaml"
RUNTIME_DIR = "runtime"
RUNTIME_KEYS = {"entrypoints", "tests"}
IGNORED_DIRS = {"__pycache__", ".pytest_cache"}
CODE_SUFFIXES = {
    ".py", ".pyw", ".pyc", ".sh", ".bash", ".zsh", ".ps1", ".psm1", ".bat", ".cmd",
    ".js", ".mjs", ".cjs", ".ts", ".rb", ".pl", ".php", ".exe", ".dll", ".so", ".dylib",
}


def _relative(value: object) -> PurePosixPath | None:
    if not isinstance(value, str) or not value.strip():
        return None
    path = PurePosixPath(value.strip())
    if path.is_absolute() or ".." in path.parts or "\\" in value:
        return None
    return path


def declared_runtimes(library_root: Path) -> tuple[dict[str, dict], list[tuple[str, str]]]:
    """Module name -> {"root", "entrypoints", "tests"} for every valid declaration."""
    runtimes: dict[str, dict] = {}
    problems: list[tuple[str, str]] = []
    for manifest in sorted(library_root.rglob(MODULE_MANIFEST)):
        module_dir = manifest.parent
        name = module_dir.relative_to(library_root).as_posix()
        try:
            data = yaml.safe_load(manifest.read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError):
            continue  # module_requirements reports unreadable manifests
        if not isinstance(data, dict) or "runtime" not in data:
            continue
        spec = data["runtime"]
        if not isinstance(spec, dict) or not set(spec) <= RUNTIME_KEYS or "entrypoints" not in spec:
            problems.append((name, "runtime must be a mapping with entrypoints and optional tests"))
            continue
        entries = spec["entrypoints"]
        if not isinstance(entries, list) or not entries:
            problems.append((name, "runtime.entrypoints must be a non-empty list"))
            continue
        ok, entrypoints = True, []
        for entry in entries:
            path = _relative(entry)
            if path is None or path.parts[0] != RUNTIME_DIR or path.suffix != ".py":
                problems.append((name, f"runtime entrypoint must be a .py path under {RUNTIME_DIR}/: {entry}"))
                ok = False
            elif not (module_dir / path).is_file():
                problems.append((name, f"runtime entrypoint does not exist: {entry}"))
                ok = False
            else:
                entrypoints.append(path.as_posix())
        tests = spec.get("tests")
        if tests is not None:
            path = _relative(tests)
            if path is None or path.parts[0] != RUNTIME_DIR or len(path.parts) < 2:
                problems.append((name, f"runtime tests must be a directory under {RUNTIME_DIR}/: {tests}"))
                ok = False
            elif not any((module_dir / path).glob("test_*.py")):
                problems.append((name, f"runtime tests directory has no test_*.py: {tests}"))
                ok = False
            else:
                tests = path.as_posix()
        else:
            problems.append((name, "a runtime must declare its tests; a release runs them before shipping"))
            ok = False
        if ok:
            runtimes[name] = {"root": module_dir, "entrypoints": entrypoints, "tests": tests}
    return runtimes, problems


def _stdlib_problems(path: Path, local: set[str]) -> list[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError, UnicodeDecodeError) as exc:
        return [f"cannot parse {path.name}: {exc}"]
    found = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            found.add(node.module.split(".")[0])
    foreign = sorted(found - set(sys.stdlib_module_names) - local)
    return [f"{path.name} imports non-standard-library module(s): {', '.join(foreign)}"] if foreign else []


def runtime_problems(library_root: Path) -> list[tuple[str, str]]:
    runtimes, problems = declared_runtimes(library_root)
    declared_roots = {
        (library_root / name / RUNTIME_DIR).resolve(): name for name in runtimes
    }
    for name, spec in runtimes.items():
        runtime_root = spec["root"] / RUNTIME_DIR
        python_files = [p for p in runtime_root.rglob("*.py") if not IGNORED_DIRS & set(p.parts)]
        local = {p.stem for p in python_files}
        for path in python_files:
            problems.extend((name, text) for text in _stdlib_problems(path, local))
        for path in runtime_root.rglob("*.md"):
            if path.name != "README.md":
                problems.append((name, f"{path.relative_to(spec['root']).as_posix()}: runtime documentation "
                                       "belongs in README.md or --help; any other Markdown would be read as a card"))
    for path in sorted(library_root.rglob("*")):
        if not path.is_file() or IGNORED_DIRS & set(path.relative_to(library_root).parts):
            continue
        inside = any(root == parent for parent in path.resolve().parents for root in declared_roots)
        relative = path.relative_to(library_root).as_posix()
        parts = relative.split("/")
        in_module_runtime = any(
            part == RUNTIME_DIR and (library_root.joinpath(*parts[:index]) / MODULE_MANIFEST).is_file()
            for index, part in enumerate(parts[:-1])
        )
        if not inside and (path.suffix.casefold() in CODE_SUFFIXES or in_module_runtime):
            owner = relative.split("/")[0]
            problems.append((owner, f"{relative}: executable or runtime file outside a declared module runtime"))
    return problems


def run_runtime_tests(module_dir: Path, tests: str) -> tuple[bool, str]:
    """Run a module runtime's declared tests where they sit, without leaving
    bytecode behind in the tree that will ship."""
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    completed = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", str(module_dir / tests), "-p", "test_*.py"],
        cwd=module_dir, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env,
    )
    output = (completed.stdout + completed.stderr).strip()
    return completed.returncode == 0, output.splitlines()[-1] if output else ""
