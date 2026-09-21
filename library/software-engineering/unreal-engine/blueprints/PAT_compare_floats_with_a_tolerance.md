---
object_id: PAT_compare_floats_with_a_tolerance
object_type: pattern
name: Compare Floats with a Tolerance
library_path:
- software-engineering
- unreal-engine
- blueprints
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: PAT_treat_floating_point_arithmetic_as_approximate
tags:
- unreal_engine
- blueprints
- floating_point
cross_links:
- rel: related_to
  target_object_id: PAT_store_meter_values_as_a_normalized_fraction
- rel: related_to
  target_object_id: PAT_treat_floating_point_arithmetic_as_approximate
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Compare Floats with a Tolerance

## Pattern Rule
**IF** you compare two floating-point values for equality — is the meter full, does the value equal the target
**THEN** use a tolerance-based comparison (Nearly Equal with an error tolerance) instead of strict equality, because floating-point values rarely land exactly on the target.

## Do
- Use Nearly Equal (float) with an Error Tolerance when testing whether a float equals a value.
- To test "greater than or equal" on floats, combine Greater with Nearly Equal under an OR, since there is no tolerance-aware greater-equal node.
- Keep the tolerance small enough to mean "equal for our purposes" but large enough to absorb floating-point error.

## Don't
- Don't test a float for strict equality — accumulated adds and subtracts leave it a hair off the target, so the test fails when it should pass.
- Don't use a tolerance so large that distinct values compare as equal.

## Checklist
- Equality tests on floats use a tolerance, not strict equality.
- A "greater than or equal" test on floats is Greater OR Nearly Equal.
- The tolerance is small but nonzero.

## Notes
This is the Unreal Blueprint specialization of `PAT_treat_floating_point_arithmetic_as_approximate`: it records the engine-specific Nearly Equal node and the Blueprint construction for a tolerance-aware greater-or-equal test.

Floating-point values do not land exactly on their targets: a meter filled by repeated small adds ends up a hair below 1.0, so a strict equality test against 1.0 fails. A tolerance-based comparison (Nearly Equal with an Error Tolerance) treats values within the tolerance as equal. Because there is no tolerance-aware greater-equal node, "greater than or equal" on floats is built as Greater OR Nearly Equal.
