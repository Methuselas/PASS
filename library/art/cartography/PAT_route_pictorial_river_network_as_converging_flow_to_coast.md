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
variants:
- variant_id: VAR_construct_delta_as_hierarchical_distributary_island_network
  variant_name: Construct Delta as Hierarchical Distributary-Island Network
  variant_basis: context
  difference_from_foundation: "At a deliberate delta, replace ordinary downstream convergence near the mouth with a bounded distributary field: establish the delta footprint, split the lower river into a few major channels, add smaller connecting or subdividing channels, and treat the remaining negative spaces as island or sediment masses."
  when_to_use: "Use when a river reaches a mouth where a delta is intended, especially where the outlet is inset or otherwise protected enough for deposited material to plausibly accumulate."
  when_not_to_use: "Do not apply delta branching to ordinary river courses, strongly exposed mouths where the map is not depicting deposition, or at scales where the distributary network would collapse into clutter."
  absorbed_from_object_id: none
- variant_id: VAR_route_low_gradient_river_as_alternating_meanders_with_cutoff_potential
  variant_name: Route Low-Gradient River as Alternating Meanders With Cutoff Potential
  variant_basis: context
  difference_from_foundation: "Across relatively flat or low-gradient terrain, replace a merely generic curved course with an alternating meander sequence whose bends can be read as one evolving channel: the outside of a bend is the erosional/steeper side when bank form is shown, the inside is the depositional/gentler side, and an extreme loop may be bypassed by a shorter cutoff that leaves the abandoned bend as an oxbow-like water body."
  when_to_use: "Use when a natural river crosses relatively unconstrained low-gradient terrain and needs believable lateral wandering rather than a rigid straight course or terrain-forced mountain bends."
  when_not_to_use: "Do not force repeated meanders through strongly constraining terrain, engineered channels, or maps whose scale cannot support the local bend structure; an extreme loop does not require a cutoff unless that landform is intended."
  absorbed_from_object_id: none
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

`VAR_construct_delta_as_hierarchical_distributary_island_network` makes that mouth exception explicit. Establish the broad delta footprint first, lay in a few major distributaries, then add smaller channels so the network reads hierarchically; the land masses are the negative spaces left between those channels. Add marsh or edge texture only after the distributary topology is legible.

`VAR_route_low_gradient_river_as_alternating_meanders_with_cutoff_potential` owns the low-gradient exception where the river's own channel processes can generate curvature even without obvious terrain obstacles. Build a linked sequence of bends rather than arbitrary side-to-side noise. When local bank form is visible, the outer bend can read steeper/deeper and the inner bend gentler/shallower; if a loop becomes extreme, a shorter cutoff may become the active channel while the old loop remains as an oxbow-like water body.
