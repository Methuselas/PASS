---
object_id: PAT_normalize_a_vector_when_you_need_direction_only
object_type: pattern
name: Normalize a Vector When You Need Direction Only
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
- normalization
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Normalize a Vector When You Need Direction Only

## Pattern Rule
**IF** you need a direction without a specific magnitude — a movement direction, an aim direction, a surface normal
**THEN** normalize the vector to get a unit vector (length 1), which preserves the direction and removes the magnitude, then scale it if you need to apply a specific distance.

## Do
- Use the Normalize node to turn a vector into a unit vector (length 1).
- Use normalized vectors for direction-only purposes: movement direction, aim direction, surface normal.
- Scale the unit vector by a scalar to apply a specific magnitude in that direction.

## Don't
- Don't feed an unnormalized vector where a pure direction is expected; its magnitude will leak into the result.
- Don't normalize a zero vector; it has no direction and the result is undefined.
- Don't normalize when you actually need the original magnitude; normalization discards it.

## Checklist
- The vector is normalized to length 1 where a pure direction is needed.
- The direction is preserved and the magnitude removed.
- A specific magnitude is applied by scaling the unit vector.

## Notes
Normalizing a vector produces a unit vector (length 1) that keeps the direction and drops the magnitude. Use it whenever you need a direction without a specific size — a movement direction, an aim direction, or a surface normal. To move a specific distance in that direction, scale the unit vector by the distance. A zero vector has no direction, so normalizing it is undefined.
