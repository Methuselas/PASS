---
object_id: PAT_gate_a_behavior_tree_node_with_a_blackboard_decorator
object_type: pattern
name: Gate a Behavior Tree Node with a Blackboard Decorator
library_path:
- software-engineering
- unreal-engine
- blueprints
- ai
stage_binding: 0 design
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- blueprints
- ai
- behavior_tree
- decorator
- blackboard
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: low
references: []
variants: []
---

# Gate a Behavior Tree Node with a Blackboard Decorator

## Pattern Rule
**IF** you want a Behavior Tree node to run only when a condition is met — for example, only while the AI has a reference to the player
**THEN** attach a Decorator to the node (such as a Blackboard decorator with an "Is Set" key query on the relevant key) so the node is allowed to run only while the condition holds, and set the decorator's "Observer aborts" to Lower Priority so that when the condition becomes true it aborts a lower-priority behavior and takes over.

## Do
- Attach the decorator to the top of the node it gates (Add Decorator on the node).
- Use a Blackboard decorator with a key query (Is Set) to gate on whether a reference or value is present.
- Set "Observer aborts" to Lower Priority so the gated behavior preempts whatever lower-priority behavior is running when the condition turns true.
- Give the decorator a clear Node Name (such as "Can see Player?") so the condition reads in the tree.

## Don't
- Don't put the condition inside the task when a decorator can gate the whole node — the decorator is the place for "may this run at all?"
- Don't leave "Observer aborts" unset when you want the new behavior to interrupt the current one; without it the gated behavior waits instead of taking over.
- Don't gate on a key that nothing writes; the condition will never be true and the node will never run.

## Checklist
- A decorator is attached to the node it gates.
- The decorator's key query matches the data the AI actually writes.
- "Observer aborts" is set so the gated behavior preempts lower-priority work when the condition turns true.
- The gated node runs only while the condition holds.

## Notes
A decorator is how you add a condition to a Behavior Tree node without changing the node itself. It attaches to the top of a node and decides whether the node may run. A Blackboard decorator with an "Is Set" query gates a behavior on whether a reference is present — here, whether the AI currently sees the player. Setting "Observer aborts" to Lower Priority is what makes the gated behavior (chase the player) interrupt the lower-priority behavior (patrol) the moment the player is seen, and drop back to patrol when the reference is cleared.
