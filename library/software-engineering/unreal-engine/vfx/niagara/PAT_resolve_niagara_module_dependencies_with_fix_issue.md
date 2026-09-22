---
object_id: PAT_resolve_niagara_module_dependencies_with_fix_issue
object_type: pattern
name: Resolve Niagara Module Dependencies with Fix Issue
library_path:
- software-engineering
- unreal-engine
- vfx
- niagara
stage_binding: 2 block
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

# Resolve Niagara Module Dependencies with Fix Issue

## Pattern Rule
**IF** Niagara reports that a module has an unmet declared dependency
**THEN** use the editor Fix Issue action when it identifies the required dependency.

## Do
- Read the dependency error before changing the stack.
- Use Fix Issue when Niagara can add or repair the declared dependency automatically.

## Don't
- Do not guess at stack repairs while ignoring a precise dependency diagnostic.

## Checklist
- The dependency warning clears and the required module appears in a valid location.

## Notes
The grid-spawn and collision-event examples both demonstrate this workflow.
