---
object_id: PAT_inherit_user_defined_exceptions_from_exception_not_baseexception
object_type: pattern
name: Inherit User-Defined Exceptions from Exception, Not BaseException
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
- inheritance
cross_links:
- rel: related_to
  target_object_id: PAT_catch_exception_not_a_bare_except_for_a_catchall
- rel: related_to
  target_object_id: PAT_give_a_librarys_exceptions_a_common_category_superclass
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Inherit User-Defined Exceptions from Exception, Not BaseException

## Pattern Rule
**IF** you are defining a new exception class for your own application or library
**THEN** derive it from `Exception` (directly, or through a category superclass that itself derives from `Exception`), never from `BaseException` directly
**ELSE** there is no current case where an application-level exception should skip `Exception`; `BaseException` is reserved for the small, fixed set of system-exit style exceptions Python itself defines

## Do
- Derive every custom exception class from `Exception`, whether directly or through a category superclass placed between them.
- Let a category superclass (see the related pattern on grouping a library's exceptions) also derive from `Exception`, so both the category and its members stay catchable by `except Exception`.
- Treat "derives from `Exception`" as a basic requirement to check on any new exception class, the same way you would check a required base class for any other interface.

## Don't
- Don't derive a new exception from `BaseException` directly; doing so removes it from everything that catches `Exception` as a catchall, so handlers written with the normal, safe catchall convention silently stop seeing it.
- Don't assume `BaseException` is simply "the more general version" of `Exception` and therefore the safer choice to inherit from; it is reserved for conditions meant to bypass ordinary application-level handling, such as a requested program exit.
- Don't forget this requirement because the body of the exception class is empty; a class with nothing but `pass` still carries all the consequences of whichever base it names.

## Checklist
- Does every custom exception class derive from `Exception`, directly or through a category superclass that itself derives from `Exception`?
- Is any custom exception class derived from `BaseException` directly, and if so, is that truly intended to escape ordinary catchall handling?
- Would `except Exception` in calling code actually catch this exception, as its author would expect?

## Notes
`Exception` exists specifically to split ordinary application errors from `BaseException`'s other direct subclasses — `SystemExit`, `KeyboardInterrupt`, and `GeneratorExit` — which represent requests to stop rather than conditions to handle and recover from. Deriving a custom exception from `Exception` is what makes `except Exception` work as the safe, conventional catchall: it reliably includes every application-level error precisely because that convention — and the whole ecosystem of code that catches `Exception` expecting to see application errors — depends on every such exception actually living under `Exception` in the class tree.
