---
object_id: PAT_keep_progress_critical_information_from_becoming_a_single_failure_point
object_type: pattern
name: Keep Progress-Critical Information from Becoming a Single Failure Point
library_path:
- game-design
- adventures
stage_binding: 0 design
lane_fit: both
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- adventures
- clues
- information
- failure
cross_links:
- rel: related_to
  target_object_id: PAT_prepare_executable_adventure_outcome_states
- rel: related_to
  target_object_id: PAT_structure_adventure_narratives_with_milestones_plot_beats_and_player_agency
reference:
  source_title: Designing TTRPGs For Dummies
  author: Martin Buinicki
confidence: high
references: []
variants: []
---

# Keep Progress-Critical Information from Becoming a Single Failure Point

## Pattern Rule
**IF** later supported play requires the characters to obtain a particular piece of information
**THEN** give that information multiple viable access routes, make failed access change the situation while still opening a path forward, or provide an explicit recovery route
**ELSE** allow optional secrets and advantages to remain genuinely missable when losing them does not collapse required progression.

## Do
- Identify information whose absence would make a required milestone, supported location, or necessary decision unreachable.
- Give progress-critical information more than one plausible route of access when repeated attempts or alternative approaches fit the fiction.
- When a failed access attempt should matter, attach a consequence such as time loss, exposure, resource cost, changed opposition, incomplete information, or a harder route rather than converting failure into a dead campaign state.
- Provide a recovery path when the fiction supports only one initial access opportunity but the campaign still requires the information later.
- Let optional clues remain missable when they grant leverage, context, shortcuts, safety, or alternate understanding rather than serving as hidden mandatory keys.
- Make the facilitator aware which information is progression-critical so improvised adjudication does not accidentally turn an optional check into a hard lock.

## Don't
- Put mandatory information behind one failable check and provide no alternate route, consequence-driven continuation, or recovery path.
- Secretly hand over a clue after failure with no consequence when the uncertainty was supposed to matter; either make access automatic or let failure change the route.
- Protect every secret from being missed merely because it was authored; distinguish required information from optional discovery.
- Rely on facilitator intuition to rescue a dead end that the adventure structure itself can identify in advance.

## Checklist
- Every concealed fact required for supported progression is explicitly identified.
- Each required fact has multiple access routes, a failure consequence that still moves play, or a defined recovery path.
- Failed access can matter without making the next required state unreachable.
- Optional discoveries can remain missable without silently becoming mandatory later.
- The facilitator can distinguish progression-critical information from bonus context or leverage.

## Notes
A failed information check should create a changed situation, not an accidental unsupported state, when the adventure still requires the information to continue. The designer has three main levers already present in the information architecture: **redundancy** through alternate access, **consequence-driven continuation** in which failure changes cost or circumstances, and **recovery** through a later explicit route. Optional information needs no such protection when missing it is itself a valid outcome.
