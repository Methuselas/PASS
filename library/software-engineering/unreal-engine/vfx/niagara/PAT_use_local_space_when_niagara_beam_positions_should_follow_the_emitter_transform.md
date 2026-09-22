---
object_id: PAT_use_local_space_when_niagara_beam_positions_should_follow_the_emitter_transform
object_type: pattern
name: Use Local Space When Niagara Beam Positions Should Follow the Emitter Transform
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

# Use Local Space When Niagara Beam Positions Should Follow the Emitter Transform

## Pattern Rule
**IF** beam positions are authored relative to the emitter and should move with that emitter
**THEN** enable Local Space so the beam endpoints transform with the Niagara emitter.

## Do
- Enable Local Space for beam geometry that should remain emitter-relative.
- Move the system in the level to verify both endpoints follow it.

## Don't
- Do not leave emitter-relative beam positions interpreted as world-space positions.

## Checklist
- Moving the Niagara System preserves the beam shape relative to the emitter.

## Notes
The lightning example otherwise leaves its beam end tied to a world-space location.
