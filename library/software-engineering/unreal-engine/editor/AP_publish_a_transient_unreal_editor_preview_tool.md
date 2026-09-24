---
object_id: AP_publish_a_transient_unreal_editor_preview_tool
object_type: ap
name: Publish a Transient Unreal Editor Preview Tool
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
- toolmenus
- actor_lifecycle
- preview
cross_links:
- rel: supports
  target_object_id: PAT_register_unreal_toolmenus_after_editor_startup
- rel: supports
  target_object_id: PAT_route_unreal_tool_input_through_active_commands
- rel: supports
  target_object_id: PAT_keep_unreal_editor_preview_actors_transient_and_disposable
- rel: supports
  target_object_id: PAT_separate_shared_unreal_defaults_from_local_tool_preferences
reference:
  source_title: Extending and Customizing Unreal Engine Editor
  author: Roger Mattsson
confidence: medium
references: []
variants: []
---

# Publish a Transient Unreal Editor Preview Tool

## Objective
Publish an Unreal editor toolbar tool whose checked state, temporary scene actor, live preview settings and teardown remain coherent across interaction, map changes and module shutdown.

## Steps / Flow
1. Name the preview result and choose the editor world and viewport it observes. Stop if the feature actually edits authored content; a disposable preview lifecycle is then the wrong contract.
2. Apply `PAT_route_unreal_tool_input_through_active_commands`: declare a toggle command, map execution to one idempotent state transition and make the checked query read the real active resource rather than an independent Boolean.
3. Apply `PAT_register_unreal_toolmenus_after_editor_startup` to publish the toggle and any adjacent options control with owned entries, an explicit command list, installed style resources and removable startup registration.
4. Apply `PAT_keep_unreal_editor_preview_actors_transient_and_disposable`. On activation, install the updater, spawn the editor-only transient actor in the chosen editor world and configure it from current settings. If any acquisition fails, run the deactivation path and leave the checked query false.
5. During each update, validate both the preview actor and current viewport before copying view-dependent state. Do not infer continued validity from the ticker handle alone.
6. Apply `PAT_separate_shared_unreal_defaults_from_local_tool_preferences` to route settings to their intended local/shared destination. Preview high-frequency value changes in memory and invalidate the relevant viewport; persist only at a commit boundary.
7. Route toggle-off, map change and module shutdown through the same safe teardown order: remove updaters and raw delegates, destroy the temporary actor, clear handles/references, then release command and menu owners.
8. Exercise enable, live adjustment, commit, disable, map change and module unload. Completion requires restored settings after restart, no saved preview actor, no stale receiver and checked UI that agrees with the real resource.

## Notes
The protocol applies to camera-following lights, measurement helpers and other temporary editor-world visualizations. A preview actor is an implementation technique, not authored level data. If an operation must participate in undo or persist into the level, use an authored-edit protocol instead of weakening the transient contract.
