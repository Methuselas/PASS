---
object_id: PAT_share_rust_mutable_state_with_arc_and_mutex
object_type: pattern
name: Share Rust Mutable State With Arc and Mutex
library_path: [software-engineering, languages, rust, concurrency]
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: PAT_lock_the_smallest_region_that_must_be_atomic
tags: [rust, concurrency, arc, mutex, shared_state]
cross_links:
- rel: related_to
  target_object_id: PAT_avoid_sharing_before_you_reach_for_protecting_it
- rel: related_to
  target_object_id: PAT_end_a_rust_resource_guard_with_scope_or_drop
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: high
references: []
variants: []
---

# Share Rust Mutable State With Arc and Mutex

## Pattern Rule
**IF** multiple Rust threads must own access to one mutable value and the sharing cannot be removed
**THEN** put the value behind `Arc&lt;Mutex&lt;T&gt;&gt;`, clone the `Arc` for each owner, and keep every `MutexGuard` scoped to the smallest atomic operation
**ELSE** move independent values to their worker or send messages to a single owner instead of introducing shared mutable state.

## Do
- Use `Arc` for shared ownership across threads and `Mutex` for exclusive mutable access; each type supplies a different half of the contract.
- Clone the `Arc`, not the protected value, before moving an owner into a spawned thread.
- Acquire the lock only immediately before the operation that must be atomic.
- Read or mutate through the returned guard, then end the guard's scope before blocking, joining, sending through a bounded path, or doing unrelated long work.
- Decide how the application handles lock poisoning instead of assuming acquisition cannot fail after another thread panics while holding the lock.

## Don't
- Don't use `Rc&lt;Mutex&lt;T&gt;&gt;` across threads; `Rc` does not provide thread-safe reference-count updates and is not `Send`.
- Don't hold a guard longer because the protected value is still in lexical scope; the guard, not the `Arc`, controls the lock interval.
- Don't wrap a value in a mutex before asking whether ownership transfer or partitioning can remove the sharing.
- Don't infer freedom from deadlock from Rust's memory-safety checks. Multiple locks can still be acquired in a cycle.

## Checklist
- Is the state inherently shared, or can one thread own it?
- Does every spawned owner receive an `Arc` clone?
- What exact operation must be atomic?
- Where is the guard dropped?
- What is the poisoning policy?
- Can any path hold one guard while acquiring another or waiting for a peer?

## Notes
`Arc` makes the ownership count safe to update across threads; it does not make the contained value mutable or synchronized. `Mutex` serializes access and returns an RAII guard that unlocks when dropped. Their composition is useful precisely because the responsibilities remain separate. It prevents data races when its trait bounds are met, but it does not prevent deadlock, excessive contention, or a shutdown protocol that waits while still holding a guard.
