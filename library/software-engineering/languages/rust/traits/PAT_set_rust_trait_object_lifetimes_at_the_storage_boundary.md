---
object_id: PAT_set_rust_trait_object_lifetimes_at_the_storage_boundary
object_type: pattern
name: Set Rust Trait Object Lifetimes at the Storage Boundary
library_path: [software-engineering, languages, rust, traits]
stage_binding: 1 skeleton
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags: [rust, traits, trait_objects, lifetimes, borrowing, api_design]
cross_links:
- rel: related_to
  target_object_id: PAT_design_rust_traits_for_dyn_compatibility
- rel: related_to
  target_object_id: PAT_express_rust_nested_borrow_validity_with_outlives_bounds
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: high
references: []
variants: []
---

# Set Rust Trait Object Lifetimes at the Storage Boundary

## Pattern Rule
**IF** a Rust trait object may erase an implementor that contains non-`'static` references
**THEN** make the object lifetime follow the containing borrow or state an explicit `dyn Trait + 'a` bound at the storage or return boundary.
**ELSE** omit the bound only after confirming that the contextual default matches the ownership contract.

## Do
- Let `&'a dyn Trait` or `&'a mut dyn Trait` carry the containing reference lifetime when the object is borrowed through that reference.
- On a `Box` or another owning pointer, add `+ 'a` to the `dyn Trait` object when the erased implementor may borrow data for `'a`; an unqualified boxed trait object in a type position commonly means `+ 'static`.
- Resolve omitted bounds from the containing type first and then from the trait's own lifetime bounds; use an explicit bound when those rules yield no unique intended lifetime.
- Use `+ '_` when ordinary elision should determine the object lifetime but spelling out that it is not an accidental `'static` default improves the boundary.

## Don't
- Don't read ownership of the trait-object pointer as ownership of everything the erased implementor references.
- Don't add `'static` merely to satisfy a return type when the implementor legitimately borrows caller-owned data.
- Don't rely on expression inference to define a public field, alias, parameter, or return type whose omitted object lifetime has a stronger type-position default.
- Don't use pre-2018 bare trait-object syntax; write `dyn Trait` explicitly.

## Checklist
- Can any intended implementor contain borrowed data?
- Which pointer or container holds the trait object, and what lifetime does that container contribute?
- In this exact type position, would omission infer a lifetime or default to `'static`?
- Does an explicit `+ 'a` describe how long the erased value's internal references must remain valid?
- Does a compiler check include both a borrowed implementor that should pass and an overlong use that should fail?

## Notes
Trait-object erasure hides the concrete implementor, not its validity obligations. The object lifetime bound limits which borrowed implementors may inhabit the erased type. Because the default changes with context, storage and return types are the safest place to make a non-`'static` contract visible.
