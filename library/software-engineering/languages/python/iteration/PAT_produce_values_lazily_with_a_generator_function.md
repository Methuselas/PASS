---
object_id: PAT_produce_values_lazily_with_a_generator_function
object_type: pattern
name: Produce Values Lazily with a Generator Function
library_path:
- software-engineering
- languages
- python
- iteration
stage_binding: 2 block
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- python
- iteration
- generators
- yield
cross_links:
- rel: related_to
  target_object_id: PAT_know_whether_an_iterable_supports_multiple_passes_before_reusing_it
- rel: related_to
  target_object_id: PAT_choose_where_function_state_lives
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Produce Values Lazily with a Generator Function

## Pattern Rule
**IF** a function must produce a series of values, and building the whole series first would cost too much memory, delay the first result too long, or be outright impossible because the series is unbounded or astronomically large
**THEN** write it as a generator function — a `def` whose body yields each value instead of appending to a list and returning it — so each result is produced on request while the function's position and local state are kept between resumptions
**ELSE** when the series is small, already in memory, and the caller will consume all of it anyway, return a plain list; it reads more simply, can be scanned repeatedly, and is usually produced just as fast

## Do
- Convert the accumulate-and-return shape directly: wherever the list-building version appended, yield instead, and delete both the result list and the final return.
- Expect the call itself to run none of the body; nothing executes until a value is requested, and each request resumes the function immediately after the `yield` that last ran.
- End the series by letting the function finish normally or by using a bare `return`; the iteration protocol turns that exit into the signal that no values remain.
- Delegate part of the series to another generator or iterable with `yield from`, rather than writing a forwarding loop that yields its items one at a time.
- Rely on local variables surviving between resumptions: a suspended generator keeps its entire local scope, which is what removes the need to save progress by hand.

## Don't
- Don't expect a generator to be rescannable; it is its own iterator and supports one pass, so a second loop over the same object yields nothing and a rescan requires a freshly created generator.
- Don't use `return value` in a generator expecting the caller to receive it as the call's result; a return there ends the series rather than handing anything back through the iteration.
- Don't convert a small list-returning helper into a generator on principle; laziness pays only when the caller can act on early results before the series finishes, or when the whole series would not fit in memory.
- Don't treat a generator as per-call state: it holds the state of one suspended run, not an independent copy for each call the way a closure or an instance does.

## Checklist
- Would the caller benefit from the first result before the last one exists?
- Could the complete series be too large to hold, or unbounded?
- Does any code scan these results more than once, and if so does it build a fresh generator or keep a list?
- Is a forwarding loop over another iterable doing what `yield from` would state directly?

## Notes
State suspension is the whole mechanism: a function containing `yield` is compiled into something that returns a generator object, and that object remembers both the next statement to run and every local variable, which is why the series can be produced across many separate requests without the function hand-rolling a record of its progress.

The strongest case for this is a result set that cannot be built at all. Permutations of a fifty-item sequence are a number with sixty-odd digits; a list-builder cannot finish at any speed or fit the result, while a generator hands back the first ordering immediately and each subsequent one on request. Where the series is merely large rather than impossible, the gain is narrower — memory, and time to first result — and must be weighed against the fact that a list is the simpler object to hand to someone else.
