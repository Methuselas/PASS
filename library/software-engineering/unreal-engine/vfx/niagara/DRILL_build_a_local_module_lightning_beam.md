---
object_id: DRILL_build_a_local_module_lightning_beam
object_type: drill
name: Build a Local-Module Lightning Beam
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
target_skill: Build a Dynamic Beam lightning effect and add embedded Local Module
  logic that colors beam particles by stable identity.
---

# Build a Local-Module Lightning Beam

## Practice Task
Build a Dynamic Beam lightning effect and add embedded Local Module logic that colors beam particles by stable identity.

## Target Skill
Build a Dynamic Beam lightning effect and add embedded Local Module logic that colors beam particles by stable identity.

## Setup
Use a disposable test project or duplicate Niagara assets so the exercise can be repeated without damaging production content.

## Instructions
1. Start from the Dynamic Beam template and shorten/tune its temporal behavior.
2. Add jitter/randomization so the bolt changes shape.
3. Create a Local Module in Particle Update.
4. Read PARTICLES.ID/index and use conditional Linear Color output.
5. Enable Requires Persistent IDs.
6. Enable Local Space and move the System to verify the beam follows the emitter.

## Success Check
The lightning changes shape, uses the intended color segmentation, and remains emitter-relative when moved.

## Common Failures
- Leaving persistent IDs disabled.
- Leaving emitter-relative endpoints interpreted in world space.

## Notes
Use visible behavior and the Niagara interfaces named in the task as evidence; do not grade by expected theory alone.
