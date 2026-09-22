---
object_id: PAT_use_gpu_compute_and_fixed_bounds_for_niagara_texture_sampling
object_type: pattern
name: Use GPU Compute and Fixed Bounds for Niagara Texture Sampling
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

# Use GPU Compute and Fixed Bounds for Niagara Texture Sampling

## Pattern Rule
**IF** a Niagara emitter uses Sample Texture and the module reports the CPU-simulation limitation
**THEN** run the emitter on GPU compute and configure fixed bounds required by the GPU simulation.

## Do
- Switch the emitter Sim Target to GPUComputeSim when Sample Texture reports the CPU limitation.
- Set fixed bounds large enough to contain the effect.

## Don't
- Do not ignore simulation-target errors from Sample Texture.
- Do not leave GPU effects with missing/incorrect bounds.

## Checklist
- The Sample Texture error clears and particles remain visible within the expected region.

## Notes
GPU simulations do not receive the same dynamic per-frame bounds calculation as CPU simulation in this workflow.
