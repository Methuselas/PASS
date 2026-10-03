---
object_id: PAT_redefine_the_dunder_methods_a_wrapper_must_forward
object_type: pattern
name: Redefine the Dunder Methods a Wrapper Must Forward
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
- delegation
- composition
cross_links:
- rel: related_to
  target_object_id: PAT_fetch_an_attribute_dynamically_with_getattr
- rel: related_to
  target_object_id: PAT_overload_an_operator_only_to_mimic_a_builtin_interface
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Redefine the Dunder Methods a Wrapper Must Forward

## Pattern Rule
**IF** a class wraps another object and forwards attribute access to it with `__getattr__`
**THEN** define explicitly, on the wrapper itself, every operator-overloading method the wrapped object supports and callers will use — `__repr__`, `__len__`, `__eq__`, `__iter__`, and the rest — because `__getattr__` will never see them
**ELSE** when the wrapper genuinely is a specialized kind of the wrapped type rather than a separate object holding one, inherit from it instead and the problem does not arise

## Do
- Write one small forwarding method per protocol the wrapper needs: `def __repr__(self): return repr(self._inner)`, and the same shape for anything else callers depend on.
- Decide deliberately which protocols the wrapper exposes; a proxy that forwards everything is claiming to be substitutable for what it wraps, which is a stronger promise than most wrappers can keep.
- Keep `__getattr__` for ordinary named attributes and methods, where it does work and saves writing one forwarder per name.
- Prefer inheritance when the relationship really is is-a: a subclass gets every inherited dunder for free and needs none of this bookkeeping.
- Exercise a wrapper through the operations callers actually perform — printing it, comparing it, taking its length, iterating it — rather than only through named method calls, since the named calls are the ones that work by accident.

## Don't
- Don't expect `__getattr__` to intercept dunder lookups. It runs only for attributes not found by normal means, and every class inherits default implementations of `__repr__`, `__str__`, `__eq__`, `__hash__` and others from `object` — so those are always found, and the hook never fires.
- Don't expect assigning a dunder onto an instance to help either; implicit invocations by operators and built-ins look the method up on the type and bypass the instance entirely.
- Don't conclude the forwarding works because an explicit call such as `wrapper.__repr__()` returns a string; that is `object`'s inherited default, the same wrong answer `print()` gives.
- Don't silently keep `object`'s identity-based `__eq__` and `__hash__` on a wrapper meant to compare equal to what it wraps; those defaults compare wrappers by identity and nothing warns you.

## Checklist
- Does the wrapper define, by hand, each operator-overloading method its callers rely on?
- Has the wrapper been exercised through printing, comparison and iteration, not just named method calls?
- Would plain inheritance express this relationship more honestly than wrapping plus forwarding?

## Notes
Two independent rules combine into this trap. First, `__getattr__` is a fallback for *undefined* attributes, and `object` defines a great many dunders, so they are never undefined. Second, implicit special-method lookup — what the interpreter does to evaluate `a + b` or `print(x)` — goes to the type and skips both the instance and those fallbacks. Delegation therefore reaches ordinary methods automatically and protocol methods not at all, which is the main hidden cost of choosing composition over inheritance in Python.
