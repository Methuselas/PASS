---
object_id: AP_add_a_toolkit_interface_to_an_unreal_fedmode
object_type: ap
name: Add a Toolkit Interface to an Unreal FEdMode
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
cross_links:
- rel: supports
  target_object_id: PAT_choose_unreal_mode_base_from_tool_requirements
- rel: supports
  target_object_id: PAT_separate_shared_unreal_defaults_from_local_tool_preferences
- rel: supports
  target_object_id: PAT_bind_unreal_mode_toolkits_to_guarded_tool_state
- rel: supports
  target_object_id: PAT_route_unreal_tool_input_through_active_commands
- rel: supports
  target_object_id: PAT_scope_unreal_context_menu_extenders_to_their_tool
reference:
  source_title: Extending and Customizing Unreal Engine Editor
  author: Roger Mattsson
confidence: medium
references: []
variants: []
---

# Add a Toolkit Interface to an Unreal FEdMode

## Objective
Add guarded controls and context-menu actions to an existing FEdMode tool, with persistent preference scope and clean teardown.

## Steps / Flow
1. Confirm an existing registered FEdMode and callable tool actions. If reflection requirements change the base choice, use `PAT_choose_unreal_mode_base_from_tool_requirements` and stop this FEdMode-specific procedure for a different framework.
2. Apply `PAT_separate_shared_unreal_defaults_from_local_tool_preferences`; define shared tool defaults and local interface preferences before binding persistence callbacks.
3. Apply `PAT_bind_unreal_mode_toolkits_to_guarded_tool_state`: construct sections and controls, bind current state and guard mode lookup, then create and initialize the toolkit from the mode's enter path.
4. Apply `PAT_route_unreal_tool_input_through_active_commands` for the common callable actions and scoped command lists.
5. Apply `PAT_scope_unreal_context_menu_extenders_to_their_tool` to register relevant menu entries while the tool is active.
6. Exercise controls, buttons and menu actions. Verify display follows external state changes and collapse/expand preferences survive reopening; correct state translation before proceeding.
7. Exit the mode and release registrations and retained callbacks before receiver destruction. Repeat activation and deactivation, then verify there are no duplicate entries or callable dead receivers.

## Notes
This coordinates existing operation helpers; it does not move game behavior into widgets. Modern reflected-mode setup is a separate procedure.
