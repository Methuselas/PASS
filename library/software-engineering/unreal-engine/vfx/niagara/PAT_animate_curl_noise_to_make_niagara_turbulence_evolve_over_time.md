---
object_id: PAT_animate_curl_noise_to_make_niagara_turbulence_evolve_over_time
object_type: pattern
name: Animate Curl Noise to Make Niagara Turbulence Evolve over Time
library_path:
- software-engineering
- unreal-engine
- vfx
- niagara
stage_binding: 3 rough
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- niagara
- vfx
cross_links: []
reference:
  source_title: Build Stunning Real-time VFX with Unreal Engine 5
  author: Hrishikesh Andurlekar
confidence: high
references: []
variants: []
---

# Animate Curl Noise to Make Niagara Turbulence Evolve over Time

## Pattern Rule
**IF** Curl Noise produces turbulence that appears fixed or locked in space
**THEN** pan the noise field so the force pattern itself changes over time.

## Do
- Use Curl Noise Force for turbulent motion.
- Enable Pan Noise Field and set a direction/speed appropriate to the effect.

## Don't
- Do not assume stronger static noise will create evolving turbulence.

## Checklist
- The turbulence pattern changes over time rather than appearing spatially frozen.

## Notes
A panned curl field changes the force field itself, not only particle motion through a fixed field.
