---
object_id: PAT_choose_rust_library_layer_by_runtime_environment
object_type: pattern
name: Choose the Rust Library Layer by Runtime Environment
library_path:
- software-engineering
- languages
- rust
- packages
stage_binding: 0 design
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- rust
- std
- core
- alloc
- no-std
- embedded
cross_links:
- rel: related_to
  target_object_id: PAT_start_with_portable_interfaces_then_isolate_platform_extensions
reference:
  source_title: Practical System Programming for Rust Developers
  author: Prabhu Eshwarla
confidence: medium
references: []
variants: []
---

# Choose the Rust Library Layer by Runtime Environment

## Pattern Rule
**IF** a Rust crate must run where linking the standard library is unavailable or intentionally excluded
**THEN** use `#![no_std]` with `core`, adding `alloc` only when an allocator is available and heap-backed types are actually required
**ELSE** use `std` by default and reach its re-exported `core` and allocation-backed facilities through the standard library

## Do
- Treat `core` as the platform-agnostic foundation for primitives, traits, and computation that do not require standard-library runtime services.
- Add `alloc` explicitly in a `no_std` crate only when the target provides an allocator and the crate needs facilities such as `Box`, `Vec`, or `String`.
- Keep functionality that requires files, networking, process management, or other unavailable platform services behind a boundary that the target can replace or omit.
- For `no_std` binaries, account for target-specific runtime obligations such as panic handling and entry-point support rather than assuming removing `std` is the only change.

## Don't
- Don't equate `no_std` with "no operating system"; the relevant contract is whether the crate can and should link `std` for the target/runtime.
- Don't import `core` or `alloc` directly in an ordinary `std` crate merely because their types originate there; `std` re-exports the common surface.
- Don't add `alloc` to `no_std` code before establishing that a compatible allocator exists.

## Checklist
- Can this target link and support the Rust standard library?
- Which required operations actually depend on `std` rather than `core`?
- If heap-backed types are needed, where does the allocator come from?
- Does a `no_std` binary provide the runtime pieces its target requires?

## Notes
`#![no_std]` stops automatic linkage of `std` and uses `core` instead. `alloc` supplies heap-backed types when allocation is available without the rest of `std`. The decision is therefore about available runtime services and dependencies, not a simplistic hosted-versus-embedded label: many embedded targets motivate `no_std`, but the attribute itself states a library-linkage contract.
