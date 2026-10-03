---
object_id: PAT_define_custom_rust_iterators_as_next_state_transitions
object_type: pattern
name: Define Custom Rust Iterators as Next-State Transitions
library_path: [software-engineering, languages, rust, iterators]
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: PAT_design_modular_interfaces
tags: [rust, iterators, traits, state_machine, next]
cross_links:
- rel: related_to
  target_object_id: PAT_choose_rust_iteration_by_element_ownership
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: high
references: []
variants: []
---

# Define Custom Rust Iterators as Next-State Transitions

## Pattern Rule
**IF** a Rust type represents a stateful sequence that should compose with standard iterator adaptors
**THEN** implement `Iterator` by naming its item type and making `next` advance exactly one state transition, yielding one item or the end marker.

## Do
- Store only the state needed to decide the next item and the terminal condition.
- Make each `next` call advance consistently before or after yielding according to one documented invariant.
- Return the end marker after exhaustion and keep returning it when the iterator promises fused behavior, adding the fused marker trait only when that promise is true.
- Test the boundary sequence directly: first item, intermediate items, last item, first exhausted call, and any promised repeated-exhaustion behavior.
- Reuse default adaptors only after the direct `next` contract is correct; their behavior inherits every off-by-one and state bug in `next`.

## Don't
- Don't put whole-sequence work in one `next` call; callers rely on incremental progress and may stop early.
- Don't yield an item without updating state when that would repeat it forever.
- Don't claim stronger length, double-ended, exact-size, or fused guarantees unless the implementation maintains their contracts.
- Don't implement a custom iterator when an existing range, collection iterator, generator-like facility, or adaptor composition already expresses the sequence clearly.

## Checklist
- What state identifies the next item and exhaustion?
- Does one call perform one transition and yield at most one item?
- Are the first, last, and exhausted boundaries tested directly?
- Which optional iterator guarantees are truly maintained?
- Do standard consumers produce the expected result from this `next` implementation?

## Notes
The required method is deliberately small: standard consumers and adaptors are built on repeated calls to `next`. Treating it as a state transition exposes the invariant and boundary cases that matter, while the trait's default methods supply the larger vocabulary once that primitive is trustworthy.

