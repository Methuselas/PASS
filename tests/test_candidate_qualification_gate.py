"""Direct contracts for the CRQ per-case delta and the section 23 final gate.

The gate is pure: these tests feed it case facts and check the status, the
reason's owner and the blocking cases for every precedence rule, each pair of
adjacent rules, and the aggregate "net win" that must never hide a regression.
"""

from __future__ import annotations

import importlib
import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "PASS" / "runtime"


def load_package(runtime: Path, name: str = "candidate_qualification"):
    """Load the CRQ package found in `runtime` under `name`; return its gate."""
    if name not in sys.modules:
        package_dir = runtime / "candidate_qualification"
        spec = importlib.util.spec_from_file_location(
            name, package_dir / "__init__.py", submodule_search_locations=[str(package_dir)]
        )
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return importlib.import_module(f"{name}.gate")


gate = load_package(RUNTIME)


def case(case_id: str, baseline: str, candidate: str, *, role: str = "target",
         origin: str = "empirical", required: bool = True, eligible: bool | None = None) -> dict:
    if eligible is None:
        eligible = role == "target" and origin != "synthetic"
    return {
        "case_id": case_id, "role": role, "origin": origin, "required": required,
        "positive_qualification_eligible": eligible, "baseline": baseline, "candidate": candidate,
        "delta": gate.case_delta(baseline, candidate),
    }


def protect(case_id: str, baseline: str, candidate: str, **options) -> dict:
    return case(case_id, baseline, candidate, role="protected", **options)


def stress(case_id: str, baseline: str, candidate: str, **options) -> dict:
    return case(case_id, baseline, candidate, role="protected", origin="synthetic", **options)


IMPROVED = case("TARGET_001", "fail", "pass")
HELD = protect("PROTECT_001", "pass", "pass")


class DeltaTests(unittest.TestCase):
    def test_every_verdict_pair(self) -> None:
        expected = {
            ("fail", "pass"): "improved",
            ("pass", "pass"): "stable",
            ("pass", "fail"): "regressed",
            ("fail", "fail"): "persistent-fail",
            ("invalid", "pass"): "invalid",
            ("invalid", "fail"): "invalid",
            ("pass", "invalid"): "invalid",
            ("fail", "invalid"): "invalid",
            ("invalid", "invalid"): "invalid",
        }
        for (baseline, candidate), delta in expected.items():
            with self.subTest(baseline=baseline, candidate=candidate):
                self.assertEqual(gate.case_delta(baseline, candidate), delta)
        self.assertEqual(set(expected.values()), set(gate.DELTAS))

    def test_partial_and_unknown_verdicts_are_refused(self) -> None:
        for verdict in ("partial", None, "PASS", ""):
            with self.subTest(verdict=verdict):
                with self.assertRaises(ValueError):
                    gate.case_delta("pass", verdict)
                with self.assertRaises(ValueError):
                    gate.case_delta(verdict, "pass")


