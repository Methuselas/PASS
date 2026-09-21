---
object_id: PAT_use_the_dot_product_to_test_direction_alignment
object_type: pattern
name: Use the Dot Product to Test Direction Alignment
library_path:
- software-engineering
- unreal-engine
- blueprints
stage_binding: 0 design
lane_fit: both
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- unreal_engine
- blueprints
- vectors
- dot_product
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Use the Dot Product to Test Direction Alignment

## Pattern Rule
**IF** you need to know the angular relationship between two directions — whether they point the same way, are perpendicular, or point opposite ways
**THEN** take the dot product of the two normalized vectors, which equals the cosine of the angle between them and ranges from -1.0 (opposite) through 0 (perpendicular) to 1.0 (aligned).

## Do
- Normalize both vectors before the dot product so the result is the cosine of the angle.
- Read the result: 1.0 means the same direction, 0 means perpendicular, -1.0 means opposite.
- Use it to test alignment, perpendicularity, or opposition between two directions.

## Don't
- Don't take the dot product of unnormalized vectors and read it as a cosine; the magnitude of the inputs changes the result.
- Don't expect an exact 0 or ±1; floating-point arithmetic is approximate, so compare against a tolerance.
- Don't use the dot product to get a distance; it measures angular relationship, not separation.

## Checklist
- Both vectors are normalized before the dot product.
- The result is read as the cosine of the angle (-1.0 to 1.0).
- 1.0 = aligned, 0 = perpendicular, -1.0 = opposite.

## Notes
The dot product of two normalized vectors equals the cosine of the angle between them, ranging from -1.0 (pointing opposite ways) through 0 (perpendicular) to 1.0 (pointing the same way). Use it to test whether two directions are aligned, perpendicular, or opposite. Normalize both vectors first so the result is a pure cosine, and compare against a tolerance rather than an exact value, since floating-point arithmetic is approximate.
