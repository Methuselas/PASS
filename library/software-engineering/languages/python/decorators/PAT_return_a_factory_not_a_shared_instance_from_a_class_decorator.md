---
object_id: PAT_return_a_factory_not_a_shared_instance_from_a_class_decorator
object_type: pattern
name: Return a Factory, Not a Shared Instance, from a Class Decorator for Multiple Instances
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
- classes
- state
cross_links:
- rel: related_to
  target_object_id: PAT_choose_a_closure_variable_or_function_attribute_for_decorator_state
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Return a Factory, Not a Shared Instance, from a Class Decorator for Multiple Instances

## Pattern Rule
**IF** a class decorator wraps instance creation and the decorated class is expected to support more than one independent instance at a time
**THEN** have the decorator return something that builds a fresh wrapper object on every instance-creation call — a nested class whose `__init__` runs per call, or a nested function that constructs and returns a new wrapper — so each call produces its own independent state
**ELSE** when at most one instance should ever exist at all (a genuine singleton), a single shared callable-class instance that reuses itself on every call is exactly the right tool, not a bug to avoid

## Do
- Return a nested class (or an equivalent factory function) from the decorator whenever the decorated class will be instantiated more than once; let that returned callable create a new wrapper object on each instance-creation call.
- Treat "does this decorator need to support multiple instances?" as the first question to settle, since it decides between two shapes that look superficially similar in code but behave oppositely.
- Verify any class decorator intended for general reuse by creating at least two instances of the decorated class and confirming each retains its own independent state.

## Don't
- Don't code a class decorator as a callable class (`__init__` on `@` decoration, `__call__` on instance creation that assigns and returns `self`) if more than one instance is ever needed; `__call__` overwrites the same shared instance's state on every creation call, so the second instance silently replaces the first wherever they share state.
- Don't assume this bug will surface immediately; a test that creates only one instance of the decorated class will pass regardless of which shape was chosen, and the failure appears only once a second instance is created.
- Don't confuse this with the singleton pattern just because both use a callable-class decorator with an instance-overwriting `__call__`; a singleton deliberately wants exactly this reuse, while a general interface-wrapping decorator does not.

## Checklist
- Does the decorator's design assume one instance of the decorated class, or more than one?
- Where multiple instances are expected, does each instance-creation call produce a distinct wrapper object rather than reusing one shared object?
- Has the decorator actually been tested by creating two or more instances and checking that one's state is unaffected by the other's?

## Notes
A class decorator coded as a callable-class instance is itself a single object, created once when the `@` line runs; routing every later instance-creation call through that one object's `__call__` means every call shares whatever state `__call__` sets, including the identity of "the" wrapped instance. A factory — a nested class or function returned by the decorator — sidesteps this by construction: it is called once per instance-creation request, and each call naturally produces its own separate wrapper, which is the same reason a nested-function decorator naturally supports both functions and methods while a callable-class decorator does not.
