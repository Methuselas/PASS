---
object_id: PAT_write_to_a_shared_stream_through_a_synchronized_wrapper
object_type: pattern
name: Write to a Shared Stream Through a Synchronized Wrapper
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
- streams
- diagnostics
- threading
cross_links:
- rel: related_to
  target_object_id: PAT_know_when_two_accesses_are_a_data_race
- rel: related_to
  target_object_id: PAT_take_the_simplest_lock_type_that_does_the_job
- rel: related_to
  target_object_id: PAT_read_characters_with_a_streambuf_iterator_not_a_formatted_one
reference:
  source_title: 'Concurrency with Modern C++: What every professional C++ programmer should know about concurrency'
  author: Rainer Grimm
confidence: high
references: []
variants: []
---

# Write to a Shared Stream Through a Synchronized Wrapper

## Pattern Rule
**IF** several threads write to the same output stream and you want each thread's message to arrive whole
**THEN** write through C++20 `std::osyncstream` over the destination stream, which accumulates into its own buffer and emits the buffered run without interleaving with other synchronized wrappers on the same stream buffer
**ELSE** where the only concern is that concurrent writes are a data race and the messages are single insertions anyway, a lock around each write is sufficient and adds nothing to learn.

## Do
- Separate data-race safety from message integrity. The synchronized standard streams permit concurrent formatted and unformatted access while synchronized with the C streams, but characters from different threads may interleave. A custom stream object has no blanket permission for concurrent mutation and needs its own synchronization contract.
- See why locking each insertion is not enough for a multi-part message. A line built from several insertions releases the lock between them, so another thread's output lands in the middle — the result is well-defined, correctly synchronized, and unreadable.
- Let the `std::osyncstream` lifetime define the unit that arrives together. Everything buffered through one wrapper is emitted as one non-interleaved run when explicitly emitted or destroyed, so its scope is the message boundary.
- Reach for this in preference to holding a lock across a whole message. Both work; the wrapper does not hold anything while you format, so threads doing expensive formatting do not serialize on each other.

## Don't
- Don't generalize the standard streams' special concurrency guarantee to arbitrary stream objects or to code that has disabled their synchronization. Establish the actual stream and stream-buffer contract.
- Don't build the message with several separately locked writes and expect it to arrive intact. Each write is safe and the message is not, which is the failure that survives a careless fix and looks fixed.
- Don't assume this makes the stream shareable for everything. It arranges for output to arrive in whole runs; it says nothing about a stream's state, its formatting flags, or anything else two threads might both be adjusting.

## Checklist
- Do several threads write to this stream?
- Is any message built from more than one insertion?
- Does the wrapper's scope match the run of output that must stay together?
- Are all writers that require non-interleaving using synchronized wrappers over the same destination stream buffer?
- Is anything else about the stream — flags, precision, width — being set from more than one thread?

## Notes
The distinction between data-race freedom and non-interleaving is what makes this worth a decision rather than a lookup. Standard synchronized output can be race-free yet still mix characters from different threads. A mutex per insertion has the same message-level defect. `std::osyncstream` supplies a C++20 message buffer whose emission is coordinated with other synchronized wrappers targeting the same stream buffer.

Framing the wrapper's lifetime as the unit of atomicity is the useful way to hold it. You are not locking anything and then unlocking it; you are declaring a buffer whose contents transfer as one piece at a known moment. That makes the scope of the object the thing to get right, and it is visible in the code in a way that the extent of a held lock often is not.

Diagnostic output from concurrent code is where this matters most, and it is also where the temptation to skip it is strongest, because the output is "only for debugging". Interleaved diagnostics from a concurrency bug are actively misleading about the order things happened in, which is precisely the question being investigated.
