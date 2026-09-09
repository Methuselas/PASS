---
object_id: PAT_construct_pictorial_town_icon_from_compact_building_cluster
object_type: pattern
name: Construct Pictorial Town Icon From Compact Building Cluster
library_path:
- art
- cartography
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: domain
foundation_object_id: none
tags:
- cartography
- settlements
- towns
- icons
- architecture
- pictorial-symbols
cross_links:
- rel: related_to
  target_object_id: PAT_plan_town_distribution_from_settlement_support_and_regional_density
confidence: high
references: []
variants: []
---

# Construct Pictorial Town Icon From Compact Building Cluster

## Pattern Rule
**IF** a map needs a pictorial town symbol that reads clearly without rendering a complete settlement
**THEN** compress the town into a small coherent cluster of roofs and building masses, vary the structures enough to avoid a stamped group, and add selective architectural details or distinctive structures only after the cluster already reads as one settlement at map scale

## Do
- Start with a compact group of adjacent or overlapping roof forms.
- Give the roof forms enough building body to read as architecture rather than abstract triangles.
- Vary roof, building, and silhouette character within a coherent settlement family.
- Add doors, beams, chimneys, or similar small details selectively after the cluster reads.
- Use a distinctive structure when it helps identify the town or communicate setting character.
- Let cultural or setting character influence architecture when that distinction remains legible at map scale.

## Don't
- Do not fully render every building before the town cluster reads as one symbol.
- Do not repeat one identical house stamp for the entire icon.
- Do not require a fixed building count or mandatory specialty structure.
- Do not let tiny architectural details overpower the settlement silhouette.

## Checklist
- The icon reads as one town at map scale before small details are inspected.
- The buildings vary enough to suggest a settlement without losing visual family resemblance.
- Selective details support identity rather than carrying all recognition by themselves.
- Any cultural or setting-specific architecture remains legible in the compressed symbol.

## Notes
The cartographic move is architectural compression. A town icon needs enough clustered building structure to imply settlement while remaining a single map symbol; exact roof counts, house rectangles, chimneys, and other small features are implementation choices.
