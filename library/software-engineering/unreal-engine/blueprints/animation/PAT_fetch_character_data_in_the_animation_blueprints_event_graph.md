---
object_id: PAT_fetch_character_data_in_the_animation_blueprints_event_graph
object_type: pattern
name: Fetch Character Data in the Animation Blueprint's EventGraph
library_path:
- software-engineering
- unreal-engine
- blueprints
- animation
stage_binding: 1 skeleton
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- blueprints
- animation
- animation_blueprint
- event_graph
- anim_graph
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Fetch Character Data in the Animation Blueprint's EventGraph

## Pattern Rule
**IF** an Animation Blueprint needs character data (velocity, input state, component values) to drive its animation
**THEN** fetch that data in the EventGraph on Event Blueprint Update Animation and store it in Animation Blueprint variables, because the AnimGraph can only read Animation Blueprint variables — and end the AnimGraph in the Output Pose node.

## Do
- Wire the character to the Animation Blueprint: on the Mesh component, set Animation Mode to Use Animation Blueprint and set Anim Class to the Animation Blueprint.
- Run the fetch on Event Blueprint Update Animation, which executes every frame, so the variables track the character continuously.
- Get the character with Try Get Pawn Owner and guard the result with an Is Valid check before reading any data from it.
- Derive the value you need from the character (for example, Get Velocity then VectorLength for a scalar speed) and write it to an Animation Blueprint variable.
- Use Event Blueprint Initialize Animation for one-time setup instead of repeating it every frame.
- Connect the final animation node to the Output Pose node, which receives the resulting pose of each frame to apply to the Skeletal Mesh.

## Don't
- Don't read character data directly in the AnimGraph — it has no access to the character, only to Animation Blueprint variables.
- Don't skip the Is Valid guard on Try Get Pawn Owner; the owner reference can be invalid and reading from it is unsafe.
- Don't leave the AnimGraph without an Output Pose node — it is the node that delivers the pose to the Skeletal Mesh.

## Checklist
- The character data is fetched in the EventGraph and stored in Animation Blueprint variables.
- The fetch runs on Event Blueprint Update Animation, every frame.
- The AnimGraph reads only Animation Blueprint variables and ends in the Output Pose node.

## Notes
An Animation Blueprint is a specialized Blueprint with two graphs that work together: the EventGraph, which is like the Blueprint Editor's EventGraph but with animation-specific nodes, and the AnimGraph, which plays Animation Sequences and Blend Spaces and organizes them into State Machines. The division of labor is the point: the EventGraph reaches the character and updates the Animation Blueprint's variables, and the AnimGraph consumes those variables to choose the pose. This keeps the animation logic (AnimGraph) separate from the game logic (EventGraph), which is a core advantage of Animation Blueprints. Dragging an animation asset from the Asset Browser into the AnimGraph creates the equivalent Play node, and a Blend Space dropped in creates a Blendspace Player node whose parameter you wire to the variable you fetched.
