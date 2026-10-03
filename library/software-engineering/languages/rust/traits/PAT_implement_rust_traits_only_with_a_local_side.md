---
object_id: PAT_implement_rust_traits_only_with_a_local_side
object_type: pattern
name: Implement Rust Traits Only With a Local Side
library_path: [software-engineering, languages, rust, traits]
stage_binding: 0 design
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags: [rust, traits, coherence, orphan_rule, api_design]
cross_links:
- rel: related_to
  target_object_id: PAT_depend_on_interfaces_not_concrete_classes
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: high
references: []
variants: []
---

# Implement Rust Traits Only With a Local Side

## Pattern Rule
**IF** a Rust crate needs a trait implementation for a type
**THEN** make either the trait or an eligible type in the implementation local to that crate, preserving one coherent implementation choice.
**ELSE** introduce a local wrapper or local trait instead of trying to implement a foreign trait directly for a foreign type.

## Do
- Implement an external trait for a local type when interoperability with an established contract is the goal.
- Implement a local trait for external types when the crate owns the behavior contract.
- Wrap an external type in a local newtype when the crate needs a distinct implementation policy for an external trait.
- For a foreign trait with generic parameters, verify that a local eligible type appears before any uncovered type parameter in the implementation's type sequence; the simple "one local type" summary is not the complete rule.
- Treat the wrapper as a real API boundary: expose conversions and forwarding deliberately rather than pretending the wrapped type was extended globally.

## Don't
- Don't design around an implementation whose trait and type are both owned by other crates; coherence rejects that extension point.
- Don't use a wrapper only to silence the rule while leaking the inner type everywhere, because callers then bypass the policy the wrapper was meant to own.
- Don't assume two downstream crates can safely publish competing implementations for the same trait-and-type pair.

## Checklist
- Which crate owns the trait?
- Which crate owns the implementing type under the current coherence rules?
- Do generic parameters and fundamental wrappers leave the proposed local type eligible under the current orphan-rule ordering constraints?
- If neither side is local, should this crate own a new trait or a new wrapper type?
- Does the chosen local side express an intentional policy rather than a syntactic workaround?

## Notes
Rust's coherence rules prevent unrelated crates from making competing global claims about the same trait-and-type pair. The design consequence arrives before the `impl`: choose the side your crate legitimately owns, and introduce a local boundary when neither foreign side can carry your policy.
