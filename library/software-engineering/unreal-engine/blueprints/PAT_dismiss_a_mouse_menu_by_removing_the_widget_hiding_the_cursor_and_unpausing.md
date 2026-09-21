---
object_id: PAT_dismiss_a_mouse_menu_by_removing_the_widget_hiding_the_cursor_and_unpausing
object_type: pattern
name: Dismiss a Mouse Menu by Removing the Widget, Hiding the Cursor, and Unpausing
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
- pause
cross_links:
- rel: related_to
  target_object_id: PAT_pause_the_game_and_show_the_cursor_before_a_mouse_menu
- rel: related_to
  target_object_id: PAT_display_a_widget_with_create_widget_and_add_to_viewport
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Dismiss a Mouse Menu by Removing the Widget, Hiding the Cursor, and Unpausing

## Pattern Rule
**IF** a mouse-driven menu (a pause menu, a settings screen) is dismissed and play should resume
**THEN** remove the menu widget from the viewport, hide the mouse cursor, and unpause the game, in that order.

## Do
- Remove the menu widget from its parent (Remove from Parent) so it is no longer on screen.
- Hide the mouse cursor (Show Mouse Cursor unchecked on the player controller) so the player returns to mouse-look.
- Unpause the game (Set Game Paused unchecked) so the world runs again.
- Order the chain: remove the widget, hide the cursor, then unpause.

## Don't
- Don't unpause before removing the widget — the world resumes while the menu is still on screen.
- Don't forget to hide the cursor; in a mouse-look game the cursor must be hidden for play to resume correctly.
- Don't leave the menu widget in the viewport after dismissing it.

## Checklist
- The menu widget is removed from the viewport.
- The mouse cursor is hidden.
- The game is unpaused.
- The order is: remove widget, hide cursor, unpause.

## Notes
Dismissing a mouse menu is the inverse of showing one. Showing pauses the game and shows the cursor before displaying the menu; dismissing removes the widget, hides the cursor, and unpauses. Get the order wrong and the world resumes while the menu is still visible or the cursor lingers.
