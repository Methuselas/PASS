---
object_id: PAT_use_an_enumeration_for_a_fixed_set_of_named_constants
object_type: pattern
name: Use an Enumeration for a Fixed Set of Named Constants
library_path:
- software-engineering
- unreal-engine
- blueprints
- data-structures
stage_binding: 0 design
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- blueprints
- data_structures
- enumerated_types
cross_links:
- rel: related_to
  target_object_id: PAT_choose_blueprint_variable_type_by_value_kind
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Use an Enumeration for a Fixed Set of Named Constants

## Pattern Rule
**IF** a variable's value is restricted to a fixed, known set of named alternatives
**THEN** define an enumeration and use it as the variable's type, so the value can only be one of the named constants and the editor restricts it to that set.
**ELSE** where the set of values is open or numeric, a plain type (String, Integer) is the right choice.

## Do
- Create the enumeration as a standalone asset (Content Browser → ADD → Blueprints → Enumeration), not inside a Blueprint class.
- Follow the naming convention of prefixing the enumeration name with an uppercase E (for example, EWeaponCategory).
- Add named constants with the New button; you can add descriptions to the enumeration and to each constant.
- Use the enumeration as a variable's type; the editor then restricts the value to the constants.
- When execution genuinely needs a branch for each enum value, use the enum-specific Switch on node rather than reconstructing the cases with unrelated comparisons.

## Don't
- Don't use an enumeration for an open or numeric set of values — it is for a fixed set of named alternatives.
- Don't define the enumeration inside a Blueprint class when it should be a shared asset.
- Don't skip the E prefix — it is the convention that marks a type as an enumeration.

## Checklist
- Is the value a fixed set of named alternatives?
- Is the enumeration a standalone asset with an E-prefixed name?
- Is the variable's type the enumeration, restricting it to the constants?
- If the enum drives multi-way control flow, is the enum-specific Switch on node the clearest branch?

## Notes
An enumeration is a data type containing a fixed set of named constants. Using it as a variable's type means the value is restricted to that set — the editor will not let you assign anything else. Each enumeration type also gets a Switch on node that is useful when the value needs to drive multi-way execution. The enum remains valuable even when no Switch is needed: the type itself enforces the closed set of alternatives.
