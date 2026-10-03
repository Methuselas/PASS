---
object_id: PAT_state_which_way_integer_division_rounds_negative_operands
object_type: pattern
name: State Which Way Integer Division Rounds Negative Operands
library_path:
- software-engineering
- languages
- python
- numbers
stage_binding: 3 rough
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- python
- integer-division
- modulo
- rounding
- negative-numbers
cross_links:
- rel: related_to
  target_object_id: PAT_bound_an_arithmetic_expression_before_trusting_it
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# State Which Way Integer Division Rounds Negative Operands

## Pattern Rule
**IF** Python code divides integers with `//` or takes a remainder with `%`, and either operand can be negative
**THEN** decide whether the result must round toward negative infinity (what `//` and `%` do) or toward zero (what C, Java and most hardware do), and write the operation that produces that rounding explicitly
**ELSE** when both operands are provably non-negative, `//` and `%` agree with every other convention and need no further thought.

## Do
- Use `//`, `%` and `divmod(a, b)` when floor semantics are what you want: bucketing, calendar arithmetic and wrap-around indexing. `-7 // 2` is `-4` and `-7 % 2` is `1`, so `a % n` always lands in `range(n)` for positive `n` — exactly what a circular buffer index needs.
- For truncation toward zero on integers, compute it without leaving integer arithmetic: `q = abs(a) // abs(b)` with the sign reapplied, or `-(-a // b)` style rewrites for ceiling division. A remainder that keeps the dividend's sign, as in C, is `math.fmod(a, b)` for floats or `a - b * q` with that truncated `q`.
- Convert floats to integers with the function that names the rounding you mean: `math.trunc` or `int()` toward zero, `math.floor` down, `math.ceil` up, `round` to nearest.
- Test the negative case explicitly whenever the operands' signs are not fixed; the positive cases pass under every convention and prove nothing.

## Don't
- Don't port a C, Java or JavaScript formula that uses integer division or `%` on signed values without checking the negative cases; `7 // -2` is `-4` in Python and `-3` in those languages.
- Don't get truncation by writing `int(a / b)` on large integers. `/` always returns a float, so above 2**53 the quotient has already lost digits: `int(10**20 / 3)` is `33333333333333331968`, while `10**20 // 3` is exact.
- Don't assume `//` returns an integer: with a float operand it returns a floored float (`7.5 // 2` is `3.0`).

## Checklist
- Can either operand be negative here, and which rounding does the caller expect?
- Does any quotient on large integers pass through `/`?
- Is there a test with a negative dividend and one with a negative divisor?

## Notes
Python ties `//` and `%` together by the identity `a == (a // b) * b + a % b`, and it chose floor rounding so that the remainder takes the sign of the divisor. That makes modular arithmetic behave mathematically, at the cost of disagreeing with the truncating division most other languages inherited from hardware. Neither choice is wrong; the defect is code written assuming the other one.

Python integers have unlimited precision, so integer division never overflows and `//` on two integers is always exact. The precision loss only appears when a value detours through a float.
