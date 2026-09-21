---
object_id: PAT_choose_a_collision_preset_that_overlaps_the_actors_you_detect
object_type: pattern
name: Choose a Collision Preset That Overlaps the Actors You Detect
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
- collision
- overlap
- trigger
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Choose a Collision Preset That Overlaps the Actors You Detect

## Pattern Rule
**IF** an actor should notice when another actor enters its space without physically blocking it — a pickup, a trigger, a sensor
**THEN** set its collision preset to overlap (not block) the actor types you want to detect and enable overlap events, so the contact generates an event instead of a collision.

## Do
- Set the actor's Collision Preset to one that overlaps the target actor type (e.g., OverlapAllDynamic to overlap dynamic actors such as the player).
- Enable Generate Overlap Events so the contact produces an Event ActorBeginOverlap.
- Leave the actor non-blocking so the player can walk through it.

## Don't
- Don't use a blocking collision preset for a trigger; the player would be stopped by it instead of passing through and triggering it.
- Don't rely on overlap events without enabling them; the preset alone does not guarantee the event fires.
- Don't make the trigger block the very actors it is meant to detect.

## Checklist
- The collision preset overlaps (not blocks) the actor types to detect.
- Generate Overlap Events is enabled.
- The actor does not physically stop the detected actors.

## Notes
A trigger or pickup that should be walked through needs overlap, not block, collision. The collision preset decides which actor types the actor overlaps; enabling overlap events turns that overlap into an Event ActorBeginOverlap you can respond to. Choose a preset that overlaps the actors you care about (the player, for a pickup) and leave the actor non-blocking, so the player passes through and the event fires.
