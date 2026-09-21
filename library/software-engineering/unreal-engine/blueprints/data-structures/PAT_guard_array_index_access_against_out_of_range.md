---
object_id: PAT_guard_array_index_access_against_out_of_range
object_type: pattern
name: Guard Array Index Access Against Out-of-Range
library_path:
- software-engineering
- unreal-engine
- blueprints
- data-structures
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- blueprints
- data_structures
- arrays
- bounds
- defensive_programming
cross_links:
- rel: related_to
  target_object_id: PAT_guard_object_references_with_is_valid
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Guard Array Index Access Against Out-of-Range

## Pattern Rule
**IF** you are reading or writing an array element by index in a Blueprint
**THEN** keep the index within the array's bounds — the last valid index is LENGTH minus 1 (or the LAST INDEX node) — and check the array is not empty before indexing, because an index past the last element gives unexpected results and can cause crashes that are difficult to track down later.
**ELSE** where the index comes from a value you control and can prove is in range, the emptiness check is optional, but the bound still holds.

## Do
- Compute the last valid index as LENGTH minus 1, or use the LAST INDEX node, rather than hard-coding a number.
- Check IS NOT EMPTY (or IS EMPTY) before indexing an array that may be empty.
- Treat the array's length as dynamic: removal, clearing, resizing, or reordering can invalidate an index that was previously safe; recompute bounds from the current array when the collection can change.

## Don't
- Don't access an index greater than the last index — it may give unexpected results and, in turn, cause crashes that are difficult to track down later.
- Don't assume a fixed size when the array can be mutated; especially do not reuse an index after operations that can remove, clear, resize, or reorder elements without revalidating it.
- Don't index an empty array.

## Checklist
- Is every index provably less than LENGTH?
- Is the last index computed from LENGTH or LAST INDEX, not hard-coded?
- Is an empty array checked before indexing?

## Notes
Array indices start at 0, so a four-element array has last index 3. The danger is the off-by-one at the top: an index equal to LENGTH is one past the end. Because the array can change over time, the safe bound should be computed from the current length rather than remembered. Growth changes the last index but does not by itself make an already-valid lower index invalid; shrinkage, clearing, and reordering are the operations that can invalidate a previously safe numeric index.
