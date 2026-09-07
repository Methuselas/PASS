---
object_id: AP_design_character_roles_and_options
object_type: ap
name: Design Character Roles and Options
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
- roles
- options
- advancement
- balance
cross_links:
- rel: supports
  target_object_id: PAT_derive_character_capabilities_from_expected_play
- rel: supports
  target_object_id: PAT_choose_character_capability_granularity_by_play_distinctions
- rel: supports
  target_object_id: PAT_define_roles_by_distinct_world_interfaces
- rel: supports
  target_object_id: PAT_choose_specialization_boundaries_by_permission_and_economic_effect
- rel: supports
  target_object_id: PAT_reuse_capability_effect_grammar_across_fictional_sources
- rel: supports
  target_object_id: PAT_price_character_options_by_mechanical_leverage_and_constraint
- rel: supports
  target_object_id: PAT_price_drawbacks_by_the_constraint_they_actually_impose
- rel: supports
  target_object_id: PAT_audit_character_economy_exchange_rates_across_creation_and_advancement
- rel: supports
  target_object_id: PAT_treat_near_mandatory_role_options_as_role_infrastructure
- rel: supports
  target_object_id: PAT_attach_persistent_costs_to_capability_gains
- rel: supports
  target_object_id: PAT_keep_persistent_capability_dependencies_local_and_explicit
- rel: supports
  target_object_id: PAT_balance_character_roles_by_consequential_contribution
- rel: supports
  target_object_id: PAT_make_character_creation_preview_recurring_play
- rel: supports
  target_object_id: PAT_use_editable_templates_as_onboarding_scaffolds
- rel: supports
  target_object_id: PAT_make_character_background_mechanically_causal
- rel: supports
  target_object_id: PAT_reduce_initial_choice_load_without_erasing_later_option_space
- rel: supports
  target_object_id: PAT_treat_overlapping_progression_packages_as_reachable_ceilings
confidence: high
references: []
variants: []
---

# Design Character Roles and Options

## Objective
Create a character capability and option architecture that exposes the distinctions recurring play actually uses, gives roles or specializations meaningful interfaces where the game needs them, prices leverage and constraints coherently across creation and advancement, and lets character creation teach the decisions the game will continue asking players to make.

