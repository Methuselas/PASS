---
object_id: PAT_cycle_through_options_with_a_multigate
object_type: pattern
name: Cycle Through Options with a MultiGate
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
- cycling
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Cycle Through Options with a MultiGate

## Pattern Rule
**IF** each trigger should select the next option from a fixed set in turn — set a different mesh on each press, advance through a list of states
**THEN** wire the trigger to a MultiGate node, connect each option's action to its own output pin, and set the Loop input to True so the node returns to the first pin after the last one.

## Do
- Connect each option's action to its own output pin (Out 0, Out 1, and so on), adding pins with Add pin +.
- Set the Loop input to True when the options should cycle back to the first after the last.
- Set the Start Index input to the first output pin to execute when the default start is not the first pin.
- Set the Is Random input to True when the options should be chosen in a random order rather than in turn.

## Don't
- Don't leave Loop unset when the options should cycle — with Loop False the node stops after the last pin and later triggers do nothing.
- Don't use a MultiGate for value-based dispatch — it advances through its pins in order (or randomly), so it cannot route to a specific pin based on a variable's value; a Switch is the right node for that.
- Don't rely on the node remembering a position across a Reset — firing the Reset pin returns it to the start, so wire Reset only when a restart of the cycle is intended.

## Checklist
- Each trigger executes the next output pin in turn.
- With Loop set, the node returns to the first pin after the last one.
- The options' actions are each connected to their own output pin.

## Notes
A MultiGate is the node for stepping through a fixed set of options in turn, one per trigger. Its Loop input makes the cycle wrap from the last pin back to the first, its Start Index chooses where the cycle begins, and its Is Random input shuffles the order. It is the "advance to the next option" shape — distinct from a Switch, which routes to a pin chosen by a value, and from a Gate, which opens and closes a single path.
