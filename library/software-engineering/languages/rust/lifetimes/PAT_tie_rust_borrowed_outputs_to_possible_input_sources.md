---
object_id: PAT_tie_rust_borrowed_outputs_to_possible_input_sources
object_type: pattern
name: Tie Rust Borrowed Outputs to Possible Input Sources
library_path: [software-engineering, languages, rust, lifetimes]
stage_binding: 1 skeleton
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags: [rust, lifetimes, borrowing, signatures, api_design]
cross_links:
- rel: related_to
  target_object_id: PAT_return_owned_rust_values_created_inside_a_function
- rel: related_to
  target_object_id: PAT_let_rust_structs_own_fields_unless_borrowing_is_the_model
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: high
references: []
variants: []
---

# Tie Rust Borrowed Outputs to Possible Input Sources

## Pattern Rule
**IF** a Rust function can return a reference borrowed from one or more inputs and elision cannot determine which relationship is promised
**THEN** use lifetime parameters to connect the output only to the inputs that can actually supply it.
**ELSE** rely on lifetime elision and keep unrelated references out of the output's validity constraint.

## Do
- Trace every return branch to the storage it may borrow before writing the signature.
- Give possible sources the same lifetime parameter when the output may come from any of them; callers can then use the result only within the overlap that keeps every possible source valid.
- Leave an unrelated reference on its own lifetime when the function never returns data borrowed from it.
- Return an owned value when the result is created locally and no caller-owned input can keep a borrowed result alive.

## Don't
- Don't treat a lifetime annotation as a request to extend how long a value lives; it only states a relationship the borrow checker must enforce.
- Don't attach one lifetime parameter to every reference mechanically, because that can reject callers for a relationship the implementation does not need.
- Don't assign an unconstrained output lifetime to a reference into a local value; no annotation can make dropped storage remain valid.
- Don't reach for `'static` unless the referenced data genuinely remains available for the entire program.

## Checklist
- For every returned reference, which input or static storage can own the referent?
- Do all inputs sharing the output lifetime represent possible return sources?
- Could an unrelated input have a shorter lifetime without invalidating the result?
- Does the signature reject use of the result after any possible source has expired?

## Notes
Lifetime parameters describe provenance and usable overlap, not duration by decree. A signature that may return either of two borrowed inputs must conservatively connect the result to both. A signature that always returns the first input should connect the result only to the first, even when a second borrowed argument participates in the computation.

