---
object_id: PAT_spawn_actors_at_a_random_navigable_point
object_type: pattern
name: Spawn Actors at a Random Navigable Point
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
- navigation
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: low
references: []
variants: []
---

# Spawn Actors at a Random Navigable Point

## Pattern Rule
**IF** you need a random location that an AI can actually reach — a spawn point, a wander destination
**THEN** sample it from the navigation mesh with GetRandomPointInNavigableRadius (a radius around an origin) instead of generating a raw random vector, so the point is guaranteed to be on traversable space.

## Do
- Set the radius to cover the area you want the point to fall in (a large radius around the spawner for spawns, around the level origin for level-wide wandering).
- Set the origin to the center of the area (the spawner's location for spawns, the level origin for level-wide draws).
- Feed the returned location into the spawn node's Location or the Move To's destination.

## Don't
- Don't generate a raw random vector and hope it lands on the floor — a point off the navigation mesh is unreachable, and the AI's move or spawn fails or drops.
- Don't use a radius smaller than the area you want covered; the node returns points within the radius, not beyond it.

## Checklist
- The random point comes from GetRandomPointInNavigableRadius, not a raw random vector.
- The radius and origin cover the intended area.
- The AI can actually reach the point (it is on the navigation mesh).

## Notes
The navigation mesh is the map of where the AI can be. Sampling from it — rather than from raw coordinates — is what makes "random" mean "random somewhere the AI can stand." The same node serves both spawning (a random point near the spawner) and wandering (a random point anywhere in the level); only the origin and radius change.
