---
object_id: PAT_transform_niagara_particle_positions_to_world_space_before_world_space_comparisons
object_type: pattern
name: Transform Niagara Particle Positions to World Space before World-Space Comparisons
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

# Transform Niagara Particle Positions to World Space before World-Space Comparisons

## Pattern Rule
**IF** particle positions must be compared with a value expressed in world space
**THEN** transform the particle position into world space before subtraction, distance, or proximity calculations.

## Do
- Identify the coordinate space of every position used in the calculation.
- Use owner transform data to convert local particle positions before comparing with world-space gameplay positions.

## Don't
- Do not subtract positions expressed in different coordinate spaces.

## Checklist
- Both operands of the spatial comparison use the same coordinate space.

## Notes
The Presence Detector compares particles with a Blueprint-provided player world position.
