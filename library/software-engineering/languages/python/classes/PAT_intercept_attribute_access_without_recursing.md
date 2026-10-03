---
object_id: PAT_intercept_attribute_access_without_recursing
object_type: pattern
name: Intercept Attribute Access Without Recursing
library_path:
- software-engineering
- languages
- python
- classes
stage_binding: 2 block
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- python
- classes
- attributes
- protocols
cross_links:
- rel: related_to
  target_object_id: PAT_redefine_the_dunder_methods_a_wrapper_must_forward
- rel: related_to
  target_object_id: PAT_fetch_an_attribute_dynamically_with_getattr
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Intercept Attribute Access Without Recursing

## Pattern Rule
**IF** a class must run code when its attributes are read, assigned, or deleted — to delegate to a wrapped object, compute a value on demand, or validate an assignment
**THEN** use `__getattr__` for reads of names that do not otherwise exist and `__setattr__` for assignments, and inside `__setattr__` always store through `object.__setattr__(self, name, value)` rather than `self.name = value`, which would call `__setattr__` again and recurse until the stack is exhausted
**ELSE** when only one or two specific attributes need managing, use `@property` instead — it is scoped to the names you name, so it cannot recurse and cannot accidentally intercept everything else

## Do
- Use `__getattr__` for the fallback case only: it runs just for names normal lookup did not find, so ordinary attributes keep their usual speed and behavior.
- Raise `AttributeError` from `__getattr__` for names the class genuinely does not provide; callers, `hasattr`, and `getattr`'s default argument all depend on that signal.
- Store through `object.__setattr__(self, name, value)` inside `__setattr__`; it works whether or not the instance has a `__dict__`, which matters for classes using `__slots__` or properties.
- Prefer `@property` for a managed attribute with a known name — a getter, optional setter, and no risk of intercepting unrelated names.
- Treat `__delattr__` the same as `__setattr__`: route the actual deletion through `object.__delattr__` to avoid the same loop.

## Don't
- Don't assign to any `self` attribute inside `__setattr__`, including one with a different name. Every assignment anywhere in the class routes back through `__setattr__`, so even `self.other = 99` re-enters it.
- Don't reach for `__getattribute__` when `__getattr__` will do. `__getattribute__` runs for *every* attribute access, including the ones your own method body makes, so it loops far more easily and slows down all access.
- Don't expect `__getattr__` to intercept operator-overloading methods on a wrapper; implicit dunder lookup bypasses it entirely.
- Don't use these hooks to fake private attributes as a security measure. They can make misuse inconvenient, which is useful, but any caller who wants the value can still reach it.

## Checklist
- Does every write inside `__setattr__` go through `object.__setattr__` rather than plain assignment?
- Does `__getattr__` raise `AttributeError` for names it does not handle?
- Would `@property` cover this case with less reach and no recursion risk?
- Does anything in the class rely on `self.__dict__` existing, in a class that might later gain `__slots__`?

## Notes
The recursion trap exists because these hooks are installed at the level of the operation, not the name: `__setattr__` catches every assignment made on an instance of the class, including the ones its own body performs. Breaking the loop therefore means reaching a storage mechanism that does not go through your class at all, which is exactly what `object.__setattr__` provides. `__getattr__` has no such problem, because it only runs when normal lookup already failed — and that difference is also why it is the safer of the two to reach for.
