---
object_id: PAT_give_an_ai_hearing_with_on_hear_noise_and_a_distance_gate
object_type: pattern
name: Give an AI Hearing with On Hear Noise and a Distance Gate
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
- sensing
- pawn_sensing
- hearing
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: low
references: []
variants: []
---

# Give an AI Hearing with On Hear Noise and a Distance Gate

## Pattern Rule
**IF** you want an AI to react to sounds made nearby (footsteps, gunfire) rather than only to what it can see
**THEN** use the PawnSensing component's On Hear Noise event, gate the reaction on the distance between the noise location and the AI (only noises within a hearing distance count), and record the stimulus in the Blackboard — a flag that a sound was heard and the location it came from — so the Behavior Tree can decide what to do about it.

## Do
- Add the On Hear Noise event from the PawnSensing component (the same component that owns the AI's sight).
- Compute the distance from the noise location to the AI's own location (subtract the AI's location from the noise location and take the vector length) and branch on it being less than a hearing-distance variable.
- Keep the hearing distance as a variable so the detection range can be tuned without rewiring the graph.
- On a close-enough noise, write both the location (a Vector key) and a "heard sound" flag (a Bool key) to the Blackboard.
- Let the Behavior Tree, not the event, decide what the AI does with the stimulus.

## Don't
- Don't let every noise in the level be heard — an unbounded hearing range lets the player reveal their position from across the map, which feels unfair.
- Don't act on the noise in the event graph when the decision belongs in the Behavior Tree; the event's job is to record what was heard, the tree decides what to do about it.
- Don't store only the flag without the location — the AI needs to know where to go to investigate.

## Checklist
- The On Hear Noise event is wired on the AIController's PawnSensing component.
- The reaction is gated on the noise being within the hearing distance of the AI.
- A close noise writes both a location key and a heard-sound flag to the Blackboard.
- The Behavior Tree can read both keys to decide whether to investigate.

## Notes
Hearing is the same sense/decide/act split as sight: the On Hear Noise event records the stimulus (where it was and that it happened), and the Behavior Tree decides the response. The distance gate is what makes hearing a fair sense — it bounds how far the AI can hear so the player can act at range without instantly revealing themselves. The flag-plus-location pair is the Blackboard's version of "I heard something over there": the flag says whether there is anything to investigate, and the location says where.
