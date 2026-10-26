---
object_id: PAT_prefer_tagged_rust_enums_unless_overlapping_representation_is_required
object_type: pattern
name: Prefer Tagged Rust Enums Unless Overlapping Representation Is Required
library_path:
- software-engineering
- languages
- rust
- unsafe
stage_binding: 1 skeleton
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- rust
- enum
- union
- unsafe
- ffi
- repr-c
cross_links:
- rel: related_to
  target_object_id: PAT_isolate_rust_ffi_behind_one_audited_boundary
- rel: related_to
  target_object_id: PAT_encode_rust_alternatives_with_data_carrying_enum_variants
reference:
  source_title: Practical System Programming for Rust Developers
  author: Prabhu Eshwarla
confidence: medium
references: []
variants: []
---

# Prefer Tagged Rust Enums Unless Overlapping Representation Is Required

## Pattern Rule
**IF** a Rust value represents one of several alternatives
**THEN** use an enum so the active alternative is represented in the type, and use a union only when overlapping storage or an external layout contract is itself a requirement
**ELSE** keep ordinary data in structs or other safe representations instead of introducing untagged reinterpretation

## Do
- Model ordinary closed alternatives with enums so pattern matching and the type system track which payload is valid.
- Use a union only after identifying the concrete representation requirement that an enum cannot satisfy, such as matching an external C union or deliberately overlapping storage.
- Apply `#[repr(C)]` when the union must match the target platform's C layout, not merely because the type contains unsafe data.
- Maintain an external discriminant or another explicit invariant that proves which interpretation is valid before an unsafe union-field read.

## Don't
- Don't claim a Rust union has a compiler-tracked "active field"; union storage carries no such tag.
- Don't read a union field merely because another field was most recently written; prove that the stored bytes are valid for the field type being read under the program's representation contract.
- Don't expose raw union interpretation throughout safe application code when the boundary can validate it once and convert it to an enum.

## Checklist
- Does the requirement truly need overlapping representation, or only one-of-many semantics?
- If a union is required, what invariant or discriminant proves the valid interpretation at each read?
- Is `repr(C)` required by an ABI/layout contract?
- Can the union be converted to a tagged safe type at the boundary where its invariant is known?

## Notes
Rust unions overlap field storage and have no notion of an active field; reading a field interprets the stored bytes as that field's type and therefore requires `unsafe`. Enums solve a different problem: representing alternatives with an explicit discriminant and safe variant access. FFI is a common reason to require a C-compatible union layout, but it is not the definition of a union's usefulness—the durable rule is to choose a union only when overlapping representation is part of the contract.
