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
variants:
- variant_id: game_design_variant_preserve_stable_reference_topology_across_staged_expansions
  variant_name: Preserve Stable Reference Topology Across Staged Expansions
  variant_basis: method_sequence
  difference_from_foundation: Organize later rule stages under the same recurring conceptual headings as earlier stages so users attach new material to an existing mental and reference map instead of learning a second document topology.
  when_to_use: A rules line expands in stages while preserving the same core conceptual grammar and later users need to combine or cross-reference those stages frequently.
  when_not_to_use: The later stage replaces the earlier conceptual model, the old topology is itself a usability defect, or parallel headings would force unrelated material into misleading categories.
  absorbed_from_object_id: none
- variant_id: game_design_variant_fade_instructional_scaffolding_as_competence_grows
  variant_name: Fade Instructional Scaffolding as Competence Grows
  variant_basis: method_sequence
  difference_from_foundation: Begin with guided participation, worked decisions, and explicit prompts, then remove those supports as the learner can operate the same real procedure independently while preserving direct reference access.
  when_to_use: The learner must acquire a complex role or procedure through actual use and early guidance can be withdrawn without changing the underlying rules.
  when_not_to_use: The simplified teaching procedure differs materially from normal operation, the learner cannot safely practice the real task, or continued prompts are part of the permanent interface.
  absorbed_from_object_id: none
- variant_id: game_design_variant_reindex_a_mature_rules_corpus_around_reference_tasks
  variant_name: Reindex a Mature Rules Corpus Around Reference Tasks
  variant_basis: method_sequence
  difference_from_foundation: Consolidate a staged or multi-volume rules corpus for experienced use by grouping related rules around lookup tasks and subjects rather than preserving the order in which those rules were originally taught or published.
  when_to_use: Experienced users already understand the operating model, related rules are dispersed across stages or volumes, and repeated retrieval is a larger cost than first-exposure sequencing.
  when_not_to_use: New users still depend on prerequisite teaching order, later stages replace the earlier conceptual model, or consolidation would hide operationally important scope boundaries or omit required dependencies without explicit signaling.
  absorbed_from_object_id: none
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

Variant `game_design_variant_preserve_stable_reference_topology_across_staged_expansions` keeps recurring categories in predictable places as a staged rules line grows. Use it when later material extends the same conceptual model; preserving topology lets users expand a known map rather than relearn where every class of rule lives.

Variant `game_design_variant_fade_instructional_scaffolding_as_competence_grows` treats guidance as temporary support around the real procedure. Early steps can be narrated or prompted heavily, but those cues should recede as competence becomes observable; the reference surface remains available even after tutorial support is removed.

Variant `game_design_variant_reindex_a_mature_rules_corpus_around_reference_tasks` treats consolidation as a change of access architecture rather than a neutral concatenation. Once users already know the game, material that entered through different learning stages can be regrouped by the questions users repeatedly ask at the table. The consolidated reference should still state its scope and exclusions explicitly so improved retrieval does not blur which operational regimes are actually supported.
