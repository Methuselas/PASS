---
object_id: PAT_validate_a_functions_input_parameters_before_using_them
object_type: pattern
name: Validate a Function's Input Parameters Before Using Them
library_path:
- software-engineering
- unreal-engine
- blueprints
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- blueprints
- validation
- input_parameters
- defensive_programming
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Validate a Function's Input Parameters Before Using Them

## Pattern Rule
**IF** a function or macro takes input parameters that will be used in its calculations
**THEN** validate the parameters at the function's entry, before any node uses them, and run the body only on the valid branch.

## Do
- Add a Branch node as the first node of the function and wire the parameter into its Condition pin through a comparison node (for example, a Greater node checking that a face count is greater than 1).
- Connect the True pin of the Branch to the body and the Return Node, so the function computes and returns only when the parameter is valid.
- Leave the False branch empty, so an invalid parameter ends the call without running the body.

## Don't
- Don't feed an unvalidated parameter into a calculation — an invalid value produces unexpected and hard-to-find errors downstream in the graph.
- Don't skip the check on a function just because a sibling function already has it — each function's entry needs its own validation.

## Checklist
- The function's first node is a Branch on the parameter's validity.
- The body and the Return Node are reachable only from the True pin.
- An invalid parameter ends the call without running the body.

## Notes
A library function is called from many Blueprints, so it cannot trust that every caller passes a sensible value. Validating the parameters at the entry keeps the function safe no matter who calls it: a bad value is caught before it reaches the calculations, instead of producing unexpected and hard-to-find errors deep in the graph. The check belongs at the function's entry, before any node uses the parameter. Example: a dice-roll function checks that NumberOfFaces is greater than 1 before generating a random value in the range 1 to NumberOfFaces; a face count of two simulates a coin flip.
