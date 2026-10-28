---
object_id: PAT_enforce_cross_request_uniqueness_with_a_database_constraint
object_type: pattern
name: Enforce Cross-Request Uniqueness with a Database Constraint
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
- constraints
- uniqueness
- concurrency
- integrity
cross_links:
- rel: related_to
  target_object_id: PAT_assume_calls_can_overlap_and_arrive_in_any_order
reference:
  source_title: Fullstack Rust
  author: Nate Murray
confidence: high
references: []
variants: []
---

# Enforce Cross-Request Uniqueness with a Database Constraint

## Pattern Rule
**IF** one persisted value must be unique across requests, workers, processes, or other concurrent writers
**THEN** make the database uniqueness constraint the authoritative invariant and treat any application-side precheck only as an optional user-experience optimization

## Do
- Declare the unique key or index in the schema migration that introduces the invariant.
- Handle the database constraint violation as an expected domain conflict and map it to the caller-facing error policy.
- Keep any friendly availability check non-authoritative because another writer can win between the check and insert.
- Exercise the invariant with competing or repeated writes rather than testing only the happy path.

## Don't
- Don't enforce shared uniqueness only with read-then-write application code.
- Don't assume one server process or one worker is the only writer unless that is itself an enforced system invariant.
- Don't turn every database failure into a uniqueness error; classify the specific constraint violation.
- Don't remove or weaken the database constraint merely because validation also exists in the UI or service layer.

## Checklist
- Where can concurrent writes to this data originate?
- Which exact columns or expression define uniqueness?
- How is the constraint violation represented to the caller?
- Does a test prove that duplicate concurrent writes cannot both commit?

## Notes
A database uniqueness constraint places the invariant at the serialization point shared by all writers. Application validation can improve feedback, but it cannot close a race that the storage boundary still permits.
