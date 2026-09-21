---
object_id: PAT_use_function_local_variables_for_temporary_values
object_type: pattern
name: Use Function Local Variables for Temporary Values
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
- variables
- scope
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Use Function Local Variables for Temporary Values

## Pattern Rule
**IF** a piece of logic needs a variable that holds a temporary value used only inside that logic
**THEN** create it as a local variable inside a function, not as a Blueprint-level variable.

## Do
- Create a function for the logic that needs the temporary value.
- Add the temporary value as a local variable in the function; while editing the function it appears in a LOCAL VARIABLES category in the My Blueprint panel.
- Let the local variable's value be discarded at the end of the function's execution.

## Don't
- Don't promote a temporary value to a Blueprint-level variable just because the logic is complex — that pollutes the Blueprint's state with a value that only makes sense inside one computation.
- Don't expect a local variable to persist across calls — its value is discarded when the function finishes.

## Checklist
- The temporary value is a local variable inside a function, not a Blueprint variable.
- The local variable is visible only within the function.
- The value is discarded at the end of the function's execution.

## Notes
Local variables are only visible within the function they are declared in, and their values do not persist across calls. Example: a `PartialResult` float local variable inside a `CalculateTargetGoal` function.
