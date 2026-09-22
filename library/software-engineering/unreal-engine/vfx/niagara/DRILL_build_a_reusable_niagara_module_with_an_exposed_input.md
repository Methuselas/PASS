---
object_id: DRILL_build_a_reusable_niagara_module_with_an_exposed_input
object_type: drill
name: Build a Reusable Niagara Module with an Exposed Input
library_path:
- software-engineering
- unreal-engine
- vfx
- niagara
stage_binding: 2 block
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
target_skill: Create a reusable Niagara Module Script that exposes one input and writes a particle attribute.
---

# Build a Reusable Niagara Module with an Exposed Input

## Practice Task
Create a reusable Niagara Module Script that exposes one input and writes a particle attribute.

## Target Skill
Create a reusable Niagara Module Script that exposes one input and writes a particle attribute.

## Setup
Use a disposable test project or duplicate Niagara assets so the exercise can be repeated without damaging production content.

## Instructions
1. Create a Niagara Module Script asset.
2. Add a Module Input named SizeOfParticle through Map Get.
3. Wire the value to PARTICLES.SpriteSize through Map Set.
4. Compile and apply the module.
5. Add the module to an emitter and change SizeOfParticle in the Selection panel.

## Success Check
The exposed SizeOfParticle control appears on the module instance and changing it changes particle sprite size.

## Common Failures
- Hard-coding the size inside the graph.
- Building the graph as a Local Module instead of a reusable Module Script.

## Notes
Use the consuming emitter's Selection panel as the acceptance surface for the exposed input.
