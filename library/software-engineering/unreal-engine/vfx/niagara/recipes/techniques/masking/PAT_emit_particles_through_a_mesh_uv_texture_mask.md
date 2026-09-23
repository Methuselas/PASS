---
object_id: PAT_emit_particles_through_a_mesh_uv_texture_mask
object_type: pattern
name: Emit Particles through a Mesh-UV Texture Mask
library_path:
- software-engineering
- unreal-engine
- vfx
- niagara
- recipes
- techniques
- masking
stage_binding: 2 block
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- niagara
- vfx
- recipe
- family_mask_emission
- variant_01
- style_style_agnostic
- ue_5_1_1_baseline
- texture_mask
- gpu
- mesh_uv
- sample_texture
- kill_particles
cross_links: []
confidence: high
references: []
variants: []
---

# Emit Particles through a Mesh-UV Texture Mask

## Pattern Rule
**IF** particles should appear only in selected regions of a mesh defined by a black/white texture mask,  
**THEN** sample the mesh and its UVs on GPU, sample the texture with those UVs, and kill particles whose sampled channel equals black.  
**ELSE** use an unmasked mesh-location spawn when the whole surface should emit.

## Do
**Target result.** Particles populate only the white areas of a black/white texture mapped onto a mesh, allowing text, logos, symbols, or painted masks to define the emission shape.

**Mesh UV Texture Mask setup.**
- Create/import a simple static mesh with valid UVs. A plane is sufficient for a flat mask.
- Create/import a black/white mask texture. White is the kept/emitting area; black is removed.
- Create a Niagara emitter with Spawn Rate and sprite particles.

**Mesh UV Texture Mask build.**
1. Add **Sample Static Mesh** to Particle Spawn and assign the target mesh.
2. Add **Static Mesh Location** to Particle Spawn so particle positions are actually generated from the sampled mesh.
3. Set Spawn Rate to `1000` while setting up so the mask shape is easy to see.
4. Add **Sample Texture** to Particle Spawn.
5. Change **Sim Target** to **GPUComputeSim**; Sample Texture is not supported by this setup on CPU and texture sampling is intended for GPU here.
6. Set **Calculate Bounds Mode** to **Fixed**. Expand Fixed Bounds only if the effect is being culled incorrectly.
7. Assign the black/white mask texture to Sample Texture.
8. From the parameters produced by Sample Static Mesh, bind `Particles.SampleStaticMesh.MeshUV` into **Sample Texture > UV**.
9. Add **Kill Particles** to Particle Spawn.
10. On its Kill Particles Boolean, add the Dynamic Input **Set Bool by Float Comparison**.
11. On input A, add **Make Float from Linear Color**.
12. Set Make Float from Linear Color **Channel = R**.
13. Bind `Particles.SampleTexture.SampledColor` into its LinearColor input.
14. Set comparison type to **A Equal To B**.
15. Set B to `0.0`.
16. Verify that black texels now produce `true` for Kill Particles while white regions remain visible.
17. If the mask shape is hard to read, start with Uniform Sprite Size Min `1.0`, Max `4.0`, Lifetime Min `0.1`, Lifetime Max `0.2`, then tune.

**Mesh UV Texture Mask tuning.**
- Spawn Rate controls how quickly/densely the image fills in.
- Sprite Size and Lifetime control edge clarity and persistence.
- Use a different texture channel by changing Make Float from Linear Color's channel.
- Change the comparison rule/threshold when the mask is grayscale rather than pure black/white.
- Fixed Bounds must contain the entire visible effect or it can vanish under frustum culling.

## Don't
- Don't sample the texture with arbitrary UVs; bind the UVs produced by the sampled mesh.
- Don't leave the emitter on CPU simulation after adding Sample Texture for this implementation.
- Don't interpret missing particles as a texture failure before checking fixed bounds and kill comparison logic.

## Checklist
- Before Kill Particles, particles cover the sampled mesh surface.
- After mask logic, black regions contain no surviving particles and white regions remain populated.
- The emission silhouette matches the mask orientation on the mesh.
- Moving the camera does not unexpectedly cull the visible effect while it remains within Fixed Bounds.

## Notes
Recipe catalog metadata: family `vfx.emission.texture-mask`; local variant 01 (`mesh-uv-kill-black` — Mesh UV Texture Mask); visual style `style_agnostic`; implementation Unreal Engine Niagara; authored-against baseline 5.1.1; later engine versions remain unverified until tested.

- **Symptom:** Sample Texture reports simulation errors.  
  **Likely cause:** emitter is still CPUSim.  
  **Correction:** switch to GPUComputeSim.
- **Symptom:** GPU effect disappears unexpectedly.  
  **Likely cause:** Fixed Bounds do not contain the rendered particles.  
  **Correction:** enable Fixed bounds and enlarge them to cover the effect.
- **Symptom:** mask appears inverted.  
  **Likely cause:** kill comparison is removing the wrong side of the threshold.  
  **Correction:** for the baseline black/white mask, kill when sampled R equals `0.0`; invert only intentionally.

The core reusable idea is UV-consistent sampling: obtain position and UV from the same mesh sample, then use the sampled texture value to decide particle survival.
