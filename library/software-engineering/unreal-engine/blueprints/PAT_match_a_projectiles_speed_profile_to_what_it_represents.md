---
object_id: PAT_match_a_projectiles_speed_profile_to_what_it_represents
object_type: pattern
name: Match a Projectile's Speed Profile to What It Represents
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
- projectile
- movement
- tuning
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Match a Projectile's Speed Profile to What It Represents

## Pattern Rule
**IF** you are tuning a projectile's movement to represent a specific kind of projectile — a fast bullet, an accelerating rocket
**THEN** set the speed profile to match the thing it represents: a projectile that does not accelerate after launch (a bullet) starts at its top speed, with its initial speed equal to its maximum and its gravity scaled down; a projectile that accelerates after launch (a rocket) starts below its maximum so the post-launch force has room to act.

## Do
- Set the initial speed to the speed the projectile has the moment it is created, and the maximum speed to the fastest it can go if a force is applied to it after creation.
- For a bullet, set both to the same top value so it travels at full speed from the muzzle and never accelerates.
- Lower the gravity scale so the projectile is barely affected by gravity and travels in a near-straight line.
- Disable bouncing and destroy the projectile on collision, so it stops where it hits instead of rebounding.

## Don't
- Don't leave a bullet's initial speed below its maximum — it would accelerate after launch, which is the behavior of a rocket, not a bullet.
- Don't leave gravity at full scale on a fast projectile — it arcs like a thrown ball instead of flying straight.
- Don't let the projectile bounce off surfaces when it should stop on impact.

## Checklist
- The projectile's speed at creation matches the thing it represents (a bullet at top speed, a rocket below its top speed).
- The gravity scale is low enough that the projectile travels in a near-straight line.
- The projectile is destroyed on collision rather than bouncing.

## Notes
The initial speed is the speed at creation; the maximum speed is the ceiling if a force acts after creation. The decision is to match that profile to the projectile's behavior: a bullet is fastest at the muzzle and never accelerates, so its initial and maximum speeds are equal; a rocket accelerates after launch, so its initial speed is below its maximum. The gravity scale and the bounce setting complete the profile — a low gravity scale keeps the path straight, and disabling bounce with a destroy-on-collision makes the projectile stop where it hits.
