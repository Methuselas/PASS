---
object_id: PAT_scale_per_round_difficulty_from_the_round_number_via_a_multiplier
object_type: pattern
name: Scale Per-Round Difficulty From the Round Number Via a Multiplier
library_path:
- software-engineering
- unreal-engine
- blueprints
stage_binding: 0 design
lane_fit: both
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- unreal_engine
- blueprints
- difficulty
- rounds
- arcade
cross_links:
- rel: related_to
  target_object_id: AP_implement_save_and_load_with_a_savegame_child_class
- rel: related_to
  target_object_id: PAT_check_the_goal_condition_when_the_tracked_counter_changes
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Scale Per-Round Difficulty From the Round Number Via a Multiplier

## Pattern Rule
**IF** a game uses rounds to escalate difficulty (arcade-style)
**THEN** derive each round's difficulty parameter from the round number via a tuning multiplier (for example, target goal = round × multiplier), so difficulty scales predictably with progress.

## Do
- Store the round number (persisted across sessions).
- Define a tuning multiplier (for example, an Integer variable with a default such as 2).
- At the start of each round, compute the difficulty parameter as round × multiplier (for example, the number of enemies to defeat).
- Set the gameplay parameter (for example, the target goal) from that computed value.

## Don't
- Don't hard-code a fixed difficulty for every round — that makes later rounds no harder than earlier ones.
- Don't tie difficulty to wall-clock time or session length; tie it to the round the player has reached, so progress (not time) drives the challenge.

## Checklist
- A round number drives the difficulty.
- A tuning multiplier scales it.
- The gameplay parameter is set from round × multiplier at round start.

## Notes
Arcade games raise difficulty as the player progresses through rounds. Multiplying the round number by a tuning constant gives a simple, predictable escalation that reuses existing assets (no new content per round). The multiplier is the tuning knob: raise it for a steeper curve.
