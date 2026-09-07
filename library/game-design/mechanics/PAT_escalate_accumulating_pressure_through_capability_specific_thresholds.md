---
object_id: PAT_escalate_accumulating_pressure_through_capability_specific_thresholds
object_type: pattern
name: Escalate Accumulating Pressure Through Capability-Specific Thresholds
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
- pressure
- stress
- thresholds
- impairment
cross_links:
- rel: related_to
  target_object_id: PAT_escalate_pressure_before_a_finite_resource_reaches_zero
- rel: related_to
  target_object_id: PAT_evaluate_mechanics_by_the_decisions_and_agency_they_create
- rel: related_to
  target_object_id: PAT_budget_mechanical_operating_cost_by_decision_value_and_activation_cadence
reference:
  source_title: Warhammer Fantasy Roleplay, Third Edition
  author: Jay Little with Daniel Lovat Clark, Michael Hurley, and Tim Uren
confidence: high
references: []
variants: []
---

# Escalate Accumulating Pressure Through Capability-Specific Thresholds

## Pattern Rule
**IF** one accumulating load should impair several capabilities according to their different tolerances rather than disable the character all at once
**THEN** compare the same pressure total against capability-specific thresholds so vulnerable functions degrade first and further accumulation broadens or deepens impairment
**ELSE** use one global threshold when all affected capabilities are intended to degrade together.

## Do
- Identify which capabilities share the pressure source and which rating or threshold expresses each capability's tolerance.
- Apply impairment only to capabilities whose threshold has actually been exceeded so a weak social, cognitive, physical, or technical function can deteriorate before stronger ones.
- Let additional pressure beyond a threshold increase the impairment when the design needs rising severity rather than a binary healthy/impaired switch.
- Define a higher collapse threshold separately when total overload should eventually remove participation or force recovery.
- Allow two pressure domains to create a named compound state when their simultaneous activation should unlock additional consequences that neither produces alone.
- Make recovery reduce the underlying pressure so capability recovery follows automatically from the same thresholds instead of requiring independent repair of every derived penalty.
- Test characters with uneven capability ratings; equal-stat examples cannot reveal whether the threshold architecture is doing useful work.

## Don't
- Give every affected capability the same threshold while claiming the mechanic represents differentiated tolerance.
- Apply a global penalty to all functions as soon as the weakest threshold is crossed unless cascading impairment is the explicit goal.
- Create separate impairment counters for every capability when all of them can be derived unambiguously from one pressure total.
- Add a compound overload state whose extra consequence does not change behavior beyond the penalties already active.
- Let escalating penalties create an accidental no-recovery spiral without checking how characters can change behavior before collapse.

## Checklist
- One pressure total can be compared against at least two materially different capability thresholds.
- A representative uneven character can have one affected capability while another remains unaffected.
- Additional accumulation either broadens the set of impaired capabilities, deepens an existing penalty, or both according to an explicit rule.
- Any higher collapse threshold and any compound state have separate, testable trigger conditions.
- Recovery from pressure automatically removes derived impairments at the correct thresholds.
- Players can see enough of the pressure and threshold state to make informed conservation, retreat, or recovery decisions when those decisions are intended.

## Notes
This architecture turns one accumulating burden into a **progressive impairment surface** rather than a single countdown to failure. If a character has different tolerances across affected capabilities, the same pressure value can first compromise the weakest function, then progressively reach stronger ones. It differs from a finite resource becoming dangerous near zero: here the tracked quantity is an accumulating load, and its decision value comes from crossing several capability-relative thresholds on the way toward overload.
