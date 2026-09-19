---
object_id: PAT_move_an_actor_per_frame_with_a_delta_time_scaled_offset
object_type: pattern
name: Move an Actor Per-Frame with a Delta-Time-Scaled Offset
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
- movement
- delta_time
cross_links:
- rel: related_to
  target_object_id: PAT_compose_blueprint_behavior_from_ready_components
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Move an Actor Per-Frame with a Delta-Time-Scaled Offset

## Pattern Rule
**IF** you need an Actor to move continuously at runtime — a patrol, a drift, a chase
**THEN** drive it from Event Tick by applying a per-frame offset scaled by delta time, so the speed is the same at any frame rate.

## Do
- Set the Actor's Mobility to Movable before writing any movement logic, because a Static Actor cannot be manipulated during gameplay.
- Normalize the direction vector so its length is one, then multiply it by the speed scaled by delta time (Speed × Get World Delta Seconds).
- Feed the result into AddActorWorldOffset's Delta Location and run it from Event Tick, so the offset is applied every frame.
- Keep the speed, direction, and timing as variables so the movement can be tuned without rewiring the graph.

## Don't
- Don't move by a fixed amount each frame — without delta time the speed depends on the frame rate and the Actor races ahead on fast machines.
- Don't leave the Actor Static and wonder why it won't move — Static is the cheaper default, but it cannot be moved at runtime.
- Don't skip normalizing the direction — an unnormalized vector leaks its magnitude into the speed.

## Checklist
- The Actor moves at the same real-world speed whether the game runs at 30 or 144 frames per second.
- The Actor's Mobility is Movable.
- The per-frame offset is the product of a normalized direction and a delta-time-scaled speed.

## Notes
Delta time is the time between the previous frame and the current frame, and it varies from frame to frame. Multiplying the speed by delta time converts a per-second speed into a per-frame offset, so the movement is frame-rate independent. Event Tick runs every frame, so applying the offset there moves the Actor continuously. The direction is normalized first so that only the speed controls how fast the Actor moves, not the length of the direction vector.
