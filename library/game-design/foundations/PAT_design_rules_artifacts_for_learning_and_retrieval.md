---
object_id: PAT_design_rules_artifacts_for_learning_and_retrieval
object_type: pattern
name: Design Rules Artifacts for Learning and Retrieval
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
- learning
- reference
cross_links:
- rel: related_to
  target_object_id: PAT_make_the_game_operable_without_hidden_designer_knowledge
- rel: related_to
  target_object_id: PAT_curate_modular_rules_for_safe_onboarding
- rel: related_to
  target_object_id: PAT_account_for_the_intended_play_environment_before_freezing_the_design
reference:
  source_title: Designing TTRPGs For Dummies
  author: Martin Buinicki
confidence: high
references: []
variants: []
---

# Design Rules Artifacts for Learning and Retrieval

## Pattern Rule
**IF** intended users must learn and repeatedly reference a nontrivial rules surface
**THEN** organize prerequisite knowledge, teaching transitions, high-frequency lookup paths, and visual hierarchy so users can learn exact operation and later retrieve it without expert memory
**ELSE** keep the interface proportionate when the rules surface is small enough to remain directly legible.

## Do
- Treat the rulebook, digital reference, or equivalent surface as part of the game's operating interface rather than as passive storage for correct text.
- Organize prerequisite concepts before they are needed or provide direct navigation that lets users recover missing prerequisites cheaply.
- Put high-frequency procedures, modifiers, tables, exceptions, definitions, and branch destinations close enough to use that ordinary play does not require memorizing the document graph.
- Separate learning architecture from reference architecture; a sequence optimized for first exposure need not be the cheapest lookup surface during repeated play.
- When onboarding simplifies a procedure, identify what is simplified and provide a clear transition to the full behavior rather than disguising a later replacement as added detail.
- Use consistent hierarchy, tables, boxes, indexes, cross-references, summaries, and other navigation signals to reduce search and interpretation cost.
- Test novice retrieval separately from veteran retrieval because experienced users may have cached locations and shortcuts that the artifact itself does not communicate.
- Treat delivery format as part of retrieval design: printed spreads, searchable PDFs, phone-sized displays, virtual tabletop references, and other surfaces can impose different navigation, display, and cross-reference costs even when the rule content is identical.
- Validate the actual presentation formats the game intends to support rather than assuming a layout or reference structure proven in one medium transfers without friction to another.
- Preserve thematic presentation only while legibility and retrieval remain reliable.

## Don't
- Treat correct text somewhere in the artifact as sufficient when intended users cannot reliably locate it at the moment of need.
- Present a teaching simplification as the exact procedure when later rules change sequencing, information, permissions, or other behavior the learner must relearn.
- Let ornamental style or dense page furniture slow high-frequency retrieval or reduce legibility.
- Use cross-references that reveal the destination only after the user has already had to infer which branch or product applies.
- Treat veteran table-location memory or habitual shortcuts as evidence that the published interface works for novices.
- Assume a book layout, table, spread, or navigation structure remains equally usable when moved unchanged to a different screen size or delivery format.

## Checklist
- Prerequisite concepts appear in a usable learning order or can be reached through explicit navigation.
- High-frequency rules and reference material can be recovered quickly enough that lookup is not a recurring avoidable friction source.
- Learning aids that simplify the full procedure say what changed and how to transition to exact operation.
- Visual hierarchy consistently distinguishes rules, examples, tables, warnings, and reference material.
- Frequent branch points expose their next destination at the point of need.
- Novice and veteran retrieval have been tested separately when expert familiarity could hide interface cost.
- Each intended rules-delivery format has been checked for legibility, navigation, and retrieval cost in the conditions where users will actually consult it.

## Notes
Learning and reference are two access modes over the same rules. A teaching sequence often benefits from dependency order and worked examples; repeated play benefits from cheap direct retrieval of procedures and exceptions. The two structures can share an artifact, but they should not be mistaken for the same navigation problem. The same content can also impose different retrieval costs across print, searchable PDF, phone-sized, or virtual tabletop surfaces, so format transfer requires its own usability check. A simplified teaching model is useful only when the learner knows it is simplified and can transition to the exact procedure without discovering that earlier behavior was secretly replaced.
