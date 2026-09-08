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
- rel: related_to
  target_object_id: PAT_design_scenario_progression_as_a_redundant_node_network
reference:
  source_title: Designing TTRPGs For Dummies
  author: Martin Buinicki
confidence: high
references: []
variants:
- variant_id: game_design_variant_track_required_conclusions_with_a_revelation_list
  variant_name: Track Required Conclusions with a Revelation List
  variant_basis: method_sequence
  difference_from_foundation: Organize progress-critical information around the conclusions players need to reach, list several independent clue or access routes under each conclusion, and track both delivered clues and conclusions actually reached during play.
  when_to_use: An investigation, mystery, conspiracy, or other information-heavy scenario contains several required conclusions whose individual clues may be missed, misunderstood, or reached through unplanned methods.
  when_not_to_use: The scenario has little concealed information, the facts are optional rather than progress-critical, or a single automatic disclosure already makes the conclusion reliably available.
  absorbed_from_object_id: none
---

# Keep Progress-Critical Information from Becoming a Single Failure Point

## Pattern Rule
**IF** later supported play requires the characters to obtain a particular piece of information
**THEN** give that information multiple viable access routes, make failed access change the situation while still opening a path forward, or provide an explicit recovery route
**ELSE** allow optional secrets and advantages to remain genuinely missable when losing them does not collapse required progression.

## Do
- Identify information whose absence would make a required milestone, supported location, or necessary decision unreachable.
- Give progress-critical information more than one plausible route of access when repeated attempts or alternative approaches fit the fiction. Several genuinely independent clues are often safer than relying on one supposedly obvious clue; three is a useful robustness heuristic for an important conclusion, not a requirement to manufacture redundant trivia.
- Treat prepared clues as a safety net rather than an exclusive answer key. If a player-devised investigation would logically expose the needed information, let that approach produce an appropriate clue or conclusion instead of rejecting it because it was not prewritten.
- When a failed access attempt should matter, attach a consequence such as time loss, exposure, resource cost, changed opposition, incomplete information, or a harder route rather than converting failure into a dead campaign state.
- Provide a recovery path when the fiction supports only one initial access opportunity but the campaign still requires the information later.
- Let optional clues remain missable when they grant leverage, context, shortcuts, safety, or alternate understanding rather than serving as hidden mandatory keys.
- Make the facilitator aware which information is progression-critical so improvised adjudication does not accidentally turn an optional check into a hard lock.

## Don't
- Put mandatory information behind one failable check and provide no alternate route, consequence-driven continuation, or recovery path.
- Secretly hand over a clue after failure with no consequence when the uncertainty was supposed to matter; either make access automatic or let failure change the route.
- Protect every secret from being missed merely because it was authored; distinguish required information from optional discovery.
- Rely on facilitator intuition to rescue a dead end that the adventure structure itself can identify in advance.
- Veto a logically successful investigative approach solely because the exact clue it would reveal was not on the author's prepared list.

## Checklist
- Every concealed fact required for supported progression is explicitly identified.
- Each required fact has multiple access routes, a failure consequence that still moves play, or a defined recovery path.
- Failed access can matter without making the next required state unreachable.
- Optional discoveries can remain missable without silently becoming mandatory later.
- The facilitator can distinguish progression-critical information from bonus context or leverage.
- When several required conclusions interact, the facilitator has a compact way to see which clues have surfaced and which conclusions the players have actually reached.

## Notes
A failed information check should create a changed situation, not an accidental unsupported state, when the adventure still requires the information to continue. The designer has three main levers already present in the information architecture: **redundancy** through alternate access, **consequence-driven continuation** in which failure changes cost or circumstances, and **recovery** through a later explicit route. Optional information needs no such protection when missing it is itself a valid outcome. Variant `game_design_variant_track_required_conclusions_with_a_revelation_list` is useful when clue density becomes large enough that the facilitator needs to track revelations separately from individual clue instances; the prepared list remains a reliability tool, not a restriction on logically earned discoveries.
