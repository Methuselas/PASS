---
object_id: DRILL_wrap_a_niagara_effect_and_supporting_material_behind_synchronized_blueprint_controls
object_type: drill
name: Wrap a Niagara Effect and Supporting Material behind Synchronized Blueprint
  Controls
library_path:
- software-engineering
- unreal-engine
- vfx
- niagara
stage_binding: 4 final
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
target_skill: Wrap the logo-fire Niagara System and supporting plane material in one
  reusable Blueprint with synchronized public controls.
---

# Wrap a Niagara Effect and Supporting Material behind Synchronized Blueprint Controls

## Practice Task
Wrap the logo-fire Niagara System and supporting plane material in one reusable Blueprint with synchronized public controls.

## Target Skill
Wrap the logo-fire Niagara System and supporting plane material in one reusable Blueprint with synchronized public controls.

## Setup
Duplicate the completed logo-fire Niagara System and supporting material/Blueprint assets so the wrapper can be rebuilt and tested without changing the source example.

## Instructions
1. Create an Actor Blueprint with Niagara and Plane components.
2. Parameterize the plane material and create a Dynamic Material Instance.
3. Expose public density, texture, and color variables.
4. Drive both User.Texture and the material texture from the same texture variable.
5. Drive both User.FireColor and the material color from the same color variable.
6. Organize the controls and test them from a placed actor.

## Success Check
One public texture updates both mask and plane, one public color updates both fire and logo, and density changes particle count without opening internal editors.

## Common Failures
- Exposing duplicate public controls for coupled visual values.
- Setting parameters on the shared base material instead of the dynamic instance.

## Notes
Grade this drill from the placed Actor: the same public texture and color controls must update both Niagara and the plane material, while density changes only the particle system.
