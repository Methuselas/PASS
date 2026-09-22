---
object_id: PAT_compose_niagara_systems_from_reusable_emitters
object_type: pattern
name: Compose Niagara Systems from Reusable Emitters
library_path:
- software-engineering
- unreal-engine
- vfx
- niagara
stage_binding: 1 skeleton
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

# Compose Niagara Systems from Reusable Emitters

## Pattern Rule
**IF** an effect is naturally made of distinct particle behaviors that may be reused or edited independently
**THEN** build those behaviors as separate Niagara Emitters and reference one or more of them from a Niagara System.

## Do
- Give each emitter one coherent particle role, such as flame, ember, or smoke.
- Combine emitters at the System level to create the full effect.
- Edit the reusable emitter independently when the shared behavior changes.

## Don't
- Don't collapse unrelated particle roles into one emitter merely because they appear in the same effect.
- Don't duplicate an emitter when the same reusable behavior can be referenced.

## Checklist
- Each emitter has a clear role.
- The Niagara System composes the required emitters into one effect.

## Notes
A Niagara Emitter is not directly placeable in a level; package the emitter inside a Niagara System, which is the level-placeable composition surface.

Niagara emitters and systems are independent assets; a System can reference multiple emitters.
