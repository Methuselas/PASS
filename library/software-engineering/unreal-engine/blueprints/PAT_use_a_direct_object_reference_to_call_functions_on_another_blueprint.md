---
object_id: PAT_use_a_direct_object_reference_to_call_functions_on_another_blueprint
object_type: pattern
name: Use a Direct Object Reference to Call Functions on Another Blueprint
library_path:
- software-engineering
- unreal-engine
- blueprints
stage_binding: 0 design
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- blueprints
- communication
- object_reference
cross_links:
- rel: related_to
  target_object_id: PAT_use_an_event_dispatcher_to_notify_listeners_without_naming_them
- rel: related_to
  target_object_id: PAT_guard_object_references_with_is_valid
- rel: related_to
  target_object_id: PAT_declare_who_may_read_and_write_blueprint_state
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Use a Direct Object Reference to Call Functions on Another Blueprint

## Pattern Rule
**IF** one Blueprint must call functions on or read state from a specific other Blueprint, and the sender knows the receiver's concrete type
**THEN** hold an object reference variable to the receiver and use it as the Target of the calls, because a direct reference is the tightest form of Blueprint communication and is right for one-to-one calls on a known receiver.

## Do
- Create an object reference variable typed to the receiver's class (or a base class it inherits from).
- Check Instance Editable when the reference is assigned per placed instance in the Level Editor, so the variable appears in the Details panel and you can pick the level instance.
- Guard the reference with Is Valid before calling through it, and route the not-valid branch to a safe no-op.
- Use the reference as the Target input of the function or property you want to call.

## Don't
- Don't hold a direct reference when the sender should not know who reacts, or when several things should react to the same event — that coupling belongs to an event dispatcher.
- Don't call through a reference that might still be None without an Is Valid guard.

## Checklist
- The reference variable is typed to the receiver's class (or a base class it inherits from).
- The reference is assigned (Instance Editable for level instances, or at runtime from a spawn or lookup).
- Every call through the reference is behind an Is Valid branch.
- The sender names the receiver's concrete type, and that coupling is intentional.

## Notes
A direct object reference is the tightest form of Blueprint communication: the sender knows the receiver's concrete type and calls its functions directly, using the reference as the Target of each call. It is the right tool for one-to-one communication where the sender needs to call specific functions or read specific state on a known receiver. The cost is coupling — the sender depends on the receiver's concrete type — so when the sender should not know who reacts, or several things should react to the same event, the direct reference is the wrong tool and an event dispatcher is the right one.
