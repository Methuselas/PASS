---
object_id: PAT_use_construction_script_for_per_instance_configuration
object_type: pattern
name: Drive Per-Instance Configuration From the Construction Script
library_path:
- software-engineering
- unreal-engine
- blueprints
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- blueprints
- construction_script
cross_links:
- rel: related_to
  target_object_id: PAT_declare_who_may_read_and_write_blueprint_state
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Drive Per-Instance Configuration From the Construction Script

## Pattern Rule
**IF** a Blueprint's appearance or setup must be configurable per placed instance in the Level Editor and re-applied automatically when the designer changes the setting
**THEN** read Instance Editable variables in the Construction Script instead of the Event Graph, because the Construction Script runs when the Blueprint is first added to the level, when its properties change in the Level Editor, and when an instance is spawned at runtime.

## Do
- Wire the Construction Script to apply the variable to the owning component — for example, Get the Instance Editable Static Mesh variable and Set Static Mesh on the mesh component.
- Mark the configurable variables Instance Editable so each placed instance can hold its own value in the Level's Details panel.
- Give the variable a sensible default value so instances that are never customized still render correctly.
- Use this shape to let level designers configure instances without opening the Blueprint: different meshes, sizes, or settings per placed copy.

## Don't
- Don't put editor-reactive configuration in the Event Graph or BeginPlay — that graph runs at play time and does not re-run when a designer edits an instance's properties in the editor.
- Don't expect the Construction Script to run during gameplay in response to runtime events; it is a construction-time hook, not a general event graph.

## Checklist
- Changing an Instance Editable variable on a placed instance in the Level Editor immediately updates the instance without playing the level.
- Two instances of the same class can show different configured values at the same time.
- The configuration logic lives in the Construction Script, not the Event Graph.

## Notes
The Construction Script is a special function every Actor Blueprint performs at construction time; it is the mechanism that makes a Blueprint flexible for level designers. The per-instance value decision (which variables to mark Instance Editable) is owned by the state-access pattern; this pattern owns where the configuration logic runs.
