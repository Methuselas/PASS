---
object_id: PAT_default_to_plain_for_over_range_len_manual_indexing
object_type: pattern
name: Default to a Plain for Over range(len())/Manual Indexing
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
foundation_object_id: PAT_choose_the_loop_by_where_it_tests
tags:
- python
- control-flow
- iteration
- enumerate
cross_links:
- rel: related_to
  target_object_id: PAT_choose_the_loop_by_where_it_tests
- rel: related_to
  target_object_id: PAT_copy_a_shared_mutable_object_to_the_depth_the_change_reaches
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Default to a Plain for Over range(len())/Manual Indexing

## Pattern Rule
**IF** iterating across the items of a Python sequence or other iterable
**THEN** write `for item in sequence:` directly, and reach for a helper only when the loop needs more than the bare items — `enumerate(sequence)` when the index is needed alongside the item, a strided slice (`sequence[::n]`) when only every Nth item is needed, or `range(len(sequence))` when the loop must assign back into the sequence by position
**ELSE** when there is no sequence at all, just a repeat count, `range(n)` is the right tool on its own

## Do
- Use plain `for item in sequence:` as the default for any exhaustive scan; it is both less code and, because Python handles the iteration machinery internally, usually faster than a hand-rolled `while` with a counter.
- Reach for `enumerate(sequence)` the moment both the item and its position are needed, instead of maintaining a separate counter variable or indexing with `range(len(sequence))`.
- Reach for a strided slice, `sequence[::2]`, to visit every Nth item; it reads more directly than `range(0, len(sequence), 2)` indexing.
- Reserve `range(len(sequence))` for the one case none of the above covers: assigning back into the sequence by position while iterating.

## Don't
- Don't index a sequence with `range(len(sequence))` merely to read its items; `for item in sequence` gets the same items with less code and no index arithmetic to get wrong.
- Don't reach for a `while` loop with a manually incremented index to scan a sequence exhaustively; it does the same job as a plain `for` with more code that can go wrong.
- Don't assume a strided slice is free; unlike `range`, slicing copies the portion of the sequence it selects, which matters for very large sequences.

## Checklist
- Does this loop actually need the index, or only the item?
- If it needs both, is it using `enumerate` rather than a hand-kept counter?
- If it assigns back into the sequence by position, is that the actual reason `range(len(...))` is here?

## Notes
`PAT_choose_the_loop_by_where_it_tests` names the general principle this specializes: a collection-iterating construct removes loop-housekeeping arithmetic entirely, and arithmetic that does not exist cannot be off by one. Python's `for` is that construct; `range(len(...))`-style indexing reintroduces the arithmetic the general principle says to avoid, and earns its place only for the index-dependent or mutate-in-place cases above.

`PAT_copy_a_shared_mutable_object_to_the_depth_the_change_reaches` explains why `for x in L: x += 1` cannot be used for the mutate-in-place case: `x` is rebound each iteration, and the list itself is untouched.
