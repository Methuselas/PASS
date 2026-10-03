---
object_id: PAT_compare_values_with_eq_and_reserve_is_for_singletons
object_type: pattern
name: Compare Values with == and Reserve is for Singletons
library_path:
- software-engineering
- languages
- python
- objects
stage_binding: 3 rough
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- python
- equality
- identity
- none
- sentinels
cross_links:
- rel: related_to
  target_object_id: PAT_copy_a_shared_mutable_object_to_the_depth_the_change_reaches
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Compare Values with == and Reserve is for Singletons

## Pattern Rule
**IF** Python code compares two objects
**THEN** use `==` when the question is whether they have the same value, and use `is` only when the question is whether they are the very same object — in practice `None`, a sentinel object you created, or a deliberate check for sharing
**ELSE** when a comparison with `is` happens to work on numbers or strings, treat that as an accident of caching and change it to `==`.

## Do
- Test for absence with `x is None` and `x is not None`; `None` is a single object, and `is` cannot be fooled by a class that overrides `==`.
- Create a private sentinel with `_MISSING = object()` when `None` is a legitimate value, and test it with `is`.
- Use `a is b` to diagnose aliasing: it answers whether a change through one name will be seen through the other.

## Don't
- Don't write `x is 42` or `name is 'spam'`. Small integers and short strings are cached, so these often succeed, but values built at run time are separate objects: `int('1000') is int('1000')` is `False`. Python 3.8 and later emit `SyntaxWarning: "is" with 'int' literal` for exactly this.
- Don't use `==` to check for `None`; an object's `__eq__` can claim equality with anything.
- Don't compare lists, dicts or other containers with `is` to ask whether they hold the same items; two separately built equal lists are `==` but not `is`.

## Checklist
- Does every `is` compare against `None`, a sentinel, or an intentional identity check?
- Is any literal on either side of an `is`?
- Would the test still be right if the values were built at run time rather than typed as literals?

## Notes
`==` calls the objects' equality method and compares values; `is` compares object identity, which is the reference itself. Because Python caches and reuses some immutable objects as an optimization, identity can coincide with equality for small values in one interpreter and not in another, so an `is` test on values passes in quick experiments and fails in production data.
