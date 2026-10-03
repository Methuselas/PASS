---
object_id: PAT_choose_a_class_decorator_over_a_metaclass_unless_construction_or_metaclass_methods_are_needed
object_type: pattern
name: Choose a Class Decorator Over a Metaclass Unless Construction or Metaclass Methods Are Needed
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
- decorators
- class-design
cross_links:
- rel: related_to
  target_object_id: PAT_return_a_factory_not_a_shared_instance_from_a_class_decorator
- rel: related_to
  target_object_id: PAT_put_class_only_behavior_in_a_metaclass_not_expecting_instance_inheritance
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Choose a Class Decorator Over a Metaclass Unless Construction or Metaclass Methods Are Needed

## Pattern Rule
**IF** the task is to augment or manage a class after it already exists — adding methods, registering it, wrapping every method of it with the same function decorator — or to manage the instances it creates
**THEN** use a class decorator; it runs on the already-built class and achieves the same result with far less machinery
**ELSE** reach for a metaclass only when the task needs to influence the class object's actual construction (a custom `__new__`, before the class exists at all) or needs methods that are callable on the class itself but deliberately invisible to the class's own instances

## Do
- Default to a class decorator for the common cases: adding or replacing methods, registering a class to some lookup table, or wrapping every method of a class with another decorator.
- Reach for a metaclass's `__new__` specifically when the class's namespace dictionary, base classes, or very shape must be altered before the class object is created, not merely patched afterward.
- Use a metaclass when the goal is a method reachable through the class itself but never through its instances — a capability decorators have no equivalent for — rather than trying to approximate it with class attributes and instance-level checks.
- Let a metaclass declaration be inherited naturally when every subclass in a hierarchy should pick up the same construction-time behavior; this composes with further subclassing in a way a one-off decorator call does not.

## Don't
- Don't reach for a metaclass to manage normal instance creation calls (wrapping instances in a proxy); it works, but it forces you to build the class object by hand inside the metaclass function, an extra step a class decorator never needs.
- Don't assume a metaclass gives you something a decorator fundamentally cannot for ordinary augmentation tasks (adding methods, registering, wrapping methods); for these, the two tools produce the identical end result, and the decorator reaches it with less code.
- Don't choose a metaclass "because it seems more powerful" without a concrete need for construction-time control or metaclass-only methods; the extra conceptual weight is real and should be paid for by an actual requirement.

## Checklist
- Does this task need to change the class before it is constructed, or is it only ever modifying a class that already exists?
- Does anything here require a method callable through the class but intentionally absent from its instances?
- If a metaclass is already chosen, would the same result be reachable with a class decorator at a fraction of the code?

## Notes
Both tools run at the same moment — the end of a `class` statement — which is exactly why their common cases overlap so completely: a class decorator receives the already-constructed class and can modify or replace it, while a metaclass is itself responsible for making that class in the first place. That timing difference is the whole story. Tasks that only ever touch a class after it exists cost nothing extra as a decorator; tasks that must shape the class's construction, or that want behavior reachable only through the class and not its instances, have no decorator equivalent and are what metaclasses exist for.
