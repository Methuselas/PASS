---
object_id: PAT_reduce_initial_choice_load_without_erasing_later_option_space
object_type: pattern
name: Reduce Initial Choice Load Without Erasing Later Option Space
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
- onboarding
- choice-load
- random-generation
- progression
cross_links:
- rel: related_to
  target_object_id: PAT_use_editable_templates_as_onboarding_scaffolds
- rel: related_to
  target_object_id: PAT_make_character_creation_preview_recurring_play
- rel: related_to
  target_object_id: PAT_choose_a_randomizer_by_the_uncertainty_profile_it_must_produce
reference:
  source_title: Warhammer Fantasy Roleplay, First and Second Editions
  author: Richard Halliwell, Rick Priestley, Graeme Davis, Jim Bambra, Phil Gallagher, Chris Pramas, and contributors
confidence: high
references: []
variants:
- variant_id: game_design_variant_reward_accepting_generated_start
  variant_name: Reward Accepting a Generated Start
  variant_basis: constraint
  difference_from_foundation: Keep direct selection available from the start, but offer a bounded reward for accepting the generated result immediately and a smaller reward for accepting one from a short generated set.
  when_to_use: Random discovery is desirable but the design should preserve full authorship for players who value control more than the bonus.
  when_not_to_use: Random generation is mandatory to the experience, the reward is large enough to make direct choice a trap, or generated outcomes can be unusable without a repair valve.
  absorbed_from_object_id: none
---

# Reduce Initial Choice Load Without Erasing Later Option Space

## Pattern Rule
**IF** a novice must choose from more starting options than they can meaningfully evaluate before play
**THEN** narrow, assign, generate, or scaffold the initial choice while preserving broader authorship and transition options once the player has enough system context to use them
**ELSE** expose the full starting choice surface when the intended player can evaluate it without excessive setup cost.

## Do
- Reduce the number of options a new player must understand at once instead of reducing the total diversity the system can eventually support.
- Use random assignment, bounded lists, editable templates, recommendations, or staged unlocking according to the experience the game wants from character creation.
- Give experienced players an explicit route to choose directly when discovery through assignment is no longer providing useful onboarding value.
- Preserve later mobility so a constrained starting point does not permanently trap the character unless long-term constraint is itself part of the intended game.
- Explain enough about the assigned or recommended option for the player to operate it immediately; deferred comparison knowledge should not become hidden rules knowledge.

## Don't
- Present dozens of opaque starting choices and call the resulting paralysis meaningful agency.
- Use random assignment as an excuse to deny all later authorship when the game's progression model already supports plausible change.
- Remove interesting later options merely because exposing them all at creation would overwhelm a novice.
- Pretend a constrained start is optional if escaping it requires expertise the onboarding path never supplies.

## Checklist
- A novice can begin without evaluating the entire long-term option catalog.
- The narrowing method produces a playable starting state rather than only postponing unresolved required choices.
- Experienced players have a clear direct-choice path when the design intends one.
- Later progression or revision restores meaningful authorship unless permanent constraint is deliberate.
- The system retains more long-term option diversity than it asks a novice to compare at the first decision point.

## Notes
Initial option count and total option space are separate design variables. A game can contain many careers, roles, packages, or specializations while asking a beginner to learn only one starting slice. Assignment or random generation can function as progressive disclosure when it turns a large catalog into one immediately actionable result, especially if later play reopens the wider graph. The technique fails when the starting constraint becomes an unexplained permanent loss of authorship rather than temporary onboarding support. Variant `game_design_variant_reward_accepting_generated_start` keeps direct selection available but compensates players who voluntarily surrender some initial control to the generator; use it when discovery is desirable without making randomness compulsory.
