---
object_id: PAT_combine_particle_forces_with_vector_arithmetic
object_type: pattern
name: Combine Particle Forces with Vector Arithmetic
library_path:
- software-engineering
- unreal-engine
- vfx
- niagara
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- niagara
- vfx
cross_links: []
reference:
  source_title: Build Stunning Real-time VFX with Unreal Engine 5
  author: Hrishikesh Andurlekar
confidence: high
references: []
variants: []
---

# Combine Particle Forces with Vector Arithmetic

## Pattern Rule
**IF** several directional influences contribute to a particle result
**THEN** combine their vector components with the required addition, subtraction, or scalar multiplication to produce the resultant vector.

## Do
- Add vectors component-wise when influences combine.
- Subtract a vector when one influence opposes another.
- Scale a direction vector by a scalar when you need the same direction with a different magnitude.

## Don't
- Don't add scalar magnitudes when the directions of the forces matter.
- Don't normalize away magnitude unless the operation needs direction only.

## Checklist
- The resultant vector reflects both direction and magnitude of the contributing values.
- The Niagara arithmetic nodes use compatible vector/scalar types.

## Notes
Particle motion is often the result of multiple vector quantities acting together.
