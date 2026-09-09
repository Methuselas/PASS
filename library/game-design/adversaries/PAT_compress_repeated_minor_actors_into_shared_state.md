---
object_id: PAT_compress_repeated_minor_actors_into_shared_state
object_type: pattern
name: Compress Repeated Minor Actors into Shared State
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
- groups
- state
- compression
cross_links:
- rel: related_to
  target_object_id: PAT_preserve_decision_relevant_state_while_compressing_resolution_procedure
confidence: high
references: []
variants: []
---

# Compress Repeated Minor Actors into Shared State

## Pattern Rule
**IF** many similar low-decision actors participate in the same scene or are controlled by the same participant
**THEN** first decide what function the group performs in the scene, then choose the least detailed representation that preserves meaningful targeting, risk, capability, consequence, and choice
**ELSE** keep actors individually represented when their separate state creates decisions the scene actually uses.

## Do
- Decide whether the group functions as individually targetable actors, shared state, a collective threat, an obstacle or terrain condition, a pressure source, background scale, or a mixture that changes over the scene.
- Identify which values are invariant across the group, such as initiative handling, common resources, repeated damage conventions, or other state that would otherwise be serviced identically for every actor.
- Keep separate state only where individual identity, position, condition, equipment, capability, or consequence changes a decision.
- Apply the same compression test to player-owned or player-commanded drones, summons, pets, hirelings, and helpers; controller identity does not by itself justify full individual fidelity.
- Preserve the game's established resolution grammar so compression reduces repeated servicing work rather than creating a second rules engine for groups.
- Expand an actor back into individual detail when play promotes it into a recurring, consequential, or strategically distinct role.

## Don't
- Give every minor actor a full independent record merely because the system can represent one.
- Merge state that players need in order to choose targets, assess danger, protect a specific actor, or understand distinct consequences.
- Treat player-controlled subordinate actors as exempt from table-bandwidth costs.
- Compress a group by replacing meaningful decisions with an opaque aggregate that no longer exposes what changed.

## Checklist
- The group's scene function is explicit enough to justify whether it needs individual actors, shared state, collective handling, environmental pressure, or background representation.
- Repeated values that do not create individual decisions are handled once rather than serviced separately for every actor.
- Any state kept per actor has a named decision or consequence that requires the distinction.
- A representative scene with several similar actors has been checked for reduced bookkeeping, lookup, or serial handling.
- Player-owned subordinate actors are tested by the same decision-value standard as referee-controlled actors.
- An actor can be expanded cleanly if later play makes its individual state consequential.

## Notes
A large group does not automatically need to be represented as many independently resolving actors. Its useful fidelity depends first on what the mass is doing in the scene, then on which individual distinctions create decisions. Shared initiative, resources, damage, movement, or other handling can preserve scale while removing repeated servicing work, and an individual can be expanded whenever play makes that identity consequential.
