---
object_id: PAT_gate_consequential_injury_behind_a_recoverable_buffer
object_type: pattern
name: Gate Consequential Injury Behind a Recoverable Buffer
library_path:
- game-design
- mechanics
stage_binding: 0 design
lane_fit: both
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- injury
- health
- criticals
- consequences
- recovery
cross_links:
- rel: related_to
  target_object_id: PAT_expand_resolution_detail_only_after_consequential_state_change
- rel: related_to
  target_object_id: PAT_separate_stabilization_from_recovery
- rel: related_to
  target_object_id: PAT_allocate_simulation_detail_by_expected_persistence
reference:
  source_title: Warhammer Fantasy Roleplay, First Edition
  author: Richard Halliwell, Rick Priestley, Graeme Davis, Jim Bambra, and Phil Gallagher
confidence: high
references: []
variants: []
---

# Gate Consequential Injury Behind a Recoverable Buffer

## Pattern Rule
**IF** characters should withstand routine exchanges while serious harm needs specific persistent consequences
**THEN** let a recoverable buffer absorb ordinary attrition and route threshold-crossing or overflow damage into a separate consequential injury state
**ELSE** use one damage track when routine and serious harm do not need different downstream behavior.

## Do
- Define the buffer as pacing state: ordinary depletion should matter because it moves the character toward danger without requiring every hit to create a lasting wound.
- When damage crosses the threshold, preserve overflow or severity information if it should affect the seriousness of the resulting injury.
- Let the consequential layer produce state that changes later decisions, such as bleeding, impairment, lost mobility, damaged limbs, unconsciousness, treatment requirements, or extended recovery.
- Keep the ordinary buffer from going negative when negative values would merely duplicate severity already represented in the injury layer.
- Give minor or disposable actors a compressed consequence route when their detailed recovery state will never matter again.

## Don't
- Resolve every small hit through the full injury procedure merely because the game supports anatomical or critical detail.
- Use a buffer so large or easy to refresh that the consequential layer almost never activates in the intended play ecology.
- Throw away excess damage at the threshold when greater penetration is supposed to mean more serious injury.
- Let the consequential state be colorful text only; serious injury should alter capability, risk, treatment, recovery, or another future choice.

## Checklist
- Routine damage can resolve without generating a persistent injury every time.
- Crossing the buffer threshold invokes a distinct consequence procedure.
- Severity at threshold crossing is preserved when larger overflow should matter.
- At least one consequential result changes later capability, treatment, recovery, or risk.
- The system can compress detailed injury for actors whose future state does not justify the extra procedure.

## Notes
One health number often has to serve two incompatible jobs: pace an exchange and describe what happened to a body. Splitting those jobs lets ordinary harm stay cheap while serious injury remains specific. The buffer answers how close the character is to real trouble; the injury layer answers what lasting trouble actually occurred. This preserves gritty consequences without forcing anatomical resolution on every successful attack.
