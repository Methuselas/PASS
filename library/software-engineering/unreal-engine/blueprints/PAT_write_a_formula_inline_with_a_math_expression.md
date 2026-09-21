---
object_id: PAT_write_a_formula_inline_with_a_math_expression
object_type: pattern
name: Write a Formula Inline With a Math Expression Node
library_path:
- software-engineering
- unreal-engine
- blueprints
stage_binding: 1 skeleton
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- blueprints
- math
- expression
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Write a Formula Inline With a Math Expression Node

## Pattern Rule
**IF** you need to compute a value from a formula over several inputs
**THEN** use a Math Expression node, which is a collapsed graph created by the editor from the expression typed in the node's name.

## Do
- Type the formula in the node's name (for example, `(PlayerLuck/5) * (EnemyHP/30)`).
- Wire each variable name found in the expression to its input pin — an input parameter pin is created for each variable name.
- Use the Return Value as the result of the expression.

## Don't
- Don't wire a chain of individual math nodes when a single expression is clearer.

## Checklist
- The formula is in the node's name.
- Each variable name in the expression has a wired input pin.
- The Return Value is the result of the expression.

## Notes
Example: a `Calculate Money Reward` function that uses the Math Expression `(PlayerLuck/5) * (EnemyHP/30)`.
