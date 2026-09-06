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
reference:
  source_title: Designing TTRPGs For Dummies
  author: Martin Buinicki
confidence: high
references: []
variants: []
---

# Compress Repeated Minor Actors into Shared State

## Pattern Rule
**IF** many similar low-decision actors participate in the same scene or are controlled by the same participant
**THEN** factor repeated state and procedures into shared group-level handling while preserving individual distinctions only where they change meaningful targeting, risk, capability, or consequence
**ELSE** keep actors individually represented when their separate state creates decisions the scene actually uses.

## Do
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
- Repeated values that do not create individual decisions are handled once rather than serviced separately for every actor.
- Any state kept per actor has a named decision or consequence that requires the distinction.
- A representative scene with several similar actors has been checked for reduced bookkeeping, lookup, or serial handling.
- Player-owned subordinate actors are tested by the same decision-value standard as referee-controlled actors.
- An actor can be expanded cleanly if later play makes its individual state consequential.

## Notes
Uniform mechanics do not require uniform state servicing. A scene with many similar actors can preserve the distinctions that matter while sharing repeated initiative, resource, damage, or other handling that would otherwise multiply without adding decisions. The test is not whether an actor is friendly or hostile, but whether its individual state changes what participants can meaningfully decide.
