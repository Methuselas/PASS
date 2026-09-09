---
object_id: PAT_encode_repeatable_special_location_categories_with_compact_illustrative_glyphs
object_type: pattern
name: Encode Repeatable Special-Location Categories With Compact Illustrative Glyphs
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
- icons
- locations
- glyphs
- semantic-symbols
- context
cross_links: []
confidence: high
references: []
variants:
- variant_id: VAR_encode_location_state_with_secondary_icon_cue
  variant_name: Encode Location State With Secondary Icon Cue
  variant_basis: context
  difference_from_foundation: Keep the category-defining base glyph stable while adding, removing, or altering one secondary cue to distinguish a meaningful state of that same location type.
  when_to_use: Use when readers need to distinguish states of one location category without learning unrelated symbols.
  when_not_to_use: Do not add a state cue when it makes the base category ambiguous or the state is not important to the map.
  absorbed_from_object_id: none
---

# Encode Repeatable Special-Location Categories With Compact Illustrative Glyphs

## Pattern Rule
**IF** repeated non-settlement points of interest need category recognition without a bespoke illustration for every location
**THEN** encode each category with a compact pictorial glyph built from a strong primary form and a small number of recognizable cues, repeat the grammar consistently, and place context-dependent glyphs where direct feature alignment or surrounding spatial context reinforces their meaning

## Do
- Reduce each category to a primary form that survives at map scale.
- Add only the cues needed to distinguish the category.
- Repeat equivalent glyphs consistently enough that readers can learn the symbol family.
- Align a glyph directly with a mapped feature when its meaning depends on physical attachment.
- When meaning depends on broader context, place the glyph where nearby geography, a route network, or relative remoteness reinforces the intended reading.
- Allow local or cultural variation when the category remains recognizable.

## Don't
- Do not turn repeatable categories into unique bespoke landmarks unless individual site identity matters.
- Do not add so many cues that the glyph loses compact readability.
- Do not place a context-dependent glyph as arbitrary decoration when its position is part of the meaning.
- Do not let state cues replace the base category identity.

## Checklist
- The glyph category is recognizable at map scale.
- Equivalent instances share a learned visual grammar.
- Context-dependent glyphs align with or occupy spatial contexts that support their meaning.
- Local variation does not erase category identity.
- State changes remain subordinate to the base glyph.

## Notes
The variant `VAR_encode_location_state_with_secondary_icon_cue` preserves the category-defining base glyph while changing one secondary cue to communicate a meaningful condition or state of the same location class. Use it only when that state matters and remains legible.
