---
object_id: PAT_bind_a_widget_property_to_the_value_it_displays
object_type: pattern
name: Bind a Widget Property to the Value It Displays
library_path:
- software-engineering
- unreal-engine
- blueprints
stage_binding: 0 design
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: PAT_single_source_of_truth_for_data
tags:
- unreal_engine
- blueprints
- umg
- ui
- binding
- single_source_of_truth
cross_links:
- rel: related_to
  target_object_id: PAT_use_an_event_dispatcher_to_notify_listeners_without_naming_them
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Bind a Widget Property to the Value It Displays

## Pattern Rule
**IF** a UI element — a progress bar, a text label — should display a gameplay value that changes over time (health, stamina, ammo, a score)
**THEN** bind the widget's display property (Percent, Text) to a function that returns the value, so the display is derived from the value and updates automatically whenever the value changes; update only the value, never the display.

## Do
- In the UMG Editor, select the widget and click the Bind button next to the display property (Percent for a progress bar, Text for a text label), then Create Binding.
- In the generated binding function, return the value: get the object that owns the value, cast it to the type that declares the variable, get the variable, and return it.
- For a numeric value displayed as text, leave the ToText conversion node the engine inserts automatically wired into the return.
- Modify the value in the game logic — the event that changes it — and let the bound display update on its own.

## Don't
- Don't store a copy of the value in the widget and update it manually every time the value changes — that creates two sources of truth that can disagree.
- Don't have the game logic reach into the widget to set its display — that couples the producer to the consumer and defeats the binding.
- Don't bind a display to a value the widget itself owns or mutates — the value should live on the object that owns the gameplay state.

## Checklist
- The widget's display property is bound to a function that returns the value.
- The binding function returns the value from the object that owns it (get the object, cast, get the variable, return).
- The game logic modifies the value; the display updates without any code touching the widget.
- There is no stored copy of the value in the widget.

## Notes
A UMG binding ties a widget property to a function of the Blueprint; whenever the value the function returns changes, the widget re-evaluates the binding and the display updates automatically. This makes the display a derived value rather than a stored copy: there is one source of truth (the gameplay variable), and the display is computed from it on demand. The binding is the pull form of letting a consumer react to a producer's value — the display pulls the value — in contrast to an event dispatcher, which is the push form where the producer broadcasts an event and listeners react. Use a binding to display a value; use an event dispatcher to react to an event. The binding function typically gets the object that owns the value (the player character), casts it to the type that declares the variable, and returns the variable; the cast is what lets the widget reach a variable on a specific subclass.
