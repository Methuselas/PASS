---
object_id: PAT_place_no_nodes_after_destroy_actor_self
object_type: pattern
name: Place No Nodes After a Self-Targeting DestroyActor
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
- execution_order
- destroy
- actor
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Place No Nodes After a Self-Targeting DestroyActor

## Pattern Rule
**IF** an execution chain ends by destroying the actor that owns it (a DestroyActor node whose Target is self)
**THEN** place every node that must still run before the DestroyActor, because the destroy removes the instance from the level and nothing after it in the chain executes.

## Do
- Order the chain so all remaining logic — updating a counter, playing an effect, notifying other objects — runs before the DestroyActor.
- When inserting new logic into a chain that already ends in a self-destroy, break the link into the DestroyActor and place the new nodes before it, keeping the DestroyActor last.

## Don't
- Don't wire any node after a self-targeting DestroyActor expecting it to run — the instance is gone and the chain stops.
- Don't assume a DestroyActor aimed at another actor is terminal for this chain — only a self-destroy removes the executing instance.

## Checklist
- The self-targeting DestroyActor is the final node in its execution chain.
- Every node that must run (counters, effects, notifications) is wired before it.
- No node depends on executing after the self-destroy.

## Notes
A DestroyActor node whose Target is self removes the current instance from the level, so the execution chain stops there — any node wired after it never runs. This is why a counter that must increment when a target is destroyed is wired before the destroy, not after: the target's Event Hit chain runs the increment and then destroys the target last. A DestroyActor aimed at a different actor does not remove the executing instance, so nodes after it still run; the terminal constraint applies only to the self-destroy.
