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
**IF** you spawn actors periodically and want to cap how many are alive at once, and the actors can be destroyed by gameplay
**THEN** enforce the cap by counting the live actors of the class in the world on each spawn cycle (Get All Actors Of Class, then compare its Length to the cap) and spawn only when the count is below the cap.

## Do
- Keep the cap as a variable (such as MaxEnemies) so the population limit can be tuned.
- Pass the Behavior Tree to Spawn AI From Class so the spawned enemy is immediately autonomous rather than inert.
- On each spawn cycle, query the world for the live actors of the spawned class and take the array's Length.
- Branch on the count being less than the cap: spawn only on the true path.
- Let the count fall naturally as actors are destroyed — the cap is checked against the world, not against a bookkeeping variable.

## Don't
- Don't track the spawned references to count the population — references go stale when the actors are destroyed, and the count drifts from the truth.
- Don't spawn unconditionally on the timer — without the cap check, the level fills with actors and performance degrades.
- Don't store the count in a variable you update on spawn and destroy; the world is the source of truth and the query is one node.

## Checklist
- The spawn cycle queries the live actors of the class and compares the count to the cap.
- A spawn happens only when the count is below the cap.
- Destroying actors frees population without any bookkeeping update.

## Notes
When the spawned actors have a lifecycle the spawner does not control — the player can destroy them — the world is the only reliable census. Get All Actors Of Class plus Length is that census: it counts what is actually alive, so the cap holds no matter how the population changes. Storing the spawned references would work only if the spawner were the sole owner of the actors' lifetimes; here it is not, so the count is queried, not kept.