## Steps / Flow
1. **Enter with recurring play already defined.** Know what characters are expected to attempt repeatedly, which decisions belong to players, and which differences between characters the game wants to make consequential. If expected play is still only a genre label or list of fictional archetypes, return to the game foundation before building a character catalog.
2. **Derive the capability surface from play.** Use **Derive Character Capabilities from Expected Play** to identify the actions, permissions, resources, resistances, relationships, and other competencies the game repeatedly queries. Avoid importing a conventional attribute or skill list until each element has a job in the intended play loop.
3. **Choose the granularity of those capabilities.** Use **Choose Character Capability Granularity by Play Distinctions** to split or combine capabilities according to distinctions that repeatedly change decisions. If two labels are rarely distinguished in play, merge them; if one broad capability hides strategically different activities the game cares about, separate them.
4. **Create formal roles only when they provide distinct interfaces.** If the game uses classes, careers, playbooks, professions, packages, or another role architecture, use **Define Roles by Distinct World Interfaces** so each role changes how a character can access, influence, interpret, or survive the game world rather than merely rearranging small numeric bonuses. When a role or background represents prior life, use **Make Character Background Mechanically Causal** so the fiction explains present capabilities, possessions, permissions, or future routes. If the game does not need formal roles, skip this branch and let capabilities/options carry differentiation directly.
5. **Define specialization boundaries only where specialization is a real choice.** If characters can specialize inside a broader capability or role, use **Choose Specialization Boundaries by Permission and Economic Effect** to decide whether the boundary changes what the character may attempt, how efficiently they may attempt it, or what opportunity cost they accept. Do not add nested specialty labels that produce neither a permission nor a meaningful economic distinction.
6. **Reuse effect grammar when different fiction produces the same mechanical question.** If backgrounds, species, gear, powers, training, cyberware, magic, or other sources grant mechanically similar effects, use **Reuse Capability Effect Grammar Across Fictional Sources** so equivalent bonuses, permissions, costs, and state changes use recognizable language. Preserve source-specific fiction without creating separate mechanical dialects for the same effect.
7. **Price positive options by actual leverage.** Use **Price Character Options by Mechanical Leverage** to compare frequency, breadth, reliability, action-economy effect, stacking, permission value, and consequence reduction rather than pricing by how dramatic an option sounds in fiction. Test combinations, not just isolated options, when leverage compounds.
8. **Price drawbacks by the constraint they actually impose.** If disadvantages, flaws, debts, obligations, restrictions, vulnerabilities, or other drawbacks purchase value, use **Price Drawbacks by the Constraint They Actually Impose**. Reduce compensation when a drawback is easy to avoid, rarely activated, voluntarily beneficial, or already implied by the character concept; increase scrutiny when it reliably removes options or creates recurring exposure.
9. **Audit creation and advancement as one economy.** If the same or comparable capabilities can be acquired at multiple lifecycle stages, use **Audit Character Economy Exchange Rates Across Creation and Advancement** to find cheaper alternate routes, conversion loops, front-loaded bargains, or advancement prices that invalidate creation choices. When several progression packages expose the same advancement territory, use **Treat Overlapping Progression Packages as Reachable Ceilings** to distinguish duplicate access from intentionally deeper mastery. Repair the exchange rate or permission boundary rather than relying on players not to notice the arbitrage.
10. **Move near-mandatory role taxes into the role's infrastructure.** If nearly every competent member of a role must buy the same option to perform the role's advertised function, use **Treat Near-Mandatory Role Options as Role Infrastructure**. Make the function part of the role/package or redesign the choice so declining it remains genuinely viable.
11. **Attach persistent costs only when capability should create ongoing dependency.** If a powerful capability is supposed to generate maintenance, obligation, exposure, resource demand, vulnerability, or future constraint, use **Attach Persistent Costs to Capability Gains** to make that cost recur in play rather than existing only as acquisition flavor. When the dependency exists, use **Keep Persistent Capability Dependencies Local and Explicit** so the player can see what the capability depends on and what happens when the dependency is disrupted. Skip this branch when ongoing cost is not part of the intended tradeoff.
12. **Balance roles by consequential contribution, not identical output.** If formal roles exist, use **Balance Character Roles by Consequential Contribution** to compare whether each role can make meaningful decisions and alter outcomes across the situations the game promises. Do not force identical damage, spotlight time, or task coverage when asymmetric contribution is part of the design; instead repair roles that routinely lack consequential agency.
13. **Make creation teach recurring play.** Use **Make Character Creation Preview Recurring Play** so the choices, tradeoffs, vocabulary, and information architecture used during creation resemble the decisions players will continue making. If the initial catalog exceeds what a novice can evaluate, use **Reduce Initial Choice Load Without Erasing Later Option Space** to narrow the first decision while preserving later authorship. If the game benefits from fast starts or novice scaffolding, use **Use Editable Templates as Onboarding Scaffolds** to offer ready-to-play examples that remain editable rather than disguising fixed characters as customization.
14. **Run the character-architecture gate with representative builds.** Create or simulate several characters that pursue different viable concepts, including at least one non-obvious build and, where relevant, one advancement path. Check that important capabilities appear at useful granularity and option prices reflect leverage; where the corresponding branches exist, verify that roles expose distinct interfaces, drawbacks bite as priced, creation/advancement exchange rates do not create a dominant arbitrage route, and supported roles can contribute consequentially. Route failures back to the smallest owning Pattern instead of compensating with broad global bonuses.
15. **Close when differentiation is both legible and playable.** Completion requires a capability model tied to expected play, option economics that survive representative combinations and lifecycle transitions, and a creation process that communicates the game's recurring choices. Role, specialization, persistent-cost, drawback, advancement, and template branches are required only when the current game actually uses them.

## Notes
This protocol does not require classes, point-buy, disadvantages, advancement, or templates. It orders those decisions when they exist so character fiction, mechanical permission, economics, and recurring play stay aligned. The central gate is not whether every build has the same numbers; it is whether character differences create intentional, intelligible, and consequential differences in play without hidden taxes or exploitable exchange rates.
