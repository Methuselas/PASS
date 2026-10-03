---
object_id: PAT_construct_rust_validated_types_through_the_only_open_boundary
object_type: pattern
name: Construct Rust Validated Types Through the Only Open Boundary
library_path: [software-engineering, languages, rust, contracts]
stage_binding: 1 skeleton
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags: [rust, validation, invariants, privacy, constructors]
cross_links:
- rel: related_to
  target_object_id: PAT_make_misuse_impossible_by_removing_invalid_states
- rel: related_to
  target_object_id: PAT_open_rust_visibility_only_through_the_intended_api_path
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: medium
references: []
variants: []
---

# Construct Rust Validated Types Through the Only Open Boundary

## Pattern Rule
**IF** Rust code must preserve a value invariant after construction
**THEN** keep representation fields private and expose constructors and mutators that validate before producing the type
**ELSE** use the simpler underlying type when no durable invariant is gained.

## Do
- Validate external or otherwise fallible input with a constructor returning `Result`.
- Use an infallible constructor only when invalid input is a documented caller bug or cannot be represented at its boundary.
- Keep every field or mutation path that could violate the invariant inaccessible to outside code.
- Expose queries that reveal needed facts without handing out uncontrolled mutation.

## Don't
- Don't validate once while leaving a public field that can later bypass the check.
- Don't panic on malformed runtime data that the caller can reasonably reject or correct.
- Don't create a wrapper type whose public API permits the same invalid states as the wrapped value.

## Checklist
- Can outside code construct the type without validation?
- Can any public mutation break the invariant afterward?
- Is invalid input a caller bug or expected runtime data?
- Does the type's API let downstream code rely on the invariant without rechecking?

## Notes
Private fields make the constructor a validation boundary. Once all open paths preserve the invariant, accepting the validated type in a function signature moves repeated checks into the type system and module boundary.
