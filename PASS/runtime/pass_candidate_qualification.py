#!/usr/bin/env python3
"""Command line for PASS Candidate Refinement & Qualification (CRQ).

The administration itself lives in the `candidate_qualification` package beside
this script; this file only parses arguments and reports. It never writes
`library/` or Skillset Memory, never calls a model, and never judges domain
semantics. Run directories live under
`workspace/candidate-qualification/<domain>/<run-id>/`.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in (None, ""):
    # Run as a script: make the package beside this file importable.
    _HERE = str(Path(__file__).resolve().parent)
    if _HERE not in sys.path:
        sys.path.insert(0, _HERE)

from candidate_qualification.controller import (  # noqa: E402
    BASELINE_ROLES,
    WORKSPACE_BUCKET,
    CandidateQualificationError,
    abandon,
    evaluate,
    finalize,
    freeze_assessment,
    freeze_candidate,
    freeze_execution,
    freeze_plan,
    invalidate,
    load_baseline_manifest,
    open_execution,
    prepare,
    prepare_synthesis,
    stage_candidate,
    status_report,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    prepare_command = commands.add_parser(
        "prepare", help="start a run from one Skillset Memory card_candidate"
    )
    prepare_command.add_argument("--domain", required=True)
    prepare_command.add_argument("--memory-entry", required=True)
    prepare_command.add_argument(
        "--out", type=Path, default=None,
        help=f"run directory; default {WORKSPACE_BUCKET}/<domain>/<next run id>",
    )
    prepare_command.add_argument("--library", type=Path, default=None)
    prepare_command.add_argument("--memory-root", type=Path, default=None)
    prepare_command.add_argument("--max-changed-cards", type=int, default=None)
    prepare_command.add_argument("--max-new-cards", type=int, default=None)
    prepare_command.add_argument(
        "--override-reason", default=None,
        help="required when a ceiling is raised above its default",
    )
    freeze = commands.add_parser(
        "freeze-assessment", help="validate and freeze controller/assessment.json"
    )
    freeze.add_argument("--run", type=Path, required=True)
    for name, text in (
        ("freeze-plan", "validate and freeze the qualification plan and its cases"),
        ("stage-candidate", "copy the revisable cards into candidate/cards/ for authoring"),
        ("freeze-candidate", "account for the candidate, validate its overlay, and freeze it"),
        ("open-execution", "write arm result templates and freeze both arm card bundles"),
        ("freeze-execution", "validate and freeze every arm result and its evidence"),
        ("evaluate", "compute per-case deltas and the final gate; write qualification_result.json"),
        ("prepare-synthesis", "build or advance hierarchical evidence packets before assessment"),
        ("finalize", "check the synthesis disposition, write the report, and close the run"),
    ):
        command = commands.add_parser(name, help=text)
        command.add_argument("--run", type=Path, required=True)
    status = commands.add_parser("status", help="print a read-only run summary")
    status.add_argument("--run", type=Path, required=True)
    for name, text in (
        ("invalidate", "close a run whose qualification is invalid"),
        ("abandon", "close a run intentionally stopped without an evidence claim"),
    ):
        command = commands.add_parser(name, help=text)
        command.add_argument("--run", type=Path, required=True)
        command.add_argument("--reason", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "prepare":
            out, run = prepare(
                domain=args.domain,
                memory_entry_id=args.memory_entry,
                out=args.out,
                library_root=args.library,
                memory_root=args.memory_root,
                max_changed_cards=args.max_changed_cards,
                max_new_cards=args.max_new_cards,
                override_reason=args.override_reason,
            )
            entries = load_baseline_manifest(out, run)["entries"]
            roles = {role: sum(1 for e in entries if e["role"] == role) for role in sorted(BASELINE_ROLES)}
            print(
                f"PREPARED: {run['run_id']} at {out}; baseline "
                + ", ".join(f"{count} {role}" for role, count in roles.items())
                + "; fill controller/assessment.json, then run freeze-assessment"
            )
        elif args.command == "freeze-assessment":
            run = freeze_assessment(args.run)
            print(f"ASSESSMENT FROZEN: {run['run_id']}")
        elif args.command == "freeze-plan":
            run = freeze_plan(args.run)
            print(f"PLAN FROZEN: {run['run_id']}")
        elif args.command == "stage-candidate":
            run = stage_candidate(args.run)
            print(f"CANDIDATE STAGED: {run['run_id']}; edit candidate/cards/ as README.md describes")
        elif args.command == "freeze-candidate":
            run = freeze_candidate(args.run)
            print(f"CANDIDATE FROZEN: {run['run_id']}")
        elif args.command == "open-execution":
            run = open_execution(args.run)
            print(f"EXECUTION OPEN: {run['run_id']}; run both arms of every case as README.md describes")
        elif args.command == "freeze-execution":
            run = freeze_execution(args.run)
            print(f"EXECUTION FROZEN: {run['run_id']}")
        elif args.command == "evaluate":
            run = evaluate(args.run)
            status = status_report(args.run)["gate"]
            print(f"EVALUATED: {run['run_id']}: {status}; canon was not modified")
        elif args.command == "prepare-synthesis":
            report = prepare_synthesis(args.run)
            if report["complete"]:
                print("SYNTHESIS COMPLETE: synthesis/input.json holds the final summary for the assessor")
            else:
                print(
                    f"SYNTHESIS LEVEL {report['level']}: {report['batches']} batch(es); write summary.json "
                    "beside each input.json, then run prepare-synthesis again"
                )
        elif args.command == "finalize":
            run = finalize(args.run)
            print(f"FINALIZED: {run['run_id']}; synthesis/report.md written; library and memory unchanged")
        elif args.command == "status":
            print(json.dumps(status_report(args.run), indent=2, ensure_ascii=False))
        elif args.command == "invalidate":
            run = invalidate(args.run, args.reason)
            print(f"INVALIDATED: {run['run_id']}: {run['invalid_reason']}")
        elif args.command == "abandon":
            run = abandon(args.run, args.reason)
            print(f"ABANDONED: {run['run_id']}: {run['abandoned_reason']}")
        return 0
    except (CandidateQualificationError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
