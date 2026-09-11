---
object_id: writing_adventure_modules_structure_encounter_entries_for_live_retrieval
object_type: pattern
name: Structure Encounter Entries for Live Retrieval
library_path:
  - writing
  - adventure-modules
  - operations
stage_binding: 2 block
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: medium
foundation_object_id: writing_adventure_modules_write_context_for_interpretive_handoff
tags:
  - adventure_modules
  - encounters
  - information_architecture
  - live_use
  - retrieval
cross_links:
  - rel: related_to
    target_object_id: writing_adventure_modules_partition_information_by_reader_role_and_reveal_state
reference:
  source_title: "How to Write Adventure Modules That Don't Suck!"
  author: Chris Doyle
confidence: high
references: []
variants:
  - variant_id: writing_adventure_modules_variant_write_escalating_hazards_as_trigger_threshold_response_chains
    variant_name: Write Escalating Hazards as Trigger-Threshold-Response Chains
    variant_basis: method_sequence
    difference_from_foundation: For a local hazard whose danger changes as a count or state accumulates, present the normal state, initiating trigger, tracked variable, successive thresholds and effects, and available relief or countermeasures in activation order so the operator can advance the hazard without reconstructing its logic.
    when_to_use: One encounter contains a persistent local state such as contamination, swarm agitation, heat, flooding, collapse, or another escalating hazard whose thresholds change what the operator resolves.
    when_not_to_use: The hazard resolves in one step, no persistent state is tracked, or threshold presentation would add structure without improving live retrieval.
    absorbed_from_object_id: none
---

# Structure Encounter Entries for Live Retrieval

## Pattern Rule
**IF** an encounter entry will be consulted repeatedly while the operator is describing the scene, resolving actions, and reacting to player choices
**THEN** organize the entry into predictable, colocated chunks for player-facing observations, operator-facing state, special mechanics, actors, behavior, rewards, and downstream consequences, omitting categories the encounter does not need
**ELSE** use ordinary continuous prose when the material will be read once rather than queried during live operation

## Do
- Put the first perceivable facts where the operator can find them before hidden state, explanation, or resolution details.
- Separate environmental or physical facts the operator must track from prose intended to be spoken or paraphrased to players.
- Keep encounter-specific rules, hazards, puzzles, checks, or exceptions next to the situation that invokes them.
- Place an actor's statistics, special capabilities, and tactical behavior close enough that one live decision does not require several page jumps.
- Put recoverable treasure, evidence, or other post-encounter discoveries in the same entry when they belong to that local state.
- State alerts, aftermath, reinforcements, changed access, or other downstream effects where the operator finishes resolving the encounter.
- Use consistent section order across similar entries so the operator can predict where a kind of information will appear.

## Don't
- Write an encounter as uninterrupted literary prose when the operator must repeatedly search inside it for rules and state.
- Scatter one actor's behavior, statistics, equipment, and consequences across distant sections without a live-use reason.
- Force every entry to contain ceremonial headings for categories that have no information in that encounter.
- Hide a critical rule exception inside descriptive flavor that the operator is likely to paraphrase or skip.
- Duplicate system rules at length when a concise local reminder or reference is enough to operate the encounter.

## Checklist
- The operator can locate player-facing observations before reading hidden resolution information aloud by mistake.
- Special mechanics and the state that triggers them are colocated.
- Each consequential actor's capabilities and behavior can be retrieved without reconstructing them from unrelated sections.
- Rewards or discoveries that belong to the encounter are findable at the point they become relevant.
- Downstream consequences are visible before the operator leaves the entry.
- Repeated encounter entries use a sufficiently stable order that retrieval becomes predictable without preserving empty sections.

## Notes
An encounter entry is an operational interface as well as prose. During play the operator does not consume it from top to bottom once; they move among description, state, rules, actors, behavior, and aftermath as the scene changes. Predictable information architecture therefore matters independently of sentence quality.

The useful unit is the retrieval task, not a mandatory template. A simple empty room may need only observable state. A complex hazard may need player-facing description, physical geometry, a special procedure, creature behavior, recoverable evidence, and a consequence for nearby areas. Keep the needed pieces together and omit the rest.

Variant `writing_adventure_modules_variant_write_escalating_hazards_as_trigger_threshold_response_chains` makes a local state machine readable at the table. Start with what the operator sees before escalation, name the action or event that changes state, state what must be counted or tracked, and list each threshold in the order it becomes relevant. Put relief, escape conditions, and non-obvious countermeasures after the danger logic but close enough that the operator can retrieve them during the same encounter. This format is useful when repeated ordinary actions compound danger; it is unnecessary for a trap or hazard that resolves once and leaves no changing local state.
