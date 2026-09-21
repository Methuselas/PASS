---
object_id: PAT_choose_a_trace_function_by_what_you_need_to_detect
object_type: pattern
name: Choose a Trace Function by What You Need to Detect
library_path:
- software-engineering
- unreal-engine
- blueprints
- traces
stage_binding: 0 design
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- blueprints
- traces
- collision
cross_links:
- rel: related_to
  target_object_id: PAT_choose_a_collision_preset_that_overlaps_the_actors_you_detect
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Choose a Trace Function by What You Need to Detect

## Pattern Rule
**IF** you need to test for collisions along a line or a volume
**THEN** choose the trace function by three axes: line vs. shape (line is cheaper), single vs. multiple hits (single is cheaper), and by channel (Visibility, Camera) vs. by object type (WorldStatic, WorldDynamic, Pawn, and the rest).

## Do
- Use a line trace when a straight-line test is enough; it is the cheapest trace.
- Use a shape trace (sphere, capsule, box) when you need to test a volume, accepting that it is more expensive than a line trace.
- Use a single-hit trace (LineTrace…) when you only need the first actor hit; use a multi-hit trace (MultiLineTrace…) only when you need every actor hit, which is more expensive.
- Trace by channel (Visibility or Camera) or by object type (WorldStatic, WorldDynamic, Pawn, PhysicsBody, Vehicle, Destructible, Projectile) depending on what you are trying to detect.

## Don't
- Don't reach for a shape trace when a line trace answers the question; the volume test costs more.
- Don't use a multi-hit trace when you only need the first hit; it returns an array of every hit and is more expensive.
- Don't pick the selection method (channel vs. object type) arbitrarily; match it to the actors you intend to hit.

## Checklist
- The trace shape matches the test (line vs. sphere/capsule/box).
- The hit count matches the need (single first hit vs. all hits).
- The selection method matches the target (channel vs. object type).

## Notes
Traces test whether anything collides along a defined line segment or volume. Line traces are cheaper than shape traces (sphere, capsule, box). A single-hit trace returns the first actor hit; a multi-hit trace returns an array of every actor hit and is more expensive. You can select targets by trace channel (Visibility, Camera) or by object type (WorldStatic, WorldDynamic, Pawn, PhysicsBody, Vehicle, Destructible, Projectile). Choose the combination that matches what you need to detect, and pay the extra cost only when the cheaper option cannot answer the question.
