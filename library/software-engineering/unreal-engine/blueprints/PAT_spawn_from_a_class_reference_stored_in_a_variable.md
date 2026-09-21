---
object_id: PAT_spawn_from_a_class_reference_stored_in_a_variable
object_type: pattern
name: Spawn From a Class Reference Stored in a Variable
library_path:
- software-engineering
- unreal-engine
- blueprints
stage_binding: 0 design
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- blueprints
- spawning
- class_reference
- data_driven
cross_links:
- rel: related_to
  target_object_id: PAT_spawn_actors_at_a_random_navigable_point
- rel: related_to
  target_object_id: PAT_store_the_spawned_actor_reference
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Spawn From a Class Reference Stored in a Variable

## Pattern Rule
**IF** you want the type of actor you spawn to be configurable per instance rather than hard-coded in the spawn call
**THEN** store the Actor class in an Instance Editable class reference variable and spawn from that variable (SpawnActor from Class), so the level designer chooses what spawns by setting the variable on the instance.
**ELSE** where the spawned type is fixed for the life of the Blueprint, a hard-coded class in the spawn call is simpler.

## Do
- Create a class reference variable (for example, SpawnClass) and check Instance Editable so it can be set per instance in the Level Editor.
- Spawn with the SpawnActor from Class node, wiring the class reference variable to the Class input.
- Combine the spawn with a data-driven location source (for example, the transform of a randomly chosen element of an array of target points) when the spawn location is also data.

## Don't
- Don't hard-code the actor class in the spawn call when it should vary per instance — the class reference variable is what makes it data.
- Don't forget Instance Editable — without it the variable cannot be set on a placed instance.
- Don't spawn from a class reference without validating it first (Is Valid Class).

## Checklist
- The spawned type is a class reference variable, not a hard-coded class.
- The variable is Instance Editable.
- The class reference is validated before the spawn.

## Notes
Storing the class in a variable turns the spawned type from code into data: the same Blueprint can spawn different actors depending on which instance you place and what you set on it. This pairs naturally with an array of target points (each an object reference) and a Random Array Item node, so both the what and the where of the spawn are level data rather than logic.
