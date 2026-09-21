---
object_id: PAT_make_a_collectible_one_shot_by_destroying_it_on_pickup
object_type: pattern
name: Make a Collectible One-Shot by Destroying It on Pickup
library_path:
- software-engineering
- unreal-engine
- blueprints
stage_binding: 0 design
lane_fit: both
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- unreal_engine
- blueprints
- collectible
- overlap
- pickup
cross_links:
- rel: related_to
  target_object_id: PAT_choose_a_collision_preset_that_overlaps_the_actors_you_detect
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Make a Collectible One-Shot by Destroying It on Pickup

## Pattern Rule
**IF** an object in the world should give the player something and then be gone — it can be collected only once
**THEN** make it an actor that applies its effect when the player overlaps it and then destroys itself, so a second overlap is impossible.

## Do
- Give the pickup an overlap (not blocking) collision preset with overlap events enabled, so the player can walk into it and it notices.
- On Event ActorBeginOverlap, cast the Other Actor to the player type; only the player's overlap should trigger the pickup.
- Apply the effect to the player (add to the player's resource) and play feedback (a sound at the pickup's location).
- End the chain with DestroyActor on the pickup itself so it can be collected only once.

## Don't
- Don't leave the pickup in the world after collection — without the self-destroy the player can walk over it again and collect it again.
- Don't let any actor trigger the pickup; cast to the player type so only the player's overlap counts.
- Don't block the player with the pickup's collision; it should overlap, not stop, the player.

## Checklist
- The pickup is an actor with overlap (not blocking) collision and overlap events enabled.
- Event ActorBeginOverlap casts the Other Actor to the player before applying the effect.
- The effect is applied to the player and feedback is played.
- DestroyActor(self) ends the chain, so the pickup is collected only once.

## Notes
A collectible that can be picked up only once is an actor that notices the player entering it and then removes itself. The overlap collision lets the player walk in without being stopped; the cast makes sure only the player triggers it; the self-destroy at the end of the chain is what makes it one-shot — once collected, there is nothing left to overlap.
