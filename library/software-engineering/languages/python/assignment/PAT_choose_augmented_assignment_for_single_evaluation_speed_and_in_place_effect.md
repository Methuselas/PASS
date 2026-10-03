---
object_id: PAT_choose_augmented_assignment_for_single_evaluation_speed_and_in_place_effect
object_type: pattern
name: Choose Augmented Assignment for Single Evaluation, Speed, and In-Place Effect
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
- performance
- aliasing
cross_links:
- rel: related_to
  target_object_id: PAT_copy_a_shared_mutable_object_to_the_depth_the_change_reaches
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Choose Augmented Assignment for Single Evaluation, Speed, and In-Place Effect

## Pattern Rule
**IF** updating a variable based on an operation with its own current value — incrementing a counter, extending a list, building up a string
**THEN** write the augmented form (`+=`, `-=`, `*=`, and so on) instead of spelling out `x = x + y`; it evaluates the left side only once, generally runs faster, and automatically uses an in-place operation instead of a copy when the target type supports one
**ELSE** when the target is shared with other names and a fresh, independent object is specifically needed rather than an in-place change, use the non-augmented form (`x = x + y`) to force a new object instead

## Do
- Default to `+=`/`-=`/etc. for ordinary counters and accumulators; the left-hand target is evaluated only once even when it is a complex expression, not twice as in the spelled-out form.
- Expect `+=` on a list to behave like `.extend()`, not like concatenation: it accepts any iterable on the right — a string, a generator, not just another list — and mutates the list in place rather than building a new one.
- Trust the augmented form to pick the faster operation automatically — appending to a list with `+=` avoids the copy that `L = L + [x]` performs, without having to remember to call `.append`/`.extend` directly.
- Reach for the plain `x = x + y` form specifically when the point is to produce a new, independent object rather than to update the existing one.

## Don't
- Don't assume `L += other` and `L = L + other` are interchangeable for a list; the first mutates `L` in place and is visible through every other name that references the same list, while the second rebinds `L` to a new object and leaves other holders of the old list untouched.
- Don't be surprised when a list passed around under two names changes "by itself" after a `+=` on one of them — this is the general shared-mutable-object hazard, applied to a form that looks like simple arithmetic.
- Don't expect C-style `x++`/`--x`; Python has no auto-increment or auto-decrement operator, because that idea does not map onto a model where immutable numbers cannot be changed in place at all.

## Checklist
- Is the target of a `+=` on a list or dict shared with another name that should not see the in-place change?
- For a performance-sensitive loop, is the augmented form being used instead of rebuilding the object each iteration?
- Where a genuinely new, independent object is required, is the plain, non-augmented form used instead?

## Notes
The in-place/copy distinction is not cosmetic: augmented assignment on a mutable type is permitted to choose whichever implementation is faster, and for sequence types that usually means an in-place extend rather than a concatenation that copies every existing element. The two forms converge for immutable operands (numbers, strings, tuples) precisely because there is no in-place option available to choose — `x += 1` can only ever rebind `x` to a new integer, so the only thing augmented assignment saves there is typing and a second evaluation of the left side.

`PAT_copy_a_shared_mutable_object_to_the_depth_the_change_reaches` owns the general rule for when a change through one name should or should not be visible through another; this pattern is that rule's specific consequence for the augmented-assignment operators.
