---
object_id: PAT_choose_a_rust_struct_form_by_the_meaning_of_its_fields
object_type: pattern
name: Choose a Rust Struct Form by the Meaning of Its Fields
library_path: [software-engineering, languages, rust, structs]
stage_binding: 0 design
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags: [rust, structs, tuple_structs, domain_types, modeling]
cross_links:
- rel: related_to
  target_object_id: PAT_encapsulate_related_data_together
- rel: related_to
  target_object_id: PAT_convey_usage_through_names_and_types
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: medium
references: []
variants: []
---

# Choose a Rust Struct Form by the Meaning of Its Fields

## Pattern Rule
**IF** each component of a Rust product type has a distinct role that callers must read or construct correctly
**THEN** use a named-field struct
**ELSE** use a tuple struct when the type name supplies the missing meaning and field names would be redundant, or a unit-like struct when the type carries behavior or identity but no instance data.

## Do
- Give related values one domain type when passing them separately would leave their relationship and order implicit.
- Use named fields when two fields share a type but mean different things, or when call sites benefit from construction by name rather than position.
- Use a tuple struct to prevent interchange with another structurally identical tuple while retaining positional access that remains obvious.
- Use a unit-like struct for a marker or trait implementation whose type matters but whose instances need no stored fields.

## Don't
- Don't use a plain tuple when callers must memorize whether position zero means width, height, source, destination, or another distinct role.
- Don't choose a tuple struct merely to save field names when positional meaning will be unclear at use sites.
- Don't add empty or dummy fields to a type that exists only to carry type-level behavior.

## Checklist
- Does each field have a name callers need to see?
- Would swapping same-typed positions compile while changing meaning?
- Is the type distinction useful even when field labels are redundant?
- Does this type need stored data at all?

## Notes
Rust's three struct forms trade explicit field meaning against compact positional representation. The choice is not about syntax length: it determines which mistakes the type system and call-site spelling make visible.

