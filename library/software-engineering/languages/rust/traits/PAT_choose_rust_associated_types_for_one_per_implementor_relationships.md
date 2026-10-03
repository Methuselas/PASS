---
object_id: PAT_choose_rust_associated_types_for_one_per_implementor_relationships
object_type: pattern
name: Choose Rust Associated Types for One-Per-Implementor Relationships
library_path: [software-engineering, languages, rust, traits]
stage_binding: 0 design
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags: [rust, traits, associated_types, generics, api_design]
cross_links:
- rel: related_to
  target_object_id: PAT_constrain_rust_generics_by_required_behavior
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: high
references: []
variants: []
---

# Choose Rust Associated Types for One-Per-Implementor Relationships

## Pattern Rule
**IF** a Rust trait needs a type selected once by each implementor and callers should not choose among several implementations for the same receiver type
**THEN** make that type an associated type in the trait contract.
**ELSE** use a generic trait parameter when one receiver type must support multiple caller-selected type relationships.

## Do
- Name the associated type for its semantic role, then use `Self::TypeName` wherever trait methods consume or produce it.
- Require every implementation to assign the associated type explicitly, so the receiver type determines the relationship without repeated call-site annotations.
- Put bounds on the associated type when every implementation must provide specific behavior.
- Use a generic parameter instead when multiple distinct implementations for one receiver type are part of the intended API.

## Don't
- Don't use a generic trait parameter for a one-per-implementor choice when that would force callers to disambiguate an implementation that should be inherent in the receiver.
- Don't use an associated type when the same receiver legitimately needs several implementations distinguished by the related type.
- Don't leave the associated type's meaning implicit; it is part of the public trait contract even though the concrete type is chosen later.

## Checklist
- Is the related type selected by the implementor or by each caller?
- May one receiver type need more than one implementation with different related types?
- Can method signatures state the relationship through `Self::TypeName` without extra call-site annotations?
- Are required bounds and the semantic meaning of the associated type documented in the trait?

## Notes
Associated types and generic trait parameters both defer a concrete type choice, but they assign that choice to different owners. An associated type makes the implementation the single source of truth. A generic parameter keeps the choice in the trait identity and permits multiple implementations for the same receiver.
