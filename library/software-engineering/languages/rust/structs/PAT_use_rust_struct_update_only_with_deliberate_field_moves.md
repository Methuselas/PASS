---
object_id: PAT_use_rust_struct_update_only_with_deliberate_field_moves
object_type: pattern
name: Use Rust Struct Update Only With Deliberate Field Moves
library_path: [software-engineering, languages, rust, structs]
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags: [rust, structs, ownership, struct_update, partial_moves]
cross_links:
- rel: related_to
  target_object_id: PAT_clone_rust_values_only_for_independent_ownership
- rel: related_to
  target_object_id: PAT_give_every_acquired_resource_one_named_owner
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: medium
references: []
variants: []
---

# Use Rust Struct Update Only With Deliberate Field Moves

## Pattern Rule
**IF** a new Rust struct value should reuse unspecified fields from a base value
**THEN** use struct-update syntax only after deciding which remaining fields will copy and which will move from the base
**ELSE** initialize fields explicitly or clone only the fields that truly need independent ownership.

## Do
- List changed fields before `..base` and treat every omitted field as an ownership operation, not just a shorthand assignment.
- Check each omitted field's type: `Copy` fields remain available, while moved non-`Copy` fields can make the base partially moved.
- Use the update when consuming the base is intended or when every reused field can copy without invalidating it.
- Prefer explicit initialization when later code must keep using the base as a complete value and that requirement would be easy to miss.

## Don't
- Don't assume `..base` clones omitted fields.
- Don't use the base as a whole after any of its non-`Copy` fields moved into the new value.
- Don't clone every field preemptively merely to preserve the old value; decide whether two owners are actually required.

## Checklist
- Which omitted fields are `Copy`, and which move?
- Must the base remain usable as a complete value afterward?
- Are any still-available fields being mistaken for proof that the whole base remains valid?
- Would explicit field spelling make the ownership result clearer?

## Notes
Struct-update syntax is concise because it performs the same field-level copy or move operations that explicit initialization would perform. The punctuation hides repetition, not ownership consequences.

