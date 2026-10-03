---
object_id: PAT_override_str_not_repr_for_a_custom_exception_display
object_type: pattern
name: Override __str__, Not __repr__, for a Custom Exception Display
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
- dunder-methods
- display
cross_links:
- rel: related_to
  target_object_id: PAT_choose_repr_or_str_by_who_reads_the_display
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Override __str__, Not __repr__, for a Custom Exception Display

## Pattern Rule
**IF** a custom exception class needs its own error message text, shown both when caught and printed and when it reaches the default uncaught-exception handler
**THEN** define `__str__` on the exception class to return that text
**ELSE** defining only `__repr__` does not change what is displayed; the inherited `__str__` from the built-in exception superclass runs instead and your `__repr__` is never consulted for this purpose

## Do
- Define `__str__` on any exception class that needs a message different from its default constructor-argument display.
- Return the message text as a plain string built from the instance's own state, the same way any `__str__` would.
- Keep in mind that this is the one case where `__str__` alone, without a matching `__repr__`, is the complete and correct thing to write.

## Don't
- Don't define `__repr__` expecting it to change an exception's printed message or traceback text; both of those go through `str()`, and the built-in exception superclass's own `__str__` wins over your `__repr__` every time.
- Don't conclude from the general rule of implementing `__repr__` first that the same applies to exceptions; exceptions are the specific case where that general rule does not produce the result you want, because the class you are inheriting from already supplies a working `__str__`.
- Don't assume an exception class needs a custom display at all before checking whether the inherited default — showing the constructor arguments — is already sufficient.

## Checklist
- Does the exception class define `__str__` rather than only `__repr__`, if a custom display is intended?
- Was the custom display actually verified by catching and printing an instance, or by letting one reach the default handler — not just read from the source?
- Is the inherited default display (showing constructor arguments) genuinely insufficient, rather than custom code duplicating it?

## Notes
Every built-in exception inherits a working `__str__` from its superclasses, so an exception class already has display behavior before you write a line of your own code, unlike an ordinary class that starts with only the default object display. Overriding `__repr__` on an ordinary class is enough to change what gets shown almost everywhere, because `print()` and `str()` fall back to `__repr__` when no `__str__` exists — but an exception class is never in that fallback position, since one already exists on its superclass. Only replacing that inherited `__str__` with one of your own actually changes what callers and the default handler see.
