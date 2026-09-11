---
object_id: PAT_check_an_atomic_is_lock_free_before_relying_on_it
object_type: pattern
name: Check an Atomic Is Lock-Free Before Relying on It
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
- lock_free
- portability
cross_links:
- rel: related_to
  target_object_id: PAT_classify_synchronization_by_progress_guarantee
- rel: related_to
  target_object_id: PAT_know_when_two_accesses_are_a_data_race
- rel: related_to
  target_object_id: PAT_choose_the_compare_exchange_form_by_whether_you_loop
- rel: prerequisite_for
  target_object_id: PAT_choose_the_compare_exchange_form_by_whether_you_loop
- rel: prerequisite_for
  target_object_id: PAT_make_shared_pointer_atomicity_a_property_of_the_type
- rel: related_to
  target_object_id: AP_make_shared_state_safe_in_cpp
reference:
  source_title: 'Concurrency with Modern C++: What every professional C++ programmer should know about concurrency'
  author: Rainer Grimm
confidence: high
references: []
variants: []
---

# Check an Atomic Is Lock-Free Before Relying on It

## Pattern Rule
**IF** you are using an atomic type because you intend the code to be lock-free — no thread can be suspended holding the data hostage, or the code runs somewhere a lock is not permitted
**THEN** verify that the type actually is lock-free on your targets rather than assuming it, because the standard permits every atomic type except the atomic flag to be implemented with an internal mutex
**ELSE** where you want atomicity for correctness and have no requirement about how it is achieved, the implementation's choice is its own business and this check is noise.

## Do
- Know which guarantee you actually have. `std::atomic_flag` is guaranteed lock-free; other atomic specializations may or may not be. Common scalar atomics are often lock-free on mainstream targets, but neither popularity nor object size is a portable guarantee.
- Prefer `std::atomic&lt;T&gt;::is_always_lock_free` when the design requires a compile-time guarantee for that specialization on the target implementation. Use `object.is_lock_free()` when the implementation can decide per object or at runtime. Neither result should be extrapolated from one build target to every supported target.
- Check whether a custom `std::atomic&lt;T&gt;` is permitted before asking whether it is lock-free. Under the C++20 floor, `T` must be trivially copyable and meet the required copy/move construction and assignment properties; enforce the properties relevant to a generic interface with constraints or `static_assert` and let the standard-library declaration diagnose unsupported types.
- Keep representation concerns separate from lock-freedom. Padding bits and multiple value representations can affect compare-exchange behavior even for a permitted `T`; they do not create a general rule that an atomic object must be "bitwise comparable."

## Don't
- Don't equate "atomic" with "lock-free". They are different properties: atomicity says the operation is indivisible, lock-freedom says the mechanism achieving that guarantees system-wide progress. An atomic implemented over a mutex is still perfectly atomic.
- Don't rely on a check performed only on your development machine. The runtime query is honest about the machine it runs on and says nothing about the target, which is the platform where the property mattered.
- Don't infer interprocess suitability from `is_lock_free`. Shared-memory layout, process-shared synchronization guarantees, object lifetime, and the platform ABI are separate requirements that the standard atomic query does not establish.

## Checklist
- Does anything here depend on lock-freedom rather than merely on atomicity, and what would break without it?
- Is the check the runtime query or the compile-time constant?
- If a custom type is being made atomic, is the specialization permitted and are its representation constraints understood?
- Do all target architectures answer the same way?

## Notes
The gap this closes is between what the name promises and what the standard guarantees. Reading an atomic type as necessarily lock-free is a reasonable inference from the word and it is not what the specification says, and because the common architectures make it true in practice the mistaken inference survives testing indefinitely.

Where it matters is narrow and worth stating, because otherwise this reads as ceremony. It matters when a thread being suspended mid-operation would be unacceptable — a signal handler, a real-time deadline, code shared between processes through a mapped region — and it matters when the atomic is the whole point of a non-blocking algorithm, since an internal mutex silently converts that algorithm into a locking one with worse performance than an honest lock.

The custom-type restrictions make atomic operations definable over an object's representation, but they do not promise a hardware instruction. An implementation can accept the type and still use a non-lock-free mechanism. Treat eligibility, representation behavior, and progress guarantees as three questions rather than one size-based heuristic.
