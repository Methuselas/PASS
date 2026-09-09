---
object_id: PAT_refine_coastline_from_broad_framework_to_clear_boundary
object_type: pattern
name: Refine Coastline From Broad Framework to Clear Boundary
library_path:
- art
- cartography
stage_binding: 1 skeleton
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: domain
foundation_object_id: none
tags:
- cartography
- coastline
- landmass
- islands
- lakes
- bays
- inlets
- refinement
cross_links:
- rel: related_to
  target_object_id: PAT_alternate_free_search_and_controlled_refinement
- rel: related_to
  target_object_id: PAT_select_and_shape_contour_for_expressive_meaning
- rel: related_to
  target_object_id: PAT_plan_map_land_water_framework_from_geographic_intent
confidence: high
references: []
variants: []
---

# Refine Coastline From Broad Framework to Clear Boundary

## Pattern Rule
**IF** a map's broad landmass framework reads at the whole-map scale but its coastline is still generic or unresolved
**THEN** refine the outer boundary from the simple large shape into smaller coastline variation, freely revise the first contour, add islands and inland water where they fit the framework, then strengthen the accepted land-water edges and remove obsolete construction

## Do
- Begin from a simple, light, erasable landmass outline rather than trying to solve a finished coastline in the first pass.
- Rework the rough contour instead of tracing it mechanically; add, remove, or reshape shoreline passages whenever the refined map improves.
- Introduce smaller-scale coastline variation with islands, island groups, bays, inlets, and similar interruptions where they fit the framework; add lakes as internal water shapes where they belong.
- Vary feature shapes and sizes instead of repeating one identical coastline motif throughout the map.
- Keep the land-sea division visually clear as the contour becomes more intricate.
- After the coastline is resolved, make the accepted boundary the committed line and erase or remove the superseded framework.

## Don't
- Do not preserve the first rough contour merely because it was drawn first.
- Do not treat every island as requiring a cluster, every lake as requiring one particular shape, or any demonstrated feature as a geographic law.
- Do not add local irregularity until the broad landmass placement is stable enough to support it.
- Do not leave the final coastline visually ambiguous against the water because construction and committed edges carry equal weight.
- Do not keep obsolete sketch lines after they have been replaced by the accepted boundary.

## Checklist
- The coastline grew from a readable broad framework rather than from unplanned local detail.
- The refined boundary departs from the first outline where a better coastline required it.
- Coastline features vary the outer boundary, and any lakes read as deliberate internal water shapes, without becoming mandatory repeated formulas.
- Land and water remain immediately distinguishable after refinement.
- Only the accepted coastline remains visually authoritative when the construction pass is cleaned up.

## Notes
The useful sequence is broad shape before local variation and final commitment. A pencil implementation can move from a light construction line to progressively darker selected contours, but the transferable mechanism is commitment state rather than a required pencil grade. Islands, bays, and inlets are a vocabulary for breaking a generic outer boundary into a more specific coastline, while lakes create internal land-water boundaries. They are options to fit the map, not a checklist every landmass must contain.
