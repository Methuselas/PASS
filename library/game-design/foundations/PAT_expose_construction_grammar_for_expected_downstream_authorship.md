---
object_id: PAT_expose_construction_grammar_for_expected_downstream_authorship
object_type: pattern
name: Expose Construction Grammar for Expected Downstream Authorship
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
- authorship
- construction
- extensibility
cross_links:
- rel: related_to
  target_object_id: PAT_make_the_game_operable_without_hidden_designer_knowledge
- rel: related_to
  target_object_id: PAT_spend_worldbuilding_detail_where_it_changes_play
- rel: related_to
  target_object_id: PAT_structure_adventure_narratives_with_milestones_plot_beats_and_player_agency
reference:
  source_title: Designing TTRPGs For Dummies
  author: Martin Buinicki
confidence: high
references: []
variants:
- variant_id: game_design_variant_use_a_sample_adventure_as_an_executable_reference_implementation
  variant_name: Use a Sample Adventure as an Executable Reference Implementation
  variant_basis: context
  difference_from_foundation: When a game expects new referees to run play or create their own adventures, pair the construction grammar with at least one representative adventure that can be run directly and that demonstrates how rules, setting assumptions, encounter structures, information, and referee procedures compose in practice.
  when_to_use: The game expects inexperienced or downstream referees to learn how its abstract rules and authoring guidance become actual playable material.
  when_not_to_use: The sample would substitute for explicit construction guidance, teach an atypical edge case as though it were the normal form, or require users to reverse-engineer hidden assumptions from the example.
  absorbed_from_object_id: none
- variant_id: game_design_variant_encode_baseline_calibration_in_a_novice_generator
  variant_name: Encode Baseline Calibration in a Novice Generator
  variant_basis: method_sequence
  difference_from_foundation: Provide novice downstream authors with a bounded generator whose distributions embody a tested baseline relationship, so early construction can remain calibrated before the user has developed reliable intuition.
  when_to_use: New referees or content authors must create quantitatively sensitive content immediately and a random or tabular generator can preserve a known risk, reward, density, or difficulty relationship.
  when_not_to_use: The author already needs bespoke placement, the baseline is intentionally unstable, or using the generator would hide the relationship it is meant to teach.
  absorbed_from_object_id: none
---

# Expose Construction Grammar for Expected Downstream Authorship

## Pattern Rule
**IF** a game expects referees, players, modders, or other downstream users to create campaign-central content rather than only select or lightly modify published examples
**THEN** expose the reusable fields, constraints, scaling guidance, composition rules, baselines, and examples needed to construct new instances coherently
**ELSE** stock examples and bounded modification guidance are sufficient when novel construction is not part of expected use.

## Do
- Distinguish local fictional rulings from recurring or campaign-central construction tasks; repeated authorship needs stronger support than one-off adjudication.
- For each content type users are expected to author, state the required fields, constraints, scaling guidance, templates, and interaction rules that make a novel instance usable.
- When setting expansion is expected, expose stable anchors and dependency rules strongly enough that new material can be integrated without hidden designer intent.
- Provide enough baselines to calibrate novel work rather than forcing the user to infer the entire grammar from finished examples.
- When adventure creation is an expected downstream task, pair the grammar with a representative runnable adventure so the documented pieces can be seen composing into actual play.
- Explain composition and exception behavior where user-authored elements can interact, overlap, or violate ordinary assumptions.

## Don't
- Treat a catalog of stock examples as a substitute for construction rules when users are expected to make new instances.
- Call unsupported extrapolation healthy referee freedom when a recurring creation or calibration task lacks usable grammar and baselines.
- Make the example the only specification; examples demonstrate the grammar but do not replace it.
- Require users to reverse-engineer hidden scaling, compatibility, or completeness assumptions from existing content.

## Checklist
- Every content category users are expected to extend has a stated construction grammar appropriate to the decisions that creation requires.
- A new intended user can construct at least one novel instance without obtaining unwritten designer guidance.
- Open setting or campaign content has enough stable anchors to determine what belongs and what important dependencies a new addition changes.
- Scaling and compatibility guidance cover the dimensions that can make a new instance unusable or disruptive.
- When adventure creation is expected, at least one representative sample can be run directly and visibly demonstrates how the grammar composes into play.
- Examples are recognizable as examples of reusable rules rather than the only place those rules can be inferred.

## Notes
Downstream authorship is a different responsibility from local referee judgment. A referee can improvise a one-off fictional ruling with broad authority and a few calibration rails; creating a new adversary family, adventure, spell list, setting institution, vehicle, or other reusable game object may require a stable grammar so the result continues to interact correctly with the rest of the game. The stronger the game promises user-created content, the less it can rely on reverse-engineering finished examples. A runnable sample is especially useful when it acts as a reference implementation of an already explicit grammar rather than as a substitute for one. Variant `game_design_variant_use_a_sample_adventure_as_an_executable_reference_implementation` applies that move when adventure authorship is part of expected use.

Variant `game_design_variant_encode_baseline_calibration_in_a_novice_generator` uses a bounded generator as embedded authoring expertise. It is useful when a novice must create calibrated material before intuition is trustworthy: the distribution preserves a baseline relationship while the surrounding guidance explains what that relationship is protecting and when deliberate override is appropriate.
