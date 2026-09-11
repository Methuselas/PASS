---
object_id: PAT_make_shared_pointer_atomicity_a_property_of_the_type
object_type: pattern
name: Make Shared-Pointer Atomicity a Property of the Type
library_path:
- software-engineering
- languages
- cpp
- concurrency
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- cpp
- concurrency
- atomics
- smart_pointers
- api_design
cross_links:
- rel: related_to
  target_object_id: PAT_price_shared_ownership_before_choosing_it
- rel: related_to
  target_object_id: PAT_publish_shared_data_through_one_atomic_handle
- rel: related_to
  target_object_id: PAT_know_when_two_accesses_are_a_data_race
- rel: related_to
  target_object_id: AP_make_shared_state_safe_in_cpp
reference:
  source_title: 'Concurrency with Modern C++: What every professional C++ programmer should know about concurrency'
  author: Rainer Grimm
confidence: high
references: []
variants: []
---

# Make Shared-Pointer Atomicity a Property of the Type

## Pattern Rule
**IF** several threads will write to the same shared-pointer object — not merely share the pointee, but assign to or reset the same handle
**THEN** declare that handle as an atomic shared pointer, so the type system requires every access to be atomic, rather than relying on everyone remembering to route accesses through free atomic functions
**ELSE** where each thread holds its own copy of the handle, the reference-counting machinery is already thread-safe and nothing further is needed.

## Do
- Separate the guarantees the plain type gives you. Operations on distinct shared-pointer objects that share ownership do not race solely on their common control block; the implementation synchronizes that bookkeeping. The pointee is not thereby protected, and neither is one non-atomic handle object that two threads both modify.
- Read the two derived rules straight off that split. Multiple threads may read one handle simultaneously; multiple threads may write to *different* handles simultaneously even when those handles share a control block. Neither permits two threads writing to the same handle.
- Let the type carry the requirement. Assignment to `std::atomic&lt;std::shared_ptr&lt;T&gt;&gt;` is itself an atomic store, and reads use its conversion or load operation, so ordinary-looking access cannot silently bypass the handle's synchronization.
- Measure rather than assuming the atomic specialization is cheaper than a mutex. An implementation may use locks internally, and the surrounding operation may still need a larger critical section than one pointer load or store can provide.
- Ask the object whether it is lock-free before building anything on that property. The specialization may use locks, and even a lock-free pointer update does not make a larger pointee operation or reclamation protocol lock-free.

## Don't
- Don't rely on the free atomic functions. They were the only mechanism available for a long time, they are deprecated, and their defect is structural: nothing distinguishes a correct atomic store from a plain assignment at the point of use, so a single forgotten call is a data race that compiles cleanly and reviews cleanly.
- Don't conclude from the thread-safe control block that the handle is thread-safe. That inference is what makes the plain type look usable here, and it is exactly wrong about the case where two threads assign to one handle.
- Don't reach for shared ownership *because* of thread safety. What the reference counting buys is a guarantee about destruction, not about concurrent mutation, and the cost of the counting is real whether or not you needed it.

## Checklist
- Do two threads write to the same handle object, or do they each hold their own copy?
- If they share one handle, is its type atomic?
- Is every concurrently shared handle access performed through the atomic object's load, store, exchange, compare-exchange, or atomic assignment/conversion interface?
- Is the pointee itself mutated concurrently, which this addresses not at all?

## Notes
The general principle here is worth more than the specific facility, and the proposal that introduced it argues it explicitly: of the three benefits claimed — consistency, correctness, and performance — correctness is the decisive one, because it moves a requirement from discipline into the type system. A rule that must be remembered at every use site will eventually not be, and the failure is silent.

The oddity being corrected is worth noticing too. The shared pointer was the only non-atomic type in the library with atomic operations defined on it, which is precisely the shape that invites the mistake: the operations exist, they look optional, and using the ordinary syntax instead produces undefined behaviour rather than a diagnostic.

None of this touches the pointee. A handle that is safe to assign from several threads still points at an object those threads can corrupt freely, and the guidance about not sharing mutable data applies there unchanged.
