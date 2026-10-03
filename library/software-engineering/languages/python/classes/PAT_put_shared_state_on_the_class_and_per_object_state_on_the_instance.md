---
object_id: PAT_put_shared_state_on_the_class_and_per_object_state_on_the_instance
object_type: pattern
name: Put Shared State on the Class and Per-Object State on the Instance
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
- state
cross_links:
- rel: related_to
  target_object_id: PAT_set_every_instance_attribute_in_init
- rel: related_to
  target_object_id: PAT_copy_a_shared_mutable_object_to_the_depth_the_change_reaches
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Put Shared State on the Class and Per-Object State on the Instance

## Pattern Rule
**IF** deciding where an attribute of a class-based object should live
**THEN** assign it in the class body when every instance should see one shared value — a constant, a registry, a method — and assign it to `self` in `__init__` when each object needs its own copy, because an attribute *fetch* searches instance then class, while an attribute *assignment* only ever writes the object it is applied to
**ELSE** when the shared value is mutable and instances need their own, put an immutable sentinel (such as `None`) in the signature and build the real object per instance inside `__init__`

## Do
- Put genuinely shared, read-only data in the class body: version strings, lookup tables, counters of class-wide facts, and the methods themselves.
- Build every mutable per-object value (`[]`, `{}`, `set()`) inside `__init__` so each instance owns a distinct object.
- Expect `self.x = v` inside a method to create or replace the attribute on *that instance*, leaving the class attribute of the same name untouched and still visible to every other instance.
- Change a class-wide value through the class (`Cls.count += 1`), not through an instance (`self.count += 1`), which instead creates a new instance attribute that shadows the class one from then on.
- Use the shadowing behavior deliberately when it helps: a class attribute makes a perfectly good default that an instance may override by assignment.

## Don't
- Don't put a mutable default in the class body expecting per-instance storage; `class Basket: items = []` gives every basket the same list, and one `append` is visible from all of them.
- Don't assume an attribute you can read on an instance lives on that instance — it may be inherited from the class or any superclass, and `instance.__dict__` will not show it.
- Don't reach for a class attribute as a cheap global; a value shared by every instance of a type is shared mutable state with all of that term's usual costs.

## Checklist
- Is every mutable attribute built per instance in `__init__` rather than sitting in the class body?
- Does any `self.x = ...` intend to change a class-wide value? If so, it does not — it shadows it.
- For each class-body attribute, is one value genuinely correct for every instance that will ever exist?

## Notes
The asymmetry is the whole rule: attribute reference climbs the tree (instance, then its class, then superclasses bottom-up and left-to-right, stopping at the first hit), while attribute assignment never climbs at all. Every surprising class-attribute bug is some version of reading through the link and then expecting a write to follow the same path back.
