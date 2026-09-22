---
object_id: PAT_shape_niagara_particle_emission_with_shape_location
object_type: pattern
name: Shape Niagara Particle Emission with Shape Location
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

# Shape Niagara Particle Emission with Shape Location

## Pattern Rule
**IF** particles should originate from a specific primitive region
**THEN** configure the Shape Location module to match that intended spawn geometry.

## Do
- Choose a Shape Primitive that matches the desired emission region.
- Tune the shape dimensions independently of downstream particle behavior.

## Don't
- Do not rebuild motion or rendering logic merely to change where particles originate.

## Checklist
- Particles originate from the intended spatial region.

## Notes
The book demonstrates changing a Fountain emitter from Sphere to Torus while keeping later behavior intact.
