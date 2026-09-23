---
object_id: PAT_randomize_particle_color_with_chained_dynamic_inputs
object_type: pattern
name: Randomize Particle Color with Chained Dynamic Inputs
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
- variant_01
- style_style_agnostic
- ue_5_1_1_baseline
- dynamic_input
- color
- randomization
- particle_spawn
cross_links: []
confidence: high
references: []
variants: []
---

# Randomize Particle Color with Chained Dynamic Inputs

## Pattern Rule
**IF** each particle should choose a color once at spawn and keep that color for its lifetime, while the color itself is generated through nested Dynamic Inputs,  
**THEN** drive Initialize Particle > Color with chained **Random Range Linear Color** inputs.  
**ELSE** use the simpler Random Hue/Saturation/Value color mode when you only need broad hue variation.

## Do
**Target result.** Each particle receives a random spawn color. With the baseline chain, the available range spans red through green into blue rather than only interpolating between two endpoints.

**Chained Linear-Color Ranges setup.**
- Use an emitter with **Initialize Particle** in Particle Spawn.
- Temporarily disable any later **Scale Color** module if it would overwrite or obscure the spawn colors.

**Chained Linear-Color Ranges build.**
1. In **Initialize Particle**, locate **Color**.
2. Open the Dynamic Input menu for Color.
3. Choose **Random Range Linear Color**.
4. Set its **Minimum** color to red.
5. Set its **Maximum** color to green.
6. Open the Dynamic Input menu on that Maximum property.
7. Replace Maximum with another **Random Range Linear Color** Dynamic Input.
8. On the nested input, set Minimum to green and Maximum to blue.
9. Play the system. Each particle should select a random color when spawned and keep that color until it dies.

**Chained Linear-Color Ranges tuning.**
- Change the three endpoint colors to bias the palette toward a specific art direction.
- Add or remove nested color generators to change the complexity of the random range.
- Re-enable Scale Color only when you intentionally want lifetime tinting on top of the spawn color.

## Don't
- Don't place the random assignment in Particle Update if the intent is one stable color per particle; Update will allow the value to change during life.
- Don't leave a strong Scale Color treatment enabled while testing this recipe; it can make correct randomization appear broken.

## Checklist
- Two particles alive at the same time can have visibly different colors.
- A particle's chosen color remains stable over its own lifetime.
- The population contains colors beyond a simple red-to-green interpolation after the nested green-to-blue range is added.

## Notes
Recipe catalog metadata: family `vfx.color.random-at-spawn`; local variant 01 (`chained-linear-color` — Chained Linear-Color Ranges); visual style `style_agnostic`; implementation Unreal Engine Niagara; authored-against baseline 5.1.1; later engine versions remain unverified until tested.

- **Symptom:** particles all look white.  
  **Likely cause:** Color is still a local constant or the Dynamic Input was attached to the wrong property.  
  **Correction:** verify Initialize Particle > Color is driven by Random Range Linear Color.
- **Symptom:** colors appear to change after spawn.  
  **Likely cause:** a later color module is modifying them.  
  **Correction:** disable Scale Color while verifying the spawn assignment.

This variant is useful when the nesting itself is part of the desired control structure. It is more cumbersome than the dedicated HSV randomization mode but demonstrates how Dynamic Inputs can be chained recursively.
