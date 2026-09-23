---
object_id: PAT_randomize_particle_color_with_hsv_ranges
object_type: pattern
name: Randomize Particle Color with HSV Ranges
library_path:
- software-engineering
- unreal-engine
- vfx
- niagara
- recipes
- techniques
- dynamic-inputs
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
- family_color
- variant_02
- style_style_agnostic
- ue_5_1_1_baseline
- color
- randomization
- hsv
- particle_spawn
cross_links: []
confidence: high
references: []
variants: []
---

# Randomize Particle Color with HSV Ranges

## Pattern Rule
**IF** you need random particle colors at spawn and want direct artist control over hue, saturation, value, and alpha variation,  
**THEN** use Initialize Particle's **Random Hue/Saturation/Value** Color Mode.  
**ELSE** use chained Dynamic Inputs when the color generator must be composed from reusable sub-inputs.

## Do
**Target result.** Particles receive stable random colors at spawn, with the randomization range controlled directly in HSV space.

**HSV Randomization setup.**
- Use **Initialize Particle** in Particle Spawn.
- Use a non-white, non-black base color so hue changes are visible.
- Temporarily disable later color overrides while validating the effect.

**HSV Randomization build.**
1. In **Initialize Particle > Color**, locate **Color Mode**.
2. Change Color Mode to **Random Hue/Saturation/Value**.
3. Pick a visibly saturated base color.
4. For a narrow hue family, set **Hue Shift Range** to `X=-0.1, Y=0.1`.
5. For broad/full-spectrum randomization, set **Hue Shift Range** to `X=-0.5, Y=0.5`.
6. Use **Saturation Range**, **Value Range**, and **Alpha Scale Range** when you also want those properties randomized. Their normal ranges are `0..1`, although saturation/value can be overdriven for more intense results.

**HSV Randomization tuning.**
- Narrow hue shifts keep a coherent palette while avoiding identical particles.
- A `-0.5..0.5` hue shift spans the full hue circle.
- Lower saturation produces washed-out variation; higher saturation gives stronger color separation.
- Overdriven value can push particles toward an emissive appearance.

## Don't
- Don't test hue shifting with pure white or black; the hue variation may be visually invisible.
- Don't confuse the `0..1` normalized saturation/value/alpha ranges with the hue-shift range.

## Checklist
- With `-0.1..0.1`, particles remain near the chosen base hue.
- With `-0.5..0.5`, the live particle population spans the color spectrum.
- Individual particles keep their chosen spawn color unless another module intentionally changes it.

## Notes
Recipe catalog metadata: family `vfx.color.random-at-spawn`; local variant 02 (`hsv-range` — HSV Randomization); visual style `style_agnostic`; implementation Unreal Engine Niagara; authored-against baseline 5.1.1; later engine versions remain unverified until tested.

- **Symptom:** hue range changes do almost nothing.  
  **Likely cause:** base color is white/black or nearly unsaturated.  
  **Correction:** choose a saturated non-neutral base color.
- **Symptom:** random colors are correct at spawn but later become uniform.  
  **Likely cause:** a Particle Update color module is overriding them.  
  **Correction:** disable or intentionally blend that later module.

For ordinary random color variation this is usually the more direct artist-facing variant than chained Random Range Linear Color inputs.
