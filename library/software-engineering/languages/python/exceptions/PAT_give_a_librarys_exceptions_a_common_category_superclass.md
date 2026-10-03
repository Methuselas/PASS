---
object_id: PAT_give_a_librarys_exceptions_a_common_category_superclass
object_type: pattern
name: Give a Library's Exceptions a Common Category Superclass
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
- api-design
cross_links:
- rel: related_to
  target_object_id: PAT_inherit_user_defined_exceptions_from_exception_not_baseexception
- rel: related_to
  target_object_id: PAT_catch_the_specific_built_in_exception_subclass_instead_of_sniffing_errno
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Give a Library's Exceptions a Common Category Superclass

## Pattern Rule
**IF** code (a library, module, or any boundary other call sites depend on) can raise more than one kind of exception that callers might reasonably want to catch as a group
**THEN** define a shared superclass for the category and make each specific exception inherit from it, so a caller can catch the whole category by naming the superclass once
**ELSE** when there is genuinely only one exception type and no plan to add related ones, a single class deriving directly from `Exception` is enough; a category superclass with one subclass underneath it is ceremony with nothing to organize

## Do
- Create one category superclass per family of related failures, and derive each specific exception from it rather than from `Exception` directly.
- Let callers catch the category by naming only the superclass; a caller who needs to distinguish specific members can still inspect the caught instance's class.
- Add new specific exceptions later as new subclasses of the existing category superclass; existing code that catches the category keeps working without being revisited.
- Document the category superclass as the stable, supported thing to catch, since that is the promise that lets you add subclasses safely later.

## Don't
- Don't ship a set of unrelated standalone exception classes from one module and expect callers to list every one of them in a tuple; that list breaks every time you add a new exception type.
- Don't tell callers to use a bare `except` or `except Exception` just to avoid updating their except lists; that also catches things that have nothing to do with your library, including process exit signals and genuine bugs elsewhere in the caller's own code.
- Don't skip the category superclass because there is only one exception today if you already know more are coming; retrofitting a superclass underneath an exception already in the wild changes its class identity for anyone pattern-matching on it directly.

## Checklist
- Can a caller catch "any error from this library" by naming exactly one class?
- When a new, more specific exception is added, does every existing caller that catches the category keep working unchanged?
- Is the category superclass itself documented as the thing callers should catch, rather than an implementation detail?

## Notes
The mechanism behind this is superclass matching: an `except` clause catches the named class and everything beneath it in the inheritance tree, so a category superclass with no behavior of its own still does real work by giving every present and future subclass a single name to be caught by. Without it, a caller's only options are to list every specific exception by name — which breaks the moment the library adds one — or to catch something far too broad, which starts intercepting unrelated failures the caller never meant to handle. The superclass is what lets the library's exception set grow without ever forcing a caller's except clauses to change.
