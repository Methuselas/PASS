---
object_id: AP_publish_a_persistent_unreal_toolbar_action
object_type: ap
name: Publish a Persistent Unreal Toolbar Action
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
- toolmenus
cross_links:
- rel: supports
  target_object_id: PAT_route_unreal_tool_input_through_active_commands
- rel: supports
  target_object_id: PAT_register_unreal_toolmenus_after_editor_startup
- rel: supports
  target_object_id: PAT_report_unreal_tool_outcomes_through_a_small_facade
reference:
  source_title: Extending and Customizing Unreal Engine Editor
  author: Roger Mattsson
confidence: medium
references: []
variants: []
---

# Publish a Persistent Unreal Toolbar Action

## Objective
Publish an always-available editor action through ToolMenus, with deliberate command routing and removable ownership.

## Steps / Flow
1. Confirm a callable editor action, its input/result contract and module owner. Apply `PAT_route_unreal_tool_input_through_active_commands` to declare and map the action in its intended persistent scope.
2. Apply `PAT_register_unreal_toolmenus_after_editor_startup`: select the installed menu and section, supply style/dependencies, and defer entry registration through the startup callback.
3. Apply `PAT_report_unreal_tool_outcomes_through_a_small_facade` inside execution. Keep availability polling cheap and validate changing external input again when the action executes.
4. Run the deferred registration and exercise the entry's actual command route. If the environment cannot show toolbar UI, retain native construction results and defer visible interaction qualification explicitly.
5. End the startup callback, owned entries and retained mappings before receivers or resources disappear. Repeat registration/teardown and verify other owners remain intact; stop on duplicates or stale callbacks.

## Notes
Persistent means the action does not require an optional editor mode. It does not mean the module's resources survive shutdown.
