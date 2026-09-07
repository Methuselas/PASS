---
object_id: PAT_model_extended_processes_with_persistent_progress_state
object_type: pattern
name: Model Extended Processes with Persistent Progress State
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
- mechanics
- progress
- clocks
- extended-tasks
- state
cross_links:
- rel: related_to
  target_object_id: PAT_use_time_to_structure_opportunity
- rel: related_to
  target_object_id: PAT_invoke_resolution_only_for_meaningful_uncertainty
- rel: related_to
  target_object_id: PAT_externalize_live_rules_state_at_the_point_of_use
- rel: related_to
  target_object_id: PAT_preserve_decision_relevant_state_while_compressing_resolution_procedure
reference:
  source_title: Tome of Adventure - A Guide to Game Mastery & Roleplaying
  author: Fantasy Flight Games
confidence: high
references: []
variants: []
---

# Model Extended Processes with Persistent Progress State

## Pattern Rule
**IF** an outcome should emerge from multiple contributions over time and intermediate progress, rival progress, or threshold events can change decisions before resolution
**THEN** represent the process with persistent progress state advanced by explicit triggers, using separate accumulators for independent success, failure, or competing objectives when those states can advance independently
**ELSE** resolve the event directly when only the final outcome matters or when intermediate state creates no new decisions.

## Do
- Decide first whether the process answers **when** an expected event occurs or **which outcome happens**; one advancing marker is often enough for the former, while competing outcomes need independent state.
- Give rivals separate markers when each side can make progress through different actions, rates, delays, or setbacks.
- Give success and failure separate accumulators when they are independent; this prevents one back-and-forth marker from producing indefinite stalemate when both sides of the process can accumulate evidence.
- Define exactly what advances each marker: successful actions, elapsed rounds, resource loss, discoveries, environmental events, enemy actions, or another observable trigger.
- Use threshold spaces to change permissions, difficulty, resources, available information, or other situation state before the terminal outcome when intermediate escalation matters.
- Choose whether current progress is public, hidden, or visible without explanation according to what participants should know and what decisions that knowledge supports.
- Let several kinds of action influence the same process when the fiction supports different approaches to the shared objective.
- Stop servicing the track when its intermediate distinctions no longer matter; if managing the abstraction costs more attention than the primary scene, compress it further.

## Don't
- Add a progress track to a routine task whose success is assumed and whose speed has no consequence.
- Move one marker forward for success and backward for failure when success and failure are genuinely accumulating toward separate endpoints.
- Advance a track by arbitrary facilitator pacing when the design expects players to learn what actions influence it.
- Treat reaching the end as the only meaningful event if intermediate thresholds are supposed to alter the situation.
- Expose hidden process state merely because a visible component exists when uncertainty about that state is part of play.
- Use a detailed progress procedure to simulate background actors when a coarser state would preserve every decision relevant to the player-facing scene.

## Checklist
- The process has a reason to persist across more than one action or decision.
- Each active marker has a distinct meaning, trigger set, and terminal condition.
- Independent success, failure, deadline, or competitor conditions are represented independently when they can accumulate at the same time.
- At least one intermediate progress value can change a current decision, threat, opportunity, or rule when intermediate state is retained.
- Participants can identify how their actions can affect the process to the degree the fiction makes that information available.
- The terminal states produce executable consequences rather than only announcing that a meter is full.
- The number of markers and update operations remains cheaper than resolving the underlying process at full detail.

## Notes
Persistent progress is useful when a task, chase, investigation, social contest, morale state, environmental threat, large background conflict, or other process develops through several contributions that matter before the endpoint. The important design split is between a countdown to an expected event and independent races toward different outcomes. Separate accumulators preserve simultaneous progress and avoid accidental cancellation; threshold events let the process change shape before it ends. The track is an abstraction, not a commitment to physical components: boxes, clocks, counters, software meters, or ordinary recorded values can all carry the same state.
