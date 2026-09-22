---
object_id: PAT_reset_niagara_parameters_to_the_intended_default_layer
object_type: pattern
name: Reset Niagara Parameters to the Intended Default Layer
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

# Reset Niagara Parameters to the Intended Default Layer

## Pattern Rule
**IF** a System-level Niagara parameter override needs to be reset
**THEN** choose whether to restore the inherited Emitter default or the Module default according to which layer you intend to preserve.

## Do
- Use the emitter-default reset when discarding only System tuning.
- Use the module-default reset when returning to the module built-in baseline.

## Don't
- Do not treat all reset arrows as equivalent.

## Checklist
- The parameter value matches the intended inheritance layer after reset.

## Notes
Niagara exposes distinct reset targets for module and emitter defaults.
