---
object_id: PAT_spawn_secondary_particles_from_a_death_event
object_type: pattern
name: Spawn Secondary Particles from a Death Event
library_path:
- software-engineering
- unreal-engine
- vfx
- niagara
- recipes
- techniques
- events
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
- family_event_spawn
- variant_01
- style_style_agnostic
- ue_5_1_1_baseline
- death_event
- event_handler
- cpu_sim
- persistent_ids
cross_links: []
confidence: high
references: []
variants: []
---

# Spawn Secondary Particles from a Death Event

## Pattern Rule
**IF** one particle population should create another population at the moment the first particles die,  
**THEN** generate Death Events on a CPU-simulated Sender and receive them through a Receiver Event Handler.  
**ELSE** use Collision Events for impact-triggered spawning or Location Events for continuous trail-style spawning.

## Do
**Target result.** Every qualifying Sender death can spawn a configurable number of Receiver particles at the event location.

**Death Event Secondary Spawn setup.**
- Create one **Sender** emitter and one **Receiver** emitter in the same Niagara System.
- Set the event-producing emitter to **CPUSim**.
- Enable **Requires Persistent IDs** where required by the event workflow.

**Death Event Secondary Spawn build.**
1. On the Sender, add **Generate Death Event** to Particle Update.
2. Confirm Sender **Sim Target = CPUSim**.
3. Enable **Requires Persistent IDs** on the Sender.
4. On the Receiver, add an **Event Handler** stage.
5. Set the Event Handler's Source/Event to the Sender's **Death Event**.
6. Set Event Handler **Execution Mode** to **Spawned Particles**.
7. Set **Spawn Number** to `5` as a visible baseline.
8. Add **Receive Death Event** inside the Receiver's Event Handler.
9. Set Receiver life-cycle behavior so it remains available as part of the system rather than ending independently before events arrive.

**Death Event Secondary Spawn tuning.**
- Spawn Number controls how many secondary particles each death creates.
- Sender lifetime controls event timing.
- Receiver appearance can be completely different from Sender appearance.

## Don't
- Don't use GPU simulation for this baseline Niagara Event workflow.
- Don't forget persistent IDs where the event path requires them.
- Don't confuse the Receiver's ordinary emitter spawn with event-driven spawning.

## Checklist
- Killing/expiring one Sender particle produces Receiver particles at that event.
- Changing Spawn Number changes the number of particles created per death.
- Disabling Generate Death Event stops the secondary spawn.

## Notes
Recipe catalog metadata: family `vfx.event.secondary-spawn`; local variant 01 (`death-event` — Death Event Secondary Spawn); visual style `style_agnostic`; implementation Unreal Engine Niagara; authored-against baseline 5.1.1; later engine versions remain unverified until tested.

- **Symptom:** the Event Handler receives nothing.  
  **Likely cause:** Sender is not CPUSim, persistent IDs/event generation are missing, or the handler points at the wrong event.  
  **Correction:** verify all four: CPU simulation, persistent IDs, Generate Death Event, and Death Event selected as the Receiver source.

This is an integration mechanism rather than an art-style recipe. It becomes fireworks, debris bursts, dissolves, secondary smoke, or other effects depending on what the Sender and Receiver render.
