---
object_id: AP_publish_an_unreal_latent_blueprint_action
object_type: ap
name: Publish an Unreal Latent Blueprint Action
library_path:
- software-engineering
- unreal-engine
- editor
stage_binding: 1 skeleton
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- blueprints
- latent_actions
- node_design
cross_links:
- rel: supports
  target_object_id: PAT_model_unreal_latent_actions_as_owned_state_machines
- rel: supports
  target_object_id: PAT_shape_blueprint_function_nodes_for_graph_use
reference:
  source_title: Extending and Customizing Unreal Engine Editor
  author: Roger Mattsson
confidence: medium
references: []
variants: []
---

# Publish an Unreal Latent Blueprint Action

## Objective
Expose a multi-frame C++ operation as one readable Blueprint node with deterministic identity, safe references and explicit terminal continuations.

## Steps / Flow
1. Define the operation states, continuation outputs, duplicate-call policy, cancellation behavior and the conditions under which the operation must finish silently or report failure.
2. Declare a Blueprint-callable wrapper with category and tooltip metadata, `Latent`, `LatentInfo`, and an appropriate `WorldContext`. Expand a small stable result enum into execution pins when it makes terminal paths clearer.
3. Resolve the world from the context object. Reject an invalid context before allocating anything and obtain that world's latent-action manager.
4. Look up the callback-target/UUID identity. Apply the declared ignore, replace or join policy rather than registering accidental duplicates.
5. Allocate a focused `FPendingLatentAction` state machine. Copy value state, retain the continuation metadata and use weak references for UObject dependencies not guaranteed by the callback target.
6. In `UpdateOperation`, validate dependencies and optional delegates, perform only bounded work, set the result state before triggering a link and end exactly once on success, cancellation, failure or owner loss.
7. Test first-frame behavior, continued ticks, every terminal pin, unbound optional inputs, duplicate UUIDs, destroyed dependencies, invalid world context and callback-target destruction.
8. Profile the expected concurrent action count. Replace per-frame polling with a subsystem callback or event when scale or latency makes polling wasteful.

## Notes
The public node should hide manager and continuation boilerplate without hiding ordering, cost or failure. A reusable project base class may own the common continuation fields once several actions prove the repetition.
