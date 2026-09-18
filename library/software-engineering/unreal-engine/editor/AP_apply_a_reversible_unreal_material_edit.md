---
object_id: AP_apply_a_reversible_unreal_material_edit
object_type: ap
name: Apply a Reversible Unreal Material Edit
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
- materials
- transactions
cross_links:
- rel: supports
  target_object_id: PAT_route_unreal_tool_input_through_active_commands
- rel: supports
  target_object_id: PAT_snapshot_unreal_edit_targets_before_mutation
- rel: supports
  target_object_id: PAT_cache_unreal_tool_selections_as_weak_objects
- rel: supports
  target_object_id: PAT_report_unreal_tool_outcomes_through_a_small_facade
reference:
  source_title: Extending and Customizing Unreal Engine Editor
  author: Roger Mattsson
confidence: medium
references: []
variants: []
---

# Apply a Reversible Unreal Material Edit

## Objective
Apply a selected material to the intended editor component and slot, with a recoverable prior state and an explicit outcome.

## Steps / Flow
1. Resolve the intended component and material slot. For a viewport tool, use `PAT_route_unreal_tool_input_through_active_commands`; for a callable function, validate its explicit target and slot arguments.
2. Resolve the material selection with `PAT_cache_unreal_tool_selections_as_weak_objects` when the tool caches it. If the material is unavailable, report that outcome and stop without changing state.
3. Validate component eligibility and the slot before transacting. Reject unsupported targets with a reason. If the intended value is already present, report the unchanged outcome without adding an undo entry.
4. Apply `PAT_snapshot_unreal_edit_targets_before_mutation`: begin a named transaction, record the affected actor/component state before editing, and apply the material to the selected slot.
5. Finish the transaction and report the outcome through `PAT_report_unreal_tool_outcomes_through_a_small_facade`. Preserve machine-readable failure information for remote callers.
6. Verify the material actually assigned by readback. During verification in a disposable editor fixture, undo once and check the prior override; redo once and check the new override.
7. If restoration fails, check transaction participation, snapshot timing and the actual storage owner before broadening the tool. Repeat on a non-root component before promising arbitrary-component support.

## Notes
Copying a selection changes tool state; applying it changes editor content. The procedure separates those changes so an unavailable clipboard cannot silently mutate the scene. Viewport gestures and callable plugin functions may share the edit primitive while keeping their target-resolution and feedback interfaces distinct.
