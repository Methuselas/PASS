---
object_id: PAT_keep_the_niagara_preview_realtime_while_tuning
object_type: pattern
name: Keep the Niagara Preview Realtime While Tuning
library_path:
- software-engineering
- unreal-engine
- vfx
- niagara
stage_binding: 2 block
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

# Keep the Niagara Preview Realtime While Tuning

## Pattern Rule
**IF** you are interactively tuning a Niagara emitter or system
**THEN** keep realtime preview enabled and use the preview camera controls to judge changes immediately.

## Do
- Keep Realtime on during ordinary effect tuning.
- Use Orbit Mode for stable inspection and press F to recover framing when the effect drifts out of view.

## Don't
- Do not tune blindly when the Preview panel can show the effect immediately.

## Checklist
- The preview updates as parameters change.

## Notes
For debugging transient problems, later debugger controls may intentionally pause or slow the simulation.
