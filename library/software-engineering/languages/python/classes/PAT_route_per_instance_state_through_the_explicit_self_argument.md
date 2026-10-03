---
object_id: PAT_route_per_instance_state_through_the_explicit_self_argument
object_type: pattern
name: Route Per-Instance State Through the Explicit self Argument
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
- self
cross_links:
- rel: related_to
  target_object_id: PAT_resolve_names_by_legb_and_let_assignment_decide_scope
- rel: related_to
  target_object_id: PAT_make_classes_care_about_themselves
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Route Per-Instance State Through the Explicit self Argument

## Pattern Rule
**IF** writing a method that reads or changes the state of the object it was called on
**THEN** name the method's first parameter `self` and reach every piece of per-object state through it (`self.attr`), because Python passes the instance to that parameter automatically and provides no implicit alternative path to it
**ELSE** when a function inside a class never touches instance state, say so explicitly with `@staticmethod`, or take the class rather than the instance with `@classmethod`

## Do
- Write `def method(self, ...)` and let the call `obj.method(x)` supply `obj` as `self`; the arguments you pass start at the second parameter.
- Treat `obj.method(x)` and `Cls.method(obj, x)` as the same call written two ways — the first finds the function by inheritance search and then passes `obj`; the second does both steps by hand. The explicit form is how a method is invoked on a specific superclass's version.
- Read a bare name in a method body as an ordinary local or global, and a `self.`-qualified name as instance state; the prefix is the only thing that distinguishes them, which is exactly why Python requires it.
- Keep the name `self` even though the language only cares about position; every reader and tool expects it, and renaming it buys nothing.

## Don't
- Don't omit `self` from a method that uses instance state and then call it on an instance; the instance is passed regardless, so the first real argument silently lands in the wrong parameter.
- Don't try to reach instance state from a bare name inside a method (`data` instead of `self.data`); methods have no implicit access to the instance's namespace, and the bare name resolves by ordinary scope rules — usually to a `NameError` or, worse, an unrelated global.
- Don't use `self` in a function defined outside any class and expect anything special; it is a parameter name, not a keyword, and nothing is passed to it until the function becomes a class attribute.

## Checklist
- Does every method that touches object state take `self` first and qualify that state through it?
- Is any function inside the class body that ignores instance state marked `@staticmethod` or `@classmethod`?
- Does any bare name inside a method mean to refer to an instance attribute?

## Notes
The explicitness is deliberate. Because a plain function can become a method just by being assigned as a class attribute, and a method can be called as a plain function through its class, Python cannot infer an implied subject the way languages with an invisible `this` do. Making the parameter visible also makes the two kinds of names inside a method body unambiguous at a glance: unqualified names follow ordinary scope rules, `self.`-qualified names are instance state.
