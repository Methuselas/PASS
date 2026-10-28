---
object_id: PAT_enforce_relational_references_with_database_foreign_keys
object_type: pattern
name: Enforce Relational References with Database Foreign Keys
library_path:
- software-engineering
- core
- contracts
stage_binding: 1 skeleton
lane_fit: both
foundation_role: specialization
routing_class: general
specialization_axis: none
foundation_object_id: PAT_enforce_contracts_at_runtime_with_checks
tags:
- database
- foreign-keys
- referential-integrity
- constraints
cross_links:
- rel: related_to
  target_object_id: PAT_enforce_cross_request_uniqueness_with_a_database_constraint
reference:
  source_title: Fullstack Rust
  author: Nate Murray
confidence: high
references: []
variants: []
---

# Enforce Relational References with Database Foreign Keys

## Pattern Rule
**IF** a persisted row references another persisted row and dangling references are invalid
**THEN** declare the relationship as a database foreign-key constraint so every writer shares one referential-integrity boundary
**ELSE** omit the constraint only when dangling or externally-resolved identifiers are an intentional part of the data model

## Do
- Declare the foreign key in the schema migration that introduces the relationship.
- Verify that foreign-key enforcement is actually active in every deployed database and connection configuration; a declared constraint is not protection if the engine or connection is configured not to enforce it.
- Choose delete and update behavior deliberately rather than relying on an accidental database default.
- Map constraint violations to the service's domain error policy instead of treating them as impossible.
- Keep application-side existence checks only when they improve diagnostics or authorization; let the database remain authoritative for referential integrity.
- Test insertion and mutation paths against missing or removed parents, including the selected delete behavior.

## Don't
- Don't rely on a read-before-write existence check as the only protection against dangling references.
- Don't assume one application process is the only writer to the database.
- Don't assume that successfully declaring a foreign key means the deployed database is enforcing it; verify the engine and connection setting.
- Don't add cascade behavior without confirming that deleting a parent is allowed to delete or rewrite its dependents.
- Don't duplicate the relationship solely in ORM metadata while leaving the storage schema unenforced.

## Checklist
- Is a missing referenced row invalid at commit time?
- Which columns form the relationship?
- Is foreign-key enforcement enabled and verifiably active on every connection/environment that can write this data?
- What should happen when the parent is updated or deleted?
- Can every writer to this database be trusted to perform the same application-side precheck?
- Do tests prove the database rejects an invalid reference?

## Notes
A foreign key places referential integrity at the storage boundary shared by all writers only when the database actually enforces the declared constraint. ORM association metadata can improve query ergonomics, but it does not substitute for an enforced database constraint when dangling references are invalid; deployment and connection configuration are therefore part of the contract.
