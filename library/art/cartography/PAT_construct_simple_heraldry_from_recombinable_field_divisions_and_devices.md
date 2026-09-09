---
object_id: PAT_construct_simple_heraldry_from_recombinable_field_divisions_and_devices
object_type: pattern
name: Construct Simple Heraldry From Recombinable Field Divisions and Devices
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
- heraldry
- emblems
- shields
- factions
- symbols
cross_links: []
confidence: high
references: []
variants:
- variant_id: VAR_differentiate_related_houses_with_controlled_heraldic_changes
  variant_name: Differentiate Related Houses With Controlled Heraldic Changes
  variant_basis: context
  difference_from_foundation: Preserve part of the heraldic structure while varying selected divisions, devices, or placements so related groups read as connected but individually identifiable.
  when_to_use: Use when houses, branches, allies, or related factions need visible family resemblance without identical emblems.
  when_not_to_use: Do not reuse so much structure that individual emblems become indistinguishable.
  absorbed_from_object_id: none
- variant_id: VAR_add_external_heraldic_embellishment_to_encode_exceptional_status_or_role
  variant_name: Add External Heraldic Embellishment to Encode Exceptional Status or Role
  variant_basis: context
  difference_from_foundation: Keep the core shield identity unchanged while adding a secondary external embellishment that encodes exceptional rank, civic importance, religious significance, commercial importance, or another special role.
  when_to_use: Use when one heraldic instance needs an additional status or role cue without redesigning its core emblem.
  when_not_to_use: Do not make external ornament so strong that it obscures, replaces, or visually overpowers the shield.
  absorbed_from_object_id: none
---

# Construct Simple Heraldry From Recombinable Field Divisions and Devices

## Pattern Rule
**IF** a map needs a compact heraldic emblem that can identify a house, faction, city, or related political entity
**THEN** build the emblem from a bounded grammar of field divisions and simple devices, add one dominant charge when a stronger identity cue is needed, and keep all layers visually separable enough that the emblem reads as one coherent symbol

## Do
- Start with a simple shield field and divide it only when the division helps the emblem.
- Recombine a small vocabulary of bars, diagonals, chevrons, quarters, stars, dots, or similarly strong devices.
- Use one dominant charge or sigil when it can carry the primary identity more clearly than several competing symbols.
- Preserve clear figure-ground separation between the dominant charge and the field beneath it.
- If the charge merges with a busy or similar-value field, simplify or interrupt the field locally or change value or color.
- Build related emblems through controlled shared structure when kinship or alliance should be visible.

## Don't
- Do not invent every emblem from an unrelated miniature illustration.
- Do not pile several equal-priority charges onto a shield when one symbol already carries the identity.
- Do not let field divisions obscure the dominant charge.
- Do not assume real-world heraldic conventions are mandatory for an invented emblem system.

## Checklist
- The shield reads as one coherent emblem at map scale.
- Field divisions and devices come from a bounded repeatable grammar.
- A dominant charge remains visually separable from the field.
- Related emblems share enough structure to communicate relationship without becoming identical.
- Optional external embellishment does not replace or overpower the core shield identity.

## Notes
The variant `VAR_differentiate_related_houses_with_controlled_heraldic_changes` preserves selected divisions, devices, or placements while changing others so related houses remain visibly connected but distinct. The variant `VAR_add_external_heraldic_embellishment_to_encode_exceptional_status_or_role` leaves the core emblem intact and adds subordinate external ornament when one instance needs an extra rank or role cue.
