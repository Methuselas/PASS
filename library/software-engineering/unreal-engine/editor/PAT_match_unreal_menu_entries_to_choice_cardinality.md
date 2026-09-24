---
object_id: PAT_match_unreal_menu_entries_to_choice_cardinality
object_type: pattern
name: Match Unreal Menu Entries to Choice Cardinality
library_path:
- software-engineering
- unreal-engine
- editor
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- editor_tools
- menus
- settings
cross_links: []
reference:
  source_title: Extending and Customizing Unreal Engine Editor
  author: Roger Mattsson
confidence: medium
references: []
variants: []
---

# Match Unreal Menu Entries to Choice Cardinality

## Pattern Rule
**IF** an Unreal editor menu exposes persistent Boolean or mutually exclusive settings
**THEN** use toggle entries for independent Booleans and a radio-entry group for a one-of-many choice, with checked queries derived from the stored setting.

## Do
- Build each entry from an `FUIAction` whose execute callback mutates the intended default object, persists the committed choice and whose checked callback reads that same object.
- Use `EUserInterfaceActionType::ToggleButton` for an independent on/off value.
- Generate one `RadioButton` entry per valid enum choice when exactly one value may be selected; capture the iteration value by value in each action.
- Put a large or conceptually separate choice set in a submenu and choose hover/click and auto-close behavior from whether the user is performing an action or editing several settings.
- Supply clear labels and tooltips, and use separators only when they expose meaningful groups.
- Exercise every entry and verify that reopening the menu paints the persisted state rather than widget-local state.

## Don't
- Don't present a mutually exclusive choice as unrelated checkboxes; the controls would imply combinations the model cannot represent.
- Don't keep a second menu-only selection variable or capture the loop variable by reference into deferred actions.

## Checklist
- Does the control type communicate whether zero, one or many choices are legal?
- After each action, do the checked states agree with the one stored value and survive reopening?
- Can every generated action still identify the enum value it was created for?

## Notes
Control appearance is part of the setting contract. A radio group says selection is exclusive, while a checkbox says the value is independently toggled. `FMenuBuilder` supplies both forms without requiring hand-built Slate layout.
