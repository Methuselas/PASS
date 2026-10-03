---
object_id: PAT_accept_unsized_rust_types_only_through_an_indirection
object_type: pattern
name: Accept Unsized Rust Types Only Through an Indirection
library_path: [software-engineering, languages, rust, types]
stage_binding: 1 skeleton
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags: [rust, dst, sized, generics, api_design]
cross_links:
- rel: related_to
  target_object_id: PAT_constrain_rust_generics_by_required_behavior
- rel: related_to
  target_object_id: PAT_use_rust_slices_for_views_into_existing_data
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: high
references: []
variants: []
---

# Accept Unsized Rust Types Only Through an Indirection

## Pattern Rule
**IF** a generic Rust API must admit both statically sized values and dynamically sized pointees such as slices or trait objects
**THEN** relax the implicit `Sized` bound with `T: ?Sized` and accept the value through a reference, smart pointer, or another representation whose own size is known
**ELSE** keep the implicit `Sized` bound because by-value storage and movement require a compile-time-known layout.

## Do
- Put the possibly unsized parameter at an indirection boundary that carries the metadata needed to use its referent.
- Choose a slice when the dynamic property is a sequence length and a trait object when the dynamic property is implementation identity and behavior.
- Keep `Sized` unless the API has an actual unsized caller to support.
- Remember that type parameters and associated types are `Sized` by default, while a trait's `Self` is `?Sized` by default; add an explicit `Self: Sized` requirement only to operations that need it.
- Keep an unsized field last when defining a dynamically sized struct, so pointer metadata can describe the unsized tail.

## Don't
- Don't attempt to bind or pass a dynamically sized value directly by value.
- Don't describe every wide pointer's metadata as a byte length; its meaning depends on the pointee kind.
- Don't add `?Sized` mechanically when the function's body or return contract still requires a sized value.

## Checklist
- Which concrete unsized pointee must this API support?
- Which indirection owns or borrows it, and what metadata does that representation carry?
- Does any operation still require a compile-time size for `T` or move a `T` by value?
- Does the bound belong on the whole type, one associated type, or only one method?

## Notes
Generic type parameters and associated types have an implicit `Sized` bound unless it is relaxed. The relaxed bound changes what may be named by the parameter; it does not make an unsized value valid as a local variable or by-value parameter. A pointer to a slice or `str` carries a length, a pointer to a trait object carries a vtable pointer, and a pointer to a composite with an unsized tail carries the tail's metadata.
