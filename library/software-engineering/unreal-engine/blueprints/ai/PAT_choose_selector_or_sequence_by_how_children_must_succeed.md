---
object_id: PAT_choose_selector_or_sequence_by_how_children_must_succeed
object_type: pattern
name: Choose Selector or Sequence by How the Children Must Succeed
library_path:
- software-engineering
- unreal-engine
- blueprints
- ai
stage_binding: 0 design
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- blueprints
- ai
- behavior_tree
- control_flow
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: low
references: []
variants: []
---

# Choose Selector or Sequence by How the Children Must Succeed

## Pattern Rule
**IF** you are composing the control flow of a Behavior Tree
**THEN** use a Selector when the children are alternatives to try in order (it runs them left to right and succeeds, stopping, as soon as one child succeeds — a later child only runs if the earlier ones failed), and use a Sequence when every child must succeed (it runs them left to right and the first child to fail aborts the whole sequence).

## Do
- Use a Selector to pick the highest-priority behavior that is currently possible, listing the most important child first.
- Use a Sequence to run a set of steps that must all happen, in order, for the behavior to count as done.
- Order a Selector's children by priority, because the first one that succeeds wins and the rest are skipped.
- Put task nodes (the leaf actions) at the bottom of the tree, under the control flow nodes that decide when they run.

## Don't
- Don't use a Sequence when you actually want alternatives — it will fail the moment one child fails, instead of trying the next option.
- Don't use a Selector when every step is required — it will stop at the first success and skip the rest.
- Don't rely on the visual order alone; the execution order follows left-to-right, top-to-bottom, and the numbered badges show which child runs first.

## Checklist
- Each control flow node is the right kind for its intent: alternatives → Selector, all-required → Sequence.
- A Selector's children are ordered by priority, most important first.
- Task nodes sit at the leaves, under the control flow that gates them.

## Notes
Selector and Sequence are the two primary control flow nodes in a Behavior Tree, and they are opposites. A Selector answers "which of these should I do?" and stops at the first that works; a Sequence answers "do all of these, in order, and if any fails, the whole thing fails." Choosing the right one — and ordering a Selector's children by priority — is what gives the tree its decision structure.
