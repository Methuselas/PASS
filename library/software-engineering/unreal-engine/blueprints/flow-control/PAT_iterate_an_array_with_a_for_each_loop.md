---
object_id: PAT_iterate_an_array_with_a_for_each_loop
object_type: pattern
name: Iterate an Array with a For Each Loop
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
- arrays
- iteration
cross_links:
- rel: related_to
  target_object_id: PAT_guard_array_index_access_against_out_of_range
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Iterate an Array with a For Each Loop

## Pattern Rule
**IF** an action should run once for each element of an array — turn on every lamp in a list, apply an effect to every actor in a collection
**THEN** wire the array to a For Each Loop node and connect the per-element action to its Loop Body pin, so the node runs the action once per element.

## Do
- Wire the array to the For Each Loop's Array input.
- Connect the per-element action to the Loop Body output pin.
- Use the Array Element output to reach the current element and the Array Index output when the action needs the element's position.
- Connect the actions that should run after the whole loop to the Completed pin.

## Don't
- Don't hand-roll an index loop with a counter and an index guard when a For Each Loop will do — the node handles the iteration and the completion for you.
- Don't put post-loop actions in the loop body — the body runs once per element, and the Completed pin is the only place that runs after the last element.

## Checklist
- The per-element action runs once for each element of the array.
- The Array Element output is used to reach the current element.
- The post-loop actions are on the Completed pin, not in the loop body.

## Notes
A For Each Loop is the node for running an action over every element of an array. It exposes the current element and its index on each iteration and a Completed pin that fires once the last element is done. It replaces a hand-rolled index loop and its out-of-range guard for the common case of "do this to every element."
