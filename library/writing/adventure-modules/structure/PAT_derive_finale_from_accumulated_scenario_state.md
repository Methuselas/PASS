---
object_id: writing_adventure_modules_derive_finale_from_accumulated_scenario_state
object_type: pattern
name: Derive the Finale from Accumulated Scenario State
library_path:
  - writing
  - adventure-modules
  - structure
stage_binding: 2 block
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: medium
foundation_object_id: none
tags:
  - adventure_modules
  - endings
  - consequences
  - branching
  - state_tracking
cross_links:
  - rel: related_to
    target_object_id: writing_adventure_modules_anchor_episodic_adventure_to_stable_mission_spine
  - rel: related_to
    target_object_id: writing_adventure_modules_write_reactive_location_as_stateful_response_system
reference:
  source_title: "The Arasaka Brainworm"
  author: "Thomas M. Kane"
confidence: high
references: []
variants:
  - variant_id: writing_adventure_modules_variant_return_revealed_wrongdoing_to_affected_stakeholders
    variant_name: Return Revealed Wrongdoing to Affected Stakeholders
    variant_basis: method_sequence
    difference_from_foundation: After a hidden past wrongdoing is established, make disclosure, confrontation, concealment, negotiation, or public judgment the final pressure, and provide likely stakeholder responses without prescribing a single moral verdict.
    when_to_use: The adventure's discovered truth materially affects the legitimacy, relationships, safety, or standing of people or institutions who remain available for confrontation after the investigative or physical objective is complete.
    when_not_to_use: The truth has no surviving stakeholder consequence, the affected parties are absent or unreachable, or the scenario still has a more immediate unresolved objective that must be completed first.
    absorbed_from_object_id: none
---

# Derive the Finale from Accumulated Scenario State

## Pattern Rule
**IF** an adventure supports several valid approaches whose consequences can leave different allies, enemies, alert levels, resources, target conditions, or exit routes in play
**THEN** define what counts as completing the mission and which accumulated states shape the ending, then let the final confrontation, escape, withdrawal, or handoff emerge from those states instead of forcing one canned final encounter
**ELSE** use a fixed climax when the scenario's established dependencies genuinely require the same culminating event

## Do
- Separate mission completion from finale form: state what objective must be accomplished even when the last scene can vary.
- Identify the few state variables most likely to determine the ending, such as who survives, who is alerted, what evidence was obtained, which relationships changed, what transportation remains, and what opposition still has reason and ability to act.
- Provide several likely ending families or pressures rather than scripting one mandatory sequence of actions.
- Honor advantages the characters created earlier, including secrecy, cooperation, disabled systems, acquired access, prepared transport, or neutralized threats.
- Carry earlier liabilities forward as well, including exposed identities, active pursuit, damaged resources, betrayed allies, or unresolved obligations.
- Use only opposition, rescue, escape, or retaliation that follows from capabilities and relationships already established in the scenario.
- After the immediate ending, state the consequences that remain relevant to payment, reputation, future pursuit, surviving relationships, or follow-up adventures.

## Don't
- Force a boss fight, chase, or ambush merely because the module appears to need a dramatic last scene after the objective has already been solved another way.
- Erase a successful quiet approach by automatically triggering the same maximal opposition written for a loud failure state.
- Rescue the characters with an unestablished escape route or ally when their own decisions have left them trapped.
- Invent stronger opposition retroactively only to punish an unexpectedly effective plan.
- Leave completion undefined and call the absence of a written ending "open-ended."
- Treat aftermath hooks as substitutes for resolving the current mission's immediate consequences.

## Checklist
- The operator can state the mission's completion condition independently of any one final scene.
- The ending depends on a bounded set of scenario states that earlier play can actually change.
- At least two materially different accumulated states can produce different plausible finales or exits.
- Earlier advantages and liabilities remain visible in the ending rather than being reset for dramatic convenience.
- Every major late response comes from an actor, resource, or capability established before the finale.
- The module explains what immediate consequences remain after the characters leave the final active scene.
- A fixed climax is used only when a named dependency makes it necessary, not simply because finales are expected to look alike.

## Notes
Open-ended adventure writing still needs closure. The useful alternative to a prewritten final encounter is not to abandon structure, but to define the objective and let the accumulated situation decide how the last pressure manifests. A quiet extraction, negotiated departure, improvised escape, pursuit, or violent confrontation can all be legitimate endings when the scenario has established the actors and resources that make them possible.

This method is especially useful in infiltration, investigation, rescue, and heist structures where player choices change who knows what and which routes remain open. It rewards preparation because the finale remembers earlier work, and it preserves consequences because a messy approach can leave a genuinely harder exit without the author manufacturing a new obstacle at the last moment.

`writing_adventure_modules_variant_return_revealed_wrongdoing_to_affected_stakeholders` uses social accountability as a legitimate finale form. Once the facts are established, give the operator the implicated parties, affected community or relationships, and several credible response families: confession, denial, resignation, justification, rejection, forgiveness, retaliation, concealment, or divided opinion where the fiction supports them. Do not announce which response is morally correct; make the consequences follow from established interests, history, and what the characters choose to reveal.
