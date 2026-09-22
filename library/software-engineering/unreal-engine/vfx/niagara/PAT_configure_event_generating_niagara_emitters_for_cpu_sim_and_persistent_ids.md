---
object_id: PAT_configure_event_generating_niagara_emitters_for_cpu_sim_and_persistent_ids
object_type: pattern
name: Configure Event-Generating Niagara Emitters for CPU Sim and Persistent IDs
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

# Configure Event-Generating Niagara Emitters for CPU Sim and Persistent IDs

## Pattern Rule
**IF** a Niagara emitter uses Niagara event-dispatcher events that require stable particle tracking
**THEN** set the emitter to CPU simulation and enable persistent IDs as required by the event system.

## Do
- Set Sim Target to CPUSim for this Event workflow.
- Enable Requires Persistent IDs.

## Don't
- Do not debug event-handler wiring before satisfying the sender's simulation prerequisites.

## Checklist
- The sender can generate events that the receiver sees.

## Notes
CPU simulation and persistent IDs are prerequisites for this Niagara Event workflow.
