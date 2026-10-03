---
object_id: PAT_put_class_only_behavior_in_a_metaclass_not_expecting_instance_inheritance
object_type: pattern
name: Put Class-Only Behavior in a Metaclass, Never Expecting Instance Inheritance
library_path:
- software-engineering
- languages
- python
- metaclasses
stage_binding: 2 block
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- python
- metaclasses
- inheritance
- class-design
cross_links:
- rel: related_to
  target_object_id: PAT_choose_a_class_decorator_over_a_metaclass_unless_construction_or_metaclass_methods_are_needed
- rel: related_to
  target_object_id: PAT_choose_instance_static_or_class_method_by_what_it_needs
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Put Class-Only Behavior in a Metaclass, Never Expecting Instance Inheritance

## Pattern Rule
**IF** behavior or data should be reachable on a class object itself but must never leak to that class's own instances
**THEN** define it as an attribute or method on the metaclass, since classes acquire their metaclass's attributes but normal instances do not
**ELSE** when the behavior should be reachable from ordinary instances too, put it on an ordinary base class instead; normal inheritance reaches instances, metaclass acquisition deliberately does not

## Do
- Define methods meant to process the class as a whole — registries, per-class configuration, class-level computed data — on the metaclass, and call them through the class name (`MyClass.method()`), not through an instance.
- Remember that a metaclass's methods behave like implicit class methods: calling one through the class passes the class itself as the first argument, with no `@classmethod` declaration needed.
- Choose an ordinary superclass instead of a metaclass whenever the same behavior should also be reachable from instances; a metaclass is strictly the narrower tool of the two.

## Don't
- Don't define a metaclass method expecting any instance of the class to inherit it; `I.method()` raises `AttributeError` even though `MyClass.method()` works, because instance inheritance never follows a class's own `__class__` link.
- Don't confuse "the class acquires this from its metaclass" with ordinary inheritance; acquisition through a metaclass and inheritance through `__bases__` are different relationships that happen to look similar in the attribute-access syntax.
- Don't reach for a metaclass just to get class-level data or a class-level computation when a `@classmethod` or an ordinary class attribute on a ordinary base class already does the job without the added inheritance-model complexity.

## Checklist
- Is every attribute placed on a metaclass genuinely meant to be invisible to the class's own instances?
- Where instances also need the behavior, has it been placed on an ordinary base class instead of (or in addition to) the metaclass?
- Has a call through an actual instance been tried, to confirm the metaclass attribute is correctly unreachable there?

## Notes
A class is an instance of its metaclass in exactly the sense that an ordinary object is an instance of its class, and the same one-hop rule applies both times: an object's attribute lookup follows its own `__class__` link once, but does not then continue following that class's own `__class__` link onward to the metaclass. That single-hop limit is what keeps metaclass attributes visible to the class and invisible to the class's instances — the mechanism is consistent, but it inverts a very common intuition that "more class-like" always means "more inheritable."
