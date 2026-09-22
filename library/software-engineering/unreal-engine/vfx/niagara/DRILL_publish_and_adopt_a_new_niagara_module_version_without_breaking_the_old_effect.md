---
object_id: DRILL_publish_and_adopt_a_new_niagara_module_version_without_breaking_the_old_effect
object_type: drill
name: Publish and Adopt a New Niagara Module Version without Breaking the Old Effect
library_path:
- software-engineering
- unreal-engine
- vfx
- niagara
stage_binding: 4 final
lane_fit: teach
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- niagara
- vfx
cross_links: []
reference:
  source_title: Build Stunning Real-time VFX with Unreal Engine 5
  author: Hrishikesh Andurlekar
confidence: high
references: []
variants: []
target_skill: Practice evolving a reusable Niagara module while preserving an existing
  consumer.
---

# Publish and Adopt a New Niagara Module Version without Breaking the Old Effect

## Practice Task
Practice evolving a reusable Niagara module while preserving an existing consumer.

## Target Skill
Practice evolving a reusable Niagara module while preserving an existing consumer.

## Setup
Use a disposable test project or duplicate Niagara assets so the exercise can be repeated without damaging production content.

## Instructions
1. Enable versioning on a reusable module with an existing consumer.
2. Keep the current version intact and create a new version with a Change Description.
3. Make a visibly different change only in the new version.
4. Verify the existing consumer still uses the old behavior.
5. Explicitly switch the consumer to the new version and verify the change.
6. Switch back to prove rollback remains available.

## Success Check
Old and new module behavior coexist, adoption is explicit, and rollback works.

## Common Failures
- Editing the exposed production version directly.
- Assuming all consumers automatically upgrade.

## Notes
Use visible behavior and the Niagara version-selection interfaces named in the task as evidence; do not grade by expected theory alone.
