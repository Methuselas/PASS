---
object_id: PAT_traverse_multiple_sequences_in_parallel_with_zip
object_type: pattern
name: Traverse Multiple Sequences in Parallel with zip
library_path:
- software-engineering
- languages
- python
- control-flow
stage_binding: 2 block
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- python
- control-flow
- iteration
- zip
cross_links: []
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Traverse Multiple Sequences in Parallel with zip

## Pattern Rule
**IF** stepping through two or more sequences together, position by position
**THEN** wrap them in `zip(seq1, seq2, ...)` and unpack each resulting tuple in the `for` target — `for x, y in zip(L1, L2):` — rather than indexing each sequence manually with a shared counter
**ELSE** when the sequences may differ in length and a mismatch should be an error rather than silently handled, pass `strict=True` to `zip` (current Python, 3.10+) instead of trusting its default truncation

## Do
- Pass as many sequences to `zip` as needed; with three arguments it yields three-item tuples, and in general N arguments yield N-item tuples.
- Unpack each `zip` result with tuple assignment in the `for` target, the same mechanism that unpacks any other sequence of tuples.
- Build a dict directly from parallel keys and values with `dict(zip(keys, values))` instead of looping and assigning one key at a time.
- Pass `strict=True` when every sequence is expected to be the same length and a mismatch should raise immediately, rather than silently losing the extra items.

## Don't
- Don't assume `zip` pads the shorter sequences; by default it truncates every result to the length of the shortest argument, silently dropping the extra items from longer ones.
- Don't manually index two sequences with one shared counter (`for i in range(len(L1)): x, y = L1[i], L2[i]`) when `zip` does the same pairing with less code and no index arithmetic to get wrong.
- Don't forget that `zip` itself is a lazy iterator; wrap it in `list(...)` when the paired-up result needs to be displayed, counted, or iterated more than once.

## Checklist
- Does the loop actually need items from more than one sequence at matching positions?
- If the sequences could differ in length, is the default truncation the intended behavior, or should `strict=True` catch the mismatch instead?
- Is `zip`'s result consumed once as a lazy iterator, or does the code need it materialized with `list()` first?

## Notes
`zip` only pairs positions; it says nothing about whether the sequences were supposed to be the same length, which is exactly the gap `strict=True` closes for code written against a current Python. Before that option existed, catching a silent truncation meant comparing lengths separately before zipping.
