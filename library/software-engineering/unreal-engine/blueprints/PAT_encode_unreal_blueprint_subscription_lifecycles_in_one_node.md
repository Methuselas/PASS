---
object_id: PAT_encode_unreal_blueprint_subscription_lifecycles_in_one_node
object_type: pattern
name: Encode Unreal Blueprint Subscription Lifecycles in One Node
library_path:
- software-engineering
- unreal-engine
- blueprints
stage_binding: 0 design
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: PAT_give_every_acquired_resource_one_named_owner
tags:
- unreal_engine
- blueprints
- subscriptions
- delegates
- lifecycle
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

# Encode Unreal Blueprint Subscription Lifecycles in One Node

## Pattern Rule
**IF** Blueprint users must acquire and release a callback subscription with several related event paths
**THEN** expose the lifecycle as one coherent node whose subscribe identity, duplicate policy, event outputs and automatic cleanup contract are visible and enforced together.

## Do
- Choose a stable subscription identity containing the listener plus any channel, source or filter needed to distinguish simultaneous subscriptions. State whether repeated subscribe replaces, ref-counts, joins or rejects.
- Put subscribe and unsubscribe entry pins beside the event outputs they control. Make required cleanup obvious, but also remove subscriptions automatically when the listener, source, world or owning subsystem ends.
- Keep subscriber references weak unless retaining the listener is an explicit part of the API. Prune invalid listeners before broadcast and never let a registry accidentally keep arbitrary Blueprint instances alive.
- Validate source lookup, world context, filters and delegate binding before registration. Return an explicit failure path or compiler/runtime diagnostic when the requested source cannot be resolved.
- Make callback dispatch safe when a callback subscribes, unsubscribes or destroys another listener. Iterate a stable snapshot or defer registry mutations until dispatch completes.
- Check optional delegates before execution. Define ordering and reentrancy when several event outputs can fire in one frame.
- Store the registry in a subsystem or owner whose network/world scope matches the events. Avoid a server-only manager for callbacks expected on clients.
- Test duplicate registration, explicit unsubscribe, listener destruction, source destruction, world teardown, reentrant removal, no connected callback pins and multiple events in one frame.

## Don't
- Don't key a long-lived registry with strong raw UObject references unless keeping listeners alive is intentional and documented.
- Don't rely on every graph author to call unsubscribe on every exit path.
- Don't mutate a container directly while invoking callbacks from an iterator over that same container.
- Don't accept a filter or team parameter and then silently ignore it.

## Checklist
- What exactly identifies one subscription and what does a duplicate call do?
- Which owner guarantees cleanup if explicit unsubscribe never runs?
- Can callbacks safely alter the registry during dispatch?
- Does manager placement match server, client, editor and world lifetime expectations?

## Notes
The custom node is valuable when it makes the safe protocol easier than manual delegate wiring. It should reduce lifecycle states users can forget, not merely hide them.
