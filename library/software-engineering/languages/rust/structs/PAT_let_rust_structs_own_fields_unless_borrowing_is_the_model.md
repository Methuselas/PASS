---
object_id: PAT_let_rust_structs_own_fields_unless_borrowing_is_the_model
object_type: pattern
name: Let Rust Structs Own Fields Unless Borrowing Is the Model
library_path: [software-engineering, languages, rust, structs]
stage_binding: 0 design
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags: [rust, structs, ownership, lifetimes, api_design]
cross_links:
- rel: related_to
  target_object_id: PAT_give_every_acquired_resource_one_named_owner
- rel: related_to
  target_object_id: PAT_return_owned_rust_values_created_inside_a_function
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: medium
references: []
variants: []
---

# Let Rust Structs Own Fields Unless Borrowing Is the Model

## Pattern Rule
**IF** a Rust struct should remain valid independently of the values used to build it
**THEN** store owned field types
**ELSE** store references only when borrowing external data is an intentional part of the type's model and its lifetime relationship can be expressed.

## Do
- Store owned strings, collections, and resources when the struct is responsible for their lifetime.
- Use borrowed fields when the struct is deliberately a view, adapter, parser result, or other object that must not outlive its source.
- Make lifetime parameters describe the actual owner the fields borrow from; they document a relationship rather than extending storage.
- Consider the cost and semantics of construction explicitly when owned fields require moving or copying caller data.

## Don't
- Don't add references to avoid an allocation without accepting the resulting lifetime constraint on the whole struct.
- Don't add `'static` to make a borrowed-field error disappear when the source data is not truly static.
- Don't assume a reference field owns or keeps its referent alive.

## Checklist
- Should the struct be usable after its construction inputs go out of scope?
- Is the struct an owner or a temporary view?
- Which external owner keeps each borrowed field valid?
- Does the public type make that lifetime coupling acceptable to callers?

## Notes
Owned fields simplify a struct's lifetime because its validity depends on itself. Borrowed fields can remove duplication and model views precisely, but they deliberately couple the struct to another owner's lifetime; that coupling is a design property, not merely a compiler annotation.

