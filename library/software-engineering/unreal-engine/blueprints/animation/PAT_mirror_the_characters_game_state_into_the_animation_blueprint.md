---
object_id: PAT_mirror_the_characters_game_state_into_the_animation_blueprint
object_type: pattern
name: Mirror the Character's Game State into the Animation Blueprint
library_path:
- software-engineering
- unreal-engine
- blueprints
- animation
stage_binding: 1 skeleton
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- blueprints
- animation
- animation_blueprint
- state
- transition_rule
cross_links:
- rel: related_to
  target_object_id: PAT_fetch_character_data_in_the_animation_blueprints_event_graph
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Mirror the Character's Game State into the Animation Blueprint

## Pattern Rule
**IF** a State Machine Transition Rule needs to read a game state that lives in the Character (for example, a Proning flag)
**THEN** mirror that state into the Animation Blueprint as its own variable, updated every frame in the EventGraph from the Character, because Transition Rules can only read Animation Blueprint variables.

## Do
- Create a variable in the Animation Blueprint for the state you need (for example, a Boolean Proning).
- In the EventGraph, on Event Blueprint Update Animation, cast to the Character, read the Character's state variable, and write it to the Animation Blueprint's copy every frame.
- Use the Animation Blueprint's copy in the Transition Rules, not the Character's variable.

## Don't
- Don't read the Character's variable directly in a Transition Rule — the rule has no access to the Character, only to Animation Blueprint variables.
- Don't copy the state once at initialization — the Character's state changes at runtime, so the mirror must update every frame to stay in sync.

## Checklist
- The Animation Blueprint has its own variable for the state.
- The EventGraph updates that variable from the Character every frame.
- The Transition Rules read the Animation Blueprint's copy of the state.

## Notes
The Character keeps the authoritative state; the input event sets it. The Animation Blueprint holds a read-only mirror that the Transition Rules consult, because the rules have no access to the Character. The mirror is a variable in the Animation Blueprint that the EventGraph refreshes every frame: cast to the Character, read the Character's state, and write it to the Animation Blueprint's copy. This is the same fetch-and-store division as the Animation Blueprint's EventGraph/AnimGraph split, applied to a state flag instead of a continuous value.
