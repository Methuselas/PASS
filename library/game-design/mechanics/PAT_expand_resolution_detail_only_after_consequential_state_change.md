---
object_id: PAT_expand_resolution_detail_only_after_consequential_state_change
object_type: pattern
name: Expand Resolution Detail Only After Consequential State Change
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
- complexity
- consequences
- operator-cost
cross_links:
- rel: related_to
  target_object_id: PAT_invoke_resolution_only_for_meaningful_uncertainty
- rel: related_to
  target_object_id: PAT_preserve_decision_relevant_state_while_compressing_resolution_procedure
- rel: related_to
  target_object_id: PAT_factor_repeated_resolution_structures_into_shared_procedures_and_data
- rel: related_to
  target_object_id: PAT_budget_mechanical_operating_cost_by_decision_value_and_activation_cadence
- rel: related_to
  target_object_id: DRILL_profile_serial_resolution_latency
- rel: related_to
  target_object_id: PAT_gate_consequential_injury_behind_a_recoverable_buffer
reference:
  source_title: Cyberpunk 2020 (2.0.2.0 Version)
  author: Mike Pondsmith and R. Talsorian Games contributors
confidence: high
references: []
variants: []
---

# Expand Resolution Detail Only After Consequential State Change

## Pattern Rule
**IF** an attempted action has a cheap branch where no consequential state changes and a richer branch where success or failure creates persistent effects
**THEN** keep the common attempt path shallow and invoke detailed consequence processing only after the state-changing branch is reached
**ELSE** use one bounded procedure when every outcome requires the same meaningful state update.

## Do
- Make misses, harmless failures, or other no-change outcomes terminate quickly.
- Put location, severity, equipment interaction, impairment, or other detailed processing behind the event that makes those distinctions relevant.
- A depletion threshold can serve as the trigger: keep routine buffer loss cheap, then activate richer injury or failure state only when the threshold is crossed, preserving overflow when it affects severity.
- Stop resolving additional sub-events when they no longer change any decision-relevant final state, unless the remaining state is explicitly important to later recovery, ownership, or campaign consequences.
- Test the state-changing branch at realistic maximum multiplicity when one declaration can generate several consequential results; if repeated consequence processing becomes the dominant cost, route compression to the procedure/state-compression owner rather than expanding this Pattern's scope.

## Don't
- Pay full consequence-processing cost for every failed attempt merely because the successful branch is detailed.
- Assume a cheap single-event procedure remains cheap when another rule can invoke it ten times inside one action.
- Continue tracing intermediate quantities after they have ceased to alter final state.

## Checklist
- The cheapest ordinary no-change path has a clear early exit.
- Detailed resolution begins at a named state-changing trigger.
- Multi-event actions have been tested at realistic maximum output rather than one event at a time.
- The procedure terminates when further detail no longer changes future decisions or persistent consequences.

## Notes
Simulation detail can be asymmetric. An attack roll may be cheap while a successful hit opens location, protection, injury, shock, and recovery state. That is efficient when the detailed branch fires only when something changed. The same architecture becomes expensive when burst, area, or multi-target rules multiply the consequence branch, so success-triggered expansion must still be tested at real cadence. Stable repeated calculations belong to `PAT_factor_repeated_resolution_structures_into_shared_procedures_and_data`; process compression that preserves consequential end state belongs to `PAT_preserve_decision_relevant_state_while_compressing_resolution_procedure`. This Pattern owns only **where the detailed branch begins**.
