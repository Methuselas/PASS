---
object_id: PAT_visualize_hidden_niagara_module_behavior_with_debug_drawing
object_type: pattern
name: Visualize Hidden Niagara Module Behavior with Debug Drawing
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

# Visualize Hidden Niagara Module Behavior with Debug Drawing

## Pattern Rule
**IF** particle output alone does not explain what a spatial Niagara module is calculating
**THEN** enable supported Debug Drawing to visualize hidden rays, directions, or forces.

## Do
- Turn on Debug Drawing for supported modules.
- Compare the debug geometry with the visible particle response.

## Don't
- Do not infer an invisible force or query solely from the final sprites when the module can draw its internal behavior.

## Checklist
- The diagnostic drawing corresponds to the module's expected spatial calculation.

## Notes
Examples include collision rays and Vortex Force vectors.
