---
object_id: PAT_convert_niagara_numeric_pins_to_the_required_data_type
object_type: pattern
name: Convert Niagara Numeric Pins to the Required Data Type
library_path:
- software-engineering
- unreal-engine
- vfx
- niagara
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- niagara
- vfx
cross_links: []
reference:
  source_title: Build Stunning Real-time VFX with Unreal Engine 5
  author: Hrishikesh Andurlekar
confidence: high
references: []
variants: []
---

# Convert Niagara Numeric Pins to the Required Data Type

## Pattern Rule
**IF** a Niagara arithmetic node starts with generic Numeric pins but the operation needs a concrete scalar or vector type
**THEN** convert the Numeric pin to the data type required by the connected values before wiring the operation.

## Do
- Use Convert Numeric To on the pin when a concrete type is needed.
- Choose Vector 2D, Vector, Vector 4, float, or another compatible type based on the data being processed.
- Confirm the output type matches the destination input.

## Don't
- Don't assume a generic Numeric pin already has the type required by the graph.
- Don't mix incompatible vector dimensions without an explicit conversion.

## Checklist
- The arithmetic node exposes the intended concrete data type.
- Connected pins are type-compatible.

## Notes
Niagara arithmetic nodes may begin with generic Numeric pins that are specialized by conversion.
