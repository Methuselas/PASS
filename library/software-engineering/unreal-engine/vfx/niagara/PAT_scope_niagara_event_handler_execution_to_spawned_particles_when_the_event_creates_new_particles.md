---
object_id: PAT_scope_niagara_event_handler_execution_to_spawned_particles_when_the_event_creates_new_particles
object_type: pattern
name: Scope Niagara Event Handler Execution to Spawned Particles When the Event Creates
  New Particles
library_path:
- software-engineering
- unreal-engine
- vfx
- niagara
stage_binding: 2 block
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

# Scope Niagara Event Handler Execution to Spawned Particles When the Event Creates New Particles

## Pattern Rule
**IF** an Event Handler exists to spawn secondary particles in response to each event
**THEN** use the Spawned Particles execution mode so the handler script affects the particles created for that event.

## Do
- Set the Event Handler execution mode to Spawned Particles for secondary-spawn behavior.
- Verify only the event-created particles receive the handler-stage work.

## Don't
- Do not apply the event script to unrelated receiver particles when only new event particles should be affected.

## Checklist
- Secondary particles are created and processed per event as intended.

## Notes
Execution Mode controls the event-handler processing scope.
