---
object_id: PAT_choose_rust_iteration_by_element_ownership
object_type: pattern
name: Choose Rust Iteration by Element Ownership
library_path: [software-engineering, languages, rust, iterators]
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: PAT_encode_rust_ownership_intent_in_function_signatures
tags: [rust, iterators, ownership, borrowing, collections]
cross_links:
- rel: related_to
  target_object_id: PAT_iterate_rust_collections_without_manual_index_bounds
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: high
references: []
variants: []
---

# Choose Rust Iteration by Element Ownership

## Pattern Rule
**IF** Rust code is about to iterate a collection
**THEN** choose the iteration route from the authority each item needs: shared references for observation, mutable references for in-place change, and owned items when the collection or elements should be consumed.

## Do
- Use `iter` when the loop or pipeline only reads elements and the collection remains usable afterward.
- Use `iter_mut` when each step must mutate elements in place while preserving the collection itself.
- Use `into_iter` when the operation should take ownership and may move elements into the result, another owner, or a consuming callback.
- Let the function signature and returned values agree with the chosen route; a consuming transform should not clone elements merely to preserve an input it does not need.
- Check the item type at the first adaptor or loop body so reference depth and pattern matching remain intentional.

## Don't
- Don't add clones to make an ownership mismatch disappear before deciding whether the input should be borrowed or consumed.
- Don't consume a collection when later code still needs it.
- Don't select an iteration route from spelling alone; `for` and many adapters use `IntoIterator`, so the receiver form determines ownership.
- Don't assume every collection yields the same item shape for owned, shared, and mutable iteration.

## Checklist
- Must the original collection remain usable after iteration?
- Does the body need shared access, mutable access, or ownership of each item?
- Is any clone preserving a value that has no later owner?
- Do the closure parameter and result types match the chosen item authority?
- Does the collection's own `IntoIterator` implementation yield the item form you expect?

## Notes
The three common collection routes are ownership choices, not merely iterator syntax. Making that choice first prevents later adapters from accumulating dereferences, clones, and borrow errors that all trace back to the wrong authority at the pipeline entrance.

