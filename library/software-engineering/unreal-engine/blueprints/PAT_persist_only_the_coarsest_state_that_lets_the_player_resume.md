---
object_id: PAT_persist_only_the_coarsest_state_that_lets_the_player_resume
object_type: pattern
name: Persist Only the Coarsest State That Lets the Player Resume
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
- design
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

# Persist Only the Coarsest State That Lets the Player Resume

## Pattern Rule
**IF** a game needs to save progress so the player can quit and later resume
**THEN** save only the coarsest state that lets the player resume meaningfully (for example, the current round), and recompute the rest at load time — do not save every transient value.

## Do
- Identify the smallest set of values that, restored, lets the player continue from a sensible point (for example, the round number).
- Store only those values in the save container.
- Derive the rest (for example, the round's target goal, the enemy count) from the saved values at load time.

## Don't
- Don't save transient per-session values that reset each round (for example, how many enemies the player has killed this round) — restoring them would be wrong or pointless because each session starts at the beginning of a round.
- Don't let the save file become a dump of every variable; that couples the save format to incidental state and bloats it.

## Checklist
- The save container holds only the values needed to resume.
- Values that reset each round are not saved.
- Derived values are recomputed from the saved values at load.

## Notes
The decision is about the resume point. If each session starts at the beginning of a round, the round number is enough; the kill count within the round is meaningless across a quit. Save the coarsest state that defines the resume point and recompute the fine-grained state from it.
