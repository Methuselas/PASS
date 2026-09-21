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
**IF** you need a random spawn point or movement destination constrained to navigable space
**THEN** use GetRandomPointInNavigableRadius with an origin and radius instead of generating an unconstrained raw random vector.

## Do
- Set the radius to cover the area you want the point to fall in.
- Set the origin to the center of the intended search area, such as the spawner's location for local spawning.
- Feed the returned location into the spawn node's Location or a movement destination.

## Don't
- Don't use a raw random world-space vector when the point is intended to come from the navigation mesh.
- Don't use a radius smaller than the area you intend to sample; the node searches within the requested radius.

## Checklist
- The random point comes from GetRandomPointInNavigableRadius.
- The radius and origin cover the intended area.
- The returned point is used as the spawn or movement location.

## Notes
The source uses GetRandomPointInNavigableRadius to choose locations based on the navigation mesh. The node constrains the random draw to navigable space within the requested area; this card does not claim that every such point is unconditionally reachable from every possible AI start state.
