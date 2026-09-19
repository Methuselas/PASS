---
object_id: PAT_make_blueprint_function_pure_when_it_only_computes
object_type: pattern
name: Make a Blueprint Function Pure When It Only Computes
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
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Make a Blueprint Function Pure When It Only Computes

## Pattern Rule
**IF** you are creating a Blueprint function that only computes and returns a value without modifying any state
**THEN** mark it Pure so it has no execution pins and can be used inside expressions.

## Do
- Mark a function Pure when it just returns a value — a get-type function that computes a result from its inputs and changes nothing.
- Use a Pure function inside an expression, where a node with execution pins cannot be placed.
- Keep the function free of any action that changes a variable, so its result depends only on its inputs.

## Don't
- Don't mark a function Pure if it changes any variable of its Blueprint — a Pure function must not modify state.
- Don't expect to drive a Pure function along an execution path; it has no execution pins, so it cannot be sequenced.
- Don't use a non-Pure function where an expression is required; only a Pure function can sit inside an expression.

## Checklist
- The function has no execution pins and can be placed inside an expression.
- The function returns a value and does not modify any variable of its Blueprint.
- The function's result depends only on its inputs.

## Notes
A Pure function has no execution pins, so it can be used inside expressions where a node with execution pins cannot be placed. Because it has no execution flow, it should not modify the variables of its Blueprint; it is mostly used as a get-type function that just returns a value. The visual difference is that a standard function carries execution pins while a Pure function does not. Marking a function Pure is a declaration that it is a computation, not a sequence of side effects.
