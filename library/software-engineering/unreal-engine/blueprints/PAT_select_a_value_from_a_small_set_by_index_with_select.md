---
object_id: PAT_select_a_value_from_a_small_set_by_index_with_select
object_type: pattern
name: Select a Value From a Small Set by Index With the Select Node
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
- select
- value_choice
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Select a Value From a Small Set by Index With the Select Node

## Pattern Rule
**IF** you need to pick one value from a small fixed set based on an index or enumeration
**THEN** use the Select node, which returns the value of the option that corresponds to the index passed as input.

## Do
- Wire each option pin (Option 0, Option 1, …) to a value of the same type; add more options with Add pin.
- Drive the Index pin with an Integer, Enum, Boolean, or Byte.
- Use the Return Value as the selected value.

## Don't
- Don't use the Select node to route execution — it returns a value, it does not branch execution (use a Switch or Branch for that).
- Don't wire an Index of a type other than Integer, Enum, Boolean, or Byte.

## Checklist
- All option pins are the same type.
- The Index is an Integer, Enum, Boolean, or Byte.
- The Return Value is the selected option's value.

## Notes
The option values can be any type (for example, Actor Class Reference); the index must be Integer, Enum, Boolean, or Byte. Example: a `Difficult Level` enumeration (Easy, Normal, Hard) selects which Boss class a Spawn Boss event spawns.
