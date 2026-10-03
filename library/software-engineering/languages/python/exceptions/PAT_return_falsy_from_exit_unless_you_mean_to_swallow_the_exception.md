---
object_id: PAT_return_falsy_from_exit_unless_you_mean_to_swallow_the_exception
object_type: pattern
name: Return a Falsy Value from __exit__ Unless You Mean to Swallow the Exception
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
- context-managers
- dunder-methods
cross_links:
- rel: related_to
  target_object_id: PAT_prefer_with_as_over_try_finally_when_the_protocol_is_supported
- rel: related_to
  target_object_id: PAT_dont_hide_errors
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Return a Falsy Value from __exit__ Unless You Mean to Swallow the Exception

## Pattern Rule
**IF** you are writing a context manager's `__exit__(self, exc_type, exc_value, exc_tb)` method
**THEN** return `False`, `None`, or nothing at all when the block's exception should keep propagating after your cleanup runs, and return a true value only in the deliberate case where `__exit__` has fully handled the condition the exception represented
**ELSE** when the `with` block exits without an exception, `exc_type`, `exc_value`, and `exc_tb` all arrive as `None`, and the return value is never consulted for propagation in that case

## Do
- Treat `exc_type` being `None` as the signal for a clean exit, and anything else as the signal that an exception is live and needs a propagate-or-suppress decision.
- End `__exit__` without a `return` statement, or with an explicit `return False`, whenever cleanup alone is the job — closing a file or releasing a lock does not mean the error that occurred is resolved.
- Reserve a true return value for a context manager whose entire purpose is to convert certain exceptions into a handled, suppressed outcome, and document that behavior where callers will see it.

## Don't
- Don't return `True` reflexively because the method did "something" with the exception, like logging it; logging is not handling, and a caller who expected the exception to propagate now never sees it.
- Don't forget that `__exit__`'s return value only matters when an exception is active; a method that always returns a true value, intending it to mean "cleanup succeeded," silently suppresses every exception the `with` block raises.
- Don't rely on an exception being caught elsewhere later as a safety net; once `__exit__` returns true, the exception is gone and no later code can catch it.

## Checklist
- Does `__exit__` return a value that is false for every case where the exception should still propagate?
- Is a true return value reserved for a context manager whose documented job is to resolve that category of exception?
- Would a reader of this `__exit__` expect, from its return value alone, which outcomes are suppressed?

## Notes
`__exit__`'s three-argument signature and its boolean-like return meet at one hinge: whether the exception that was active when the block exited continues after `__exit__` returns. Every other activity the method performs — closing, releasing, logging — is independent of that hinge, which is exactly why a method that correctly does cleanup can still silently delete an error if its return value defaults to something truthy. The safe default is to let the hinge alone decide propagation, and treat a true return as a specific claim that this exception's story ends here.
