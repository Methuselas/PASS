---
object_id: PAT_define_set_to_make_a_descriptor_attribute_read_only
object_type: pattern
name: Define __set__ to Make a Descriptor Attribute Read-Only
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
- descriptors
- immutability
cross_links:
- rel: related_to
  target_object_id: PAT_write_a_descriptor_class_to_reuse_managed_attribute_logic
- rel: related_to
  target_object_id: PAT_add_a_computed_or_validated_attribute_with_property
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Define __set__ to Make a Descriptor Attribute Read-Only

## Pattern Rule
**IF** a descriptor-managed attribute should reject assignment
**THEN** define `__set__` on the descriptor and raise an exception (typically `AttributeError` or `TypeError`) from it
**ELSE** simply omitting `__set__` does not make the attribute read-only; it only means the descriptor has nothing to say about assignment, and an ordinary instance-attribute assignment will go through instead

## Do
- Define `__set__` explicitly and raise from it whenever a descriptor-managed name must be truly immutable from the outside.
- Remember that a descriptor with a defined `__set__` is a *data descriptor*, which Python's attribute lookup gives precedence over an instance's own `__dict__` — this is exactly the property that makes the raise effective.
- Contrast this deliberately with `@property`: omitting a property's setter already makes assignment raise `AttributeError` automatically, so the equivalent behavior needs no extra code there — the descriptor case is the one that needs an explicit raising `__set__`.
- Test the read-only guarantee by actually attempting an assignment on an instance, not by inspecting the descriptor's source for a `__set__` method's absence.

## Don't
- Don't assume a descriptor with only `__get__` is read-only; assigning to that attribute name on an instance creates a same-named entry in the instance's own `__dict__`, which then shadows the descriptor for every future read on that instance.
- Don't be misled by the shadowing instance still working for other instances; only the one instance that received the stray assignment is affected, which can make the bug look intermittent.
- Don't confuse this with `__delattr__`/`__delete__`; a read-only guarantee needs `__set__` to reject assignment specifically, and a separate `__delete__` to reject deletion if that should be blocked too.

## Checklist
- For every descriptor meant to be read-only, is there a `__set__` method that raises, rather than simply no `__set__` at all?
- Has an actual assignment attempt on a live instance confirmed the attribute rejects the write, rather than silently creating a shadowing instance attribute?
- Where deletion should also be blocked, is `__delete__` defined to raise as well?

## Notes
A descriptor's three methods are independent hooks, not a single combined contract, so the absence of one does not imply the corresponding operation is refused — it only means that operation falls through to Python's ordinary attribute machinery, which for assignment means writing straight into the instance's `__dict__`. A descriptor that defines `__set__` becomes a data descriptor, and the attribute lookup rules specifically place data descriptors ahead of instance `__dict__` entries, which is the mechanism that lets a raising `__set__` actually block the write rather than being shadowed by it.
