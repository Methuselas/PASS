---
object_id: PAT_build_a_firework_launch_streak
object_type: pattern
name: Build a Firework Launch Streak
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
- family_firework_launch
- variant_01
- style_stylized
- ue_5_1_1_baseline
- firework
- fountain
- launch
- sender
cross_links: []
confidence: high
references: []
variants: []
---

# Build a Firework Launch Streak

## Pattern Rule
**IF** a firework-style composite needs a sparse primary particle that launches and then hands off to a secondary burst,  
**THEN** use a Fountain emitter with a low Spawn Rate and short randomized lifetime.  
**ELSE** use a longer lifetime when the launch streak itself needs to remain visible longer.

## Do
**Target result.** A small number of short-lived Fountain particles launch upward and expire quickly enough to act as triggers for a secondary burst.

**Fountain Launch Particle setup.**
- Create a Niagara emitter from **Fountain**.
- Place it in a Niagara System.

**Fountain Launch Particle build.**
1. In **Initialize Particle**, set **Lifetime Mode** to `Random`.
2. Set Lifetime Min to `0.25` seconds.
3. Set Lifetime Max to `0.75` seconds.
4. In **Emitter Update > Spawn Rate**, set Spawn Rate to `5.0`.
5. If this emitter will generate Niagara Events, use CPUSim and enable Requires Persistent IDs before wiring those events.

**Fountain Launch Particle tuning.**
- Lifetime controls where/when a downstream death-triggered effect will occur.
- Spawn Rate controls launch frequency.
- Fountain velocity/spread can be tuned to make a tighter rocket ascent or a wider celebratory launch.

## Don't
- Don't set lifetime so short that particles die before the intended launch movement is visible.
- Don't raise Spawn Rate so high that individual firework launches become an unreadable continuous stream.

## Checklist
- Individual primary particles are easy to distinguish.
- Each particle lives between roughly 0.25 and 0.75 seconds.
- Spawn cadence is sparse at 5 particles/second relative to dense spark systems.

## Notes
Recipe catalog metadata: family `vfx.firework.launch`; local variant 01 (`fountain-short-life` — Fountain Launch Particle); visual style `stylized`; implementation Unreal Engine Niagara; authored-against baseline 5.1.1; later engine versions remain unverified until tested. Style descriptors: simple, arcade, prototype.

- **Symptom:** the launch reads as a continuous fountain rather than discrete firework starters.  
  **Likely cause:** Spawn Rate is too high or particle lifetime is too long.  
  **Correction:** return to Spawn Rate `5` and Lifetime `0.25..0.75`, then tune deliberately.

This recipe is deliberately minimal so it can be embedded into larger fireworks without forcing a particular burst appearance.
