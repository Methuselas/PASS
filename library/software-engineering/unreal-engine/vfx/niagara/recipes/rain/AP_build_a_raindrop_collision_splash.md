---
object_id: AP_build_a_raindrop_collision_splash
object_type: ap
name: Build a Raindrop Collision Splash
library_path:
- software-engineering
- unreal-engine
- vfx
- niagara
- recipes
- rain
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
- family_rain
- variant_01
- style_style_agnostic
- ue_5_1_1_baseline
- rain
- splash
- collision_event
- composite
cross_links: []
confidence: high
references: []
variants: []
---

# Build a Raindrop Collision Splash

## Objective
Build a two-stage particle behavior in which primary particles live long enough to reach the ground and each collision emits a secondary radial burst that can be art-directed into a splash.

## Steps / Flow
**Final effect structure.**
- **Drop stage:** Fountain-style Sender with lifetime `1.25..2.5` seconds and Collision.
- **Trigger:** Generate Collision Event.
- **Splash stage:** Omnidirectional Burst-style Receiver.
- **Integration:** Receiver Event Handler consumes the Collision Event.

**Entry state.**
- Create one Niagara System with a Sender and Receiver.
- Use CPU simulation for the event path and enable persistent IDs.
- Ensure there is collision geometry/floor for the primary particles to hit.

1. Create the Sender from a Fountain-style emitter.
2. In Sender Initialize Particle, set Lifetime Min to `1.25` and Lifetime Max to `2.5` seconds so particles have time to reach the floor.
3. Add **Collision** to Sender Particle Update.
4. Add **Generate Collision Event** after the collision behavior.
5. Set Sender to **CPUSim** and enable **Requires Persistent IDs**.
6. Create the Receiver from **Omnidirectional Burst**.
7. Add an Event Handler to Receiver.
8. Set the Event Handler source to Sender **Collision Event**.
9. Add **Receive Collision Event** inside that handler.
10. Tune Event Handler Spawn Number for the desired splash density.
11. Play the system above a collidable floor and verify the Receiver is emitted at each impact.
12. Art-direct Receiver size, velocity, lifetime, and color/material to move from a diagnostic burst toward the desired water splash look.

**Integration rules.**
- The Sender must survive long enough to physically reach the collider.
- Collision must exist before collision events can be generated.
- The Receiver should be driven by the Collision Event during validation; disable unrelated independent spawning.

**Tuning.**
- Sender lifetime changes whether drops reach the ground.
- Gravity/velocity determines drop speed and angle.
- Receiver Spawn Number controls splash density.
- Receiver outward/upward velocity controls crown-like versus flat splashes.
- Visual style is intentionally open: materials/renderers decide whether this becomes realistic water or a stylized splash.

**Avoid.**
- Don't shorten Sender lifetime until particles die in mid-air.
- Don't use a Death Event if the desired timing is physical impact.
- Don't judge splash quality from event wiring alone; event correctness and final water art direction are separate checks.

**Completion check.**
- Primary particles visibly reach and collide with the ground.
- Secondary particles originate at each collision point.
- Increasing Sender lifetime from a too-short value restores impacts when drops were dying early.
- Disabling Collision prevents the intended secondary splash.
- **Near-miss excluded:** secondary bursts at particle expiration rather than impact indicate Death Event wiring remains active.

## Notes
Recipe catalog metadata: family `vfx.rain.collision-splash`; local variant 01 (`collision-burst` — Particle Drop to Collision Burst); visual style `style_agnostic`; implementation Unreal Engine Niagara; authored-against baseline 5.1.1; later engine versions remain unverified until tested. Style descriptors: prototype, impact-driven.

- **Symptom:** drops disappear before impact.  
  **Likely cause:** lifetime is too short.  
  **Correction:** return to `1.25..2.5` seconds, then tune from there.
- **Symptom:** Generate Collision Event reports a missing dependency.  
  **Likely cause:** Collision is absent.  
  **Correction:** add Collision or use Fix Issue.
- **Symptom:** collisions happen but no splash spawns.  
  **Likely cause:** Receiver handler is not listening to Collision Event or Receive Collision Event is absent.  
  **Correction:** verify Receiver Event Handler source and receive module.

The interaction architecture is complete; the recipe intentionally leaves the final water shading/render style open so the same behavior can support realistic or stylized art direction.
