---
object_id: PAT_set_trace_complex_for_precision_vs_performance
object_type: pattern
name: Set Trace Complex for Precision vs. Performance
library_path:
- software-engineering
- unreal-engine
- blueprints
- traces
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- blueprints
- traces
- performance
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Set Trace Complex for Precision vs. Performance

## Pattern Rule
**IF** you are running a trace and need to decide how precisely it should test collisions
**THEN** set Trace Complex to True to test against the actual mesh (precise but expensive) or False to test against the simplified collision shapes (fast but less precise), defaulting to False unless the result must be exact.

## Do
- Set Trace Complex to True when the trace result must match the actual mesh geometry.
- Leave Trace Complex False when the simplified collision shapes are good enough; it is the faster default.
- Revisit the setting if a trace misses or hits something it shouldn't — the collision shape may be too coarse.

## Don't
- Don't set Trace Complex to True by default; the complex mesh test is more expensive and usually unnecessary.
- Don't assume a False trace is exact; it tests simplified collision shapes, not the mesh.
- Don't use a complex trace to paper over a wrong start/end or a missing collision response.

## Checklist
- Trace Complex is set to match the precision the result needs.
- True tests the actual mesh; False tests simplified collision shapes.
- The cheaper False setting is the default unless exactness is required.

## Notes
The Trace Complex parameter controls what a trace tests against: True tests the actual mesh (precise, expensive), False tests the simplified collision shapes (fast, less precise). Default to False for performance and switch to True only when the trace result must be exact. If a trace behaves wrong, check the start/end locations and the actors' collision responses before reaching for the complex test.
