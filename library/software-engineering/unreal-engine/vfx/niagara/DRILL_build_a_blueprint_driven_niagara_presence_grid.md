---
object_id: DRILL_build_a_blueprint_driven_niagara_presence_grid
object_type: drill
name: Build a Blueprint-Driven Niagara Presence Grid
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
target_skill: Build the Presence Detector end to end so Blueprint player position drives a particle grid through a custom Niagara module.
---

# Build a Blueprint-Driven Niagara Presence Grid

## Practice Task
Build the Presence Detector end to end so Blueprint player position drives a particle grid through a custom Niagara module.

## Target Skill
Build the Presence Detector end to end so Blueprint player position drives a particle grid through a custom Niagara module.

## Setup
Use a disposable test project or duplicate Niagara assets so the exercise can be repeated without damaging production content.

## Instructions
1. Create the grid emitter and resolve its Grid Location dependency.
2. Create the custom proximity module and transform particle positions into world space.
3. Compute distance, clamp and remap it, and drive sprite size and color.
4. Expose USER.PlayerPosition and bind it to the module input.
5. Embed the System in an Actor Blueprint and update the User parameter from the player location.
6. Move the player and verify the affected particle region follows.

## Success Check
The proximity region tracks the player while nearby particles visibly change size and color.

## Common Failures
- Comparing local particle positions directly with a world-space player position.
- Updating a differently named or unbound User parameter.

## Notes
Use the visible moving influence region as evidence that the Blueprint-to-Niagara data path is correct.
