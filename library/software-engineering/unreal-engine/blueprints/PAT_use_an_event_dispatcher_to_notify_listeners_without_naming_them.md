---
object_id: PAT_use_an_event_dispatcher_to_notify_listeners_without_naming_them
object_type: pattern
name: Use an Event Dispatcher to Notify Listeners Without Naming Them
library_path:
- software-engineering
- unreal-engine
- blueprints
stage_binding: 0 design
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: PAT_publish_changes_and_let_consumers_register
tags:
- unreal_engine
- blueprints
- communication
- events
- decoupling
cross_links:
- rel: related_to
  target_object_id: PAT_choose_level_blueprint_or_blueprint_class_by_reuse_scope
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Use an Event Dispatcher to Notify Listeners Without Naming Them

## Pattern Rule
**IF** several Blueprints or the Level Blueprint should react to an event, and the sender should not know who reacts
**THEN** declare an event dispatcher on the sender and let each interested Blueprint bind to it, because the dispatcher keeps the sender ignorant of its listeners.

## Do
- Create the event dispatcher in the sender's My Blueprint panel; give it input parameters for the data listeners need, such as a reference to the sender instance that raised the event.
- Call the dispatcher from the sender when the event happens, passing the parameters.
- Have each listener bind to the dispatcher: the Level Blueprint adds the dispatcher as an event in its Event Graph; another Blueprint class uses a Bind Event node to bind one of its own custom events to the dispatcher.
- Keep the sender ignorant of its listeners — it only knows it has a dispatcher to call.

## Don't
- Don't have the sender call its listeners directly or name them — that reintroduces the coupling the dispatcher removes.
- Don't broadcast one dispatcher to everything when listeners only need specific events — give each distinct event its own dispatcher.
- Don't forget that a listener must hold a reference to the sender (or the dispatcher's target) in order to bind to it.

## Checklist
- The sender calls a dispatcher and does not name any listener.
- Each listener binds to the dispatcher (a Level Blueprint event or a Bind Event node in another Blueprint).
- The dispatcher carries the parameters its listeners need.
- Adding a new listener touches only the new listener, not the sender.

## Notes
An event dispatcher inverts who holds the knowledge: the sender knows only that it has a dispatcher to call; it does not know what the listeners are, how many there are, or what they do with the event. The listener knows what it wants and binds to that, so adding a listener touches one file — the new one. The Level Blueprint is the simplest listener (it adds the dispatcher as an event), and Bind Event lets a Blueprint class listen to another Blueprint's dispatcher without the Level Blueprint in the middle. This is the Blueprint form of the general publish/subscribe pattern: the publisher stays ignorant of its consumers, and each consumer registers for the specific change it wants.
