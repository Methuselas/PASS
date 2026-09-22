---
object_id: DRILL_expose_a_niagara_parameter_as_an_editor_tunable_blueprint_property
object_type: drill
name: Expose a Niagara Parameter as an Editor-Tunable Blueprint Property
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
- blueprints
cross_links: []
reference:
  source_title: Build Stunning Real-time VFX with Unreal Engine 5
  author: Hrishikesh Andurlekar
confidence: high
references: []
variants: []
target_skill: Expose a Niagara User parameter through a public Blueprint property
  that updates in editor mode.
---

# Expose a Niagara Parameter as an Editor-Tunable Blueprint Property

## Practice Task
Expose a Niagara User parameter through a public Blueprint property that updates in editor mode.

## Target Skill
Expose a Niagara User parameter through a public Blueprint property that updates in editor mode.

## Setup
Use a disposable Niagara System with an obvious float control, such as the Fountain Spawn Rate, plus an Actor Blueprint containing a Niagara component.

## Instructions
1. Create a typed USER parameter for an emitter property such as Spawn Rate.
2. Bind the emitter/module property to that User parameter.
3. Embed the Niagara System in an Actor Blueprint through a Niagara component.
4. In Construction Script, use the matching typed Set Niagara Variable node and target the USER parameter.
5. Promote the setter value input to a Blueprint variable and make that variable public.
6. Place the Blueprint Actor in the level and change the public value from the Details panel.

## Success Check
Changing the placed Actor's public Blueprint property in the Details panel immediately changes the bound Niagara behavior without opening the Niagara Editor or entering Play mode.

## Common Failures
- Using Begin Play when editor-time feedback is required.
- Using a Niagara setter whose type does not match the User parameter.
- Setting the wrong Niagara variable name/reference.

## Notes
A representative setup can expose User.SpawnRate through a public ParticleSpawnRate Blueprint variable. The specific value is tunable; the practice target is the typed bridge and editor-time abstraction.
