---
object_id: PAT_use_a_structure_to_group_related_variables
object_type: pattern
name: Use a Blueprint Structure Asset to Group Related Variables
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
foundation_object_id: PAT_encapsulate_related_data_together
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

# Use a Blueprint Structure Asset to Group Related Variables

## Pattern Rule
**IF** several related values in an Unreal Blueprint should travel, be stored, or be defaulted as one composite value
**THEN** create a Blueprint Structure asset for that group and use the resulting struct type in Blueprint variables and Make/Break nodes.
**ELSE** where the values are unrelated or only occasionally used together, keep them separate.

## Do
- Create the structure as a standalone asset from the Content Browser under Blueprints -> Structure.
- Add the related members with New Variable; members may use different types, including other structures, containers, or object references.
- Use the structure as a Blueprint variable type.
- Use the Make node to assemble the composite value and the Break node to expose its members where needed.
- Set default values for the structure after compiling.

## Don't
- Don't group unrelated variables merely to reduce the visible variable count.
- Don't pass the same conceptual record field by field when the Blueprint Structure is the value that should cross the boundary.

## Checklist
- The members form one meaningful record or concept.
- The group is represented by a reusable Blueprint Structure asset.
- Blueprint variables can use the structure as their type.
- Make/Break nodes assemble and deconstruct the value where appropriate.

## Notes
This is the Unreal Blueprint specialization of `PAT_encapsulate_related_data_together`. The source demonstrates a Structure asset as a composite data type whose members can themselves be complex values; the same structure can also serve as the row type of a Data Table.
