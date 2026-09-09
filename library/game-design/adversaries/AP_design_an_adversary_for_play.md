---
object_id: AP_design_an_adversary_for_play
object_type: ap
name: Design an Adversary for Play
library_path:
- game-design
- adversaries
stage_binding: 0 design
lane_fit: both
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- adversaries
- npcs
- factions
- behavior
- representation
cross_links:
- rel: supports
  target_object_id: PAT_give_adversaries_a_distinct_play_pattern
- rel: supports
  target_object_id: PAT_scale_npc_and_adversary_detail_to_their_role_in_play
- rel: supports
  target_object_id: PAT_compress_repeated_minor_actors_into_shared_state
- rel: supports
  target_object_id: PAT_use_behavioral_commitment_to_resolve_routine_opposition_decisions
- rel: supports
  target_object_id: PAT_express_faction_power_as_deployable_response_capacity
- rel: supports
  target_object_id: PAT_run_consequential_npcs_from_executable_social_state
confidence: high
references: []
variants: []
---

# Design an Adversary for Play

## Objective
Turn an opposing character, creature, group, or organization into a runnable source of pressure with a recognizable play pattern, only as much state as its role needs, coherent routine behavior, and—when the adversary is institutional—concrete response capacity that players can anticipate and affect.

## Steps / Flow
1. **Enter with an adversarial job, not merely a stat concept.** Know what pressure this adversary is meant to create, what it wants or protects, and what kinds of player decisions it should provoke. If its only definition is “a fight of difficulty X,” return to the surrounding scenario or game design and identify the adversary's actual role before adding detail.
2. **Give the adversary a recognizable decision pattern.** Use **Give Adversaries a Distinct Play Pattern** to define the behaviors, capabilities, constraints, vulnerabilities, phases, positioning, or resource logic that make interacting with this adversary meaningfully different from interacting with another one. The pattern should be learnable enough that players can adapt, not a hidden script that only the facilitator can exploit.
3. **Choose representation fidelity from expected role.** Use **Scale NPC and Adversary Detail to Their Role in Play** to decide how much individual state this adversary deserves. A recurring rival, negotiation partner, or strategically complex threat may justify richer representation; a transient obstacle should not inherit character-equivalent detail merely because the system can express it.
4. **Compress repeated minor actors when individual servicing adds no decisions.** If the adversary appears as many similar low-distinction actors, use **Compress Repeated Minor Actors into Shared State** to factor repeated initiative, resource, damage, or other handling while keeping separate only the distinctions that affect targeting, risk, capability, or consequence. If individual identities or states matter, keep them explicit.
5. **Give routine opposition a compact commitment rule when repeated behavior needs consistency.** If ordinary adversaries repeatedly face choices to flee, surrender, bargain, panic, or fight on, use **Use Behavioral Commitment to Resolve Routine Opposition Decisions**. Tie the abstraction to a cause such as discipline, doctrine, professionalism, or mission commitment, and let changed circumstances alter it. For major adversaries whose individual judgment is part of play, use their actual motives instead of forcing them through a generic morale rule.
6. **Give consequential individual adversaries executable social state when judgment itself is part of play.** If the adversary may bargain, deceive, defect, cooperate temporarily, protect a relationship, trade information, or revise a plan for personal reasons, use **Run Consequential NPCs from Executable Social State**. Record the goals, knowledge, leverage, loyalties and relationships, constraints, default behavior, thresholds, offers, and secrets needed to resolve those choices from state rather than a preferred plot outcome. Skip this branch for minor or purely tactical opposition.
7. **Operationalize organizational power only when the adversary persists beyond one scene.** If the adversary is a faction, corporation, government, gang, cult, command structure, or another organization whose off-screen power can respond to player action, use **Express Faction Power as Deployable Response Capacity**. Define the personnel, access, information, transport, money, authority, safe sites, supply, or escalation channels it can actually deploy, conditioned by what it knows, wants, can reach, and is willing to spend. If the adversary has no persistent organizational reach, skip this branch.
8. **Run the representative interaction test.** Exercise the adversary against the materially different player responses the surrounding game or scenario actually supports, including an informed response aimed at its distinctive pattern where that pattern can be learned. For a consequential individual, test at least one unexpected bargain, failed plan, threat, loyalty change, or other social turn and verify that the stored state is sufficient to resolve it without inventing a preferred outcome. Verify that representation and behavior remain coherent without inventing new powers or motives after the fact. For organizational adversaries, also verify that at least one player action can alter a response channel rather than leaving faction power as unlimited referee permission. Do not invent extra response routes merely to satisfy the test.
9. **Close when the adversary is runnable without overbuilding.** Completion requires a clear adversarial job, a distinct and learnable play pattern, enough state for the role it actually occupies, and a consistent answer to recurring behavior questions. Repeated-actor compression, behavioral commitment, executable social state, and faction response capacity are conditional. Encounter difficulty, placement, and adventure pacing remain downstream decisions owned by the scenario that uses the adversary.

## Notes
Faction-scale opposition is a conditional extension of adversary design rather than a separate requirement for every opponent. Treat faction capacity as a branch when the adversary itself is organizational or commands persistent institutional power. Encounter calibration and campaign plotting remain downstream work that consumes the finished adversary rather than part of this action.
