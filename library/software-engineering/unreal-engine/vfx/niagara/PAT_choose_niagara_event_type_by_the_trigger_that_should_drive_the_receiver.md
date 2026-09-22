---
object_id: PAT_choose_niagara_event_type_by_the_trigger_that_should_drive_the_receiver
object_type: pattern
name: Choose Niagara Event Type by the Trigger That Should Drive the Receiver
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

# Choose Niagara Event Type by the Trigger That Should Drive the Receiver

## Pattern Rule
**IF** a receiver emitter should react to a specific sender-particle occurrence
**THEN** choose Death, Collision, or Location events according to the actual trigger semantics.

## Do
- Use Death when the sender particle ending should trigger the response.
- Use Collision when contact with geometry is the trigger.
- Use Location when the receiver should follow/respond along sender positions over time.

## Don't
- Do not treat event types as interchangeable visual presets.

## Checklist
- The chosen event corresponds to the occurrence that should drive the receiver.

## Notes
Typical mappings include fireworks on Death, impact secondary particles on Collision, and trails from Location events.
