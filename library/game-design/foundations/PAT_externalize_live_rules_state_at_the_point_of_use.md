---
object_id: PAT_externalize_live_rules_state_at_the_point_of_use
object_type: pattern
name: Externalize Live Rules State at the Point of Use
library_path:
- game-design
- foundations
stage_binding: 0 design
lane_fit: both
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- usability
- interface
- state
- components
- bookkeeping
cross_links:
- rel: related_to
  target_object_id: PAT_design_rules_artifacts_for_learning_and_retrieval
- rel: related_to
  target_object_id: PAT_account_for_the_intended_play_environment_before_freezing_the_design
- rel: related_to
  target_object_id: PAT_budget_mechanical_operating_cost_by_decision_value_and_activation_cadence
reference:
  source_title: Warhammer Fantasy Roleplay, Third Edition
  author: Jay Little with Daniel Lovat Clark, Michael Hurley, and Tim Uren
confidence: high
references: []
variants: []
---

# Externalize Live Rules State at the Point of Use

## Pattern Rule
**IF** mutable rules state changes often and must be consulted while resolving a specific option, actor, location, or group
**THEN** display and update that state on or immediately beside the rules surface that consumes it so availability, cost, impairment, progress, or risk can be read where the decision is made
**ELSE** keep stable or low-frequency state in the cheaper central record when another component or interface element would add handling without reducing retrieval or interpretation cost.

## Do
- Put cooldown, charge, exhaustion, condition, stance, wound, or similar state on the ability, actor, or other object whose operation it changes rather than requiring a separate lookup to reconnect state with its owner.
- Use orientation, counters, flips, sockets, tracks, overlays, badges, or equivalent digital controls when the manipulation itself makes the state transition legible.
- Distinguish materially different operating bands where they are consulted differently, such as ordinary reserve versus excess reserve, instead of forcing players to remember which identical-looking points have crossed a threshold.
- Keep shared state on a shared surface when every participant may need to inspect or modify it.
- Define the exact manipulation caused by each transition: what receives a marker, what flips, what clears a marker, and when the object becomes usable again.
- Count table footprint, setup, sorting, touch operations, and replacement requirements as real operating costs alongside memory and lookup savings.
- Preserve state visibility only for information the participant is entitled to know; facilitator-owned hidden processes can still use a local state surface without exposing its meaning to players.

## Don't
- Create a separate physical or digital object for state that changes so rarely that ordinary recording is cheaper.
- Store a frequently changing marker far from the rule it modifies and rely on users to reconstruct the mapping repeatedly.
- Add counters or card states that merely restate information already obvious from the primary record without changing retrieval or decisions.
- Assume moving bookkeeping out of memory removes bookkeeping; component handling and table management are still human operations.
- Let a local state display become ambiguous when several effects can be active on the same option or actor at once.

## Checklist
- A user can identify the current operative state at the moment of use without searching an unrelated record.
- Every visible marker, orientation, slot, or toggle has a defined owner and a defined transition rule.
- Distinct threshold states that change risk or permission remain visually or structurally distinguishable.
- Shared state is reachable by every participant who is expected to inspect or change it.
- The intended setup has been tested with representative concurrent effects rather than one clean component at a time.
- The reduction in memory or retrieval burden justifies the added component, screen-space, setup, and manipulation cost in the intended play environment.

## Notes
Moving mutable state onto the object it modifies trades **search and working-memory cost** for **handling and display cost**. A recharge counter sitting on an ability can make both availability and the path back to availability immediately legible; a condition object beside a character can carry the rule that is currently affecting that character; a reserve displayed next to its governing specialty can make a safety threshold visible without recalculation. This move is strongest when the state changes repeatedly and the same rule surface is consulted at the same cadence. It is weakest when components proliferate faster than the decisions they clarify. Static reference layout remains a separate problem owned by rules-artifact retrieval design.
