---
object_id: PAT_know_whether_an_iterable_supports_multiple_passes_before_reusing_it
object_type: pattern
name: Know Whether an Iterable Supports Multiple Passes Before Reusing It
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
- gotcha
cross_links: []
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Know Whether an Iterable Supports Multiple Passes Before Reusing It

## Pattern Rule
**IF** planning to iterate the same iterable object more than once — two separate loops over it, or nested loops that both scan it
**THEN** check whether it is multi-pass (a list, tuple, dict, dict view, string, or `range` — each call to `iter()` returns an independent, position-tracking iterator) or single-pass (a `map`, `zip`, `filter`, a file, or a generator — exhausted after one full scan, with further iteration silently yielding nothing)
**ELSE** when reuse is genuinely needed from a single-pass iterable, materialize it once with `list(...)` or `tuple(...)` and iterate that stored result as many times as needed instead

## Do
- Treat `map`, `zip`, and `filter` results as one-shot: once consumed by a `for` loop, a comprehension, or manual `next()` calls, a second scan over the same object produces nothing, silently, with no error.
- Treat `range` as the exception among the iteration-returning builtins: it supports `len()`, indexing, and independent iterators from repeated `iter()` calls, behaving like a real sequence for everything except direct `next()` calls on the range object itself.
- Treat dictionaries and their `keys()`/`values()`/`items()` views the same way as `range`: each is reusable across multiple independent scans, even though none of them is itself an iterator — `next()` on a view or a dict raises `TypeError`; `iter()` is needed first.
- Store the materialized result of a single-pass iterable in a variable the first time it is built, when more than one pass over it is needed, rather than recreating or re-consuming the original.

## Don't
- Don't write a second `for` loop over a `map`/`zip`/`filter` result (or a generator, or a file) expecting it to scan from the start again; it will simply produce zero iterations with no error to flag the mistake.
- Don't assume identity (`iter(obj) is obj`) alone identifies single-pass objects reliably on sight; check it directly rather than guessing from how an object looks or prints.
- Don't materialize a multi-pass object (a list, a dict, a `range`) into a list purely out of caution; it already supports repeated iteration without that extra step.

## Checklist
- Will this iterable actually be scanned more than once, directly or through nested loops?
- If so, is it multi-pass (list, tuple, dict, dict view, range) or single-pass (map, zip, filter, file, generator)?
- If single-pass and reuse is required, has the result been captured once with `list(...)`/`tuple(...)` rather than re-consumed from the original?

## Notes
This distinction was not visible in Python 2.X, where `map`, `zip`, and `filter` built and returned real, reusable lists; it only becomes a practical hazard once these tools return iterables that generate results on demand. A second loop that silently does nothing is an easy defect to miss precisely because nothing raises — the absence of output is the only symptom.
