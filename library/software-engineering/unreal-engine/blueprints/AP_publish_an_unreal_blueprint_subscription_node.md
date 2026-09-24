---
object_id: AP_publish_an_unreal_blueprint_subscription_node
object_type: ap
name: Publish an Unreal Blueprint Subscription Node
library_path:
- software-engineering
- unreal-engine
- blueprints
stage_binding: 1 skeleton
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
- delegates
cross_links:
- rel: supports
  target_object_id: PAT_encode_unreal_blueprint_subscription_lifecycles_in_one_node
- rel: supports
  target_object_id: PAT_lower_unreal_k2_exec_outputs_to_typed_delegate_events
- rel: supports
  target_object_id: PAT_expand_custom_unreal_k2_nodes_with_verified_pin_contracts
- rel: supports
  target_object_id: PAT_place_unreal_k2_compiler_extensions_in_uncooked_modules
reference:
  source_title: Extending and Customizing Unreal Engine Editor
  author: Roger Mattsson
confidence: medium
references: []
variants: []
---

# Publish an Unreal Blueprint Subscription Node

## Objective
Publish a custom Blueprint node that turns a multi-event delegate subscription into a readable, lifecycle-safe graph construct and compiles entirely into supported runtime calls and delegates.

## Steps / Flow
1. Confirm repeated use across graphs or authors justifies a custom node. Define listener/source identity, event outputs, filters, duplicate behavior, network/world scope, reentrancy and cleanup guarantees before designing pins.
2. Implement the runtime registry in a runtime-capable owner. Use weak listener references, safe dispatch under reentrant mutation, explicit source lookup failure and automatic teardown cleanup.
3. Expose one internal-use-only Blueprint-callable function for subscribe/unsubscribe operations with typed delegate parameters and only the metadata needed by the expansion.
4. Put the custom `UK2Node` in an UncookedOnly module. Allocate stable subscribe/unsubscribe inputs, source/filter inputs and callback outputs; expose node properties only when they are configuration rather than dataflow.
5. Register the node and supply concise category, title and tooltip text. Make cleanup expectations and callback meanings visible at the graph interface.
6. In `ExpandNode`, spawn and configure the internal runtime call and self/context inputs. Move visible entry and data links through checked compiler helpers.
7. For each connected callback output, apply `PAT_lower_unreal_k2_exec_outputs_to_typed_delegate_events`; validate signature, unique name and both generated connections.
8. Confirm all original links were transferred, then compile tests for zero, one and all callback outputs; multiple node instances; copy/paste; reconstruction; explicit unsubscribe; duplicate subscribe; owner/source destruction; world teardown and callback-driven unregister.
9. Build an uncooked target that compiles the node and a cooked target that proves only the runtime registry/calls remain.

## Notes
Gameplay tags, enums and actor references are interchangeable source selectors. The reusable capability is the safe lowering of a paired subscription protocol into a compact Blueprint interface.
