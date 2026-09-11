---
object_id: PAT_reach_for_a_fence_only_when_no_atomic_carries_the_order
object_type: pattern
name: Reach for a Fence Only When No Atomic Carries the Order
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
- performance
cross_links:
- rel: related_to
  target_object_id: PAT_specify_a_memory_order_the_operation_can_actually_carry
- rel: related_to
  target_object_id: PAT_make_the_acquire_actually_observe_the_release
- rel: related_to
  target_object_id: PAT_weaken_a_memory_order_only_against_a_measurement
reference:
  source_title: 'Concurrency with Modern C++: What every professional C++ programmer should know about concurrency'
  author: Rainer Grimm
confidence: medium
references: []
variants: []
---

# Reach for a Fence Only When No Atomic Carries the Order

## Pattern Rule
**IF** you need to stop memory operations being reordered across a point in the code
**THEN** first express the synchronization on the atomic load, store, or read-modify-write that communicates between threads; use `std::atomic_thread_fence` only when a reviewed fence–atomic protocol creates the required synchronizes-with edge
**ELSE** where only compiler reordering between a thread and an allowed signal-handler interaction is at issue, evaluate `std::atomic_signal_fence` under the signal-safety contract rather than treating it as inter-thread synchronization.

## Do
- Name the standard synchronization shape before writing a fence: release fence followed by a communicating atomic write and an acquiring read; releasing write followed by a communicating atomic read and an acquire fence; or release fence and acquire fence connected by an atomic write/read pair. In every case, an atomic object's modification order and a reads-from relation carry the inter-thread link.
- Place ordinary accesses on the sequenced-before/after sides required by that shape. The fence does not make those accesses atomic; it makes them ordered only when the full synchronization chain exists.
- Prefer acquire/release directly on the communicating atomic when it expresses the same protocol. It is easier to review because the ordering and communication occur on one operation.
- Treat sequentially consistent fences as participation in the global sequentially consistent order, not as a portable spelling for one processor's "full barrier" instruction.
- Verify the protocol against the language model first, then inspect generated code and measure on supported targets if a fence is proposed for performance. Instruction selection and cost are implementation and architecture properties.

## Don't
- Don't use a fence by itself and expect threads to synchronize. Without the required communicating atomic operations and observation relationship, two fences are merely two unrelated events.
- Don't reason from a memorized load/store reordering matrix such as "a full fence blocks every pair except store-load." Such tables describe particular hardware or compiler mappings, not the portable C++ fence contract.
- Don't expect the signal fence to synchronize threads. It orders a thread against a handler executing on that same thread, which is a compiler-level constraint rather than an inter-processor one, and using it between threads orders nothing.
- Don't place a relaxed atomic beside a fence and assume the pair is automatically acquire or release. The exact sequenced-before relation and the value read from the communicating atomic determine whether a standard fence synchronization rule applies.

## Checklist
- Is there already a communicating atomic operation that can carry acquire or release directly?
- Which standard fence–atomic synchronization shape is being used?
- Which atomic write is read by which atomic read, and how is that established?
- Which ordinary accesses are sequenced before the release side and after the acquire side?
- Is the fence a thread fence or a signal fence, and does that match what is being ordered?

## Notes
The distinction that makes this a decision rather than a style preference is where communication and ordering are expressed. An acquiring load both observes an atomic value and can carry acquire semantics. An acquire fence has no value to observe, so a surrounding atomic read must connect it to the release side under one of the standard rules. That separation can enable specialized protocols, but it also makes review easier to get wrong.

That said, the confidence on this card is deliberately lower than its neighbours. The precise guarantees fences give — and how they interact with atomic operations of various orders — are among the subtlest parts of the memory model, and Grimm himself notes that a great deal of effort goes into getting the acquire and release fence definitions and their consequences right. Treat the summary above as orientation and check the standard before writing one.

The signal fence is easy to overlook and easy to misuse. It is a compiler-ordering facility for interactions with a signal handler on the same thread; it neither creates inter-thread synchronization nor broadens what a signal handler may safely do. Keep it out of ordinary thread protocols.
