---
object_id: PAT_establish_rectangular_map_neatline_before_building_border_treatment
object_type: pattern
name: Establish Rectangular Map Neatline Before Building Border Treatment
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
- neatline
- border
- framing
- perimeter
cross_links: []
confidence: high
references: []
variants: []
---

# Establish Rectangular Map Neatline Before Building Border Treatment

## Pattern Rule
**IF** a rectangular map needs a defined drawing field and an outer border treatment
**THEN** establish the neatline as the hard perimeter of the geographic drawing first, contain map content inside it, and build any parallel or segmented border treatment outside that boundary

## Do
- Set the neatline before adding decorative border structure.
- Keep geographic drawing, symbols, and other map-field marks contained by the inner perimeter unless a later element deliberately crosses it.
- Build border lines as a separate framing system around the neatline rather than treating them as part of the mapped geography.
- When using a repeated segmented band, divide the run evenly before applying alternating or repeated fills.
- Close the outer framing treatment cleanly so the border reads as one perimeter system.

## Don't
- Do not let the border treatment become ambiguous with geographic boundaries inside the map.
- Do not place repeated border segments by eye when uneven subdivision would make the frame visibly drift.
- Do not assume a checker or ruler-like border is a quantitative distance scale unless the map has an actual scale system that defines it.

## Checklist
- The geographic drawing has one clear rectangular inner perimeter.
- Map-field content reads as contained by the neatline.
- Border lines or bands read as framing outside the map field.
- Repeated border segments are regular when a segmented treatment is used.
- The completed border forms a visually closed perimeter.

## Notes
The neatline owns containment; the surrounding border owns framing. A repeated checker or alternating band can decorate the frame, but its visual segmentation is not by itself evidence of a calibrated map scale.
