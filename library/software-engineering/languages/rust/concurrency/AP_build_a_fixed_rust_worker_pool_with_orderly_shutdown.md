---
object_id: AP_build_a_fixed_rust_worker_pool_with_orderly_shutdown
object_type: ap
name: Build a Fixed Rust Worker Pool with Orderly Shutdown
library_path: [software-engineering, languages, rust, concurrency]
stage_binding: 0 design
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags: [rust, concurrency, thread_pool, channels, shutdown]
cross_links:
- rel: supports
  target_object_id: PAT_do_not_create_a_thread_for_every_task
- rel: supports
  target_object_id: PAT_share_rust_mutable_state_with_arc_and_mutex
- rel: supports
  target_object_id: PAT_end_rust_channel_consumption_by_dropping_every_sender
- rel: supports
  target_object_id: PAT_give_a_spawned_rust_thread_owned_inputs_and_a_join_boundary
- rel: supports
  target_object_id: PAT_plan_the_shutdown_early
- rel: supports
  target_object_id: PAT_lock_the_smallest_region_that_must_be_atomic
- rel: supports
  target_object_id: PAT_choose_rust_closure_bounds_by_capture_and_call_needs
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: high
references: []
variants: []
---

# Build a Fixed Rust Worker Pool with Orderly Shutdown

## Objective
Run independently owned jobs on a fixed set of Rust threads without holding the queue lock during job execution, and make pool teardown stop admission, wake every worker, settle queued-work policy, and join every thread.

## Steps / Flow
1. Confirm that a hand-built pool is warranted. Prefer a maintained executor or pool when production scheduling, observability, cancellation, priorities, panic containment, or adaptive sizing matter.
2. Specify the client contract first: a positive worker count, the accepted job shape, whether submission blocks, rejects, or drops work at capacity, the maximum queued backlog, and whether shutdown drains or abandons accepted jobs.
3. Represent a one-shot owned job as a boxed dynamic `FnOnce` value that is `Send` and owns everything it needs for the worker lifetime.
4. Create the queue and spawn exactly the configured workers. Keep the sending endpoint with the pool; share the standard channel's single receiving endpoint through `Arc` and `Mutex` only when that is the chosen queue design.
5. In each worker, acquire the receiver guard only long enough to wait for and remove one message. Store the receive result in a local so the guard is dropped before invoking the job.
6. Submit by transferring job ownership into the queue. Treat disconnection, blocking backpressure, or capacity refusal according to the public admission contract rather than assuming submission cannot fail.
7. Start shutdown by preventing further admission and closing every sender, or by delivering an explicit control protocol when drain, cancel, and immediate-stop states must differ. Ensure a blocked receiver is guaranteed to wake.
8. After the stop signal is observable by all workers, take and join every worker handle. Provide an explicit shutdown operation that can report worker panics or join failures when callers need recovery; keep any destructor fallback non-panicking or document the process-level consequence of a second panic during unwinding.
9. Test the lifecycle under load: one slow job must not serialize unrelated jobs, queue saturation must follow the declared policy, shutdown must exercise both idle and busy workers, every accepted job must meet the drain policy, and no join may wait on a worker that can no longer receive its stop condition.

## Notes
- A fixed worker count bounds concurrent execution, not queued work. An unbounded channel can still consume unbounded memory under overload; use a bounded admission path or another explicit backpressure mechanism when the backlog must be bounded.
- The receiver mutex protects removal of one message, not execution of the message. Running arbitrary job code while the guard lives serializes the pool and lets a job monopolize admission to every other worker.
- Closing the job channel naturally composes Rust ownership with shutdown when disconnection means drain then stop. An explicit message enum is appropriate only when the protocol needs more states than end of stream.
- Channel closure does not discard jobs already buffered by the standard channel. Workers can drain accepted jobs and then observe disconnection, so a cancel-now contract requires a different queue or an explicit protocol.
