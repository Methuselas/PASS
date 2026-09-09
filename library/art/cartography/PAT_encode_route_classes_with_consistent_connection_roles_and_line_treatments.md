---
object_id: PAT_encode_route_classes_with_consistent_connection_roles_and_line_treatments
object_type: pattern
name: Encode Route Classes With Consistent Connection Roles and Line Treatments
library_path:
- art
- cartography
stage_binding: 3 rough
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: domain
foundation_object_id: none
tags:
- cartography
- routes
- roads
- paths
- sea-routes
- line-language
cross_links: []
confidence: high
references: []
variants: []
---

# Encode Route Classes With Consistent Connection Roles and Line Treatments

## Pattern Rule
**IF** a map needs more than one route class to distinguish different transportation roles
**THEN** define each route class by both the kind of connection it represents and a repeatable line treatment, then apply that vocabulary consistently so route type can be recognized at a glance

## Do
- Decide which route classes the map actually needs.
- Associate major links, ordinary roads, minor paths, and water routes with distinct connection roles when those classes are useful.
- Use consistent paired, solid, broken, dotted, weight, or spacing treatments to distinguish classes.
- Keep the vocabulary small enough to learn.

## Don't
- Do not change line treatment arbitrarily within one route class.
- Do not rely on line style alone if the connection role contradicts the class meaning.
- Do not multiply route classes beyond what the map needs.

## Checklist
- Each route class has one understandable connection role.
- Equivalent route classes repeat the same visual convention.
- Different route classes remain distinguishable without reading every label.
- The route vocabulary does not overwhelm other map information.

## Notes
Route lines encode connection rather than separation. Their visual grammar should be learned as a transportation system, not confused with political boundary lines.
