"""CRQ gate: the per-case baseline/candidate delta and the final qualification gate.

Pure and deterministic. Nothing here reads or writes a run, and there is no
score: every case is compared on its own, and one protected regression vetoes
qualification however many targets improved.
"""

from __future__ import annotations

from typing import Any, Iterable


DELTAS = ("improved", "stable", "regressed", "persistent-fail", "invalid")
STATUSES = (
    "invalid",
    "rejected-regression",
    "rejected-target-failure",
    "blocked-by-synthetic-stress",
    "inconclusive-protection-gap",
    "inconclusive-no-improvement",
    "qualified-for-synthesis-review",
)
GATE_CASE_KEYS = frozenset({
    "case_id", "role", "origin", "required", "positive_qualification_eligible",
    "baseline", "candidate", "delta",
})


def case_delta(baseline: str, candidate: str) -> str:
    """Compare one case's two arms. An invalid arm makes the comparison invalid."""
    for verdict in (baseline, candidate):
        if verdict not in {"pass", "fail", "invalid"}:
            raise ValueError(f"unknown arm verdict: {verdict!r}")
    if baseline == "invalid" or candidate == "invalid":
        return "invalid"
    if baseline == "fail" and candidate == "pass":
        return "improved"
    if baseline == "pass" and candidate == "pass":
        return "stable"
    if baseline == "pass" and candidate == "fail":
        return "regressed"
    return "persistent-fail"


def final_gate(cases: Iterable[dict[str, Any]], *, contamination_confirmed: bool) -> dict[str, Any]:
    """Apply the section 23 precedence to per-case facts.

    Each case carries its plan metadata, both arm verdicts and its delta.
    Non-required cases are diagnostics and never decide the status. Returns the
    status, the reason, the blocking case ids and the cases that earned positive
    qualification. Precedence: invalidity, protected regression, target failure,
    synthetic stress, protection gap, positive improvement, qualified.
    """
    cases = list(cases)
    for case in cases:
        if set(case) != GATE_CASE_KEYS:
            raise ValueError(f"gate case needs exactly {sorted(GATE_CASE_KEYS)}")
        if case["delta"] not in DELTAS:
            raise ValueError(f"unknown delta: {case['delta']!r}")
    required = [case for case in cases if case["required"]]
    real = [case for case in required if case["origin"] != "synthetic"]
    synthetic = [case for case in required if case["origin"] == "synthetic"]
    positive = [
        case["case_id"] for case in real
        if case["role"] == "target" and case["positive_qualification_eligible"]
        and case["delta"] == "improved"
    ]

    def result(status: str, reason: str, blocking: Iterable[dict[str, Any]] = ()) -> dict[str, Any]:
        return {
            "status": status,
            "reason": reason,
            "blocking_cases": [case["case_id"] for case in blocking],
            "positive_qualification_cases": positive if status == "qualified-for-synthesis-review" else [],
        }

    invalid = [case for case in required if case["delta"] == "invalid"]
    if contamination_confirmed or invalid:
        reason = "confirmed contamination invalidates the batch" if contamination_confirmed else (
            "a required case has an invalid arm or comparison; no capability conclusion is drawn"
        )
        return result("invalid", reason, invalid)
    regressed = [case for case in real if case["role"] == "protected" and case["delta"] == "regressed"]
    if regressed:
        return result("rejected-regression", "established protected behavior regressed", regressed)
    failed = [case for case in required if case["role"] == "target" and case["candidate"] == "fail"]
    if failed:
        return result("rejected-target-failure", "a required target still fails on the candidate", failed)
    stressed = [case for case in synthetic if case["candidate"] == "fail" or case["delta"] == "regressed"]
    if stressed:
        return result(
            "blocked-by-synthetic-stress",
            "a required synthetic stress case fails; it blocks without ever proving the candidate",
            stressed,
        )
    if not any(case["role"] == "protected" for case in real):
        return result(
            "inconclusive-protection-gap",
            "no required non-synthetic protected case protects established behavior",
        )
    if not positive:
        return result(
            "inconclusive-no-improvement",
            "no eligible non-synthetic target improved from fail to pass",
        )
    return result(
        "qualified-for-synthesis-review",
        "an eligible target improved and every protection held; this never edits canon",
    )
