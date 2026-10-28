---
object_id: PAT_reuse_database_connections_through_a_pool
object_type: pattern
name: Reuse Database Connections Through a Pool
library_path:
- software-engineering
- core
- performance
stage_binding: 1 skeleton
lane_fit: both
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- database
- connections
- pooling
- resource_management
- performance
cross_links:
- rel: related_to
  target_object_id: PAT_keep_a_spare_before_releasing_capacity
- rel: related_to
  target_object_id: PAT_test_what_happens_when_a_resource_runs_out
reference:
  source_title: Fullstack Rust
  author: Nate Murray
confidence: high
references: []
variants: []
---

# Reuse Database Connections Through a Pool

## Pattern Rule
**IF** a service repeatedly needs database connections and opening a fresh connection for each operation is expensive or can exhaust backend resources
**THEN** keep a shared connection pool for the service lifetime and borrow a reusable connection only for the database work
**ELSE** for rare one-shot database work where connection setup and resource pressure are immaterial, keep the simpler direct connection path

## Do
- Construct the pool at the application or service lifetime boundary and share the pool handle with the work that needs database access.
- Acquire a connection close to the database operation and return it promptly when that operation is finished.
- Treat pool capacity and checkout failure as finite-resource behavior that belongs in the service's error and load policy.
- If the database driver is synchronous inside an asynchronous server, keep the blocking checkout and query work off the asynchronous execution threads.

## Don't
- Don't open a brand-new database connection for every ordinary request when the same backend will be used repeatedly.
- Don't hold a checked-out connection while doing unrelated network, CPU, or user-facing work that does not need the database.
- Don't treat a pool as proof that synchronous database work has become non-blocking.
- Don't substitute one globally shared raw connection for a pool of independently checked-out connections.

## Checklist
- Is connection establishment repeated often enough that reuse removes real setup and resource cost?
- Does the pool live long enough to be reused across operations without becoming accidental global business state?
- Is each connection held only around the database work that requires it?
- What happens when no pooled connection is available or the backend rejects another connection?
- Can blocking database work stall an event loop or asynchronous executor?

## Notes
A connection pool separates connection lifetime from request lifetime. Reusing established connections avoids paying setup on every operation and places a finite acquisition boundary around a backend that cannot accept unlimited concurrent connections; the pool is resource management, not a substitute for query concurrency or asynchronous I/O design.
