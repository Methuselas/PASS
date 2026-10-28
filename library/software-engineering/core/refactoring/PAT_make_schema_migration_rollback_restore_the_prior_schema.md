---
object_id: PAT_make_schema_migration_rollback_restore_the_prior_schema
object_type: pattern
name: Make a Schema Migration Rollback Restore the Prior Schema
library_path:
- software-engineering
- core
- refactoring
stage_binding: 4 final
lane_fit: both
foundation_role: specialization
routing_class: general
specialization_axis: none
foundation_object_id: PAT_make_every_milestone_a_place_you_could_stop
tags:
- database
- schema
- migration
- rollback
- deployment
cross_links: []
reference:
  source_title: Fullstack Rust
  author: Nate Murray
confidence: high
references: []
variants: []
---

# Make a Schema Migration Rollback Restore the Prior Schema

## Pattern Rule
**IF** a database migration is declared reversible and ships an explicit rollback operation
**THEN** design and test the rollback so applying the migration and then reverting it restores the prior schema contract, while documenting any data loss or irreversible transformation separately

## Do
- Define the forward and rollback operations as a pair during the same change.
- Test the pair against the real database backend, including constraints and indexes that are easy to omit.
- Distinguish schema reversibility from data reversibility; restoring a table shape does not recreate deleted or transformed data.
- Mark migrations irreversible when a truthful rollback cannot reconstruct the prior contract instead of supplying a misleading placeholder.

## Don't
- Don't call a migration reversible because the rollback command exits successfully.
- Don't assume DDL is portable across database backends.
- Don't hide destructive data loss behind a nominal schema rollback.
- Don't postpone rollback design until an incident requires it.

## Checklist
- What exact schema state exists before the migration?
- Does forward-then-rollback reproduce that state on the supported backend?
- What data transformations cannot be undone?
- Is operational policy prepared for an explicitly irreversible migration?

## Notes
Reversibility is a property to verify, not a filename convention. For migrations that intentionally support rollback, the useful invariant is restoration of the prior schema contract; data restoration has to be evaluated separately.
