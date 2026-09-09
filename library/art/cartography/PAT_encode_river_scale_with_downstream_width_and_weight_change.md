---
object_id: PAT_encode_river_scale_with_downstream_width_and_weight_change
object_type: pattern
name: Encode River Scale With Downstream Width and Weight Change
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
- hydrography
- rivers
- line-weight
- scale
- encoding
cross_links:
- rel: related_to
  target_object_id: PAT_route_pictorial_river_network_as_converging_flow_to_coast
confidence: high
references: []
variants: []
---

# Encode River Scale With Downstream Width and Weight Change

## Pattern Rule
**IF** a mapped river route is established but its graphic treatment does not yet communicate the difference between smaller headwaters and a larger lower river
**THEN** keep headwaters and tributaries thinner or lighter while broadening or strengthening the main channel downstream so the mark system encodes increasing river scale along its course

## Do
- Keep upstream headwaters and minor tributaries visually lighter or narrower than the lower main river.
- Increase the main channel width or graphic weight downstream as the depicted river becomes larger.
- Judge the change along the full watercourse so the hierarchy reads as one system.
- Keep tributary treatment subordinate enough that the main channel remains identifiable.

## Don't
- Do not use identical width and weight everywhere when the map needs river scale to change visibly downstream.
- Do not make tributaries heavier than the main channel they feed without a specific reason.
- Do not turn a demonstrated pencil-pressure sequence into a mandatory medium recipe.
- Do not use downstream graphic weight as a substitute for resolving the river network itself.

## Checklist
- Headwaters and tributaries read as smaller than the lower main river.
- The main channel becomes visibly broader or stronger downstream.
- The river hierarchy remains readable across the whole network.
- The graphic change communicates scale rather than an unrelated lighting or contour effect.

## Notes
Width and weight can function semantically in cartography. Here they encode river scale along the course, which is a different job from generic contour emphasis or lighting-based line variation.
