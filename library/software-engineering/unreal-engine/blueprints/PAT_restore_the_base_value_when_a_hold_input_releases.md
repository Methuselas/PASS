---
object_id: PAT_restore_the_base_value_when_a_hold_input_releases
object_type: pattern
name: Restore the Base Value When a Hold Input Releases
library_path:
- software-engineering
- unreal-engine
- blueprints
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- blueprints
- input
- hold_to_modify
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Restore the Base Value When a Hold Input Releases

## Pattern Rule
**IF** an input temporarily modifies a value while it is held — sprint raises the walk speed, zoom narrows the field of view
**THEN** wire both the Pressed and Released events of the input: Pressed sets the modified value, Released restores the base value, so the modification does not persist after the input is released.

## Do
- On Pressed, set the value to the modified amount (for example, the sprint walk speed on the Character Movement component).
- On Released, set the value back to the base amount (the component's default walk speed), not to zero or to some other value.
- Keep the base value as the component's default so the restore returns to the intended resting state.

## Don't
- Don't wire only the Pressed event and let the modified value persist — the player sprints forever, or the camera stays zoomed, after the key is released.
- Don't restore to a value you made up; restore to the base value the component started with.
- Don't treat the Released event as optional — it is what makes the modification temporary.

## Checklist
- Releasing the input returns the value to its base state.
- Both the Pressed and Released events are wired, each to a setter.
- The Released setter's value is the base value, not the modified one.

## Notes
A hold-to-modify input is a pair: the press applies the modification and the release removes it. Wiring only the press leaves the modification in place — the player sprints forever, or the camera stays zoomed, after the key is released. The restore on release is what makes the modification temporary rather than permanent.
