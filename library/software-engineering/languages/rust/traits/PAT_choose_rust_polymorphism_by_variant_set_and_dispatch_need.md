---
object_id: PAT_choose_rust_polymorphism_by_variant_set_and_dispatch_need
object_type: pattern
name: Choose Rust Polymorphism by Variant Set and Dispatch Need
library_path: [software-engineering, languages, rust, traits]
stage_binding: 0 design
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: PAT_use_generics_for_type_independence
tags: [rust, polymorphism, enums, generics, trait_objects]
cross_links:
- rel: related_to
  target_object_id: PAT_constrain_rust_generics_by_required_behavior
- rel: related_to
  target_object_id: PAT_design_rust_traits_for_dyn_compatibility
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: high
references: []
variants: []
---

# Choose Rust Polymorphism by Variant Set and Dispatch Need

## Pattern Rule
**IF** Rust code must apply common behavior to multiple concrete types
**THEN** use an enum for a closed known set, a generic trait bound for one concrete type per use and static dispatch, or a `dyn Trait` object for an open heterogeneous set chosen at runtime
**ELSE** keep the concrete type visible when polymorphism adds no real substitution requirement.

## Do
- Choose an enum when the complete variant set belongs to the abstraction and exhaustive matching should force every operation to handle additions.
- Choose a generic parameter or `impl Trait` when each collection or call uses one concrete type and callers benefit from static dispatch and specialization by monomorphization.
- Choose a trait object behind a reference or owning pointer when one value or collection must hold different implementor types, or downstream crates must extend the set without changing the owner.
- Define the trait around the behavior the consumer needs rather than around the fields or class hierarchy the source types happen to have.
- Price dynamic dispatch against the actual flexibility it buys; measure if call overhead or lost inlining matters on a hot path.

## Don't
- Don't reach for a trait object merely because several types implement the same trait; homogeneous generic code may express the requirement more directly.
- Don't use an enum for an extension point whose valid implementors are intentionally open to downstream crates.
- Don't promise runtime heterogeneity with a generic collection; one monomorphized instance still has one concrete element type.
- Don't imitate inheritance by forcing unrelated capabilities into one broad trait.

## Checklist
- Is the set of alternatives closed or open?
- Must one collection contain different concrete types at the same time?
- Is the concrete type known at compilation for each use?
- Must downstream code add implementations without editing this crate?
- Does dynamic dispatch occur on a path where measurement justifies concern?

## Notes
These choices solve different substitution problems. Enums preserve concrete variants and make the compiler check a closed set. Generics erase repetition in source while retaining a concrete type in each compiled instance. Trait objects erase the concrete type behind a pointer and select behavior through dynamic dispatch, enabling open heterogeneous collections at the cost of indirect calls and some optimization opportunities.
