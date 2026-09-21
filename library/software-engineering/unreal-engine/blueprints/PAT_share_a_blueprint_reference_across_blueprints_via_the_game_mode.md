---
object_id: PAT_share_a_blueprint_reference_across_blueprints_via_the_game_mode
object_type: pattern
name: Share a Blueprint Reference Across Blueprints via the Game Mode
library_path:
- software-engineering
- unreal-engine
- blueprints
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- blueprints
- game_mode
- communication
- service_locator
cross_links:
- rel: related_to
  target_object_id: PAT_put_game_rules_and_defaults_in_the_game_mode
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Share a Blueprint Reference Across Blueprints via the Game Mode

## Pattern Rule
**IF** several Blueprints need to reach the same key object (a controller or manager actor) and there is no other natural owner for the reference
**THEN** store the object's reference on the game mode (a singleton reachable from any Blueprint via Get Game Mode) so each Blueprint can retrieve it there.

## Do
- In the shared object's BeginPlay, get the game mode (Get Game Mode) and cast it to the game mode subclass.
- Set a variable on that subclass to the object's reference.
- In any other Blueprint, get the game mode, cast it to the subclass, and read the reference from the variable.
- Cast the game mode to the subclass before reading the variable — Get Game Mode returns the base GameModeBase, which does not expose the subclass's members.

## Don't
- Don't store the reference in a level Actor or the Level Blueprint — those are destroyed on a level change and are not reachable from every Blueprint.
- Don't read the reference through the base GameModeBase — the variable lives on the subclass, so the cast is required.

## Checklist
- The reference is stored on the game mode subclass.
- Another Blueprint retrieves it via Get Game Mode plus a Cast To the subclass.
- The reference is still available after a level change, because the game mode persists.

## Notes
The game mode is a singleton that persists across level changes and is reachable from any Blueprint via Get Game Mode. Storing a reference to a key object on the game mode turns it into a service locator: any Blueprint can retrieve the object without holding a direct reference to it. Get Game Mode returns the base GameModeBase, so cast to the subclass to reach the stored variable. This is a different use of the game mode from defining its rules and default classes — here the game mode is a shared home for a reference, not the owner of the game's rules.
