---
object_id: PAT_drive_niagara_color_over_particle_age_with_a_linear_color_curve
object_type: pattern
name: Drive Niagara Color over Particle Age with a Linear Color Curve
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

# Drive Niagara Color over Particle Age with a Linear Color Curve

## Pattern Rule
**IF** particle color or opacity should evolve throughout lifetime
**THEN** drive Scale Color with an RGBA Linear Color Curve indexed by particle normalized age.

## Do
- Use PARTICLES.NormalizedAge as the curve index.
- Author color and alpha stops that express the birth-to-death transition.

## Don't
- Do not use one fixed spawn color when the visual intent is a lifetime transition.

## Checklist
- Color/alpha change predictably from age 0 to age 1.

## Notes
This is the Niagara lifetime-gradient workflow used by the spark and fire examples.
