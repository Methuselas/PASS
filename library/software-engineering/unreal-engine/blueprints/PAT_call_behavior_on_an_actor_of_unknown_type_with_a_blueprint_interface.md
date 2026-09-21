---
object_id: PAT_call_behavior_on_an_actor_of_unknown_type_with_a_blueprint_interface
object_type: pattern
name: Call Behavior on an Actor of Unknown Type with a Blueprint Interface
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
- interface
- communication
- decoupling
cross_links:
- rel: related_to
  target_object_id: PAT_use_an_event_dispatcher_to_notify_listeners_without_naming_them
- rel: related_to
  target_object_id: PAT_use_a_direct_object_reference_to_call_functions_on_another_blueprint
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Call Behavior on an Actor of Unknown Type with a Blueprint Interface

## Pattern Rule
**IF** you need to call behavior on an actor whose concrete type you do not know, or that may vary
**THEN** define a Blueprint Interface with the function names and parameters, have the actor implement the interface, and call the interface function on the actor reference.

## Do
- Create a Blueprint Interface (content browser → Add → Blueprints → Blueprint Interface) that contains only function names and parameters.
- Add the interface to the actor's class (Class Settings → Details → Interfaces → Add).
- Implement each interface function in the actor. A function with no output parameters is implemented as an event.
- Call the interface function on the actor reference (for example, the actor owner of a component you are holding).

## Don't
- Don't call a concrete-type function on an actor reference when the type may vary — the caller would have to know the concrete type and branch on it.
- Don't expect anything to happen if the actor does not implement the interface — the call is a no-op.

## Checklist
- The interface contains only function names and parameters, with no implementation.
- The actor lists the interface under Implemented Interfaces in its Class Settings.
- The caller invokes the interface function on an actor reference, not on a concrete-type reference.
- A no-output interface function is implemented as an event in the actor.

## Notes
A Blueprint Interface is a special type of Blueprint that holds only function names and parameters. It lets different types of Blueprints communicate without the caller knowing the concrete type: if the actor implements the interface, the function runs; if it does not, nothing happens. This is a third communication mode alongside the other two. An event dispatcher is push — the sender broadcasts without naming the listeners. A direct object reference is pull with a known concrete type — the caller names a specific class and calls its members. An interface is pull with a known contract but an unknown concrete type — the caller names only the interface and the actor decides whether it honors it. Example: a VR pawn calls Trigger Pressed on whatever actor a hand is holding; only actors that implement the interface (such as a pistol) respond by firing, while everything else is ignored.
