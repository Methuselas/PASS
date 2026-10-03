---
object_id: PAT_make_a_class_iterable_and_decide_how_many_scans_it_supports
object_type: pattern
name: Make a Class Iterable and Decide How Many Scans It Supports
library_path:
- software-engineering
- languages
- python
- classes
stage_binding: 2 block
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- python
- classes
- iteration
- protocols
cross_links:
- rel: related_to
  target_object_id: PAT_know_whether_an_iterable_supports_multiple_passes_before_reusing_it
- rel: related_to
  target_object_id: PAT_produce_values_lazily_with_a_generator_function
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Make a Class Iterable and Decide How Many Scans It Supports

## Pattern Rule
**IF** instances of a class should work in `for` loops, comprehensions, `in` tests, and the other iteration contexts
**THEN** give the class an `__iter__` method, and decide deliberately whether each call returns a *fresh* iterator — making the object re-scannable — or returns `self`, making it a one-shot stream that is empty after the first pass
**ELSE** when the object is genuinely a sequence addressed by position, `__getitem__` alone still powers iteration as a fallback, and brings indexing and slicing with it

## Do
- Write `__iter__` as a generator with `yield`: each call then produces a new generator with its own local state, so multiple and nested scans work with no extra class and no explicit `__next__`.
- Return a separate iterator object from `__iter__` when the state is too complex for a generator; that second object owns the cursor and the `__next__` method, so each scan is independent.
- Return `self` from `__iter__` only when a single consuming pass is the intent — a stream over a socket or a cursor over a result set that cannot be rewound.
- Raise `StopIteration` from `__next__` to end a scan when writing the iterator by hand; a generator does this for you by returning.
- Add `__contains__` when membership has a faster answer than a scan — a mapping can check a key directly instead of walking every item, and `in` prefers it over `__iter__`.
- Remember that `__getitem__` gives you iteration for free: Python indexes from zero upward until `IndexError`, so one method also buys `in`, unpacking, `list()`, and comprehensions.

## Don't
- Don't return `self` from `__iter__` and then expect nested loops over the same object to work; both loops share one cursor, and the inner loop exhausts it before the outer one has advanced.
- Don't leave the scan count to chance. A caller cannot tell a one-shot object from a re-scannable one by looking at it; the second loop just silently produces nothing.
- Don't implement `__iter__` and `__getitem__` with different meanings for the same class — `__iter__` wins in iteration contexts, so the `__getitem__` behavior would appear only for explicit indexing, which is a trap for readers.
- Don't reach for a class at all when a plain generator function does the job; classes earn their place when the iterable also needs other behavior, configuration, or inheritance.

## Checklist
- Does `__iter__` return a fresh iterator per call, and is that the intended scan behavior?
- Do nested loops over one instance produce the expected cross product rather than nothing?
- Is `__contains__` worth defining, or is a full scan genuinely the only way to answer `in`?
- Would a generator function be simpler than this class?

## Notes
Iteration contexts call `iter()` first, which looks for `__iter__` and falls back to `__getitem__` only when it is absent; whatever `__iter__` returns is then driven by repeated `next()` calls until `StopIteration`. The whole single-versus-multiple-scan question reduces to one line of your code — what `__iter__` hands back. Returning `self` reuses one set of state; returning a new object, or being a generator, creates fresh state per scan.
