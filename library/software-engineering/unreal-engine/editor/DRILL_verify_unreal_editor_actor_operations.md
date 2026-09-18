---
object_id: DRILL_verify_unreal_editor_actor_operations
object_type: drill
name: Verify Unreal Editor Actor Operations
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
- rel: teaches
  target_object_id: AP_place_and_update_unreal_editor_actors
reference:
  source_title: Extending and Customizing Unreal Engine Editor
  author: Roger Mattsson
confidence: medium
references: []
variants: []
target_skill: Verify Unreal Editor Actor Operations
---

# Verify Unreal Editor Actor Operations

## Practice Task
Produce a disposable fixture for class-based placement, selection and actor-setting updates, with recorded undo/redo and rejected cases.

## Target Skill
Practise `AP_place_and_update_unreal_editor_actors` on explicit editor-world targets.

## Setup
An Unreal editor toolchain and a disposable map with two suitable actor classes and editable settings.

## Instructions
1. State the world, class, selection and unsupported-target policies, with reasons.
2. Place an actor with a distinguishable transform; record returned identity, actual class/transform and selection effects.
3. Select a filtered actor set, update a declared setting, and record exact before/after selection sets and property values. Include an unchanged target and report changed, unchanged, unsupported and failed counts separately.
4. Run undo and redo for placement, selection and settings; record restored identities, transforms, sets, values and transaction counts.
5. Attempt invalid classes and invalid or foreign targets. Record reasons and before/after world state and history.
6. Repeat an unchanged operation and record its outcome/history. Record the observed notification behavior and supported persistence scope.
7. Retain the built fixture, execution evidence and any unexercised interfaces.

## Success Check
- The fixture builds and runs; predicted behavior or a source listing is insufficient.
- Class, transform and final target sets match the declared policies.
- Each promised user action restores its exact supported state through one undo and redo; merely opening a transaction fails this check.
- Rejected inputs preserve the observed authoring state and history with useful reasons.
- Change counts and unchanged-operation claims match actual values rather than processed targets.
- Notification and persistence claims match exercised interfaces.

## Common Failures
- Editing PIE actors accidentally.
- Treating bare actor spawn inside a transaction as proof of undo.
- Clearing selection before validating the requested set.
- Counting unchanged actors as changed.

## Notes
Use neutral actor settings. This exercise concerns editor construction contracts, not the actor's gameplay purpose.
