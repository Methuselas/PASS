---
object_id: PAT_choose_a_rust_callable_representation_by_storage_and_dispatch
object_type: pattern
name: Choose a Rust Callable Representation by Storage and Dispatch
library_path: [software-engineering, languages, rust, closures]
stage_binding: 0 design
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: PAT_use_anonymous_functions_only_when_small
tags: [rust, closures, function_pointers, trait_objects, api_design]
cross_links:
- rel: related_to
  target_object_id: PAT_choose_rust_closure_bounds_by_capture_and_call_needs
- rel: related_to
  target_object_id: PAT_isolate_rust_ffi_behind_one_audited_boundary
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: high
references: []
variants: []
---

# Choose a Rust Callable Representation by Storage and Dispatch

## Pattern Rule
**IF** a Rust interface accepts, stores, or returns callable behavior
**THEN** preserve the callable's concrete type with a generic bound or opaque return when one type suffices; use a function pointer only for stateless function-address semantics, and a callable trait object only when runtime type erasure is required.

## Do
- Accept a generic `F` with the weakest sufficient call-trait bound when the caller's concrete type can remain static.
- Return an opaque callable type when every return path produces one concrete hidden type.
- Use a boxed callable trait object when callers must receive one runtime-erased owning type across genuinely different concrete implementations.
- Use an `fn` pointer when captures are forbidden by the contract or an ABI boundary requires a function address.
- Write `impl Fn`, `impl FnMut`, or `impl FnOnce` for an unboxed return whose function body resolves every return path to the same concrete closure type; use an enum when a small closed set of concrete alternatives should stay statically dispatched.
- Spell foreign callbacks with the required ABI and safety qualifiers, such as `unsafe extern "C" fn(...)`, and keep the rest of that contract in the FFI boundary owner.

## Don't
- Don't box a closure merely because its generated concrete type cannot be named.
- Don't use `fn` as a general substitute for closures; it has no storage for captured state.
- Don't erase the callable before deciding its call trait, lifetime, ownership, and thread-safety requirements.
- Don't promise that safe Rust function pointers, unsafe function pointers, and foreign-ABI function pointers are interchangeable; their qualifiers are part of the type.

## Checklist
- Is the callable passed once, stored, or returned?
- Must it carry captured state?
- Do all return paths have one concrete type?
- Is dynamic dispatch or a foreign ABI an actual requirement?
- What lifetime and auto-trait bounds must an erased callable satisfy at its storage boundary?

## Notes
Function items and noncapturing, non-async closures can coerce to matching function pointers. Safe Rust function pointers implement the ordinary call traits, so a generic call-trait parameter can accept both functions and closures. Generic and opaque forms keep static dispatch; trait objects trade that concrete identity for one runtime representation and may add allocation and indirect dispatch when boxed. The companion closure-bound card owns the separate question of `FnOnce`, `FnMut`, or `Fn`.
