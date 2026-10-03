---
object_id: PAT_use_nested_functions_not_callable_classes_for_decorators_that_wrap_methods
object_type: pattern
name: Use Nested Functions, Not Callable Classes, for Decorators That Must Wrap Methods
library_path:
- software-engineering
- languages
- python
- decorators
stage_binding: 2 block
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- python
- decorators
- methods
- closures
cross_links:
- rel: related_to
  target_object_id: PAT_choose_a_closure_variable_or_function_attribute_for_decorator_state
- rel: related_to
  target_object_id: PAT_write_a_descriptor_class_to_reuse_managed_attribute_logic
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Use Nested Functions, Not Callable Classes, for Decorators That Must Wrap Methods

## Pattern Rule
**IF** a function decorator must work correctly on both plain functions and class-level methods
**THEN** implement it as a decorator function returning a nested function (a closure), not as a class whose instances implement `__call__`
**ELSE** when a decorator will only ever be applied to plain, module-level functions and never to methods, a callable-class wrapper works fine and may be simpler to extend with helper methods

## Do
- Write the decorator as `def decorator(func): def wrapper(*args, **kwargs): ...; return wrapper` whenever methods are a possible target.
- Let the nested `wrapper` function receive the subject instance as its own first positional argument when wrapping a method; this happens automatically because Python creates a bound method only when the attribute is a plain function, which a nested-function decorator produces.
- Verify any new decorator intended for general use by applying it to at least one class method, not only to a standalone function, before considering it finished.

## Don't
- Don't decorate a method with a callable-class decorator (`class decorator: def __init__(self, func): ...; def __call__(self, *args): ...`) and expect `self` inside `__call__` to be the subject instance; `self` there is always the decorator instance, and the actual subject instance is simply missing from `*args`.
- Don't conclude a callable-class decorator is broken just because it works fine on plain functions; the failure is specific to methods, and a decorator exercised only against standalone functions will look completely correct until someone applies it to a class.
- Don't reach for a descriptor-based (`__get__`) fix as the first solution to this problem; it produces the same correct result with substantially more code and an extra call per access, and is better treated as a fallback for cases a nested function genuinely cannot handle.

## Checklist
- Is the decorator's wrapping logic a nested function returned from the decorator, rather than a `__call__` method on a decorator-class instance?
- Has the decorator actually been applied to and tested against a class method, not only a plain function?
- Where a callable class is used anyway, is it certain the decorator will never be asked to wrap a method?

## Notes
The failure has nothing to do with the decorator's logic and everything to do with how Python builds bound methods: an attribute that is a plain function gets wrapped in a bound method at access time, which is what inserts the instance as the first argument; an attribute that is an instance of some other callable class does not get this treatment, so no instance is ever inserted. A decorator coded as nested functions produces exactly the plain-function shape Python expects, which is why it works uniformly on both functions and methods without special-casing either.
