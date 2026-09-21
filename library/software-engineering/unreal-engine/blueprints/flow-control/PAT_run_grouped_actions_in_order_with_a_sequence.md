---
object_id: PAT_run_grouped_actions_in_order_with_a_sequence
object_type: pattern
name: Run Grouped Actions in Order with a Sequence
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
- ordering
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Run Grouped Actions in Order with a Sequence

## Pattern Rule
**IF** one execution trigger should dispatch several follow-up execution paths in a fixed order
**THEN** wire the trigger to a Sequence node and connect each path to its own output pin, so the Sequence fires those output paths from Then 0 onward in pin order.

## Do
- Connect the first group's actions to the first output pin (Then 0), the second group's to the next pin, and so on.
- Add more output pins with Add pin + when a group needs its own pin.

## Don't
- Don't treat Sequence as a completion barrier for latent or asynchronous work — it orders execution dispatch, not the eventual completion of delayed work started by an earlier pin.
- Don't use pin order when correctness requires waiting for an earlier latent/asynchronous operation to finish; use that operation's completion signal or a state/event handoff instead.

## Checklist
- The output execution paths are dispatched in pin order.
- Any dependency on actual completion of latent/asynchronous work is handled separately rather than inferred from Sequence ordering.

## Notes
A Sequence organizes several execution paths under one trigger and dispatches its output pins in a fixed order. For ordinary immediate Blueprint nodes this often looks like “do this, then that,” but latent or asynchronous work can still be running after the Sequence has advanced to a later pin. Use completion events/state when later logic must wait for that work to finish.
