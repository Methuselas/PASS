---
object_id: PAT_choose_a_generator_expression_when_results_should_stream
object_type: pattern
name: Choose a Generator Expression When Results Should Stream
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
- comprehensions
- generators
cross_links:
- rel: related_to
  target_object_id: PAT_produce_values_lazily_with_a_generator_function
- rel: related_to
  target_object_id: PAT_build_a_list_with_a_comprehension_instead_of_a_manual_append_loop
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Choose a Generator Expression When Results Should Stream

## Pattern Rule
**IF** writing a comprehension and deciding between square brackets and parentheses — a collection built now, or values produced as a consumer asks for them
**THEN** use parentheses for a generator expression when the consumer takes items one at a time, may stop early, or would be handed a list too large to want; use square brackets when the result must be indexed, measured, scanned more than once, or stored
**ELSE** when the per-item work needs statements rather than a single expression, neither bracket form fits — write a generator function and call it instead

## Do
- Omit the parentheses where the expression is already a call's only argument, so a total or a join over a stream reads as one call rather than a nested pair of brackets.
- Expect the two forms to produce identical values; wrapping a generator expression in a `list` call is exactly what the square-bracket form does.
- Prefer the streaming form when feeding a consumer that can stop early, since items beyond the point where it stops are never computed at all.
- Reach for a generator expression when a set or dict comprehension would be the wrong tool because results are wanted on demand: both of those build their entire result immediately, however lazily their input arrives.
- Wrap the expression in a small function taking the subject as a parameter when the same streaming computation is needed for different inputs.

## Don't
- Don't index, slice, or ask the length of what a generator expression returns; it is not a sequence, and those are exactly the operations the bracketed form exists to provide.
- Don't hand one generator expression to two consumers; the first exhausts it and the second silently sees an empty series.
- Don't wrap a generator expression in `list` out of habit where nothing needs a real list, and don't leave it unwrapped where the surrounding code then needs one.
- Don't nest a generator expression inside another comprehension that materialises it immediately; one of the two levels of laziness is then doing no work.

## Checklist
- Does the consumer take items one at a time, or does it need the whole collection?
- Could the consumer stop before the end, making the unproduced items pure savings?
- Is the result indexed, measured, or scanned twice anywhere downstream?
- If the per-item work has grown past a single expression, has it moved to a generator function?

## Notes
The choice of bracket is the whole decision: the same clauses, filters, and nesting work in both forms, and what changes is only whether the values exist all at once or on request. That makes this one of the cheapest performance decisions in the language to revisit — a pair of characters — and also one of the easiest to get subtly wrong, because the streaming form quietly fails to support the sequence operations the bracketed form allowed. `PAT_know_whether_an_iterable_supports_multiple_passes_before_reusing_it` governs the reuse half of that hazard, and `PAT_produce_values_lazily_with_a_generator_function` takes over when one expression is no longer enough.
