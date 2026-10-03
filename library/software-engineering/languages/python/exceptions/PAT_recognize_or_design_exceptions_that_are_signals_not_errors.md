---
object_id: PAT_recognize_or_design_exceptions_that_are_signals_not_errors
object_type: pattern
name: Recognize or Design Exceptions That Are Signals, Not Errors
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
- control-flow
- api-design
cross_links:
- rel: related_to
  target_object_id: PAT_prefer_null_safety_or_optionals
- rel: related_to
  target_object_id: PAT_return_result_type_to_convey_error_cause
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Recognize or Design Exceptions That Are Signals, Not Errors

## Pattern Rule
**IF** a function cannot signal an expected, non-error outcome with an ordinary return value — either because every return value is potentially valid, or because the outcome (end of input, item found, item not found) naturally interrupts the caller's control flow
**THEN** raise a dedicated exception to carry that outcome, and let the caller catch it as part of ordinary, expected control flow rather than treating the catch itself as evidence something went wrong
**ELSE** when a clear, always-invalid sentinel value exists and no value is ambiguous, an ordinary return value is simpler and does not require the caller to use a `try` at all

## Do
- Read a caught exception's meaning from its role, not its name alone: built-ins like `EOFError` from `input()` are raised on an expected end-of-data condition, not a malfunction, exactly like a `Found` or `Failure` exception a function raises on purpose to report its outcome.
- Define a small, purpose-built exception class for a success-or-failure signal when no sentinel return value is safe — when a search function, for instance, could legitimately return any object as a found result.
- Pair the signaling exception with a `try`/`except`/`else` at the call site, so the "exception happened" and "exception didn't happen" branches both read as ordinary, anticipated outcomes rather than as a main path and an error path.
- Treat a caught signal exception as a normal branch when logging, metrics, or tests observe it; counting every catch as a failure will misreport what actually happened.

## Don't
- Don't assume every caught exception represents a defect to investigate; some are the chosen mechanism for reporting an expected outcome, and treating them as alarms creates noise that drowns out the exceptions that are genuine errors.
- Don't reach for a sentinel return value (`None`, `-1`, an empty collection) to signal "not found" or "end of data" when that same value could also be a legitimate result; that ambiguity is exactly what a dedicated signal exception avoids.
- Don't name a signaling exception so generically that a reader cannot tell, from the except clause alone, whether it represents a real problem or an expected outcome.

## Checklist
- Can every return value from this function be a legitimate result, making a sentinel return value ambiguous?
- Does the code that catches this exception treat it as an expected branch (with `else` or ordinary follow-on logic), rather than logging or escalating it the way a real error would be?
- Would a reader unfamiliar with this exception's name be able to tell, from where and how it is raised, that it signals an outcome rather than a malfunction?

## Notes
Python's own standard library already relies on this split — file objects use a return value (an empty string) for end-of-file, while `input()` uses an exception for the same kind of boundary, because an empty line is itself a legitimate result it must not be confused with. The same reasoning scales to application code: once "no return value is safe as a sentinel" is true, an exception is not a workaround but the correct tool, and the `try`/`except`/`else` statement exists in part to let that usage read as cleanly as an `if`/`else` would for an ordinary flag.
