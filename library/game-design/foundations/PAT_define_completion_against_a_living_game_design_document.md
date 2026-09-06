---
object_id: PAT_define_completion_against_a_living_game_design_document
object_type: pattern
name: Define Design Completion Against Current-Version Fundamentals
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
- scope
- completion
- gdd
- iteration
cross_links:
- rel: related_to
  target_object_id: PAT_define_the_intended_player_before_designing_for_them
- rel: related_to
  target_object_id: PAT_make_the_game_operable_without_hidden_designer_knowledge
- rel: related_to
  target_object_id: PAT_cover_required_production_functions_with_explicit_ownership
- rel: related_to
  target_object_id: PAT_keep_game_design_specification_living_and_dependency_aware
- rel: related_to
  target_object_id: PAT_treat_optional_modules_as_removable_dependency_sets
- rel: related_to
  target_object_id: PAT_distinguish_future_hooks_from_current_supported_functionality
reference:
  source_title: Designing TTRPGs For Dummies
  author: Martin Buinicki
confidence: high
references: []
variants: []
---

# Define Design Completion Against Current-Version Fundamentals

## Pattern Rule
**IF** a game has a defined current-version scope
**THEN** name the fundamentals that scope requires, give each one a concrete completion condition, and call the design complete when those fundamentals are implemented or documented, integrated with their dependencies, and testable as a whole
**ELSE** do not judge completion against every feature the setting or future product line could conceivably support.

## Do
- Define the current version's required fundamentals before progress is measured.
- Include the systems, content domains, interfaces, and production-facing design requirements necessary to deliver the intended experience, not every desirable addition.
- Distinguish required fundamentals from experiments, enhancements, expansions, stretch goals, optional modules, and backlog ideas.
- Give each fundamental a concrete completion condition rather than relying on states such as "mostly done."
- Treat the design as complete when every current-version fundamental is specified, implemented or documented, integrated with its dependencies, and testable as part of the whole.
- Use the defined scope to distinguish a missing fundamental from a merely absent feature.
- Once the defined fundamentals are complete, classify new ideas honestly as revisions, enhancements, expansions, optional modules, or next-version work rather than automatically reopening the current design.
- Evaluate release readiness as a later gate that can additionally require playtesting, regression testing, independent operability, editing, production, packaging, and delivery validation.

## Don't
- Add new fundamentals indefinitely merely because another idea occurred during development.
- Confuse time already invested in a feature with its importance to the intended game.
- Let local polishing prevent progress toward a testable whole.
- Declare the design unfinished merely because further improvement is possible.
- Declare a product release-ready merely because all design-completion conditions are satisfied.
- Treat requests for additional systems as proof that the current version was incomplete when those systems were outside its defined fundamentals.
- Measure completeness by feature count instead of whether the scoped experience is fully supported.

## Checklist
- The current version has an explicit scope and intended experience.
- Every required fundamental is named somewhere recoverable.
- Each fundamental has a concrete completion condition.
- Optional, expansion, and next-version ideas are distinguishable from current-version requirements.
- All current-version fundamentals are specified, implemented or documented, integrated, and testable as a whole before the design is called complete.
- Release readiness is evaluated separately from design completeness.
- The project can explain why an absent feature is either a missing fundamental or intentionally outside the current version's scope.
- The design-completion gate is explicit: fundamentals defined -> fundamentals implemented -> dependencies integrated -> whole testable.

## Notes
Completeness is measured against the defined scope of the current version, not against every feature the game could eventually support. *Star Frontiers: Alpha Dawn* supplied a complete science-fiction roleplaying game for planetary adventure even though player characters could not yet operate starships as a full subsystem. *Knight Hawks* later expanded the product line into starship design, spaceship skills, space movement, combat, and campaign play. The expansion added scope; its existence does not retroactively make the original design incomplete.

The useful boundary is between **design completion** and **release readiness**. A design can have all required fundamentals integrated and testable while still needing validation, editing, production, or delivery work before publication. Finish the scoped fundamentals, validate the whole, then stop treating every optional improvement as evidence that the current design is unfinished.
