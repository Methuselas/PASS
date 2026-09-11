---
object_id: PAT_specify_a_memory_order_the_operation_can_actually_carry
object_type: pattern
name: Specify a Memory Order the Operation Can Actually Carry
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
- memory_model
- atomics
- avoiding_surprises
cross_links:
- rel: related_to
  target_object_id: PAT_weaken_a_memory_order_only_against_a_measurement
- rel: related_to
  target_object_id: PAT_make_the_acquire_actually_observe_the_release
- rel: related_to
  target_object_id: PAT_choose_the_compare_exchange_form_by_whether_you_loop
- rel: prerequisite_for
  target_object_id: PAT_make_the_acquire_actually_observe_the_release
- rel: prerequisite_for
  target_object_id: PAT_reach_for_a_fence_only_when_no_atomic_carries_the_order
- rel: related_to
  target_object_id: AP_make_shared_state_safe_in_cpp
reference:
  source_title: 'Concurrency with Modern C++: What every professional C++ programmer should know about concurrency'
  author: Rainer Grimm
confidence: high
references: []
variants: []
---

# Specify a Memory Order the Operation Can Actually Carry

## Pattern Rule
**IF** you are naming a memory order on an atomic operation rather than taking the default
**THEN** choose an order permitted for that exact operation and prove the synchronization protocol it participates in, because invalid load/store/failure-order combinations are not a portable downgrade and relaxed atomicity does not publish surrounding data
**ELSE** retain the default sequentially consistent order until a measured need and a reviewed happens-before argument justify weakening it.

## Do
- Classify the operation before annotating it. A load may use relaxed, consume, acquire, or sequentially consistent order; a store may use relaxed, release, or sequentially consistent order; a read-modify-write may also use acquire-release. Prefer acquire over consume under the C++20 baseline unless a reviewed platform-specific dependency protocol requires otherwise.
- For compare-exchange, validate both orders. The failure path is a load, so it may not use release or acquire-release and may not be stronger than the success order under the operation's rules.
- Separate atomicity from synchronization. A relaxed fetch-add still participates in the atomic object's modification order and can allocate distinct counter values without a data race; it does not make ordinary writes in one thread visible to another.
- Draw the release/acquire observation that creates happens-before. A release operation publishes earlier writes only to an acquire operation that reads from the relevant release sequence; merely using the words somewhere in the program is insufficient.
- Use named constants or a wrapper when a protocol repeats, and test the intended outcomes with stress tests and sanitizers while keeping the proof in reviewable documentation. Tests cannot prove a weak-memory protocol, but they can catch broken implementations and surrounding races.

## Don't
- Don't use the consume ordering as a casual optimization. Its dependency rules are difficult to preserve through refactoring and have historically received conservative implementation treatment; acquire is the maintainable C++20 default for publication.
- Don't read relaxed as "slightly synchronized." It preserves atomic modification-order guarantees for that atomic object but creates no inter-thread happens-before relationship for surrounding ordinary data.
- Don't assume an annotation that compiles is valid. Passing release or acquire-release to a load, acquire/consume/acquire-release to a store, or an invalid compare-exchange failure order violates the operation's requirements; do not rely on a diagnostic or a downgrade.

## Checklist
- Is this operation a read, a write, or a read-modify-write?
- Is the named order one that this kind of operation can carry?
- If a load names a releasing order or a store names an acquiring order, has the invalid combination been removed?
- For compare-exchange, is the failure order valid relative to the success order?
- Which acquire reads from which release, and which ordinary accesses does that order?
- Does anything use consume, and is that a deliberate supported-target decision rather than a presumed cheaper acquire?

## Notes
The validity table is the first guardrail. Memory-order parameters share one enumeration, but not every enumerator is permitted for every operation. A compiler may accept the expression syntactically without diagnosing the semantic precondition, so code review must reject invalid combinations before any performance reasoning begins.

The consume ordering is the one place in this area where the honest advice is simply not to use it. Its intent was real: on architectures that track data dependencies in hardware, ordering only the dependent operations is cheaper than a full acquire. What it delivers is a rule about dependency chains that is difficult to reason about, easy to break by refactoring, and that implementations have declined to exploit — so the cost is paid in comprehension and the benefit is not collected.

The independent guarantee on read-modify-writes is easy to lose among the ordering rules and is often the property a counter actually needs. All modifications of one atomic object occupy a single modification order, and a read-modify-write takes its value from the modification immediately preceding it in that order. That supports unique increments even with relaxed order; it does not mean "latest in wall-clock time" or publish unrelated memory.
