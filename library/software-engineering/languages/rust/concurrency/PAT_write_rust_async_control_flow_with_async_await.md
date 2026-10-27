---
object_id: PAT_write_rust_async_control_flow_with_async_await
object_type: pattern
name: Write Rust Async Control Flow With async/await
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
- await
- future
- concurrency
- control-flow
cross_links:
- rel: related_to
  target_object_id: PAT_make_rust_future_poll_return_pending_instead_of_blocking
- rel: related_to
  target_object_id: PAT_keep_rust_failures_as_result_until_recovery_context_exists
reference:
  source_title: Network Programming with Rust
  author: Abhishek Chanda
confidence: high
references: []
variants: []
---

# Write Rust Async Control Flow With async/await

## Pattern Rule
**IF** a Rust operation must wait on futures while preserving ordinary sequential or branching control flow
**THEN** express the orchestration with async fn or an async block and use .await where a future result is required so the task can suspend and later resume without blocking the executor thread
**ELSE** use ordinary synchronous control flow when there is no useful asynchronous suspension boundary; if the operation itself is blocking or long-running, move that work to an execution context that permits blocking instead of wrapping it in async syntax

## Do
- Use async fn when the function itself is the asynchronous operation, and use an async block when a local Future value is the clearer boundary.
- Place .await at the dependency point where the next step needs a Future's output; treat suspension there as task suspension, not as a blocking wait on the executor thread.
- When the async operation returns Result, use normal Rust control flow and ? to propagate recoverable failures through the Future until a layer with recovery context handles them.
- Keep blocking system calls, sleeps, and long CPU-bound work out of the async execution path unless they are moved to a blocking-capable worker or runtime facility.

## Don't
- Don't use legacy `#[async]`/`await!` macro-style syntax in new Rust code when native `async`/`.await` expresses the operation.
- Don't assume calling an async fn immediately performs its body; the call produces a Future that makes progress when polled.
- Don't assume async syntax makes a synchronous blocking operation nonblocking.

## Checklist
- Where are the actual asynchronous dependency points that require .await?
- Does the async body preserve Result/error information until an appropriate recovery boundary?
- Could any call in the async path block the executor thread or run CPU work for too long without yielding?
- Would synchronous code be simpler because this operation has no useful suspension boundary?

## Notes
In current Rust, calling an `async fn` or evaluating an async block produces a Future, and `.await` suspends the current async context until the awaited Future can complete. This is source-level composition over the same cooperative Future polling model: it improves control-flow expression, but it does not create a thread or make blocking work safe inside the executor.
