---
object_id: DRILL_verify_unreal_editor_preview_lifecycles
object_type: drill
name: Verify Unreal Editor Preview Lifecycles
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
- actor_lifecycle
- testing
cross_links:
- rel: teaches
  target_object_id: AP_publish_a_transient_unreal_editor_preview_tool
reference:
  source_title: Extending and Customizing Unreal Engine Editor
  author: Roger Mattsson
confidence: medium
references: []
variants: []
target_skill: Verify Unreal Editor Preview Lifecycles
---

# Verify Unreal Editor Preview Lifecycles

## Practice Task
Build a small toggleable Unreal editor preview actor and produce lifecycle evidence across live adjustment, map replacement and module teardown.

## Target Skill
Practise `AP_publish_a_transient_unreal_editor_preview_tool` with observable persistence and cleanup boundaries.

## Setup
An Unreal editor C++ plugin with a toolbar location, a local numeric setting, a temporary editor actor and a per-frame viewport update.

## Instructions
1. State the chosen editor world, viewport, settings destination and lifetime owner with reasons.
2. Implement the toggle command, checked-state query, temporary actor spawn and updater; retain the code and build result.
3. Enable the tool twice, disable it twice and record actor counts, checked state, updater handles and visible behavior after each transition.
4. Drag the numeric control through several updates, record live actor values and config-file writes, then commit once and record the persisted value after editor restart.
5. Enable the tool, replace the map and record the old actor, updater and checked state afterward.
6. Enable it again, unload or shut down the plugin and record any remaining menu entry, callback, actor or package/save delta.
7. Retain the fixture, logs and before/after level/config evidence, and state any interface the run could not exercise.

## Success Check
- A compiled and executed fixture proves repeated toggles are idempotent; a code-only lifecycle prediction does not pass.
- Live adjustment changes the preview without one durable config write per intermediate value, while the committed value survives restart.
- Map replacement and module teardown leave no preview actor or callable raw receiver, unlike the near-miss that destroys the actor but leaves its ticker active.
- Saving the level produces no authored preview actor or package delta, and the checked UI agrees with actual resource state after every transition.
- World, viewport and settings choices have stated reasons, and any unexercised editor interface is reported rather than inferred.

## Common Failures
- Using a saved actor to implement a disposable preview.
- Keeping a separate checked Boolean that drifts from the spawned resource.
- Calling `SaveConfig` for every drag update.
- Destroying the actor without removing the ticker or map delegate.

## Notes
The drill separates four claims that a static review can conflate: non-persistence, idempotent state, callback safety and commit-boundary saving.
