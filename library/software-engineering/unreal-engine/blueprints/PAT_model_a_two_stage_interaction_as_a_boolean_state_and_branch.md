---
object_id: PAT_model_a_two_stage_interaction_as_a_boolean_state_and_branch
object_type: pattern
name: Model a Two-Stage Interaction as a Boolean State and a Branch
library_path:
- software-engineering
- unreal-engine
- blueprints
stage_binding: 1 skeleton
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- blueprints
- state
- branching
- hit
cross_links:
- rel: related_to
  target_object_id: PAT_separate_blueprint_state_from_event_driven_behavior
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Model a Two-Stage Interaction as a Boolean State and a Branch

## Pattern Rule
**IF** an object should behave differently on the first occurrence of an event than on later ones — the first hit marks it, the second destroys it
**THEN** store the occurrence as a Boolean state variable (defaulting to the not-yet-happened value) and branch on it in the event handler; the first-occurrence path performs the first-occurrence action and advances the state, and the later-occurrence path performs the terminal action.

## Do
- Create a Boolean variable that represents the state (for example, "has been hit"), and leave its default at the not-yet-happened value so the object starts in the first state.
- In the event handler, branch on the Boolean: the false path is the first occurrence, the true path is the later occurrence.
- In the first-occurrence path, perform the first-occurrence action and set the Boolean to true, so the next event takes the later-occurrence path.
- In the later-occurrence path, perform the terminal action (for example, destroy the object).

## Don't
- Don't leave the Boolean's default at the happened value — the object would start in the later state and skip the first-occurrence behavior.
- Don't forget to advance the state in the first-occurrence path — without it, every event takes the first-occurrence path and the terminal action never fires.
- Don't put the state in the event graph; the state lives in the variable, the behavior in the handler.

## Checklist
- The first event takes the first-occurrence path and advances the state.
- The second and later events take the later-occurrence path.
- The Boolean's default is the not-yet-happened value.

## Notes
The first step of building a branch is to determine what the Boolean represents and what will cause it to change from false to true. A Boolean state plus a branch is the small state machine for an object whose behavior changes after the first occurrence of an event. The first-occurrence path is the one that advances the state; the later-occurrence path is terminal.
