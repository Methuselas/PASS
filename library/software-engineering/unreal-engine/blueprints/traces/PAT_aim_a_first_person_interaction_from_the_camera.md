---
object_id: PAT_aim_a_first_person_interaction_from_the_camera
object_type: pattern
name: Aim a First-Person Interaction from the Camera
library_path:
- software-engineering
- unreal-engine
- blueprints
- traces
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- blueprints
- traces
- first_person
- camera
cross_links:
- rel: related_to
  target_object_id: PAT_use_cast_to_test_a_type_or_reach_subclass_members
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Aim a First-Person Interaction from the Camera

## Pattern Rule
**IF** a first-person player should interact with whatever they are looking at (toggle a light, pick up an item, activate a switch)
**THEN** originate the interaction trace from the camera and aim it along the camera's forward vector scaled by the interaction distance, because in a first-person game the camera is the eye, not the character.

## Do
- Get the camera with Get Player Camera Manager and read its location with GetActorLocation.
- Read the camera's forward vector with Get Actor Forward Vector, scale it by the interaction distance, and add it to the camera location to get the trace End.
- Run the trace from the camera location to that end point, break the hit result, and act on the hit actor.

## Don't
- Don't originate a first-person look-based trace from the character's location or forward vector; the character's aim can differ from the camera's, especially with mouse look.
- Don't assume the trace hits the intended actor; break the hit result and cast the hit actor to the expected type before acting.

## Checklist
- The trace Start is the camera's location, not the character's.
- The trace End is the camera location plus the camera's forward vector scaled by the interaction distance.
- The hit actor is cast to the expected type before the interaction is applied.

## Notes
The trap is reaching for the character's location or forward vector, because in a third-person habit the character is the natural origin. In a first-person game the camera is the player's eye, and the character's own forward vector can point a different way from the camera (especially with mouse look), so aiming from the character sends the interaction at the wrong place. The interaction distance is a parameter you choose (for instance 300 cm), not a fixed offset. After the trace, the hit actor must be cast to the expected type before the interaction is applied, because the trace may hit something other than the intended actor.
