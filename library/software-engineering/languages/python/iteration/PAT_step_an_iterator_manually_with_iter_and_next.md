---
object_id: PAT_step_an_iterator_manually_with_iter_and_next
object_type: pattern
name: Step an Iterator Manually with iter() and next()
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
- iterator-protocol
cross_links: []
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Step an Iterator Manually with iter() and next()

## Pattern Rule
**IF** a `for` loop can't express the needed control flow directly — advancing one iterator from inside logic that also does something else, peeking ahead without committing, or driving two independent iterators at different rates
**THEN** get an iterator explicitly with `iter(obj)`, then advance it with `next(iterator)`, catching `StopIteration` (or passing a default, `next(iterator, default)`, to get a sentinel back instead of an exception)
**ELSE** when a plain left-to-right scan is all that's needed, use a `for` loop instead; it already does exactly this internally, with less code

## Do
- Call `iter(obj)` once to get the iterator, then call `next()` on that same iterator object repeatedly — not `next(obj)` again, which would restart iteration on objects that return a fresh iterator each time `iter()` is called.
- Catch `StopIteration` with `try`/`except` when the loop needs to do something special at exhaustion, mirroring what a `for` loop's internal machinery already does automatically.
- Prefer `next(iterator, default)`'s two-argument form over a `try`/`except` when a sentinel value is an acceptable stand-in for "no more items," since it avoids exception-handling machinery for an expected, ordinary condition.
- Check whether an object is its own iterator before assuming a separate `iter()` step is needed: `iter(f) is f` is `True` for an open file, so calling its iteration method directly works — but this isn't guaranteed for every iterable, since a list is not its own iterator.

## Don't
- Don't call an object's iteration method directly in new code merely because it has been demonstrated that way; the `next(object)` built-in is the idiomatic, version-neutral spelling and does the same thing.
- Don't assume every iterable responds to `next()` directly; a `list`, `dict`, or `range` is iterable but is not itself an iterator — call `iter()` first to get the object that actually advances.
- Don't keep calling `next()` on an exhausted iterator without catching `StopIteration` or supplying a default; the exception is the signal that iteration is complete, not an incidental error to work around.

## Checklist
- Does the code call `iter()` once and reuse the resulting iterator, rather than re-fetching a new iterator on every step?
- Is `StopIteration` either caught or avoided with `next(iterator, default)`, rather than left to propagate unexpectedly?
- Would a plain `for` loop already express this control flow, making the manual version unnecessary?

## Notes
This manual sequence — `iter()` then repeated `next()` until `StopIteration` — is exactly what every `for` loop, comprehension, and other left-to-right scanning tool in Python performs automatically and invisibly. Writing it out by hand only pays off when something about the control flow doesn't fit the shape a `for` loop provides.
