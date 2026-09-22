---
object_id: PAT_use_niagara_for_new_unreal_particle_effects
object_type: pattern
name: Use Niagara for New Unreal Particle Effects
library_path:
- software-engineering
- unreal-engine
- vfx
- niagara
stage_binding: 0 design
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- niagara
- cascade
- vfx
cross_links: []
reference:
  source_title: Build Stunning Real-time VFX with Unreal Engine 5
  author: Hrishikesh Andurlekar
confidence: high
references: []
variants: []
---

# Use Niagara for New Unreal Particle Effects

## Pattern Rule
**IF** you are creating a new particle effect in Unreal Engine 5 rather than maintaining an older project
**THEN** use Niagara as the primary particle system and treat Cascade as a legacy compatibility tool.

## Do
- Create new particle effects as Niagara Systems or Niagara Emitters.
- Open Cascade when an older asset or project already depends on it.
- Keep Cascade knowledge available for maintenance and migration work.

## Don't
- Don't choose Cascade for new UE5 particle work merely because an old project or Marketplace asset uses it.
- Don't assume Cascade has disappeared; legacy projects may still require it.

## Checklist
- New effects are authored in Niagara.
- Cascade is used only where legacy compatibility or maintenance requires it.

## Notes
UE5 keeps Cascade for compatibility, while Niagara is the primary particle-effects workflow for new work.
