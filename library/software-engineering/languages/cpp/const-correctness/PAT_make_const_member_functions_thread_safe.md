---
object_id: PAT_make_const_member_functions_thread_safe
object_type: pattern
name: Make const Member Functions Thread Safe
library_path:
- software-engineering
- languages
- cpp
- const-correctness
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- cpp
- const_correctness
- concurrency
- threading
- class_design
cross_links:
- rel: related_to
  target_object_id: PAT_use_logical_constness_with_mutable
- rel: related_to
  target_object_id: PAT_put_the_thread_safety_guarantee_at_the_transaction_boundary
- rel: related_to
  target_object_id: PAT_match_the_lock_to_the_length_of_the_critical_section
- rel: related_to
  target_object_id: PAT_verify_an_object_is_as_immutable_as_you_think
- rel: related_to
  target_object_id: AP_make_a_class_const_correct
reference:
  source_title: 'Effective Modern C++: 42 Specific Ways to Improve Your Use of C++11 and C++14'
  author: Scott Meyers
confidence: high
references: []
variants: []
---

# Make const Member Functions Thread Safe

## Pattern Rule
**IF** a member function is declared const but modifies mutable state — a cache, a validity flag, a memoized result
**THEN** either synchronize that state so the type supports concurrent const calls or document that instances require external synchronization, because `const` alone is not a language-level concurrency guarantee
**ELSE** where you are certain the type will never be used from more than one thread, the synchronization is overhead you can decline — and that certainty is part of the type's documented contract, not an assumption.

## Do
- Recognize the shape, because it is a normal and correct design that becomes a data race for free. A function that computes an expensive result, caches it, and returns the cache on later calls is logically a read; the flag and the stored value are `mutable` so it can stay const. Two threads calling it at once are then reading and writing the same memory with no synchronization, which is the definition of a data race.
- Accept that logical constness is not itself the error. Retrieving a cached value may correctly be an observer; what is missing is either internal synchronization or an explicit external-synchronization contract.
- Reach for a mutex first, held for the whole function. It covers the check, the computation, and the store as one operation, which is what the caller needs. The mutex itself is a `mutable` data member, and declaring it so is legitimate — it is implementation detail rather than logical state.
- Use an atomic only where one atomic state and its memory-order contract genuinely express the operation. Do not assume it is cheaper than a mutex without measurement; a cache that consists of an independent flag and value needs a publication protocol or one lock guarding the invariant, not merely two atomic declarations.
- Notice that directly embedding a standard mutex suppresses default copying and moving. Decide whether the enclosing type should remain non-copyable, define value semantics that recreate synchronization state, or move shared state behind an appropriate owner; do not discover the consequence from a distant container error.
- Publish which guarantee the type offers. A type that is safe for concurrent const calls and a type that is not are both legitimate; a caller cannot tell them apart from the interface, so the contract has to say.

## Don't
- Don't assume a const interface means no writes are happening. `mutable` exists precisely so that it can, and a caller reading the declaration has no way to see it.
- Don't guard two related pieces of state with two atomics. Each operation is atomic and the pair is not, so a second thread can observe the flag set before the value is stored — the same non-composition that defeats any sequence of individually safe steps.
- Don't skip the synchronization because the caching is idempotent. Computing the same value twice is harmless; the concurrent read and write of the same memory is undefined behaviour regardless of what the values would have been.
- Don't take an arbitrary type's constness as a promise of thread safety unless its contract says so. Standard-library thread-safety requirements provide specific guarantees for standard objects; user-defined types must publish their own.

## Checklist
- Does this const member function write to any `mutable` member?
- How many distinct locations does it write, and are they guarded as one?
- Could two threads reasonably call this function on the same object at once?
- If a mutex was embedded, are the type's copy and move semantics still explicit and appropriate?
- Does the type's documentation state which concurrency guarantee it offers?

## Notes
What makes this worth a rule of its own is the gap between two separate contracts. Language `const` restricts mutation through an access path while allowing `mutable` implementation state; it says nothing by itself about simultaneous calls. A library can additionally promise that const operations on one object are safe together. Every caching observer has to decide whether to uphold that concurrency promise internally or require the caller to serialize access.

The cost question is real and the answer is usually to pay it. Synchronizing a const function costs on every call including the single-threaded ones, and the alternative is a type whose contract says it must not be shared. Both are defensible; what is not is leaving the question unanswered, because the failure mode is a data race that appears under load in someone else's code.

The atomic-versus-mutex choice looks like a performance decision and is first a correctness one. One atomic object can work when a sentinel or a suitably representable combined state expresses the whole publication. Independent atomics for a value and validity flag require a correct memory-order protocol and still may not express multi-step cache construction cleanly. A mutex is the direct default when the invariant spans ordinary state.
