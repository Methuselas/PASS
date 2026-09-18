---
object_id: AP_reimport_an_unreal_asset_from_an_explicit_target
object_type: ap
name: Reimport an Unreal Asset from an Explicit Target
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
- reimport
cross_links:
- rel: supports
  target_object_id: PAT_enforce_an_explicit_unreal_selection_policy
- rel: supports
  target_object_id: PAT_reimport_unreal_assets_through_validated_sources
- rel: supports
  target_object_id: PAT_report_unreal_tool_outcomes_through_a_small_facade
- rel: supports
  target_object_id: PAT_route_unreal_tool_input_through_active_commands
reference:
  source_title: Extending and Customizing Unreal Engine Editor
  author: Roger Mattsson
confidence: medium
references: []
variants: []
---

# Reimport an Unreal Asset from an Explicit Target

## Objective
Refresh the intended existing asset from its source files, with an explicit target, usable outcome and verified refreshed data.

## Steps / Flow
1. Apply `PAT_enforce_an_explicit_unreal_selection_policy` when starting from editor selection. Otherwise validate the explicit actor/component or asset argument. Stop on ambiguity or absence.
2. For an actor/component target, extract the intended component's asset reference; for an explicit asset target, retain that validated asset. Report which asset will change. For a batch, collect unique assets before executing.
3. Apply `PAT_reimport_unreal_assets_through_validated_sources`: check capability, required files and interactive versus unattended handling before dispatch.
4. Execute the reimport and obtain its completion outcome. Stop or report per-asset failures according to the declared batch policy; do not imply all-or-nothing behavior.
5. Apply `PAT_report_unreal_tool_outcomes_through_a_small_facade` to expose the result and reason through the actual caller interface.
6. Read back the refreshed asset's relevant data against the intended source change. If it differs, report the verification failure and attribute it to target resolution, source selection, import execution or verification before retrying. Only matching readback establishes the intended refresh.
7. Save or restore only through an explicitly supported procedure. State whether persistence and restoration were exercised.

## Notes
For a keyboard entry point, use `PAT_route_unreal_tool_input_through_active_commands` to scope and bind the command. Validation inside an intentionally handled command prevents a rejected operation from falling through to an unrelated command sharing its key.
