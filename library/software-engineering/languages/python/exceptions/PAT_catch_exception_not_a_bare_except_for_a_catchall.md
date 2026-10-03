---
object_id: PAT_catch_exception_not_a_bare_except_for_a_catchall
object_type: pattern
name: Catch Exception, Not a Bare except, for a Catchall Handler
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
- except
cross_links:
- rel: related_to
  target_object_id: PAT_separate_the_no_exception_path_with_trys_else_clause
- rel: related_to
  target_object_id: PAT_dont_hide_errors
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Catch Exception, Not a Bare except, for a Catchall Handler

## Pattern Rule
**IF** a try statement needs a handler general enough to catch anything the main action might raise
**THEN** name the handler `except Exception`, which matches every exception meant to be handled this way while leaving process exit and interrupt signals to propagate
**ELSE** only use a bare `except` (no name at all) when you deliberately mean to intercept those signals too, and reraise immediately after whatever cleanup made that necessary

## Do
- Reach for `except Exception` as the default "catch everything reasonable" clause.
- List specific exception types above a catchall when some of them need distinct handling, since `except` clauses are tried top to bottom and the first match wins.
- Treat a caught-and-silently-passed exception as a design smell regardless of which form caught it; broad catching does not excuse hiding what was caught.

## Don't
- Don't reach for a bare `except` as the default broad handler; it also matches process-level exit and interrupt requests, which then get treated as ordinary errors instead of being allowed to stop the program.
- Don't assume `except Exception` and bare `except` are interchangeable; they differ in exactly the cases that matter most for keeping a program responsive to being stopped.
- Don't let a broad except, of either form, mask a programming mistake that should have surfaced as a visible error.

## Checklist
- Does the catchall clause name `Exception` rather than being bare, unless interception of exit/interrupt signals is actually intended?
- Where a bare `except` is used deliberately, does it reraise rather than swallow the signal it caught?
- Are more specific `except` clauses, where needed, listed above the catchall?

## Notes
A bare `except` matches literally everything Python can raise, including the exceptions used to request that the process exit or stop. `except Exception` matches the hierarchy of ordinary errors without reaching that high, so code wrapped in it keeps responding to an interrupt or an exit request instead of absorbing it as if it were a bug in the wrapped code. That one exclusion is the entire difference between the two forms, and it is also the entire reason the named form is the safer default.
