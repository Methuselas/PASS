---
object_id: AP_build_a_death_event_firework
object_type: ap
name: Build a Death-Event Firework
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
- family_firework
- variant_01
- style_stylized
- ue_5_1_1_baseline
- firework
- death_event
- sender
- receiver
- composite
cross_links: []
confidence: high
references: []
variants: []
---

# Build a Death-Event Firework

## Objective
Build a complete two-stage firework in which sparse launch particles rise briefly and, when each launch particle dies, an omnidirectional secondary burst appears at that death position.

## Steps / Flow
**Final effect structure.**
- **Launch stage:** Fountain Sender, Spawn Rate `5`, randomized lifetime `0.25..0.75` seconds.
- **Trigger:** Generate Death Event on the Sender.
- **Burst stage:** Omnidirectional Burst Receiver.
- **Event integration:** Receiver Event Handler listens to Death Event and spawns `5` particles per event as a visible baseline.

**Entry state.**
- Enable Niagara.
- Create one Niagara System with two emitters named **Sender** and **Receiver** for clarity.
- Create Sender from **Fountain** and Receiver from **Omnidirectional Burst**.

1. **Build the launch stage.** On Sender Initialize Particle, set Lifetime Mode to Random, Min `0.25`, Max `0.75` seconds.
2. Set Sender Spawn Rate to `5.0`.
3. Set Sender **Sim Target = CPUSim**.
4. Enable **Requires Persistent IDs** on Sender.
5. Add **Generate Death Event** to Sender Particle Update.
6. **Build the burst stage.** Use the Omnidirectional Burst Receiver. Give its test particles a contrasting color such as red so Receiver particles are easy to distinguish from Sender particles.
7. Add an **Event Handler** stage to Receiver.
8. Set the handler's Source/Event to Sender **Death Event**.
9. Set Execution Mode to **Spawned Particles**.
10. Set **Spawn Number** to `5`.
11. Add **Receive Death Event** in the Event Handler.
12. Set Receiver life-cycle behavior so it remains active as part of the system and is ready when events arrive.
13. Play the system and verify that each short-lived launch particle produces a secondary burst where it dies.

**Integration rules.**
- Sender owns event generation; Receiver owns event consumption.
- Death timing is controlled by Sender lifetime, not Receiver lifetime.
- The Event Handler's Spawn Number is a multiplier at the handoff point; changing it does not change how many Sender particles launch.
- Keep the event workflow on CPU simulation for this implementation.

**Tuning.**
- Increase Sender upward velocity to make the launch more rocket-like.
- Increase/decrease Sender lifetime to move the burst point higher/lower.
- Adjust Spawn Rate to control firework cadence.
- Adjust Receiver color, lifetime, speed, size, and event Spawn Number to shape the explosion.

**Avoid.**
- Don't duplicate the Receiver as an independently timed burst and assume it is event-driven.
- Don't use GPU simulation for this baseline event architecture.
- Don't omit persistent IDs when the event workflow depends on them.

**Completion check.**
- White/primary Sender particles appear first.
- The secondary/Receiver burst begins only when a Sender particle dies.
- Bursts occur at the corresponding Sender death locations.
- Changing Sender lifetime changes burst timing/location.
- Changing Event Handler Spawn Number changes burst density without changing launch cadence.
- **Near-miss excluded:** a burst that always happens at system start rather than at Sender death is not correctly event-wired.

## Notes
Recipe catalog metadata: family `vfx.firework.death-burst`; local variant 01 (`fountain-death-burst` — Fountain-to-Radial Death Burst); visual style `stylized`; implementation Unreal Engine Niagara; authored-against baseline 5.1.1; later engine versions remain unverified until tested. Style descriptors: arcade, radial, event-driven.

- **Symptom:** launch particles work, but no secondary burst appears.  
  **Likely cause:** Generate Death Event, CPU simulation, persistent IDs, Event Handler source, or Receive Death Event is missing.  
  **Correction:** verify that entire chain in order.
- **Symptom:** Receiver particles spawn, but from the wrong place/time.  
  **Likely cause:** Receiver is also using an independent spawn path.  
  **Correction:** isolate/disable unrelated Receiver spawning while validating the Death Event path.

This composite is fully closed: the launch component, secondary burst, and Death Event integration are all defined here even though each mechanism can also be useful on its own.
