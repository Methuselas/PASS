---
object_id: PAT_put_cross_level_state_in_the_game_instance
object_type: pattern
name: Hold Cross-Level State in the GameInstance
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
- game_instance
- persistence
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Hold Cross-Level State in the GameInstance

## Pattern Rule
**IF** a value must survive a level transition
**THEN** store it in the GameInstance, because every Actor and other object in a level is destroyed and respawned when a new level loads, while the GameInstance is created when the game starts and removed only when the game closes.

## Do
- Assign your GameInstance subclass in Project Settings → Maps & Modes → Game Instance Class so the game uses it.
- Put the values that must persist across levels (scores, unlocked state, carried-over settings) in the GameInstance's variables.
- Treat the GameInstance as the game-lifetime home for state, in contrast to level-lifetime state in Actors.

## Don't
- Don't keep must-survive values in an Actor's variables and expect them to be there after the level changes — the Actor is gone with the level.
- Don't create a new persistence mechanism for every value; the GameInstance is the built-in option for game-lifetime state.

## Checklist
- The value is stored in a GameInstance variable, not in an Actor.
- The project's Game Instance Class is set to your subclass.
- The value is still present after loading a different level.

## Notes
The GameInstance is not one of the Common Classes shown in the parent-class picker, but it is the standard place for data that outlives individual levels.
