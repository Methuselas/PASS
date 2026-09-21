---
object_id: PAT_choose_the_abstraction_level_by_reuse_scope
object_type: pattern
name: Choose the Abstraction Level by Reuse Scope
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
- abstraction
- readability
cross_links:
- rel: related_to
  target_object_id: PAT_choose_between_blueprint_macro_function_and_custom_event
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Choose the Abstraction Level by Reuse Scope

## Pattern Rule
**IF** a group of nodes in an EventGraph should be hidden behind a single named node
**THEN** choose the form by its reuse scope: a collapsed graph when the group is used in one place only, a macro when it is reused in other places of the same EventGraph, and a function when it may be called from another Blueprint.

## Do
- Select the group of nodes and use the ORGANIZATION menu: Collapse Nodes, Collapse to Macro, or Collapse to Function.
- Use Collapse Nodes (a collapsed graph) when the group is not going to be used in another place; give the collapsed node a meaningful name and double-click it to see or edit its nodes.
- Use Collapse to Macro when the same group of nodes is used in other places of the EventGraph.
- Use Collapse to Function when the group of nodes could be called from another Blueprint.
- Name the abstractions meaningfully so the graph reads as an overview of what the Blueprint does.

## Don't
- Don't use a collapsed graph for a group that is reused elsewhere — a collapsed graph cannot be called from another place.
- Don't use a macro for a group that must be called from another Blueprint — a macro is local to its own Blueprint.
- Don't leave a giant flat graph when the nodes can be grouped into named abstractions.

## Checklist
- The form matches the reuse scope: single use → collapsed graph, reused within the graph → macro, cross-Blueprint → function.
- Each collapsed node has a meaningful name.
- The graph reads as an overview of named abstractions rather than a wall of nodes.

## Notes
Abstraction handles complexity by hiding low-level details, so the developer can focus on the problem at a high level and look at the details of a specific part when needed. The macro/function/custom-event choice is also driven by capability (output parameters, execution paths, latent actions, timeline nodes); the reuse-scope axis decides which of the three — plus the collapsed graph — fits. Example: the pause-menu nodes (Set Game Paused, Show Mouse Cursor, Create Widget, Add to Viewport) collapse into a single "Show Pause Menu" node.
