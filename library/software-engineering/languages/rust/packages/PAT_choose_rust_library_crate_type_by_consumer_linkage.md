---
object_id: PAT_choose_rust_library_crate_type_by_consumer_linkage
object_type: pattern
name: Choose Rust Library Crate Type by Consumer Linkage
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
- cargo
- crate_type
- linkage
- ffi
- cdylib
cross_links:
- rel: related_to
  target_object_id: PAT_choose_cargo_targets_by_artifact_boundary
- rel: related_to
  target_object_id: PAT_isolate_rust_ffi_behind_one_audited_boundary
reference:
  source_title: Practical System Programming for Rust Developers
  author: Prabhu Eshwarla
confidence: medium
references: []
variants: []
---

# Choose Rust Library Crate Type by Consumer Linkage

## Pattern Rule
**IF** a Rust library must be emitted in a form that a particular linker or non-Rust consumer will load or link
**THEN** choose the library crate type from that consumer boundary: keep ordinary Rust library forms for rustc consumers, use cdylib for a dynamic system library consumed through a foreign ABI, and use staticlib when a non-Rust final link needs a static system library

## Do
- Identify the consumer first: another Rust crate, a foreign-language dynamic loader or linker, or a non-Rust static link.
- Use cdylib for a dynamic library intended to be consumed as a system library from C or another language rather than as a Rust crate dependency.
- Use staticlib when the foreign build needs Rust code packaged into a static system library, and account for the native libraries that final linkage must also satisfy.
- Keep crate type separate from ABI safety: exported functions still need the intended extern ABI, stable symbol exposure where required, and FFI-safe representations and ownership rules.
- Verify the produced artifact and exported interface on every supported target because filenames, linker behavior, and native dependencies are platform-specific.

## Don't
- Do not choose dylib merely because the desired artifact has a .so, .dylib, or .dll extension; dylib is a dynamic Rust library for Rust linkage.
- Do not infer that cdylib or staticlib makes Rust types, Rust's native ABI, unwinding, or ownership conventions safe for foreign callers.
- Do not force a system-library crate type when the consumer is an ordinary Rust crate and the default Rust library artifact is sufficient.

## Checklist
- Who consumes this library artifact: rustc or a foreign/system linker or loader?
- Does the foreign consumer require dynamic loading or static final linkage?
- Which exported symbols and ABI are part of the foreign contract?
- What target-specific linker and native-library requirements must the consuming build satisfy?

## Notes
Cargo target kind and Rust library crate type answer different questions. A library target says that the package produces library code; crate type controls the linkage form of that library. In current Rust, dylib remains a Rust dynamic-library form, while cdylib is the dynamic system-library form intended for consumption from another language.
