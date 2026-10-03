---
object_id: PAT_extend_a_superclass_method_by_calling_it_through_super
object_type: pattern
name: Extend a Superclass Method by Calling It Through super
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
- inheritance
- super
cross_links:
- rel: related_to
  target_object_id: PAT_set_every_instance_attribute_in_init
- rel: related_to
  target_object_id: PAT_route_per_instance_state_through_the_explicit_self_argument
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Extend a Superclass Method by Calling It Through super

## Pattern Rule
**IF** a subclass overrides a method (including `__init__`) but still needs what the superclass version does
**THEN** call the inherited version from inside the override with `super().method(args)` and add only the difference, rather than copying the superclass body and editing it
**ELSE** when the override deliberately *replaces* the superclass behavior rather than extending it, omit the `super()` call entirely — that is a real choice, and the only one that should leave the superclass version unrun

## Do
- Write `super().__init__(...)` in a subclass constructor whenever the superclass sets up state; Python automatically runs only the lowest `__init__` in the tree, so any higher one that must run has to be called explicitly.
- Pass only the arguments the superclass expects, adjusting them to express the customization — a manager raise that adds a bonus becomes `super().give_raise(percent + bonus)`, which leaves the actual raise arithmetic in exactly one place.
- Use the no-argument `super()` form inside a class body; it resolves against the current class's method resolution order, so inserting or reordering classes later does not require editing every call site.
- Reach for the explicit `Base.method(self, ...)` form only when you deliberately mean one specific class's implementation rather than the next one in the MRO — and expect to pass `self` yourself, because only calls made through an instance get it filled in automatically.
- Keep one convention per hierarchy: a tree that mixes `super()` in some classes and hardcoded superclass names in others stops dispatching predictably as soon as more than one base is involved.

## Don't
- Don't copy a superclass method body into the subclass and edit it; that creates two places to change, and the copy stops tracking the original the moment either is touched.
- Don't call `self.method(...)` inside that same method's override expecting the superclass version. `self` is still the subclass instance, so the search finds the override again and recurses until the interpreter runs out of stack.
- Don't skip `super().__init__()` by accident; an instance whose superclass constructor never ran is missing exactly the attributes that constructor was responsible for, and the failure surfaces later and elsewhere.
- Don't read `super()` as "my superclass". It means the next class in this instance's method resolution order, which under multiple inheritance can be a sibling branch rather than the class named in the header.

## Checklist
- Does every override that needs the inherited behavior call it rather than reproduce it?
- Does every subclass `__init__` relying on superclass state call `super().__init__(...)`?
- Is the whole hierarchy consistent about `super()` versus explicitly named base calls?
- Does any override call back into itself through `self` by mistake?

## Notes
A call written `instance.method(args)` is resolved to `class.method(instance, args)` by the inheritance search, which is why calling through a class directly works at all, and why that form needs `self` passed by hand. `super()` drives the same machinery but picks the class from the method resolution order instead of from a name hardcoded in the body. The difference is invisible in a single-inheritance chain and decisive once a hierarchy has more than one base — which is the case where a hardcoded name is most likely to be wrong.
