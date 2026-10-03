---
object_id: PAT_unpack_or_swap_values_with_sequence_assignment
object_type: pattern
name: Unpack or Swap Values with Sequence Assignment
library_path:
- software-engineering
- languages
- python
- assignment
stage_binding: 2 block
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- python
- assignment
- unpacking
- tuples
cross_links:
- rel: prerequisite_for
  target_object_id: PAT_split_a_sequence_by_position_with_starred_unpacking
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Unpack or Swap Values with Sequence Assignment

## Pattern Rule
**IF** several related values need names at once, or two names need to trade values
**THEN** write a sequence of targets on the left and the matching sequence of values on the right in one assignment — `a, b = b, a` to swap, `x, y, z = values` to unpack — and let Python pair them by position
**ELSE** when the right side's length only sometimes matches the left, don't force this form; confirm the length first or reach for starred unpacking instead

## Do
- Swap two or more names with one tuple assignment, `a, b = b, a`, instead of a temporary variable.
- Mix sequence types freely on the two sides — a tuple of names can unpack a string, a list, or any other iterable of matching length, such as `a, b, c = 'ABC'`.
- Match nested structure on both sides when the data is nested, `(a, b), c = ('SP', 'AM')`, rather than unpacking in two separate steps.
- Confirm the lengths actually match before relying on this form at a boundary; a right side one item short or long raises `ValueError`, not a silent partial assignment.

## Don't
- Don't introduce a temporary variable to swap two names; that is exactly the extra step this form removes, and the manual version is more to type and easier to get backwards.
- Don't assume list- and tuple-target syntax behave differently; `[a, b] = [1, 2]` and `a, b = 1, 2` pair items the same way — the brackets are cosmetic here, not two separate assignment forms.
- Don't unpack a sequence whose length can vary from call to call into a fixed number of plain names; a length mismatch is a runtime `ValueError`, not something caught ahead of time.

## Checklist
- Does the number of names on the left equal the number of items the right side will actually produce?
- If the data is nested, does the shape of the target mirror the shape of the source?
- Could a temporary variable be eliminated here by assigning both sides from one tuple expression?

## Notes
The swap works because Python evaluates the entire right-hand side into a value before performing any of the left-hand assignments, so `a, b = b, a` reads both old values first and only then rebinds `a` and `b` — there is no moment where one target already holds its new value while the expression still needs the other's old one.
