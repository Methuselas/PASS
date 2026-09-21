---
object_id: PAT_make_an_action_one_shot_with_do_once
object_type: pattern
name: Make an Action One-Shot with Do Once
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
- one_shot
cross_links:
- rel: related_to
  target_object_id: PAT_make_starting_a_timer_idempotent
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Make an Action One-Shot with Do Once

## Pattern Rule
**IF** an action should run at most once until it is explicitly reset — a charged weapon fires once, then needs a cooldown before it can fire again
**THEN** wire the trigger to a Do Once node and connect the action to its output pin, so the action runs on the first trigger and is ignored on every later trigger until the Reset pin fires.

## Do
- Wire the reset condition (such as a timer that expires after the cooldown) to the Do Once's Reset pin, so the action can run again after the reset.
- Connect the one-shot action to the Do Once's output pin.

## Don't
- Don't rely on the trigger firing only once — a held or re-pressed input re-enters the trigger, and only the Do Once's internal state blocks the re-run.
- Don't forget to wire the Reset pin — without it, the action runs exactly once for the life of the Blueprint and never again.
- Don't use a Do Once for an action that should run a fixed number of times greater than one — it locks after the first run; a counted gate is the right node for that.

## Checklist
- The first trigger runs the action and later triggers do not.
- Firing the Reset pin allows the action to run again.
- The reset is driven by the intended condition (such as a cooldown timer), not by a manual re-trigger.

## Notes
A Do Once is the node for an action that should happen exactly once and then stay locked until something explicitly resets it. Its internal state blocks re-triggers, which is what makes a charged weapon or a one-time trigger safe against a held or re-pressed input. The Reset pin is what re-arms it, so wire the reset to the condition that should allow the next run, such as a cooldown timer expiring.
