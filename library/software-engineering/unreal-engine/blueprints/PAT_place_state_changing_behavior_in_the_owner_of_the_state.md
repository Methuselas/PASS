---
object_id: PAT_place_state_changing_behavior_in_the_owner_of_the_state
object_type: pattern
name: Place State-Changing Behavior in the Owner of the State
library_path:
- software-engineering
- unreal-engine
- blueprints
stage_binding: 0 design
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: PAT_single_source_of_truth_for_logic
tags:
- unreal_engine
- blueprints
- ownership
- single_source_of_truth
cross_links:
- rel: related_to
  target_object_id: PAT_route_damage_through_the_engine_damage_event
- rel: related_to
  target_object_id: PAT_use_a_direct_object_reference_to_call_functions_on_another_blueprint
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Place State-Changing Behavior in the Owner of the State

## Pattern Rule
**IF** a behavior changes the state of a Blueprint and several other Blueprints can trigger it
**THEN** implement the behavior once, in the Blueprint that owns the state, and have the other Blueprints trigger it through a custom event or function on the owner rather than duplicating the logic in each of them.

## Do
- Give the owner a named custom event or function for the behavior (for example, a `Death` custom event on the player Blueprint) and put the state-changing nodes under it.
- Have each triggering Blueprint (an enemy, a trap) call that event or function on the owner through a direct object reference — cast to the owner's type, then call.
- Send data between the Blueprints through the event's or function's input or output parameters.
- Make any change to the behavior in the one place that owns it.

## Don't
- Don't copy and paste the state-changing logic into every Blueprint that can trigger it — a later change means hunting down and editing every copy, and you will miss some.
- Don't let a triggering Blueprint write the owner's state directly when the owner should own the reaction.
- Don't scatter the definition of one behavior across several Blueprints.

## Checklist
- The behavior that changes a state is implemented in exactly one Blueprint: the one that owns the state.
- The other Blueprints trigger it through a custom event or function on the owner.
- Data flows through the event's or function's parameters.
- A change to the behavior is made in one place.

## Notes
A Blueprint must be responsible for its internal state and be as independent as possible. The failure mode is duplication: if every enemy that can kill the player carries its own copy of the death logic (spawn an explosion, destroy the actor), then changing how the player dies means editing every enemy. The fix is to give the player a `Death` custom event and reduce each enemy's `Event Hit` to casting to the player and triggering that event. This is the Blueprint form of keeping a single source of truth for logic: the owner of the state owns the behavior that changes it. The engine's damage pipeline (Apply Damage / Event AnyDamage) is the same principle applied to damage specifically.
