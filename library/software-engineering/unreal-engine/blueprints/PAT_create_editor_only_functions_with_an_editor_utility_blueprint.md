---
object_id: PAT_create_editor_only_functions_with_an_editor_utility_blueprint
object_type: pattern
name: Create Editor-Only Functions With an Editor Utility Blueprint
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
- editor_utility
- editor_scripting
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Create Editor-Only Functions With an Editor Utility Blueprint

## Pattern Rule
**IF** you need a function that manipulates assets or level actors only while editing (a tool that aligns selected actors, batches asset edits) and never runs in the shipped game
**THEN** create an Editor Utility Blueprint with AssetActionUtility as the parent class for content-browser assets or ActorActionUtility for level actors; its functions then appear in the Script Actions submenu when you right-click an asset or actor.

## Do
- Create the function in the Editor Utility Blueprint's Event Graph; it is exposed automatically under Scripted Actor/Asset Actions in the right-click menu.
- Pick the parent class by the target: AssetActionUtility to act on assets in the content browser, ActorActionUtility to act on actors in the level.
- Use the Get Selection Set node to read the actors the designer has selected, then iterate the set (for example with a For Each Loop) to apply the operation to every selected actor.
- Browse the Editor Scripting category in the node menu to find the editor functions (asset, content browser, level, materials, dialogs, and more) the utility can call.

## Don't
- Don't put editor-only tooling in a normal game Blueprint — Editor Utility Blueprints run only in the editor and are excluded from the game, so game logic and editor tools stay separate.
- Don't assume an Editor Utility Blueprint function runs at runtime; it is an edit-mode tool and will not exist in a packaged build.

## Checklist
- The new function appears in the Script Actions submenu when right-clicking the appropriate asset or actor.
- Running it on a multi-actor selection applies the operation to every selected actor.
- The function has no effect in a running (packaged) game.

## Notes
Editor Utility Blueprints are Blueprints that exist only in the editor; they let you script editor behavior — manipulating assets in the content browser or actors in the level — without writing C++. The parent class decides what the functions can act on: AssetActionUtility for assets, ActorActionUtility for actors. A companion Editor Utility Widget (a UMG widget) can add panels to the editor for richer tool UI. The typical shape is a function that reads the current selection (Get Selection Set) and applies a batch operation, such as copying one selected actor's X location to all the others.
