---
object_id: PAT_alternate_between_two_actions_with_a_flip_flop
object_type: pattern
name: Alternate Between Two Actions with a Flip Flop
library_path:
- software-engineering
- unreal-engine
- blueprints
- flow-control
stage_binding: 1 skeleton
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- blueprints
- flow_control
- state
cross_links:
- rel: related_to
  target_object_id: PAT_model_a_two_stage_interaction_as_a_boolean_state_and_branch
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Alternate Between Two Actions with a Flip Flop

## Pattern Rule
**IF** two actions should alternate on each trigger — the first trigger runs action A, the second runs action B, the third runs A again
**THEN** wire the trigger to a Flip Flop node and connect action A to its A pin and action B to its B pin, so each execution toggles to the other action.

## Do
- Read the Is A output when you need to know which pin just ran: True means A ran, False means B ran.
- Connect the first action to the A pin and the second action to the B pin.

## Don't
- Don't put a Flip Flop inside a function — the node keeps its toggle state in an internal variable that is deleted when the function ends, so the A pin runs every time the function is called and the alternation never happens.
- Don't use a Flip Flop for a one-way two-stage transition (first occurrence versus later) — it toggles back and forth, so it cannot model a state that advances once and stays.

## Checklist
- The first trigger runs the A action and the second trigger runs the B action.
- The Flip Flop sits in the event graph, not inside a function.
- Each trigger toggles to the other action.

## Notes
A Flip Flop is the small toggle for two actions that should take turns on each trigger, such as firing a left and a right pistol alternately. Its state lives in an internal variable, so it only persists in the event graph; inside a function the variable is deleted at the end of the call and the node always takes the A pin. For a one-way two-stage transition, a Boolean state and a Branch model it correctly; a Flip Flop is for back-and-forth alternation.
