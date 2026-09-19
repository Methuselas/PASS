---
object_id: PAT_choose_gameplay_framework_base_class_by_role
object_type: pattern
name: Choose the Gameplay Framework Base Class by Role
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
- gameplay_framework
cross_links:
- rel: related_to
  target_object_id: PAT_put_player_input_in_the_player_controller
- rel: related_to
  target_object_id: PAT_put_cross_level_state_in_the_game_instance
- rel: related_to
  target_object_id: PAT_put_game_rules_and_defaults_in_the_game_mode
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Choose the Gameplay Framework Base Class by Role

## Pattern Rule
**IF** you are creating a new Blueprint and must choose its parent class
**THEN** pick the Gameplay Framework class that matches the role the object plays: Actor for anything that exists in a level, Pawn for a body a controller possesses, Character for a walking or flying character, PlayerController for human input, AIController for AI, GameMode for the game's rules and default class choices, or GameInstance for state that must survive level transitions.

## Do
- Base plain level objects (props, effects, targets) on Actor, the parent of everything that can be placed or spawned in a level.
- Base a possessed game character on Character when it walks, runs, jumps, swims, or flies — it inherits the CapsuleComponent for collision, the ArrowComponent for facing, the skeletal Mesh, and the CharacterMovement component that handles movement, replication, and prediction.
- Use plain Pawn when the character does not need Character's movement components, and WheeledVehicle for wheeled vehicles.
- Put the "brain" in a Controller: PlayerController for a human player, AIController for AI. The Pawn is the body; the Controller possessing it is what moves it and performs actions.
- Define the game's rules and the default classes for Pawn, PlayerController, GameState, and HUD in a GameMode (a Game Mode Base subclass) via its Class Defaults.
- Hold values that must persist across level transitions in the GameInstance, which is created when the game starts and destroyed only when it closes.

## Don't
- Don't base everything on Actor out of habit — a possessed character built on Actor misses the movement, collision, and possession machinery that Character and Pawn provide.
- Don't put human input handling in the Pawn when the character may be swapped; the PlayerController is the stable home for input.
- Don't expect level objects to remember values across a level load — every Actor in a level is destroyed and respawned when the level changes; only the GameInstance persists.
- Don't confuse components with Actors: Actor Component and Scene Component are not Actors; they are attached to Actors.

## Checklist
- The parent class matches the object's role: level object (Actor), possessed body (Pawn/Character), input or AI brain (PlayerController/AIController), rules and defaults (GameMode), cross-level state (GameInstance).
- A character that moves on foot or in the air is a Character, not a plain Actor or Pawn.
- State that must survive a level transition lives in the GameInstance, not in an Actor.

## Notes
The hierarchy is Object → Actor → {Pawn → Character/WheeledVehicle, GameMode, Controller → PlayerController/AIController}; Actor Component and Scene Component branch off separately and are attached to Actors rather than placed in levels. Choosing the parent class is the first step of creating any Blueprint, and the class type accumulates up the hierarchy: a Character instance is also a Pawn and an Actor, so it can be passed anywhere its parent types are accepted.
