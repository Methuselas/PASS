---
object_id: PAT_choose_instance_static_or_class_method_by_what_it_needs
object_type: pattern
name: Choose Instance, Static, or Class Method by What It Needs
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
- methods
- decorators
cross_links:
- rel: related_to
  target_object_id: PAT_route_per_instance_state_through_the_explicit_self_argument
- rel: related_to
  target_object_id: PAT_put_shared_state_on_the_class_and_per_object_state_on_the_instance
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Choose Instance, Static, or Class Method by What It Needs

## Pattern Rule
**IF** writing a function inside a class
**THEN** pick its kind by what it actually uses: an ordinary instance method taking `self` when it touches per-object state, `@classmethod` taking `cls` when it needs the class — to build an instance a different way or to read or update per-class data — and `@staticmethod` when it needs neither and is grouped with the class only for discoverability
**ELSE** when it needs nothing from the class at all and no caller will look for it there, make it a module-level function instead

## Do
- Use `@classmethod` for alternative constructors — `from_json`, `from_file` — and return `cls(...)` rather than the hardcoded class name, so a subclass calling it gets an instance of itself.
- Use `@classmethod` for state that should differ per class in a hierarchy; the method receives the most specific class of the call, so each subclass can carry its own copy.
- Hardcode the class name instead, in an ordinary or static method, when the data genuinely belongs to one class and must stay shared across every subclass.
- Use `@staticmethod` for a helper that belongs to the class conceptually — a small conversion or validation used by its methods — and that would otherwise clutter the module namespace.
- Declare `@staticmethod` even on a self-less method that is currently only called through the class, because an instance-level call would otherwise pass an instance the method has no parameter for.

## Don't
- Don't assume a `@classmethod` always receives the class that defined it; it receives the class the call was made through, so updating `cls.counter` from an inherited method writes to the *subclass*, creating a new attribute there and leaving the base untouched.
- Don't reach for `@staticmethod` as a way to avoid thinking about `self`; if the function reads or changes object state, it is an instance method with a missing parameter.
- Don't use a class as a namespace for unrelated functions; a module already is one, and functions placed in a class imply a connection to its objects.
- Don't make an alternative constructor a `@staticmethod` returning a hardcoded class; subclasses then silently get base-class instances from it.

## Checklist
- Does each method use `self`, use `cls`, or use neither — and does its declaration match?
- Does any `@classmethod` write to `cls` attributes where writing to a subclass would be wrong?
- Do alternative constructors return `cls(...)` so subclasses work?
- Would any `@staticmethod` here be better placed as a module-level function?

## Notes
The three kinds differ in exactly one respect: what gets inserted as the first argument. An instance method gets the instance, a class method gets the class, a static method gets nothing. Everything else — inheritance, overriding, the way they are looked up — is identical, which is why the choice is settled entirely by what the body needs. The one sharp edge is that a class method's `cls` is the class the call came through rather than the one the method was written in, which makes class methods excellent for per-subclass data and a trap for data meant to be shared by the whole hierarchy.
