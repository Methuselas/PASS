---
object_id: PAT_place_niagara_modules_in_the_group_that_matches_execution_scope
object_type: pattern
name: Place Niagara Modules in the Group That Matches Execution Scope
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

# Place Niagara Modules in the Group That Matches Execution Scope

## Pattern Rule
**IF** you add a Niagara module and need to decide where it should execute
**THEN** place it in the System, Emitter, or Particle group and Spawn/Update stage that matches the data and timing it is supposed to affect.

## Do
- Use Particle Spawn for one-time initialization at particle birth.
- Use Particle Update for behavior that must run during particle life.
- Use emitter/system groups for emitter- or system-level state rather than particle-only work.

## Don't
- Don't place a lifetime behavior in a spawn-only stage.
- Don't place particle-only logic at a broader scope without a reason.

## Checklist
- The module executes at the intended scope.
- The module runs at the intended time in the lifecycle.

## Notes
Niagara groups and stages determine where a module runs and what data it can affect.
