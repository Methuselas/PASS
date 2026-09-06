---
object_id: AP_design_and_integrate_a_core_resolution_system
object_type: ap
name: Design and Integrate a Core Resolution System
library_path:
- game-design
- mechanics
stage_binding: 0 design
lane_fit: both
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- mechanics
- resolution
- integration
- uncertainty
- complexity
cross_links:
- rel: supports
  target_object_id: PAT_invoke_resolution_only_for_meaningful_uncertainty
- rel: supports
  target_object_id: PAT_decide_whether_a_mechanic_acts_on_the_player_or_the_character
- rel: supports
  target_object_id: PAT_choose_a_randomizer_by_the_uncertainty_profile_it_must_produce
- rel: supports
  target_object_id: PAT_reuse_core_resolution_grammar_before_adding_new_mechanics
- rel: supports
  target_object_id: PAT_add_resolution_factors_only_when_they_expose_actionable_causes
- rel: supports
  target_object_id: PAT_build_complete_resolution_procedures_incrementally
- rel: supports
  target_object_id: PAT_define_temporal_priority_by_the_advantage_it_grants
- rel: supports
  target_object_id: PAT_factor_repeated_resolution_structures_into_shared_procedures_and_data
- rel: supports
  target_object_id: PAT_preserve_decision_relevant_state_while_compressing_resolution_procedure
- rel: supports
  target_object_id: PAT_budget_mechanical_operating_cost_by_decision_value_and_activation_cadence
- rel: supports
  target_object_id: PAT_automate_mechanical_maintenance_without_hiding_causality
confidence: high
references: []
variants: []
---

# Design and Integrate a Core Resolution System

## Objective
Create a coherent core resolution system that invokes procedure only for consequential uncertainty, uses an uncertainty model suited to the intended experience, reuses one recognizable rules grammar where possible, carries actions from trigger to terminal state, and remains affordable to operate at the cadence and composition where play will actually use it.

## Steps / Flow
1. **Enter with defined actions and consequences.** The entry state is a game foundation that can name representative actions, meaningful success/failure states, and the kinds of uncertainty the game intends to expose. If those cannot be named, return to foundation design rather than choosing dice or procedures in a vacuum.
2. **Decide when resolution should fire.** Use **Invoke Resolution Only for Meaningful Uncertainty** to separate inevitable or low-stakes outcomes from states where success and failure materially change risk, cost, time, information, access, position, resources, or another meaningful game state. Remove checks whose failure has no consequential answer before designing their arithmetic.
3. **Resolve the player-versus-character boundary when real-world performance enters the mechanic.** If puzzles, physical actions, acting skill, memory, knowledge, or real-time pressure can determine fictional outcomes, use **Decide Whether a Mechanic Acts on the Player or the Character** to state whether competence belongs to the player, the character, or a deliberate hybrid. If the mechanic is purely character-facing, skip this branch.
4. **Choose the uncertainty device from required behavior.** If the system needs randomness, use **Choose a Randomizer by the Uncertainty Profile It Must Produce** to specify probability shape, granularity, useful result information, competence/difficulty modification, stateful versus independent uncertainty, and handling burden before committing to dice, cards, or another device. If no randomness is needed, preserve the deterministic structure and continue.
5. **Establish one reusable resolution grammar.** Use **Reuse Core Resolution Grammar Before Adding New Mechanics** to map representative tasks onto the same primitives and result language where they ask the same rules question. Extend or refactor the grammar when recurring gaps appear; create a specialized subsystem only when the activity genuinely needs a different decision structure or experience.
6. **Add situational factors only when they buy actionable causality.** Use **Add Resolution Factors Only When They Expose Actionable Causes** to decide which modifiers, tags, conditions, or categories deserve explicit mechanical representation. If a factor does not change what participants can understand, prepare for, choose, or respond to, fold it into a coarser state instead of expanding the common path.
7. **Build a complete baseline before layering detail.** Use **Build Complete Resolution Procedures Incrementally** to carry one representative action from trigger through inputs, branch conditions, state changes, resource expenditure, and termination. Gate advance on a smallest complete procedure that works end to end; then add mechanics one at a time at dependency-correct insertion points and retest the whole affected path after each addition.
8. **Define order only where order grants advantage.** If acting earlier, interrupting, reacting, or sequencing participants changes opportunity, use **Define Temporal Priority by the Advantage It Grants** to make that advantage explicit and choose an ordering method that expresses it. If order does not alter a consequential opportunity, do not add initiative machinery merely by convention.
9. **Factor repeated structure after the procedure is trustworthy.** When several actions repeat the same invariant sequence or data, use **Factor Repeated Resolution Structures into Shared Procedures and Data** so one shared owner replaces duplicated handling without erasing meaningful differences. Do not abstract before the repeated behavior is understood well enough to name the invariant.
10. **Compress process without erasing decision-relevant aftermath.** If a detailed procedure is expensive but its output states matter, use **Preserve Decision-Relevant State While Compressing Resolution Procedure** to reduce process granularity while keeping the injuries, component states, exposure, access loss, positioning, or other consequences that still change later decisions.
11. **Run the operating-cost gate at real cadence and composition.** Use **Budget Mechanical Operating Cost by Decision Value and Activation Cadence** to measure arithmetic, lookup, branch handling, state writes, maintenance, serial latency, and stacked conditional burden against the decisions and consequences the system buys. If cost exceeds value, route the defect back to the smallest owner: remove a low-value factor, compress procedure, refactor repeated structure, or revisit the grammar rather than merely asking players to tolerate more work.
12. **Use automation only as a servicing reduction.** If software or tooling will execute bookkeeping, use **Automate Mechanical Maintenance Without Hiding Causality** to remove arithmetic, lookup, timers, or derived-state servicing while keeping player-facing causes and state changes inspectable. If performing the work is itself intended play, keep it visible instead of automating away the decision.
13. **Close with representative end-to-end proofs.** The system is ready to hand to broader content design only when representative common actions resolve from trigger to terminal state, similar rules questions share recognizable grammar, meaningful factors expose usable causes, ordering exists only where it changes opportunity, and observed operating burden remains proportionate under realistic repetition and composition. Any failure routes back to the Pattern that owns the decision rather than being patched at the end of the chain.

## Notes
The protocol deliberately chooses semantics before arithmetic and integration before optimization. Randomness, player-facing challenges, temporal ordering, compression, and automation are conditional branches rather than universal requirements. A core resolver earns its place by concentrating meaningful uncertainty into legible decisions at an affordable operating cost, not by maximizing mechanical novelty or detail.
