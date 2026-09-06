---
object_id: PAT_make_the_game_operable_without_hidden_designer_knowledge
object_type: pattern
name: Make the Game Operable Without Hidden Designer Knowledge
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
- usability
- rules
- handoff
- delegation
cross_links:
- rel: related_to
  target_object_id: PAT_define_the_intended_player_before_designing_for_them
- rel: related_to
  target_object_id: PAT_spend_worldbuilding_detail_where_it_changes_play
- rel: related_to
  target_object_id: PAT_scale_npc_and_adversary_detail_to_their_role_in_play
- rel: related_to
  target_object_id: PAT_build_complete_resolution_procedures_incrementally
- rel: related_to
  target_object_id: PAT_structure_adventure_narratives_with_milestones_plot_beats_and_player_agency
- rel: related_to
  target_object_id: PAT_layer_adventure_information_by_how_players_can_access_it
- rel: related_to
  target_object_id: PAT_account_for_the_intended_play_environment_before_freezing_the_design
- rel: related_to
  target_object_id: PAT_expose_construction_grammar_for_expected_downstream_authorship
- rel: related_to
  target_object_id: PAT_design_rules_artifacts_for_learning_and_retrieval
- rel: related_to
  target_object_id: PAT_curate_modular_rules_for_safe_onboarding
- rel: related_to
  target_object_id: PAT_keep_common_path_procedures_inside_the_declared_playable_core
reference:
  source_title: Designing TTRPGs For Dummies
  author: Martin Buinicki
confidence: high
references: []
variants: []
---

# Make the Game Operable Without Hidden Designer Knowledge

## Pattern Rule
**IF** players, facilitators, testers, or implementers will use the game without the designer present
**THEN** make the assumptions, rules, expectations, and required information explicit enough for the intended user to operate the game independently
**ELSE** temporary explanatory debt is acceptable in an internal prototype only when it is tracked as unfinished design rather than mistaken for a complete rule.

## Do
- Watch for moments where the designer answers a question from memory instead of from the game’s written or implemented interface.
- Test with people who were not present during design so missing assumptions become visible.
- During at least one handoff playtest, remain silent when players or another facilitator encounter a rules question long enough to see whether the written game lets them recover; record any designer explanation required to continue as missing or unclear design information.
- At completed-game stage, include at least one referee or facilitator who did not learn the game directly from the designer. Treat any designer intervention as test contamination that must be recorded even when intervention is necessary to keep play moving.
- When an unfamiliar referee hesitates, distinguish intentionally delegated referee judgment from ordinary unfamiliarity that the documentation can resolve and from information that is actually missing and can only be supplied by hidden designer knowledge.
- Distinguish an intentionally adjudicated open space from a rule whose missing logic is being supplied unconsciously by the creator.
- Treat delegation as healthy only when the user receives explicit authority plus enough boundaries, reusable categories, examples, baselines, or other calibration to make the delegated decision without reverse-engineering the designer.
- Rewrite rules around the decision the user must make, including inputs, outputs, and exceptional states that matter to play.


## Don't
- Treat “it is obvious” as evidence that another player will infer the same rule.
- Use designer availability as a permanent support mechanism for unclear procedures.
- Rescue an independent handoff test with unwritten explanations and still count the resulting execution as proof that the published artifact is self-sufficient.
- Hide required knowledge in scattered examples when the user needs it to execute a core interaction.


## Checklist
- A new user can begin and resolve core play without asking what the designer meant.
- Rules that rely on judgment say who exercises that judgment and what boundaries apply.
- Delegated judgment has enough categorical rails, examples, baselines, or calibration that an intended user can make a ruling without reconstructing hidden designer assumptions.
- Playtests record repeated clarification questions as design defects to investigate.
- A handoff or designer-silence test has shown that intended users can recover from ordinary rules questions without the designer supplying unwritten intent.
- At least one completed-game handoff has been run by a referee or facilitator who learned the game from the artifact rather than from the designer, and every designer intervention required to continue was logged.
- Handoff observations distinguish intentional adjudication space, recoverable unfamiliarity, and genuinely missing information.
- Internal prototypes clearly mark unresolved or temporarily explained behavior.

## Notes
Independent operation is a handoff property. The decisive test is whether intended users can recover from ordinary uncertainty using the artifact and the authority it explicitly delegates, rather than borrowing the designer's memory. Open adjudication can be healthy when the user is told that judgment is theirs and receives enough boundaries or calibration to exercise it consistently; hidden logic is different because only the creator knows it exists. Handoff tests are therefore strongest when the designer remains silent long enough to expose missing assumptions and records any intervention needed to continue.

This decision owns **independent operability and delegated judgment**, not every documentation problem. Complete multi-step procedure design belongs to **Build Complete Resolution Procedures Incrementally**; downstream content construction belongs to **Expose Construction Grammar for Expected Downstream Authorship**; learning and retrieval belong to **Design Rules Artifacts for Learning and Retrieval**, while modular starting configurations belong to **Curate Modular Rules for Safe Onboarding** and declared-core dependency completeness belongs to **Keep Common-Path Procedures Inside the Declared Playable Core**; prepared-adventure information and structure remain with their adventure Patterns.
