---
object_id: PAT_derive_a_new_menu_screen_from_an_existing_one_by_duplication
object_type: pattern
name: Derive a New Menu Screen From an Existing One by Duplication
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
- umg
- ui
- menu
- widget
cross_links:
- rel: related_to
  target_object_id: PAT_display_a_widget_with_create_widget_and_add_to_viewport
- rel: related_to
  target_object_id: PAT_pause_the_game_and_show_the_cursor_before_a_mouse_menu
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Derive a New Menu Screen From an Existing One by Duplication

## Pattern Rule
**IF** a new menu or screen shares structure with an existing one (the same layout, similar buttons)
**THEN** duplicate the existing widget as a template and rework the elements, rather than rebuilding the screen from scratch.

## Do
- Duplicate the existing Widget Blueprint (for example, a win menu) to create the new one (for example, a lose menu, a pause menu, a round-transition screen).
- Rename the new asset to reflect its new purpose.
- Rework the elements: change the message text and color, add or remove buttons, and rename buttons to match the new actions.
- Rewire the button events to the new actions.

## Don't
- Don't rebuild a screen from scratch when an existing one already has the layout and button structure you need — duplication is faster and keeps the screens consistent.
- Don't leave the duplicated screen's old names and text (for example, a "You Win!" message on a lose screen) — rename and rework so the screen matches its purpose.

## Checklist
- The new screen is a duplicate of an existing one.
- The asset is renamed to reflect its purpose.
- The message, buttons, and button events match the new purpose.

## Notes
Menus in a game often share structure (a message plus a few buttons). Duplicating an existing widget as a template and reworking it is faster than rebuilding and keeps the screens visually consistent. Rename the asset and its elements so the name reflects the new purpose, not the template's original one.
