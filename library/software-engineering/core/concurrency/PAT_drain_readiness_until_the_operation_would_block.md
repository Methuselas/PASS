---
object_id: PAT_drain_readiness_until_the_operation_would_block
object_type: pattern
name: Drain Readiness Until the Operation Would Block
library_path:
- software-engineering
- core
- concurrency
stage_binding: 2 block
lane_fit: both
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- concurrency
- io
- readiness
- event-loop
- nonblocking
cross_links:
- rel: related_to
  target_object_id: PAT_dispatch_on_readiness_or_on_completion
reference:
  source_title: Network Programming with Rust
  author: Abhishek Chanda
confidence: medium
references: []
variants: []
---

# Drain Readiness Until the Operation Would Block

## Pattern Rule
**IF** a readiness-driven event loop has notified a handler that an operation may make progress and the readiness contract requires the source to be drained
**THEN** repeat the corresponding nonblocking operation until it reports that it would block or is otherwise no longer ready, treating that result as the normal boundary of the readiness episode
**ELSE** when the API is completion-driven or explicitly promises level-triggered redelivery without draining, follow that different contract rather than importing edge-trigger behavior by habit

## Do
- Treat a readiness notification as permission to attempt the operation, not as proof that one particular read, write, or accept must succeed.
- After a readiness event, keep performing the matching nonblocking operation until the API reports that it would block or is otherwise not ready when the contract requires draining.
- Handle a spurious readiness notification by returning to the event loop when the first operation reports that it would block or is otherwise not ready.
- Apply the same drain rule to accept loops as to data reads when a listener readiness API can represent more than one queued connection.

## Don't
- Don't perform exactly one operation per edge/change notification and assume another event will arrive for work that was already ready.
- Don't treat a documented would-block or not-ready result after a readiness event as an exceptional failure when the readiness API defines it as the ordinary retry boundary.
- Don't generalize edge-trigger draining to completion APIs, where the event represents an operation that has already finished.

## Checklist
- Does this API report readiness or completion?
- Can readiness notifications be spurious?
- What result means the source has been drained for now?
- Could work remain ready if the handler performs only one operation?
- Will the event source be re-notified under the documented triggering mode if the handler returns early?

## Notes
Readiness is state, not a one-event/one-operation queue. On edge- or change-driven interfaces, failing to drain the ready state can strand work because no new transition is guaranteed to occur. The exact retry sentinel is API-specific; the decision rule is to follow the readiness contract until the source reports that progress would now block.
