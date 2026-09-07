---
object_id: PAT_preserve_advancement_headroom_across_the_intended_progression_horizon
object_type: pattern
name: Preserve Advancement Headroom Across the Intended Progression Horizon
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
- advancement
- progression
- scaling
- headroom
cross_links: []
confidence: high
references: []
variants:
- variant_id: game_design_variant_redirect_post_cap_growth_into_a_narrower_progression_track
  variant_name: Redirect Post-Cap Growth into a Narrower Progression Track
  variant_basis: method_sequence
  difference_from_foundation: Preserve an intentional ceiling on the full progression package while continuing advancement through selected capabilities, ranks, permissions, or defenses that do not reproduce the entire capped package.
  when_to_use: A class, role, license, rank, or other progression package has a meaningful identity or balance ceiling but characters are expected to remain active and improve after reaching it.
  when_not_to_use: The cap is only accidental numeric exhaustion, the full package is intended to keep advancing, or the secondary track would simply recreate hidden extra levels with the same contents.
  absorbed_from_object_id: none
---

# Preserve Advancement Headroom Across the Intended Progression Horizon

## Pattern Rule
**IF** a capability is expected to improve repeatedly across a known campaign or progression horizon
**THEN** project its effective improvement curve across that whole horizon and retune earlier gains when necessary so later advancement still changes expected play instead of arriving after the capability has already saturated
**ELSE** allow a short or deliberately capped progression when additional growth is not part of the promised experience.

## Do
- Identify the effective ceiling of the capability under conditions the game actually expects, not merely the highest number the notation can print.
- Project early, middle, and late advancement together before committing the initial curve.
- Count reduced failure, expanded scope, better efficiency, new permissions, resistance to penalties, and other meaningful gains as headroom; advancement need not increase the same number every step.
- When the intended campaign horizon is extended, revisit earlier progression rather than automatically appending more tiers to a curve that was designed for a shorter game.
- Preserve intentionally flat tiers when another advancement dimension supplies meaningful growth during that interval.

## Don't
- Treat a nominal value below 100%, a printed maximum, or another visible cap as proof that useful headroom remains.
- Consume nearly all ordinary outcome space early and then fill later levels with numerically cosmetic increases.
- Stretch a short progression by reducing every gain until early advancement stops feeling consequential.
- Force a capped package to keep growing when the ceiling is itself part of the role's identity or balance.

## Checklist
- Repeatedly improving capabilities have been projected to the intended final progression point.
- A representative late-stage increase still changes outcomes, scope, cost, reliability, or another consequential property.
- Any apparent numeric ceiling has been tested under expected penalties and circumstances before being treated as saturation.
- Extending the campaign horizon triggers a recheck of earlier curves and supporting reward math.
- Deliberate caps state whether advancement stops entirely or changes grammar afterward.

## Notes
Progression can run out of useful space long before a number reaches its printed maximum. A success chance that already succeeds in almost every expected circumstance, a defense that has made ordinary threats irrelevant, or a cost that has effectively fallen to zero may have saturated even when more increments are technically possible. Headroom is therefore measured by changed play, not notation.

Variant `game_design_variant_redirect_post_cap_growth_into_a_narrower_progression_track` preserves a meaningful ceiling on a full progression package while letting long-running characters continue to grow through a narrower secondary track. Use it only when the later track clearly states what continues and what remains capped; otherwise the original ceiling has merely been renamed.
