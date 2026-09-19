---
object_id: PAT_choose_action_or_axis_mapping_by_input_shape
object_type: pattern
name: Choose Action or Axis Mapping by the Input's Shape
library_path:
- software-engineering
- unreal-engine
- blueprints
stage_binding: 0 design
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- blueprints
- input
- mappings
cross_links:
- rel: related_to
  target_object_id: PAT_put_player_input_in_the_player_controller
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Choose Action or Axis Mapping by the Input's Shape

## Pattern Rule
**IF** you are adding a new player input to a game and must decide how to map it
**THEN** map discrete on/off triggers (a key press or release, a mouse click) as Action Mappings and continuous ranged inputs (an analog stick, or keys on opposite ends of a range) as Axis Mappings, because the two mapping kinds carry different data — an Action fires on press and release, an Axis carries a value across a range.

## Do
- Add the mapping in Project Settings under Engine → Input → Bindings, in the Action Mappings or Axis Mappings section.
- Map a hold-to-modify input (sprint, zoom) as an Action Mapping so the input exposes Pressed and Released events.
- Map a movement input that has a range (forward/backward, left/right) as an Axis Mapping so the input carries a value from one end of the range to the other, with the opposite direction represented as a negative value.

## Don't
- Don't map a continuous input as an Action — you lose the range and are left with only on/off.
- Don't map a discrete trigger as an Axis — you get a value you then have to threshold back into on/off.
- Don't pick the mapping kind by habit; pick it from the shape of the input.

## Checklist
- Each new input is mapped as the kind that matches its shape: discrete trigger → Action, ranged value → Axis.
- A hold-to-modify input exposes Pressed and Released events.
- A movement input carries a value across a range, with the opposite direction as a negative value.

## Notes
Action Mappings are keypress and mouse click events that trigger player Actions; they fire on press and release. Axis Mappings map player movements and events that have a range, such as two keys affecting the same action on opposite ends of the range. The mappings insert a layer of indirection between the input behavior and the physical keys that invoke it, so the behavior is bound to the mapping name rather than to a key. The choice between the two kinds is driven by the shape of the input — whether it is a discrete trigger or a continuous value — not by which mapping is familiar.
