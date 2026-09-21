---
object_id: PAT_organize_character_animation_into_states_with_a_state_machine
object_type: pattern
name: Organize Character Animation into States with a State Machine
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
- state_machine
- anim_graph
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Organize Character Animation into States with a State Machine

## Pattern Rule
**IF** a character has several distinct animation modes (idle, moving, crouching, prone) that it switches between
**THEN** organize them as states in a State Machine in the AnimGraph, with a transition arrow between each pair of states that may change, and give each state its own graph that ends in an Output Animation Pose node.

## Do
- Add a State Machine to the AnimGraph (right-click, Add New State Machine) and connect it to the Output Pose node.
- Add one state per animation mode and connect a transition arrow between each pair of states that may change; the arrow marks that a transition is possible.
- Edit each state by double-clicking it, drop the animation asset that plays in that state into the state's graph, and connect it to the state's Output Animation Pose node.
- Put a Blend Space in a state that must vary continuously (for example, the moving state blends idle, walk, and run by speed).
- Define a Transition Rule on each transition arrow to control when the transition happens.

## Don't
- Don't wire every animation directly to the Output Pose node and branch between them by hand — the State Machine is the structure that keeps the modes and their transitions organized.
- Don't leave a transition arrow without a Transition Rule — the transition will not be controlled.
- Don't put the state's animation outside the state's own graph; each state owns the pose it outputs.

## Checklist
- The AnimGraph contains a State Machine connected to the Output Pose node.
- Each animation mode is a state with its own graph ending in an Output Animation Pose node.
- Every possible mode change has a transition arrow with a Transition Rule.

## Notes
The State Machine is the structure that replaces wiring every animation directly to the Output Pose node and branching between them by hand. Each state is its own graph: you double-click the state node to edit it, drop the animation asset that plays in that state, and connect it to the state's Output Animation Pose node. The State Machine node itself connects to the AnimGraph's Output Pose node, so the active state's pose is what the Skeletal Mesh receives. Transitions are the arrows between states; each arrow carries a Transition Rule that decides when the change happens. This is how a character's locomotion (idle, jog, run, crouch, jump) and added modes (prone) stay organized as the character's state changes.
