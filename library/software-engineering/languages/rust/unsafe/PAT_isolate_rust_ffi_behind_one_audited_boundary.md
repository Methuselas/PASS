---
object_id: PAT_isolate_rust_ffi_behind_one_audited_boundary
object_type: pattern
name: Isolate Rust FFI Behind One Audited Boundary
library_path: [software-engineering, languages, rust, unsafe]
stage_binding: 0 design
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: PAT_barricade_dirty_data_at_a_named_boundary
tags: [rust, ffi, unsafe, abi, validation]
cross_links:
- rel: related_to
  target_object_id: PAT_confine_rust_unsafe_to_a_documented_safe_abstraction
- rel: related_to
  target_object_id: PAT_define_your_code_contract_explicitly
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: high
references: []
variants: []
---

# Isolate Rust FFI Behind One Audited Boundary

## Pattern Rule
**IF** Rust must call foreign code or export symbols to another language
**THEN** put ABI declarations and calls in one narrow module, verify the foreign contract exactly, and translate between raw foreign representations and validated Rust types at that boundary
**ELSE** use an ordinary Rust API whose types and calling convention the compiler can check end to end.

## Do
- Declare foreign items in an `unsafe extern` block and verify the symbol name, ABI, parameter and return layouts, mutability, nullability, ownership, lifetime, and thread rules against the foreign definition.
- Mark an individual foreign item safe only when every value of its Rust signature is valid for the foreign implementation; otherwise require an unsafe call and wrap it only after checking its preconditions.
- Use explicit FFI-safe representations such as C-compatible scalar types and `#[repr(C)]` records where the contract requires them.
- Convert nullable pointers, lengths, status codes, strings, and owned handles into Rust types before they enter the safe interior; convert them back only at the outbound edge.
- Keep callbacks and exported functions from unwinding across an ABI that does not permit it, and make ownership and cleanup responsibility explicit on both sides.
- Use unsafe attribute syntax such as `#[unsafe(no_mangle)]` when exporting a symbol whose global name and linkage obligations the compiler cannot verify.

## Don't
- Don't copy a plausible Rust signature into an extern block and assume the linker proves it correct; a mismatched declaration can compile and still cause undefined behavior.
- Don't spread raw handles and foreign pointers through ordinary application modules.
- Don't create references from a foreign pointer until its validity, alignment, extent, aliasing, and lifetime have been established.
- Don't expose a safe wrapper if the foreign library's documented preconditions still depend on unchecked caller behavior.

## Checklist
- Does the Rust declaration exactly match the foreign ABI and data layout?
- Which inputs may be null, aliased, retained, mutated, or freed by the foreign side?
- Where are error codes and raw representations converted to Rust results and owned types?
- Can a panic or foreign unwind cross this boundary, and is that ABI permitted?
- Is the remaining unsafe surface confined to one reviewable module?

## Notes
An extern block is a promise made by the Rust author, not information verified from a foreign header by the compiler. Rust 2024 therefore requires the block itself to be declared unsafe. Items default to unsafe, although an item may be declared safe when its complete foreign contract is valid for every value admitted by its Rust signature.

The same boundary applies in the other direction. Exported names, layouts, callbacks, and ownership protocols participate in a process-wide contract. A safe Rust interior should see typed values and explicit resources rather than raw ABI details.
