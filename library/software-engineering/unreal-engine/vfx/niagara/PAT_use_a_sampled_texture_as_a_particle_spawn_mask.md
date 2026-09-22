---
object_id: PAT_use_a_sampled_texture_as_a_particle_spawn_mask
object_type: pattern
name: Use a Sampled Texture as a Particle Spawn Mask
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

# Use a Sampled Texture as a Particle Spawn Mask

## Pattern Rule
**IF** particle presence should follow an arbitrary image-shaped mask
**THEN** sample the texture at each particle's mapped UV and conditionally remove particles outside the desired mask region.

## Do
- Convert the sampled color into the scalar/condition needed by the mask.
- Drive a particle-kill condition from that comparison.
- Verify the surviving particles reproduce the intended image silhouette.

## Don't
- Do not hard-code emitter geometry when a texture mask is the intended shape control.

## Checklist
- The particle silhouette follows the sampled texture mask.

## Notes
A black-and-white mask can be implemented by sampling color, deriving a comparison value, and driving Kill Particles from that condition.
