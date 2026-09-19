---
object_id: PAT_put_game_rules_and_defaults_in_the_game_mode
object_type: pattern
name: Define Game Rules and Default Classes in the GameMode
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
- game_mode
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Define Game Rules and Default Classes in the GameMode

## Pattern Rule
**IF** you need to define the rules of the game or choose the default classes for its Pawn, PlayerController, GameState, and HUD
**THEN** do it in a GameMode (a Game Mode Base subclass) through its Class Defaults, set the project-wide default in Project Settings → Maps & Modes, and override per level in World Settings → GameMode Override.

## Do
- Subclass Game Mode Base for each distinct set of game rules; the GameMode specifies the default classes used to create the Pawn, PlayerController, GameStateBase, HUD, and related objects.
- Set the project's Default GameMode in Project Settings → Maps & Modes so every level has a rules owner.
- Give a level its own rules by setting the GameMode Override in the level's World Settings; the level's GameMode overrides the project default.

## Don't
- Don't scatter the game's rules across individual Actors or the level — the GameMode is the single owner of the rules and the default class choices.
- Don't expect a per-level override to change the project default; the override applies only to that level.

## Checklist
- The game's rules and default class choices live in a GameMode's Class Defaults.
- The project has a Default GameMode set.
- Levels with different rules use the World Settings GameMode Override.

## Notes
A GameMode is how the engine knows which classes to instantiate when a match starts: the default Pawn, the controller, the state, and the HUD all come from its class defaults.
