---
object_id: PAT_encode_settlement_class_with_relative_icon_scale_and_shape_family
object_type: pattern
name: Encode Settlement Class With Relative Icon Scale and Shape Family
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
- settlements
- icons
- hierarchy
- politics
- symbol-language
cross_links: []
confidence: high
references: []
variants:
- variant_id: VAR_encode_political_affiliation_with_shared_settlement_icon_family
  variant_name: Encode Political Affiliation With Shared Settlement Icon Family
  variant_basis: context
  difference_from_foundation: Preserve settlement-class cues while adding a shared color or compatible form family across locations that belong to the same political group.
  when_to_use: Use when one map contains multiple political groups and affiliation should be visible directly in the settlement symbol system.
  when_not_to_use: Do not let affiliation treatment erase the capital, city, town, village, or fortification distinctions the map still needs.
  absorbed_from_object_id: none
---

# Encode Settlement Class With Relative Icon Scale and Shape Family

## Pattern Rule
**IF** simplified settlement symbols are being used and the map needs to distinguish settlement or fortification classes
**THEN** assign each required class a repeatable combination of relative scale, base shape, silhouette, or internal marks so ordered rank and categorical differences remain legible

## Do
- Use relative size when classes form an ordered hierarchy.
- Use shape or internal marks when classes differ by category rather than only rank.
- Keep equivalent classes consistent enough to become a learned symbol family.
- Preserve the class system when adding a second affiliation layer.

## Don't
- Do not make every class an unrelated symbol with no shared grammar.
- Do not use size alone when two categories are not meaningfully ranked.
- Do not let political affiliation styling erase settlement-class distinctions.

## Checklist
- Settlement classes remain identifiable without pictorial architecture.
- Higher-ranked classes are visibly stronger when rank is encoded.
- Categorical differences have repeatable visual cues.
- The vocabulary remains learnable across the map.

## Notes
The variant `VAR_encode_political_affiliation_with_shared_settlement_icon_family` adds a second semantic layer: settlements from the same political group may share color or a compatible form treatment while the settlement-class grammar remains intact.
