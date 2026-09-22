---
object_id: PAT_drive_niagara_module_parameters_with_dynamic_inputs
object_type: pattern
name: Drive Niagara Module Parameters with Dynamic Inputs
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

# Drive Niagara Module Parameters with Dynamic Inputs

## Pattern Rule
**IF** a Niagara module parameter should be computed, varied, or randomized instead of remaining constant
**THEN** replace the local value with an appropriate Dynamic Input.

## Do
- Choose a Dynamic Input compatible with the parameter type.
- Tune its inputs and observe the resulting effect in Preview.

## Don't
- Do not create a custom module when a supported Dynamic Input cleanly expresses the required parameter logic.

## Checklist
- The parameter responds to the intended function or randomization.

## Notes
Dynamic Inputs are a parameter-level extension point between constants and custom module graphs.
