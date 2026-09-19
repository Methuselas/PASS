---
object_id: PAT_separate_blueprint_state_from_event_driven_behavior
object_type: pattern
name: Separate Blueprint State from Event-Driven Behavior
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
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Separate Blueprint State from Event-Driven Behavior

## Pattern Rule
**IF** you are structuring the logic of a Blueprint
**THEN** keep the state in variables and the behavior in events and actions — variables represent the current state, events are the triggers, and actions are the responses.

## Do
- Store the current state (health, speed, ammunition) in variables, not in the event graph.
- Use events as triggers: collision events when two actors collide or overlap, input events from keyboard, mouse, touch, or gamepad, BeginPlay when the game starts or the actor is spawned, End Play when the actor is about to be removed, and Tick every frame.
- Use actions as responses: get or set variable values, or call functions that modify the state.
- Add each engine event only once, and create a custom event for any trigger the engine does not provide.

## Don't
- Don't scatter state across the event graph — the state lives in variables, the behavior lives in events and actions.
- Don't add the same engine event twice; each one can be added only once.
- Don't treat an event as a place to store a value; an event is a trigger, and the value it carries belongs in a variable.

## Checklist
- The Blueprint's state is in variables, not in the event graph.
- Each behavior is an event (trigger) connected to actions (responses) along the execution path.
- Each engine event appears at most once, and custom events cover the triggers the engine does not provide.

## Notes
Variables represent the current state of a Blueprint; the behavior is defined by events and actions. Events are triggers — collision, input, BeginPlay, End Play, and Tick every frame — and actions are the responses, such as getting or setting a variable or calling a function. The execution path is the white wire that starts at a red event node and follows left to right through the actions. Each engine event can be added only once; a custom event (Add Custom Event) covers any trigger the engine does not provide, and it can carry its own input parameters.
