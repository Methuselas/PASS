---
object_id: PAT_use_a_trigger_volume_as_a_waypoint_for_overlap_detection
object_type: pattern
name: Use a Trigger Volume as a Waypoint for Overlap Detection
library_path:
- software-engineering
- unreal-engine
- blueprints
- ai
stage_binding: 0 design
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- blueprints
- ai
- navigation
- overlap
- trigger
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: low
references: []
variants: []
---

# Use a Trigger Volume as a Waypoint for Overlap Detection

## Pattern Rule
**IF** you need a point or zone in the level that an actor can be detected as reaching — a patrol point, a trigger area, a pickup spot
**THEN** represent it with a trigger volume (such as a Sphere Trigger), because it generates overlap events when an actor enters it and is hidden in the game, so it marks the spot without adding visible geometry.

## Do
- Place a trigger volume (Sphere Trigger) at each point you want to detect arrival at.
- Name each instance clearly (PatrolPoint1, PatrolPoint2) so the references are readable in the level and in Blueprints.
- Detect arrival with the actor's overlap event (Event ActorBeginOverlap) and compare the Other Actor against the waypoint.
- Keep the waypoint hidden in the game so it is a pure marker, not part of the visible scene.

## Don't
- Don't use a visible static mesh as a waypoint when a trigger volume will do — you add geometry the player sees for no reason.
- Don't rely on a volume that does not generate overlap events; the arrival will never be detected.
- Don't place waypoints so close together that the movement between them is not noticeable.

## Checklist
- Each waypoint is a trigger volume placed at the intended spot.
- The waypoint generates overlap events.
- The waypoint is hidden in the game.
- Arrival is detected by comparing the overlapping actor to the waypoint.

## Notes
A trigger volume is the natural way to mark a point in space that matters to logic but not to the player. It gives you an overlap event to react to and stays out of the rendered scene. For a patrol, each point is a trigger volume, and the actor's overlap event is what tells it it has arrived and should head to the next point.
