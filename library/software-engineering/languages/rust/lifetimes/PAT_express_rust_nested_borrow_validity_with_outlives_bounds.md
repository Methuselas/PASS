---
object_id: PAT_express_rust_nested_borrow_validity_with_outlives_bounds
object_type: pattern
name: Express Rust Nested Borrow Validity with Outlives Bounds
library_path: [software-engineering, languages, rust, lifetimes]
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags: [rust, lifetimes, outlives_bounds, generics, borrowing, api_design]
cross_links:
- rel: related_to
  target_object_id: PAT_tie_rust_borrowed_outputs_to_possible_input_sources
- rel: related_to
  target_object_id: PAT_constrain_rust_generics_by_required_behavior
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: high
references: []
variants: []
---

# Express Rust Nested Borrow Validity with Outlives Bounds

## Pattern Rule
**IF** a Rust type or implementation borrows a value whose type can itself contain references with a different validity interval
**THEN** model the intervals separately and add only the outlives relationships required for every nested referent to remain valid while the outer borrow is usable.
**ELSE** use elision or one lifetime parameter when the relationships are genuinely identical.

## Do
- Name lifetimes by role while designing the relationship, such as one for the outer borrow and another for data reachable through the borrowed value.
- Read an outlives bound from right to left as a validity obligation: `'data: 'borrow` requires the data lifetime to cover the borrow lifetime, and `T: 'borrow` requires references contained by `T` to remain valid for that interval.
- Tie a borrowed return value to the lifetime of the storage it actually reaches, not automatically to the shorter-lived wrapper used to access that storage.
- Let the compiler infer outlives relationships that are structurally implied, and write an explicit bound when an API, implementation, or diagnostic needs a relationship that inference does not supply.

## Don't
- Don't assign one lifetime parameter to an outer reference, the value it borrows, and a returned reference merely because that is the shortest annotation; it can impose a false equality and reject a valid caller.
- Don't read `'long: 'short` as an inheritance hierarchy or as a request to prolong storage; it states that `'long` already lasts at least as long as `'short`.
- Don't add `'static` to silence an outlives error unless every reference carried by the constrained type truly satisfies the program-lifetime contract.
- Don't preserve an explicit bound from older code until current compiler behavior shows that the relationship is still required rather than inferred.

## Checklist
- Does each lifetime parameter correspond to a distinct borrow or reachable-data interval?
- For every outer borrow, can all references reachable through its referent remain valid for the borrow's full use?
- Does each explicit `'a: 'b` or `T: 'b` bound express a required relationship rather than accidental equality?
- Is a returned reference tied to its actual backing storage instead of a temporary accessor or wrapper?
- Does the signature compile on the target Rust version with no unnecessary explicit outlives requirement?

## Notes
Nested borrowing has two independent questions: how long the handle is borrowed and how long data reachable through that handle remains valid. Collapsing them can make a temporary parser, view, or wrapper appear to own the validity of longer-lived input data. Outlives bounds express the direction of the dependency without claiming that the intervals are equal.
