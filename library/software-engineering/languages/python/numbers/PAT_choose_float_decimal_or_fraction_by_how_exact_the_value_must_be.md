---
object_id: PAT_choose_float_decimal_or_fraction_by_how_exact_the_value_must_be
object_type: pattern
name: Choose Float, Decimal or Fraction by How Exact the Value Must Be
library_path:
- software-engineering
- languages
- python
- numbers
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: PAT_treat_floating_point_arithmetic_as_approximate
tags:
- python
- floating_point
- decimal
- fractions
- money
- rounding
cross_links:
- rel: related_to
  target_object_id: PAT_treat_floating_point_arithmetic_as_approximate
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Choose Float, Decimal or Fraction by How Exact the Value Must Be

## Pattern Rule
**IF** a Python value holds a non-integer quantity and you are choosing its type, comparing it, or rounding it
**THEN** use `float` for measured or computed quantities that tolerate approximation, `decimal.Decimal` for decimal quantities that must balance to the last digit (money, rates, quoted prices), and `fractions.Fraction` for exact ratios — and compare, round and convert each with the tool built for its type
**ELSE** when a value is already a `float` and must stay one, compare it with `math.isclose` rather than `==` and accept that its last digits are not trustworthy.

## Do
- Build `Decimal` and `Fraction` values from strings or integers: `Decimal('0.1')` is exactly one tenth, while `Decimal(0.1)` faithfully copies the float's error as `0.1000000000000000055511151231257827021181583404541015625`.
- Round money with `Decimal.quantize` and a named rounding mode: `Decimal('2.665').quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)` gives `2.67`. The default mode is half-to-even, which gives `2.66`; choose the mode your domain's rules specify.
- Change precision for one calculation with `with decimal.localcontext() as ctx: ctx.prec = ...`, so the setting cannot leak into unrelated code in the same thread.
- Compare floats with `math.isclose(a, b)`, and pass `abs_tol` whenever either value can be at or near zero — the default relative tolerance makes `isclose(1e-12, 0.0)` false.
- Format floats for display with a format spec (`f"{x:.2f}"`); keep the full value for further arithmetic.
- Use `Fraction.limit_denominator(n)` to recover a simple ratio from a float-derived fraction: `Fraction(0.1)` is `3602879701896397/36028797018963968`, and `limit_denominator(100)` gives `1/10`.

## Don't
- Don't mix `Decimal` with `float` in arithmetic; Python refuses with `TypeError`, and converting the float to make it work reintroduces the error `Decimal` was chosen to avoid.
- Don't expect `round(x, 2)` on a float to follow the printed digits: the float nearest 2.665 lies slightly above it, so it rounds to `2.67` while `round(Decimal('2.665'), 2)` gives `2.66`. Both use half-to-even; the float was never exactly 2.665.
- Don't set `decimal.getcontext().prec` globally inside a library function; every later `Decimal` operation in that thread inherits it.
- Don't use `Fraction` for long running computations without watching the size of its numerator and denominator; exact rationals can grow without bound and slow down.

## Checklist
- Is each non-integer quantity's type chosen by how exact it must be, not by habit?
- Are all `Decimal` and `Fraction` constructors fed strings or integers, not floats?
- Do comparisons of floats use `math.isclose`, with `abs_tol` near zero?
- Is the rounding mode for money stated, rather than inherited?

## Notes
`float` is the hardware binary double, so `0.1 + 0.1 + 0.1 - 0.3` is `5.551115123125783e-17`, not zero, while the same sum in `Decimal('0.1')` or `Fraction(1, 10)` is exactly zero. `Decimal` trades speed for decimal exactness at a chosen precision (28 significant digits by default); `Fraction` keeps an exact numerator and denominator and simplifies them automatically. Mixing is directional: `Fraction + int` stays a `Fraction`, but `Fraction + float` becomes a `float`, so exactness is lost silently at the first float operand.

`round()` in Python 3 rounds halves to the nearest even digit (`round(2.5)` is `2`, `round(3.5)` is `4`) and returns a number, while string formatting returns text. Since Python 3.12, `sum()` of floats uses compensated summation, so `sum([0.1] * 10) == 1.0`; ordering still matters for hand-written accumulation loops, and `math.fsum` remains the explicit choice.
