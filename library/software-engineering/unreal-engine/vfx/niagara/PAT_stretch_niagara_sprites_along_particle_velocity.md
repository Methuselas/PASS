---
object_id: PAT_stretch_niagara_sprites_along_particle_velocity
object_type: pattern
name: Stretch Niagara Sprites along Particle Velocity
library_path:
- software-engineering
- unreal-engine
- vfx
- niagara
stage_binding: 3 rough
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

# Stretch Niagara Sprites along Particle Velocity

## Pattern Rule
**IF** sprite particles should read as directional streaks
**THEN** use non-uniform sprite dimensions and set the Sprite Renderer alignment to Velocity Aligned.

## Do
- Give sprites an elongated axis.
- Set Sprite Renderer Alignment to Velocity Aligned.

## Don't
- Do not expect elongated dimensions alone to orient sprites along motion.

## Checklist
- Streaks rotate to follow particle velocity.

## Notes
The FireSparks example shows the two settings are jointly required.
