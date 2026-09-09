---
object_id: writing_adventure_modules_sequence_load_bearing_adventure_scenes_by_dependency
object_type: pattern
name: Sequence Load-Bearing Adventure Scenes by Dependency
library_path:
  - writing
  - adventure-modules
  - structure
stage_binding: 1 skeleton
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: medium
foundation_object_id: none
tags:
  - adventure_modules
  - structure
  - sequencing
  - dependency
  - transitions
cross_links:
  - rel: related_to
    target_object_id: writing_adventure_modules_anchor_episodic_adventure_to_stable_mission_spine
reference:
  source_title: "Famine in Far-Go"
  author: "Michael Price"
confidence: high
references: []
variants: []
---

# Sequence Load-Bearing Adventure Scenes by Dependency

## Pattern Rule
**IF** later adventure material requires a clue, status change, resource, relationship, location, permission, or transformed objective produced by an earlier scene
**THEN** order those load-bearing scenes by dependency, state what each scene hands forward, and preserve freedom inside and between dependencies wherever the later material does not require a single method
**ELSE** use an episodic mission spine when scenes can be reordered, shortened, or omitted without invalidating what follows

## Do
- Identify the input each required scene assumes and the concrete output it must hand to later material.
- Fix scene order only where a later scene truly depends on an earlier discovery, transformation, acquisition, or decision.
- Tell the operator why the next phase follows from the current one instead of relying on numbered order alone.
- Distinguish the required handoff from optional color, hazards, rewards, and side discoveries that may vary without breaking the sequence.
- Allow local openness inside a required location or scene when several approaches can still produce the needed handoff.
- Give a required handoff a fallback, alternate source, or degraded form when ordinary play can plausibly weaken or miss it.

## Don't
- Declare scenes mandatory merely because the author prefers a particular dramatic order.
- Make optional atmosphere or side content falsely load-bearing by placing it between required numbered scenes.
- Force every action inside a required scene to occur in one prescribed sequence when only the scene's output matters.
- Hide the reason for a transition so the operator must infer why the characters should proceed to the next phase.
- Let one ordinary failed observation, conversation, or search erase information that all later scenes require.

## Checklist
- Every fixed-order scene can name the later dependency that justifies its position.
- Each required scene hands forward at least one concrete piece of state needed later.
- The operator can explain both the next objective and why it follows from the current result.
- Removing or reordering a truly load-bearing scene would break a named dependency rather than merely change pacing.
- Choices remain open wherever the dependency does not require a specific method.
- Required handoffs that can be missed have a written recovery path or reduced-but-usable outcome.

## Notes
A linear macrostructure and local player freedom are compatible. A module may require a ritual before a revelation, a revelation before a destination, or one transformation before the next phase while still allowing exploration, negotiation, combat, avoidance, or several routes inside each phase. The useful distinction is dependency, not chronology. Numbered encounters do not become load-bearing until later material actually needs what they produce. This pattern complements an episodic mission spine: use the spine when episodes are modular; use dependency sequencing when changing their order would make later material unintelligible or unreachable.
