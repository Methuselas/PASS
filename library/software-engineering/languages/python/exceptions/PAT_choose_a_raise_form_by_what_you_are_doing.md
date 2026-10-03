---
object_id: PAT_choose_a_raise_form_by_what_you_are_doing
object_type: pattern
name: Choose a raise Form by What You're Doing
library_path:
- software-engineering
- languages
- python
- exceptions
stage_binding: 2 block
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- python
- exceptions
- raise
- exception-chaining
cross_links:
- rel: related_to
  target_object_id: PAT_catch_exception_not_a_bare_except_for_a_catchall
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Choose a raise Form by What You're Doing

## Pattern Rule
**IF** code must trigger an exception
**THEN** raise a new instance with `ClassName(args)` to signal a fresh error; use a bare `raise` inside a handler to propagate the exception currently being handled unchanged; use `raise New from original` when deliberately replacing one exception with another while keeping the original visible as its documented cause; and append `from None` only when that chain itself would be noise worth suppressing from the final error message
**ELSE** do not reach for `raise ClassName` without parentheses out of habit; it is accepted shorthand that constructs the instance for you, but writing the call explicitly is clearer once constructor arguments are involved

## Do
- Use plain `raise` with no arguments inside an `except` block to reraise exactly the exception just caught, rather than raising a new instance of the same type and losing its original traceback and message.
- Use `raise New from original` when translating a low-level exception into one meaningful at the current layer, so a reader of the final traceback sees both what went wrong underneath and what that was reported as above.
- Reserve `raise New from None` for cases where showing the chained original would only clutter the message your caller sees, since suppressing it removes real diagnostic information.

## Don't
- Don't let an except block's own `raise ClassName()` for "the same kind of problem" replace the exception it just caught with a materially different one unless that replacement is deliberate; a bare `raise` is the tool for faithful propagation, not a closer-looking substitute.
- Don't suppress chaining with `from None` by default; most of the time the original exception is exactly the information whoever reads the traceback needs.

## Checklist
- Where an exception is reraised after being caught, is it a bare `raise` rather than a freshly constructed one, unless replacement is intended?
- Where one exception is deliberately raised in response to another, does the raise use an explicit `from` clause rather than letting the chain form implicitly?
- Is `from None` reserved for cases where the chained context is genuinely unwanted, rather than used as a default?

## Notes
Python attaches whichever exception was active to a newly raised one automatically, as its context, so even a plain `raise New()` inside a handler shows both exceptions in the final error message. Writing `from` explicitly turns that automatic attachment into a documented cause rather than an incidental fact of where the raise happened to execute, which is the difference between a traceback that explains itself and one that merely records what happened to be true at the time.
