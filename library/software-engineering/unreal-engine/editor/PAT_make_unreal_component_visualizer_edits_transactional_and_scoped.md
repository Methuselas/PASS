---
object_id: PAT_make_unreal_component_visualizer_edits_transactional_and_scoped
object_type: pattern
name: Make Unreal Component Visualizer Edits Transactional and Scoped
library_path:
- software-engineering
- unreal-engine
- editor
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- editor_tools
- component_visualizer
- transactions
- viewport
cross_links:
- rel: related_to
  target_object_id: PAT_snapshot_unreal_edit_targets_before_mutation
- rel: related_to
  target_object_id: PAT_cache_unreal_tool_selections_as_weak_objects
reference:
  source_title: Extending and Customizing Unreal Engine Editor
  author: Roger Mattsson
confidence: medium
references: []
variants: []
---

# Make Unreal Component Visualizer Edits Transactional and Scoped

## Pattern Rule
**IF** an Unreal component visualizer draws selectable viewport affordances or edits reflected component data
**THEN** bind each hit proxy to validated component/item identity, bracket continuous edits as one transaction, and restore every editor-global interaction setting when editing ends.

## Do
- Register the visualizer only after `GUnrealEd` is available and unregister the exact component class during module shutdown; keep the feature in an editor module.
- Treat the visualizer instance as reusable. Store the active component weakly and validate it, the owning actor and any selected index on every draw/input path.
- Set a hit proxy only for the exact primitive or sprite it owns and clear it immediately afterward. Carry stable item identity rather than trusting an array index after mutation when reorder/delete is possible.
- Return a widget location only for a valid active item. Apply only supported transform deltas and reject rotation/scale explicitly when they are not meaningful.
- Begin a transaction at gesture start, call `Modify()` before the first mutation, apply deltas during the gesture, and close one transaction at gesture end; do not create one undo step per mouse-move callback.
- Route context actions through owned commands and reset active item identity after deletion.
- If editor-global behavior is changed to improve interaction, capture its previous value and restore that value on end editing, deselection, module shutdown and exceptional exit.
- Keep diagnostic drawing side-effect free and bounded; cache expensive path queries or recompute only when source data changes.

## Don't
- Don't retain a raw selected component or stale array index across selection changes and structural edits.
- Don't hard-code restoration to an assumed global default.
- Don't perform expensive navigation/path work every viewport draw when inputs are unchanged.
- Don't mutate the component from rendering callbacks.

## Checklist
- Does one drag produce one meaningful undo step and restore correctly on redo?
- Can add/select/delete survive stale proxies, reorder and component destruction?
- Are global interaction settings restored on every exit path?
- Are registration, commands, textures and module dependencies owned and released coherently?

## Notes
Hit proxies, transform widgets, context menus and HUD drawing are pieces of one editor interaction state machine. Treating them separately is how stale selection and leaked global-state bugs arise.
