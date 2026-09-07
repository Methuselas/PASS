---
object_id: PAT_choose_specialization_boundaries_by_permission_and_economic_effect
object_type: pattern
name: Choose Specialization Boundaries by Permission and Economic Effect
library_path:
- game-design
- characters
stage_binding: 0 design
lane_fit: both
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- characters
- specialization
- permissions
- costs
cross_links:
- rel: related_to
  target_object_id: PAT_balance_character_roles_by_consequential_contribution
- rel: related_to
  target_object_id: PAT_price_character_options_by_mechanical_leverage_and_constraint
reference:
  source_title: Designing TTRPGs For Dummies
  author: Martin Buinicki
confidence: high
references: []
variants:
- variant_id: game_design_variant_bundle_identity_and_role_into_one_progression_package
  variant_name: Bundle Identity and Role into One Progression Package
  variant_basis: context
  difference_from_foundation: Treat an identity and adventuring or professional role as one archetypal progression package with shared permissions, abilities, advancement, limits, and tradeoffs instead of exposing the two axes as independently recombinable choices.
  when_to_use: The game intentionally wants a specific identity-role combination to be the meaningful archetype and values fast legibility, strong package identity, and reduced combinatorial load.
  when_not_to_use: Players are expected to express the same identity through many professions or the same profession through many identities, because bundling would erase desired recombination.
  absorbed_from_object_id: none
---

# Choose Specialization Boundaries by Permission and Economic Effect

## Pattern Rule
**IF** a character role or specialty needs to be distinguished from adjacent characters
**THEN** decide whether that distinction should come from cost, efficiency, access, packaging, or hard permission boundaries based on the behavior the game needs specialization to create
**ELSE** do not harden a soft economic difference into permanent exclusion merely because named archetypes are easier to present.

## Do
- Separate **soft specialization** through price, efficiency, or opportunity cost from **hard specialization** through permission or access boundaries.
- Use soft boundaries when nonspecialists should remain able to attempt the activity but specialists should perform it more efficiently, reliably, or broadly.
- Use hard boundaries when exclusive access itself creates an important identity, world interface, institutional gate, or protection the design genuinely needs.
- Compare the same specialty under cost-based and permission-based implementations before deciding which character philosophy fits the game.
- Check whether a hard boundary creates compulsory-party-key behavior for routine progress rather than meaningful differentiation.
- Check whether an economic boundary is strong enough to preserve a niche or simply makes the broad parent option the rational purchase.

## Don't
- Harden a soft specialization framework into permanent role or permission boundaries merely because named classes are easier to communicate.
- Give universal access at effectively equal performance when the design depends on specialist differentiation.
- Make one specialist a compulsory permission key for ordinary campaign progress unless that dependency is an intentional part of the game.
- Assume cost and access are interchangeable because both can reduce how many characters possess a capability.

## Checklist
- The specialization boundary is identified as cost, efficiency, access, packaging, permission, or a deliberate combination.
- Nonspecialist access matches the intended role ecology rather than being accidental.
- Any hard boundary names the design benefit that cannot be achieved as cleanly through softer incentives.
- Any soft boundary preserves enough differential value to make specialization meaningful.
- The chosen boundary does not accidentally make one role mandatory for routine progress unless that dependency is intended.

## Notes
Two character systems can contain nearly identical skill lists while producing very different play because one uses price differences and the other uses permission gates. Specialization architecture therefore belongs at the level of access and economics, not merely labels. Soft boundaries preserve broader participation while rewarding investment; hard boundaries can create stronger identity and exclusive world interfaces but also risk compulsory-role dependencies. Choose the boundary for the behavior it creates.

Variant `game_design_variant_bundle_identity_and_role_into_one_progression_package` collapses two normally separate choice axes into one advancement package. It trades combinatorial freedom for a strongly legible archetype; use it only when the combined identity-role fantasy is intentional rather than a shortcut around supporting flexible combinations.
