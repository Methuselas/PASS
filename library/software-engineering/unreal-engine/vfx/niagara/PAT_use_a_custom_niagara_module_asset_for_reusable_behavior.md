---
object_id: PAT_use_a_custom_niagara_module_asset_for_reusable_behavior
object_type: pattern
name: Use a Custom Niagara Module Asset for Reusable Behavior
library_path:
- software-engineering
- unreal-engine
- vfx
- niagara
stage_binding: 1 skeleton
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

# Use a Custom Niagara Module Asset for Reusable Behavior

## Pattern Rule
**IF** custom Niagara graph logic should be reused across systems, users, or projects
**THEN** author it as a separate Niagara Module Script asset with a deliberate public interface.

## Do
- Keep reusable logic in an independent Module Script asset.
- Expose only the inputs consumers need to tune.

## Don't
- Do not leave reusable logic trapped as a one-off local module.

## Checklist
- The module can be added to another compatible Niagara stack without copying the graph.

## Notes
Separate Module Script assets are the reusable custom-logic boundary; version them when production consumers need stable historical behavior.
