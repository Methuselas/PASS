---
object_id: AP_run_a_simulation_budget_audit
object_type: ap
name: Run a Simulation Budget Audit
library_path:
- game-design
- foundations
stage_binding: 2 block
lane_fit: both
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- simulation
- complexity
- HOPR
- TBMD
- resources
- cadence
cross_links:
- rel: supports
  target_object_id: PAT_evaluate_mechanics_by_the_decisions_and_agency_they_create
- rel: supports
  target_object_id: PAT_budget_mechanical_operating_cost_by_decision_value_and_activation_cadence
- rel: supports
  target_object_id: PAT_allocate_simulation_detail_by_expected_persistence
- rel: supports
  target_object_id: PAT_preserve_decision_relevant_state_while_compressing_resolution_procedure
- rel: supports
  target_object_id: PAT_account_for_the_intended_play_environment_before_freezing_the_design
- rel: supports
  target_object_id: PAT_retest_revisions_before_treating_them_as_validated
- rel: related_to
  target_object_id: DRILL_profile_serial_resolution_latency
reference:
  source_title: 'Twilight: 2000 (1st Edition) and Twilight: 2000 Version 2.2'
  author: Frank Chadwick; David Nilsen, Loren Wiseman, and Lester Smith
confidence: high
references: []
variants: []
---
# Run a Simulation Budget Audit

## Objective
Audit an executable subsystem to determine which simulation detail should remain explicit, which procedure should be compressed, and where complexity is affordable based on decision value, persistence, activation cadence, and whole-table operating cost. The audit is complete when every retained cost has a demonstrated play value and every proposed compression has been rerun without losing required decisions or consequential state.

## Steps / Flow
1. **Entry gate — use an executable subsystem.** Enter only when the subsystem can be run from trigger to termination with enough representative state to expose its normal decisions, branches, and bookkeeping. If the procedure is still only an idea, finish the executable procedure before auditing its budget.
2. **Name the intended pressure.** Use **Evaluate Mechanics by the Decisions and Agency They Create** to state the player-facing pressure, choice, or behavior the subsystem is supposed to produce. Preserve that purpose as an invariant through the audit.
3. **Name the state that must survive.** Use **Allocate Simulation Detail by Expected Persistence** to identify which distinctions need to persist because later play actually consumes them. Use **Preserve Decision-Relevant State While Compressing Resolution Procedure** to mark any state whose loss would erase a later choice, consequence, or causal feedback.
4. **Measure the common operating path.** Use **Budget Mechanical Operating Cost by Decision Value and Activation Cadence** to trace the representative procedure, separate meaningful decisions from human servicing work such as arithmetic, lookups, translation, reminders, branches, and state writes, and record where that cost is paid: common runtime, conditional runtime, creation, downtime, preparation, construction, or another cadence.
5. **Separate local and aggregate cost.** Continue with **Budget Mechanical Operating Cost by Decision Value and Activation Cadence** to count event and actor throughput as well as per-resolution complexity. Distinguish player specialization from facilitator integration cost, and distinguish a subsystem's local cost from the cost of keeping its state coherent with other simultaneously active domains.
6. **Check environmental assumptions at real frequency.** Use **Account for the Intended Play Environment Before Freezing the Design** to test the procedure in the actual medium, table structure, automation level, and activation cadence it is expected to face. A genre-common special mode is audited at its real frequency even when the rulebook isolates it in a separate section.
7. **Prototype compression only where cost exceeds value.** Use **Preserve Decision-Relevant State While Compressing Resolution Procedure** to test categorical compression, precomputation, better reference locality, a coarser intermediate model, or another simplification. Do not remove a distinction merely because it is detailed; remove or redesign work that does not buy a decision, consequence, or useful causal state.
8. **Advance gate — rerun the same pressure.** Use **Retest Revisions Before Treating Them as Validated** to rerun the affected procedure and the nearby dependencies that can inherit the compression. Advance only if the intended decisions, consequences, and marked persistent state remain available. If the rerun loses one, return to the owner of that lost decision or state and restore it, choose a different compression, or reject the compression.
9. **Aggregate gate — combine the surviving costs.** Use **Budget Mechanical Operating Cost by Decision Value and Activation Cadence** to recheck the subsystem alongside the other domains likely to be active in the same session. Individually justified rules can still exceed a usable human operating budget when combat, gear, magic, hacking, vehicles, economy, minions, or facilitator state become active together.
10. **Completion check.** Stop when every retained cost has an explicit decision, consequence, persistence, or environmental reason; every removed cost has survived a rerun; and the aggregate operating budget is acceptable for the intended play environment. Otherwise route the remaining hotspot back to the Pattern that owns the failing decision, state distinction, or environment assumption and iterate.

## Notes
A simulation budget is not a target rule count. A once-per-character lifepath, a weekly recovery procedure, and an every-attack branch can tolerate very different operating costs. The audit protects purposeful friction while locating human servicing work that can be compressed without flattening the game. Locally justified complexity still accumulates globally, and interoperability can improve the game while also creating integration work. Measure both the cost of each subsystem and the cost of keeping their shared state coherent.
