---
object_id: PAT_use_a_structure_to_group_related_variables
object_type: pattern
name: Use a Structure to Group Related Variables
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
- structures
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

# Use a Structure to Group Related Variables

## Pattern Rule
**IF** several related variables of different types always travel together and should be treated as one value
**THEN** define a structure (struct) that groups them into a single composite type, so you pass, store, and default the group as one unit.
**ELSE** where the variables are unrelated or only occasionally used together, separate variables are clearer.

## Do
- Create the structure as a standalone asset (Content Browser → ADD → Blueprints → Structure), not inside a Blueprint class.
- Add variables of different types with New Variable; a member can itself be a complex type (another structure, array, set, map, or object reference).
- Use the structure as a variable's type in a Blueprint.
- Use the Make node to build a structure from its separate elements and the Break node to separate a structure into its elements.
- Set default values in the DEFAULT VALUE panel after compiling.

## Don't
- Don't group unrelated variables into a structure just to reduce their count — a struct is for data that is meaningfully one thing.
- Don't define the structure inside a Blueprint class when it should be a shared asset.
- Don't pass the group field by field when a Make/Break node can carry it as one unit.

## Checklist
- Do the variables always travel together and form one meaningful unit?
- Is the structure a standalone asset?
- Are Make and Break nodes used to build and deconstruct it?

## Notes
A structure is a composite data type that groups variables of different types into a single type. Its members can be complex (another structure, a container, an object reference), which is what makes it the building block for richer data — a weapon's name, category, damage, fire rate, range, and accuracy become one WeaponType value. The Make node assembles the group from its parts; the Break node takes a group apart. A structure is also the row type for a data table.
