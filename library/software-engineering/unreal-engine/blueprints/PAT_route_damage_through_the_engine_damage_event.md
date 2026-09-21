---
object_id: PAT_route_damage_through_the_engine_damage_event
object_type: pattern
name: Route Damage Through the Engine Damage Event
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
- damage
- event
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: low
references: []
variants: []
---

# Route Damage Through the Engine Damage Event

## Pattern Rule
**IF** one actor should damage another (an enemy's attack, a projectile, a trap)
**THEN** have the attacker call the engine's Apply Damage function on the target, and have the victim react in its own Event AnyDamage handler — the victim's single reaction point for every damage source — rather than letting the attacker write the victim's health directly.

## Do
- Call Apply Damage on the target reference, passing the damage amount; the engine routes the event to the victim.
- Handle the damage in the victim's Event AnyDamage, which fires for every damage source and carries the damage amount, the damage type, and the instigator.
- Keep the victim's health update (and any other damage reaction) in that one handler, so new damage sources need no new wiring on the victim.
- Keep the attacker and the victim decoupled: the attacker names the target and the amount, the victim decides what damage does to it.

## Don't
- Don't write the victim's health variable from the attacker's blueprint — that couples every attacker to the victim's internals and bypasses the victim's own damage logic.
- Don't scatter damage reactions across per-source handlers; Event AnyDamage is the one place the victim reacts to being hurt.
- Don't skip the damage event because setting the variable directly is "simpler" — the event is what lets the victim react uniformly to any source.

## Checklist
- The attacker calls Apply Damage on the target with the damage amount.
- The victim updates its health in Event AnyDamage, not in the attacker's graph.
- A new damage source works on the victim without changing the victim's blueprint.

## Notes
The engine's damage pipeline is the seam between attacker and victim. The attacker's job ends at Apply Damage; the victim's job begins at Event AnyDamage. That split is what lets the enemy's melee task, the player's gun, and any future trap all hurt the player through the same handler, and it keeps the victim's health rules (clamping, effects, death) in one place that the attacker never sees. The victim's handler is also where the pool's invariant is kept: clamp the drained value at the pool's floor (a MAX with 0.0 for health) so an over-large drain lands exactly on the floor instead of driving the pool negative.
