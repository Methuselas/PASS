---
object_id: PAT_investigate_a_stimulus_location_with_a_flagged_sequence
object_type: pattern
name: Investigate a Stimulus Location with a Flagged Sequence
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
- behavior_tree
- blackboard
- investigation
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: low
references: []
variants: []
---

# Investigate a Stimulus Location with a Flagged Sequence

## Pattern Rule
**IF** an AI should react once to a stimulus it recorded (such as a heard sound) by going to where it happened
**THEN** add a sequence, lower in priority than the AI's active behaviors, gated by a decorator on the stimulus flag: move to the stored stimulus location, wait a moment, and clear the flag as the sequence's last step so the reaction happens once per stimulus.

## Do
- Gate the sequence with a Blackboard decorator (Is Set on the stimulus flag) and set Observer aborts to Lower Priority so the investigation interrupts whatever lower-priority behavior is running.
- Make the first child a Move To the stored stimulus location (a Vector key).
- Add a short Wait after the move so the AI lingers at the location rather than immediately returning to its default behavior.
- End the sequence with a task that clears the stimulus flag, so the next stimulus starts a fresh investigation.
- Keep the sequence below the AI's sight-driven behaviors in priority, so seeing the target always wins over investigating a sound.

## Don't
- Don't leave the flag set after the reaction — with the flag still set, the decorator keeps the sequence eligible and the AI re-investigates the same stale location.
- Don't give the investigation the same priority as the active behavior — the AI should drop the investigation the moment it sees the target.
- Don't clear the flag before the AI has moved and waited; the flag is what keeps the sequence running for the whole reaction.

## Checklist
- The sequence is gated by a decorator on the stimulus flag and aborts lower-priority work when the flag is set.
- The sequence moves to the stored location, waits, and clears the flag in that order.
- After the flag is cleared, the AI returns to its default behavior until the next stimulus.
- A higher-priority behavior (such as attacking a seen target) preempts the investigation.

## Notes
The flag is the whole mechanism: the sensing event sets it, the decorator reads it, and the sequence's last task clears it. That lifecycle — set, react, clear — is what makes the investigation a one-shot reaction to each stimulus instead of a permanent state. The Wait in the middle is the "look around" beat: the AI arrives, pauses at the location, and only then gives up. Priority ordering is what keeps the behavior sane: sight outranks hearing, so the moment the AI sees the player during the investigation, the attack sequence takes over.
