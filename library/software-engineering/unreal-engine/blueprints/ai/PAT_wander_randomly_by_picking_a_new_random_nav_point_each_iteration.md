---
object_id: PAT_wander_randomly_by_picking_a_new_random_nav_point_each_iteration
object_type: pattern
name: Wander Randomly by Picking a New Random Nav Point Each Iteration
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
- wander
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: low
references: []
variants: []
---

# Wander Randomly by Picking a New Random Nav Point Each Iteration

## Pattern Rule
**IF** you want an AI to wander the level randomly instead of following fixed waypoints
**THEN** store the destination as a Vector Blackboard key and build a sequence whose first task picks a new random navigable point into that key; the sequence's re-execution is the loop — each pass picks a new point and moves to it.

## Do
- Create a Vector Blackboard key for the wander destination; a computed destination is a vector, not an actor reference, so it does not need a placed waypoint.
- Write a custom task that sets the key to a random navigable point (GetRandomPointInNavigableRadius with a radius that covers the level) and finishes with success.
- Put that task first in the sequence, followed by a Move To the key and a short Wait.
- Let the sequence re-run from the top: each iteration re-picks the point, so the AI never follows the same route twice.
- Sample the point from the navigation mesh so every destination is actually reachable.

## Don't
- Don't store a computed destination as an actor reference — there is no actor to point at, and a Vector key is what the Move To needs.
- Don't pick the random point with a raw random vector; a point off the navigation mesh is unreachable and the Move To will fail.
- Don't keep the old fixed-waypoint behavior alongside the wander — remove the setup that fed the replaced behavior so the two don't fight.

## Checklist
- A Vector key holds the current wander destination.
- The first task in the sequence writes a new random navigable point to the key on every run.
- The sequence moves to the key and waits, then re-runs to pick the next point.
- The AI moves to a different random location on each iteration.

## Notes
Wandering is patrol with the waypoints replaced by a random draw. The two pieces that make it work: the destination lives in a Vector key because it is computed rather than placed, and the point is drawn from the navigation mesh so it is always reachable. The loop is implicit in the Behavior Tree — a sequence that succeeds re-runs from its first child, so "pick a point, go there, wait" repeats, each pass with a fresh destination. Compared with a two-point patrol, wandering makes the AI's position unpredictable, which is the point: the player can no longer hide from a predictable route. To test the wandering, use Simulate mode (the menu next to the Play button) to move freely through the level with a free camera — hold the right mouse button and use the movement keys and the mouse — so you can watch the AI wander without being the player.
