---
object_id: PAT_derive_rust_traits_only_when_generated_semantics_match
object_type: pattern
name: Derive Rust Traits Only When Generated Semantics Match
library_path: [software-engineering, languages, rust, traits]
stage_binding: 0 design
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: PAT_define_your_code_contract_explicitly
tags: [rust, derive, traits, equality, ordering, hashing]
cross_links:
- rel: related_to
  target_object_id: PAT_implement_rust_traits_only_with_a_local_side
- rel: related_to
  target_object_id: PAT_convey_usage_through_names_and_types
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: high
references: []
variants: []
---

# Derive Rust Traits Only When Generated Semantics Match

## Pattern Rule
**IF** a Rust derive macro's structural implementation is the public meaning intended for the type
**THEN** derive the complete coherent trait family and treat field or variant order as part of that behavior
**ELSE** implement the semantic trait deliberately or omit it rather than publishing convenient but false behavior.

## Do
- Decide what equality, ordering, hashing, duplication, and default construction mean for the abstraction before selecting derives.
- Derive `Eq` with `PartialEq` only when equality is reflexive. When the type is hashable, derive or implement `Hash` from the same identity fields so equal values always hash alike.
- Keep `PartialOrd` and `Ord` consistent with equality. Remember that structural derives compare struct fields in declaration order and enum variants by discriminant and then fields.
- Derive `Clone` when fieldwise duplication is correct; add `Copy` only when implicit bitwise duplication is a durable part of the type's contract and every component permits it.
- Give `Default` a useful domain meaning. For an enum, mark one eligible unit variant as the default only when that state is genuinely the natural fallback.
- Test trait laws and observable semantics, such as equality-hash consistency and ordering transitivity, instead of snapshotting unstable hash values.

## Don't
- Don't derive a trait solely because every field satisfies the compiler bounds.
- Don't derive one member of a semantic family and hand-write another from different fields unless their required laws are proved and tested.
- Don't let incidental field or variant reordering silently redefine externally observed sort order.
- Don't use `Debug` as a substitute for a stable user-facing `Display` contract.
- Don't derive `Default` when there is no unsurprising valid default value.

## Checklist
- Which fields define equality and identity?
- If hashing is exposed, do equal values necessarily produce equal hashes?
- Is the order partial or total, and does it agree with equality?
- Would reordering fields or variants change behavior users observe?
- Is duplication implicit and trivial enough for `Copy`, or should it remain explicit through `Clone`?
- Is the default state valid and unsurprising?

## Notes
Derive removes implementation repetition; it does not make the generated meaning correct for the domain. Structural behavior is most reliable when the representation already is the abstraction. When the representation contains caches, metadata, presentation fields, or a business-specific ordering key, a manual implementation or a separate comparison key can state the real contract more honestly.
