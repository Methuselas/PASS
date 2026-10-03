---
object_id: PAT_separate_the_no_exception_path_with_trys_else_clause
object_type: pattern
name: Separate the No-Exception Path with try's else Clause
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
- try
- control-flow
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

# Separate the No-Exception Path with try's else Clause

## Pattern Rule
**IF** code must run only when the try block's main action completed without raising, and the try already has one or more except clauses for that action
**THEN** put that code in the try statement's `else` clause, which runs exactly when the try block raised nothing
**ELSE** when there is no `except` clause to pair it with, or the action is unconditional cleanup needed regardless of whether an exception occurred, use `finally` or plain code after the try instead — `else` requires at least one `except` and means something different from either

## Do
- Use `else` to make "no exception occurred" an explicit branch, not something tracked with a boolean flag you set and check afterward.
- Keep the `else` body free of whatever exception the try block's `except` clause is watching for, by moving that code there specifically to get it out of the try block's reach.
- Pair `else` only with a try that already has at least one `except` clause.

## Don't
- Don't append "no exception occurred" code directly to the end of the try block; if that code itself raises the exception named in an `except` clause below, it is misreported as a failure of the original action rather than of the follow-up code.
- Don't confuse `else` with `finally`: `else` runs only on the no-exception path and is skipped whenever any `except` clause handles a raised exception, while `finally` always runs.
- Don't write an `else` on a try with no `except` clause; a bare try/else is not a meaningful statement, since `else` requires an `except` to pair with.

## Checklist
- Is the "no exception occurred" code in `else` rather than tacked onto the end of the try block?
- Would moving that code into the try block let it be erroneously caught by the block's own `except` clause?
- Does the try already have at least one `except` clause for this `else` to attach to?

## Notes
Without `else`, the only way to tell whether execution reached the code after a try because nothing went wrong or because an exception was raised and handled is to track a flag yourself. `else` makes that distinction structural: it runs exactly when the try block's main action completed clean, and is skipped whenever any `except` clause fires. The same distinction is why `else` must not be replaced by appending its code to the try block — doing so merges two different failure categories into one, letting a bug in the follow-up code masquerade as a bug in the original action.
