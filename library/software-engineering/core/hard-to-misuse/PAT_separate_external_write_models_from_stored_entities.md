---
object_id: PAT_separate_external_write_models_from_stored_entities
object_type: pattern
name: Separate External Write Models From Stored Entities
library_path:
- software-engineering
- core
- hard-to-misuse
stage_binding: 0 design
lane_fit: both
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- api_design
- input_models
- persistence
- authority
- hard_to_misuse
cross_links:
- rel: related_to
  target_object_id: PAT_barricade_dirty_data_at_a_named_boundary
reference:
  source_title: Network Programming with Rust
  author: Abhishek Chanda
confidence: medium
references: []
variants: []
---

# Separate External Write Models From Stored Entities

## Pattern Rule
**IF** an external create or update request is allowed to supply only a subset of the fields carried by the stored or internal entity
**THEN** accept a boundary write model containing only caller-controlled fields, validate it, and construct or mutate the stored entity inside the service where generated and internal fields remain under service control
**ELSE** when the caller is genuinely allowed to supply every field and the boundary object has the same lifecycle and meaning as the stored entity, one model can serve both roles

## Do
- Separate caller-controlled fields from fields assigned or maintained by the service, such as generated identifiers, lifecycle state, ownership metadata, or internal bookkeeping.
- Let create, update, and stored models differ when their writable fields or lifecycles differ; the smallest boundary shape should express exactly what that operation accepts.
- Validate the boundary model before mapping it inward, then apply service defaults, generated values, and persistence-specific state inside the trusted side of the boundary.
- Make the conversion from external write data to internal state explicit enough that a reviewer can see which fields the caller can influence.

## Don't
- Don't deserialize an external write directly into a complete persistence entity when that entity contains fields the caller is not meant to choose.
- Don't require callers to echo service-generated identifiers or internal state merely because the storage representation contains them.
- Don't reuse one convenient data structure across create, update, and storage when doing so silently grants a write operation fields it should not own.

## Checklist
- Which fields may the caller choose, and which are generated or maintained internally?
- Do create and update have the same writable field set, or do they need different boundary models?
- Can any external field overwrite an identifier, ownership value, lifecycle state, or other service-controlled data unintentionally?
- Where are boundary validation and the conversion into stored state performed?

## Notes
The external write shape and the stored entity answer different questions: what a caller is permitted to request versus what the system must retain. Keeping them separate when those answers differ makes field authority visible in the type boundary and prevents persistence convenience from becoming accidental API authority. This applies independently of any particular web framework, serializer, or database.
