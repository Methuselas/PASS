---
object_id: PAT_make_a_player_action_detectable_by_ai_with_a_pawn_noise_emitter
object_type: pattern
name: Make a Player Action Detectable by AI with a Pawn Noise Emitter
library_path:
- software-engineering
- unreal-engine
- blueprints
stage_binding: 1 skeleton
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- blueprints
- ai
- sensing
- noise
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: low
references: []
variants: []
---

# Make a Player Action Detectable by AI with a Pawn Noise Emitter

## Pattern Rule
**IF** you want an AI to be able to hear a specific player action (sprinting, firing)
**THEN** add a Pawn Noise Emitter component to the player's actor and call Make Noise on it at the moment the action occurs, with a loudness and the actor's location as the noise location — the noise is an event for the AI's sensors, not the sound the player hears.

## Do
- Add a Pawn Noise Emitter component to the actor that performs the action.
- Call Make Noise (PawnNoiseEmitter) in the action's graph at the moment the action happens (after the action's own state update).
- Set the Noise Location to the actor's location so the AI knows where the noise came from.
- Set a Loudness value for the noise; the sensing side decides how far it carries.

## Don't
- Don't expect the audible sound effect to be heard by the AI — the sound the player hears and the noise the AI senses are separate systems; only a Make Noise broadcast reaches the PawnSensing.
- Don't add the Make Noise call to the wrong action — the noise should fire exactly when the detectable action happens.
- Don't put the noise emitter on the AI; it belongs on the actor that makes the noise.

## Checklist
- A Pawn Noise Emitter component is on the actor that performs the action.
- The action's graph calls Make Noise with the actor's location as the noise location.
- The AI's sensing reacts to the action (the noise is detected), not to the audible sound.

## Notes
The noise is a message to the AI, not a sound to the ear. The player's gun has an audible sound effect, but that effect is invisible to the AI; the Make Noise call is what makes the shot detectable. Keeping the two separate — the audible sound and the sensed noise — is what lets you tune what the AI can hear independently of what the player hears, and it is why adding hearing to the AI requires a change on the player's side, not just the AI's.
