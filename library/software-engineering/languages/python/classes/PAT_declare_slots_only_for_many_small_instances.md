---
object_id: PAT_declare_slots_only_for_many_small_instances
object_type: pattern
name: Declare __slots__ Only for Many Small Instances
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
- memory
- attributes
cross_links:
- rel: related_to
  target_object_id: PAT_set_every_instance_attribute_in_init
- rel: related_to
  target_object_id: PAT_let_measurement_decide_what_to_tune
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Declare __slots__ Only for Many Small Instances

## Pattern Rule
**IF** a class is instantiated in very large numbers, each instance holds only a few known attributes, and measurement shows the per-instance attribute dictionaries are a real memory cost
**THEN** list those attribute names in `__slots__`, which replaces each instance's namespace dictionary with fixed storage, and accept that instances can then hold no other attributes
**ELSE** in every other case leave `__slots__` out — the ordinary dictionary is what makes instances flexible, introspectable, and compatible with tools that expect `__dict__` to exist

## Do
- Treat `__slots__` as a measured optimization, not a declaration feature: decide with a memory profile of real instance counts, not with the intuition that fewer attributes should cost less.
- List every attribute the class assigns; an attribute missing from the list cannot be set at all once the dictionary is gone.
- Repeat `__slots__` in every class in the hierarchy that adds attributes. Slots are not concatenated into one list — each class declares its own, and the instance gets the union — so a single subclass without `__slots__` restores a `__dict__` and gives back the memory for all of them.
- Use `getattr`, `setattr` and `dir` in any generic tool that may meet slotted instances; they see slot attributes, while `instance.__dict__` does not exist or is incomplete.
- Add `'__dict__'` to the list deliberately if some instances also need arbitrary attributes; that reinstates the dictionary alongside the slots.

## Don't
- Don't use `__slots__` to prevent typos or to enforce a fixed set of fields; that is a side effect, and `@dataclass` with type annotations expresses a fixed field set far more clearly to both readers and type checkers.
- Don't assume `instance.__dict__` exists in library or tool code; on a slotted instance the attribute raises `AttributeError`, which breaks generic serializers, debuggers and display helpers.
- Don't inspect `cls.__slots__` to enumerate an instance's attributes; it shows only that one class's list and misses every slot declared higher in the tree.
- Don't reach for slots on a class with a handful of instances; the saving is per-instance and rounds to nothing, while the constraints are permanent.

## Checklist
- Is there a measurement showing instance dictionaries are a significant share of memory here?
- Does every class in the hierarchy that adds attributes declare its own `__slots__`?
- Does any code touching these instances assume `__dict__` exists?
- Would a `@dataclass` express the intended fixed field set better than a slots list?

## Notes
A slot is a class-level descriptor that manages a reserved storage position in the instance, which is why the instance needs no dictionary and why the names are visible on the class rather than the object. That implementation explains both its benefit and all of its edge cases: attributes become class-managed, so the usual assumption that instance data lives in `instance.__dict__` stops holding. Note that this trades against a moving target — the interpreter's own dictionary implementation shares keys between similar instances, so the gap slots close is narrower than it once was, which is one more reason to measure rather than assume.
