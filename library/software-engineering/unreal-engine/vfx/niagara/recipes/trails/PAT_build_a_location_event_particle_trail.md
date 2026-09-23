---
object_id: PAT_build_a_location_event_particle_trail
object_type: pattern
name: Build a Location-Event Particle Trail
library_path:
- software-engineering
- unreal-engine
- vfx
- niagara
- recipes
- trails
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
- family_trail
- variant_01
- style_style_agnostic
- ue_5_1_1_baseline
- trail
- location_event
- event_handler
- missile
- rocket
cross_links: []
confidence: high
references: []
variants: []
---

# Build a Location-Event Particle Trail

## Pattern Rule
**IF** a moving Sender should continuously leave secondary particles along its path,  
**THEN** generate Location Events from the Sender and receive them in a secondary emitter.  
**ELSE** use a conventional trail/ribbon solution when event-driven secondary particles are unnecessary.

## Do
**Target result.** A Receiver emits particles along a moving Sender's positions, producing a trail suitable for missiles, rockets, moving energy points, or similar effects.

**Location Event Receiver Trail setup.**
- Create Sender and Receiver emitters in one Niagara System.
- Use the Niagara Event workflow on CPU simulation with persistent IDs.

**Location Event Receiver Trail build.**
1. On Sender Particle Update, add **Generate Location Event**.
2. Set Sender to **CPUSim** and enable **Requires Persistent IDs**.
3. On Receiver, add an **Event Handler**.
4. Set the handler source to Sender **Location Event**.
5. Add **Receive Location Event** to the handler.
6. Disable/remove unrelated Death/Collision event generators and receivers while validating this path.
7. Increase the number of Receiver particles spawned per event until the trail reads continuously enough for the target speed.
8. Give Receiver particles the lifetime, size, color, and material appropriate for smoke, sparks, energy, or another trail style.

**Location Event Receiver Trail tuning.**
- Receiver Spawn Number controls trail density.
- Receiver lifetime controls trail length/persistence.
- Sender speed determines how far apart event samples appear in world space.
- Receiver velocity can make the trail expand, drift, fall, or remain close to the path.

## Don't
- Don't assume a Spawn Number that works for a slow Sender will also look continuous on a very fast Sender.
- Don't leave other event types active while diagnosing a Location Event trail.

## Checklist
- Receiver particles appear behind/along the moving Sender instead of only at death or collision.
- Faster movement exposes whether event density is sufficient.
- Increasing Receiver spawn count makes the trail denser.
- Disabling Generate Location Event stops the event-driven trail.

## Notes
Recipe catalog metadata: family `vfx.trail.location-event`; local variant 01 (`location-event-receiver` — Location Event Receiver Trail); visual style `style_agnostic`; implementation Unreal Engine Niagara; authored-against baseline 5.1.1; later engine versions remain unverified until tested.

- **Symptom:** the trail has visible gaps.  
  **Likely cause:** too few Receiver particles are spawned relative to Sender speed.  
  **Correction:** increase event Spawn Number and/or Receiver lifetime.
- **Symptom:** particles appear only at impacts or death.  
  **Likely cause:** Receiver is still listening to Collision/Death Events.  
  **Correction:** set the Event Handler source to Location Event and disable competing handlers.

This recipe defines the event architecture, not a specific trail material. That makes it usable for realistic exhaust, stylized energy, sparks, smoke, or other secondary trail visuals.
