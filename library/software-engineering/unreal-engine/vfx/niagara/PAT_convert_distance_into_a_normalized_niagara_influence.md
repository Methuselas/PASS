---
object_id: PAT_convert_distance_into_a_normalized_niagara_influence
object_type: pattern
name: Convert Distance into a Normalized Niagara Influence
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

# Convert Distance into a Normalized Niagara Influence

## Pattern Rule
**IF** a Niagara effect should vary smoothly with proximity
**THEN** measure distance, bound the active range, and remap it into a normalized control value.

## Do
- Compute the distance from a consistent-space position delta.
- Clamp or otherwise bound the range of influence.
- Remap the active interval to a normalized value and reuse that signal for related attributes.

## Don't
- Do not independently hand-tune several attributes when they should respond to the same proximity signal.

## Checklist
- The normalized influence is 0..1 over the intended range.

## Notes
The Presence Detector uses one proximity signal to drive size and color.
