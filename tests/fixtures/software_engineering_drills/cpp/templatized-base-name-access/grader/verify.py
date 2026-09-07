#!/usr/bin/env python3
"""Compile the C++ Drill packet's positive and negative cases with CMake."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


EXPECTED = {
    "this_prefix.cpp": True,
    "using_declaration.cpp": True,
    "explicit_qualification.cpp": True,
    "missing_specialization.cpp": False,
}


class InfrastructureError(RuntimeError):
    pass


def cmake_source(source: Path) -> str:
    escaped = source.resolve().as_posix().replace('"', '\\"')
    return f"""cmake_minimum_required(VERSION 3.20)
project(skillforge_drill_probe LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
if(MSVC)
  add_compile_options(/permissive- /W4)
else()
  add_compile_options(-Wall -Wextra -pedantic-errors)
endif()
add_executable(probe \"{escaped}\")
"""


def visual_studio_environment() -> dict[str, str] | None:
    if os.name != "nt":
        return None
    roots = [
        Path(os.environ.get("ProgramFiles", r"C:\Program Files")),
        Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")),
    ]
    candidates: list[Path] = []
    for root in roots:
        candidates.extend(
            root.glob("Microsoft Visual Studio/*/*/VC/Auxiliary/Build/vcvars64.bat")
        )
    if not candidates:
        return None
    vcvars = sorted(candidates, reverse=True)[0]
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".cmd", encoding="utf-8", delete=False
    ) as command_file:
        command_file.write(f'@call "{vcvars}" >nul\n@set\n')
        command_path = Path(command_file.name)
    try:
        configured = subprocess.run(
            [os.environ.get("COMSPEC", "cmd.exe"), "/d", "/c", str(command_path)],
            text=True, capture_output=True,
        )
    finally:
        command_path.unlink(missing_ok=True)
    if configured.returncode:
        raise InfrastructureError(configured.stdout + configured.stderr)
    environment = os.environ.copy()
    configured_keys: set[str] = set()
    for line in configured.stdout.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            normalized = key.upper()
            if normalized not in configured_keys:
                environment[normalized] = value
                configured_keys.add(normalized)
    return environment


def compiler_environment() -> tuple[dict[str, str], list[str]]:
    environment = os.environ.copy()
    generator: list[str] = []
    if os.name == "nt" and not shutil.which("cl", path=environment.get("PATH")):
        environment = visual_studio_environment() or environment
    if os.name == "nt" and shutil.which("nmake", path=environment.get("PATH")):
        generator = ["-G", "NMake Makefiles"]
    return environment, generator


def compile_one(
    cmake: str,
    source: Path,
    work_root: Path,
    environment: dict[str, str],
    generator: list[str],
) -> tuple[bool, str, Path | None]:
    source_root = work_root / source.stem / "source"
    build_root = work_root / source.stem / "build"
    source_root.mkdir(parents=True)
    (source_root / "CMakeLists.txt").write_text(cmake_source(source), encoding="utf-8")

    configure = subprocess.run(
        [cmake, "-S", str(source_root), "-B", str(build_root), *generator],
        text=True, capture_output=True, env=environment,
    )
    output = "$ cmake configure\n" + configure.stdout + configure.stderr
    if configure.returncode:
        raise InfrastructureError(output)

    build = subprocess.run(
        [cmake, "--build", str(build_root), "--target", "probe"],
        text=True, capture_output=True, env=environment,
    )
    output += "\n$ cmake build\n" + build.stdout + build.stderr
    executable = None
    if build.returncode == 0:
        candidates = [
            path for path in build_root.rglob("probe*")
            if path.is_file() and path.suffix.lower() in ("", ".exe")
        ]
        executable = candidates[0] if candidates else None
    return build.returncode == 0, output, executable


def verify(answer_dir: Path, starter: Path, evidence_dir: Path) -> list[str]:
    cmake = shutil.which("cmake")
    if not cmake:
        raise InfrastructureError("cmake is not available on PATH")
    environment, generator = compiler_environment()
    evidence_dir.mkdir(parents=True, exist_ok=True)
    problems: list[str] = []

    sources = {"broken.cpp": (starter, False)}
    sources.update({name: (answer_dir / name, should_compile) for name, should_compile in EXPECTED.items()})
    for name, (source, should_compile) in sources.items():
        if not source.is_file():
            problems.append(f"missing answer file: {source}")

    ranking = answer_dir / "RANKING.md"
    if not ranking.is_file():
        problems.append(f"missing answer file: {ranking}")
    if problems:
        return problems

    with tempfile.TemporaryDirectory(prefix="skillforge-cpp-drill-") as temporary:
        work_root = Path(temporary)
        for name, (source, should_compile) in sources.items():
            compiled, output, executable = compile_one(
                cmake, source, work_root, environment, generator
            )
            (evidence_dir / f"{Path(name).stem}.txt").write_text(output, encoding="utf-8")
            if compiled != should_compile:
                expectation = "compile" if should_compile else "fail to compile"
                problems.append(f"{name}: expected to {expectation}")
                continue
            if compiled:
                if executable is None:
                    problems.append(f"{name}: compiler succeeded but executable was not found")
                    continue
                run = subprocess.run([str(executable)], text=True, capture_output=True)
                if run.returncode:
                    problems.append(f"{name}: executable returned {run.returncode}")

    ranking_text = ranking.read_text(encoding="utf-8").casefold()
    for term in ("this->", "using", "qualification", "virtual dispatch"):
        if term.casefold() not in ranking_text:
            problems.append(f"RANKING.md does not discuss {term}")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("answer_dir", nargs="?", type=Path)
    parser.add_argument("--self-test", action="store_true", help="Use the hidden reference answers.")
    parser.add_argument("--evidence-dir", type=Path, help="Where compiler transcripts are retained.")
    args = parser.parse_args()

    grader = Path(__file__).resolve().parent
    packet = grader.parent
    if args.self_test == (args.answer_dir is not None):
        parser.error("choose exactly one of --self-test or answer_dir")
    answer_dir = grader / "reference" if args.self_test else args.answer_dir.resolve()
    evidence_dir = args.evidence_dir

    try:
        if evidence_dir is None:
            if args.self_test:
                with tempfile.TemporaryDirectory(prefix="skillforge-cpp-evidence-") as temporary:
                    problems = verify(answer_dir, packet / "taker/starter/broken.cpp", Path(temporary))
            else:
                problems = verify(answer_dir, packet / "taker/starter/broken.cpp", answer_dir / "evidence")
        else:
            problems = verify(answer_dir, packet / "taker/starter/broken.cpp", evidence_dir.resolve())
    except InfrastructureError as exc:
        print(f"INFRASTRUCTURE ERROR: {exc}", file=sys.stderr)
        return 2

    if problems:
        for problem in problems:
            print(f"FAIL: {problem}")
        return 1
    print("PASS: positive cases compiled and ran; negative cases failed to compile")
    print("MANUAL REVIEW REQUIRED: inspect diagnostics and RANKING.md against SUCCESS_CHECK.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
