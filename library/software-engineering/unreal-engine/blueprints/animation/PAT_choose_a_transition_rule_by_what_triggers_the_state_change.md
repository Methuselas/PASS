---
object_id: PAT_choose_a_transition_rule_by_what_triggers_the_state_change
object_type: pattern
name: Choose a Transition Rule by What Triggers the State Change
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
- state_machine
- transition_rule
cross_links:
- rel: related_to
  target_object_id: PAT_organize_character_animation_into_states_with_a_state_machine
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Choose a Transition Rule by What Triggers the State Change

## Pattern Rule
**IF** you are defining when a State Machine transition happens
**THEN** choose the Transition Rule by what should trigger the change: a condition on a variable when the change is driven by game state (for example, a Proning flag), or a Time Remaining (ratio) check when the change should happen when a one-shot animation finishes.

## Do
- For a state-driven transition, wire the condition to the Result node: for example, Get Proning to Result for Idle to StandToProne, and Get Proning through a Not Boolean to Result for Prone to ProneToStand.
- For an animation-end transition, add a Time Remaining (ratio) node for the state's animation, compare it with a Less node against a small threshold such as 0.1, and wire the result to the Result node.
- Uncheck the Loop Animation property on a one-shot animation that must finish so the Time Remaining (ratio) check can reach the end.
- Double-click the transition rule icon on the arrow to edit its graph; the transition happens when the Result node receives True.

## Don't
- Don't use a Time Remaining (ratio) check on a looping animation — it never ends, so the transition never fires.
- Don't drive a state change with a condition when the change should follow the animation's completion — the character would leave the state before the animation finishes.
- Don't leave the Result node unwired — with no condition the transition is not controlled.

## Checklist
- A state-driven transition wires a variable condition to the Result node.
- An animation-end transition wires a Time Remaining (ratio) Less threshold to the Result node.
- The one-shot animation that triggers an animation-end transition has Loop Animation unchecked.

## Notes
A Transition Rule is the graph on a state-machine transition arrow; the transition happens when its Result node receives True. There are two shapes to it. The first checks a variable — the rule reads a state flag (for example, Proning) and transitions when the flag is set, optionally negated with a Not Boolean for the reverse direction. The second waits for an animation to finish — a Time Remaining (ratio) node reports how much of the state's animation is left, and a Less comparison against a small threshold such as 0.1 fires the transition as the animation ends. The choice is driven by what should trigger the change: a game-state change uses the variable condition, and a one-shot animation's completion uses the time-remaining check.
