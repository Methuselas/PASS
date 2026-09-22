---
object_id: DRILL_build_a_texture_masked_subuv_logo_fire_effect
object_type: drill
name: Build a Texture-Masked SubUV Logo Fire Effect
library_path:
- software-engineering
- unreal-engine
- vfx
- niagara
stage_binding: 3 rough
lane_fit: teach
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
target_skill: Build the Niagara portion of the logo-fire effect using mesh sampling,
  UV-aligned texture masking, GPU simulation, SubUV flames, and exposed controls.
---

# Build a Texture-Masked SubUV Logo Fire Effect

## Practice Task
Build the Niagara portion of the logo-fire effect using mesh sampling, UV-aligned texture masking, GPU simulation, SubUV flames, and exposed controls.

## Target Skill
Build the Niagara portion of the logo-fire effect using mesh sampling, UV-aligned texture masking, GPU simulation, SubUV flames, and exposed controls.

## Setup
Use a disposable test project or duplicate Niagara assets so the exercise can be repeated without damaging production content.

## Instructions
1. Sample a plane/static mesh and use Static Mesh Location for spawn positions.
2. Add Sample Texture, switch to GPUComputeSim, and configure fixed bounds.
3. Feed sampled mesh UVs into Sample Texture.
4. Build a conditional particle-kill mask from sampled color.
5. Assign a SubUV flame material and configure grid/frame animation.
6. Expose texture, density, and color as User parameters.

## Success Check
Particles form the texture silhouette, animate through the flame sheet, and respond to all exposed User parameters.

## Common Failures
- Sampling texture on CPU despite the module error.
- Using unrelated UVs that do not match the mesh mapping.

## Notes
Treat the particle silhouette, animated SubUV frames, and response of the exposed texture/density/color controls as the grading evidence for this exercise.
