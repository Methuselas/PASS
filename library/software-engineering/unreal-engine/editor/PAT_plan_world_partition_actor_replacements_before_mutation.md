---
object_id: PAT_plan_world_partition_actor_replacements_before_mutation
object_type: pattern
name: Plan World Partition Actor Replacements Before Mutation
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
- world_partition
- migration
- validation
cross_links:
- rel: related_to
  target_object_id: PAT_inspect_unreal_blueprint_component_templates_across_inheritance
- rel: related_to
  target_object_id: PAT_scope_unreal_asset_validation_with_registry_queries
reference:
  source_title: Extending and Customizing Unreal Engine Editor
  author: Roger Mattsson
confidence: medium
references: []
variants: []
---

# Plan World Partition Actor Replacements Before Mutation

## Pattern Rule
**IF** an Unreal editor migration replaces actors across a World Partition map
**THEN** derive and validate an unambiguous replacement plan before cell mutation, preserve declared actor semantics, and commit package creates/deletes through the partition builder's save and source-control boundary.

## Do
- Build candidate mappings in a pre-run phase from explicit rules or validated class defaults. Record zero, one or many destinations for each source key; never let insertion order resolve ambiguity.
- Provide a dry-run report listing every proposed replacement, ambiguity, unsupported actor and package effect before writes are enabled.
- Use an appropriate `UWorldPartitionBuilder` loading mode and operate through partition actor descriptors/helpers so cells can be processed without loading the entire map.
- For each candidate, validate the source actor, destination class and spawn result before deleting anything.
- Declare which semantics transfer: transform, label, folder, data layers, runtime grid, HLOD/layer settings, attachments, tags, mobility, per-instance overrides and external references. Reject or explicitly migrate unsupported state.
- Make execution idempotent and resumable: a second run must not replace already migrated actors or compound partial results.
- Accumulate exact external-actor packages to create/save/delete, use builder/package source-control helpers, and treat any save/delete failure as a failed cell/run.
- Produce counts and stable identities for replaced, skipped, ambiguous and failed actors.

## Don't
- Don't delete the source actor until the destination exists and required state has been copied successfully.
- Don't map a shared mesh to whichever Blueprint happened to be scanned last.
- Don't assume copying only `FTransform` preserves authored actor meaning.
- Don't report success after ignoring package or source-control failures.

## Checklist
- Is every replacement mapping unique, explainable and reviewable before mutation?
- Are map-specific actor semantics and references either preserved or explicitly rejected?
- Can the migration resume safely after interruption and run twice without additional change?
- Do package save/delete results and source-control operations determine the final outcome?

## Notes
Replacing plain static-mesh actors with interactive Blueprint actors is one migration. The same protocol applies to class upgrades, deprecated actor conversion and partition-wide authored-data repair.
