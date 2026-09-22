---
object_id: PAT_order_niagara_modules_as_top_to_bottom_dataflow
object_type: pattern
name: Order Niagara Modules as Top-to-Bottom Dataflow
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

# Order Niagara Modules as Top-to-Bottom Dataflow

## Pattern Rule
**IF** multiple Niagara modules read or modify related particle data in the same stack
**THEN** order them deliberately because the stack flows from top to bottom and later modules receive the state produced by earlier ones.

## Do
- Trace which values each module reads and writes.
- Place prerequisite calculations before modules that consume their results.
- Recheck ordering when two modules both affect the same property.

## Don't
- Don't treat stack order as cosmetic.
- Don't debug a downstream result without checking what earlier modules wrote into the same state.

## Checklist
- The stack order reflects the intended data dependencies.
- Reordering modules that share data is expected to change behavior and is tested deliberately.

## Notes
Niagara stack order is execution order, not just visual organization.
