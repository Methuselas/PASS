---
object_id: PAT_keep_unreal_editor_preview_actors_transient_and_disposable
object_type: pattern
name: Keep Unreal Editor Preview Actors Transient and Disposable
library_path:
- software-engineering
- unreal-engine
- editor
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: PAT_give_every_acquired_resource_one_named_owner
tags:
- unreal_engine
- editor_tools
- actor_lifecycle
- preview
cross_links: []
reference:
  source_title: Extending and Customizing Unreal Engine Editor
  author: Roger Mattsson
confidence: medium
references: []
variants: []
---

# Keep Unreal Editor Preview Actors Transient and Disposable

## Pattern Rule
**IF** an Unreal editor tool spawns an actor only to visualize or support the current editing session
**THEN** create it as editor-only transient state with no actor package, and destroy it across every tool, map and module lifetime boundary.

## Do
- Spawn into the editor world chosen for the tool, clear transactional participation when undo is not part of the feature, add `RF_Transient`, set `bTemporaryEditorActor`, disable actor-package creation and mark the actor editor-only.
- Hide purely supportive actors from the Scene Outliner and suppress incidental components such as billboards when they would pollute the editing view.
- Keep the spawned actor reference and every updater together in one helper. On deactivation, remove the ticker before destroying the actor and clear both the handle and reference.
- Subscribe to map changes when a live actor cannot cross worlds, and turn the feature off before the old editor world is replaced.
- During module shutdown, remove raw delegates while their receiver still exists and run the same idempotent deactivation path used by the toggle.
- Verify the world remains unmodified after saving, changing maps, disabling the tool and unloading the module.

## Don't
- Don't let a convenience actor acquire a package, appear as authored level content or survive through a raw ticker callback after its helper is gone.
- Don't treat `TObjectPtr` in a non-`UCLASS` helper as a substitute for explicit lifetime cleanup or garbage-collection ownership.

## Checklist
- Is the actor absent from saved level state and ordinary authored-actor workflows?
- Do disable, map change and module shutdown each remove the updater before destroying and clearing the actor?
- Can repeated enable/disable cycles complete without duplicates, stale callbacks or a reference into the previous editor world?

## Notes
This specializes named resource ownership for editor-only actors that exist to make a tool visible or interactive. The transient flags prevent persistence; they do not by themselves end ticker and delegate borrows. A non-reflected helper must make those separate lifetimes explicit.
