---
object_id: PAT_read_an_array_element_by_value_with_get_a_copy
object_type: pattern
name: Read an Array Element by Value with Get (a Copy)
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
- array
- get_a_copy
- reference_vs_value
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Read an Array Element by Value with Get (a Copy)

## Pattern Rule
**IF** you only need to read the value stored in an array element
**THEN** use the Get (a copy) node to read it by value, instead of the plain Get node, which returns a mutable reference to the element.

## Do
- Add a Get (a copy) node for the array and wire the element's index into its index pin.
- Use the value it returns directly in a comparison or calculation (for example, compare the current XP against the experience points stored at the next level's index).

## Don't
- Don't use the plain Get node when you only need to read — it returns a mutable reference to the element, and writing through it would modify the array.
- Don't write through a Get (a copy) result expecting to modify the array — it is a copy, so changes to it do not affect the array.

## Checklist
- The array read uses Get (a copy), not the plain Get node.
- The read value is used in a comparison or calculation without modifying the array.

## Notes
An array's Get node comes in two forms: the plain Get returns a reference to the element, so writing through it changes the array, while Get (a copy) returns a value, so using it cannot. When the intent is to read, the copy is the safe choice — it makes the read side-effect-free and removes the risk of accidentally mutating the array. Example: a level-up check reads the experience points stored at the next level's index with Get (a copy) and compares the current XP against that value.
