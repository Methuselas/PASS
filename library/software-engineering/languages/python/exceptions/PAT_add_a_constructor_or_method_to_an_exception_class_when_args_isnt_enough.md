---
object_id: PAT_add_a_constructor_or_method_to_an_exception_class_when_args_isnt_enough
object_type: pattern
name: Add a Constructor or Method to an Exception Class When args Isn't Enough
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
- class-design
- state
cross_links:
- rel: related_to
  target_object_id: PAT_set_every_instance_attribute_in_init
- rel: related_to
  target_object_id: PAT_override_str_not_repr_for_a_custom_exception_display
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Add a Constructor or Method to an Exception Class When args Isn't Enough

## Pattern Rule
**IF** an exception needs to carry structured context (named fields, not just a flat message) or expose handler-callable behavior (such as logging itself) rather than plain positional display text
**THEN** give the exception class its own `__init__` that sets named instance attributes, and add methods for whatever handler-side behavior should travel with the exception
**ELSE** when the exception only ever needs to show a message, rely on the inherited constructor: passing arguments to the built-in exception superclass's `__init__` already stores them in `self.args` and displays them automatically, with no custom code required

## Do
- Reach for a custom `__init__` the moment the data a handler needs is more than "one message to show" — a line number and a filename, for instance, that a handler wants to use separately rather than read out of a formatted string.
- Access the raised instance in the handler through the `as` name, and read its attributes or call its methods directly from there, rather than parsing information back out of a display string.
- Put logic a handler would otherwise duplicate at every catch site — such as writing a standard log entry — on the exception class itself as a method, so every caller that catches it gets the same behavior by calling one method.
- Let subclasses override an inherited method (like a logging method) to customize behavior for a more specific exception, the same as with any other class.

## Don't
- Don't rely on positional `args` indexing (`X.args[0]`, `X.args[1]`) for data a custom constructor could instead store under a descriptive attribute name; positional access is not self-documenting and breaks silently if the argument order ever changes.
- Don't write a custom `__init__` that forgets to store the data a handler will need; unlike the inherited constructor, a custom one must assign every attribute itself, since it no longer runs the default `args`-storing behavior unless it calls it explicitly.
- Don't duplicate the same handler-side logic (formatting a log line, deciding a response) at every `except` clause that catches this exception when that logic could live once as a method on the exception class itself.

## Checklist
- Does the exception expose the context a handler needs as named attributes, rather than requiring the handler to parse a display string or index into `args`?
- If handler-side behavior is reused across multiple catch sites, does it live as a method on the exception class instead of being duplicated at each site?
- Where a custom `__init__` is defined, does it actually set every attribute a handler will read?

## Notes
An exception class starts with real behavior already built in: the inherited constructor stores whatever you pass it in `self.args` and the inherited display shows it automatically, which is sufficient for exceptions that are really just a message. The moment a handler needs structured, independently addressable context, or needs to trigger the same handling logic from more than one catch site, that default stops being enough — and because an exception is an ordinary class underneath the raise/except machinery, the ordinary tools (a custom constructor for state, methods for behavior, subclassing to specialize both) apply to it exactly as they would to any other class.
