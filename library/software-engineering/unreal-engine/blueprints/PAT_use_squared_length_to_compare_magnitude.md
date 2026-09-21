---
object_id: PAT_use_squared_length_to_compare_magnitude
object_type: pattern
name: Use Squared Length to Compare Magnitude
library_path:
- software-engineering
- unreal-engine
- blueprints
stage_binding: 2 block
lane_fit: both
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- unreal_engine
- blueprints
- vectors
- performance
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Use Squared Length to Compare Magnitude

## Pattern Rule
**IF** you only need to know whether a vector is nonzero, or to compare its magnitude against a threshold — is the player moving, is the distance within range
**THEN** compare the vector's squared length against the squared threshold instead of taking the square root, because the square root is the expensive step and the comparison result is the same.

## Do
- Use the squared-length value (VectorLengthSquared) when the test is "is it greater than zero" or "is it within a radius."
- Square the threshold once and compare it against the squared length, so both sides are in the same units.
- Take the square root only when you actually need the true length as a value.

## Don't
- Don't compute the full length (VectorLength) just to test whether the vector is nonzero — the square root buys nothing for a zero test.
- Don't compare a squared length against an unsquared threshold; the comparison is wrong unless both sides are squared.

## Checklist
- The magnitude test uses the squared length, not the full length.
- The threshold is squared to match the squared length's units.
- The square root is taken only where the true length is needed as a value.

## Notes
A vector's length is the square root of its squared length. The square root is the expensive operation, and for a comparison — "is the velocity greater than zero," "is the distance within the radius" — it is not needed: comparing the squared length against the squared threshold gives the same true/false result. Take the square root only when the actual length is needed as a number.
