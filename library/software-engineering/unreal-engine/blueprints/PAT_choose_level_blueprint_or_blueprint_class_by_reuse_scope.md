---
object_id: PAT_choose_level_blueprint_or_blueprint_class_by_reuse_scope
object_type: pattern
name: Choose Level Blueprint or Blueprint Class by Reuse Scope
library_path:
- software-engineering
- unreal-engine
- blueprints
stage_binding: 0 design
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- blueprints
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Choose Level Blueprint or Blueprint Class by Reuse Scope

## Pattern Rule
**IF** you must decide where new behavior lives in an Unreal Engine project
**THEN** put reusable interactive game objects in a Blueprint Class, and level-specific one-off logic in that level's Level Blueprint — each level has exactly one Level Blueprint and it cannot be created separately.

## Do
- Decide the ownership of the logic (level-local or reusable object) before opening an editor.
- Open the level's existing Level Blueprint from the Blueprints dropdown in the toolbar.
- Create a Blueprint Class from the Content Browser (Add button or right-click menu) and choose its parent class.

## Don't
- Don't build level-specific one-off logic into a Blueprint Class that then gets scattered across the project.
- Don't try to create a second Level Blueprint for a single level — it already exists; you can only open it.

## Checklist
- A new behavior has an explicit owner: the level's Level Blueprint when it only makes sense in that level, a Blueprint Class when the object should be placeable in any level.
- The Level Blueprint editor (only My Blueprint, Details, and Event Graph panels) is used for level-local work; the full Blueprint Class editor (Toolbar, Components, My Blueprint, Details, Viewport, Event Graph) is used for reusable objects.

## Notes
In Unreal, "Blueprint" names both the visual scripting language and the game object created with it, so the two Blueprint kinds are different answers to different ownership questions. The Level Blueprint editor is simpler than the Blueprint Class editor precisely because a level is a container, not a placed, reusable object. The choice is structural, not cosmetic: it fixes where the logic lives and whether other levels can reuse it.
