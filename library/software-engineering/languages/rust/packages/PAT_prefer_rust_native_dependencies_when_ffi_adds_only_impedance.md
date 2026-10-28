---
object_id: PAT_prefer_rust_native_dependencies_when_ffi_adds_only_impedance
object_type: pattern
name: Prefer Rust-Native Dependencies When FFI Adds Only Impedance
library_path:
- software-engineering
- languages
- rust
- packages
stage_binding: 0 design
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- rust
- dependencies
- ffi
- api-design
- libraries
cross_links: []
reference:
  source_title: 'Practical Rust Web Projects: Building Cloud and Web-Based Applications'
  author: Shing Lyu
confidence: medium
references: []
variants: []
---

# Prefer Rust-Native Dependencies When FFI Adds Only Impedance

## Pattern Rule
**IF** a Rust-native library and an FFI-backed wrapper both satisfy the required capability and the foreign implementation is not itself a requirement
**THEN** prefer the Rust-native option when it avoids a foreign-language API shape, build boundary, or ownership model that the wrapper would expose to Rust callers

## Do
- Compare the caller-facing API rather than only the implementation language; the benefit exists when the native crate can express Rust ownership, error, and type conventions directly.
- Include the foreign build and runtime boundary in the comparison, because a wrapper may add native toolchain, linking, or deployment constraints beyond the Rust package graph.
- Choose the FFI-backed option when the foreign library provides capability, maturity, compatibility, or performance that the native candidate cannot match.

## Don't
- Don't reject a foreign library merely because it is not written in Rust; FFI can be the right boundary when the underlying implementation is the stronger dependency.
- Don't assume a wrapper becomes idiomatic just because its surface uses Rust syntax; foreign ownership and API assumptions can remain visible through it.

## Checklist
- Do both candidates actually satisfy the same functional and operational requirements?
- Does the FFI-backed choice expose foreign calling, ownership, error, build, or deployment constraints to the Rust side?
- Is any advantage of the foreign implementation important enough to justify that boundary?

## Notes
Rust's FFI makes mature foreign libraries available, but wrapping an API designed around another language can preserve assumptions that do not map cleanly onto Rust. Native implementation is therefore a preference only when the candidates are otherwise suitable; it is not a purity rule.
