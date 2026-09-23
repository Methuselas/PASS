---
object_id: PAT_build_a_firework_secondary_burst
object_type: pattern
name: Build a Firework Secondary Burst
library_path:
- software-engineering
- unreal-engine
- vfx
- niagara
- recipes
- fireworks
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
- family_firework_burst
- variant_01
- style_stylized
- ue_5_1_1_baseline
- firework
- burst
- receiver
- omnidirectional
cross_links: []
confidence: high
references: []
variants: []
---

# Build a Firework Secondary Burst

## Pattern Rule
**IF** an event-triggered firework needs a radial secondary particle population,  
**THEN** use an **Omnidirectional Burst** emitter as the Receiver and let an Event Handler spawn it.  
**ELSE** choose a directional receiver when the secondary particles must preserve a preferred direction.

## Do
**Target result.** A radial burst of particles suitable for the secondary stage of a simple firework.

**Omnidirectional Burst Receiver setup.**
- Create a Niagara emitter from **Omnidirectional Burst**.
- Add it to the same Niagara System as the primary launch emitter when it will receive events.

**Omnidirectional Burst Receiver build.**
1. Create the emitter from **Omnidirectional Burst**.
2. Give the particles a clearly distinguishable color while testing; red is a useful baseline against a white Sender.
3. When integrating with an event-driven system, add the appropriate Event Handler to this emitter rather than relying on its ordinary one-shot timing alone.
4. Keep the Receiver alive as part of the parent system so it remains ready to process incoming events.

**Omnidirectional Burst Receiver tuning.**
- Change burst color, size, velocity, lifetime, and count to define the artistic look of the firework.
- Use event Spawn Number to multiply the number of Receiver particles created per source event.

## Don't
- Don't use color alone as proof that event wiring works; validate that the particles originate at the event location/time.
- Don't let the Receiver life cycle end before the Sender can trigger it.

## Checklist
- When spawned, particles move outward in multiple directions.
- When used as a Receiver, the burst originates at the triggering event rather than from an unrelated emitter start.

## Notes
Recipe catalog metadata: family `vfx.firework.burst`; local variant 01 (`omnidirectional-burst` — Omnidirectional Burst Receiver); visual style `stylized`; implementation Unreal Engine Niagara; authored-against baseline 5.1.1; later engine versions remain unverified until tested. Style descriptors: simple, radial, prototype.

- **Symptom:** burst exists but occurs independently of the launch particle.  
  **Likely cause:** Receiver is still using ordinary emitter timing instead of being driven by an Event Handler.  
  **Correction:** configure the desired event on the Receiver and verify its source emitter/event.

This is the visual burst component only. It is intentionally usable without any particular event type.
