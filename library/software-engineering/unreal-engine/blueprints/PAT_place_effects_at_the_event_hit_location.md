---
object_id: PAT_place_effects_at_the_event_hit_location
object_type: pattern
name: Place Effects at the Event's Hit Location
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
- effects
- hit
- location
cross_links:
- rel: related_to
  target_object_id: PAT_swap_an_actors_material_at_runtime
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Place Effects at the Event's Hit Location

## Pattern Rule
**IF** you are spawning a sound or a particle effect in response to a hit or collision event
**THEN** feed the event's Hit Location pin into the effect's Location input, so the effect appears at the point of impact rather than at the actor's center.

## Do
- Use the Hit Location output of the hit event as the Location for the sound and for the particle emitter, so both appear where the impact happened.
- Leave the emitter's rotation at its default when the effect looks the same from all angles.

## Don't
- Don't use the actor's own location for the effect — the impact may be at the edge of the actor, and the effect would appear offset from where the player saw the hit.
- Don't place the sound and the particle at different locations when they represent the same impact.

## Checklist
- The sound and the particle effect appear at the point of impact, not at the actor's center.
- Both effects use the same Hit Location.

## Notes
A hit event carries the location where the two objects collide. That location is the natural place for the feedback of the impact — the sound and the particles of an explosion belong at the point of contact, not at the center of the object that was hit. Using the event's own location data keeps the feedback aligned with what the player saw.
