---
object_id: PAT_keep_unreal_editor_table_interactions_coherent
object_type: pattern
name: Keep Unreal Editor Table Interactions Coherent
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
- slate
- sorting
- transactions
cross_links:
- rel: related_to
  target_object_id: PAT_keep_unreal_editor_browser_models_synchronized
- rel: related_to
  target_object_id: PAT_snapshot_unreal_edit_targets_before_mutation
reference:
  source_title: Extending and Customizing Unreal Engine Editor
  author: Roger Mattsson
confidence: medium
references: []
variants: []
---

# Keep Unreal Editor Table Interactions Coherent

## Pattern Rule
**IF** an Unreal Slate list or table can sort, filter, select and edit live editor objects
**THEN** model those operations as coordinated transformations over stable row identities, make object edits transactional, and coalesce derived-view refreshes after mutations.

## Do
- Keep canonical object state separate from the visible row array. Derive the visible array from current scope, filters and sort descriptors.
- Represent primary and secondary sort descriptors explicitly. Use a strict weak ordering with a deterministic stable-identity tie-breaker; equality must remain false in both comparator directions.
- Treat filters as visibility policy, not deletion. When filters change, rebuild or diff the visible projection and retain only still-visible selection by stable identity.
- For inline edits and bulk actions, start one scoped transaction, call `Modify()` on every valid target before its first mutation, change the object, and then request one refresh/resort.
- Bind collapsed and expanded editor controls to the current object value or update both after commit. Do not let a row widget become a second value owner.
- Coalesce high-frequency property/delegate callbacks into one pending refresh. Before refreshing, remove invalid weak rows and recompute any sort/filter keys affected by the change.
- Keep Slate selection and editor selection deliberately synchronized. Ignore direct/programmatic selection callbacks that would feed back, and batch the final editor notification.
- Scope context-menu actions to a validated invocation/selection snapshot, state what filtered-out objects mean for the action, and make no-op outcomes visible.

## Don't
- Don't invert a less-than result to implement descending order; it makes equal values compare as ordered and violates the sort contract.
- Don't mutate reflected properties without `Modify()` and a transaction when undo/redo is promised.
- Don't refresh and resort once for every property callback in the same frame.
- Don't silently let a context action operate on a stale or ambiguous selection.

## Checklist
- Is ordering deterministic for equal primary and secondary keys?
- Do undo and redo restore both object values and the visible sorted/filtered projection?
- Can programmatic selection update the table without recursively changing editor selection?
- Are hidden, invalid and stale rows handled explicitly by bulk/context actions?

## Notes
Multi-column rows, combo boxes, check boxes and context menus are presentation choices. The reusable contract is one transactional object authority feeding a deterministic, refreshable projection with controlled selection feedback.
