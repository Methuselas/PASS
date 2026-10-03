---
object_id: PAT_assign_and_test_in_one_while_header_with_the_walrus_operator
object_type: pattern
name: Assign and Test in One while Header with the Walrus Operator
library_path:
- software-engineering
- languages
- python
- control-flow
stage_binding: 2 block
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- python
- control-flow
- loops
- walrus-operator
cross_links: []
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Assign and Test in One while Header with the Walrus Operator

## Pattern Rule
**IF** writing a `while` loop whose test is "keep going while some expression — often a function call — keeps returning a useful value," the same shape as C's `while ((x = next(obj)) != NULL)`
**THEN** use the walrus operator to assign and test in the same header — `while (x := next(obj, None)) is not None: ...process x...` — rather than any of the older workarounds that move the assignment into or around the loop body
**ELSE** when the iteration is really just "step through every item of an iterable," skip all of this and write a plain `for x in obj:` instead; Python's iteration protocol already does the job

## Do
- Write `while (name := expression):` when the loop should keep running for as long as `expression`'s result is truthy, and the result itself, not just its truth value, is needed inside the body.
- Pair the walrus with an explicit comparison, `while (x := next(obj, None)) is not None:`, when a legitimate falsy value (`0`, `''`, an empty list) must still keep the loop going — plain truthiness would stop early on it.
- Prefer a plain `for x in obj:` over any assign-and-test `while` whenever the loop is simply walking an iterable to exhaustion; the walrus form exists for cases a `for` loop cannot express, not as a shorter `for`.
- Fall back to moving the assignment into the loop body with a `break` (`while True: x = next(obj); if not x: break`) only in code that must keep running on Python versions before 3.8, where the walrus operator does not exist.

## Don't
- Don't confuse `:=` with `=`; only `:=` is legal inside an expression context like a `while` test, and that one-character difference is what keeps the classic C `=`-for-`==` typo impossible in Python either way.
- Don't wrap the walrus assignment in extra logic inside the `while` header; keep the header to the assignment and a simple truth or comparison test, and move anything more elaborate into the loop body.
- Don't reach for the walrus just to shorten an already-simple `while x:` loop; it earns its place specifically where an older pattern would have embedded an assignment in the test, not as a general space-saver.

## Checklist
- Does the loop need the assigned value's result, not just whether it was truthy?
- Could a legitimate falsy value stop the loop early, and if so, is the test an explicit comparison rather than bare truthiness?
- Would a plain `for` loop already do this job without any assignment-in-test at all?

## Notes
Python added this operator (`:=`, introduced in 3.8) specifically to cover cases like this one. Older material could only offer workarounds for it — moving the assignment into the loop body with a `break`, moving it into a priming assignment before the loop, or restructuring around a sentinel variable — and those workarounds still work and remain reasonable in code that must run on Python versions before 3.8. Code free to target a current Python has a direct answer the walrus provides in one line, with the same immunity to the `=`/`==` typo that kept plain `=` out of expressions in the first place.
