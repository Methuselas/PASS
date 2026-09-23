---
object_id: PAT_spawn_secondary_particles_from_a_collision_event
object_type: pattern
name: Spawn Secondary Particles from a Collision Event
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
- variant_02
- style_style_agnostic
- ue_5_1_1_baseline
- collision_event
- event_handler
- cpu_sim
- persistent_ids
cross_links: []
confidence: high
references: []
variants: []
---

# Spawn Secondary Particles from a Collision Event

## Pattern Rule
**IF** a secondary effect should occur where a primary particle collides,  
**THEN** give the Sender Collision, generate Collision Events, and receive those events in a Receiver Event Handler.  
**ELSE** use Death Events for expiration-triggered effects or Location Events for continuous trail emission.

## Do
**Target result.** Receiver particles spawn at Sender collision events, supporting splashes, welding sparks, impact puffs, and similar effects.

**Collision Event Secondary Spawn setup.**
- Create Sender and Receiver emitters in one Niagara System.
- Use CPU simulation for the event-producing workflow.
- Enable persistent IDs where required.

**Collision Event Secondary Spawn build.**
1. Add **Collision** to Sender Particle Update.
2. Add **Generate Collision Event** to Sender Particle Update.
3. Set Sender Sim Target to **CPUSim** and enable **Requires Persistent IDs**.
4. On Receiver, add an **Event Handler**.
5. Set the Event Handler source to **Collision Event** from Sender.
6. Add **Receive Collision Event** in that handler.
7. Configure Spawn Number to the amount of secondary particles wanted per collision.
8. Disable/remove old Death Event receive/generate paths if converting an existing event setup, so only the intended event drives the Receiver.

**Collision Event Secondary Spawn tuning.**
- Spawn Number controls impact/splash density.
- Sender collision properties control which contacts create events.
- Receiver velocity/lifetime controls whether the result reads as a splash, sparks, dust, fragments, or something else.

## Don't
- Don't add Generate Collision Event without the **Collision** module; it has an unmet dependency.
- Don't leave obsolete Death Event handlers enabled when converting the effect; multiple event paths can make debugging ambiguous.

## Checklist
- Receiver particles appear at collision locations rather than at Sender death locations.
- Removing/disabling Collision stops the event behavior or produces a dependency error.
- Changing Receiver Spawn Number changes secondary density per impact.

## Notes
Recipe catalog metadata: family `vfx.event.secondary-spawn`; local variant 02 (`collision-event` — Collision Event Secondary Spawn); visual style `style_agnostic`; implementation Unreal Engine Niagara; authored-against baseline 5.1.1; later engine versions remain unverified until tested.

- **Symptom:** Generate Collision Event shows an unmet dependency.  
  **Likely cause:** Collision is missing.  
  **Correction:** use Niagara's Fix Issue action or add Collision manually before the event generator.
- **Symptom:** secondary particles trigger at unexpected times.  
  **Likely cause:** an old Death Event or independent spawn path is still active.  
  **Correction:** disable competing event/spawn paths while validating Collision Event alone.

The event mechanism is visual-style agnostic; the Receiver determines whether the final effect is realistic or stylized.