class RuleTests(unittest.TestCase):
    """Each rule on its own, with every earlier rule clear."""

    def run_gate(self, cases: list[dict], contamination: bool = False) -> dict:
        return gate.final_gate(cases, contamination_confirmed=contamination)

    def assert_status(self, cases: list[dict], status: str, blocking: list[str] | None = None,
                      contamination: bool = False) -> dict:
        result = self.run_gate(cases, contamination)
        self.assertEqual(result["status"], status, result)
        if blocking is not None:
            self.assertEqual(result["blocking_cases"], blocking)
        return result

    def test_rule_g_qualified(self) -> None:
        result = self.assert_status([IMPROVED, HELD], "qualified-for-synthesis-review", [])
        self.assertEqual(result["positive_qualification_cases"], ["TARGET_001"])
        self.assertIn("never edits canon", result["reason"])

    def test_rule_a_invalid_arm_on_a_required_case(self) -> None:
        for baseline, candidate in (("invalid", "pass"), ("pass", "invalid"), ("invalid", "invalid")):
            with self.subTest(baseline=baseline, candidate=candidate):
                self.assert_status([IMPROVED, protect("PROTECT_002", baseline, candidate), HELD],
                                   "invalid", ["PROTECT_002"])

    def test_rule_a_confirmed_contamination(self) -> None:
        result = self.assert_status([IMPROVED, HELD], "invalid", [], contamination=True)
        self.assertIn("contamination", result["reason"])
        self.assertEqual(result["positive_qualification_cases"], [])

    def test_rule_a_ignores_a_diagnostic_case(self) -> None:
        self.assert_status([IMPROVED, HELD, protect("DIAG_001", "invalid", "pass", required=False)],
                           "qualified-for-synthesis-review")

    def test_rule_b_protected_regression(self) -> None:
        self.assert_status([IMPROVED, protect("PROTECT_001", "pass", "fail")],
                           "rejected-regression", ["PROTECT_001"])

    def test_rule_b_counts_deterministic_protection(self) -> None:
        self.assert_status([IMPROVED, protect("DET_001", "pass", "fail", origin="deterministic")],
                           "rejected-regression", ["DET_001"])

    def test_rule_b_ignores_a_protected_case_that_already_failed(self) -> None:
        self.assert_status([IMPROVED, HELD, protect("PROTECT_002", "fail", "fail")],
                           "qualified-for-synthesis-review")

    def test_rule_b_ignores_a_diagnostic_regression(self) -> None:
        self.assert_status([IMPROVED, HELD, protect("DIAG_001", "pass", "fail", required=False)],
                           "qualified-for-synthesis-review")

    def test_rule_c_target_failure(self) -> None:
        for baseline in ("fail", "pass"):
            with self.subTest(baseline=baseline):
                self.assert_status([IMPROVED, case("TARGET_002", baseline, "fail"), HELD],
                                   "rejected-target-failure", ["TARGET_002"])

    def test_rule_c_counts_ineligible_required_targets(self) -> None:
        self.assert_status([IMPROVED, case("TARGET_002", "fail", "fail", eligible=False), HELD],
                           "rejected-target-failure", ["TARGET_002"])

    def test_rule_d_synthetic_stress_failure(self) -> None:
        for baseline in ("pass", "fail"):
            with self.subTest(baseline=baseline):
                self.assert_status([IMPROVED, HELD, stress("STRESS_001", baseline, "fail")],
                                   "blocked-by-synthetic-stress", ["STRESS_001"])

    def test_rule_d_passing_stress_earns_nothing(self) -> None:
        result = self.assert_status([IMPROVED, HELD, stress("STRESS_001", "fail", "pass")],
                                    "qualified-for-synthesis-review")
        self.assertEqual(result["positive_qualification_cases"], ["TARGET_001"])

    def test_rule_e_protection_gap(self) -> None:
        self.assert_status([IMPROVED], "inconclusive-protection-gap", [])
        self.assert_status([IMPROVED, stress("STRESS_001", "pass", "pass")], "inconclusive-protection-gap")
        self.assert_status([IMPROVED, protect("DIAG_001", "pass", "pass", required=False)],
                           "inconclusive-protection-gap")

    def test_rule_f_no_improvement(self) -> None:
        self.assert_status([case("TARGET_001", "pass", "pass"), HELD], "inconclusive-no-improvement", [])

    def test_rule_f_needs_an_eligible_real_target(self) -> None:
        self.assert_status([case("TARGET_001", "fail", "pass", eligible=False), HELD],
                           "inconclusive-no-improvement")
        self.assert_status([case("TARGET_001", "fail", "pass", required=False), case("TARGET_002", "pass", "pass"), HELD],
                           "inconclusive-no-improvement")

    def test_synthetic_improvement_never_satisfies_rule_f(self) -> None:
        synthetic_target = case("STRESS_001", "fail", "pass", role="target", origin="synthetic", eligible=True)
        self.assert_status([case("TARGET_001", "pass", "pass"), HELD, synthetic_target],
                           "inconclusive-no-improvement")

    def test_deterministic_target_can_qualify(self) -> None:
        result = self.assert_status([case("DET_001", "fail", "pass", origin="deterministic"), HELD],
                                    "qualified-for-synthesis-review")
        self.assertEqual(result["positive_qualification_cases"], ["DET_001"])


