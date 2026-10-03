---
object_id: PAT_read_send_and_sync_as_rust_thread_boundary_contracts
object_type: pattern
name: Read Send and Sync as Rust Thread-Boundary Contracts
library_path: [software-engineering, languages, rust, concurrency]
stage_binding: 1 skeleton
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: PAT_define_your_code_contract_explicitly
tags: [rust, concurrency, send, sync, traits]
cross_links:
- rel: related_to
  target_object_id: PAT_share_rust_mutable_state_with_arc_and_mutex
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: high
references: []
variants: []
---

# Read Send and Sync as Rust Thread-Boundary Contracts

## Pattern Rule
**IF** a Rust type crosses a thread boundary or is referenced concurrently
**THEN** require `Send` for moving ownership across the boundary and `Sync` for sharing references across it, then let those auto-trait requirements propagate through every field and wrapper
**ELSE** keep the type confined to one thread and expose no API that promises cross-thread use.

## Do
- Read `T: Send` as permission to transfer ownership of a `T` to another thread.
- Read `T: Sync` as permission for multiple threads to hold shared references to the same `T`; equivalently, a shared reference to `T` can be sent when `T` is `Sync`.
- Inspect the first field or wrapper that prevents an aggregate from satisfying the required auto trait, because most types receive `Send` and `Sync` automatically from their components.
- Choose thread-aware building blocks when the API promises cross-thread use: for example, `Arc` rather than `Rc`, and synchronized interior mutability rather than `RefCell` for shared concurrent access.
- Put the required bounds on generic thread-facing APIs so misuse fails at the boundary with a local diagnostic.

## Don't
- Don't read `Send` as permission for simultaneous shared access; that is the role of `Sync` and the types that provide synchronization.
- Don't assume a type is thread-safe because its methods take `&self`; interior mutability can make shared access unsynchronized.
- Don't add a manual `unsafe impl Send` or `unsafe impl Sync` merely to silence a compiler error. The implementation asserts a safety property the compiler could not prove.
- Don't replace `Rc` or `RefCell` mechanically without deciding whether the design needs transfer, shared access, or single-thread confinement.

## Checklist
- Is the value moved to another thread, shared by reference, or both?
- Which bound does the public API actually need: `Send`, `Sync`, or both?
- Which component determines the aggregate's auto-trait result?
- Does any interior mutability synchronize concurrent access?
- If an unsafe manual implementation exists, where is its safety argument and how is it tested?

## Notes
`Send` and `Sync` are marker traits used by Rust's type system to reject unsafe thread boundaries. They are usually auto traits: a composite type gains or loses them according to its components. This makes wrappers part of the contract. `Rc` is neither `Send` nor `Sync`; `RefCell&lt;T&gt;` can be moved when `T` permits it but is not `Sync`, because its runtime borrow state is not safe for concurrent shared access. Manual implementations are unsafe because incorrect claims can permit data races or other undefined behavior in otherwise safe callers.
