---
object_id: PAT_add_a_bounded_repair_valve_to_random_generation
object_type: pattern
name: Add a Bounded Repair Valve to Random Generation
library_path:
- game-design
- foundations
stage_binding: 0 design
lane_fit: both
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- random-generation
- variance
- character-creation
- usability
- repair
cross_links:
- rel: related_to
  target_object_id: PAT_choose_a_randomizer_by_the_uncertainty_profile_it_must_produce
- rel: related_to
  target_object_id: DRILL_profile_a_randomizer_before_committing_to_it
- rel: related_to
  target_object_id: PAT_reduce_initial_choice_load_without_erasing_later_option_space
reference:
  source_title: Warhammer Fantasy Roleplay, Second Edition
  author: Chris Pramas and Black Industries contributors
confidence: high
references: []
variants: []
---

# Add a Bounded Repair Valve to Random Generation

## Pattern Rule
**IF** random generation is valuable for discovery or variety but an extreme result can disproportionately damage the usability of the generated whole
**THEN** allow a small targeted repair that normalizes a limited outlier without rerolling or rebuilding the entire result
**ELSE** preserve the full random output when tail outcomes are themselves part of the intended challenge or identity.

## Do
- Define the repair budget before results are known: one replacement, one normalization, one swap, or another clearly bounded intervention.
- Repair the most damaging outlier while leaving the rest of the generated pattern intact so randomness still produces discovery and asymmetry.
- Normalize toward a known ordinary value, floor, or bounded alternative when the goal is usability rather than optimization.
- Keep the repair optional when some players may enjoy embracing the extreme result.
- Test the rule on both ordinary and tail outcomes to ensure players are not incentivized to manipulate the valve into a general optimization tool.

## Don't
- Permit unlimited rerolls until the player receives a preferred build and still describe the process as meaningfully random.
- Repair every below-average result when the generator is supposed to create varied strengths and weaknesses.
- Give the repair enough flexibility to reconstruct the whole output after seeing it.
- Add a rescue valve when extreme results are a deliberate source of challenge, scarcity, or identity and remain playable.

## Checklist
- The generator still produces materially varied outputs after the repair rule is applied.
- The repair can affect only a clearly bounded portion of the generated whole.
- The repaired value moves toward an ordinary usable state rather than directly toward the strongest legal result.
- A player cannot repeatedly invoke the valve to erase most unwanted variance.
- At least one tail result that would have made the whole disproportionately hard to use becomes playable without rebuilding the rest.

## Notes
Random generation can create memorable combinations while still producing occasional outliers that dominate the usability of the whole character, loadout, team, or scenario. A narrow repair valve keeps the discovery value of the generator while reducing the chance that one tail result invalidates everything around it. The boundary matters: once the user can keep rerolling or freely reassigning many outputs, the procedure has become disguised point selection rather than random generation with variance control.
