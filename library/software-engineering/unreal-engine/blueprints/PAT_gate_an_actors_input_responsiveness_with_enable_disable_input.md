---
object_id: PAT_gate_an_actors_input_responsiveness_with_enable_disable_input
object_type: pattern
name: Gate an Actor's Input Responsiveness With Enable and Disable Input
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
- enable_disable
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Gate an Actor's Input Responsiveness With Enable and Disable Input

## Pattern Rule
**IF** an actor should respond to input events only under a condition (for example, only when the player is near it)
**THEN** use the Enable Input and Disable Input functions to gate the actor's input responsiveness.

## Do
- Call Enable Input when the condition becomes true (for example, when the player begins to overlap the actor).
- Call Disable Input when the condition becomes false (for example, when the player ends the overlap).
- Pass the reference to the Player Controller in use.

## Don't
- Don't leave an actor always input-responsive when it should only respond under a condition.

## Checklist
- Input is enabled when the condition becomes true and disabled when it becomes false.
- The nodes target the Player Controller in use.

## Notes
Enable Input and Disable Input are functions that define whether an actor responds to input events such as from a keyboard, mouse, or gamepad; they need a reference to the Player Controller class in use. Example: a Blueprint that enables input when the player begins to overlap it and disables it when the player ends the overlap, so the actor only receives input when the player is near.
