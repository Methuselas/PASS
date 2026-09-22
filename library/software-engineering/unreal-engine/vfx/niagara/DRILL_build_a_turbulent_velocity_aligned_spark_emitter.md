---
object_id: DRILL_build_a_turbulent_velocity_aligned_spark_emitter
object_type: drill
name: Build a Turbulent Velocity-Aligned Spark Emitter
library_path:
- software-engineering
- unreal-engine
- vfx
- niagara
stage_binding: 3 rough
lane_fit: teach
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
target_skill: Build and verify a FireSparks-style emitter by combining spawn shaping,
  evolving turbulence, velocity-aligned streaks, lifetime color, collision, and lighting.
---

# Build a Turbulent Velocity-Aligned Spark Emitter

## Practice Task
Build and verify a FireSparks-style emitter by combining spawn shaping, evolving turbulence, velocity-aligned streaks, lifetime color, collision, and lighting.

## Target Skill
Build and verify a FireSparks-style emitter by combining spawn shaping, evolving turbulence, velocity-aligned streaks, lifetime color, collision, and lighting.

## Setup
Use a disposable test project or duplicate Niagara assets so the exercise can be repeated without damaging production content.

## Instructions
1. Start from a Fountain emitter.
2. Change Shape Location to a wider emission primitive.
3. Replace gravity-driven motion with Curl Noise and animate the noise field.
4. Use non-uniform sprite size and Velocity Aligned rendering.
5. Increase spawn density until the target look is readable.
6. Drive color over normalized age.
7. Add collision and verify floor response.
8. Add a Light Renderer and verify secondary illumination.

## Success Check
The emitter produces turbulent, velocity-aligned spark streaks that change color over life, collide with the floor, and contribute light.

## Common Failures
- Checking only the final frame instead of verifying each stage.
- Elongating sprites without velocity alignment.

## Notes
Use visible behavior and the Niagara/Blueprint interfaces named in the task as evidence; do not grade by expected theory alone.
