---
object_id: PAT_pulse_spawn_rate_with_a_waveform_dynamic_input
object_type: pattern
name: Pulse Spawn Rate with a Waveform Dynamic Input
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
- family_spawn_modulation
- variant_01
- style_style_agnostic
- ue_5_1_1_baseline
- dynamic_input
- waveform
- spawn_rate
- timing
cross_links: []
confidence: high
references: []
variants: []
---

# Pulse Spawn Rate with a Waveform Dynamic Input

## Pattern Rule
**IF** an emitter should breathe, pulse, surge, or periodically stop/start without Blueprint logic,  
**THEN** drive Spawn Rate with a Waveform Dynamic Input.  
**ELSE** keep a local numeric Spawn Rate when emission should remain constant.

## Do
**Target result.** The number of particles spawned rises and falls continuously according to a waveform, creating a visible pulse without external control logic.

**Sine Wave Spawn Pulse setup.**
- Start with any Niagara emitter that uses **Emitter Update > Spawn Rate**.
- A baseline Spawn Rate around `2000` makes the modulation easy to see in a dense spark-style emitter.

**Sine Wave Spawn Pulse build.**
1. Select **Spawn Rate** in Emitter Update.
2. Open the Dynamic Input menu on the SpawnRate value.
3. Choose **Waveform**.
4. Keep the default waveform as **Sine**.
5. Set **Global Amplitude Scale** to `500.0`.
6. Set the X value of **Amplitude Min/Max** to `-1.0`.
7. Play the system and observe SpawnRate rising and falling over time.
8. To exaggerate the effect for testing, temporarily raise Global Amplitude Scale as high as `5000.0`.
9. To return to a constant value, open the Dynamic Input menu and choose **Make > New Local Value**.

**Sine Wave Spawn Pulse tuning.**
- **Global Amplitude Scale** changes the strength of the pulse.
- Waveform type changes cadence: sine is smooth; other available waveforms can produce sharper or differently shaped modulation.
- Use a lower base rate for sparse pulses and a higher rate for dense bursts.

## Don't
- Don't treat a Waveform Dynamic Input as a separate emitter; it is a value generator plugged into a property.
- Don't assume an extreme amplitude is production-safe just because it makes the behavior easy to see in preview.

## Checklist
- Spawn density increases and decreases over time without Blueprint input.
- At the low part of the sine cycle, emission approaches or reaches a stop.
- Increasing Global Amplitude Scale makes the oscillation visibly stronger.

## Notes
Recipe catalog metadata: family `vfx.spawn-modulation.waveform`; local variant 01 (`sine-waveform` — Sine Wave Spawn Pulse); visual style `style_agnostic`; implementation Unreal Engine Niagara; authored-against baseline 5.1.1; later engine versions remain unverified until tested.

- **Symptom:** no visible difference after adding Waveform.  
  **Likely cause:** amplitude is too small relative to the emitter's normal spawn density.  
  **Correction:** set Global Amplitude Scale to `500`, then temporarily test at `5000`.
- **Symptom:** you need a fixed Spawn Rate again.  
  **Likely cause:** the property is still owned by the Dynamic Input.  
  **Correction:** choose **Make > New Local Value** on SpawnRate.

This is a general-purpose modulation pattern. It is visually style-agnostic and can drive far more than sparks whenever Niagara exposes a compatible numeric input.
