---
object_id: PAT_snapshot_unreal_container_iteration_before_exposing_loop_pins
object_type: pattern
name: Snapshot Unreal Container Iteration Before Exposing Loop Pins
library_path:
- software-engineering
- unreal-engine
- blueprints
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- blueprints
- containers
- iteration
- determinism
cross_links:
- rel: related_to
  target_object_id: PAT_expand_custom_unreal_k2_nodes_with_verified_pin_contracts
reference:
  source_title: Extending and Customizing Unreal Engine Editor
  author: Roger Mattsson
confidence: medium
references: []
variants: []
---

# Snapshot Unreal Container Iteration Before Exposing Loop Pins

## Pattern Rule
**IF** a Blueprint loop node exposes elements from a map, set or another container whose contents or order may change
**THEN** choose an explicit iteration contract, derive values and termination from one stable view, and never combine snapshotted elements with live bounds.

## Do
- State whether iteration observes a start-time snapshot or a live container. Prefer a snapshot for a Blueprint loop whose body can call arbitrary user logic.
- Build one entry representation or otherwise preserve the key/value association guaranteed by the container API. Do not assume independently produced key and value arrays share an undocumented order.
- Capture the iteration count from the same snapshot used for element lookup. Use that count for every bounds check and completion decision.
- Document that map and set order is unspecified unless the node explicitly sorts by a stable, supported key. Do not promise deterministic order merely because repeated tests look stable.
- Decide how additions, removals and value changes made by the loop body affect the current pass. With snapshot semantics, defer them to later passes and keep current outputs stable.
- Handle empty containers without element lookup, emit completion exactly once and keep key/value outputs valid only during the loop continuation.
- Test empty, one-entry and sparse containers, mutation from the loop body, duplicate-value maps, reconstruction and repeated runs with order-sensitive assertions disabled unless sorting is part of the contract.

## Don't
- Don't snapshot keys and values but query the live map length on every iteration.
- Don't index two separately generated arrays unless the API explicitly guarantees their positional correspondence.
- Don't let user graph execution mutate the data structure that controls the next unchecked lookup.
- Don't market hash-container iteration as ordered or deterministic by default.

## Checklist
- Do element lookup, loop bound and completion all come from the same view?
- Is key/value association guaranteed by construction rather than observation?
- Is mutation-during-iteration behavior visible and tested?
- Does the node avoid implying an ordering contract it does not implement?

## Notes
The safest compiler expansion evaluates arbitrary user loop bodies against stable iteration state. If live iteration is truly required, it needs mutation detection and a documented invalidation policy rather than snapshot-like pins over changing storage.
