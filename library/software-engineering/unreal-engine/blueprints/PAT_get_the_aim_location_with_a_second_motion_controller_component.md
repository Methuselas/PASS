---
object_id: PAT_get_the_aim_location_with_a_second_motion_controller_component
object_type: pattern
name: Get the Aim Location with a Second Motion Controller Component
library_path:
- software-engineering
- unreal-engine
- blueprints
stage_binding: 1 skeleton
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- blueprints
- vr
- motion_controller
- aim
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Get the Aim Location with a Second Motion Controller Component

## Pattern Rule
**IF** you need the aim location of a motion controller rather than its grip location
**THEN** add a second Motion Controller component whose Motion Source is set to the aim, and uncheck its Display Device Model so it is not shown in the level.

## Do
- Add an extra Motion Controller component for each hand whose aim you need.
- Set its Motion Source in the Details panel to the aim (for example, RightAim or LeftAim) instead of the default grip.
- Uncheck Display Device Model so the extra component does not render a device model in the level.
- Read the aim location and forward vector from this component.

## Don't
- Don't read the aim from the grip component — by default a Motion Controller component reports the grip location, not the aim.
- Don't leave Display Device Model checked on the aim component — it will draw a second controller model in the level.

## Checklist
- The aim component's Motion Source is set to the aim, not the grip.
- The aim component's Display Device Model is unchecked.
- Aim-dependent logic (such as a teleport trace direction) reads from the aim component.

## Notes
A Motion Controller component tracks a physical controller and, by default, reports its grip location. When logic needs where the controller is pointing (its aim) rather than where it is gripped, the simple approach is a second Motion Controller component with its Motion Source switched to the aim. Because it is only a data source, its Display Device Model is turned off so it does not add a visible model to the level. Example: a VR teleport trace starts at the right aim component's world location and points along its forward vector.
