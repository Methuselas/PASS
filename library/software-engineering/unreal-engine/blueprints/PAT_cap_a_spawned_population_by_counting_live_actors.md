---
object_id: PAT_cap_a_spawned_population_by_counting_live_actors
object_type: pattern
name: Cap a Spawned Population by Counting Live Actors
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
- spawning
- population
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: low
references: []
variants: []
---

# Cap a Spawned Population by Counting Live Actors

## Pattern Rule
**IF** you spawn actors periodically and want to cap how many are alive at once
**THEN** query the live actors of that class on each spawn cycle, compare the array Length to the cap, and spawn only when the count is below the cap.

## Do
- Keep the cap as a variable (such as MaxEnemies) so the population limit can be tuned.
- On each spawn cycle, use Get All Actors Of Class for the spawned class and take the returned array's Length.
- Branch on the count being less than the cap and spawn only on the true path.
- When spawning AI with Spawn AI From Class, supply the Behavior Tree when the new enemy should begin acting immediately.

## Don't
- Don't spawn unconditionally on the timer when the design requires a population cap.
- Don't compare against a stale snapshot; perform the live-actor query on the spawn cycle that makes the decision.

## Checklist
- The spawn cycle queries the live actors of the class and compares the count to the cap.
- A spawn happens only when the count is below the cap.
- Destroyed actors are absent from a later live-actor count.

## Notes
The demonstrated Blueprint uses Get All Actors Of Class plus Length as a live-world count before each spawn attempt. This is one direct way to keep a periodic spawner under a maximum while allowing gameplay to remove actors between spawn cycles.
