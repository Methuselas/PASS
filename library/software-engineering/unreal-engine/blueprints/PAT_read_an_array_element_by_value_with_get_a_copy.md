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
**IF** you need to read an array element without changing the value stored in the array
**THEN** use Get (a copy) to retrieve a copy of the element and use that copy in the downstream comparison or calculation.

## Do
- Add a Get (a copy) node for the array and wire the element index into its index pin.
- Use the returned value directly in a comparison or calculation.
- Treat changes made to the returned value as changes to the copy, not to the array element.

## Don't
- Don't modify a Get (a copy) result expecting the stored array element to change.
- Don't add a write-back step unless the design actually intends to update the array.

## Checklist
- The read uses Get (a copy).
- The returned value is consumed without relying on it to mutate the source array.
- Any intended array mutation is performed explicitly rather than assumed from changing the copy.

## Notes
Get (a copy) returns the selected element as a temporary value. In the book's array example, that value is read for comparison; changing the copy does not change the element stored in the array.
