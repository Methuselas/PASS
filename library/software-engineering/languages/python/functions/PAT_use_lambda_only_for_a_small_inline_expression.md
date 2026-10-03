---
object_id: PAT_use_lambda_only_for_a_small_inline_expression
object_type: pattern
name: Use lambda Only for a Small Inline Expression
library_path:
- software-engineering
- languages
- python
- functions
stage_binding: 2 block
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- python
- functions
- lambda
- readability
cross_links:
- rel: related_to
  target_object_id: PAT_treat_def_as_a_runtime_assignment_of_a_function_object
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Use lambda Only for a Small Inline Expression

## Pattern Rule
**IF** a function is small enough to be a single expression and is wanted at the point where it is used — a callback registered in a call, an entry in a table of actions, a key or test handed to another function
**THEN** write it as a `lambda` right there, so the code sits beside its only use and needs no name that could collide with another or drift pages away from the call
**ELSE** as soon as the body needs a statement — a loop, a `try`, an assignment, anything beyond one expression — write a `def` and pass it by name; that boundary is where `lambda` is deliberately drawn

## Do
- Keep the body to one expression whose value is the result; a lambda hands that value back with no `return` statement to write.
- Use the ordinary parameter forms inside a lambda: plain names, defaults, and star forms all behave exactly as they do in a `def` header.
- Rely on enclosing-scope lookup for values from the function the lambda sits in, the same as for a nested `def`; a default argument is needed only where a loop rebinds the name being captured.
- Reach for a lambda where a function is wanted somewhere a statement cannot go, such as inside a list or dict literal or directly in another call's argument list.

## Don't
- Don't smuggle statement logic into a lambda through expression tricks — a conditional expression standing in for an `if` block, an and/or chain, a comprehension evaluated only for its side effects; each one is harder to read than the `def` it displaced.
- Don't assign a lambda to a name and then use it as though it were a `def`; the two produce the same kind of object, but the named `def` form gives the function a real name in tracebacks and introspection, which the lambda does not.
- Don't nest one lambda inside another; it works, since each sees the enclosing one's names, but the result reads as a puzzle rather than as code.
- Don't try to annotate a lambda's parameters or result; annotation syntax exists only in a `def` header, which is itself a hint that anything needing a declared interface wants a `def`.

## Checklist
- Is the body a single expression, with no statement disguised as one?
- Is this function used in exactly one place, close enough to read together with it?
- Would a reader of the surrounding line know what the lambda computes without scrolling elsewhere?
- Would a name and a `def` make the traceback, the signature, or the intent clearer?

## Notes
The one-expression restriction is a design decision rather than an oversight: it keeps the construct the size of the hole it was meant to fill, which is why pressure to exceed it is a reliable signal that a `def` is the right tool instead. The payoff for staying inside the limit is proximity — a deferred action written where it is registered, rather than defined far away and referenced by a name invented only to connect the two.
