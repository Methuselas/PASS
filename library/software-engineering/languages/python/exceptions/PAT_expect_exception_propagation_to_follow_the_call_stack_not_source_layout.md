---
object_id: PAT_expect_exception_propagation_to_follow_the_call_stack_not_source_layout
object_type: pattern
name: Expect Exception Propagation to Follow the Call Stack, Not Source Layout
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
  target_object_id: PAT_separate_the_no_exception_path_with_trys_else_clause
- rel: related_to
  target_object_id: PAT_prefer_with_as_over_try_finally_when_the_protocol_is_supported
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Expect Exception Propagation to Follow the Call Stack, Not Source Layout

## Pattern Rule
**IF** more than one active `try` statement could match a raised exception — because one function calls another that is itself wrapped in a `try`, or because `try` statements are nested in the source
**THEN** expect Python to jump to the most recently entered matching `except` clause (the one deepest in the current call stack), run only that one handler, and run every `finally` block between the raise point and that handler on the way, even though none of those `finally` blocks stop the exception
**ELSE** with only one active `try` in play, there is nothing to reason about: that `try` either catches the exception or does not

## Do
- Trace which `try` statements are *active* at the moment of the raise — entered but not yet exited — rather than which ones appear nearest in the source text; a `try` in a function three calls up the stack can be "closer" than one textually adjacent to the raise.
- Expect every `finally` block between the raise point and the handler that finally catches it to run, in order, before the handler's own code runs.
- Treat syntactically nested `try` statements and the equivalent runtime nesting (a `try` in a caller wrapping a call into a `try`-free or differently-wrapped callee) as producing identical propagation behavior; the source layout is a convenience, not a separate mechanism.

## Don't
- Don't assume an exception raised deep in a call chain will be caught by a `try` that merely looks close to it in the file; only the nearest *active* handler on the call stack gets the chance, and only the first one.
- Don't expect a caught exception to resume execution at the point it was raised; once a handler catches it, the functions that were exited while propagating are gone, and execution resumes after the handler's own `try` statement.
- Don't assume a `finally` block running during propagation means the exception has been handled; `finally` runs on the way out regardless, and the exception keeps propagating past it unless something else actually catches it.

## Checklist
- For a given raise, has the actual call stack at that moment been traced, rather than inferred from source proximity?
- Are all `finally` blocks between the raise point and the eventual handler accounted for as code that will run during propagation, not as competing handlers?
- Does the code assume resumption at the raise point, when execution will actually resume after whichever `try` statement caught the exception?

## Notes
Python stacks `try` statements as they are entered, and a raised exception searches that stack from the most recently entered try outward, stopping at the first one whose `except` clause matches — the same search whether the nesting came from one function calling another or from `try` statements physically nested in one block. A `finally` block never offers to catch anything; it is guaranteed to run as the stack unwinds past it, which is exactly why it is suited to cleanup actions but cannot be used to decide where an exception ultimately lands.
