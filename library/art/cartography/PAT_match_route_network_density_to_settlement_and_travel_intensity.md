---
object_id: PAT_match_route_network_density_to_settlement_and_travel_intensity
object_type: pattern
name: Match Route Network Density to Settlement and Travel Intensity
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
- routes
- roads
- networks
- density
- travel
cross_links: []
confidence: high
references: []
variants: []
---

# Match Route Network Density to Settlement and Travel Intensity

## Pattern Rule
**IF** a regional map needs a route network whose overall connectivity should communicate how settled and traveled the territory is
**THEN** set the amount of route connectivity to match the intended settlement and travel intensity, using denser networks for heavily settled or traveled areas and fewer connections for wilder, isolated, or less-traveled territory

## Do
- Judge the route network as a whole rather than one connection at a time.
- Use route abundance to support the intended regional character.
- Leave some settlements less connected when isolation or low travel is part of the map logic.

## Don't
- Do not give every settlement equivalent access in every direction by default.
- Do not make a wilderness network as dense as a major settled corridor without an intentional reason.
- Do not use connectivity density that contradicts the intended travel pattern.

## Checklist
- The overall network density matches the region’s intended travel intensity.
- More connected areas read as more traveled or settled.
- Sparse areas retain meaningful isolation.
- The network remains coherent when individual route styles are ignored.

## Notes
Route density is a separate information layer from settlement density: the same settlements can imply very different movement patterns depending on how strongly they are connected.
