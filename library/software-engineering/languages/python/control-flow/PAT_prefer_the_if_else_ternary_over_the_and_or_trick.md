---
object_id: PAT_prefer_the_if_else_ternary_over_the_and_or_trick
object_type: pattern
name: Prefer the if/else Ternary Over the and/or Trick
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
- expressions
- readability
cross_links:
- rel: related_to
  target_object_id: PAT_use_or_to_pick_the_first_truthy_value_or_a_default
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Prefer the if/else Ternary Over the and/or Trick

## Pattern Rule
**IF** a four-line `if`/`else` statement only assigns one of two simple values, or its result needs to be nested inside a larger expression rather than bound to a variable
**THEN** write it as the `Y if X else Z` conditional expression, which short-circuits exactly like the statement form, running only whichever of `Y`/`Z` the test selects
**ELSE** once the branches involve more than a simple expression each, write the full `if`/`else` statement instead of packing logic into an expression

## Do
- Reach for `Y if X else Z` as the direct, mnemonic replacement for a simple two-way `if`/`else` statement that only assigns or returns a value.
- Nest the ternary inside a larger expression (a function argument, another expression) when that's the actual need, since unlike the statement form it is itself an expression.
- Keep both `Y` and `Z` simple; if either branch needs more than one expression's worth of logic, that is the signal to write the statement form instead.

## Don't
- Don't use the older `(X and Y) or Z` idiom in new code; it silently breaks when `Y` itself is falsy, because the `and` would then skip past `Y` and the `or` would fall through to `Z` even though `X` was true.
- Don't assume `(X and Y) or Z` and `Y if X else Z` are freely interchangeable; they only produce the same result when `Y` is guaranteed truthy, which the ternary form never requires.
- Don't reach for `[Z, Y][bool(X)]` as a conditional-expression substitute; indexing evaluates both `Z` and `Y` unconditionally before picking one, so any side effect or error in the unchosen branch still happens.

## Checklist
- Could the `and`/`or` form here ever receive a falsy `Y`, and if so, has it been replaced with the ternary?
- Does a list-indexing conditional trick appear anywhere a side effect or an expensive computation sits in the unchosen branch?
- Have both ternary branches stayed simple enough to read as one expression, rather than growing into something that belongs in a full `if` statement?

## Notes
The ternary short-circuits the same way the Boolean operators and the full `if` statement do — only the selected branch's expression actually runs — which is what makes it a safe, general replacement for the `and`/`or` trick rather than just a shorter way to write the same risk. The `and`/`or` form survives only in code written before the ternary existed, or carried over by habit; new code has no reason to accept its `Y`-must-be-truthy constraint.
