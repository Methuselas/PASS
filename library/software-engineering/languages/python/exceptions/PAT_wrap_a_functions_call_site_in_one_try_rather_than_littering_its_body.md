---
object_id: PAT_wrap_a_functions_call_site_in_one_try_rather_than_littering_its_body
object_type: pattern
name: Wrap a Function's Call Site in One try Rather Than Littering Its Body
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
- design
cross_links:
- rel: related_to
  target_object_id: PAT_expect_exception_propagation_to_follow_the_call_stack_not_source_layout
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Wrap a Function's Call Site in One try Rather Than Littering Its Body

## Pattern Rule
**IF** a function's internal operations can raise, and the caller already has one natural place to decide how to respond to any failure from that function
**THEN** let the function run un-wrapped and put a single `try` around the call to it at the call site, so every exception the function can raise percolates up to that one handler
**ELSE** when different operations inside the function genuinely need different recovery actions right where they occur, place `try` statements at those specific points inside the function instead; a single outer `try` cannot express "handle this one operation's failure differently from that one's"

## Do
- Default to wrapping the call, not the callee, when the caller's response to failure is uniform regardless of which internal step actually failed.
- Let exceptions from deep inside a large function propagate untouched through it, relying on the call-stack-based propagation that already carries them to the nearest enclosing handler.
- Reserve a `try` placed inside the function itself for the specific case where that function must react differently depending on which of its own operations failed, or must guarantee a local cleanup action no outer `try` could provide.
- Reassess the wrapping choice as a function grows; a function that originally had one failure mode can grow several that genuinely need distinct internal handling.

## Don't
- Don't scatter a `try` around nearly every statement in a function "to be safe"; each one you add without a distinct recovery action just duplicates the one at the call site while adding nothing but indentation and noise.
- Don't wrap only the call site when some specific internal step actually needs its own recovery action (such as a resource that must be released regardless of what happens to the rest of the function); that need calls for a `try` at the point it applies, not just at the boundary.
- Don't assume "more try statements" means "more robust"; a function wrapped in try statements it doesn't need is harder to read without catching anything a single outer try would have caught anyway.

## Checklist
- Does the caller's handling logic differ depending on which internal operation of the callee actually failed, or is one response enough for any failure from the call?
- Is every `try` inside the function there because it performs a recovery or cleanup action a single outer `try` could not provide?
- As this function has grown, does its original wrap-the-call-site choice still match how many genuinely distinct failure modes it now has?

## Notes
The call-stack-based propagation that exceptions already use makes wrapping the call site free: nothing inside the called function needs to know a handler exists outside it, so a large function can be written as if nothing ever fails, and the one `try` around its call site is where that assumption is reconciled with reality. Each `try` placed instead is a claim that "this specific step needs its own response," and a `try` that cannot make that claim is better removed in favor of the one already covering it from outside.
