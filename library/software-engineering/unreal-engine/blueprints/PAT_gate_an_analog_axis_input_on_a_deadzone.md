---
object_id: PAT_gate_an_analog_axis_input_on_a_deadzone
object_type: pattern
name: Gate an Analog Axis Input on a Deadzone
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
- input
- axis
- deadzone
cross_links:
- rel: related_to
  target_object_id: PAT_choose_action_or_axis_mapping_by_input_shape
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Gate an Analog Axis Input on a Deadzone

## Pattern Rule
**IF** you are acting on an analog axis input (such as a thumbstick)
**THEN** gate the action on the axis value being in the intended direction and greater than the deadzone before you act.

## Do
- Check that the axis value has the sign of the intended direction (for example, positive for "up").
- Check that the axis value is greater than the deadzone, the minimum value that should start the action.
- Run the action only when both checks pass (combine them with an AND into a single Branch condition).

## Don't
- Don't act on the raw axis value — small residual values from a centered stick will trigger the action when the player did not intend it.
- Don't use a single threshold without a direction check — the opposite direction of the stick would also pass a magnitude-only test.

## Checklist
- The action fires only when the axis value is past the deadzone in the intended direction.
- A centered or barely-moved stick does not trigger the action.
- The direction check and the deadzone check are both present before the action.

## Notes
Analog axis inputs never read exactly zero when centered; they drift around a small residual. The deadzone is the minimum axis value that counts as intentional input. Gating on both the sign (direction) and the deadzone (magnitude) keeps a centered stick from firing the action while still responding to a deliberate push. Example: a VR teleport starts only when the right thumbstick is pushed up past the deadzone, and ends when it is released.
