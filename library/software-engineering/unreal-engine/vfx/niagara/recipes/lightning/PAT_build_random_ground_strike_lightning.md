---
object_id: PAT_build_random_ground_strike_lightning
object_type: pattern
name: Build Random Ground-Strike Lightning
library_path:
- software-engineering
- unreal-engine
- vfx
- niagara
- recipes
- lightning
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
- family_lightning
- variant_01
- style_stylized
- ue_5_1_1_baseline
- lightning
- beam
- ribbon
- scratch_pad
- local_module
cross_links: []
confidence: high
references: []
variants: []
---

# Build Random Ground-Strike Lightning

## Pattern Rule
**IF** you need a rapidly changing lightning bolt that strikes random points inside a ground area and colors one end differently,  
**THEN** start from Dynamic Beam, randomize Beam Start, shorten lifetime, randomize beam width, add Jitter Position, and use a local module that colors particles according to Particle ID index.  
**ELSE** omit the index-color module when a single-color bolt is enough.

## Do
**Target result.** A jagged arcing lightning bolt repeatedly appears between a fixed point in the sky and random positions inside a rectangular ground area. The bolt is mostly emissive red, with the ground end emissive blue.

**Dynamic Beam Index-Colored Lightning setup.**
- Create a Niagara System from the **Dynamic Beam** template.
- Use its Ribbon Renderer and beam modules as the starting point.

**Dynamic Beam Index-Colored Lightning build.**
1. In **Beam Emitter Setup > Beam Start**, add **Random Range Vector**.
2. Set Beam Start Minimum to `(-200, -400, 0)`.
3. Set Beam Start Maximum to `(200, 400, 1)`.
4. Set **Beam End** to `(0, 0, 625)`.
5. Enable **Absolute Beam End** and **Use Beam Tangents**.
6. Change Beam Start Tangent from the owner X axis to a local value and set it to `(0.4, 0.5, 0.6)`.
7. Set Beam End Tangent to `(1.0, 1.0, -0.2)`.
8. In **Initialize Particle**, set Lifetime to `0.02` seconds so the bolt reshapes rapidly.
9. In **Beam Width**, replace Float from Curve with **Random Range Float**: Minimum `5`, Maximum `20`.
10. Set **Beam Twist Amount** to `90`.
11. In **Ribbon Renderer > Tessellation**, set **Curve Tension** to `0.5`.
12. Add **Jitter Position** in Particle Update and set Jitter Amount to `10`.
13. Disable the template **Color** module so it does not reduce the desired intensity.
14. Add a **New Scratch Pad/Local Module** to Particle Update and name it `ModifyColor`.
15. In the local module Map Get, read `Particles.ID`.
16. Break the Niagara ID and use its **Index** output.
17. Add **Greater Than**. Feed particle Index to A. Convert B to `int32` and set B to `10`.
18. Add **Select/If**. Feed Greater Than Result into Selector.
19. Convert the Select wildcard values to **Linear Color**.
20. Set the True color to red and the False color to blue. For both, use HSV Value around `500` to make them glow.
21. Add `Particles.Color` to Map Set and connect the Select color output to it.
22. In **Emitter Properties**, enable **Local Space**.
23. Enable **Requires Persistent IDs** so the particle-ID comparison remains valid.
24. Apply/compile the local module and preview the result.

**Dynamic Beam Index-Colored Lightning tuning.**
- Beam Start min/max defines the strike area.
- Beam End Z controls bolt height.
- Start/End Tangents change the arc.
- Lifetime controls how rapidly the bolt appears to reshape.
- Beam Width 5..20 controls thickness variation.
- The integer threshold `10` controls how much of the bolt receives the ground-end color.
- Swap red/blue for another stylized palette without changing the logic.

## Don't
- Don't leave **Requires Persistent IDs** off when using Particle ID index for the color split.
- Don't leave **Local Space** off if the system must move with its actor; otherwise the beam endpoint can remain tied to world space.
- Don't keep the template Color module enabled if it visibly fights the local color treatment.

## Checklist
- Each bolt starts at a different point inside the rectangular ground area.
- The beam is curved and jagged rather than a straight uniform ribbon.
- The bolt changes shape rapidly because of the `0.02` lifetime.
- Width varies within 5..20.
- Most of the bolt is red and the index region near the ground end is blue, both strongly emissive.
- Moving the Niagara actor keeps the beam behavior attached to the actor.

## Notes
Recipe catalog metadata: family `vfx.lightning.ground-strike`; local variant 01 (`dynamic-beam-index-color` — Dynamic Beam Index-Colored Lightning); visual style `stylized`; implementation Unreal Engine Niagara; authored-against baseline 5.1.1; later engine versions remain unverified until tested. Style descriptors: jagged, glowing, red-blue, arc.

- **Symptom:** the endpoint stays at/near world origin when the Niagara actor moves.  
  **Likely cause:** Local Space is disabled.  
  **Correction:** enable Local Space in Emitter Properties.
- **Symptom:** index-based coloring errors or behaves unpredictably.  
  **Likely cause:** Requires Persistent IDs is disabled.  
  **Correction:** enable it before relying on Particle ID.
- **Symptom:** the bolt is smooth rather than lightning-like.  
  **Likely cause:** Jitter Position is missing/too weak.  
  **Correction:** add it at Jitter Amount `10` as the baseline.

This implementation is intentionally stylized because its two-color red/blue treatment is part of the visual target. The beam construction itself can be reused for more realistic color treatment.
