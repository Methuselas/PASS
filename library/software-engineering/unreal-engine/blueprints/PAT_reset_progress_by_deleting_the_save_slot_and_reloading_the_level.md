---
object_id: PAT_reset_progress_by_deleting_the_save_slot_and_reloading_the_level
object_type: pattern
name: Reset Progress by Deleting the Save Slot and Reloading the Level
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
- savegame
- persistence
- reset
cross_links:
- rel: related_to
  target_object_id: AP_implement_save_and_load_with_a_savegame_child_class
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Reset Progress by Deleting the Save Slot and Reloading the Level

## Pattern Rule
**IF** the player should be able to reset their progress and start over
**THEN** delete the save file (if it exists) and reload the level, so the game returns to its initial state.

## Do
- Build a reset macro: retrieve the save slot name from the owning character (Get Player Character, Cast to the character class, then Get the slot-name variable — needed when the reset action lives in a widget that does not own the variable), check Does Save Game Exist; if it exists, Delete Game in Slot (Slot Name, User Index 0); if it does not exist (or the cast to the owning character fails), exit.
- On the reset action (for example, a "Reset All" button), call the reset macro to delete the save file.
- Reload the level (Open Level by Object Reference) so the game restarts from the beginning.
- Remove the menu widget from the viewport after reloading.

## Don't
- Don't reload the level without deleting the save file — the game would load the old progress on the next BeginPlay.
- Don't assume the save file exists; guard the delete with Does Save Game Exist so a first-time reset (no save yet) does not error.

## Checklist
- The save file is deleted (guarded by an existence check).
- The level is reloaded.
- The menu widget is removed.

## Notes
Resetting progress means clearing the persisted state and restarting. Delete the save slot (guarded by an existence check, since a new player has no save yet) and reload the level so BeginPlay runs fresh and finds no save to load. The level reload is what actually restarts the game; deleting the file alone would leave the current session running.
