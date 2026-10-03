---
object_id: PAT_encode_rust_ownership_intent_in_function_signatures
object_type: pattern
name: Encode Rust Ownership Intent in Function Signatures
library_path: [software-engineering, languages, rust, ownership]
stage_binding: 1 skeleton
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags: [rust, ownership, borrowing, function_signatures, api_design]
cross_links:
- rel: related_to
  target_object_id: PAT_give_every_acquired_resource_one_named_owner
- rel: related_to
  target_object_id: PAT_convey_usage_through_names_and_types
- rel: related_to
  target_object_id: PAT_dont_mutate_input_parameters
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: medium
references: []
variants: []
---

# Encode Rust Ownership Intent in Function Signatures

## Pattern Rule
**IF** a Rust function accepts a value that is not merely a cheap implicit copy
**THEN** accept `T` when the function takes ownership, `&T` when it only observes borrowed data, or `&mut T` when it must mutate the caller's value exclusively
**ELSE** use a `Copy` value directly when copying is the type's declared semantics.

## Do
- Make consuming a value visible as an owned parameter when the function stores it, destroys it, transforms it into a new owner, or otherwise decides when it is dropped.
- Borrow with `&T` when the call needs temporary read access and the caller should remain able to use the value afterward.
- Require `&mut T` only when in-place mutation is part of the function's contract; the exclusive borrow makes that effect impossible to overlook at the call site.
- Choose the signature before adding clones or ownership-return tuples; those are often symptoms that the boundary says “take” when the operation means “inspect.”

## Don't
- Don't accept owned `T` merely because that is easiest inside the function if the caller must keep using the same value.
- Don't take `&mut T` for a read-only operation; it needlessly excludes concurrent shared borrows and overstates the function's authority.
- Don't assume passing syntax alone tells the story; read the parameter type to determine whether the call moves, copies, shares, or mutably borrows.

## Checklist
- Does the callee need to determine the value's lifetime, or only use it during the call?
- Is mutation of the caller's value intentional and visible as `&mut`?
- Will the caller need the value after the call?
- Is a by-value argument actually `Copy`, or will it move?

## Notes
Rust lets a signature carry an ownership contract that other languages often leave to comments. This card is the boundary decision: owned parameters transfer authority over lifetime, shared references permit observation, and mutable references permit an exclusive mutable phase. The compiler then checks call sites against that declared intent.

