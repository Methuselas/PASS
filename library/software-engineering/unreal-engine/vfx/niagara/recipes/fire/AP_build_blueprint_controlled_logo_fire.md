---
object_id: AP_build_blueprint_controlled_logo_fire
object_type: ap
name: Build Blueprint-Controlled Logo Fire
library_path:
- software-engineering
- unreal-engine
- vfx
- niagara
- recipes
- fire
stage_binding: 3 rough
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
- family_fire
- variant_01
- style_stylized
- ue_5_1_1_baseline
- fire
- logo
- texture_mask
- subuv
- blueprint
- gpu
- composite
cross_links: []
confidence: high
references: []
variants: []
---

# Build Blueprint-Controlled Logo Fire

## Objective
Build an animated flame effect that emits only from the white areas of a black/white logo mask, then expose the logo texture, particle density, and fire color as editable Actor Blueprint controls.

## Steps / Flow
**Final effect structure.**
- **Mesh sampling:** particles originate from a flat mesh with valid UVs.
- **Masking:** a black/white texture is sampled with those UVs; black-region particles are killed.
- **Fire presentation:** surviving particles use a 6x6 animated flame SubUV and a bright warm color curve.
- **Runtime/editor control:** User parameters expose texture, density, and color through a Blueprint.
- **Optional backing plane:** a material displays the logo under the particles for readability.

**Entry state.**
- Enable Niagara and add Unreal **Starter Content** so a simple plane mesh and `M_Fire_SubUV` are available.
- Prepare a square black/white logo mask texture; white will emit, black will be removed. A 1024x1024 PNG is a practical baseline.
- Create a Niagara System with a Fountain-style emitter.

1. **Prepare upward flame motion.** Tune the Fountain so particles move upward like flame. Use Initialize Particle Lifetime Min `0.2` and Max `0.5` as the final flame baseline.
2. **Sample the mesh.** Add **Sample Static Mesh** to Particle Spawn and assign a plane mesh.
3. Add **Static Mesh Location** to Particle Spawn.
4. Temporarily set Spawn Rate to `1000` and verify particles cover the plane surface.
5. **Sample the mask.** Add **Sample Texture** to Particle Spawn and assign the logo mask.
6. Set the emitter **Sim Target = GPUComputeSim**.
7. Set **Calculate Bounds Mode = Fixed**. Expand Fixed Bounds only if culling requires it.
8. Bind `Particles.SampleStaticMesh.MeshUV` into **Sample Texture > UV**.
9. **Kill black-region particles.** Add **Kill Particles** to Particle Spawn.
10. Add **Set Bool by Float Comparison** to the Kill Particles Boolean.
11. On A, add **Make Float from Linear Color**, Channel `R`.
12. Bind `Particles.SampleTexture.SampledColor` into the LinearColor input.
13. Set Comparison Type to **A Equal To B** and B to `0.0`.
14. Verify particles survive only over white mask regions.
15. For mask-readability testing, use Uniform Sprite Size Min `1.0`, Max `4.0`, Lifetime Min `0.1`, Max `0.2` if needed.
16. **Convert the surviving particles to flame.** In Scale Color, choose **RGBA Linear Color Curve**. Use a bright warm starting color with HSV Value around `10.0`, then transition through warm colors and fade later in life.
17. Assign **M_Fire_SubUV** to Sprite Renderer.
18. Set Sprite Renderer Sub Image Size to `6 x 6`.
19. Add **Sub UVAnimation** to Particle Update; Start Frame `0`, End Frame `35`.
20. Set final flame Uniform Sprite Size Min `5.0`, Max `7.0`.
21. Set final flame Lifetime Min `0.2`, Max `0.5`.
22. Raise Spawn Rate to `20000` for the dense final baseline.
23. **Expose controls in Niagara.** Create:
    - `User.Texture` — Texture Sample
    - `User.FireDensity` — Float
    - `User.FireColor` — LinearColor
