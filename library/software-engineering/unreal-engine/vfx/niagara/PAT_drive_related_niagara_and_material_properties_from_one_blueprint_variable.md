---
object_id: PAT_drive_related_niagara_and_material_properties_from_one_blueprint_variable
object_type: pattern
name: Drive Related Niagara and Material Properties from One Blueprint Variable
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

# Drive Related Niagara and Material Properties from One Blueprint Variable

## Pattern Rule
**IF** one conceptual VFX control must keep Niagara and supporting material state synchronized
**THEN** expose one Blueprint variable and fan it out to each underlying parameter that represents that concept.

## Do
- Use one public texture variable to drive both Niagara mask input and display material texture when they must match.
- Use one public color variable to drive both particle and supporting-material color when they represent one creative control.

## Don't
- Do not expose separate public values that allow coupled visual layers to drift unintentionally.

## Checklist
- Changing the one public control updates every intended implementation target.

## Notes
The Blueprint becomes the authoritative coordination layer for the wrapped effect.
