---
object_id: PAT_use_color_mode_for_common_particle_color_randomization
object_type: pattern
name: Use Color Mode for Common Particle Color Randomization
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

# Use Color Mode for Common Particle Color Randomization

## Pattern Rule
**IF** the goal is common spawn-time color randomization
**THEN** prefer Initialize Particle Color Mode options when they express the variation directly.

## Do
- Use Random Range for a bounded pair of colors.
- Use Random Hue/Saturation/Value for broad color variation when appropriate.

## Don't
- Do not build a cumbersome Dynamic Input chain for a behavior already supported directly by Color Mode.

## Checklist
- Particles receive the intended spawn-time color variation.

## Notes
The chapter contrasts a working chained-input solution with the simpler built-in Color Mode.
