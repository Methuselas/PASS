---
object_id: PAT_construct_fortified_pictorial_city_icon_from_perimeter_and_layered_interior
object_type: pattern
name: Construct Fortified Pictorial City Icon From Perimeter And Layered Interior
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
- cities
- fortification
- icons
- architecture
cross_links:
- rel: related_to
  target_object_id: PAT_construct_pictorial_town_icon_from_compact_building_cluster
- rel: related_to
  target_object_id: PAT_plan_town_distribution_from_settlement_support_and_regional_density
confidence: high
references: []
variants: []
---

# Construct Fortified Pictorial City Icon From Perimeter And Layered Interior

## Pattern Rule
**IF** a map needs a pictorial icon for a fortified city rather than a smaller town cluster
**THEN** establish a connected wall-and-tower perimeter as the dominant city silhouette, layer roofs and building masses behind or above it to communicate interior density, and add distinctive site- or function-driven structures selectively after the fortified city already reads

## Do
- Build the fortified perimeter before resolving the interior building field.
- Use connected walls and towers to establish the city-scale silhouette.
- Layer roofs and building masses behind or above that perimeter to suggest greater internal density than a town icon.
- Add distinctive structures selectively when site or function differentiates the city.
- Use features such as docks, bridges, or prominent civic or sacred architecture when they fit the city being depicted.

## Don't
- Do not assume every city in every map tradition must be walled; this pattern is for the fortified case.
- Do not let interior building detail erase the wall-and-tower silhouette that distinguishes the fortified city.
- Do not require a fixed city-to-town size ratio or a fixed number of towers.
- Do not add specialty structures merely because an example used them.

## Checklist
- The fortified perimeter reads before individual interior buildings.
- The interior mass communicates greater density without destroying the city silhouette.
- Distinctive structures correspond to site or function rather than arbitrary decoration.
- The icon remains readable as one city symbol at map scale.

## Notes
This owner is intentionally scoped to fortified pictorial cities. The durable sequence is perimeter first, interior density second, and selective differentiation last. A non-fortified city would need a different source-grounded route rather than silently removing the defining constraint.
