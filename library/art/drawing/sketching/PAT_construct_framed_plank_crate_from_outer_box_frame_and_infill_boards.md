---
object_id: PAT_construct_framed_plank_crate_from_outer_box_frame_and_infill_boards
object_type: pattern
name: Construct Framed Plank Crate From Outer Box, Frame, and Infill Boards
library_path:
- art
- drawing
- sketching
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: domain
foundation_object_id: none
tags:
- prop
- crate
- wood
- plank
- construction
- interior-map
- top-down
cross_links:
- rel: related_to
  target_object_id: PAT_block_complex_objects_with_perspective_boxes
- rel: related_to
  target_object_id: PAT_repeat_with_variation_to_balance_coherence_and_interest
- rel: related_to
  target_object_id: PAT_render_material_from_optical_response
confidence: high
references: []
variants: []
---

# Construct Framed Plank Crate From Outer Box, Frame, and Infill Boards

## Pattern Rule
**IF** a wooden crate or similar framed plank container needs to read clearly from a simplified drawing or map view
**THEN** establish the overall box shape first, build a stronger perimeter frame and any major cross-braces over that shape, and fill the remaining interior with narrower subordinate boards before adding surface texture or finish
**ELSE** use a simpler unframed box treatment when the plank-and-brace construction is not important to recognition.

## Do
- Set the crate's overall footprint and scale before dividing it into boards.
- Build the perimeter rails and major cross-pieces as the dominant structural layer so the crate reads before the infill is added.
- Keep the interior boards narrower or visually subordinate to the frame so the two construction roles remain distinct.
- Let selected frame ends or corners project slightly beyond neighboring boards when that overlap helps communicate stacked construction and depth.
- Add grain, knots, stipple, color variation, shadow, and highlights only after the outer box, frame, and infill relationships are already legible.
- When several crates appear together, preserve the same construction family while varying size, proportion, orientation, or brace arrangement only as much as the scene's order or irregularity requires.

## Don't
- Do not begin with wood grain or knots before the crate's box and frame structure are established.
- Do not make every board equally dominant if the frame is supposed to read as a stronger enclosing layer.
- Do not add so many narrow boards or texture marks that the object stops reading at its intended final scale.
- Do not force random protrusions or crookedness onto a scene that is meant to look carefully standardized or organized.

## Checklist
- The overall box shape reads before texture is considered.
- The perimeter/frame boards are distinguishable from the narrower infill boards.
- Major cross-bracing, when present, reinforces the crate rather than becoming unrelated decoration.
- Small overlaps or protruding ends add depth without breaking the basic box footprint.
- The crate remains recognizable when grain, knots, color, shadows, and highlights are ignored.
- Detail density survives the intended final viewing scale.

## Notes
A crate reads efficiently when its construction hierarchy is solved before its material surface. The broad box establishes footprint, the heavier frame and brace system explains how the object is assembled, and narrower boards fill the remaining field. Surface marks and lighting then describe wood and depth instead of trying to invent structure after the fact.
