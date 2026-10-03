---
object_id: PAT_catch_the_specific_built_in_exception_subclass_instead_of_sniffing_errno
object_type: pattern
name: Catch the Specific Built-in Exception Subclass Instead of Sniffing errno
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
- built-ins
- os-errors
cross_links:
- rel: related_to
  target_object_id: PAT_give_a_librarys_exceptions_a_common_category_superclass
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Catch the Specific Built-in Exception Subclass Instead of Sniffing errno

## Pattern Rule
**IF** code needs to respond differently to a specific operating-system-level failure (a missing file, a permission problem, and the like)
**THEN** catch the specific built-in exception subclass for that condition (`FileNotFoundError`, `PermissionError`, and the other `OSError` subclasses), rather than catching the broader category and branching on an error-number attribute
**ELSE** when no specific subclass exists for the condition, catch the closest category (`OSError` or another appropriate superclass) and inspect its attached data

## Do
- Catch the exact subclass that names the condition you mean to handle; let it, not an error number, carry the meaning.
- Reserve catching a broader category like `OSError` for code that genuinely means to handle a range of operating-system failures the same way, or that must fall back to inspecting attached data because no more specific subclass applies.
- Read error-numbering attributes as a last resort, for conditions the built-in hierarchy has not given a dedicated subclass to, not as the default way to distinguish common cases that already have one.

## Don't
- Don't branch on an error-number attribute to distinguish conditions that already have their own built-in exception subclass; that branch duplicates a distinction the class hierarchy already makes, in a way a reader has to cross-reference against a numeric code table to follow.
- Don't catch the broad category and silently handle only one error number inside it while letting every other member of that category fall through the same branch unexamined; catching the specific subclass makes that scope explicit instead of implicit in an `if`.
- Don't assume every operating-system failure has its own specific subclass; where none exists, catching the category and reading the attached data is still the correct fallback, not a sign something was missed.

## Checklist
- Where a specific built-in exception subclass exists for the condition being handled, is that subclass named in the `except` clause rather than a broader category?
- Where a broader category is caught, is that because the code genuinely handles a range of conditions uniformly, or because no more specific subclass exists?
- Would a reader be able to tell which operating-system conditions this code responds to from the `except` clauses alone, without reading into the handler body?

## Notes
Catching by class and catching by error code answer the same question through different mechanisms, and the class-based answer is the one the language itself now maintains: each specific subclass is the hierarchy's own name for a condition that used to require reading a numeric code out of an attribute and comparing it by hand. Where that subclass exists, naming it directly moves the distinction out of the handler's logic and into the `except` clause where it is visible at a glance; where it does not, falling back to the category and its attached data remains the only option, and is not a workaround so much as the hierarchy's own escape hatch for conditions it has not (yet) given a dedicated name.
