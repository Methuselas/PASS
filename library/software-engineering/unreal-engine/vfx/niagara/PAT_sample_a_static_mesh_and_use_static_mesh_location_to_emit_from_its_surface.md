---
object_id: PAT_sample_a_static_mesh_and_use_static_mesh_location_to_emit_from_its_surface
object_type: pattern
name: Sample a Static Mesh and Use Static Mesh Location to Emit from Its Surface
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

# Sample a Static Mesh and Use Static Mesh Location to Emit from Its Surface

## Pattern Rule
**IF** particles should originate across an arbitrary static-mesh surface
**THEN** sample the mesh data and use Static Mesh Location to turn that sampled geometry into particle spawn positions.

## Do
- Add Sample Static Mesh for mesh data access.
- Add Static Mesh Location in Particle Spawn to place particles on the sampled surface.

## Don't
- Do not assume sampling a mesh by itself changes particle spawn locations.

## Checklist
- Particles visibly originate from the intended mesh surface.

## Notes
Sampling mesh data and sampling spawn location are separate responsibilities; both are required when particles should originate from the mesh surface.
