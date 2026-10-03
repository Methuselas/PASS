---
object_id: PAT_iterate_rust_collections_without_manual_index_bounds
object_type: pattern
name: Iterate Rust Collections Without Manual Index Bounds
library_path: [software-engineering, languages, rust, control-flow]
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags: [rust, loops, iteration, collections, bounds_safety]
cross_links:
- rel: related_to
  target_object_id: PAT_choose_the_loop_by_where_it_tests
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: medium
references: []
variants: []
---

# Iterate Rust Collections Without Manual Index Bounds

## Pattern Rule
**IF** a Rust loop's purpose is to process each member of a collection or range
**THEN** use `for` with the collection's iteration route instead of maintaining an index and bound by hand
**ELSE** keep an index only when the position itself is part of the required result or access pattern.

## Do
- Iterate the collection directly when the body needs only each element.
- Use the collection's length-derived or iterator-provided facilities when positions are needed, so the bound still follows the data.
- Express counted repetition with a range and iterator adapters such as `rev` rather than a mutable counter when that states the sequence directly.
- Select the borrowing or consuming iteration form that matches whether the collection must remain usable afterward.

## Don't
- Don't duplicate a fixed collection length in a `while` condition; changing the collection can turn that number into an out-of-bounds panic or a skipped element.
- Don't reach for indexing merely because another language makes counted loops customary.
- Don't claim direct iteration removes every runtime failure; the body and any remaining indexing still carry their own bounds.

## Checklist
- Is the loop's real input the members, a numeric range, or the positions themselves?
- Does the loop bound derive from the collection rather than repeat its current length?
- Is ownership or borrowing after iteration preserved as intended?
- Has all unnecessary index arithmetic disappeared?

## Notes
Rust checks array and slice indexing, turning a bad index into a panic rather than unchecked memory access. Direct iteration removes the hand-maintained index and bound that create that failure in the first place; the gain is fewer states to prove, not merely shorter syntax.

