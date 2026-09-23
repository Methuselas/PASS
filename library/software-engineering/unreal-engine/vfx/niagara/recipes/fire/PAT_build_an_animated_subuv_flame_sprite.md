---
object_id: PAT_build_an_animated_subuv_flame_sprite
object_type: pattern
name: Build an Animated SubUV Flame Sprite
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
- subuv
- flipbook
- sprite_sheet
- scale_color
cross_links: []
confidence: high
references: []
variants: []
---

# Build an Animated SubUV Flame Sprite

## Pattern Rule
**IF** a sprite particle should read as animated fire rather than a static billboard,  
**THEN** use a flame flipbook material, configure matching SubUV dimensions, animate the frame index over lifetime, and use a warm emissive color curve.  
**ELSE** keep a static sprite when animation cost/asset complexity is not justified.

## Do
**Target result.** Dense short-lived particles animate through a flame flipbook and shift through a bright warm color curve, producing a stylized flame appearance.

**6x6 SubUV Flame setup.**
- Ensure **Starter Content** is available in the project. If it is absent, add it from Unreal's content-pack/Add feature workflow.
- Locate the engine-provided **M_Fire_SubUV** material. It uses a 36-frame flame animation arranged as a `6 x 6` sprite sheet.
- Start from a Fountain-style Niagara sprite emitter.

**6x6 SubUV Flame build.**
1. In **Particle Update > Scale Color**, set Scale Mode to **RGBA Linear Color Curve**.
2. Configure a warm flame gradient across normalized age. At the beginning of particle life, use a bright yellow/orange color with HSV Value around `10.0` to create glow; transition toward deeper orange/red and fade later in life.
3. In **Sprite Renderer > Material**, assign `M_Fire_SubUV`.
4. Under **Sprite Renderer > Sub UV**, set Sub Image Size X to `6.0` and Y to `6.0`.
5. Add **Sub UVAnimation** to Particle Update.
6. Use Start Frame `0` and End Frame `35` so all 36 frames are available.
7. In Initialize Particle, set **Uniform Sprite Size Min = 5.0** and **Max = 7.0**.
8. Set **Lifetime Min = 0.2** seconds and **Lifetime Max = 0.5** seconds.
9. Set Spawn Rate to `20000` for the dense baseline flame look.
10. Preview and verify that individual sprites visibly animate rather than showing a frozen atlas tile.

**6x6 SubUV Flame tuning.**
- Start/End Frame can select only part of a larger sheet.
- Sprite Size controls flame scale.
- Lifetime controls animation persistence and the perceived speed of particle turnover.
- Spawn Rate controls body/density of the flame; `20000` is intentionally dense.
- Color/alpha curve controls heat, glow, fade, and palette.

## Don't
- Don't set End Frame to `36` for a 36-frame zero-indexed sheet; the last valid frame is `35`.
- Don't set Sub Image Size to the number of total frames; it must match the row/column grid (`6 x 6`).
- Don't use the high Spawn Rate blindly on constrained platforms without profiling.

## Checklist
- The Sprite Renderer shows flame frames rather than the entire atlas at once.
- Animation traverses frames 0 through 35.
- Particles are short-lived (`0.2..0.5`) and sized around `5..7`.
- The flame reads bright/emissive near birth and changes over normalized age.
- **Near-miss excluded:** seeing a static 6x6 contact sheet on each sprite means the material/SubUV configuration is incorrect.

## Notes
Recipe catalog metadata: family `vfx.fire.subuv-flame`; local variant 01 (`6x6-flipbook` — 6x6 SubUV Flame); visual style `stylized`; implementation Unreal Engine Niagara; authored-against baseline 5.1.1; later engine versions remain unverified until tested. Style descriptors: animated, emissive, sprite, flipbook.

- **Symptom:** sprites display the whole sheet instead of one frame.  
  **Likely cause:** Sub Image Size is not `6 x 6` or the material is not SubUV-compatible.  
  **Correction:** assign M_Fire_SubUV and set both Sub Image dimensions to `6`.
- **Symptom:** flame is animated but sparse.  
  **Likely cause:** Spawn Rate is too low for the intended dense look.  
  **Correction:** test toward the `20000` baseline, then optimize downward.

This recipe uses engine-provided Starter Content so it remains reproducible without an external download. A custom flipbook can replace that material later while preserving the same Niagara setup.
