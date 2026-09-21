---
object_id: PAT_share_reusable_functions_or_macros_project_wide_with_a_blueprint_library
object_type: pattern
name: Share Reusable Functions or Macros Project-Wide with a Blueprint Library
library_path:
- software-engineering
- unreal-engine
- blueprints
stage_binding: 0 design
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- blueprints
- function_library
- macro_library
- reuse
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Share Reusable Functions or Macros Project-Wide with a Blueprint Library

## Pattern Rule
**IF** a function or macro is used in several Blueprints across a project
**THEN** gather it in a Blueprint Function Library (for functions) or a Blueprint Macro Library (for macros) so it is shared project-wide, instead of duplicating it in each Blueprint.

## Do
- Create a Blueprint Function Library to hold shared utility functions; its functions appear as a category in the node search of every Blueprint in the project.
- Create a Blueprint Macro Library to hold shared macros and choose a Parent class (Actor is the best default), because the library's macros can only be used by subclasses of that Parent.
- Put each shared function or macro in the library once and call it from any Blueprint that can use it.

## Don't
- Don't copy the same function into every Blueprint that needs it — a library keeps one copy that every Blueprint calls.
- Don't put a function in a Macro Library expecting it to be callable from any Blueprint — a Macro Library is scoped to its Parent class and that Parent's subclasses only.
- Don't choose a narrow Parent class for a Macro Library you want to reuse widely — a narrower Parent limits which Blueprints can use it.

## Checklist
- The shared function or macro lives in a library asset, not duplicated per Blueprint.
- A Function Library's functions are callable from any Blueprint.
- A Macro Library's Parent class is chosen so the library is usable by the Blueprints that need it.

## Notes
A Blueprint Function Library and a Blueprint Macro Library are asset types that hold shared code. A Function Library holds functions and can be used by all Blueprints in the project. A Macro Library holds macros and requires a Parent class: its macros have access to the Parent's variables and functions, and the library can only be used by subclasses of that Parent, so Actor is the best default for wide reuse. The library's functions or macros appear as a category in the node search of every Blueprint that can use them.
