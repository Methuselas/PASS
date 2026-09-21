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
- rel: supports
  target_object_id: PAT_persist_only_the_coarsest_state_that_lets_the_player_resume
- rel: supports
  target_object_id: PAT_guard_object_references_with_is_valid
- rel: supports
  target_object_id: PAT_use_cast_to_test_a_type_or_reach_subclass_members
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
Persist a small set of game state to a file and verify that a later load restores the saved state before dependent gameplay initialization continues.

## Steps / Flow
1. Apply `PAT_persist_only_the_coarsest_state_that_lets_the_player_resume`: create a Blueprint child of the SaveGame class and add only the variables that must survive quitting, such as the current round.
2. On the actor that owns the live state, add an Object Reference variable typed to the save child and a String variable for the save slot name.
3. Build a Save macro with In/Out Exec. Apply `PAT_guard_object_references_with_is_valid` to the save-object reference; if it is invalid, create the Save Game Object and store the result. Copy the live values into the save object, then call Save Game to Slot with the stored slot name and User Index 0.
4. Build a Load macro. Call Does Save Game Exist with the same slot name and User Index 0 and branch. If no save exists, exit the load path without changing the live state.
5. When a save exists, call Load Game from Slot and apply `PAT_use_cast_to_test_a_type_or_reach_subclass_members` to cast the loaded object to the save child. If the cast fails, exit safely. On success, store the cast result and copy the saved values back into the live state.
6. Call Load from BeginPlay before initializing values that depend on the persisted state, so resumed state is established before round goals, HUD values, or similar setup are derived.
7. Verify the completed flow end to end: save a distinguishable state, change or restart the session so the live value no longer matches, load the slot, and confirm that the live value returns to the saved value before dependent initialization uses it.

## Notes
Use User Index 0 for the single-player slot shown by the source. The SaveGame child is the file-persistence mechanism; `PAT_put_cross_level_state_in_the_game_instance` covers the different case where state only needs to survive level transitions within the running application. The validity guard, type cast, and coarse-state decisions are delegated to the named Patterns above rather than redefined here.
