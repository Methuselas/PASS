---
object_id: PAT_design_rust_traits_for_dyn_compatibility
object_type: pattern
name: Design Rust Traits for dyn Compatibility
library_path: [software-engineering, languages, rust, traits]
stage_binding: 1 skeleton
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: PAT_design_modular_interfaces
tags: [rust, traits, trait_objects, dyn_compatibility, api_design]
cross_links:
- rel: related_to
  target_object_id: PAT_build_rust_trait_defaults_from_required_primitives
- rel: related_to
  target_object_id: PAT_choose_rust_polymorphism_by_variant_set_and_dispatch_need
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: high
references: []
variants: []
---

# Design Rust Traits for dyn Compatibility

## Pattern Rule
**IF** callers must use a Rust trait through `dyn Trait`
**THEN** make the object-facing methods dispatchable without requiring the erased concrete type, and isolate non-dispatchable generic, `Self`-producing, or statically selected operations behind `Self: Sized` or a separate trait
**ELSE** keep the stronger static interface when every caller works with a known implementor type.

## Do
- Decide that dynamic use is part of the trait's API before publishing it; dyn compatibility constrains later method additions.
- Give dispatched methods a receiver that can be called through the chosen trait-object pointer, such as `&self`, `&mut self`, or an owning pointer receiver supported by the language.
- Keep method type parameters out of the dispatchable surface, because the runtime table cannot contain a separate entry for every caller-selected instantiation.
- Avoid returning bare `Self` from a dispatchable method; return an erased pointer, an associated abstraction, or make the operation available only when `Self: Sized` according to the real contract.
- Use explicit `dyn Trait` syntax and choose the pointer and lifetime that express borrowing or ownership independently from the behavior trait.

## Don't
- Don't treat an old two-rule summary as the full language contract; supertraits, associated items, receivers, opaque returns, and other features also affect dyn compatibility.
- Don't weaken a useful generic or `Self`-returning operation merely to keep it on the dynamic surface when static callers are its real audience.
- Don't assume a trait object contains the original concrete type's fields. It exposes only behavior available through its trait and pointer metadata.
- Don't confuse dyn compatibility with implementability; a trait may be valid and useful for static dispatch while intentionally unusable as a trait object.

## Checklist
- Which callers require `dyn Trait` rather than a generic bound?
- Can every dynamically dispatched method be called without knowing the concrete implementor?
- Does any method introduce its own type parameter or return bare `Self`?
- Which methods should be restricted with `where Self: Sized`?
- Does the chosen reference or owning pointer carry the required lifetime and ownership?

## Notes
A trait object stores a pointer to a value plus metadata used to find the implementation of dispatchable trait methods. The concrete type is erased at the call site, so an operation that needs that exact type or a caller-chosen generic instantiation cannot be represented by one ordinary dynamic-dispatch entry. Rust now calls this property dyn compatibility; older material and diagnostics often call it object safety.
