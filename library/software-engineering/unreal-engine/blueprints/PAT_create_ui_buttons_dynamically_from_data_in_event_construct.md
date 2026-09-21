---
object_id: PAT_create_ui_buttons_dynamically_from_data_in_event_construct
object_type: pattern
name: Create UI Buttons Dynamically From Data in Event Construct
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
- umg
- dynamic_ui
- event_construct
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Create UI Buttons Dynamically From Data in Event Construct

## Pattern Rule
**IF** the set of UI options (buttons, choices) is determined by data at runtime rather than fixed at design time
**THEN** create the buttons dynamically in Event Construct (or a populate function) from the data, rather than placing them by hand in the widget designer.

## Do
- Create one button per data entry with a Create Widget node (the button's Widget Blueprint class) and add it to the widget's container.
- Set each button's icon from the data (for example, the thumbnail stored with each option) so the button shows what it selects.
- Bind each button's On Clicked event to a handler that reports which option (index) was chosen.

## Don't
- Don't place the buttons by hand in the widget designer when the option set is data-driven — hand-placed buttons can't track a data set that changes.
- Don't create the buttons in an event that fires before the data is available — Event Construct runs when the widget is created, after the data is set.

## Checklist
- The number of buttons matches the number of entries in the data.
- Each button shows the icon for its option.
- Clicking a button reports the correct option index.

## Notes
When the options a UI offers come from data (a list of product parts, a list of settings), the buttons should be created from that data, not placed by hand. Event Construct is the natural place: it runs when the widget instance is created, so the data is available. A populate function iterates the data, creates a button per entry (Create Widget), sets its icon from the data, and binds its On Clicked to a handler that reports the chosen index. This keeps the UI in sync with the data automatically.
