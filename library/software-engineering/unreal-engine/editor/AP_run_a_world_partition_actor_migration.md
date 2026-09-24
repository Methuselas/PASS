---
object_id: AP_run_a_world_partition_actor_migration
object_type: ap
name: Run a World Partition Actor Migration
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
- world_partition
- commandlets
- migration
cross_links:
- rel: supports
  target_object_id: PAT_plan_world_partition_actor_replacements_before_mutation
- rel: supports
  target_object_id: PAT_inspect_unreal_blueprint_component_templates_across_inheritance
reference:
  source_title: Extending and Customizing Unreal Engine Editor
  author: Roger Mattsson
confidence: medium
references: []
variants: []
---

# Run a World Partition Actor Migration

## Objective
Execute a reviewable, resumable World Partition actor replacement through a builder commandlet without silently losing authored state or package changes.

## Steps / Flow
1. Define source eligibility, destination mapping and the actor properties/references that must survive. Choose iterative-cell, entire-world or custom loading based on the required context.
2. In pre-run, query candidate assets/classes and build a multimap from source keys to possible destinations. Apply `PAT_inspect_unreal_blueprint_component_templates_across_inheritance` only when static class defaults are sufficient.
3. Resolve mappings to exactly one destination or record an ambiguity. Generate a dry-run manifest with source actor/package, destination class, transferred state and predicted package operations.
4. Require an explicit write mode only after the manifest is acceptable. Retain a run identity/checkpoint for resumability.
5. For each loaded cell, enumerate actor descriptors through World Partition helpers. Skip already migrated or out-of-scope actors deterministically.
6. Spawn the destination actor, copy every declared semantic field and validate the result. Only then remove the source and record the new/deleted external-actor packages.
7. Save and delete through the builder's package/source-control helpers. Stop or mark the run failed on any package operation that prevents an atomic semantic replacement.
8. Emit a final manifest of replaced, skipped, ambiguous and failed items. Rerun in dry-run mode and require zero unexpected changes.

## Notes
The builder handles cell loading, not migration correctness. Project-specific mapping keys and copied fields belong in adapters; ambiguity handling, mutation order, package accounting and idempotency are the reusable protocol.
