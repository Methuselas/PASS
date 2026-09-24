---
object_id: PAT_scope_unreal_asset_validation_with_registry_queries
object_type: pattern
name: Scope Unreal Asset Validation with Registry Queries
library_path:
- software-engineering
- unreal-engine
- editor
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: PAT_prefer_explicit_error_signaling_for_recoverable_errors
tags:
- unreal_engine
- editor_tools
- commandlets
- asset_registry
- validation
cross_links:
- rel: related_to
  target_object_id: PAT_stream_unreal_editor_batch_processes_with_bounded_feedback
reference:
  source_title: Extending and Customizing Unreal Engine Editor
  author: Roger Mattsson
confidence: medium
references: []
variants: []
---

# Scope Unreal Asset Validation with Registry Queries

## Pattern Rule
**IF** an Unreal commandlet or editor action validates assets across project content
**THEN** normalize an explicit package-path scope, query candidate metadata through the Asset Registry, load only what each rule requires, and emit stable per-asset findings plus a meaningful process result.

## Do
- Define required rule switches and one or more canonical long package paths. Reject a missing, empty or invalid scope before scanning.
- Normalize separators and trailing delimiters, deduplicate nested selections and compare package paths by segment-aware ancestry rather than raw ambiguous prefixes.
- Use Asset Registry class/path filters to reduce candidates before loading. Distinguish direct assets from Blueprint classes and component templates.
- Let each validation rule state whether it needs metadata, a loaded asset, compiled derived data or Blueprint default/template state. Wait only for the specific derived data required by the current asset when supported.
- Emit a stable finding record containing rule ID, severity, object path and message; keep human log prose as presentation around that record.
- Count scanned, skipped, failed-to-load and invalid assets. Return nonzero for invocation/infrastructure failure and use a documented policy for validation findings so CI can gate reliably.
- When launched from the Content Browser, snapshot and validate selected package paths, quote/encode them safely, and pass the same scope contract used by build automation.

## Don't
- Don't call a full-project search or flush all compilation work when a bounded registry query or per-asset wait is sufficient.
- Don't treat every nonnegative commandlet return as an error; define and test the actual exit-code contract.
- Don't derive correctness solely from localized log text parsed by the caller.
- Don't assume a raw string prefix makes one package path a child of another.

## Checklist
- Is the exact package scope visible in output and identical between UI and CI entry points?
- Are candidate discovery, loading and derived-data waits minimized and counted?
- Can callers distinguish invalid invocation, infrastructure failure, findings and clean success?
- Does every finding retain a resolvable asset identity and stable rule identity?

## Notes
Collision checks, navigation-policy audits and mesh-usage rules are examples. The reusable capability is a deterministic asset-validation pipeline whose scope and outcome do not depend on where it was launched.
