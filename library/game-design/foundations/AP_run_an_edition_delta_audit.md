---
object_id: AP_run_an_edition_delta_audit
object_type: ap
name: Run an Edition Delta Audit
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
- editions
- comparison
- refactoring
- behavior
- complexity
- regression
cross_links:
- rel: supports
  target_object_id: PAT_use_the_defining_affordances_of_an_adopted_game_system
- rel: supports
  target_object_id: PAT_preserve_behavioral_compatibility_when_replacing_inherited_mechanics
- rel: supports
  target_object_id: PAT_evaluate_mechanics_by_the_decisions_and_agency_they_create
- rel: supports
  target_object_id: PAT_budget_mechanical_operating_cost_by_decision_value_and_activation_cadence
- rel: supports
  target_object_id: PAT_preserve_decision_relevant_state_while_compressing_resolution_procedure
- rel: supports
  target_object_id: PAT_make_the_game_operable_without_hidden_designer_knowledge
- rel: supports
  target_object_id: PAT_design_rules_artifacts_for_learning_and_retrieval
- rel: supports
  target_object_id: PAT_curate_modular_rules_for_safe_onboarding
- rel: supports
  target_object_id: PAT_reuse_core_resolution_grammar_before_adding_new_mechanics
- rel: related_to
  target_object_id: AP_run_an_evidence_driven_playtest_revision_cycle
reference:
  source_title: 'Twilight: 2000 (1st Edition) and Twilight: 2000 Version 2.2'
  author: Frank Chadwick; David Nilsen, Loren Wiseman, and Lester Smith
confidence: high
references: []
variants: []
---
# Run an Edition Delta Audit

## Objective
Compare successive editions by the behavior, state, operator work, and practical identity they preserve, improve, relocate, regulate, or lose. The audit is complete when each material delta has been classified with evidence and the final comparison states gains, regressions, tradeoffs, unchanged strengths, and unresolved questions without assuming that newer, shorter, or more unified rules are automatically better.

## Steps / Flow
1. **Entry gate — establish comparability.** Identify two versions that address the same game or inherited design problem and choose at least one equivalent player-facing task, subsystem, or information domain. If no meaningful equivalence can be established, narrow the comparison to the shared task or stop rather than manufacturing a one-to-one delta.
2. **Establish each edition's baseline independently.** Use **Use the Defining Affordances of an Adopted Game System** to record what each version promises, which affordances define its practical identity, and which recurring procedures actually deliver those affordances before comparing them.
3. **Classify the structural delta.** For every major comparable subsystem, classify the change as preserved, expanded, compressed, replaced, relocated, or lost. Use **Reuse Core Resolution Grammar Before Adding New Mechanics** to distinguish genuine grammar simplification or refactoring from a surface rewrite that merely moves exceptions elsewhere.
4. **Measure behavior before cost.** Use **Evaluate Mechanics by the Decisions and Agency They Create** to record the player decisions, sources of outcome control, and repeated behavior produced by the earlier and later procedures. Then use **Budget Mechanical Operating Cost by Decision Value and Activation Cadence** to record Human Operations Per Resolution (HOPR), Time Between Meaningful Decisions (TBMD), retrieval burden, state servicing, activation cadence, and aggregate operating load added or removed by the change.
5. **Track consequential state.** Use **Preserve Decision-Relevant State While Compressing Resolution Procedure** to identify which final states, distinctions, and campaign consequences remain distinguishable after simplification or replacement. If a newer procedure is cheaper only because a later choice or consequence disappeared, record that as a tradeoff rather than free efficiency.
6. **Audit usability separately from mechanics.** Use **Design Rules Artifacts for Learning and Retrieval** to compare learning path, reference locality, and prerequisite order. Use **Curate Modular Rules for Safe Onboarding** to compare starting configurations, safe omissions, and expansion triggers. Use **Make the Game Operable Without Hidden Designer Knowledge** separately to test whether the user must reconstruct unstated designer intent. Keep visual preference separate from operational evidence such as lookup speed and legibility.
7. **Check where complexity went.** Use **Budget Mechanical Operating Cost by Decision Value and Activation Cadence** to determine whether cost was removed, precomputed, automated, shifted to another cadence, or relocated into another high-frequency rule. When several unrelated subsystems reproduce the same multiplier or defect, treat it as an engine-level assumption and test that assumption directly.
8. **Distinguish refactoring from counterstructure.** If the later edition preserves the root pressure and surrounds it with ceilings, exceptions, exposure rules, facilitator procedures, or compensating systems, classify that as regulation or mitigation rather than claiming the root problem was removed.
9. **Evidence branch.** Treat designer claims about speed, clarity, realism, compatibility, or preserved identity as hypotheses. If the procedures or artifacts can be executed, test them. If evidence is incomplete, mark the affected delta unresolved and do not promote the claim into the conclusion.
10. **Migration and compatibility gate.** Use **Preserve Behavioral Compatibility When Replacing Inherited Mechanics** to record what existing characters, content, learned procedures, or facilitator habits must be converted, relearned, or abandoned, then test whether the intended capabilities, relative relationships, procedures, and play identity survive. A change may be architecturally cleaner while still imposing a meaningful migration cost or experiential repositioning.
11. **Completion check.** Produce an explicit ledger of gains, regressions, tradeoffs, unchanged architectural strengths, migration costs, and unresolved claims. Stop only when every material comparison point is supported by an observed procedure, a directly inspectable artifact, or an explicit unresolved status rather than by edition age or marketing language.

## Notes
Edition work is vulnerable to false simplification narratives. A redesign can improve reference locality or common grammar while losing a distinctive player behavior, and it can reduce cost in one procedure while creating a new hotspot elsewhere. A later edition can also understand an inherited pressure more clearly and add better counterweights without actually removing the underlying multiplier. The useful comparison preserves both sides of that ledger and separates removed causes from mitigated symptoms.