24. Bind `User.Texture` to Sample Texture's texture input.
25. Bind `User.FireDensity` to Spawn Rate.
26. Bind `User.FireColor` to the particle color input you want artists to control, while preserving lifetime Scale Color for the animated gradient if both are intended.
27. **Build the Actor Blueprint.** Create an Actor Blueprint and add a Niagara Particle System Component; assign this Niagara System.
28. Create public Blueprint variables for texture, density, and fire color.
29. In Construction Script, use matching typed **Set Niagara Variable** nodes to push each public variable into `User.Texture`, `User.FireDensity`, and `User.FireColor`.
30. **Optional backing logo plane.** Create a material with a Texture Sample parameter named `TextureUsed` and a Vector/Color parameter named `LogoColor`. Multiply TextureUsed by LogoColor and feed the result to both Base Color and Emissive Color.
31. A bright baseline LogoColor is `(R=5.0, G=2.5, B=0.0, A=1.0)`.
32. Add a Plane component to the Blueprint, assign that material, and offset the plane to approximately `(0,0,-3)` so it sits just behind the particles.
33. Compile, place the Blueprint, and change texture/density/color from the Details panel.

**Integration rules.**
- Mesh position sampling and mesh UV sampling must come from the same mesh so the mask aligns spatially.
- Sample Texture requires the GPU path in this implementation.
- Kill logic occurs at Particle Spawn so invalid mask regions never become visible particles.
- SubUV animation and lifetime color operate on the surviving masked particles.
- User controls must bind to Niagara properties before Blueprint setters can affect the effect.
- Keep Fixed Bounds large enough for all visible particles after the effect expands above the plane.

**Tuning.**
- **Mask texture** changes the emitted shape.
- **FireDensity** changes how completely the shape fills with flame.
- **FireColor** gives high-level palette control; the lifetime curve can still shift/fade that color.
- **Sprite size 5..7**, **lifetime 0.2..0.5**, and **Spawn Rate 20000** form the dense baseline but should be profiled/tuned for scale.
- Fixed Bounds may need to grow when flame rises farther from the plane.
- The optional backing plane can be dimmed or removed once the fire silhouette is readable by itself.

**Avoid.**
- Don't run Sample Texture on CPU in this implementation.
- Don't use a mask texture whose UV orientation does not match the sampled mesh.
- Don't forget Fixed Bounds on the GPU emitter.
- Don't expose Blueprint variables without first binding the Niagara User parameters to real module properties.
- Don't assume `36` is the correct End Frame for a 36-frame zero-indexed flipbook; use `35`.

**Completion check.**
- At Spawn Rate `1000`, particles clearly trace only the white mask regions.
- Black mask regions are empty because their particles are killed.
- With M_Fire_SubUV and SubUVAnimation active, surviving sprites animate as flame rather than displaying a static atlas.
- Final baseline sprites are approximately size `5..7`, lifetime `0.2..0.5`, Spawn Rate `20000`.
- Blueprint changes to texture, density, and color visibly update the Niagara effect.
- The optional backing plane displays the chosen logo and remains behind the fire.
- **Near-miss excluded:** a square cloud of fire with no recognizable mask means mesh UV -> texture sampling or kill logic is wrong even if the flame animation itself is correct.

## Notes
Recipe catalog metadata: family `vfx.fire.logo-mask`; local variant 01 (`texture-mask-subuv-controls` — Texture-Masked SubUV Logo Fire); visual style `stylized`; implementation Unreal Engine Niagara; authored-against baseline 5.1.1; later engine versions remain unverified until tested. Style descriptors: logo, emissive, animated, mask-shaped.

- **Symptom:** Sample Texture errors immediately.  
  **Likely cause:** emitter is CPUSim.  
  **Correction:** change Sim Target to GPUComputeSim.
- **Symptom:** mask is rotated/misaligned.  
  **Likely cause:** Sample Texture UV is not driven by the sampled mesh's MeshUV.  
  **Correction:** bind `Particles.SampleStaticMesh.MeshUV` directly into Sample Texture > UV.
- **Symptom:** fire shape vanishes when camera moves.  
  **Likely cause:** Fixed Bounds are too small.  
  **Correction:** enlarge the bounds to include the full flame volume.
- **Symptom:** Blueprint fields change but effect does not.  
  **Likely cause:** User parameters are not bound to the corresponding Niagara properties or setter types/names mismatch.  
  **Correction:** verify Niagara bindings, exact `User.` names, and typed Set Niagara Variable nodes.
- **Symptom:** sprites show an atlas instead of animation.  
  **Likely cause:** SubUV material/grid settings are wrong.  
  **Correction:** use M_Fire_SubUV, Sub Image Size `6 x 6`, Start `0`, End `35`.

This is a closed composite recipe. Mesh sampling, masking, flame rendering, User parameters, Blueprint controls, and the optional backing material are all specified here; no other recipe card is required.
