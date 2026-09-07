---
object_id: PAT_test_against_a_validity_property_when_the_answer_is_not_unique
object_type: pattern
name: Test Against a Validity Property When the Answer Is Not Unique
library_path:
- software-engineering
- core
- testing
stage_binding: 2 block
lane_fit: skill
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- testing
- correctness
- floating_point
- nondeterminism
cross_links:
- rel: related_to
  target_object_id: PAT_treat_floating_point_arithmetic_as_approximate
- rel: related_to
  target_object_id: AP_choose_test_cases_systematically
reference:
  source_title: 'Algorithms in a Nutshell: A Practical Guide'
  author: George T. Heineman, Gary Pollice, Stanley Selkow
confidence: high
references: []
variants: []
---

# Test Against a Validity Property When the Answer Is Not Unique

## Pattern Rule
**IF** the code under test can have more than one correct output for the same input — several optimal paths, a result that depends on floating-point rounding, a tie broken arbitrarily — and you are about to write a test that asserts one exact expected value
**THEN** assert a property the output must satisfy to be correct instead — a check the output can be verified against, or agreement with a second independent implementation within a stated tolerance — so the test does not fail on a legitimately different correct answer
**ELSE** where the correct output really is unique and exactly computable, assert it exactly; a property test is strictly weaker and should not replace an exact one where an exact one is available.

## Do
- State the property in terms a reader can verify independently of the code under test: a returned path actually connects its endpoints and its claimed cost matches its actual one, a returned solution actually satisfies every constraint, a set of results is internally consistent even without knowing which specific member was expected.
- Cross-check against a second, differently implemented method when the space of correct answers is too large to state as a clean property. Where a slow, obviously-correct method and a fast one should agree, comparing their outputs is itself a property test — "these two independently arrived-at answers agree" — and it catches divergence a hand-picked example would miss.
- Compare floating-point results within a stated tolerance rather than for exact equality, and be explicit that the tolerance is a property of the test, not evidence about which implementation is "more correct" when two legitimately differ only in rounding.
- Name what a property test is weaker than, and say so. A check that only confirms "some reasonable output was produced" still catches gross defects but will not catch a subtly wrong tie-break or a boundary the algorithm gets wrong in a way that still looks plausible.

## Don't
- Don't hand-pick one expected output for a problem with multiple correct answers and treat every other correct answer as a failure. That couples the test to one implementation's arbitrary tie-breaking rather than to correctness, and a later change that picks a different, equally correct answer will look like a regression when it is not one.
- Don't let a tolerance-based check hide a real defect behind "that's just floating point." A property or tolerance test should still fail deterministically on a genuinely wrong answer — if it cannot distinguish a defect from acceptable variation, the tolerance is too loose or the property too weak.
- Don't skip testing an algorithm just because its answer space is large or its output nondeterministic. The absence of one exact expected value is a reason to test differently, not a reason to test less.

## Checklist
- Does this problem have more than one correct output for at least some inputs?
- If so, does the test assert a checkable property rather than one hand-picked expected value?
- Where two implementations are compared, are they independent enough that their agreement is actually evidence?
- Is any floating-point comparison using a stated tolerance rather than exact equality, and is the tolerance justified?
- Would this test still fail on a genuine defect, or only on a difference from one arbitrary reference answer?

## Notes
The failure this guards against is easy to miss because it looks like ordinary testing discipline — pick an input, compute the expected output, assert it — and only shows up as a flaky-looking failure once a legitimate alternate answer appears. The usual response is to hand-adjust the expected value rather than notice the test was asking the wrong question in the first place; both responses make the suite pass, but only one of them stops it from failing the same way again.

The underlying move connects to designing for testability generally: a property worth asserting has to be checkable without re-deriving the algorithm's own logic, the same way a certificate on an intractable problem's answer has to be checkable without redoing the work that produced it. A test that can only be satisfied by recomputing the exact answer with the same method under test is not actually testing anything.
