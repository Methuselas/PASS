---
object_id: PAT_stub_out_unfinished_code_with_pass_or_ellipsis
object_type: pattern
name: Stub Out Unfinished Code with pass or Ellipsis
library_path:
- software-engineering
- languages
- python
- syntax
stage_binding: 1 skeleton
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- python
- syntax
- placeholders
- stubs
cross_links: []
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Stub Out Unfinished Code with pass or Ellipsis

## Pattern Rule
**IF** Python's syntax requires a statement in some block — an empty function body, an empty exception handler, a placeholder for code not yet written — but there is nothing to do there yet
**THEN** write `pass` as the explicit no-op, or `...` (the `Ellipsis` literal) as its more "to be filled in later"-flavored equivalent; both satisfy the syntax requirement and do nothing at runtime
**ELSE** once real logic exists for that block, replace the placeholder with it; neither form is meant to be permanent

## Do
- Use `pass` for any block that genuinely needs to do nothing at all, such as silently ignoring one specific caught exception.
- Use `pass` or `...` interchangeably to stub out a function body that will be filled in later; both are valid wherever a statement (or, for `...`, an expression) is expected.
- Use the single-line form (`def func(): ...` or `def func(): pass`) for a trivial stub, the same one-liner exception the rest of Python's compound-statement syntax allows.
- Use `...` where a placeholder value, not just a placeholder statement, is wanted — `X = ...` works as an alternative to `X = None` for a not-yet-decided value, something `pass` cannot do since it is a statement, not an expression.

## Don't
- Don't leave a compound statement's body empty outright; Python requires at least one statement after a header's colon, and an empty block is a syntax error, not a tolerated gap.
- Don't mistake `...` for a 2.X-compatible feature; it is valid as a general-purpose expression placeholder only in 3.X, beyond its older, narrower role in slicing syntax.
- Don't mistake a stubbed `pass`/`...` body for a finished implementation; search for both before considering a module complete, since either can silently survive in code meant to have been filled in.

## Checklist
- Does every syntactically required but intentionally empty block contain `pass` or `...`, not nothing?
- Where a placeholder value, not a placeholder statement, was wanted, was `...` used instead of `pass`?
- Have stub bodies been searched for and replaced before considering the surrounding code finished?

## Notes
`pass` is to statements what `None` is to objects — an explicit, deliberate nothing, chosen so that an empty block reads as intentionally empty rather than accidentally incomplete. `...` adds a second option with a more explicit "to be done" connotation and the added flexibility of being usable as a value, not only as a statement.
