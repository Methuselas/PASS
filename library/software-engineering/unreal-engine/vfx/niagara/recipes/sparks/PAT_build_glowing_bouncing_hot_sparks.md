---
object_id: PAT_build_glowing_bouncing_hot_sparks
object_type: pattern
name: Build Glowing Bouncing Hot Sparks
library_path:
- software-engineering
- unreal-engine
- vfx
- niagara
- recipes
- sparks
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
- family_spark
- variant_01
- style_realistic
- ue_5_1_1_baseline
- spark
- curl_noise
- collision
- light_renderer
- sprite
cross_links: []
confidence: high
references: []
variants: []
---

# Build Glowing Bouncing Hot Sparks

## Pattern Rule
**IF** you need dense, hot spark particles that tumble unpredictably, stretch along their travel direction, hit the ground, and illuminate nearby surfaces,  
**THEN** use a Fountain-based sprite emitter with animated Curl Noise, velocity-aligned non-uniform sprites, an emissive yellow-to-red color curve, Collision, and a Light Renderer.  
**ELSE** omit Collision for free-flying embers or omit the Light Renderer when the effect must be cheaper.

## Do
**Target result.** A dense field of elongated fiery sparks moves in turbulent directions, stays aligned to velocity, changes from yellow toward red, bounces from the floor, glows, and casts a small pool of light.

**Curl-Noise Lit Sprite Sparks setup.**
- Enable Niagara in the project.
- Create a Niagara emitter from the **Fountain** template and place it in a Niagara System.
- Use the default Sprite Renderer as the visual base.

**Curl-Noise Lit Sprite Sparks build.**
1. In **Particle Update**, disable **Gravity Force**.
2. Add **Curl Noise Force** and set:
   - Noise Strength: `10000.0`
   - Noise Frequency: `1.0`
   - Pan Noise Field: enabled
   - Pan Noise Field Y: `0.5`
3. In **Initialize Particle > Sprite Attributes**, change **Sprite Size Mode** from `Random Uniform` to `Random Non-Uniform`.
4. Set **Sprite Size Min** to `X=5.0, Y=10.0`.
5. Set **Sprite Size Max** to `X=5.0, Y=30.0`.
6. In **Sprite Renderer > Sprite Rendering**, change **Alignment** from `Unaligned` to `Velocity Aligned`.
7. In **Emitter Update > Spawn Rate**, set Spawn Rate to `2000` particles/second.
8. In **Particle Update > Scale Color**, change **Scale Mode** to `RGBA Linear Color Curve`.
9. Configure the color curve so particles begin yellow and move toward red over normalized age. Use an emissive Value/brightness around `500` on the bright color stop.
10. Add **Collision** in Particle Update. Its default settings are sufficient for the baseline effect.
11. Add a **Light Renderer** in addition to the Sprite Renderer.
12. Preview with a visible floor and verify that sparks bounce and cast light.

**Curl-Noise Lit Sprite Sparks tuning.**
- **Curl Noise Strength** controls how violently the spark paths bend.
- **Noise Frequency** changes the scale of the turbulent field.
- **Pan Noise Field** prevents the turbulence from looking frozen in space.
- **Sprite Size Y** controls perceived streak length; keep X much smaller for a spark shape.
- **Spawn Rate** controls density. `2000` is a dense baseline rather than a universal target.
- **Color Add** and **Radius Scale** in Light Renderer increase perceived light intensity/range.
- Color-curve stops determine whether the sparks read as yellow-hot, orange, red, or fading embers.

## Don't
- Don't leave Sprite Renderer Alignment unaligned after making the sprites non-uniform; they will be elongated in arbitrary directions instead of along movement.
- Don't leave the noise field static if the result looks like particles are following fixed invisible channels.
- Don't add a Light Renderer without profiling when particle counts become large.

## Checklist
- Sparks visibly change direction over time instead of following a frozen turbulence pattern.
- Sprite streaks point along particle travel direction.
- The emission reads as yellow-hot near birth and redder later in life.
- Particles bounce from the preview floor.
- The Light Renderer produces visible illumination around at least some particles.
- **Near-miss excluded:** elongated sprites that rotate independently of motion indicate the Sprite Renderer is not Velocity Aligned.

## Notes
Recipe catalog metadata: family `vfx.spark.hot-bounce`; local variant 01 (`curl-sprite-light` — Curl-Noise Lit Sprite Sparks); visual style `realistic`; implementation Unreal Engine Niagara; authored-against baseline 5.1.1; later engine versions remain unverified until tested. Style descriptors: hot, emissive, turbulent, bouncing.

- **Symptom:** particles appear to pass through or never reach the preview floor.  
  **Likely cause:** the emitter origin/floor relationship makes the collision difficult to observe.  
  **Correction:** enable Initialize Particle **Position Offset** and set Z to `50.0`.
- **Symptom:** the effect is turbulent but looks frozen or patterned.  
  **Likely cause:** Pan Noise Field is disabled.  
  **Correction:** enable it and use Y `0.5` as the baseline.
- **Symptom:** sparks glow but do not light nearby surfaces.  
  **Likely cause:** only Sprite Renderer is present.  
  **Correction:** add Light Renderer and tune Color Add/Radius Scale.

This recipe separates three jobs cleanly: motion comes from animated Curl Noise, spark shape comes from non-uniform velocity-aligned sprites, and environmental glow comes from a separate Light Renderer.
