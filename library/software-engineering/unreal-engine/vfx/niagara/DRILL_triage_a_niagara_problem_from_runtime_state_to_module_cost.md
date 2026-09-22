---
object_id: DRILL_triage_a_niagara_problem_from_runtime_state_to_module_cost
object_type: drill
name: Triage a Niagara Problem from Runtime State to Module Cost
library_path:
- software-engineering
- unreal-engine
- vfx
- niagara
stage_binding: 3 rough
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
target_skill: Diagnose one Niagara behavior/performance problem by controlling time,
  inspecting runtime state, visualizing hidden logic, and measuring cost.
---

# Triage a Niagara Problem from Runtime State to Module Cost

## Practice Task
Diagnose one Niagara behavior/performance problem by controlling time, inspecting runtime state, visualizing hidden logic, and measuring cost.

## Target Skill
Diagnose one Niagara behavior/performance problem by controlling time, inspecting runtime state, visualizing hidden logic, and measuring cost.

## Setup
Use a disposable test project or duplicate Niagara assets so the exercise can be repeated without damaging production content.

## Instructions
1. Reproduce the problem with pause/slow/step controls.
2. Filter the Debug HUD to the target System.
3. Inspect the System/Instance/Emitter in FX Outliner.
4. Enable Debug Drawing on a relevant supported module.
5. Use Niagara performance views to identify an expensive script/module by measurement.
6. Spawn the System with Debug Spawn and compare the isolated case.

## Success Check
The learner records one evidence-backed behavioral finding and one measured performance hotspot before proposing a fix.

## Common Failures
- Changing values before reproducing the issue.
- Calling the visually most complex module the bottleneck without measurement.

## Notes
Use visible behavior and the Niagara/Blueprint interfaces named in the task as evidence; do not grade by expected theory alone.
