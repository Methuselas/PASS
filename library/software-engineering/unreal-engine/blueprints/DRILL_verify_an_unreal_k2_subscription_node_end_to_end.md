---
object_id: DRILL_verify_an_unreal_k2_subscription_node_end_to_end
object_type: drill
name: Verify an Unreal K2 Subscription Node End to End
library_path:
- software-engineering
- unreal-engine
- blueprints
stage_binding: 4 final
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- blueprints
- k2_nodes
- subscriptions
- cooking
cross_links:
- rel: teaches
  target_object_id: AP_publish_an_unreal_blueprint_subscription_node
reference:
  source_title: Extending and Customizing Unreal Engine Editor
  author: Roger Mattsson
confidence: medium
references: []
variants: []
target_skill: Verify an Unreal K2 Subscription Node End to End
---

# Verify an Unreal K2 Subscription Node End to End

## Practice Task
Build a small custom K2 node that subscribes and unsubscribes one listener to two typed callback outputs, then prove its visible contract survives graph editing, compilation, runtime teardown and cooking.

## Target Skill
Practise `AP_publish_an_unreal_blueprint_subscription_node` across compiler and runtime lifecycle boundaries.

## Setup
- An Unreal plugin with separate runtime and `UncookedOnly` modules.
- A deterministic runtime event source and registry that can emit two callbacks, destroy the source, and expose current subscriber count.
- Blueprint automation or fixture graphs for connected, partially connected and invalid node configurations, plus a cooked test target.

## Instructions
1. State subscription identity, duplicate policy, manager scope, callback order, reentrant mutation policy and automatic cleanup conditions.
2. Implement the runtime registry with weak listener ownership and an internal-use-only subscribe/unsubscribe function. Retain evidence for duplicate registration and callback-driven unregister.
3. Implement the custom node and checked expansion. Compile fixtures with neither, one and both callback outputs connected, and with two node instances in one graph.
4. Connect and disconnect source/filter pins, copy/paste the node, undo and redo, save/reload the Blueprint and restart the editor. Record pin types, defaults, generated names and compile results after each transition.
5. Inspect compiler diagnostics and the expanded graph or equivalent compiler evidence. Verify all user links moved intentionally, no required pin remains wildcard or disconnected, and each callback uses the destination delegate's reflected signature.
6. At runtime, exercise subscribe, duplicate subscribe, both callbacks, explicit unsubscribe, listener destruction, source destruction, world teardown and unregister from inside a callback. Check subscriber counts and callback delivery after each action.
7. Build an uncooked target that compiles the fixture Blueprints, then build and run a cooked target. Verify the K2/compiler module is absent while expanded runtime behavior remains functional.
8. Preserve automation output, dependency or package evidence and the exact unexercised cases; a successful editor compile alone does not pass.

## Success Check
- Reconstruction, paste, undo and reload preserve the visible node contract without pin drift or generated-name collisions.
- Invalid signatures or connections produce localized compile errors; successful expansion accounts for every original link.
- Subscription cleanup succeeds for explicit release, listener/source destruction and world teardown, including reentrant unregister.
- The uncooked target can compile the node, the cooked target omits compiler-only dependencies, and runtime callbacks still behave as specified.
- Evidence covers both compiler behavior and runtime lifecycle behavior.

## Common Failures
- Testing one node instance and missing internal-event name collisions after duplication.
- Keeping listeners alive through strong registry keys and mistaking that for correct cleanup.
- Mutating the subscriber container during direct iteration from a callback.
- Declaring success from an editor build without inspecting a cooked dependency boundary.

## Notes
Use a minimal event domain so the evidence stays focused on node reconstruction, lowering, subscription ownership and packaging rather than game-specific behavior.
