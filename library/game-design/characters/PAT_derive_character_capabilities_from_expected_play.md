---
object_id: PAT_derive_character_capabilities_from_expected_play
object_type: pattern
name: Derive Character Capabilities from Expected Play
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
- abilities
- roles
- gameplay
cross_links:
- rel: related_to
  target_object_id: PAT_translate_genre_into_play_requirements
- rel: related_to
  target_object_id: PAT_define_the_intended_player_before_designing_for_them
- rel: related_to
  target_object_id: PAT_balance_character_roles_by_consequential_contribution
- rel: related_to
  target_object_id: PAT_price_character_options_by_mechanical_leverage_and_constraint
- rel: related_to
  target_object_id: PAT_choose_character_capability_granularity_by_play_distinctions
- rel: related_to
  target_object_id: PAT_use_editable_templates_as_onboarding_scaffolds
- rel: related_to
  target_object_id: PAT_choose_specialization_boundaries_by_permission_and_economic_effect
- rel: related_to
  target_object_id: PAT_reuse_capability_effect_grammar_across_fictional_sources
- rel: related_to
  target_object_id: PAT_express_advancement_as_greater_operating_fluency_when_that_is_the_fantasy
- rel: related_to
  target_object_id: PAT_separate_advancement_price_permission_and_fictional_cause
reference:
  source_title: Designing TTRPGs For Dummies
  author: Martin Buinicki
confidence: high
references: []
variants: []
---

# Derive Character Capabilities from Expected Play

## Pattern Rule
**IF** a game is defining the traits, abilities, skills, classes, playbooks, or other structures used to create player characters
**THEN** derive those structures from the significant actions, challenges, and roles the characters are expected to face in actual play
**ELSE** when an inherited character framework is being used, remove or reinterpret fields that do not support the intended experience before adding new ones.

## Do
- List the most exciting and recurring things player characters are expected to do before deciding which attributes, skills, powers, or roles exist.
- Use genre and setting to determine which capabilities deserve mechanical distinction and which terms make those distinctions understandable to players.
- Narrow the near-infinite set of human traits to qualities that change gameplay or meaningfully shape the player experience.
- Let classes or playbooks package recognizable roles when that helps creation and communication; use classless structures when direct trait and ability selection better fits the design.
- Make character options mechanically consequential enough that choosing them changes how the character acts, solves problems, accesses situations, or contributes to the game's important activities.
- Check the expected adventure and campaign ecology so advertised competencies actually receive consequential opportunities to matter.

## Don't
- Begin with a traditional attribute or skill list and search afterward for reasons each field should matter.
- Model every plausible human capability simply because a detailed character could possess it.
- Create a class whose title sounds appropriate to the genre but whose abilities rarely matter in the adventures the game actually produces.
- Create a new tracked field or mechanical distinction when its play value does not justify the extra state it adds to the character model.
- Keep a flavorful or elaborate capability whose promised competence the expected game almost never tests or rewards.

## Checklist
- Every major character field connects to an expected action, challenge, role, or recurring decision.
- Important adventure activities have character capabilities capable of differentiating how protagonists approach them.
- A mechanically elaborate option appears often enough, or matters strongly enough, to justify its representation cost.
- Class or role labels correspond to differences in actual play rather than cosmetic naming alone.
- Traditional elements retained from another RPG architecture have a current purpose in this game.
- The character model's advertised competencies match the situations the game is prepared to produce.

## Notes
Character architecture should be derived from what the game expects characters to do, not from an attempt to model every trait a person could possess. Classes can package broad roles while classless systems can expose capabilities directly; either approach works when the represented choices change play. A capability on the sheet is also a promise about the kinds of situations the game considers important. Selection, granularity, onboarding, specialization, fictional-source reuse, and advancement each create their own design decisions; this Pattern owns the earlier question of which capabilities deserve representation at all.
