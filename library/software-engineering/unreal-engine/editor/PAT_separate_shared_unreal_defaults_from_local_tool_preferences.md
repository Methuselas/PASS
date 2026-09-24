---
object_id: PAT_separate_shared_unreal_defaults_from_local_tool_preferences
object_type: pattern
name: Separate Shared Unreal Defaults from Local Tool Preferences
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
- editor_tools
cross_links: []
reference:
  source_title: Extending and Customizing Unreal Engine Editor
  author: Roger Mattsson
confidence: medium
references: []
variants: []
---

# Separate Shared Unreal Defaults from Local Tool Preferences

## Pattern Rule
**IF** an Unreal editor extension persists tool configuration and personal interface preferences
**THEN** choose their configuration destinations separately and keep shared defaults distinct from generated local preference writes.

## Do
- Declare a config class name and config properties deliberately.
- Use default-config behavior for defaults intended to be shared, with the corresponding project default file under team control.
- Use a local preference destination for personal choices such as collapsed tool sections; save the intended mutable configuration object.
- For continuously adjustable controls, update the mutable setting and live tool on each value change, invalidate the affected viewport when necessary, and call `SaveConfig` only when the user commits the value.
- Bind displayed values back to the current default object so reopening a generated control reads persisted state instead of a stale widget copy.
- Register settings in the appropriate editor section and remove the registration during module shutdown.
- Name a stored boolean by its actual meaning; translate expansion callbacks and initially-collapsed input consistently.
- Verify the destination, write frequency and restored value rather than inferring scope from a class name.

## Don't
- Don't save personal widget state into shared defaults.
- Don't write the config file for every intermediate mouse-drag value and turn interactive adjustment into repeated synchronous persistence.
- Don't call a value expanded while persisting the inverse without an explicit translation.

## Checklist
- Which file receives a change, and who should share it?
- Does live preview update without a durable write for every intermediate value?
- Does committing and reopening restore the chosen value and interface state?
- Are settings registrations removed safely?

## Notes
A config declaration controls engine loading and saving behavior; it does not automatically establish version-control policy, commit timing or every user's filesystem layout. Interactive controls have two useful boundaries: transient preview while the value is changing, and durable persistence after the user commits it.
