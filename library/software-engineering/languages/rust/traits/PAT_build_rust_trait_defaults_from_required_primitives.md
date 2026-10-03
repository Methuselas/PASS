---
object_id: PAT_build_rust_trait_defaults_from_required_primitives
object_type: pattern
name: Build Rust Trait Defaults From Required Primitives
library_path: [software-engineering, languages, rust, traits]
stage_binding: 0 design
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags: [rust, traits, defaults, interfaces, reuse]
cross_links:
- rel: related_to
  target_object_id: PAT_design_modular_interfaces
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: high
references: []
variants: []
---

# Build Rust Trait Defaults From Required Primitives

## Pattern Rule
**IF** every implementor must supply one type-specific primitive but a higher-level behavior can be derived uniformly from it
**THEN** require the primitive method and implement the shared behavior as a trait default that calls it.
**ELSE** require each behavior directly when no honest common implementation exists.

## Do
- Keep the required method at the smallest type-specific seam, then build richer default methods from that seam.
- Let implementors inherit the default when its semantics fit and override it only when the trait contract permits a genuinely different implementation.
- Design the required primitive so the default can depend on its documented result rather than on hidden fields or concrete types.
- Declare a supertrait when the default calls behavior from another trait, so every implementor is required to provide the dependency the body uses.
- Test both an inherited default and an override, because those are distinct execution paths under the same trait contract.

## Don't
- Don't provide a default merely to make an implementation block shorter when the default is semantically wrong for some conforming type.
- Don't expect an override to invoke the trait's shadowed default implementation; extract shared work into another method when both paths need it.
- Don't make the default depend on behavior the trait never requires, because implementors then cannot know what they must provide.

## Checklist
- Which method is the irreducible type-specific primitive?
- Can the default be implemented using only required trait behavior?
- Does the default call an item from another trait, and if so is that dependency declared as a supertrait?
- Does inheriting the default preserve the contract for every intended implementor?
- If an implementor overrides the method, is any shared behavior still reachable without trying to call the replaced default?

## Notes
A default method is strongest when it is an algorithm over a small required interface. Implementors provide the fact that varies; the trait supplies the derivation that does not. Required primitives and supertraits make every capability used by that derivation visible in the conformance contract.
