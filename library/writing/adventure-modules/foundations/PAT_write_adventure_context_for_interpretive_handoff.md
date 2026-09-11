---
object_id: writing_adventure_modules_write_context_for_interpretive_handoff
object_type: pattern
name: Write Adventure Context for Interpretive Handoff
library_path:
  - writing
  - adventure-modules
  - foundations
stage_binding: 0 design
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: medium
foundation_object_id: writing_calibrate_context_to_audience_and_venue
tags:
  - adventure_modules
  - context
  - causality
  - backstory
  - game_master
cross_links:
  - rel: related_to
    target_object_id: writing_adventure_modules_partition_information_by_reader_role_and_reveal_state
reference:
  source_title: "How to Write Adventure Modules That Don't Suck!"
  author: Jobe Bittman
confidence: high
references: []
variants:
  - variant_id: writing_adventure_modules_variant_write_unopposed_threat_trajectory_as_conditional_context
    variant_name: Write an Unopposed Threat Trajectory as Conditional Context
    variant_basis: method_sequence
    difference_from_foundation: For a scenario driven by an intentional threat, state the antagonist's objective, the major actions it would attempt if the protagonists never interfered, and the likely responses of affected NPCs or institutions, then present that trajectory as a conditional baseline the operator must recompute after player action changes the situation.
    when_to_use: The operator needs to understand how an active antagonist or faction creates pressure offscreen and what the surrounding world is likely to do before or between protagonist interventions.
    when_not_to_use: No intentional actor drives the scenario, the relevant developments are genuinely fixed processes, or projecting a sequence would encourage the operator to preserve planned events after their causes have been removed.
    absorbed_from_object_id: none
  - variant_id: writing_adventure_modules_variant_build_context_around_a_focal_story_element
    variant_name: Build Context Around a Focal Story Element
    variant_basis: method_sequence
    difference_from_foundation: Choose the person, place, event, object, time, cause, or method that most strongly defines the adventure and use supporting who, what, where, when, why, and how questions to fill only the causal gaps needed for the operator to understand the present situation.
    when_to_use: A short or medium adventure needs a coherent backstory but open-ended worldbuilding would create more prose than the operator can use.
    when_not_to_use: Several coequal threads intentionally share focus, the adventure is built as an open anthology of situations, or forcing one organizing element would distort the material.
    absorbed_from_object_id: none
---

# Write Adventure Context for Interpretive Handoff

## Pattern Rule
**IF** an adventure manuscript gives an operator people, places, hazards, rewards, or rules that must be interpreted and recombined during live play
**THEN** supply the minimum causal context that explains what those elements are doing now, how they relate, and what information the operator needs to keep them coherent when players act unpredictably
**ELSE** omit background that neither affects operation nor can become discoverable or consequential in play

## Do
- Give important actors present motives, relevant relationships, and enough prior circumstance to explain what they are likely to do next without prescribing the protagonists' response.
- For each substantial inhabitant, hazard, barrier, reward, or access feature, ask why it is present now, who benefits from or tolerates it, and what allowed it to persist.
- Check coexistence explicitly when neighboring elements would naturally threaten, consume, disable, avoid, or exploit one another; write the relationship that makes the current arrangement possible.
- Include backstory when it changes behavior, explains present state, supports discovery, or helps the operator adjudicate an unscripted consequence.
- Prefer concrete present facts and broad causal strokes over a fully authored sequence of future events.
- Leave enough stable context that an operator can infer a plausible response when play reaches a situation the manuscript did not predict.
- When a single actor carries a function that later material depends on, decide whether losing that actor should end the adventure; if not, state a plausible successor, alternate pressure, independent process, or changed objective rather than protecting the actor by fiat.

## Don't
- Write a fixed narrative outcome for protagonists whose choices belong to the players.
- Keep lore merely because it is interesting when it cannot affect behavior, discovery, consequence, or live interpretation.
- Place monsters, residents, traps, doors, treasure, or resources beside one another with no explanation for why the arrangement has not already changed.
- Use backstory to repair contradictions after the fact without making the repaired relationship visible in the present adventure state.
- Strip context so far that the operator has only isolated map keys, statistics, or set pieces and must invent the causal situation during play.

## Checklist
- Every major actor has a present motive or pressure the operator can use to choose behavior.
- Every major hazard, reward, barrier, or inhabitant has a credible reason to be where it is now.
- Potentially incompatible neighboring elements have an explicit coexistence explanation.
- Included history changes present interpretation, future response, or discoverable meaning.
- Removing any remaining background would make live interpretation materially harder; material that fails that test has been cut.
- The manuscript establishes circumstances without deciding how the protagonists must react or how the adventure must end.
- Removing a key actor early either produces a supported ending or leaves enough written causal state for the operator to continue without inventing a replacement plot from nothing.

## Notes
Adventure prose is mediated: the writer does not directly narrate the final sequence to the audience. An operator interprets the written situation, players act inside it, and the operator must then recombine the manuscript's facts in response. The useful context is therefore neither a bare key nor a complete fiction plot. It is the causal information that survives that handoff.

A practical rationale audit catches many failures early. Ask why a creature lives beside another creature, why residents tolerate a lethal trap on their own route, why a valuable object remains in a hazardous place, or why a barrier exists in relation to the people who use the site. The answer need not be elaborate. It only needs to make the current state operable and plausible enough that later consequences can be derived from it.

Variant `writing_adventure_modules_variant_write_unopposed_threat_trajectory_as_conditional_context` makes an active threat legible across time. State what the antagonist wants, what it would attempt if nobody interfered, and what affected people or institutions would plausibly notice and do. The resulting trajectory is operator context, not promised future narration: once the protagonists interrupt a step, remove a resource, expose a secret, or change an NPC response, the operator derives the next development from the new state instead of forcing the original sequence to occur.


Variant `writing_adventure_modules_variant_build_context_around_a_focal_story_element` keeps backstory generation proportionate. Choose the element that most strongly organizes the adventure, then use who, what, where, when, why, and how as prompts for the supporting context. The questions are not a completeness checklist; they are a way to explain the present people, place, pressures, and relationships around the chosen focus without turning operator support into a separate work of fiction.
