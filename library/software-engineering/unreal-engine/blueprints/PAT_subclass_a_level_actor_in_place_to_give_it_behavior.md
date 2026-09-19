---
object_id: PAT_subclass_a_level_actor_in_place_to_give_it_behavior
object_type: pattern
name: Subclass a Level Actor in Place to Give It Behavior
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
- blueprint_creation
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Subclass a Level Actor in Place to Give It Behavior

## Pattern Rule
**IF** an Actor is already placed in the Level and you want to give it scripted behavior
**THEN** create a Blueprint from the selection with the New Subclass method, so the level instance is replaced by a Blueprint instance that keeps the Actor's components and parent class.

## Do
- Select the placed Actor in the Level and open Create Blueprint From Selection from the icon beside the Add button in the Details panel.
- Choose New Subclass as the creation method so the new Blueprint inherits the Actor's parent class, which is preselected because it is the Actor's actual parent.
- Name the Blueprint and set its content path, then let the editor replace the selected instance with an instance of the new class.
- Open the Event Graph of the new Blueprint to add the behavior; the Static Mesh component and its mesh come over already assigned.

## Don't
- Don't build a brand-new Blueprint class from scratch and re-add the components when the Actor you want to script is already in the level — subclassing in place keeps the existing component setup.
- Don't expect the original placed instance to remain — New Subclass replaces it with an instance of the new Blueprint class.

## Checklist
- The level now contains an instance of the new Blueprint class where the original Actor was.
- The new Blueprint's Components panel shows the Actor's components (for example, the Static Mesh component with its mesh) already assigned.
- The parent class of the new Blueprint is the Actor's original parent class.

## Notes
Create Blueprint From Selection turns a placed Actor into a Blueprint class in one step. The New Subclass method inherits the Actor's parent class and carries its components into the new Blueprint, so you start from the Actor's existing setup rather than an empty class. The level instance is replaced by an instance of the new class, which is what lets you add behavior to an Actor that was already part of the level layout.
