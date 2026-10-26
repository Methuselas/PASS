---
object_id: PAT_choose_rust_thread_spawn_api_by_configuration_and_failure_contract
object_type: pattern
name: Choose the Rust Thread Spawn API by Configuration and Failure Contract
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
foundation_object_id: none
tags:
- rust
- concurrency
- threads
- builder
- error-handling
cross_links:
- rel: related_to
  target_object_id: PAT_give_a_spawned_rust_thread_owned_inputs_and_a_join_boundary
confidence: medium
references: []
variants: []
---

# Choose the Rust Thread Spawn API by Configuration and Failure Contract

## Pattern Rule
**IF** a Rust program is about to create a native thread and the launch contract may need a thread name, a nondefault stack size, or recoverable handling of thread-creation failure
**THEN** use `std::thread::Builder`, configure only the required launch properties, and handle `Builder::spawn`'s `io::Result` before managing the returned `JoinHandle`
**ELSE** use `std::thread::spawn` for the default configuration when failure to create the operating-system thread may remain a panic

## Do
- Use `thread::spawn` when the default thread configuration and panic-on-launch-failure behavior match the program's contract.
- Use `thread::Builder` when the thread needs an explicit diagnostic name or stack size, or when the caller must handle operating-system thread-creation failure as an `io::Result`.
- Treat successful creation and successful completion as separate boundaries: first handle `Builder::spawn`, then retain and eventually inspect the `JoinHandle` according to the thread's lifecycle contract.
- Treat a requested stack size as a requested minimum policy rather than an exact portable allocation; the platform may impose a larger minimum.

## Don't
- Do not call `unwrap` on `Builder::spawn` when recoverable launch failure was the reason for choosing Builder.
- Do not confuse an `io::Error` returned while creating the thread with a panic returned later by `JoinHandle::join`; they occur at different lifecycle boundaries.
- Do not choose `Builder` merely because a thread exists; the free `spawn` function already uses `Builder`'s default configuration.

## Checklist
- Does this thread need a name or nondefault stack size?
- Must the caller recover if the operating system refuses to create the thread?
- After creation succeeds, who owns the `JoinHandle` and where is completion observed?
- Is the requested stack size portable enough for every supported target?

## Notes
In Rust 1.98.1, `thread::spawn` is the convenience path: it uses `Builder` with default configuration and panics if the operating system cannot create the thread. `Builder::spawn` exposes that creation failure as `io::Result` and also supplies the stable name and stack-size configuration points. This decision is about thread creation; ownership, shutdown, and panic observation remain properties of the returned `JoinHandle` lifecycle.
