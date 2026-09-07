---
object_id: PAT_curate_modular_rules_for_safe_onboarding
object_type: pattern
name: Curate Modular Rules for Safe Onboarding
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
- onboarding
- optionality
- modules
cross_links:
- rel: related_to
  target_object_id: PAT_design_rules_artifacts_for_learning_and_retrieval
- rel: related_to
  target_object_id: PAT_define_the_intended_player_before_designing_for_them
- rel: related_to
  target_object_id: PAT_make_the_game_operable_without_hidden_designer_knowledge
reference:
  source_title: Designing TTRPGs For Dummies
  author: Martin Buinicki
confidence: high
references: []
variants:
- variant_id: game_design_variant_unlock_optional_complexity_after_core_familiarity
  variant_name: Unlock Optional Complexity After Core Familiarity
  variant_basis: method_sequence
  difference_from_foundation: Activate optional detail only after players have demonstrated familiarity with the core loop, using competence rather than first-session completeness as the trigger for adding operating burden.
  when_to_use: Optional procedures enrich decisions but are unnecessary for initial competence and can be added without changing the core rules already learned.
  when_not_to_use: The optional rule changes the core mental model, is required for a common-path decision from the first session, or the group explicitly wants the full complexity immediately.
  absorbed_from_object_id: none
---

# Curate Modular Rules for Safe Onboarding

## Pattern Rule
**IF** a game exposes enough optional or interdependent rules that a new facilitator must make configuration choices before competent play
**THEN** provide a sufficient starting configuration plus explicit dependencies and activation triggers for adding or omitting modules later
**ELSE** let the small rules surface remain directly configurable without manufacturing presets it does not need.

## Do
- Give a new facilitator a clearly sufficient first-campaign configuration instead of requiring expert knowledge of every available module.
- Identify which rules are required, which modules can be omitted safely, and which concrete play situations should trigger adding optional detail later.
- When the configuration surface is large, encode curation in a preset, campaign template, or equivalent package rather than leaving the novice with an unstructured catalog.
- Treat optionality as a knowledge-cost question: include the burden of learning enough about a module to know whether omission is safe.
- State module dependencies and interaction boundaries strongly enough that adding one option does not silently require reconstructing the whole rules architecture.
- Test the starting configuration as an actual playable path rather than assuming that individually optional modules compose safely when omitted together.

## Don't
- Require a new facilitator to survey the entire rules corpus before running a competent first campaign merely to discover which options are safe to omit.
- Present a large toolkit without a recommended starting configuration when its modules are interdependent enough to require expert curation.
- Label a module optional when users must already understand its internal rules to determine whether the rest of the game depends on it.
- Add optional detail by default merely because it exists; activate it when the campaign's actual situations justify its operating and learning cost.

## Checklist
- A first-time facilitator can identify one sufficient playable rules path without mastering the full system.
- Required rules and safely omitted modules are explicit for the starting configuration.
- Optional modules state dependencies and concrete activation triggers for later addition.
- A large modular game provides at least one ready-to-run preset, campaign template, or equivalent configuration when a plain option list would still require expert judgment.
- The proposed starting configuration has been checked as a whole for missing dependencies rather than only module by module.
- Omitting an option does not require hidden expert knowledge that the onboarding path never supplies.

## Notes
Optional rules are only easy to omit when the user can make that decision cheaply and safely. A system with many individually reasonable modules can impose a large configuration burden before play if their dependencies, activation conditions, and combined omissions are not curated. The starting configuration is therefore an executable recommendation, not a claim that one subset is universally correct. It gives novices a known-good path and makes later complexity conditional on concrete needs rather than on fear of accidentally leaving something essential out.

Variant `game_design_variant_unlock_optional_complexity_after_core_familiarity` stages optional complexity by learner readiness. It is useful when the table can operate the true core loop first and later add detail without relearning that loop; it is poor fit when the delayed procedure changes the foundation itself.
