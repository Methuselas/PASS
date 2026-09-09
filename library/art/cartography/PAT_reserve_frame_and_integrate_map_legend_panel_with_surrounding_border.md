---
object_id: PAT_reserve_frame_and_integrate_map_legend_panel_with_surrounding_border
object_type: pattern
name: Reserve Frame and Integrate Map Information Panel With Surrounding Border
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
- legend
- information-panel
- border
- framing
cross_links: []
confidence: high
references: []
variants:
- variant_id: VAR_use_compact_subordinate_information_box
  variant_name: Use Compact Subordinate Information Box
  variant_basis: emphasis
  difference_from_foundation: Use a smaller, lower-emphasis framed panel for secondary information or decorative text treatment that complements the primary legend, border, or corners without competing with them.
  when_to_use: Use when the map needs a secondary text element or compact informational accent in addition to the primary legend.
  when_not_to_use: Do not use when the secondary panel would compete with the legend or fragment information that belongs together.
  absorbed_from_object_id: none
---

# Reserve Frame and Integrate Map Information Panel With Surrounding Border

## Pattern Rule
**IF** a map needs a dedicated legend or other framed information panel
**THEN** reserve its footprint deliberately, establish the basic frame before adding ornament, and integrate the panel with nearby border or perimeter art when those elements visually interact

## Do
- Choose the panel location before finalizing its decorative frame.
- Rough in the footprint so the panel occupies a controlled area of the composition.
- Establish the clear container first, then add decorative edge or corner treatment.
- When the panel sits against existing border ornament, make the transition between them intentional rather than leaving a floating unrelated box.
- Keep secondary information boxes smaller and quieter than the primary legend when both appear.

## Don't
- Do not force the panel into a corner or lower-center position when another placement serves the composition better.
- Do not decorate the frame before confirming the panel has enough usable interior area.
- Do not make nearby perimeter ornament collide with the panel as if the two were designed independently.
- Do not give a secondary information box the same emphasis as the primary legend when the hierarchy should be clear.

## Checklist
- The panel has a deliberate footprint and clear frame.
- Interior information has enough usable space to remain legible.
- Decorative treatment follows the container rather than obscuring it.
- Nearby border or perimeter art connects cleanly when the two elements meet.
- Secondary information boxes remain subordinate to the primary legend.

## Notes
This pattern owns the information-panel container, not the selection of legend contents. The variant `VAR_use_compact_subordinate_information_box` uses the same framing logic for a smaller, lower-emphasis panel that complements the primary legend or surrounding ornament.
