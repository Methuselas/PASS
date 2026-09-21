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
**IF** you want an AI to wander using computed destinations instead of fixed waypoint actors
**THEN** store the destination as a Vector Blackboard key and run a sequence that first draws a random navigable point into that key, then moves to it and waits; re-running the sequence performs a fresh draw for the next iteration.

## Do
- Create a Vector Blackboard key for the computed wander destination.
- Write a custom task that sets the key from GetRandomPointInNavigableRadius and finishes with success.
- Put that task first in the sequence, followed by Move To the key and a short Wait.
- Let the sequence re-run from the top so each iteration requests another random point from the navigation query.

## Don't
- Don't store a computed destination as an actor reference when there is no waypoint actor to reference.
- Don't replace the navigation query with an unconstrained raw random vector when the design calls for navmesh-based wandering.
- Don't assume a random draw must differ from the previous draw; random selection can repeat a location.

## Checklist
- A Vector key holds the current wander destination.
- The first task in the sequence performs a fresh random navigable-point query on every run.
- The sequence moves to the key and waits before the next iteration.
- Repeated execution produces wandering from successive random draws, with repeats allowed.

## Notes
This behavior replaces fixed patrol points with a computed Vector destination. A Behavior Tree sequence of "pick a point, move, wait" can repeat continuously; each pass performs another navigation-mesh-based random query. Random does not mean unique, so two iterations may select the same or similar location.
