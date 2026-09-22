---
object_id: PAT_bridge_runtime_blueprint_data_into_niagara_with_user_parameters
object_type: pattern
name: Bridge Blueprint Data into Niagara with User Parameters
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

# Bridge Blueprint Data into Niagara with User Parameters

## Pattern Rule
**IF** Blueprint-owned data must control a Niagara System
**THEN** bind a typed USER parameter inside Niagara and set that parameter from the owning Blueprint using the matching Niagara variable setter.

## Do
- Create a User parameter with the correct type.
- Bind the Niagara module or property input to that User parameter.
- Use the corresponding typed Set Niagara Variable node from Blueprint.
- Use Construction Script when the value should update from per-instance Blueprint properties in Editor mode; use runtime graph logic when the value changes during play.

## Don't
- Do not reach into custom-module implementation details from Blueprint when a User parameter can be the interface.

## Checklist
- Changing the Blueprint value changes the bound Niagara behavior.

## Notes
User Parameters are the same typed transport boundary in both runtime and editor-time Blueprint control; the update context determines whether the setter belongs in gameplay logic or Construction Script.
