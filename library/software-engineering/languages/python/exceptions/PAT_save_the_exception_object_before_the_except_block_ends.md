---
object_id: PAT_save_the_exception_object_before_the_except_block_ends
object_type: pattern
name: Save the Exception Object Before the except Block Ends
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
- except
- scoping
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

# Save the Exception Object Before the except Block Ends

## Pattern Rule
**IF** an `except` clause binds the exception with `as name` and that instance is needed after the handler block finishes
**THEN** assign it to a different name inside the handler before the block ends, because the `as` name itself is deleted the moment the `except` block exits
**ELSE** when the instance is only needed inside the handler, the `as` name is sufficient as written and nothing further is required

## Do
- Assign the bound exception to a separate variable — `saved = exc` — as one of the handler's own statements, if anything after the try statement needs to inspect it.
- Expect a reference to the `as` name anywhere outside its own `except` block to fail, including in a later `except` clause, an `else`, a `finally`, or code after the whole try statement.
- Use a name for the `as` binding that is not already in use for something needed afterward, since the deletion removes whatever that name pointed to as well, not just the exception.

## Don't
- Don't expect the `as` name to behave like an ordinary assignment that outlives its block; it is intentionally removed on exit to avoid keeping the traceback alive, and the removal happens even if the name is reassigned inside the block.
- Don't try to work around this by widening the `except` block to include the later code instead of saving the reference; that changes what the handler is considered to catch.

## Checklist
- Is any `as`-bound exception name referenced outside the `except` block that bound it?
- Where the exception instance is needed later, has it been copied to a name that is not the `as` binding itself?
- Does the chosen separate name avoid colliding with a variable the surrounding code still needs?

## Notes
The `as` name is deleted specifically because an exception instance keeps a reference to the call stack active when it was raised, and leaving that reference reachable after the handler would hold the whole stack in memory for no purpose. The deletion is unconditional — it happens whether or not the name was reassigned inside the block — so the only reliable way to keep the exception around is to copy it to a name of your own before the block ends.
