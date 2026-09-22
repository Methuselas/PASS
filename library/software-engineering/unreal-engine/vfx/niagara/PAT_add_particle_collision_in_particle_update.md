---
object_id: PAT_add_particle_collision_in_particle_update
object_type: pattern
name: Add Particle Collision in Particle Update
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

# Add Particle Collision in Particle Update

## Pattern Rule
**IF** spawned particles should react to scene geometry during their lifetime
**THEN** add Collision in Particle Update and verify the response against known geometry.

## Do
- Add the Collision module to Particle Update.
- Use visible test geometry or the preview floor to verify contact behavior.

## Don't
- Do not place lifetime collision in a spawn-only scope.

## Checklist
- Particles visibly respond when they reach the test surface.

## Notes
Collision mode/settings can be specialized later for CPU/GPU and accuracy requirements.
