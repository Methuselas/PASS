---
object_id: PAT_create_a_new_niagara_module_version_before_making_breaking_changes
object_type: pattern
name: Create a New Niagara Module Version before Making Breaking Changes
library_path:
- software-engineering
- unreal-engine
- vfx
- niagara
stage_binding: 4 final
lane_fit: both
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
---

# Create a New Niagara Module Version before Making Breaking Changes

## Pattern Rule
**IF** a reusable Niagara module with existing consumers needs a behavior change that could alter or break those consumers
**THEN** create a new module version before changing the implementation.

## Do
- Preserve the exposed production version.
- Create a new version and make incompatible changes there.

## Don't
- Do not overwrite an exposed production version when consumers need stable historical behavior.

## Checklist
- Existing consumers retain their previous behavior after the new version is authored.

## Notes
Niagara warns when exposed versions are edited because changes propagate to current usages.
