---
object_id: PAT_choose_a_comprehension_over_map_and_filter_unless_a_function_exists
object_type: pattern
name: Choose a Comprehension Over map and filter Unless a Function Exists
library_path:
- software-engineering
- languages
- python
- iteration
stage_binding: 2 block
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- python
- iteration
- comprehensions
- functional-tools
cross_links:
- rel: related_to
  target_object_id: PAT_build_a_list_with_a_comprehension_instead_of_a_manual_append_loop
- rel: related_to
  target_object_id: PAT_know_whether_an_iterable_supports_multiple_passes_before_reusing_it
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Choose a Comprehension Over map and filter Unless a Function Exists

## Pattern Rule
**IF** applying an operation to every item of an iterable, or keeping only the items that pass a test
**THEN** write a comprehension by default, and reach for `map` or `filter` when the operation is already a named function — `map(str.upper, lines)` says what it does with nothing invented, while a comprehension covers every case where the work is an expression
**ELSE** when the goal is to collapse an iterable into one value rather than build a collection, use the purpose-built reducer — `sum`, `min`, `max`, `any`, `all`, `math.prod`, `str.join` — and keep `functools.reduce` for the rare accumulation none of them express

## Do
- Prefer the comprehension when the per-item work is an expression; `map` requires a function, so the alternative costs a lambda invented on the spot to say the same thing.
- Prefer `map` when a suitable function already exists, especially a builtin or a method, since the call then reads as its own description.
- Replace a `filter` plus lambda with the comprehension's `if` clause; both compute the same result, and the comprehension needs no second callable.
- Pass several iterables to `map` when the function takes several arguments and items should be consumed in parallel; that is the one shape a single comprehension does not express directly.
- Import `reduce` from `functools` where it is genuinely needed; it is not a builtin and has to be imported before use.

## Don't
- Don't reach for a reduction over a lambda when a named reducer exists; totals, extremes, products, and any/all tests are clearer at a glance than a two-argument function applied once per item.
- Don't forget that `map` and `filter` produce results lazily: wrap the call in `list` when the results must be displayed, counted, or scanned more than once.
- Don't chain a `map` onto a `filter` to build a pipeline that one comprehension with an `if` clause would state on a single line.
- Don't write a comprehension purely for its side effects and discard the collection it builds; that is a loop wearing an expression's syntax.

## Checklist
- Does the per-item work already have a name, or would `map` require a lambda written just for this call?
- If the result is a single value rather than a collection, is there a named reducer for it?
- Is the lazy result consumed exactly once, or does it need materialising first?
- Would the comprehension and the functional version read differently enough for the choice to matter here?

## Notes
These tools overlap almost entirely, because comprehensions arrived later and cover the same ground; what survives is a narrow distinction about whether a function already exists. Where one does, passing it is the shorter and more direct statement; where one does not, a comprehension avoids creating a throwaway function to satisfy a tool that demands one. Reduction is the exception worth remembering separately, since the general accumulator was moved out of the builtins while the specific reducers that replaced it in everyday use stayed.
