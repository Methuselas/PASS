---
object_id: PAT_use_local_niagara_modules_for_one_off_or_prototype_behavior
object_type: pattern
name: Use Local Niagara Modules for One-Off or Prototype Behavior
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

# Use Local Niagara Modules for One-Off or Prototype Behavior

## Pattern Rule
**IF** custom Niagara graph logic is specific to one system or still being explored
**THEN** use a Local/Scratch module before promoting it to a reusable Module Script asset.

## Do
- Prototype effect-specific logic as a Local Module.
- Promote or copy it into a reusable custom module when the behavior becomes shared.

## Don't
- Do not create a global reusable asset for every experimental graph.
- Do not leave broadly reused logic embedded separately in many systems.

## Checklist
- The chosen module scope matches expected reuse.

## Notes
Local Modules live with one particle system and are useful for fast iteration.
