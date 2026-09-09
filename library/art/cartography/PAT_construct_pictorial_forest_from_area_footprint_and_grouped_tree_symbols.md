---
object_id: PAT_construct_pictorial_forest_from_area_footprint_and_grouped_tree_symbols
object_type: pattern
name: Construct Pictorial Forest From Area Footprint And Grouped Tree Symbols
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
- terrain
- forest
- woods
- pictorial-symbols
- area-encoding
cross_links:
- rel: related_to
  target_object_id: PAT_repeat_with_variation_to_balance_coherence_and_interest
confidence: high
references: []
variants:
- variant_id: VAR_encode_wooded_swamp_with_overlapping_canopies_flared_roots_and_water_marks
  variant_name: Encode Wooded Swamp With Overlapping Canopies Flared Roots and Water Marks
  variant_basis: context
  difference_from_foundation: Use the forest grouping system for a wooded wetland, with irregularly overlapping canopy groups, exposed lower trunks that flare into visible root bases, and short water marks around the trees; add sparse hanging vegetation or broken organic texture only when it strengthens the intended swamp character.
  when_to_use: Use when the mapped wetland is tree-dominated and should read as a swamp or flooded woodland rather than a grass-dominated marsh.
  when_not_to_use: Do not use when the wetland is primarily open marsh, when map scale cannot support visible root or canopy structure, or when hanging vegetation would imply a character the setting does not need.
  absorbed_from_object_id: none
- variant_id: VAR_render_top_down_conifer_tree_symbols_with_radial_branch_direction
  variant_name: Render Top-Down Conifer Tree Symbols With Radial Branch Direction
  variant_basis: style
  difference_from_foundation: Use outward-radiating branch direction and a jagged contour that follows that direction so top-down tree symbols read as pine or conifer rather than rounded deciduous canopy masses.
  when_to_use: Use when a map needs top-down conifer or pine tree symbols to communicate a distinct tree family or environmental character.
  when_not_to_use: Do not use for deciduous canopies, when the viewing scale is too small to preserve branch-direction cues, or when a simpler undifferentiated forest symbol family is more readable.
  absorbed_from_object_id: none
- variant_id: VAR_build_layered_forest_with_canopy_ridges_and_partial_treetops
  variant_name: Build Layered Forest With Canopy Ridges and Partial Treetops
  variant_basis: method_sequence
  difference_from_foundation: After the footprint and tree scale are established, build the near edge from complete overlapping trees, close the far edge and interior with partial treetops whose lower portions remain occluded, and bend major interior crown rows into irregular shallow ridges that imply terrain beneath the canopy before scattering smaller crown groups between them.
  when_to_use: Use when an oblique pictorial forest should read as a dense layered canopy while also suggesting hills or rolling ground beneath the trees.
  when_not_to_use: Do not use when the map is strictly top-down, when the output scale cannot preserve partial-crown layering, or when a flatter undifferentiated woodland field is more readable.
  absorbed_from_object_id: none
- variant_id: VAR_exaggerate_tree_symbol_scale_for_recognition_while_preserving_terrain_hierarchy
  variant_name: Exaggerate Tree Symbol Scale for Recognition While Preserving Terrain Hierarchy
  variant_basis: constraint
  difference_from_foundation: Treat individual tree size as pictorial symbol scale rather than literal geographic scale when physically accurate trees would disappear at the final map size; enlarge the tree family only enough to remain recognizable while keeping forests visually subordinate to larger terrain classes such as mountains and keeping equivalent forests within one coherent scale family.
  when_to_use: Use when a regional or similarly compressed pictorial map needs recognizable individual tree symbols that would become unreadable at literal ground scale.
  when_not_to_use: Do not use when literal scale is an explicit requirement, when enlarged trees would compete with larger terrain classes, or when the forest is intentionally encoded as fine texture rather than recognizable tree symbols.
  absorbed_from_object_id: none
---

# Construct Pictorial Forest From Area Footprint And Grouped Tree Symbols

## Pattern Rule
**IF** a map needs a wooded region to read as a geographic area rather than as unrelated individual trees
**THEN** block the forest footprint lightly first, fill that area with a coherent but varied family of tree symbols until the group carries the forest shape, add smaller satellite woodlands where useful, and unify the groups with consistent trunks or directional shading only after the area read works

## Do
- Sketch the general wooded footprint before resolving individual trees.
- Populate that footprint with a recognizable tree-symbol family whose grouping carries the region shape.
- Establish a small set of representative tree symbols at the intended map scale before mass fill, then compare later trees against them so cumulative size drift does not silently change the woodland scale; reuse the same reference family across forests that share a map scale.
- Vary tree silhouettes modestly so the field does not become a mechanical stamp.
- Use smaller satellite woodlands or scattered edge trees when they help extend, punctuate, or soften the transition from the major forest mass into open terrain; vary grouping size and spacing so the falloff does not become a uniform fringe.
- Let alternate tree silhouettes suggest different woodland character locally when the map can support that distinction.
- Add shared trunk or shading treatment after the geographic grouping is clear.

## Don't
- Do not solve individual tree rendering before the forest footprint is placed.
- Do not let every tree become an independent focal object.
- Do not let repeated tree symbols drift progressively larger or smaller merely because each new symbol is judged only against its immediate neighbor.
- Do not require a fixed tree count for small woodland groups.
- Do not assume every tree species needs its own icon language unless the map actually uses that distinction.
- Do not use decorative shading to disguise a forest area that does not read as a coherent region.

## Checklist
- The forest reads first as a geographic area and second as a collection of trees.
- The tree symbols form a coherent family without becoming identical stamps.
- Repeated tree symbols remain within the intended scale family across the woodland and across same-scale forest regions.
- Smaller woodland groups support the larger terrain structure rather than appearing arbitrary, and any softened edge reads as irregular falloff rather than a repeated border.
- Any alternate tree shapes communicate a deliberate local distinction.
- Trunks or shading unify the field without replacing the forest footprint as the primary organizer.

## Notes
Pictorial forest construction separates geographic placement from local foliage symbols. The light footprint owns the region; repeated tree forms encode woodland inside it. Specific tree recipes, fixed group counts, and one-sided shading methods are optional implementations rather than the owner.


`VAR_encode_wooded_swamp_with_overlapping_canopies_flared_roots_and_water_marks` is a wooded-wetland branch. Keep the forest-area grouping logic, but let canopy overlap, flared root bases, and local water marks carry the swamp read before small decorative texture is added. Hanging vegetation can strengthen that character when appropriate, but it is not required for every wooded wetland.

`VAR_render_top_down_conifer_tree_symbols_with_radial_branch_direction` is a top-down conifer branch. Preserve the forest-area grouping logic, but replace cloud-like deciduous canopy edges with outward-radiating branch direction and a jagged contour that carries the conifer read.

`VAR_build_layered_forest_with_canopy_ridges_and_partial_treetops` is an oblique layered-canopy branch. Keep full overlapping tree forms where the forest meets the viewer, let farther rows collapse into partial crowns, and curve the major interior crown rows into irregular ridges when the canopy should reveal rolling terrain beneath it. Straight, evenly spaced crown rows flatten the land and expose the construction; use the layered route only when the map scale preserves those depth cues.
`VAR_exaggerate_tree_symbol_scale_for_recognition_while_preserving_terrain_hierarchy` is a symbolic-scale branch for compressed pictorial maps. If literal tree size would vanish at output scale, enlarge the tree family until it reads, but judge that enlargement against the map's other terrain classes rather than against real-world dimensions. Keep forests subordinate to larger terrain features, and use texture instead when the map intentionally preserves literal scale.
