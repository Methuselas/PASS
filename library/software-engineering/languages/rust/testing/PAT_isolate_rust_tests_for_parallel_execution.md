---
object_id: PAT_isolate_rust_tests_for_parallel_execution
object_type: pattern
name: Isolate Rust Tests for Parallel Execution
library_path: [software-engineering, languages, rust, testing]
stage_binding: 4 final
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: PAT_tests_fail_only_when_code_broken
tags: [rust, testing, concurrency, isolation, cargo]
cross_links:
- rel: related_to
  target_object_id: PAT_use_shared_test_setup_carefully
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: high
references: []
variants: []
---

# Isolate Rust Tests for Parallel Execution

## Pattern Rule
**IF** Rust tests can touch files, environment variables, ports, global state, or another shared resource
**THEN** give each case isolated state and assume test order and overlap are unconstrained.
**ELSE** keep the default parallel harness so independent tests return feedback quickly.

## Do
- Give each test a unique temporary path, resource name, port allocation, or fixture instance rather than sharing one fixed external identifier.
- Reset unavoidable process-wide state and keep the mutation inside a narrowly controlled test boundary.
- Use a single test thread as a diagnostic or explicit fallback when the resource genuinely cannot be partitioned, and record the reason for serialization.
- Disable output capture only when inspecting diagnostics; do not make visible print ordering part of a passing assertion.

## Don't
- Don't let two cases write the same filename or mutate the same environment key and then diagnose the resulting race as a product defect.
- Don't make one test depend on another test running first or leaving state behind.
- Don't serialize the whole suite as the first repair for interference that isolated fixtures could remove.
- Don't infer execution order from one run's interleaved output.

## Checklist
- Can any pair of cases run simultaneously without observing each other's setup or cleanup?
- Are filesystem, environment, network, and global identifiers unique or safely synchronized?
- If the harness is forced to one thread, is the non-partitionable resource and tradeoff explicit?
- Does the test pass independently of output order and neighboring cases?

## Notes
Cargo's test harness normally schedules tests concurrently and captures successful output. Those defaults expose hidden coupling quickly and keep feedback fast. The durable repair is isolation; serial execution is useful when diagnosing interference or when a resource is intrinsically singular, but it should not hide accidental sharing.