class PrecedenceTests(unittest.TestCase):
    """When two rules fire, the earlier one decides the status."""

    def status(self, cases: list[dict], contamination: bool = False) -> str:
        return gate.final_gate(cases, contamination_confirmed=contamination)["status"]

    def test_each_adjacent_pair(self) -> None:
        regressed = protect("PROTECT_002", "pass", "fail")
        failed = case("TARGET_002", "fail", "fail")
        stressed = stress("STRESS_001", "pass", "fail")
        invalid = protect("PROTECT_003", "pass", "invalid")
        pairs = (
            ([IMPROVED, HELD, invalid, regressed], "invalid"),
            ([IMPROVED, HELD, regressed, failed], "rejected-regression"),
            ([IMPROVED, HELD, failed, stressed], "rejected-target-failure"),
            ([IMPROVED, stressed], "blocked-by-synthetic-stress"),
            ([case("TARGET_001", "pass", "pass")], "inconclusive-protection-gap"),
            ([case("TARGET_001", "pass", "pass"), HELD], "inconclusive-no-improvement"),
        )
        for cases, expected in pairs:
            with self.subTest(expected=expected):
                self.assertEqual(self.status(cases), expected)

    def test_invalid_beats_every_other_status(self) -> None:
        everything = [IMPROVED, protect("PROTECT_002", "pass", "fail"), case("TARGET_002", "fail", "fail"),
                      stress("STRESS_001", "pass", "fail")]
        self.assertEqual(self.status(everything, contamination=True), "invalid")
        self.assertEqual(self.status([*everything, case("TARGET_003", "invalid", "pass")]), "invalid")

    def test_regression_beats_multiple_improvements(self) -> None:
        # Fixture B: two targets fixed, one protected behavior lost.
        cases = [case("TARGET_001", "fail", "pass"), case("TARGET_002", "fail", "pass"),
                 protect("PROTECT_001", "pass", "fail")]
        result = gate.final_gate(cases, contamination_confirmed=False)
        self.assertEqual(result["status"], "rejected-regression")
        self.assertEqual(result["blocking_cases"], ["PROTECT_001"])
        self.assertEqual(result["positive_qualification_cases"], [])

    def test_no_aggregate_net_win_hides_a_regression(self) -> None:
        # Section 24: +1 -1 +1 is a "net win" for a score and a rejection here.
        for improvements in range(1, 6):
            with self.subTest(improvements=improvements):
                cases = [case(f"TARGET_{n:03d}", "fail", "pass") for n in range(1, improvements + 1)]
                cases.append(protect("PROTECT_001", "pass", "fail"))
                cases += [protect(f"PROTECT_{n:03d}", "pass", "pass") for n in range(2, 5)]
                self.assertEqual(self.status(cases), "rejected-regression")


class ShapeTests(unittest.TestCase):
    def test_gate_refuses_unknown_shapes(self) -> None:
        with self.assertRaises(ValueError):
            gate.final_gate([dict(IMPROVED, score=1)], contamination_confirmed=False)
        with self.assertRaises(ValueError):
            gate.final_gate([dict(IMPROVED, delta="better")], contamination_confirmed=False)

    def test_statuses_are_the_designed_seven(self) -> None:
        self.assertEqual(set(gate.STATUSES), {
            "qualified-for-synthesis-review", "rejected-regression", "rejected-target-failure",
            "invalid", "inconclusive-no-improvement", "inconclusive-protection-gap",
            "blocked-by-synthetic-stress",
        })


if __name__ == "__main__":
    unittest.main()
