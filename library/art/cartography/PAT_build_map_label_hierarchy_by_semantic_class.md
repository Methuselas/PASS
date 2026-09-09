---
object_id: PAT_build_map_label_hierarchy_by_semantic_class
object_type: pattern
name: Build Map Label Hierarchy by Semantic Class
library_path:
- art
- cartography
stage_binding: 0 design
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: domain
foundation_object_id: none
tags:
- cartography
- typography
- labels
- hierarchy
- semantic-classes
cross_links: []
confidence: high
references: []
variants: []
---

# Build Map Label Hierarchy by Semantic Class

## Pattern Rule
**IF** a map contains multiple label classes that differ in geographic scope or reading priority
**THEN** assign size, spacing, capitalization treatment, path geometry, and visual strength by semantic class so labels communicate both what kind of feature they name and how strongly they should compete for attention

## Do
- Define label classes before styling individual names.
- Use geometry consistently: point labels, linear labels, and area labels should retain their distinct placement logic.
- Separate geographic extent from reading priority; a broad regional name can occupy more area while remaining quieter than a smaller high-priority point label.
- Repeat class treatments consistently enough that readers can learn the hierarchy.

## Don't
- Do not style every label independently.
- Do not assume larger geographic extent must always mean stronger visual emphasis.
- Do not use so many class treatments that the hierarchy becomes difficult to learn.

## Checklist
- Equivalent semantic classes share recognizable treatment.
- Point, linear, and area labels remain distinguishable.
- High-priority names attract attention without making lower-priority geography unreadable.
- Extent and emphasis are controlled as separate variables.

## Notes
A label system carries more than text content. Repeated class treatment lets typography communicate feature type, geographic scope, and reading priority across the map.
