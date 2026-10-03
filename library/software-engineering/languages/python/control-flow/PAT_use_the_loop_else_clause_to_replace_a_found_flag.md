---
object_id: PAT_use_the_loop_else_clause_to_replace_a_found_flag
object_type: pattern
name: Use the Loop else Clause to Replace a Found Flag
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
- loops
- search
cross_links: []
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Use the Loop else Clause to Replace a Found Flag

## Pattern Rule
**IF** a loop searches for something and the code after the loop needs to behave differently depending on whether the search succeeded or exhausted the loop without finding it
**THEN** put the success action and a `break` inside the loop body, and put the not-found action in the loop's `else` clause, which Python runs only when the loop finishes without hitting a `break`
**ELSE** when nothing needs to happen specifically on the not-found path, skip the `else` entirely; it is optional on both `while` and `for`

## Do
- Trust the `else` clause to run exactly when the loop completed normally — including when the loop body never ran at all because the test was false (or the sequence was empty) from the start.
- Line the `else` up with the loop's own header line, not with a nested `if` inside the body; its indentation is what ties it to the loop rather than to the test that triggers the `break`.
- Use this to delete a found/status flag: initialize nothing, set nothing, and let the `break`'s absence at loop exit be the signal instead of a variable that has to be set correctly on every path.
- Reach for this on a `for` loop too, not just `while`; it means exactly the same thing — not exited via `break` — whichever loop header it is attached to.

## Don't
- Don't confuse the loop's `else` with an `if`'s `else`; which statement it belongs to is decided purely by indentation, and a loop `else` placed under the wrong header silently attaches to the wrong statement.
- Don't assume the `else` runs only if the loop body executed at least once; it also runs when the body never ran because the loop's starting condition was already false.
- Don't keep a manual found/status flag alongside a loop `else` that already does the same job; that reintroduces the exact bookkeeping the `else` exists to remove.

## Checklist
- Does the loop's success path end in a `break`, with the failure path falling through to `else`?
- Is the `else` indented to match the loop header it belongs to, not a nested `if`?
- Has a redundant found/status flag been removed now that `else` carries that information?

## Notes
This clause is unique to Python — most languages have nothing equivalent — which is why it quietly perplexes newcomers and goes unused by some veterans who never learned it exists. Its value is sharpest in a search loop: the alternative is a flag set before the loop, set again inside it, and tested again afterward, three separate places that all have to agree, where the `else` collapses this into one fact the loop statement itself already knows.
