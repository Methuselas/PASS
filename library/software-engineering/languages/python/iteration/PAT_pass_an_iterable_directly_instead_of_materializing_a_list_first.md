---
object_id: PAT_pass_an_iterable_directly_instead_of_materializing_a_list_first
object_type: pattern
name: Pass an Iterable Directly Instead of Materializing a List First
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
- memory
cross_links: []
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Pass an Iterable Directly Instead of Materializing a List First

## Pattern Rule
**IF** about to call a builtin or method that conceptually processes a sequence of items — `sorted`, `sum`, `any`, `all`, `max`, `min`, `list`, `tuple`, `set`, `dict`, a string's `join`, `zip`, `map`, `filter`, sequence assignment, the `in` membership test, or unpacking arguments with `*` — and the data in hand is some other iterable (an open file, a generator, a dict view, another iterator)
**THEN** pass that iterable directly, without first converting it to a list; every one of these tools already drives its argument with the iteration protocol and reads it one item at a time
**ELSE** when the data must be scanned more than once, indexed, sliced, reversed, or otherwise handled as a real sequence, convert deliberately with `list(...)`/`tuple(...)`/`set(...)` first, rather than relying on operations that only real sequences support

## Do
- Hand an open file straight to `sorted`, `sum`, `zip`, `map`, `filter`, `list`, `tuple`, `set`, `dict`, `"sep".join(...)`, a sequence-assignment target, or an `in` test; each reads it one item at a time through the same iteration protocol a `for` loop uses, with no separate read step.
- Unpack an iterable directly into a function call with `*obj` when its items are the positional arguments needed, including when `obj` is itself something like an open file.
- Reach for `zip(*zipped_result)` to "unzip" a previous `zip` call's tuples back into separate sequences, understanding that this works because `*` unpacks any iterable into individual arguments.
- Treat this as the general case, not a trick specific to files: a generator, a dict view, or a custom iterable object gets the same treatment from all of these tools.

## Don't
- Don't call `.readlines()`, or otherwise force a list, before handing data to a tool that already accepts an iterable; the extra step adds memory use and an extra pass for no benefit.
- Don't assume a function that works on a list requires one; check whether it actually needs list-only operations (indexing, slicing, multiple passes) before converting, since most sequence-processing builtins need only the iteration protocol.
- Don't pass the same single-pass iterable to two of these tools expecting each to see the full set of items; once it has been scanned once, it has nothing left to give a second consumer.

## Checklist
- Does the function actually require list-specific behavior (indexing, slicing, length, multiple scans), or only a left-to-right scan?
- Is a file, generator, or other iterable being converted to a list only where that conversion is genuinely needed?
- If the same iterable is handed to more than one consumer, has it already been exhausted by an earlier one?

## Notes
This works because the iteration protocol is the common interface essentially all of Python's left-to-right tools are built against, not something special to sequences. A file, a generator, a dict view, and a list all satisfy the same contract — `iter()` returns something with a `next()` — so anything written against "an iterable" accepts all of them equally, without needing to know which one it got.
