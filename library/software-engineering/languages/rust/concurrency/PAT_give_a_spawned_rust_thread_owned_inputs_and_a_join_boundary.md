---
object_id: PAT_give_a_spawned_rust_thread_owned_inputs_and_a_join_boundary
object_type: pattern
name: Give a Spawned Rust Thread Owned Inputs and a Join Boundary
library_path: [software-engineering, languages, rust, concurrency]
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: PAT_plan_the_shutdown_early
tags: [rust, concurrency, threads, ownership, join]
cross_links:
- rel: related_to
  target_object_id: PAT_avoid_sharing_before_you_reach_for_protecting_it
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: high
references: []
variants: []
---

# Give a Spawned Rust Thread Owned Inputs and a Join Boundary

## Pattern Rule
**IF** Rust work must outlive the stack frame that starts it
**THEN** move the work's owned inputs into the spawned closure and keep its `JoinHandle` until the point that requires the work to be complete
**ELSE** keep the work in the current thread when no concurrent lifetime or useful overlap exists.

## Do
- Use a `move` closure when the spawned task needs values from the caller, so the closure owns those values instead of borrowing stack data that may disappear first.
- Treat the `JoinHandle` as the task's completion capability. Store it with the component that is responsible for observing the task's result.
- Call `join` at the latest boundary that must not proceed before the task finishes, so earlier independent work can still overlap.
- Handle the result of `join`; a panic in the spawned thread is returned to the joining thread rather than silently turning into success.
- Design the thread's stop signal and wake-up path before relying on `join` during shutdown.

## Don't
- Don't borrow a local into a thread that may outlive the local's scope.
- Don't call `join` immediately after `spawn` unless sequential execution is intentional; that removes the overlap the thread was created to provide.
- Don't discard a handle when completion, panic observation, or orderly shutdown matters.
- Don't assume dropping a `JoinHandle` stops its thread. Dropping detaches the handle while the thread continues running.

## Checklist
- Which inputs become owned by the spawned closure?
- Who owns the `JoinHandle` after spawning?
- What useful work runs before the join boundary?
- How is a thread panic handled?
- What wakes the task and lets it finish during shutdown?

## Notes
Rust's spawned threads may outlive the function that creates them, so their closure cannot depend on ordinary borrowed locals whose lifetime ends with that function. `move` transfers captured ownership into the closure. `join` is a separate decision: it waits for termination and returns the thread result, which lets the caller place the synchronization boundary after any work that can safely overlap.
