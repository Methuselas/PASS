---
object_id: AP_bootstrap_a_styled_unreal_editor_mode
object_type: ap
name: Bootstrap a Styled Unreal Editor Mode
library_path:
- software-engineering
- unreal-engine
- editor
stage_binding: 1 skeleton
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- plugins
- editor_modes
- slate
cross_links:
- rel: supports
  target_object_id: PAT_keep_unreal_editor_dependencies_in_editor_modules
- rel: supports
  target_object_id: PAT_register_unreal_editor_modes_with_unique_metadata
- rel: supports
  target_object_id: PAT_own_shared_unreal_slate_styles_in_the_editor_module
reference:
  source_title: Extending and Customizing Unreal Engine Editor
  author: Roger Mattsson
confidence: medium
references: []
variants: []
---

# Bootstrap a Styled Unreal Editor Mode

## Objective
Produce an editor-only plugin mode whose class links, whose registration metadata resolves, and whose normal and small icon resources come from a shared module-owned style set.

## Steps / Flow
1. Choose an existing plugin or create a Blank plugin. Inspect the descriptor and module rules instead of assuming the template has the desired module type.
2. Apply `PAT_keep_unreal_editor_dependencies_in_editor_modules`: select an editor module, retain any separate runtime module, and declare the editor and Slate dependencies.
3. Add an `FEdMode` subclass with a unique ID, base-calling Enter/Exit hooks, and an explicit property-widget policy.
4. Apply `PAT_own_shared_unreal_slate_styles_in_the_editor_module`: create a module-owned set, set its resource root, populate normal and small keys, and register it in module startup.
5. Apply `PAT_register_unreal_editor_modes_with_unique_metadata`: register the class with its display name, visibility, priority and icon keys after style registration.
6. Compile an editor target. For unresolved symbols, check the supplying module dependency; for missing icons, check the root, file and style keys separately.
7. Run the editor and verify the registered mode and both resolved icon entries. If checking interactively, select the mode and verify its property-widget policy; a headless registry check does not demonstrate viewport interaction.
8. Unregister the mode before releasing its styles. Exercise style cleanup through the module's unregister-before-reset path and verify that neither the mode nor the style remains registered. Repeat the cycle with the same fixture names to catch stale registrations.

## Notes
This procedure establishes a tool container and shared presentation resources. It does not implement object edits, Blueprint graph mutations or transactions. Later tools can use the same module and styles without putting their shared resources inside one mode instance.
