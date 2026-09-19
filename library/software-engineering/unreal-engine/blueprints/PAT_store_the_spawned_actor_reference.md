---
object_id: PAT_store_the_spawned_actor_reference
object_type: pattern
name: Store the Reference to an Actor You Spawn
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
- spawning
cross_links:
- rel: related_to
  target_object_id: PAT_guard_object_references_with_is_valid
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Store the Reference to an Actor You Spawn

## Pattern Rule
**IF** you spawn an Actor and need to act on that instance later — destroy it, move it, query it
**THEN** store the Spawn Actor from Class Return Value in a variable (or promote the pin to a variable), because the spawn call itself hands the instance to nobody.

## Do
- Pass the class to spawn and the Transformation (location, rotation, scale) for the new instance; use the Collision Handling Override to control collision at creation time.
- Drag from the Return Value pin and choose Promote to variable to create a correctly typed variable in one step.
- Remember that a single reference variable tracks only the last spawned instance: spawning again overwrites the stored reference, and earlier instances remain in the level.

## Don't
- Don't discard the Return Value when you will need the instance later — without the stored reference you cannot target it for DestroyActor or any other action.
- Don't assume one variable keeps every instance you spawned; it keeps only the most recent.

## Checklist
- The spawned instance's Return Value is stored in a variable when any later step needs it.
- DestroyActor (or the later action) receives the stored reference as its Target.
- The design accounts for the variable holding only the last spawn when multiple instances are created.

## Notes
Spawn Actor from Class creates the instance; DestroyActor with the stored reference as Target removes it. The pair is the basic create/teardown cycle for runtime-spawned objects.
