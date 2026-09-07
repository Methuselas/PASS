---
object_id: PAT_separate_persistent_identity_from_replaceable_embodiment
object_type: pattern
name: Separate Persistent Identity from Replaceable Embodiment
library_path:
- game-design
- characters
stage_binding: 0 design
lane_fit: both
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- characters
- identity
- embodiment
- state
- action-economy
cross_links: []
confidence: high
references: []
variants:
- variant_id: game_design_variant_distribute_one_identity_across_multiple_embodiments
  variant_name: Distribute One Identity Across Multiple Embodiments
  variant_basis: constraint
  difference_from_foundation: Allow one persistent actor to occupy several bodies at once while separating local embodiment state from shared identity state and preserving a shared cognitive or action bandwidth where appropriate.
  when_to_use: One mind, spirit, intelligence, or other persistent actor can maintain multiple simultaneous physical presences but those presences are not intended to become independent full characters.
  when_not_to_use: The bodies are independent minds, companions, drones with their own operators, or separate characters whose full action economies are intentionally independent.
  absorbed_from_object_id: none
---

# Separate Persistent Identity from Replaceable Embodiment

## Pattern Rule
**IF** a player character can meaningfully change, abandon, replace, or lose the body or vessel through which it acts
**THEN** define separate persistent-identity state and embodiment-local state, then specify how they merge, transfer, conflict, and survive destruction or replacement
**ELSE** keep identity and body on one character layer when embodiment is not independently mutable in play.

## Do
- Assign memories, personality, advancement, relationships, obligations, identity-level resources, and other continuity state to the persistent layer when they should survive a body change.
- Assign movement, physical ability, durability, senses, natural attacks, environmental tolerances, and other vessel properties to the embodiment layer when they should change with the body.
- Define transition cost, time, access, eligibility, occupancy limits, and what happens when no usable body is available.
- State precedence when persistent and embodiment state both provide a value for the same statistic or permission.
- Make destruction consequences explicit: loss of the vessel can be a setback without implying loss of the enduring character, but it still needs costs and vulnerabilities appropriate to the game.
- Test body replacement against equipment, healing, status effects, imprisonment, advancement, and other systems that normally assume one stable physical actor.

## Don't
- Copy the full character sheet into every body when most of that state is supposed to belong to one enduring identity.
- Let a new vessel erase wounds, obligations, resource losses, or other persistent consequences unless reset is an intentional benefit with an explicit price.
- Leave unclear whether effects target the identity, the vessel, or both.
- Allow simultaneous embodiments to multiply every action, resource, and mental capability automatically unless that multiplication is the intended power budget.

## Checklist
- Every major character statistic can be assigned to persistent identity, current embodiment, or an explicit merge rule.
- Body destruction and body replacement have defined state transitions.
- Persistent consequences cannot be escaped accidentally by changing vessels.
- Vessel-specific limitations and benefits actually change play after a transfer.
- Systems that target one physical actor have been checked for ambiguous behavior when embodiment changes.

## Notes
Replaceable bodies turn a character sheet into layered state. The important design decision is not whether the fiction calls the transfer possession, uploading, reincarnation, chassis switching, or something else; it is which parts of the player character endure and which belong to the current vessel.

Variant `game_design_variant_distribute_one_identity_across_multiple_embodiments` extends the same ownership model to simultaneous bodies. Local damage, position, and physical actions can remain separate while memory, long-term resources, and cognitive throughput stay shared. A shared action budget is especially useful when the fiction describes one mind in several places and the design wants more presence without multiplying the actor into several complete turns.
