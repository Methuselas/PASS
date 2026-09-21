---
object_id: PAT_patrol_between_two_points_by_swapping_the_current_target_on_arrival
object_type: pattern
name: Patrol Between Two Points by Swapping the Current Target on Arrival
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
- patrol
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: low
references: []
variants: []
---

# Patrol Between Two Points by Swapping the Current Target on Arrival

## Pattern Rule
**IF** you want an actor to patrol back and forth between two points
**THEN** track the current target in a variable, set it to one of the points at BeginPlay, and each time the actor overlaps the current target, swap the variable to the other point so the next move goes to the point it just left.

## Do
- Store both patrol points as object references (Instance Editable, so each placed instance can be given its own pair in the level).
- Keep a separate, non-Instance-Editable variable for the current target.
- At BeginPlay, set the current target to the first point and push it to wherever the AI reads it from.
- On the overlap event, test which point the actor reached and set the current target to the other point.
- Push the new current target to the AI's data store so the navigation behavior moves to it.

## Don't
- Don't hard-code the destination in the navigation behavior; drive it from the current-target value so the swap is what changes where the actor goes.
- Don't forget to update the AI's data store after each swap — changing the local variable alone does not change where the actor moves.
- Don't use the same variable for both the fixed points and the current target; the fixed points never change, the current target does.

## Checklist
- Two fixed point references and one current-target variable exist.
- BeginPlay sets the current target to the first point and pushes it.
- Overlap with the current target swaps it to the other point and pushes it.
- The actor alternates between the two points for as long as it runs.

## Notes
The patrol is a two-state ping-pong: the actor always moves to whichever point is currently stored, and arriving at it flips the stored point. The swap on arrival is the whole mechanism — there is no timer and no list of waypoints, just "go to the current one, then the current one becomes the other." Keeping the fixed points separate from the mutable current target is what makes the swap clean.
