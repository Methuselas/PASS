---
object_id: PAT_document_and_organize_variables_with_tooltip_and_category
object_type: pattern
name: Document and Organize Variables With Tooltip and Category
library_path:
- software-engineering
- unreal-engine
- blueprints
stage_binding: 1 skeleton
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- blueprints
- variables
- documentation
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Document and Organize Variables With Tooltip and Category

## Pattern Rule
**IF** a Blueprint has many variables and you need to identify and organize them
**THEN** use each variable's Tooltip property to describe its purpose and its Category property to group related variables.

## Do
- Give every Instance Editable variable a tooltip so the designer using an instance of the Blueprint in the Level understands its purpose; the tooltip is shown when the mouse cursor is over the variable.
- Group related variables under a Category — create a new category or select an existing one in the drop-down; variables are separated by category in the My Blueprint tab, which can be opened and closed.

## Don't
- Don't leave an Instance Editable variable without a tooltip — the designer has no way to know what the variable does.
- Don't leave a large set of variables ungrouped — a flat list is hard to understand.

## Checklist
- Each variable's purpose is described in its Tooltip.
- Instance Editable variables have tooltips.
- Related variables are grouped under a Category.

## Notes
Tooltip and Category are found in the Details panel of a variable. Example: a "Round State" category grouping `TargetsEliminated`, `TargetGoal`, and `CurrentRound`.
