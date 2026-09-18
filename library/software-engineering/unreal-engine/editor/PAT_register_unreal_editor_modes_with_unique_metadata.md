---
object_id: PAT_register_unreal_editor_modes_with_unique_metadata
object_type: pattern
name: Register Unreal Editor Modes with Unique Metadata
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
- editor_modes
- registration
cross_links:
- rel: related_to
  target_object_id: PAT_give_every_acquired_resource_one_named_owner
- rel: related_to
  target_object_id: PAT_own_shared_unreal_slate_styles_in_the_editor_module
reference:
  source_title: Extending and Customizing Unreal Engine Editor
  author: Roger Mattsson
confidence: medium
references: []
variants: []
---

# Register Unreal Editor Modes with Unique Metadata

## Pattern Rule
**IF** a group of editor tools needs its own selectable mode
**THEN** give an `FEdMode` subclass a unique `FEditorModeID` and register it through `FEditorModeRegistry` from the editor module with an explicit display name, visibility, icon and ordering priority.

## Do
- Group tools by the discipline or workflow they serve, so unrelated users need not work through one large mode.
- Use a project/plugin-qualified identifier; an `EM_` prefix alone does not prevent collisions.
- Call the base `FEdMode::Enter()` and `FEdMode::Exit()` from overrides that extend those lifecycle hooks.
- Decide whether to return true from `UsesPropertyWidgets()`: true preserves property widgets for properties marked `MakeEditWidget`; false can suit a mode whose interaction would conflict with them.
- Pass a visibility setting deliberately. A mode may be hidden until a particular map or asset makes it relevant.
- Choose a lower priority value when the mode should appear earlier in the ordered mode list.
- Register the style before constructing the `FSlateIcon` that names its entries. Supply both normal and small style keys.
- Pair the module's registration with `FEditorModeRegistry::Get().UnregisterMode(ModeID)` during shutdown, before releasing styles used by the mode. Registration borrows implementation code from the loaded module; it must not survive that code's lifetime.

## Don't
- Don't assume that compiling the mode class makes it selectable; it must be registered.
- Don't promise a fixed keyboard shortcut or list position from a priority value. Ordering depends on the other installed modes.
- Don't treat an empty mode as a finished tool. It proves the registration entry point, not the later tool behavior.

## Checklist
- Is the ID unique among registered modes?
- Can the registry create an instance of the intended subclass?
- Do the registered name, visibility, priority and icon keys match the intended mode?
- After teardown, is the fixture's mode absent from the registry?
- Does the property-widget policy match the mode's interaction?

## Notes
An editor mode is a container for a workflow, not necessarily one large tool. Registration makes its factory and presentation metadata available to the editor; the instance's Enter and Exit hooks govern later interaction. Keep those responsibilities distinct when diagnosing a mode that compiles but does not appear.
