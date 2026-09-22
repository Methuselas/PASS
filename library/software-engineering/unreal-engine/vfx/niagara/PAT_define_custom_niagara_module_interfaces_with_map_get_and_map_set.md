---
object_id: PAT_define_custom_niagara_module_interfaces_with_map_get_and_map_set
object_type: pattern
name: Define Custom Niagara Module Interfaces with Map Get and Map Set
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

# Define Custom Niagara Module Interfaces with Map Get and Map Set

## Pattern Rule
**IF** a custom Niagara module needs to read inputs and write particle or system attributes
**THEN** read the required values through the parameter map and write the module result back through Map Set.

## Do
- Expose tunable Module Inputs through Map Get.
- Perform the graph calculation between the parameter-map nodes.
- Write only the intended output attributes through Map Set.

## Don't
- Do not hide required inputs as unexplained graph constants.

## Checklist
- Exposed inputs appear on the consuming module instance.
- Written attributes change the intended Niagara state.

## Notes
The book demonstrates SizeOfParticle feeding PARTICLES.SpriteSize.
