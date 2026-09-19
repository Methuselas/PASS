---
object_id: PAT_choose_blueprint_variable_type_by_value_kind
object_type: pattern
name: Choose Blueprint Variable Type by Value Kind
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
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Choose Blueprint Variable Type by Value Kind

## Pattern Rule
**IF** you are creating a variable in a Blueprint and must choose its type
**THEN** pick the type that matches the kind and range of the value you need to store, because Blueprint is strongly typed and the type is fixed at creation and cannot change during execution.

## Do
- Use Boolean for a value that is only true or false, Byte for an 8-bit integer from 0 to 255, Integer for a 32-bit integer, and Integer64 for a 64-bit integer.
- Use Float for a fractional value that needs about seven decimal digits of precision, and Double when the value needs sixteen.
- Use Name for a piece of text that identifies an object, String for a group of alphanumeric characters, and Text for text that will be localized into other languages.
- Use Vector for X, Y, Z float values representing a 3D position, Rotator for Roll, Pitch, Yaw representing a rotation, and Transform for location, rotation, and scale together.

## Don't
- Don't default to String or Float for everything — the type is locked in at creation, so a wrong choice is fixed for the life of the variable.
- Don't use Text for an object identifier or String for localizable text; Name, String, and Text each serve a distinct purpose.
- Don't pick a numeric width by habit; match the range and precision the value actually needs.

## Checklist
- The variable's type matches the kind of value it will hold: boolean, integer range, fractional precision, identifier, text, or 3D quantity.
- The numeric type's width and precision match the value's needs (Float for about seven digits, Double for about sixteen).
- The type was chosen from the value's kind and range, not from convenience.

## Notes
Blueprint is a strongly typed language: the type is defined when the variable is created and cannot be modified during program execution, so the choice is made once and for all. Each type is represented by a distinct color in the editor. The decision is which of the built-in value kinds the data belongs to — a boolean, an integer of a given width, a fractional number of a given precision, an identifier, a string, localizable text, or a 3D quantity — and the type is the answer to that question.
