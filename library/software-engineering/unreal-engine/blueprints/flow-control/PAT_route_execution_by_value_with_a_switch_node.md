---
object_id: PAT_route_execution_by_value_with_a_switch_node
object_type: pattern
name: Route Execution by Value with a Switch Node
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
- branching
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Route Execution by Value with a Switch Node

## Pattern Rule
**IF** execution should branch on the value of a variable — an integer rank, a command string, an enumeration — rather than on a single Boolean
**THEN** use a Switch node of the matching type (Switch on Int, Switch on String, or Switch on Enum), wire the variable to the Selection input, connect each value's actions to its own output pin, and connect the actions for any value without a pin to the Default pin.

## Do
- Add an output pin for each value that needs its own actions: Add pin + for Switch on Int, the Pin Options | Pin Names list for Switch on String, and the enumeration's values for Switch on Enum.
- Wire the variable to the Selection input.
- Connect each value's actions to its output pin.
- Connect the actions for any value without a dedicated pin to the Default pin, so an unmatched value still has a path.

## Don't
- Don't chain a Branch per value — a Switch routes on the value in one node, while a chain of Branches tests one value at a time and grows with the number of values.
- Don't leave the Default pin unwired when unmatched values are possible — the execution path dies for any value without a pin.
- Don't use Switch on Enum for a value set that is not an enumeration — its pins come from the enumeration's values, so a non-enumeration set has no pins to route to.

## Checklist
- The variable is wired to the Selection input of a Switch node whose type matches the variable.
- Each value that needs its own actions has an output pin with those actions connected.
- The Default pin is wired for any value without a dedicated pin.

## Notes
A Switch routes execution on the value of a single variable, which is the natural shape for dispatching on a rank, a command, or a named state. The Default pin is the fallback for values without a dedicated pin, so the graph stays complete even when the value set is open-ended. A Boolean condition is a Branch's job; a Switch is for value-based dispatch.
