---
object_id: PAT_prefer_with_as_over_try_finally_when_the_protocol_is_supported
object_type: pattern
name: Prefer with/as Over try/finally When the Object Supports It
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
- resource-management
cross_links:
- rel: related_to
  target_object_id: PAT_give_every_acquired_resource_one_named_owner
- rel: related_to
  target_object_id: PAT_return_falsy_from_exit_unless_you_mean_to_swallow_the_exception
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Prefer with/as Over try/finally When the Object Supports It

## Pattern Rule
**IF** the object being used implements the context manager protocol (it defines `__enter__` and `__exit__`)
**THEN** wrap its use in a `with` statement to get its startup and cleanup actions run automatically around the block, including when the block raises
**ELSE** when the object does not support the protocol, or the cleanup logic does not map to a single object's lifetime, fall back to `try`/`finally`, the general tool that works for any cleanup action regardless of object support

## Do
- Reach for `with` first for any object documented as a context manager — open files, locks, and similar resources run their exit action on block exit whether or not an exception occurred.
- List multiple context managers in one `with` statement, separated by commas, when several independent resources share the same block's lifetime, rather than nesting a separate `with` for each.
- Fall back to `try`/`finally` when a cleanup action is needed but the object involved has no `__enter__`/`__exit__` pair, since `try`/`finally` places no requirement on what it is guarding.

## Don't
- Don't write a manual `try`/`finally` around an object that already supports `with` purely out of habit; it costs more lines for the same guarantee and does not also offer the entry action a context manager can provide.
- Don't assume `with` is strictly more powerful than `try`/`finally`; it is narrower in scope, limited to what the protocol can express, while `try`/`finally` accepts any cleanup code at all.
- Don't treat several comma-listed managers in one `with` as independent of each other; they nest in the order listed, so a later manager's entry runs inside an earlier manager's, and its exit runs before the earlier one's.

## Checklist
- Does the object being wrapped actually implement the context manager protocol, rather than merely having a `close()` method?
- Where several resources are opened together, are they listed in one `with` rather than duplicated in separate `try`/`finally` blocks?
- Is `try`/`finally` reserved for cleanup that has no corresponding context manager, rather than used as the default everywhere?

## Notes
A `with` statement is not a different guarantee than `try`/`finally`, it is the same guarantee — the exit action runs whether the block finished cleanly or raised — expressed through an object's own protocol instead of through code written at the call site. That is both its appeal and its limit: concise and reusable for anything that implements the protocol, and simply unavailable for anything that does not, which is when the fully general `try`/`finally` remains necessary.
