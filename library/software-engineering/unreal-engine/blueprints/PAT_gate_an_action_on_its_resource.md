---
object_id: PAT_gate_an_action_on_its_resource
object_type: pattern
name: Gate an Action on Its Resource
library_path:
- software-engineering
- unreal-engine
- blueprints
stage_binding: 1 skeleton
lane_fit: both
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- unreal_engine
- blueprints
- resources
- constraints
cross_links:
- rel: related_to
  target_object_id: PAT_store_meter_values_as_a_normalized_fraction
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Gate an Action on Its Resource

## Pattern Rule
**IF** an action consumes a limited resource — firing spends ammo, sprinting spends stamina
**THEN** put a Branch on the resource check at the action's entry, and run the action only on the branch where the resource is available, so the action cannot run past the resource's limit.

## Do
- Wire the input event to a Branch whose condition tests the resource (ammo greater than zero, stamina at least the cost).
- Run the action's body only on the True branch, where the resource is available.
- Let the False branch do nothing, so the action is silently refused when the resource is exhausted.

## Don't
- Don't run the action first and check the resource afterward — the action has already happened by the time the check fails.
- Don't let the action run when the resource is at zero; the gate is what enforces the limit.

## Checklist
- The action's entry branches on the resource being available.
- The action body runs only on the available branch.
- When the resource is exhausted, the input is accepted but the action does not run.

## Notes
A limited resource is enforced by a gate at the action's entry, not by a check after the fact. Wire the input event to a Branch that tests the resource — ammo greater than zero, stamina at least the sprint cost — and run the action only on the branch where the resource is available. When the resource is exhausted, the input still fires but the action is refused, which is exactly the constraint the resource is meant to provide.
