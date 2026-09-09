---
object_id: PAT_place_point_location_labels_as_straight_icon_associated_text
object_type: pattern
name: Place Point-Location Labels As Straight Icon-Associated Text
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
- typography
- labels
- point-locations
- icons
- hierarchy
cross_links:
- rel: related_to
  target_object_id: PAT_choose_map_lettering_style_to_support_culture_tone_and_legibility
confidence: high
references: []
variants:
- variant_id: VAR_emphasize_high_importance_location_label_with_size_or_caps
  variant_name: Emphasize High-Importance Location Label With Size or Caps
  variant_basis: emphasis
  difference_from_foundation: Increase label size or use uppercase treatment so a high-importance location outranks ordinary point-location labels while remaining part of the same label system.
  when_to_use: Use when a capital, citadel, or other deliberately important point location needs stronger textual emphasis than ordinary locations.
  when_not_to_use: Do not apply the stronger treatment so broadly that ordinary and high-priority locations lose their distinction.
  absorbed_from_object_id: none
---

# Place Point-Location Labels As Straight Icon-Associated Text

## Pattern Rule
**IF** an icon-based town, city, fortification, or other point location needs a text label on a map
**THEN** place the label on a straight line close enough to its icon for ownership to be unambiguous, reserve or clear enough surrounding space to keep the text readable, and use a sufficiently consistent treatment that point labels read as one semantic class

## Do
- Keep the label straight rather than curving it around the point icon.
- Place the text close enough to the icon that the reader does not have to guess which feature it names.
- Reserve or clear label space before lettering when nearby terrain or symbols would interfere with the text.
- Keep equivalent point-location labels consistent enough in alignment and treatment to read as one class.
- Preserve the chosen lettering style while adapting the exact label placement to the available map space.

## Don't
- Do not curve point-location labels into the treatment used for larger geographic areas.
- Do not let terrain, icons, or other map marks pass through the label until its ownership or readability becomes ambiguous.
- Do not place a label so far from its icon that another nearby feature becomes a plausible owner.
- Do not force exact uniformity when a local placement adjustment is needed to keep the label clear.

## Checklist
- Each point label is straight.
- Each label has one obvious associated icon.
- Important terrain and symbols do not obscure the text.
- Equivalent point labels share enough treatment to read as one semantic class.
- Local placement variation does not create ambiguity about what the label names.

## Notes
Straight alignment and close icon association let label geometry communicate that the text names a discrete point location. The variant `VAR_emphasize_high_importance_location_label_with_size_or_caps` increases size or uses uppercase treatment when one location must outrank ordinary point labels; use that emphasis sparingly enough that the hierarchy remains visible.
