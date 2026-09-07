---
object_id: PAT_treat_overlapping_progression_packages_as_reachable_ceilings
object_type: pattern
name: Treat Overlapping Progression Packages as Reachable Ceilings
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
- advancement
- progression
- careers
- stacking
- mastery
cross_links:
- rel: related_to
  target_object_id: PAT_audit_character_economy_exchange_rates_across_creation_and_advancement
- rel: related_to
  target_object_id: PAT_price_character_options_by_mechanical_leverage_and_constraint
- rel: related_to
  target_object_id: PAT_separate_advancement_price_permission_and_fictional_cause
reference:
  source_title: Warhammer Fantasy Roleplay, First and Second Editions
  author: Richard Halliwell, Rick Priestley, Graeme Davis, Jim Bambra, Phil Gallagher, Chris Pramas, and contributors
confidence: high
references: []
variants: []
---

# Treat Overlapping Progression Packages as Reachable Ceilings

## Pattern Rule
**IF** characters can enter multiple progression packages that improve the same persistent capability and the overlap represents alternate routes to the same degree of training
**THEN** treat the overlapping improvement as a reachable ceiling relative to persistent baseline state so prior development satisfies lower duplicate allowances instead of stacking them again
**ELSE** allow bounded additive improvement when repeated access explicitly represents deeper cumulative mastery.

## Do
- Establish a stable baseline from which package allowances are measured so switching packages does not reset the same advancement ladder.
- Credit improvement already purchased when a later package grants an equal or lower allowance in the same capability.
- When a later package grants a higher allowance, expose only the unpurchased difference above the character's current reachable ceiling.
- Distinguish duplicate permission from additional mastery. If repeated study is supposed to deepen the same skill, price and cap the extra mastery explicitly rather than letting package overlap imply unlimited stacking.
- Test path-hopping routes to make sure entering many packages is not the cheapest way to repeatedly purchase the same nominal advance.

## Don't
- Add the same package bonus again merely because it appears on a new career, class, rank, or training bundle when the fiction describes equivalent training territory.
- Erase previously purchased development because a new package lists a lower ceiling.
- Use a ceiling model for effects that are genuinely independent and cumulative, such as separate equipment, simultaneous buffs, or distinct power sources.
- Allow repeated mastery to stack without an explicit depth limit when the rest of the progression economy assumes bounded expertise.

## Checklist
- The design can identify whether each overlapping benefit is duplicate access or cumulative mastery.
- Duplicate package allowances are measured against the same persistent baseline.
- Moving into an equal or lower allowance does not grant the same advancement a second time.
- Higher allowances expose only the additional reachable range beyond prior development.
- Any intentionally cumulative mastery has an explicit price and bound.
- A multi-package advancement path has been checked for bonus stacking or cheaper repeated purchases than the intended route.

## Notes
Package-based advancement often creates accidental stacking because each package is written as if it were the character's first. A ceiling model instead says how far a given route can develop a capability. Two occupations that both train basic weapon skill need not grant two independent copies of the same improvement; a more advanced occupation can simply raise the reachable limit. Repeated access can still matter when the design intentionally models deeper mastery, but that is a separate cumulative effect that should be named, priced, and bounded.
