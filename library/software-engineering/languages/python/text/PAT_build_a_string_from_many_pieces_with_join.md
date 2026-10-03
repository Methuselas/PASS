---
object_id: PAT_build_a_string_from_many_pieces_with_join
object_type: pattern
name: Build a String from Many Pieces with join
library_path:
- software-engineering
- languages
- python
- text
stage_binding: 3 rough
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- python
- strings
- immutability
- performance
cross_links:
- rel: related_to
  target_object_id: PAT_let_measurement_decide_what_to_tune
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Build a String from Many Pieces with join

## Pattern Rule
**IF** Python code assembles a string from many pieces in a loop, or makes many edits to one large string
**THEN** collect the pieces in a list (or yield them from a generator) and combine them once with `sep.join(pieces)`, or edit a list of characters and join it at the end
**ELSE** when there are only a few pieces, plain `+` or an f-string is clearer and fast enough.

## Do
- Accumulate output as `parts.append(...)` inside the loop and finish with `''.join(parts)`, or pass a generator: `', '.join(str(x) for x in items)`.
- For many positional edits, convert once with `chars = list(s)`, assign into `chars[i]`, and rebuild with `''.join(chars)`.
- Write to an `io.StringIO` when the code already has the shape of writing to a file.
- Replace substrings with `s.replace(old, new, count)` rather than locating and slicing by hand.

## Don't
- Don't grow a large string with `s += piece` in a loop; each step may copy everything built so far, and the in-place optimisation CPython sometimes applies is not guaranteed on other implementations or when another reference to the string exists.
- Don't pass non-strings to `join`; convert them first (`map(str, items)`), since `join` raises `TypeError` on a number.
- Don't try to change a string through indexing; `s[0] = 'x'` raises `TypeError` because strings are immutable.

## Checklist
- Is any string built up inside a loop with `+` or `+=`?
- Are all items passed to `join` already strings?
- Would a list of characters or `StringIO` make the edits simpler?

## Notes
Because strings cannot change in place, every concatenation, slice or method call that "modifies" a string actually creates a new one. That costs nothing for a few operations but grows quadratically when a long string is rebuilt piece by piece. `join` is a method of the separator string, not of the list, which is why it reads `', '.join(parts)`.
