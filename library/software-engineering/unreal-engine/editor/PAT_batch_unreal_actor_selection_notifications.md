---
object_id: PAT_batch_unreal_actor_selection_notifications
object_type: pattern
name: Batch Unreal Actor Selection Notifications
library_path:
- software-engineering
- unreal-engine
- editor
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- editor_tools
cross_links: []
reference:
  source_title: Extending and Customizing Unreal Engine Editor
  author: Roger Mattsson
confidence: medium
references: []
variants: []
---

# Batch Unreal Actor Selection Notifications

## Pattern Rule
**IF** an Unreal editor operation selects a set of actors
**THEN** resolve the complete target set, declare replace or merge behavior, defer routine per-actor selection notifications, and notify when the final selection is ready.

## Do
- Search only the intended world and filter class and settings deliberately.
- Compute matches before clearing selection; declare what an empty result means.
- Deduplicate and validate targets before changing selection.
- Use a named transaction and the actual selection storage when selection undo is promised.
- Defer notifications for the initial clear as well as per-actor changes, then issue the final selection change notification.
- Detect an unchanged set before recording or notifying when the tool promises no-op requests leave history and refreshes unchanged.

## Don't
- Don't notify for every actor and repeatedly refresh dependent panels.
- Don't miss the final notification or confuse matched targets with the final selected set.

## Checklist
- Does readback match the intended target set?
- Is the editor notified of the completed selection?
- If promised, do undo and redo restore the actual selection sets?

## Notes
Actor property edits and editor selection edits have different storage owners. A selection transaction wrapper alone is not proof of reversible selection.
