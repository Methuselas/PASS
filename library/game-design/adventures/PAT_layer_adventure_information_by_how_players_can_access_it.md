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
- Treat **queryable information** as available when players ask a reasonable question, inspect an obvious feature, or focus attention on something that is plainly perceptible; do not invent a check solely because the detail was omitted from the initial description.
- Tie **discoverable information** to a concrete route of access such as searching, interacting, moving to a position, using a tool, questioning an NPC, examining evidence, making a deduction, or resolving genuine uncertainty.
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

## Checklist
- Referee-only truth is visibly distinguishable from text or facts safe to present to players.
- The initial scene description gives enough information for a fair immediate decision without trying to exhaust the location.
- Plainly perceptible details are available without unnecessary resolution.
- Important hidden details have identifiable access conditions rather than depending on referee intuition.
- Player questions can obtain ordinary additional detail without converting every inquiry into a roll.
- Checks are reserved for information access that is meaningfully uncertain and where the result changes play.
- Tactical or consequential information becomes available before the decision it is meant to inform, unless uncertainty or surprise is itself the intended challenge.
- Triggered and deferred information is recorded well enough that the referee knows when it becomes available.

## Notes
Adventure description is an information interface as well as prose. The designer knows more than the characters, and the referee must be able to distinguish underlying truth from what the characters automatically perceive, what players can learn by asking, what requires deliberate discovery, and what becomes available only after a trigger. This preserves both fairness and mystery while keeping the table interactive.

Concise read-aloud text and sensory orientation should leave room for the facilitator and players to contribute rather than scripting every reaction. *The Keep on the Borderlands* and *Star Frontiers: Crash on Volturnus* demonstrate the same information-access boundary in different forms. *Keep on the Borderlands* tells the referee to provide accurate information the characters can perceive while withholding secrets they have not discovered. *Crash on Volturnus* repeatedly separates brief player-facing descriptions from referee background, special rules, discoverable information, and planned-event logic. Together they establish a reusable information-access grammar: description establishes the decision surface, questions refine it, actions expose more, and mechanics resolve genuinely uncertain access.

This Pattern owns **how information enters play**. Risk telegraphing, progress-critical clue resilience, and numerical or spatial precision are separate decisions even though all three depend on information design.
