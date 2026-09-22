---
object_id: PAT_use_hardware_ray_traced_collision_when_depth_buffer_gpu_collision_breaks
object_type: pattern
name: Use Hardware Ray-Traced Collision When Depth-Buffer GPU Collision Breaks
library_path:
- software-engineering
- unreal-engine
- vfx
- niagara
stage_binding: 3 rough
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- niagara
- collision
- gpu
- ray_tracing
- vfx
cross_links: []
reference:
  source_title: Build Stunning Real-time VFX with Unreal Engine 5
  author: Hrishikesh Andurlekar
confidence: high
references: []
variants: []
---

# Use Hardware Ray-Traced Collision When Depth-Buffer GPU Collision Breaks

## Pattern Rule
**IF** GPU particles need accurate collision and depth-buffer collision produces occlusion-dependent failures or disappearing particle behavior
**THEN** use Niagara hardware ray-traced collision when the target hardware and project support it.

## Do
- Recognize that depth-buffer GPU collision is an approximation tied to what the view can see.
- Use hardware ray-traced collision when accurate off-screen or occluded collision is required.
- Verify the effect on the actual target hardware and rendering configuration.

## Don't
- Don't assume depth-buffer collision remains valid when the particle system is occluded.
- Don't choose hardware ray-traced collision without accounting for target support and cost.

## Checklist
- Particles continue colliding correctly in the cases that failed with depth-buffer collision.
- The selected target supports the ray-traced collision path.

## Notes
The source contrasts depth-buffer approximation with hardware ray-traced collision as a more accurate Niagara GPU collision option.
