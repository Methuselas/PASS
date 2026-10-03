---
object_id: PAT_build_a_list_with_a_comprehension_instead_of_a_manual_append_loop
object_type: pattern
name: Build a List with a Comprehension Instead of a Manual Append Loop
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
cross_links:
- rel: related_to
  target_object_id: PAT_reproduce_the_real_context_before_believing_a_microbenchmark
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Build a List with a Comprehension Instead of a Manual Append Loop

## Pattern Rule
**IF** building a new list, set, or dict by applying an expression to every item of an iterable, optionally keeping only the items that pass a test
**THEN** write it as a comprehension — `[expr for item in iterable]`, add `if cond` to filter, `{expr for item in iterable}` for a set, or `{key_expr: val_expr for item in iterable}` for a dict — instead of a manual loop that appends to a list started empty
**ELSE** once the per-item logic needs more than one expression, has side effects beyond building the result, or stops being easy to read as a single line, write the explicit `for` loop instead

## Do
- Translate directly from a loop that would otherwise be written: `res = []` then `for item in iterable: res.append(expr)` becomes `res = [expr for item in iterable]`, with no change in what gets collected.
- Add `if cond` after the `for` clause to skip items that shouldn't be in the result, rather than wrapping the whole comprehension in a conditional.
- Chain more than one `for` clause when the result should combine items from more than one iterable, exactly as nested `for` loops would, with each clause optionally carrying its own `if`.
- Nest a whole comprehension on the left to build a nested result: an inner comprehension in the expression position produces one row per step of the outer clause, which is how a matrix-shaped result is built rather than a flat one.
- Use a comprehension's iterable position the same way a `for` loop would, including opening a file right there — `[line.rstrip() for line in open(path)]` — so the comprehension itself drives the file's iterator with no separate read step.

## Don't
- Don't keep a comprehension you had to rewrite as indented statements in order to understand; needing that translation to read it is the signal that it should have been written as statements in the first place.
- Don't write a comprehension whose single line does more than most readers can parse in one pass; past roughly one `for`, one `if`, and one transformation, an explicit `for` statement is usually easier to read and to modify later.
- Don't expect a comprehension to mutate anything in place; it always builds a new list, set, or dict, so `L = [x + 1 for x in L]` creates a new object bound back to `L`, leaving any other name still referencing the original list untouched.
- Don't take a "comprehensions are roughly twice as fast" claim as settled fact for your code; relative speed depends on the exact code, the Python release, and whether filter clauses are involved, and can vary release to release.

## Checklist
- Does the comprehension read as a single, clear transformation (optionally filtered), or has it grown past that?
- If multiple `for` clauses are used, does their nesting order match the equivalent nested loops?
- Is the comprehension's result meant to be a new object, not an in-place update of something already referenced elsewhere?

## Notes
A comprehension is never strictly required — it is always translatable to the equivalent `for` loop that appends as it goes — but the common case of collecting the results of running every item through an expression is frequent enough in Python code to be worth its own syntax. `PAT_reproduce_the_real_context_before_believing_a_microbenchmark` applies directly to any performance claim about comprehensions versus loops: measure in your own code and release rather than trusting a rule of thumb.
