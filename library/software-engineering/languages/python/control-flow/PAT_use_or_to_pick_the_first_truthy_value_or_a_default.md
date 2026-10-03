---
object_id: PAT_use_or_to_pick_the_first_truthy_value_or_a_default
object_type: pattern
name: Use or to Pick the First Truthy Value or a Default
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
- booleans
- short-circuit
cross_links: []
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Use or to Pick the First Truthy Value or a Default

## Pattern Rule
**IF** picking the first nonempty value among several candidates, or substituting a default when one value is empty
**THEN** string the candidates together with `or` — `X = A or B or C or None`, or simply `X = A or default` — and let Python's left-to-right, stop-at-the-first-true evaluation return the answer directly
**ELSE** when a right-hand candidate is produced by a call with side effects that must always run, evaluate it separately before the `or` chain; short-circuiting will skip it otherwise

## Do
- Trust `or` to return one of its actual operands, not a bare `True`/`False`; `2 or 3` is `2`, and `[] or 3` is `3`, which is what makes the "pick the first truthy one" idiom work at all.
- Chain as many candidates as needed: `A or B or C or None` evaluates left to right and returns the first one that is true, falling through to the final explicit default only if every candidate is false.
- Use the simple two-operand form, `A or default`, as the idiomatic way to say "use A if it's meaningful, otherwise fall back."
- Evaluate any candidate whose own evaluation must happen regardless of the result in its own statement first, then combine the saved results with `or`: `tmp1, tmp2 = f1(), f2(); if tmp1 or tmp2: ...`.

## Don't
- Don't write `if f1() or f2(): ...` when `f2` must always run; `or` stops at the first true operand, so a true `f1()` means `f2()` never executes.
- Don't assume `and`/`or` return `True`/`False` the way comparison operators do; only comparisons and equality tests return the dedicated `True`/`False` objects, while `and`/`or` return whichever operand decided the result.
- Don't use this idiom to select among candidates where a legitimately falsy value (`0`, `''`, an empty list) should still win; `or` treats a falsy candidate exactly like a missing one and will skip past it to the next.

## Checklist
- Does every candidate in the chain really deserve to be skipped when it's falsy, or could a legitimate falsy value get silently passed over?
- If a candidate is a function call, does it need to run even when an earlier candidate is already true?
- Is the final fallback in the chain an explicit, unconditional default rather than another candidate that could itself be false?

## Notes
This reads as unusual only because `and`/`or` in Python are value-returning operators, not boolean-flag operators the way C's `&&`/`||` are: each one commits to returning the specific left or right operand that determined the result, rather than converting that decision down to `1`/`0`. The short-circuit behavior that makes the chain efficient is the same mechanism that makes it dangerous to put a required side effect on the losing side of an `or`.
