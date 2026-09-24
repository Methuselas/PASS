---
object_id: PAT_reconcile_unreal_data_table_round_trips_by_schema_and_key
object_type: pattern
name: Reconcile Unreal Data Table Round Trips by Schema and Key
library_path:
- software-engineering
- unreal-engine
- editor
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: PAT_barricade_dirty_data_at_a_named_boundary
tags:
- unreal_engine
- editor_tools
- data_tables
- csv
- validation
cross_links:
- rel: related_to
  target_object_id: PAT_secure_unreal_editor_external_data_sync_boundaries
reference:
  source_title: Extending and Customizing Unreal Engine Editor
  author: Roger Mattsson
confidence: medium
references: []
variants: []
---

# Reconcile Unreal Data Table Round Trips by Schema and Key

## Pattern Rule
**IF** an Unreal Data Table is exported to an editable external representation and later imported
**THEN** reconcile it against an explicit schema and stable row identity, preview the semantic diff, and apply an accepted result as one undoable editor mutation.

## Do
- Give every row a stable key that survives sorting and insertion. Match by that key, never by current row position or display order.
- Export a versioned schema contract with field names, expected Unreal types and any enum, range, nullability or reference constraints needed for a lossless return trip.
- Use a standards-compliant serializer and parser. Preserve quoting, embedded delimiters, line breaks, Unicode and locale-independent numeric and Boolean forms.
- Parse into a detached candidate model. Reject duplicate or missing keys, unknown required columns, incompatible schema versions and values that cannot be converted before touching the live table.
- Compute and display additions, edits, removals and invalid rows. Make direction and deletion policy explicit; require confirmation when import will discard or overwrite project data.
- Detect concurrent changes with a source revision, content hash or equivalent baseline. Require refresh or an explicit conflict decision instead of silently replacing newer local work.
- On acceptance, begin an editor transaction, call `Modify()` before mutation, apply the complete validated candidate, issue the appropriate change notifications and mark the package dirty. Roll back or leave the table unchanged on failure.
- Report bounded per-row diagnostics with stable keys and column names, plus a complete summary that distinguishes unchanged, changed, skipped and failed rows.

## Don't
- Don't feed an unvalidated remote CSV directly into the live Data Table.
- Don't treat a successful network request as proof that the returned data fits the current row structure.
- Don't normalize provider-specific values opportunistically without recording a deterministic conversion rule.
- Don't mark a package dirty after a partial import while presenting the operation as a complete success.

## Checklist
- Are schema version and stable row identity round-tripped explicitly?
- Can the user see destructive differences and conflicts before committing them?
- Does malformed or stale external data leave the live table unchanged?
- Is a successful import undoable and correctly announced to Unreal editor systems?

## Notes
CSV and spreadsheets are common transports, not the contract. The contract is a deterministic conversion between a versioned external model and an Unreal row structure, with conflict detection and an atomic editor commit.
