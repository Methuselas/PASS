---
object_id: PAT_keep_unreal_editor_dependencies_in_editor_modules
object_type: pattern
name: Keep Unreal Editor Dependencies in Editor Modules
library_path:
- software-engineering
- unreal-engine
- editor
stage_binding: 1 skeleton
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: PAT_design_the_physical_dependency_graph_too
tags:
- unreal_engine
- plugins
- module_dependencies
cross_links: []
reference:
  source_title: Extending and Customizing Unreal Engine Editor
  author: Roger Mattsson
confidence: medium
references: []
variants: []
---

# Keep Unreal Editor Dependencies in Editor Modules

## Pattern Rule
**IF** a plugin feature extends the Unreal Editor rather than the running game
**THEN** place it in a module declared `Editor` in the plugin descriptor, add the modules that provide its C++ symbols to that module's `Build.cs`, and separate runtime functionality into a runtime module when the plugin needs both.

## Do
- Treat the plugin descriptor and module build rules as different contracts: the descriptor selects module type and loading phase; `Build.cs` declares compile/link dependencies.
- For an `FEdMode` extension, declare `UnrealEd` and `EditorFramework` dependencies; add `Slate` and `SlateCore` for the shared UI styles.
- Use private dependencies for implementation-only use. Check the dependency exposure again if a public header exposes another module's types.
- Start with the default loading phase when it meets the feature's needs; change the phase for an initialization requirement, rather than copying another feature's setting.
- Declare required plugins separately in the descriptor's `Plugins` section. A C++ module dependency is not a replacement for enabling a required plugin.
- Set `CanContainContent` from the actual plugin design: false for a plugin without content, true when it ships content.
- Forward-declare types held through pointers when their complete definition is unnecessary in the header; include their definitions in the implementation.

## Don't
- Don't leave an editor-only module as `Runtime` merely because the Blank plugin template generated that value.
- Don't try to cure unresolved external symbols by adding more include files. Identify the providing module and declare the dependency.
- Don't remove content support from a mixed plugin just because an editor-only example does not use content.

## Checklist
- Does every editor feature belong to an editor module?
- Do build rules explicitly name the modules supplying the symbols used?
- Are plugin enablement and C++ dependencies both declared where needed?
- Does a clean editor-target build compile and link the extension?

## Notes
A plugin may contain multiple modules with different lifetimes and dependency sets. That split lets game-facing code remain usable without pulling editor tooling into the runtime. Header visibility and link visibility are separate: reading a declaration does not provide its compiled implementation.
