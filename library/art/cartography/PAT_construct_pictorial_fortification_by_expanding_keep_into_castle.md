---
object_id: PAT_construct_pictorial_fortification_by_expanding_keep_into_castle
object_type: pattern
name: Construct Pictorial Fortification By Expanding Keep Into Castle
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
- fortifications
- castles
- keeps
- icons
- architecture
cross_links:
- rel: related_to
  target_object_id: PAT_site_fortifications_by_defensive_role_and_protected_feature
- rel: related_to
  target_object_id: PAT_construct_fortified_pictorial_city_icon_from_perimeter_and_layered_interior
confidence: high
references: []
variants: []
---

# Construct Pictorial Fortification By Expanding Keep Into Castle

## Pattern Rule
**IF** a pictorial map needs a scalable fortification symbol that can represent a small holdfast or expand into a larger castle
**THEN** use a single tower or keep as the smallest complete strongpoint, stop there when that scale is sufficient, or expand it with connected walls and additional towers, then a dominant keep and selective details when a larger fortification is required

## Do
- Make the initial tower or keep readable as a complete small fortification.
- Stop at the keep when a small holdfast is sufficient for the map.
- For a larger castle, grow the same symbol grammar with connected defensive walls and additional towers.
- Introduce a larger dominant keep when the expanded fortification needs a stronger internal hierarchy.
- Add flags, windows, small structures, or other detail selectively after the fortification scale reads.

## Don't
- Do not require every fortification to use the largest castle construction.
- Do not make exact tower counts or proportions into rank rules.
- Do not require a closed enclosure when connected defensive mass already communicates the intended fortification.
- Do not let decorative details carry the size distinction that should already read from the fortification structure.

## Checklist
- A single keep can stand as a complete small strongpoint.
- Larger fortifications expand through connected defensive mass rather than an unrelated icon grammar.
- The dominant keep and surrounding walls or towers create a clear size hierarchy when used.
- The icon remains readable at map scale before small embellishments are inspected.

## Notes
The reusable mechanism is nested complexity. A keep is already a valid fortification symbol; additional walls, towers, and a dominant keep let the same pictorial grammar scale upward instead of requiring a separate vocabulary for each rank.
