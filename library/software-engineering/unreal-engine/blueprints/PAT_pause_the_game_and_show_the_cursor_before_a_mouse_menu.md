---
object_id: PAT_pause_the_game_and_show_the_cursor_before_a_mouse_menu
object_type: pattern
name: Pause the Game and Show the Cursor Before a Mouse Menu
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
  target_object_id: PAT_display_a_widget_with_create_widget_and_add_to_viewport
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Pause the Game and Show the Cursor Before a Mouse Menu

## Pattern Rule
**IF** a menu or end screen needs the player to click buttons with the mouse — a win screen, a pause menu, a settings screen
**THEN** pause the game and re-enable the mouse cursor before displaying the menu, so the world stops and the player can actually click the buttons.

## Do
- Pause the game (Set Game Paused) so the world stops while the player chooses.
- Re-enable the mouse cursor (Show Mouse Cursor on the player controller) so the player can move and click.
- Then create the menu widget and add it to the viewport.
- Order the chain: pause, show cursor, then display the menu.

## Don't
- Don't show a mouse-driven menu while the game is still running — the world keeps moving and the cursor may be hidden, so the player can't click.
- Don't forget to show the cursor; in a mouse-look game the cursor is hidden during play, so a menu with buttons is unclickable without re-enabling it.
- Don't display the menu before pausing; the pause and the cursor are preconditions for a clickable menu.

## Checklist
- The game is paused before the menu appears.
- The mouse cursor is shown before the menu appears.
- The menu widget is created and added to the viewport after the pause and cursor.

## Notes
A menu that needs mouse clicks has two preconditions a running mouse-look game does not satisfy: the world must be still (paused) and the cursor must be visible. Pause the game and show the cursor first, then display the menu widget. Get the order wrong — show the menu while the game runs or with the cursor hidden — and the buttons can't be clicked.
