---
object_id: PAT_dispatch_through_the_caught_instances_own_methods_rather_than_sys_exc_info
object_type: pattern
name: Dispatch Through the Caught Instance's Own Methods Rather Than sys.exc_info
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
- sys-exc-info
- polymorphism
cross_links:
- rel: related_to
  target_object_id: PAT_add_a_constructor_or_method_to_an_exception_class_when_args_isnt_enough
- rel: related_to
  target_object_id: PAT_give_a_librarys_exceptions_a_common_category_superclass
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Dispatch Through the Caught Instance's Own Methods Rather Than sys.exc_info

## Pattern Rule
**IF** a handler's behavior should differ depending on which specific exception within a caught category was actually raised, and the `except` clause already binds the instance with `as`
**THEN** call a method on that instance (or branch on an attribute it carries) to get type-appropriate behavior, rather than inspecting the exception's type through `sys.exc_info` or an explicit type test
**ELSE** only reach for `sys.exc_info()` when there is no `as` binding to work with at all — most commonly inside an empty `except` clause, where it is the only way to get at the exception that occurred

## Do
- Give exception classes in a category methods that each override to do the right type-specific thing, then call that method generically from the handler instead of testing which subclass was caught.
- Use the `as`-bound instance's own attributes and methods as the normal way to get both the exception's data and its type-appropriate behavior.
- Reserve `sys.exc_info()` for genuinely instance-less contexts, such as an empty `except:` clause with no `as` name to bind, or logging code that must report on whatever was most recently raised without having caught it directly.

## Don't
- Don't call `sys.exc_info()` inside a handler that already has the instance available through `as`; everything it would give you — the class and the instance — is already sitting in that name.
- Don't write an `if`/`elif` chain that tests the caught instance's class or type to decide what to do; that duplicates, in the handler, a decision that a method defined per exception class already makes polymorphically.
- Don't assume being more specific about exception types is automatically more correct; a handler that works through generic instance methods instead of type tests tends to keep working as new, more specific exception subclasses are added later.

## Checklist
- Where an `as` binding is available, does the handler use the instance directly instead of calling `sys.exc_info()` for information already in hand?
- Where behavior should vary by exception subtype, does that variation live in a method each subclass overrides, rather than in a type-testing chain inside the handler?
- Is every remaining use of `sys.exc_info()` in a context that genuinely has no bound instance to work with instead?

## Notes
`sys.exc_info()` exists to answer "what was just raised?" in a context that has no other way to ask — chiefly an empty `except` clause, which binds nothing at all. Once a handler names the exception with `as`, that question is already answered: the instance is sitting in the handler's own namespace, with its class reachable through `__class__` and its behavior reachable through whatever methods its class defines. Preferring the instance's own methods over a type check on it is the same preference software has for polymorphism over conditionals generally — it lets a new exception subclass slot into existing handlers by defining its own version of the method, rather than requiring every handler's type-testing chain to be found and extended.
