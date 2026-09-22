---
object_id: PAT_enable_persistent_ids_when_niagara_logic_depends_on_particle_identity
object_type: pattern
name: Enable Persistent IDs When Niagara Logic Depends on Particle Identity
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

# Enable Persistent IDs When Niagara Logic Depends on Particle Identity

## Pattern Rule
**IF** Niagara logic or a Niagara feature requires stable particle identity across simulation updates
**THEN** enable Requires Persistent IDs on the emitter.

## Do
- Enable persistent IDs before reading PARTICLES.ID for identity-based logic.
- Enable them for Niagara features, such as Events, that require stable particle tracking.

## Don't
- Do not assume transient particle ordering is a stable identity.

## Checklist
- The identity-dependent logic or feature functions consistently across updates.

## Notes
Persistent IDs are required for explicit particle-ID logic and for Niagara features such as Events that depend on stable particle tracking.
