---
object_id: AP_implement_save_and_load_with_a_savegame_child_class
object_type: ap
name: Implement Save and Load With a SaveGame Child Class
library_path:
- software-engineering
- unreal-engine
- blueprints
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- blueprints
- savegame
- persistence
- save_load
cross_links:
- rel: related_to
  target_object_id: PAT_put_cross_level_state_in_the_game_instance
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Implement Save and Load With a SaveGame Child Class

## Objective
Persist a small set of game state to a file so the player can quit and later resume where they left off, using the engine's SaveGame system.

## Steps / Flow
1. Create a Blueprint child of the SaveGame class. Add only the variables that hold the state to persist (for example, an Integer for the current round). This child is the save-data container.
2. On the actor that owns the state (often the player character), add an Object Reference variable typed to the save child (to hold the created or loaded instance) and a String variable for the save slot name (the file name).
3. Build a Save macro (In/Out Exec): guard the object reference with Is Valid; if it is invalid, Create Save Game Object (the save child class) and store the result in the reference. Set the save child's variables from the live state. Then Save Game to Slot with the Save Game Object set to the reference, the Slot Name set to the slot string, and User Index 0.
4. Build a Load macro (In/Out Exec): Does Save Game Exist (Slot Name, User Index 0) into a Branch. If the save does not exist, exit. If it does, Load Game from Slot, then Cast the result to the save child and handle Cast Failed by exiting. On success, store the cast result in the object reference and copy the saved variables into the live state.
5. Call the Load macro in BeginPlay before initializing gameplay parameters that depend on the saved state, so the resumed state is in place before the round goal, HUD, and similar setup run.

## Notes
Use User Index 0 for a single-player slot. The save child holds only what must survive a quit; derive the rest at load time. The object reference is created lazily on first save (the Is Valid guard) rather than in BeginPlay, so a fresh game has no save object until the first save. The Game Instance is an alternative for state that must survive level loads within a session; the SaveGame file is the mechanism for state that must survive quitting the application.
