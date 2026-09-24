---
object_id: DRILL_verify_a_transactional_unreal_actor_browser
object_type: drill
name: Verify a Transactional Unreal Actor Browser
library_path:
- software-engineering
- unreal-engine
- editor
stage_binding: 4 final
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- editor_tools
- slate
- testing
- undo
cross_links:
- rel: teaches
  target_object_id: AP_publish_a_dockable_unreal_actor_browser
- rel: teaches
  target_object_id: PAT_keep_unreal_editor_table_interactions_coherent
reference:
  source_title: Extending and Customizing Unreal Engine Editor
  author: Roger Mattsson
confidence: medium
references: []
variants: []
target_skill: Verify a Transactional Unreal Actor Browser
---

# Verify a Transactional Unreal Actor Browser

## Practice Task
Build a dockable Unreal actor table with two sortable columns, one filter, one inline edit and one selection-based context action, then verify projection, transaction and teardown behavior.

## Target Skill
Practise `AP_publish_a_dockable_unreal_actor_browser` and `PAT_keep_unreal_editor_table_interactions_coherent` with observable failure-path evidence.

## Setup
An Unreal editor C++ plugin and a fixture level containing repeated and equal sort keys, actors both inside and outside the filter, and at least one actor that can be deleted while displayed.

## Instructions
1. State stable row identity, primary/secondary sort semantics, filter scope, selection synchronization and transaction boundaries.
2. Open the tab repeatedly and record spawner/delegate counts; add, delete, undo, redo and rename actors while the table is open.
3. Sort ascending and descending on each column, including rows equal on both visible keys; record deterministic order across refreshes.
4. Select rows, change the filter in both directions and record editor selection, Slate selection and the policy for hidden targets.
5. Commit one inline edit and one multi-target context action, then undo and redo each; record object values and row order/filter membership after every step.
6. Generate multiple property callbacks in one frame and record the number of projection refreshes.
7. Delete a selected actor, invoke the context path, close the tab and unload the module; record stale-row handling and remaining delegates/callbacks.

## Success Check
- Equal keys never violate deterministic ordering, and descending mode does not convert equality into less-than.
- Edits and bulk actions undo/redo as one intentional operation and the visible projection follows restored object state.
- Filter and programmatic selection changes do not create selection-feedback loops or act on unspecified hidden targets.
- A mutation burst produces one coalesced refresh, and teardown leaves no callable raw receiver.
- A code-only review or happy-path screenshot does not pass.

## Common Failures
- Treating filtered rows as deleted canonical data.
- Calling `Modify()` after changing the reflected property.
- Sorting directly from invalid weak objects.
- Using the current selection after menu opening without validating that it still identifies the invocation target.

## Notes
Use a deterministic fixture so ordering and refresh counts can be asserted rather than judged visually.
