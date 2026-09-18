---
object_id: PAT_own_shared_unreal_slate_styles_in_the_editor_module
object_type: pattern
name: Own Shared Unreal Slate Styles in the Editor Module
library_path:
- software-engineering
- unreal-engine
- editor
stage_binding: 1 skeleton
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: PAT_give_every_acquired_resource_one_named_owner
tags:
- unreal_engine
- slate
- styles
- lifetime
cross_links: []
reference:
  source_title: Extending and Customizing Unreal Engine Editor
  author: Roger Mattsson
confidence: medium
references: []
variants: []
---

# Own Shared Unreal Slate Styles in the Editor Module

## Pattern Rule
**IF** several editor tools need the same plugin icon resources
**THEN** own one named `FSlateStyleSet` in the editor module, register it before consumers use it, and unregister it before releasing its owning shared pointer during module shutdown.

## Do
- Store the set in a module-owned `TSharedPtr` whose element type is `FSlateStyleSet`; forward-declare the type in the header where possible and include the full definitions in the implementation.
- Give the set a unique, stable name and expose that name to callers without forcing them to find a module instance.
- Set the content root to the plugin's actual `Resources` directory. A root built from `FPaths::ProjectPluginsDir()` applies to a project-installed plugin; do not assume that placement for every installation.
- Register separate normal and small brush keys for each icon, commonly using 40-by-40 and 20-by-20 sizes. Both may point to the same image file.
- Use `FSlateStyleRegistry::RegisterSlateStyle(*StyleSet)` after populating the brushes.
- During cleanup, check that the pointer is valid, call `UnRegisterSlateStyle(*StyleSet)`, check ownership with `ensure(StyleSet.IsUnique())`, then reset it.
- Treat a failed uniqueness check as evidence that another shared owner remains; find that owner before assuming teardown is complete.

## Don't
- Don't put a plugin-wide style in an individual mode that may leave while another tool still needs the icons.
- Don't reset the pointer while the style registry still refers to the set.
- Don't confuse a correct icon key with an existing image file; check the resource path as well.

## Checklist
- Does the registered name resolve to the intended style set?
- Do normal and small keys resolve to brushes with the expected resources and dimensions?
- Does the resource root match the current plugin installation?
- After cleanup, is the style absent from the registry and is the module's owning pointer empty?

## Notes
The style registry borrows the registered object; registration does not replace the module's lifetime responsibility. A shared style set therefore belongs at the lifetime common to its consumers. A second owning shared pointer can keep a style alive after unregistering, while an early reset can leave the registry pointing at an object whose owner has gone.
