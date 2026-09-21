---
object_id: PAT_limit_an_action_to_n_executions_with_do_n
object_type: pattern
name: Limit an Action to N Executions with Do N
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
- counting
cross_links:
- rel: related_to
  target_object_id: PAT_model_a_multi_hit_destruction_as_a_decrementing_counter
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Limit an Action to N Executions with Do N

## Pattern Rule
**IF** an action should run a fixed number of times and then stop until it is explicitly reset — a special weapon fires three shots, then needs a reload
**THEN** wire the trigger to a Do N node, set its N input to the allowed count, and connect the action to its output pin, so the action runs for the first N triggers and is ignored until the Reset pin fires.

## Do
- Wire the trigger event to the Do N's Enter input.
- Set the N input to the number of times the action may run.
- Connect the action to the Do N's output pin.
- Wire the reset condition (such as a reload input) to the Do N's Reset pin, so the action can run another N times after the reset.

## Don't
- Don't use a Do N for an action that should run exactly once — a Do Once is the simpler node for a single execution.
- Don't forget to wire the Reset pin — without it, the action runs N times total and never again.
- Don't hand-roll a decrementing counter and a Branch when a Do N will do — the node keeps the count and the lock for you.

## Checklist
- The action runs for the first N triggers and not on the N+1th.
- Firing the Reset pin allows the action to run another N times.
- The reset is driven by the intended condition (such as a reload), not by a manual re-trigger.

## Notes
A Do N is the counted gate for an action that may run a fixed number of times before it locks. It is the general form of a Do Once (which is the count-of-one case), and it replaces a hand-rolled decrementing counter and a Branch for the common "fire N times, then reload" shape. The Reset pin re-arms the count, so wire it to the condition that should allow the next batch of executions.
