---
object_id: PAT_escalate_pressure_before_a_finite_resource_reaches_zero
object_type: pattern
name: Escalate Pressure Before a Finite Resource Reaches Zero
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
- resources
- depletion
- reliability
- risk
- pressure
cross_links:
- rel: related_to
  target_object_id: PAT_budget_renewable_reserves_against_future_demands
- rel: related_to
  target_object_id: PAT_compress_resource_contents_without_erasing_resource_constraints
- rel: related_to
  target_object_id: PAT_scale_voluntary_output_with_escalating_current_risk
reference:
  source_title: Warhammer Fantasy Roleplay, First Edition
  author: Richard Halliwell, Rick Priestley, Graeme Davis, Jim Bambra, and Phil Gallagher
confidence: high
references: []
variants: []
---

# Escalate Pressure Before a Finite Resource Reaches Zero

## Pattern Rule
**IF** near-exhaustion is supposed to feel qualitatively more dangerous than merely having fewer uses remaining
**THEN** let the remaining reserve alter reliability, risk, available options, or another live pressure before the pool reaches zero
**ELSE** keep depletion linear when only the number of remaining uses is meant to matter.

## Do
- Make the pre-zero pressure visible enough that players can change behavior before the resource is fully exhausted.
- Choose a pressure curve deliberately: gradual degradation, stepped thresholds, escalating mishap risk, narrowing options, or another form should match the intended tension.
- Test several remaining-resource values rather than checking only full and empty states.
- Audit feedback when failure also consumes the same reserve; reduced reliability can create a depletion spiral that accelerates faster than the nominal resource cost suggests.
- Preserve a reason to spend from a strained pool when desperation is part of the intended experience rather than making low-resource use categorically irrational.

## Don't
- Add a sudden probability cliff near zero without checking whether one point of depletion changes reliability far more than intended.
- Make failure consume more of the same resource without testing whether the resulting spiral can remove meaningful choice too quickly.
- Hide the deterioration from players when the design expects informed conservation decisions.
- Add pre-zero penalties when ordinary depletion already creates all the pressure the subsystem needs.

## Checklist
- At least two nonzero reserve levels produce materially different risk, reliability, or option states.
- Players can recognize that the pool is becoming dangerous before it is empty.
- The pressure curve has been checked at several points for cliffs or unexpectedly flat regions.
- Any failure-to-further-depletion loop has been tested for acceleration.
- Low-reserve use can still be rational in at least one intended desperate situation when desperation is part of the design goal.

## Notes
A finite pool can create tension before exhaustion if its remaining quantity changes more than use count. The same last few points can become less reliable, more hazardous, or more restrictive, making conservation and desperation different operating states. That extra pressure is not automatically beneficial: when low reserve increases failure and failed attempts spend more reserve, a system can create a steep failure spiral. Calibrate the curve as deliberately as the pool size.
