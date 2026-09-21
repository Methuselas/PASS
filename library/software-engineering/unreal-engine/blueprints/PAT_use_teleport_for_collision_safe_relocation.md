---
object_id: PAT_use_teleport_for_collision_safe_relocation
object_type: pattern
name: Use Teleport for Collision-Safe Relocation
library_path:
- software-engineering
- unreal-engine
- blueprints
stage_binding: 1 skeleton
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- blueprints
- teleport
- movement
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Use Teleport for Collision-Safe Relocation

## Pattern Rule
**IF** you need to move an actor to a specified location that might be blocked by an obstacle
**THEN** use the Teleport node rather than setting the actor's location directly.

## Do
- Call Teleport on the actor with the destination location (and optionally the destination rotation).
- Let the engine move the actor to the location, or to a nearby place with no collision if the location is blocked.

## Don't
- Don't set the actor's location directly when the destination might be inside an obstacle — the actor will overlap the obstacle.

## Checklist
- The move uses Teleport, not a direct location set.
- If the destination is blocked, the actor lands at a nearby non-colliding place.

## Notes
The advantage of Teleport over setting the actor's location is collision safety: if there is an obstacle at the location, the actor is moved to a nearby place where there will be no collision. Example: a teleport platform that moves the player to the next platform's location when the player overlaps it.
