---
object_id: PAT_propagate_world_assumptions_along_actual_dependencies
object_type: pattern
name: Propagate World Assumptions Along Actual Dependencies
library_path:
- game-design
- worldbuilding
stage_binding: 0 design
lane_fit: both
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- worldbuilding
- causality
- dependencies
- consequences
cross_links:
- rel: related_to
  target_object_id: PAT_spend_worldbuilding_detail_where_it_changes_play
- rel: related_to
  target_object_id: PAT_translate_genre_into_play_requirements
reference:
  source_title: Designing TTRPGs For Dummies
  author: Martin Buinicki
confidence: high
references: []
variants:
  - variant_id: game_design_worldbuilding_variant_derive_nonhuman_species_through_ecological_and_cultural_causality
    variant_name: Derive Nonhuman Species through Ecological and Cultural Causality
    variant_basis: method_sequence
    difference_from_foundation: For an intelligent nonhuman species, start from the role or interaction the species must support, then work backward through habitat, ecological niche, survival pressures, the function intelligence serves, and culture so a small number of visible abilities, needs, constraints, and social expectations share one causal foundation.
    when_to_use: A recurring or first-contact species needs to feel meaningfully nonhuman while remaining coherent enough that players can investigate, predict, negotiate with, accommodate, or exploit its traits.
    when_not_to_use: The species appears only briefly and its origin, ecology, or culture will not affect interaction beyond a few direct traits; define those traits without building a deeper causal chain.
    absorbed_from_object_id: none
---

# Propagate World Assumptions Along Actual Dependencies

## Pattern Rule
**IF** a setting fact materially changes what inhabitants or player characters can do
**THEN** trace consequences through the world elements that actually depend on that fact and turn the important dependencies into player-facing choices, access, information, or constraints
**ELSE** do not force unrelated parts of the setting to change merely because the premise is dramatic or unusual.

## Do
- Define the premise's operating constraints before extrapolating: where it works, when, for whom, at what cost, and with what limits.
- Trace concrete dependencies through travel, commerce, settlement, institutions, resources, information, character options, or adventure structure only when those things rely on the changed assumption.
- Preserve apparently contradictory setting elements when no real dependency requires them to disappear.
- Use restrictions as design material; access conditions, timing windows, scarce routes, and uneven knowledge can create decisions without requiring a bespoke subsystem.
- Let information about the dependency become playable when characters can seek, combine, protect, trade, misunderstand, negotiate over, or exploit it.

## Don't
- Assume one magical, technological, political, or economic premise must transform every part of civilization.
- Patch a contradiction with an arbitrary exception before checking whether the two facts actually depend on one another.
- Add consequences only because they sound thematic if no causal link connects them to the premise.

## Checklist
- The premise has explicit operating constraints.
- Each major consequence can be traced through a named dependency.
- At least one apparent contradiction has been tested rather than automatically removed.
- The consequences create concrete differences in access, information, choices, or adventure possibilities.
- Unrelated setting elements remain unchanged unless another dependency connects them.

## Notes
A setting premise should propagate as far as its real consequences reach, not as far as the designer can imagine thematic echoes. A fixed teleportation gate that works only at a particular place and time and reaches a fixed destination might reshape access to a rare resource and the information needed to reach it without implying that ordinary roads, ships, or isolated regions cease to matter everywhere else. Constraints become especially useful when their dependencies create decisions instead of only lore.

`game_design_worldbuilding_variant_derive_nonhuman_species_through_ecological_and_cultural_causality` applies the same dependency discipline to intelligent fictional species. Begin with the interaction the species must support, then derive only enough environmental and ecological history to explain consequential traits: what conditions it survives, what it competes for, what it eats or requires, how it reproduces, what pressure made intelligence useful, and how physiology and psychology meet culture. Preserve both matches and tensions between biology and culture; a predatory species need not be socially aggressive, and a physically passive species need not have a passive culture. Carry forward the few consequences that players can actually encounter as needs, capabilities, communication problems, accommodations, vulnerabilities, habits, or social expectations. Stop before speculative biography becomes an encyclopedia.
