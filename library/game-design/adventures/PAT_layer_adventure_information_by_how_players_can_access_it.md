---
object_id: PAT_layer_adventure_information_by_how_players_can_access_it
object_type: pattern
name: Layer Adventure Information by How Players Can Access It
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
- information
- perception
- discovery
cross_links:
- rel: related_to
  target_object_id: PAT_make_the_game_operable_without_hidden_designer_knowledge
- rel: related_to
  target_object_id: PAT_invoke_resolution_only_for_meaningful_uncertainty
- rel: related_to
  target_object_id: PAT_give_high_consequence_risks_a_learnable_information_basis
- rel: related_to
  target_object_id: PAT_keep_progress_critical_information_from_becoming_a_single_failure_point
- rel: related_to
  target_object_id: PAT_match_information_precision_to_decision_precision
- rel: related_to
  target_object_id: PAT_design_scenario_progression_as_a_redundant_node_network
reference:
  source_title: Designing TTRPGs For Dummies
  author: Martin Buinicki
confidence: high
references: []
variants: []
---

# Layer Adventure Information by How Players Can Access It

## Pattern Rule
**IF** an adventure contains information that is not equally available to the referee, characters, and players
**THEN** partition that information by its actual route into play and reveal it when the characters have the perception, question, action, trigger, or meaningful resolution needed to gain access
**ELSE** present ordinary scene information directly instead of hiding it behind procedure merely because it was not included in the first description.

## Do
- Separate **referee truth** from player-facing information. Record hidden motives, actual causes, concealed hazards, secret identities, future triggers, and other underlying state where the referee can use them without accidentally presenting them as already known.
- Give **automatic perception** immediately when a character in the situation would plainly notice it or when it is necessary for ordinary orientation and a fair first decision.
- Treat perception channels as situational rather than visual by default: sound, odor, texture, temperature, vibration, taste, balance, pressure, and other available senses can reveal routes, resources, hazards, activity, or state when the fiction makes them plainly perceptible.
- Treat **queryable information** as available when players ask a reasonable question, inspect an obvious feature, or focus attention on something that is plainly perceptible; do not invent a check solely because the detail was omitted from the initial description.
- Tie **discoverable information** to a concrete route of access such as searching, interacting, moving to a position, using a tool, questioning an NPC, examining evidence, making a deduction, or resolving genuine uncertainty.
- Separate the **information payload** from its **delivery channel** when the source of the information is not itself important state. A useful fact may remain flexible until a plausible NPC, document, observation, memory, vision, successful inquiry, or other fitting interaction reveals it.
- Anchor evidence when its location, possessor, medium, timing, or method of discovery is itself causally important: a blood trail at a crime scene, a ledger in a suspect's safe, a warning carved beside a route, or a witness who personally saw the event should not become freely relocatable merely for convenience.
- Use **triggered information** when knowledge becomes available only after a location, time, state change, plot beat, NPC interaction, event, or other identifiable condition occurs.
- Front-load enough scene information to establish the immediate decision surface: where the characters are, what obvious opportunities or dangers matter now, and what they can act on next.
- Let player questions refine the scene after the initial description rather than trying to preload every potentially relevant detail into boxed text.
- Make access conditions proportionate to the information. Obvious doors, fires, exits, and creatures should not require the same discovery procedure as concealed compartments, subtle tripwires, hidden allegiances, or forensic clues.
- When information is mechanically or tactically important, verify that the characters can obtain it early enough to make the decision it is supposed to inform.
- Keep hidden information hidden because the fiction has not yet granted access, not because the adventure needs the players to make an uninformed choice.

## Don't
- Read referee-only truth aloud merely because it appears near descriptive text in the manuscript.
- Treat every omitted detail as concealed information.
- Require Perception, Search, Notice, or equivalent checks for plainly visible facts after a player asks about them.
- Hide an automatically perceptible fact until after players commit to a choice their characters would reasonably have evaluated with that fact available.
- Put all available information in the opening description and monopolize synchronous table attention before players can act.
- Reveal secrets early merely because the referee knows them.
- Turn ordinary player questions into rolls when the answer is plainly available in the fiction.
- Move causally anchored evidence to whatever location the players happen to inspect simply because the designer wants the information revealed there.
- Bind every useful fact to one predetermined source when several fictional interactions could reveal the same payload without changing its meaning.

## Checklist
- Referee-only truth is visibly distinguishable from text or facts safe to present to players.
- The initial scene description gives enough information for a fair immediate decision without trying to exhaust the location.
- Plainly perceptible details are available without unnecessary resolution.
- Important hidden details have identifiable access conditions rather than depending on referee intuition.
- Player questions can obtain ordinary additional detail without converting every inquiry into a roll.
- Checks are reserved for information access that is meaningfully uncertain and where the result changes play.
- Tactical or consequential information becomes available before the decision it is meant to inform, unless uncertainty or surprise is itself the intended challenge.
- Triggered and deferred information is recorded well enough that the referee knows when it becomes available.
- Flexible information payloads are distinguished from evidence whose source or placement is itself part of the scenario state.
- A flexible payload still has to enter through a fictional access route that makes sense in the current situation.

## Notes
Adventure description is an information interface as well as prose. The designer knows more than the characters, and the referee must be able to distinguish underlying truth from what the characters automatically perceive, what players can learn by asking, what requires deliberate discovery, and what becomes available only after a trigger. This preserves both fairness and mystery while keeping the table interactive.

Concise read-aloud text and sensory orientation should leave room for the facilitator and players to contribute rather than scripting every reaction. A useful information-access grammar is: description establishes the immediate decision surface, questions refine it, deliberate actions expose more, and mechanics resolve genuinely uncertain access.

The designer can therefore choose between two useful representations. **Anchored evidence** stores the fact with a meaningful source, place, possessor, or trigger. **Flexible payloads** store the fact independently and let the facilitator choose a plausible delivery channel during play. Flexibility is valuable when the information matters more than its source; anchoring is valuable when the source itself carries clues, causality, risk, or choice. Neither form licenses arbitrary revelation.

This Pattern owns **how information enters play**. Risk telegraphing, progress-critical clue resilience, and numerical or spatial precision are separate decisions even though all three depend on information design.
