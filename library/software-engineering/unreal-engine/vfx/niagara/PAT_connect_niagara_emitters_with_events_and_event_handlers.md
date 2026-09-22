---
object_id: PAT_connect_niagara_emitters_with_events_and_event_handlers
object_type: pattern
name: Connect Niagara Emitters with Events and Event Handlers
library_path:
- software-engineering
- unreal-engine
- vfx
- niagara
stage_binding: 1 skeleton
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- niagara
- vfx
cross_links: []
reference:
  source_title: Build Stunning Real-time VFX with Unreal Engine 5
  author: Hrishikesh Andurlekar
confidence: high
references: []
variants: []
---

# Connect Niagara Emitters with Events and Event Handlers

## Pattern Rule
**IF** one emitter should trigger behavior in another emitter inside the same Niagara System
**THEN** generate an event in the sender and consume it with an Event Handler stage in the receiver.

## Do
- Choose a sender emitter and add the matching Generate Event module.
- Add an Event Handler to the receiver and bind it to the sender event source.
- Add the corresponding Receive/Event response behavior.

## Don't
- Do not couple emitters by duplicating behavior when the dependency is event-driven.

## Checklist
- Receiver behavior occurs when the sender produces the event.

## Notes
Events create runtime emitter-to-emitter communication inside a System.
