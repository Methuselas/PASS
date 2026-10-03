---
object_id: PAT_split_a_sequence_by_position_with_starred_unpacking
object_type: pattern
name: Split a Sequence by Position with Starred Unpacking
library_path:
- software-engineering
- languages
- python
- assignment
stage_binding: 2 block
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- python
- assignment
- unpacking
- sequences
cross_links: []
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Split a Sequence by Position with Starred Unpacking

## Pattern Rule
**IF** splitting a sequence into "first and rest," "rest and last," or "first, middle, last" pieces, and the sequence's length is not fixed in advance
**THEN** use one starred name in the unpacking target — `a, *b = seq`, `*a, b = seq`, `a, *b, c = seq` — and let the starred name collect everything not claimed by the plain names
**ELSE** when the sequence's length is fixed and known, use plain, unstarred sequence assignment instead; a star adds flexibility a reader then has to account for

## Do
- Put the starred name wherever the variable part of the split belongs — first, last, or in the middle — and let the plain names claim the fixed positions around it.
- Expect the starred name to always hold a list, even at the boundaries: a single matched item still comes back as a one-item list, and nothing left over comes back as an empty list rather than an error.
- Use this to replace manual slicing for the common "pop the front, keep the rest" loop idiom: `front, *rest = seq` reads as one step instead of `front, rest = seq[0], seq[1:]`.
- Apply the same starred target inside a `for` loop header when each iterated item is itself a sequence that should be split the same way.

## Don't
- Don't use more than one starred name in a single target; `a, *b, c, *d = seq` is a `SyntaxError`, not an ambiguous-but-legal split.
- Don't write a bare starred name with no enclosing sequence, as in `*a = seq`; the star must appear inside a tuple or list target — even a single trailing one, `*a, = seq`.
- Don't assume the starred result is the same type as the input; unlike a slice, which returns the sliced type, extended unpacking always hands the starred name a list, even when splitting a string or a range.

## Checklist
- Is there exactly one starred name in the target?
- Is the starred name written inside a tuple/list target, even if that means a trailing comma for a single name?
- Does the code consuming the starred result expect a list, regardless of the input sequence's own type?

## Notes
Because everything extended unpacking does is also reachable with explicit indexing and slicing, reach for it where it reads more clearly — the "first, rest" and "rest, last" splits are the cases it earns its keep on, not a wholesale replacement for slicing.
