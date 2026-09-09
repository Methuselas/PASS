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
variants: []
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
