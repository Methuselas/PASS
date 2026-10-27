---
object_id: PAT_make_rust_future_poll_return_pending_instead_of_blocking
object_type: pattern
name: Make Rust Future Poll Return Pending Instead of Blocking
library_path:
- software-engineering
- languages
- rust
- concurrency
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: PAT_dispatch_on_readiness_or_on_completion
tags:
- rust
- async
- future
- poll
- waker
- concurrency
cross_links:
- rel: related_to
  target_object_id: PAT_do_not_create_a_thread_for_every_task
- rel: related_to
  target_object_id: PAT_block_with_a_deadline_before_polling_on_an_interval
reference:
  source_title: Network Programming with Rust
  author: Abhishek Chanda
confidence: high
references: []
variants: []
---

# Make Rust Future Poll Return Pending Instead of Blocking

## Pattern Rule
**IF** you implement a Rust Future or another executor-polled primitive and the operation cannot make further progress now
**THEN** return Poll::Pending promptly and ensure the current task can be woken when progress may be possible
**ELSE** when progress is immediately available, make it and return the resulting poll state; when the operation itself is inherently blocking or long-running, move that work to an execution context that permits blocking and bridge its completion back to the async task

## Do
- Treat poll as a bounded progress check: perform immediately available work and return rather than waiting for external progress.
- When returning Poll::Pending, retain or register the current Context/Waker as required by the resource so a later state change can schedule another poll.
- Replace a stored waker when a later poll supplies the task context that should receive the next wakeup.
- Move blocking system calls, sleeps, and long CPU-bound work to a blocking-capable worker or runtime facility instead of performing them inside poll.

## Don't
- Don't sleep, perform an unbounded blocking call, or wait for a contended blocking lock inside poll; that stalls an executor thread and unrelated tasks scheduled on it.
- Don't return Poll::Pending without a path that can wake the task when the blocked condition changes.
- Don't assume creating a Future creates a system thread; a future makes progress only when an executor polls it.

## Checklist
- Can this poll invocation return promptly even when the operation is not ready?
- If it returns Poll::Pending, what event will trigger a wakeup?
- Is the stored waker kept current with the most recent relevant poll context?
- Has inherently blocking or long-running work been moved out of the executor-polled path?

## Notes
Rust async executors rely on cooperative polling. Poll::Pending is not a request for the executor thread to wait; it means this task has no progress to make now and has arranged to be scheduled again when the condition changes.
