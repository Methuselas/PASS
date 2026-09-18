---
object_id: PAT_register_unreal_toolmenus_after_editor_startup
object_type: pattern
name: Register Unreal ToolMenus After Editor Startup
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
- editor_tools
- toolmenus
cross_links: []
reference:
  source_title: Extending and Customizing Unreal Engine Editor
  author: Roger Mattsson
confidence: medium
references: []
variants: []
---

# Register Unreal ToolMenus After Editor Startup

## Pattern Rule
**IF** a module adds persistent Unreal toolbar or menu actions through ToolMenus
**THEN** defer registration until the editor's menu startup callback, assign a scoped owner and explicit command list, and remove the callback, entries and borrowed mappings during teardown.

## Do
- Register commands and map their actions before registering the startup callback; it may execute immediately when the editor is already ready. Keep availability independent of a mode that is not required.
- Inspect the installed menu names and choose a plugin-owned section and appropriate entry type.
- Use `FToolMenuOwnerScoped` when extending menus so each entry has a removable owner.
- Set each entry's command list deliberately; a command declaration alone does not connect a button to an action.
- Resolve icons from an available style and declare the actual ToolMenus and platform dependencies in the consuming editor module.
- Unregister the startup callback and owned entries before releasing receivers, command lists or styles. End retained mappings as well as visible entries.
- Verify repeated registration and teardown without duplicates or damage to another owner's entries.

## Don't
- Don't assume editor menus are ready during module startup or that a startup callback runs in a commandlet.
- Don't leave raw callbacks behind when removing visible buttons.

## Checklist
- Do the entries exist after the deferred callback and invoke the intended command list?
- Does teardown remove only this owner's entries and end receiver borrows?
- Do two cycles preserve other owners and leave no duplicate entries?

## Notes
This specializes `PAT_give_every_acquired_resource_one_named_owner` for deferred ToolMenus registration. Native menu construction does not establish visible toolbar interaction.
