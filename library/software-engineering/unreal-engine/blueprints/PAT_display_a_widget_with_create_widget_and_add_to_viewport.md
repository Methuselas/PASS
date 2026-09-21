---
object_id: PAT_display_a_widget_with_create_widget_and_add_to_viewport
object_type: pattern
name: Display a Widget with Create Widget and Add to Viewport
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
- widget
- viewport
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Display a Widget with Create Widget and Add to Viewport

## Pattern Rule
**IF** a Widget Blueprint should appear on screen during play — a HUD, a menu
**THEN** create an instance of it (Create Widget) and then add that instance to the viewport (Add to Viewport); creating the instance alone does not show it.

## Do
- In the Blueprint that should own the display (often the player character), wire an event that matches when the display should appear to a Create Widget node with the Widget Blueprint's class selected.
- Wire the Create Widget's Return Value to an Add to Viewport node's Target.
- Use BeginPlay for an always-on HUD: if the owning instance is present when the game starts, BeginPlay fires at start and the HUD appears immediately; if the instance is spawned later, BeginPlay fires when it spawns and the HUD appears then.

## Don't
- Don't stop at Create Widget — the instance exists in memory but is not on screen until it is added to the viewport.
- Don't create the widget from an event that fires before the display is wanted or after it should be gone; match the creating event to when the display is wanted.

## Checklist
- A Create Widget node instantiates the Widget Blueprint.
- The instance's Return Value is wired to an Add to Viewport node.
- Both run from an event that matches when the display should appear.

## Notes
Creating a widget instance and showing it are two separate steps. Create Widget builds an instance of the Widget Blueprint class; Add to Viewport puts that instance on the screen. Omit the second step and the widget exists but is never drawn. BeginPlay is the natural trigger for an always-on HUD because it fires as soon as the owning instance is present — at game start if the instance is already there, or at spawn time if it is created later — so the HUD appears exactly when the player that owns it does.
