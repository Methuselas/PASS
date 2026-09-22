---
object_id: PAT_drive_time_varying_cascade_properties_with_the_curve_editor
object_type: pattern
name: Drive Time-Varying Cascade Properties with the Curve Editor
library_path:
- software-engineering
- unreal-engine
- vfx
- cascade
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- cascade
- curve_editor
- vfx
cross_links: []
reference:
  source_title: Build Stunning Real-time VFX with Unreal Engine 5
  author: Hrishikesh Andurlekar
confidence: high
references: []
variants: []
---

# Drive Time-Varying Cascade Properties with the Curve Editor

## Pattern Rule
**IF** a Cascade module property must change over particle or emitter lifetime
**THEN** use a curve-capable distribution for that property, add it to the Curve Editor, and shape its values over time there.

## Do
- Set the property to an appropriate curve distribution such as DistributionFloatConstantCurve when the source property supports it.
- Add the property to the Curve Editor from its module control.
- Edit the curve points to define the lifetime change and remove the curve when it is no longer needed.

## Don't
- Don't expect a constant distribution to expose editable lifetime variation in the Curve Editor.
- Don't leave a curve attached when the effect should use a fixed value.

## Checklist
- The property appears in the Curve Editor.
- Changing curve points changes the property over the intended lifetime interval.

## Notes
Cascade uses its own older Curve Editor interface; the transferable idea is that a time-varying module value is represented by a curve distribution and edited over lifetime.
