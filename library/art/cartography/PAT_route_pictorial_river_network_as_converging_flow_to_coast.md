---
object_id: PAT_route_pictorial_river_network_as_converging_flow_to_coast
object_type: pattern
name: Route Pictorial River Network As Converging Flow to Coast
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
- hydrography
- rivers
- tributaries
- delta
- topology
cross_links:
- rel: related_to
  target_object_id: PAT_refine_coastline_from_broad_framework_to_clear_boundary
confidence: high
references: []
variants: []
---

# Route Pictorial River Network As Converging Flow to Coast

## Pattern Rule
**IF** a pictorial regional map needs a river network whose route and connections are still unresolved
**THEN** route a light main river from plausible source terrain or a lake toward the coast, connect smaller tributaries so they converge into the upper main channel, let the course bend through the terrain, open the mouth through the coastline, and reserve outward branching near the coast for a deliberate delta

## Do
- Place the main river lightly enough to revise before committing its final marks.
- Begin from mountain, hill, or lake source terrain when that fits the mapped region.
- Add smaller tributaries from surrounding terrain so they merge into the main river upstream.
- Use curved courses where they help the river move through the terrain rather than reading as rigid connectors.
- Carry the river through the coastline into its receiving water instead of stopping the line against the shore.
- Use downstream branching near the mouth deliberately when depicting a delta.

## Don't
- Do not make ordinary tributaries repeatedly split and reconnect as if every branch were a delta.
- Do not force every river to begin in exactly the same terrain type.
- Do not stop a river at the coastline without connecting it into the receiving water.
- Do not treat a fixed tributary count or amount of curvature as a geographic law.

## Checklist
- A reader can follow the network from smaller upstream branches into a main downstream channel.
- Tributaries converge into the main river rather than forming arbitrary loops.
- The main river reaches and opens into the coast.
- Any branching at the mouth reads as a deliberate delta rather than accidental topology.
- The route works with the surrounding terrain and remains readable at map scale.

## Notes
This pattern owns the connectivity of the river network, not its rendered width. The useful topology is a main downstream channel fed by converging tributaries, with a delta as a distinct mouth condition where the flow may branch before meeting the coast.
