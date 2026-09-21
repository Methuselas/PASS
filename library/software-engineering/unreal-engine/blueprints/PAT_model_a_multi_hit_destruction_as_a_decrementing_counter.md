---
object_id: PAT_model_a_multi_hit_destruction_as_a_decrementing_counter
object_type: pattern
name: Model a Multi-Hit Destruction as a Decrementing Counter
library_path:
- software-engineering
- unreal-engine
- blueprints
stage_binding: 1 skeleton
lane_fit: both
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- unreal_engine
- blueprints
- state
- hit
- destruction
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: low
references: []
variants: []
---

# Model a Multi-Hit Destruction as a Decrementing Counter

## Pattern Rule
**IF** an object should be destroyed only after a number of hits (more than a two-stage boolean can express)
**THEN** store an integer hit counter defaulting to the hit budget, and in the hit handler branch on it: while the counter is above the threshold, decrement it; when it reaches the threshold, run the terminal sequence — the death effect, the reward, and the destroy.

## Do
- Store the hit budget as an Integer variable defaulting to the number of hits required.
- Gate the handler on the hit source (cast the hit's Other actor to the projectile class) so only the intended damage source counts.
- Branch on the counter being greater than the threshold: the true path decrements the counter, the false path runs the terminal sequence.
- In the terminal sequence, spawn the death effect at the object's own transform, hand out the reward (such as incrementing the goal counter and checking the goal), and destroy the actor last.

## Don't
- Don't count every hit — without the source gate, collisions and other actors' hits drain the budget too.
- Don't destroy the actor before the effect and the reward have run; once it is destroyed, nothing else in its graph can execute.
- Don't use a Boolean for a budget larger than two — a counter is what scales the "first hit, second hit, ... last hit" logic.

## Checklist
- The counter starts at the hit budget and decrements once per qualifying hit.
- Only hits from the intended source decrement the counter.
- The terminal sequence (effect, reward, destroy) runs exactly when the counter reaches the threshold.
- The actor is destroyed last in the terminal sequence.

## Notes
This is the two-stage boolean generalized to N: instead of "has it been hit once?", the question is "how many hits are left?", and the branch is on the counter rather than a Boolean. The source gate (the cast) is what makes the counter meaningful — it counts the hits that matter, not every contact. The terminal sequence reuses the same reward pipeline as the static targets (increment the goal counter, check the goal), so destroying an enemy and destroying a target advance the same objective. The death effect is anchored to the destroyed actor's own transform, not the hit location: the effect represents the object's destruction as a whole, not the point of the final impact.
