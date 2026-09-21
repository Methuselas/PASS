---
object_id: PAT_use_actor_vectors_for_direction_relative_movement
object_type: pattern
name: Use Actor Vectors for Direction-Relative Movement
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
- vectors
- movement
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Use Actor Vectors for Direction-Relative Movement

## Pattern Rule
**IF** you need to move, aim, or offset something relative to an actor's own orientation — forward, right, or up — rather than along the world axes
**THEN** use the actor's forward, right, and up vectors, which are normalized (length 1), and multiply by -1 to get the opposite directions (backward, left, down).

## Do
- Use Get Actor Forward Vector, Get Actor Right Vector, and Get Actor Up Vector to get the actor's local directions; they are already normalized (length 1).
- Multiply a direction vector by -1 to get the opposite — backward from forward, left from right, down from up.
- Scale the direction vector by a distance to move or place something that far in that direction (e.g., camera location + forward vector × 300 to get a point 300 cm ahead).

## Don't
- Don't hardcode world axes (X, Y, Z) for movement that should follow the actor's orientation; the actor may be rotated.
- Don't assume the actor vectors carry a magnitude; they are unit vectors, so scale them to apply a distance.
- Don't re-normalize the actor vectors; they are already length 1.

## Checklist
- Direction-relative movement uses the actor's forward/right/up vectors, not world axes.
- The vectors are treated as unit vectors (length 1).
- The opposite direction is obtained by multiplying by -1.
- A distance is applied by scaling the direction vector.

## Notes
An actor's forward, right, and up vectors point along its local axes and are normalized (length 1). Use them to move or aim relative to the actor's orientation instead of the world axes, which only work when the actor is unrotated. Multiply a vector by -1 to flip it to the opposite direction (backward, left, down). To move a specific distance in a direction, scale the unit vector by that distance and add it to a start location.
