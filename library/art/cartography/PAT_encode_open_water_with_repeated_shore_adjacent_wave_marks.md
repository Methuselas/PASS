---
object_id: PAT_encode_open_water_with_repeated_shore_adjacent_wave_marks
object_type: pattern
name: Encode Open Water With Repeated Shore-Adjacent Wave Marks
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
- water
- ocean
- lake
- wave-marks
- texture
- encoding
cross_links:
- rel: related_to
  target_object_id: PAT_reinforce_coastline_with_simplified_offset_shoreline_echoes
- rel: related_to
  target_object_id: PAT_repeat_with_variation_to_balance_coherence_and_interest
confidence: high
references: []
variants:
- variant_id: VAR_wrap_water_marks_through_and_behind_coastal_forms
  variant_name: Wrap Water Marks Through and Behind Coastal Forms
  variant_basis: context
  difference_from_foundation: When the water texture meets raised rocks, projecting cliffs, arches, or similar coastal forms, keep the water plane continuous by drawing only the visible wave-mark segments, allowing the forms to occlude hidden segments and continuing marks through visible openings where water remains exposed.
  when_to_use: Use when repeated water marks interact with pictorial coastal forms whose overlap or openings need to read in depth.
  when_not_to_use: Do not force the treatment on tiny symbols or flat regional maps where the extra occlusion detail would become clutter or imply unsupported three-dimensional structure.
  absorbed_from_object_id: none
- variant_id: VAR_signal_moving_surface_object_with_displaced_water_marks
  variant_name: Signal Moving Surface Object With Displaced Water Marks
  variant_basis: context
  difference_from_foundation: When a vessel or other surface object is moving through stylized water, let the local water-mark field react to that motion by interrupting or redirecting marks around the contact area and adding a compact wake, prow spray, or similar displaced-water cue aligned with travel.
  when_to_use: Use when the map illustration needs a moving surface object to read as interacting dynamically with the water rather than resting on top of a static texture.
  when_not_to_use: Do not add wake or spray to stationary objects, or when the map scale is too small for the cue to remain legible without clutter.
  absorbed_from_object_id: none
---

# Encode Open Water With Repeated Shore-Adjacent Wave Marks

## Pattern Rule
**IF** an ocean or large-lake area needs line-based decoration that makes the water field more clearly identifiable
**THEN** extend short, closely spaced, generally horizontal wave-like marks outward from the shore treatment, keeping direction and spacing coherent enough to read as one water field while allowing modest local variation

## Do
- Begin the water marks adjacent to the shoreline treatment so their relationship to the water area is clear.
- Use short, generally horizontal wave-like marks as a repeated family.
- Keep spacing, direction, and length coherent enough that the marks merge perceptually into one water texture.
- Allow modest variation so the field does not become a dead mechanical stripe pattern.
- Use the same method on large lakes when line decoration helps identify the water area.

## Don't
- Do not let the marks vary so widely that they stop reading as one water texture.
- Do not make the wave field visually stronger than the coastline and mapped features it supports.
- Do not require fixed mark lengths, pencil grades, or exact intervals.
- Do not treat generic hatching as equivalent when it no longer communicates a water field.

## Checklist
- The repeated marks read collectively as water rather than unrelated strokes.
- Their overall direction and spacing are coherent across the field.
- Local variation prevents obvious mechanical repetition without breaking the family.
- The water texture remains subordinate to the geographic edges and symbols it supports.

## Notes
This pattern owns semantic water texture: a repeated line field whose family resemblance makes open water legible. Generic repetition principles still govern rhythm, but the cartographic move is what those repeated marks mean on the map.

`VAR_wrap_water_marks_through_and_behind_coastal_forms` applies the same water texture when raised or pierced coastal forms interrupt the field. Keep the wave marks continuous only where the water is visible: let rocks or cliff faces hide covered segments, and resume the marks through openings or beyond the occluder so the water plane remains spatially coherent.

`VAR_signal_moving_surface_object_with_displaced_water_marks` changes the local water texture when a vessel or other surface object is actively moving. Interrupt or redirect nearby marks and use a small wake, prow spray, or comparable displacement cue aligned with travel so the object reads as moving through the water rather than sitting above a static pattern.
