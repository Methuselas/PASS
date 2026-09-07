---
object_id: PAT_convert_catastrophic_failure_protection_into_a_changed_survivable_state
object_type: pattern
name: Convert Catastrophic Failure Protection into a Changed Survivable State
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
- failure
- survival
- continuity
- defeat
- recovery
cross_links:
- rel: related_to
  target_object_id: PAT_match_the_cost_of_failure_to_the_players_prior_investment
- rel: related_to
  target_object_id: PAT_prepare_executable_adventure_outcome_states
- rel: related_to
  target_object_id: PAT_restore_meaningful_participation_before_full_fictional_recovery_when_needed
reference:
  source_title: Warhammer Fantasy Roleplay, Second Edition
  author: Chris Pramas
confidence: high
references: []
variants:
- variant_id: game_design_variant_nullify_the_immediate_terminal_result_but_preserve_repeated_exposure
  variant_name: Nullify the Immediate Terminal Result but Preserve Repeated Exposure
  variant_basis: constraint
  difference_from_foundation: Spend scarce permanent protection to erase the immediate terminal consequence and continue in the same scene, while permanently reducing future protection and leaving the character exposed to the same encounter's later risks.
  when_to_use: Continuous participation in the current scene is more valuable than preserving evidence of this single defeat, and repeated exposure can make the permanent protection cost compound naturally.
  when_not_to_use: The scene ends immediately after the negation, protection refreshes cheaply, repeated uses are common, or erasing the consequence would trivialize the objective or opponent victory.
  absorbed_from_object_id: none
---

# Convert Catastrophic Failure Protection into a Changed Survivable State

## Pattern Rule
**IF** a scarce protection resource prevents a heavily invested character or persistent asset from being removed by a catastrophic outcome
**THEN** replace the terminal result with a survivable state that preserves evidence of defeat and changes position, capability, resources, access, obligations, or another immediate condition
**ELSE** resolve the catastrophic outcome normally when the design does not promise this form of continuity protection.

## Do
- Let the catastrophic event remain consequential even when the protected subject survives it.
- Replace removal with an executable state such as unconsciousness, capture, separation, lost equipment, forced retreat, debt, damaged capability, exposure, or another consequence appropriate to the fiction.
- Make the protection resource scarce enough that invoking it still marks a serious event rather than an ordinary correction.
- Preserve the surrounding outcome where possible: opponents may still win the fight, the objective may still be lost, and allies may still have to deal with the aftermath.
- Let the replacement state create future decisions rather than merely postponing the identical terminal roll.
- Keep continuity protection exceptional when repeated use by disposable opposition would stretch encounters, cheapen victory, or make defeat feel reversible on demand.

## Don't
- Spend a scarce survival resource only to erase the fatal result and resume from the same tactical state unchanged.
- Turn survival into immunity from defeat, capture, loss, separation, or other consequences the scene legitimately produced.
- Replace death with a consequence so punitive or inescapable that the protection has no meaningful value.
- Immediately route the protected subject back through the identical terminal threat solely because the table knows protection was used.
- Give routine opponents repeated continuity protection merely to keep them on stage longer.

## Checklist
- Spending the protection prevents terminal removal but does not erase the fact that a catastrophic failure occurred.
- The protected subject enters a concrete survivable state that changes at least one meaningful future decision or resource condition.
- The scene can still preserve defeat, objective loss, enemy advantage, or another legitimate consequence independent of survival.
- The replacement state has a playable continuation path rather than functioning as delayed automatic removal.
- The protection remains scarce or role-bounded enough that repeated use does not trivialize catastrophic stakes.

## Notes
Continuity protection works best when it changes the form of failure rather than nullifying failure. A character saved from death can still wake after the battle, lose possessions, become a prisoner, owe a rescuer, or return from the event in some other altered state. This preserves long-term player investment without teaching the table that the most serious outcomes simply vanish when a metacurrency is spent. `PAT_match_the_cost_of_failure_to_the_players_prior_investment` owns whether continuity protection is warranted; this Pattern owns what the protected catastrophic result becomes once that protection is invoked. Variant `game_design_variant_nullify_the_immediate_terminal_result_but_preserve_repeated_exposure` is the deliberate exception: it allows the immediate terminal result to vanish so the character can stay active, but only when the protection is permanently scarce and continued participation leaves the character exposed to further danger that may demand additional protection.
