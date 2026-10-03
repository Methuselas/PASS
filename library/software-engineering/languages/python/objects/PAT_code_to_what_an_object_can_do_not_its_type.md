---
object_id: PAT_code_to_what_an_object_can_do_not_its_type
object_type: pattern
name: Code to What an Object Can Do, Not Its Type
library_path:
- software-engineering
- languages
- python
- objects
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: PAT_depend_on_interfaces_not_concrete_classes
tags:
- python
- polymorphism
- duck-typing
- type-checking
- protocols
cross_links:
- rel: related_to
  target_object_id: PAT_depend_on_interfaces_not_concrete_classes
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Code to What an Object Can Do, Not Its Type

## Pattern Rule
**IF** Python code is about to test what type an argument is — `type(x) == list`, `type(x) is dict`, `isinstance(x, list)` — before operating on it
**THEN** drop the test and just use the operations the code needs (iterate it, index it, call `.read()` on it), so every object that supports those operations works, not only the one type you had in mind
**ELSE** when the code genuinely must take different paths for different kinds of input, test against an abstract capability (`collections.abc.Iterable`, `Mapping`, a `typing.Protocol`) rather than a concrete class, and state the accepted interface in a type hint.

## Do
- Write the function against the operations it performs: a total that does `for x in items: t += x` works unchanged on lists, tuples, dictionary keys, ranges, generators and file lines.
- Let an unsupported object fail by itself: a missing operation raises `TypeError` or `AttributeError` at the point of use, which names exactly what the caller's object lacked.
- Document the expected interface with type hints — `Iterable[int]`, `Mapping[str, float]`, or a `Protocol` class listing the methods you call — so readers and static checkers see the contract without a runtime check narrowing it.
- When branching is unavoidable (a function that accepts either one path or many), check the capability: `isinstance(arg, str)` first, because text is itself iterable, then treat any other `Iterable` as many.

## Don't
- Don't compare `type(x) == list` or `type(x) is dict`: it rejects subclasses and every look-alike (a tuple, a generator, a `UserDict`, a custom sequence) that would have worked.
- Don't add type checks "for safety" at the top of every function; each one silently removes flexibility that callers were relying on, and the error it raises is no clearer than the one the operation would have raised.
- Don't convert every input to a list just to make it the expected type; `list(x)` on a large or infinite iterator copies or never finishes.

## Checklist
- Does the function work for any object that supports the operations it uses?
- Where a type test remains, is it against an abstract base class or `Protocol`, and is a concrete branch really needed?
- Is the accepted interface visible in the signature's type hints?
- Is a string handled before generic iterables wherever both are accepted?

## Notes
Python has no type declarations on variables: an object's type is fixed at creation and determines which operations it supports, while names and parameters take any object. Because operations are dispatched on the object, one piece of code serves every type with a compatible interface — the same `+` adds numbers and concatenates sequences. That is polymorphism, and in Python it is the default, not something you design in. A type check is the one construct that turns it off.

Modern Python adds a way to state the interface without checking it: type hints with `collections.abc` types or `typing.Protocol` describe what the code needs, a static checker verifies callers, and the runtime still accepts any object that works. A `@runtime_checkable` Protocol can also serve as the capability test in the rare branch that needs one.
