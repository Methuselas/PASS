---
object_id: PAT_gate_an_action_on_an_open_close_state_with_a_gate
object_type: pattern
name: Gate an Action on an Open-Close State with a Gate
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
- gating
cross_links:
- rel: related_to
  target_object_id: PAT_gate_an_action_on_its_resource
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Gate an Action on an Open-Close State with a Gate

## Pattern Rule
**IF** an action should run only while a condition holds — apply damage only while an actor is overlapping, run a behavior only while a flag is set
**THEN** wire the condition's begin event to a Gate node's Open pin and its end event to the Close pin, wire the action to the Gate's Exit pin through its Enter pin, and set Start Closed so the action is off until the condition begins.

## Do
- Wire the condition's begin event (such as Event Actor Begin Overlap) to the Gate's Open pin.
- Wire the condition's end event (such as Event Actor End Overlap) to the Gate's Close pin.
- Wire the repeating trigger (such as Event Tick) to the Gate's Enter pin and the action to the Gate's Exit pin.
- Set Start Closed when the action must be off until the condition begins.
- Use the Toggle pin when the condition is a single event that should flip the state rather than open and close it separately.

## Don't
- Don't leave Start Closed unset when the action must be off at start — the Gate begins open and the action would run before the condition ever begins.
- Don't wire the action directly to the repeating trigger and check the condition by hand — the Gate's internal state is what blocks the action while it is closed.
- Don't use a Gate for a one-shot or counted limit — it stays open until closed, so it cannot express "run once" or "run N times."

## Checklist
- The action runs on every trigger while the Gate is open and not while it is closed.
- The condition's begin event opens the Gate and its end event closes it.
- The Gate starts closed when the action must be off until the condition begins.

## Notes
A Gate is the open-close state for an action that should run only while a condition holds. Its internal state blocks the Exit pin while the Gate is closed, which is what lets a repeating trigger such as a tick apply an effect only during the overlap. The Open, Close, and Toggle pins set the state from the condition's events, and Start Closed keeps the action off until the first begin. For a limit on how many times an action may run, a Do Once or Do N is the right node; a Gate is for "while the condition holds."
