---
object_id: writing_adventure_modules_write_pregenerated_roles_as_playable_decision_positions
object_type: pattern
name: Write Pregenerated Roles as Playable Decision Positions
library_path:
  - writing
  - adventure-modules
  - foundations
stage_binding: 0 design
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: medium
foundation_object_id: none
tags:
  - adventure_modules
  - pregenerated_characters
  - one_shots
  - ensemble
  - characterization
cross_links:
  - rel: related_to
    target_object_id: writing_adventure_modules_partition_information_by_reader_role_and_reveal_state
reference:
  source_title: "An Act of Treason"
  author: "Jan Hendrik Friedrich and Michael Chumbler"
confidence: high
references: []
variants:
  - variant_id: writing_adventure_modules_variant_prime_pregenerated_ensemble_with_shared_launch_script
    variant_name: Prime a Pregenerated Ensemble with a Shared Launch Script
    variant_basis: method_sequence
    difference_from_foundation: After the role packets establish each character's function and pressures, use one short shared exchange to demonstrate voice, relationships, current mission context, and a looming disagreement before returning control to unscripted play.
    when_to_use: A one-shot or convention scenario needs several players to inhabit unfamiliar pregenerated characters quickly and the ensemble's relationships matter immediately.
    when_not_to_use: The group already knows the characters, the script would dictate a consequential choice, or reading assigned lines would slow the opening more than it clarifies the roles.
    absorbed_from_object_id: none
---

# Write Pregenerated Roles as Playable Decision Positions

## Pattern Rule
**IF** an adventure relies on pregenerated player characters to establish an ensemble quickly
**THEN** write each role as a playable decision position with a clear mission function, useful competence, relationship pressure, behavioral cues, and room for player judgment rather than as a stat block or biography alone
**ELSE** let ordinary character creation establish those choices when players are expected to build their own roles

## Do
- State each role's immediate function in the scenario, including relevant authority, responsibility, assignment, or reason that other characters rely on that person.
- Give each role capabilities that are likely to matter during the written scenario so the packet communicates what the character can credibly attempt, not merely who the character used to be.
- Establish at least one live relationship with another player role, such as command, mentorship, rivalry, trust, dependence, resentment, or partnership.
- Give each role one or two pressure-bearing tendencies that can shape choices without predetermining them, such as caution versus obedience, ambition versus loyalty, discipline versus empathy, or confidence versus restraint.
- Write background only when it explains present competence, relationship, obligation, vulnerability, or a likely interpretation of events.
- Keep public role information separate from any private fact that only one player should know, and state clearly when a private fact is intended to affect play.
- Check the ensemble as a set: each role should have a reason to participate, something distinct to contribute, and at least one reason to care about another role's decisions.

## Don't
- Treat a complete character sheet as a complete player role when it does not tell the player what matters now.
- Give every role the same attitude, competence profile, or relationship to authority and expect names or catchphrases to create differentiation.
- Write a private backstory that cannot affect any plausible decision in the scenario.
- Make one role the only person allowed to solve every load-bearing problem while the rest function as spectators.
- Encode a mandatory moral or tactical decision as personality. A tendency can create pressure; the player's consequential choice must remain theirs.
- Require players to memorize setting history before they can understand their immediate relationships and responsibilities.

## Checklist
- Every pregenerated role has a concrete reason to be present in the opening situation.
- Every role has at least one competence that the scenario gives a credible opportunity to use.
- Every role has at least one live relationship to another player role that can affect a scene.
- The packet distinguishes behavioral pressure from mandatory action.
- Background details retained in the packet explain present choices, access, competence, or relationships.
- No one role monopolizes all load-bearing decisions or information merely because the module needs a leader.
- A player can summarize who the character is in the current situation without reciting the whole biography.

## Notes
Pregenerated characters are part of the adventure's writing architecture. In a short scenario, they can establish the social and decision structure before play begins: who leads, who challenges, who mediates, who has the relevant expertise, and which relationships make an otherwise simple order difficult. The useful packet is therefore not just a mechanical object. It is a compact interface between the scenario and the player, designed to make the first consequential choice feel like something this particular character could interpret rather than a generic avatar selecting from options.

`writing_adventure_modules_variant_prime_pregenerated_ensemble_with_shared_launch_script` adds a short rehearsal layer when an unfamiliar ensemble needs to become legible immediately. Write a brief shared exchange that puts the current objective, relationship hierarchy, voice differences, and one relevant tension into spoken interaction. Ask players to perform the lines in the way they think their characters would speak them, then end the script before the first consequential decision so the demonstration primes play without replacing it. The script should contain only information the characters may possess at that moment and should not become the only place where a load-bearing fact appears.
