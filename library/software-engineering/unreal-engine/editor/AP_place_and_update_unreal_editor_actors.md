---
object_id: AP_place_and_update_unreal_editor_actors
object_type: ap
name: Place and Update Unreal Editor Actors
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
cross_links:
- rel: supports
  target_object_id: PAT_choose_an_explicit_unreal_tool_world
- rel: supports
  target_object_id: PAT_enforce_an_explicit_unreal_selection_policy
- rel: supports
  target_object_id: PAT_snapshot_unreal_edit_targets_before_mutation
- rel: supports
  target_object_id: PAT_batch_unreal_actor_selection_notifications
- rel: supports
  target_object_id: PAT_report_unreal_tool_outcomes_through_a_small_facade
reference:
  source_title: Extending and Customizing Unreal Engine Editor
  author: Roger Mattsson
confidence: medium
references: []
variants: []
---

# Place and Update Unreal Editor Actors

## Objective
Place an actor of the intended class or apply declared settings to a scoped actor set, with usable outcomes and verified undo behavior.

## Steps / Flow
1. Apply `PAT_choose_an_explicit_unreal_tool_world`; validate the intended authoring world and level.
2. Choose placement or update. For placement, validate the exact placeable class, scene-root support and world-space transform. For update, apply `PAT_enforce_an_explicit_unreal_selection_policy`, filter the eligible actors and validate their settings before changing them.
3. Apply `PAT_snapshot_unreal_edit_targets_before_mutation` to the actual creation containers or edited actors, grouping one user action into one transaction. Stop on unavailable recording.
4. Place and configure the actor, or update each eligible changed actor; mark persistent edits dirty. Record unchanged, unsupported and failed targets separately from actual changes.
5. If the operation changes selection, apply `PAT_batch_unreal_actor_selection_notifications`; keep an empty-result policy explicit.
6. Apply `PAT_report_unreal_tool_outcomes_through_a_small_facade` for target identities, changes and failure reasons.
7. Read back class, transform or edited fields. Exercise undo and redo against that exact result; stop on mismatch and distinguish creation, recording and notification failures before retrying. If execution began before failure, report any partial state and its recovery path rather than promising preflight-style rejection.

## Notes
The settings may belong to any suitable actor class. This procedure does not require a game-specific spawner, automatic selection after placement or a uniform save guarantee.
