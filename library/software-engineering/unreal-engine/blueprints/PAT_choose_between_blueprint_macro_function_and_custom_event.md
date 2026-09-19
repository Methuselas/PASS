---
object_id: PAT_choose_between_blueprint_macro_function_and_custom_event
object_type: pattern
name: Choose Between Blueprint Macro, Function, and Custom Event
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

# Choose Between Blueprint Macro, Function, and Custom Event

## Pattern Rule
**IF** you are organizing a group of actions into a reusable node and must choose between a macro, a function, and a custom event
**THEN** let the capabilities the node needs decide — all three accept input parameters, but they differ in output parameters, execution paths, cross-Blueprint calls, latent actions, and timeline nodes.

## Do
- Use a function or a custom event when the node must be callable from another Blueprint; a macro cannot be called across Blueprints.
- Use a macro or a function when the node must return a value through an output parameter; a custom event has no output parameters.
- Use a macro when the node needs multiple execution paths through input and output execution pins; functions and events have a single path.
- Use a macro or a custom event when the node must contain latent actions such as a delay; a function cannot.
- Use a custom event when the node must contain timeline nodes; macros and functions cannot.

## Don't
- Don't reach for a macro when the node must be called from another Blueprint — a macro is local to its own Blueprint.
- Don't use a custom event to return a value — it has no output parameters.
- Don't put a timeline node in a macro or a function — only a custom event supports timeline nodes.
- Don't pick a form by habit; pick it from the capabilities the node actually needs.

## Checklist
- The chosen form supports every capability the node needs: output parameters, multiple execution paths, cross-Blueprint calls, latent actions, and timeline nodes.
- A macro is used only when the node stays within its own Blueprint.
- A custom event is used when the node needs timeline nodes, or must be called across Blueprints without returning a value.

## Notes
Macros, functions, and custom events all accept input parameters, but they differ in the other capabilities. A macro supports output parameters and multiple execution paths and can hold latent actions, but it cannot be called from another Blueprint and cannot hold timeline nodes. A function supports output parameters and cross-Blueprint calls, but it has a single execution path and cannot hold latent actions or timeline nodes. A custom event supports cross-Blueprint calls, latent actions, and timeline nodes, but it has no output parameters and a single execution path. The choice is driven by the capabilities the node needs, not by which form is familiar.
