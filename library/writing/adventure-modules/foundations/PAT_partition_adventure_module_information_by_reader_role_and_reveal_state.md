---
object_id: writing_adventure_modules_partition_information_by_reader_role_and_reveal_state
object_type: pattern
name: Partition Adventure-Module Information by Reader Role and Reveal State
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
  - audience
  - information_architecture
  - disclosure
  - game_master
cross_links: []
reference:
  source_title: "Caravan to Ein Arris"
  author: "Creede and Sharleen Lambard"
confidence: high
references: []
variants:
  - variant_id: writing_adventure_modules_variant_write_read_aloud_as_minimum_fact_set_with_optional_sensory_palette
    variant_name: Write Read-Aloud as a Minimum Fact Set with an Optional Sensory Palette
    variant_basis: emphasis
    difference_from_foundation: Keep the player-facing passage short enough to preserve the required observable facts, write it in a natural speakable register, render important qualities through concrete perceivable evidence rather than evaluative labels, and give the operator a selective nonvisual sensory palette that can intensify mood without changing the information state or forcing verbatim delivery.
    when_to_use: A scene has a few facts players must receive and benefits from concrete sensory atmosphere, especially at a critical reveal, transition, threat, or other moment worth slowing down for.
    when_not_to_use: Exact wording is itself evidence, a legal or ritual text must be quoted precisely, the characters cannot perceive the proposed detail, or added description would bury actionable information and slow live play.
    absorbed_from_object_id: none
  - variant_id: writing_adventure_modules_variant_seed_open_exploration_with_operator_keyed_rumors
    variant_name: Seed Open Exploration with Operator-Keyed Rumors
    variant_basis: method_sequence
    difference_from_foundation: Give players a bounded pool of in-world leads whose truth status is marked only for the operator, route additional rumors through plausible speakers or situations, and use the mix to prompt inquiry without turning uncertain talk into authoritative exposition.
    when_to_use: An open adventure area contains several possible directions and players benefit from incomplete social information that suggests places, dangers, opportunities, or questions without supplying one mandatory route.
    when_not_to_use: One specific fact is required for forward motion, a false lead would consume disproportionate time with no useful consequence, or the scenario cannot support players following an inaccurate rumor.
    absorbed_from_object_id: none
---

# Partition Adventure-Module Information by Reader Role and Reveal State

## Pattern Rule
**IF** an adventure module is operated by one reader while players experience only selected information through that reader
**THEN** separate what the operator must know, what players may know now, and what becomes available only after a stated trigger, while giving each audience enough context to act without exposing later revelations
**ELSE** use ordinary audience calibration when every reader can safely share the same information

## Do
- Mark each consequential fact during planning as operator-only, player-available at the start, revealable after a trigger, or optional background.
- Give the player-facing opening the actionable premise: what the characters are doing, why they are involved, what immediate role they occupy, and the practical stakes or terms they can reasonably know.
- Give the operator hidden motives, future turns, contingency facts, and the conditions under which those facts become visible in play.
- Keep read-aloud or paraphrase-ready passages inside the characters' current sensory and informational limits.
- Place a reveal instruction where the operator will need it, naming the event, discovery, conversation, or other trigger that changes what the players can know.
- Check that concealed information can still shape earlier events through observable evidence without leaking the answer through explanatory prose meant only for the operator.

## Don't
- Put a secret in player-facing orientation merely because the operator needs it early.
- Withhold the characters' own job, destination, relationship, or immediate stakes in the name of preserving mystery.
- Write read-aloud text that states hidden motives, offstage facts, or conclusions the characters could not yet possess.
- Scatter one crucial secret across several distant sections without a usable reminder at the moment of revelation.
- Treat operator knowledge and player knowledge as two copies of the same exposition with only names removed.

## Checklist
- The operator can identify the scenario's hidden truth and future revelations before play.
- Players can understand their initial situation and make a meaningful first decision without access to operator-only material.
- Every important withheld fact has a credible trigger for disclosure.
- Player-facing prose contains no knowledge the characters have not earned or been given.
- The operator can find the information needed at each reveal without reconstructing it from unrelated sections.
- Early observable evidence remains compatible with the later truth.

## Notes
Adventure modules have a mediated audience structure: the operator reads the document directly, but players usually encounter the work through selected description, dialogue, handouts, and consequences. This specializes general audience calibration by adding reveal state to the handoff. The useful distinction is not simply "GM text" versus "player text"; some information begins hidden and later becomes player knowledge, so the module must state both ownership and timing. Clear partitioning lets the operator understand the whole causal situation while preserving discovery for the players.

`writing_adventure_modules_variant_write_read_aloud_as_minimum_fact_set_with_optional_sensory_palette` separates informational obligation from performance latitude. The base passage carries the observations that must survive paraphrase. Replace labels such as crowded, dangerous, weak, or enormous with a few physical facts that let players perceive the condition: bodies pressed around a table, a step splintering under weight, a figure dragging a stool, or a scale comparison that makes size legible. Add sound, smell, touch, temperature, or taste when those channels naturally belong to the characters' experience rather than filling a five-sense quota. Concentrate richer description at a small number of critical moments and use lighter sensory cues elsewhere; a long description of something the characters cannot currently perceive is dead weight in live delivery. Write sentences the facilitator can say aloud without mentally translating ornate written diction into ordinary speech. Optional cues can alter intensity and atmosphere without changing what the characters know, keeping read-aloud material vivid without making it a brittle script or burying the facts the scene must communicate.
`writing_adventure_modules_variant_seed_open_exploration_with_operator_keyed_rumors` uses reveal-state partitioning to support uncertain social knowledge in an open scenario. Mark each rumor's truth status for the operator, decide who can plausibly voice it, and let players choose what to investigate; do not use this method for a single indispensable clue. The rumor pool should create direction and questions without making the document itself ambiguous about what is actually true.
