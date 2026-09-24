---
object_id: AP_publish_a_dockable_unreal_actor_browser
object_type: ap
name: Publish a Dockable Unreal Actor Browser
library_path:
- software-engineering
- unreal-engine
- editor
stage_binding: 1 skeleton
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- editor_tools
- slate
- tabs
- selection
cross_links:
- rel: supports
  target_object_id: PAT_keep_unreal_editor_browser_models_synchronized
- rel: supports
  target_object_id: PAT_batch_unreal_actor_selection_notifications
- rel: supports
  target_object_id: PAT_choose_an_explicit_unreal_tool_world
reference:
  source_title: Extending and Customizing Unreal Engine Editor
  author: Roger Mattsson
confidence: medium
references: []
variants: []
---

# Publish a Dockable Unreal Actor Browser

## Objective
Publish a lifecycle-safe nomad tab that groups actors from an explicit editor world, stays synchronized with authoring changes and navigates the Level Editor without excessive selection notifications.

## Steps / Flow
1. Define the actors in scope, grouping key, stable row identity and activation policy. Decide whether activating a group selects all members and whether keyboard navigation should move cameras.
2. Register one uniquely named nomad tab spawner during module startup, place it in an intentional workspace group or hide its automatic menu entry, and retain enough ownership to unregister it on shutdown.
3. Spawn an `SDockTab` containing a browser widget. Keep tree data separate from row widgets and use weak actor references in leaf records.
4. Apply `PAT_choose_an_explicit_unreal_tool_world`, enumerate the initial model and build roots and children deterministically.
5. Apply `PAT_keep_unreal_editor_browser_models_synchronized`: subscribe to relevant editor mutations, update identifiable changes incrementally and coalesce ambiguous events such as undo/redo into a state-preserving reconciliation.
6. Generate rows from currently valid data. Show useful group counts, make stale leaves inert and request the narrowest view refresh after model changes.
7. On row activation, distinguish programmatic, keyboard and direct user selection if their behavior should differ. Apply `PAT_batch_unreal_actor_selection_notifications` when selecting a group, frame only valid leaf targets and draw attention to the Level Editor deliberately.
8. On widget destruction, cancel pending refresh work and remove every delegate. On module shutdown, unregister the tab spawner after closing or releasing owned browser state.
9. Verify actor add/delete, undo/redo, rename/regroup, map replacement, stale weak references, repeated tab open/close and module unload.

## Notes
The browser can represent pickups, lights, validation findings or any other actor family. Domain-specific actor types and labels belong in the model adapter; docking, synchronization, selection batching and teardown form the reusable protocol.
