---
object_id: AP_publish_an_unreal_editor_batch_validation_command
object_type: ap
name: Publish an Unreal Editor Batch Validation Command
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
- commandlets
- diagnostics
- progress
cross_links:
- rel: supports
  target_object_id: PAT_register_unreal_toolmenus_after_editor_startup
- rel: supports
  target_object_id: PAT_stream_unreal_editor_batch_processes_with_bounded_feedback
- rel: supports
  target_object_id: PAT_report_unreal_tool_outcomes_through_a_small_facade
reference:
  source_title: Extending and Customizing Unreal Engine Editor
  author: Roger Mattsson
confidence: medium
references: []
variants: []
---

# Publish an Unreal Editor Batch Validation Command

## Objective
Publish a cancellable Unreal editor command that runs a project-wide validator outside the current editor process and returns bounded progress, a reliable outcome and navigable diagnostics.

## Steps / Flow
1. Define the validation scope, exclusions and success contract. Choose a commandlet or executable that can run unattended and produce a nonzero exit result for failed validation.
2. Define a stable output protocol for total work, completed items and diagnostics. If the engine-owned commandlet lacks one, prefer a project-owned wrapper or versioned marker over parsing incidental prose.
3. Map one editor command to the operation and expose it through owned ToolMenus entries. Disable duplicate starts while the same owner has an active process.
4. Apply `PAT_stream_unreal_editor_batch_processes_with_bounded_feedback`: validate and quote the project/executable paths, create pipes, launch hidden, and retain all handles in one operation object.
5. Present indeterminate scanning until a valid nonzero total is known. Then advance only by newly observed completed-item markers, clamp displayed progress and keep the editor responsive.
6. On cancellation, module shutdown or editor teardown, terminate once if necessary, drain/close resources and complete retained UI state with an explicit cancelled result.
7. Parse final diagnostics into normalized records. Validate project asset references before creating clickable tokens, deduplicate stable repeats and add the records to a new message-log page for this run.
8. Combine exit code, protocol validity and diagnostics into a machine-readable result. Report success even when the page is empty, and report launch/protocol failures without disguising them as validation errors.
9. Exercise clean success, known validation failure, malformed output, launch failure, zero work, cancellation and module shutdown before publishing the command.

## Notes
Compiling every Blueprint is one use of this protocol; asset audits, commandlet-driven checks and offline transformations use the same lifecycle. Exact menu placement, log category names and project-specific exclusions are configuration, not part of the reusable capability.
