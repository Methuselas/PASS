---
object_id: PAT_encapsulate_reusable_behavior_and_state_in_an_actor_component
object_type: pattern
name: Encapsulate Reusable Behavior and State in an Actor Component
library_path:
- software-engineering
- unreal-engine
- blueprints
stage_binding: 1 skeleton
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- blueprints
- actor_component
- encapsulation
- reuse
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Encapsulate Reusable Behavior and State in an Actor Component

## Pattern Rule
**IF** a piece of behavior with its own state needs to be available to several Actors
**THEN** create an Actor Component — a Blueprint whose Parent class is Actor Component — that owns the state as variables and the behavior as functions, and add it to each Actor that needs it.

## Do
- Create a Blueprint with Actor Component as the Parent class; the Components tab is not shown, because you cannot add components inside another component.
- Declare the state as variables on the component (for example, CurrentLevel, CurrentXP, and an ExpLevel array holding the experience points needed for each level).
- Implement the behavior as functions on the component (for example, IncreaseExperience, which adds experience points and reports whether the Actor leveled up).
- Add the component to an Actor with the ADD button in the Components panel, and adjust its default values in the Details panel for that Actor.

## Don't
- Don't duplicate the behavior and state in every Actor that needs it — the component holds one copy that each Actor gets by adding it.
- Don't try to add components inside a component — the Components tab is hidden on a component Blueprint.
- Don't expect the component's state to be shared between Actors — each Actor that has the component carries its own instance of the state.

## Checklist
- The behavior and its state live in a Blueprint whose Parent class is Actor Component.
- An Actor gains the behavior by having the component added in the Components panel.
- The component's default values can be adjusted per Actor in the Details panel.

## Notes
Components are the unit of reusable behavior in an Actor. The engine ships ready-made components (Projectile Movement, Static Mesh, Collision) that you add and configure, and a custom Actor Component extends the same mechanism to behavior the engine does not provide. Because the component owns its state, each Actor that has it carries its own copy of that state, so a level-up manager added to one character does not share experience points with another. Example: a component stores CurrentLevel, CurrentXP, and an ExpLevel array, and exposes IncreaseExperience, which adds experience points and returns whether the Actor leveled up.
