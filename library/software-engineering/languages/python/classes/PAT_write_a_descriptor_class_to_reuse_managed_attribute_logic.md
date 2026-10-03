---
object_id: PAT_write_a_descriptor_class_to_reuse_managed_attribute_logic
object_type: pattern
name: Write a Descriptor Class to Reuse Managed-Attribute Logic
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
- properties
cross_links:
- rel: related_to
  target_object_id: PAT_add_a_computed_or_validated_attribute_with_property
- rel: related_to
  target_object_id: PAT_store_a_descriptors_per_client_data_on_the_client_instance
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Write a Descriptor Class to Reuse Managed-Attribute Logic

## Pattern Rule
**IF** the same get/set/validate logic for a managed attribute needs to apply to more than one attribute name, more than one class, or needs its own internal state and helper methods
**THEN** write it once as a descriptor class — a class defining `__get__`, `__set__`, and/or `__delete__` — and instantiate it as a class attribute wherever that logic is needed
**ELSE** for a single, one-off managed attribute on one class, `@property` already expresses the same `__get__`/`__set__` behavior with less code; reach for a descriptor only once reuse or descriptor-level state is actually needed

## Do
- Write the validation or computation once as a descriptor class when several attributes (an age field on several classes, several numeric fields needing the same range check) would otherwise duplicate the same property boilerplate.
- Give the descriptor its own `__init__` and helper methods when it needs internal bookkeeping a property's plain functions cannot hold without extra instance attributes.
- Nest a one-off descriptor class inside its single client class when it has no use outside that client, to keep its name out of the surrounding module scope.
- Remember a property already *is* a descriptor underneath — `property(fget, fset, fdel)` builds an object with `__get__`/`__set__`/`__delete__` for you — so choosing between them is a question of how much machinery you want to write yourself, not a different underlying mechanism.

## Don't
- Don't write a full descriptor class for a single managed attribute used in exactly one class; that duplicates what `@property` already provides with a getter, setter, and optional deleter in a few lines.
- Don't assume a descriptor needs to be a top-level class; nesting it inside the one class that uses it is appropriate and keeps the two definitions visually together.
- Don't forget that a descriptor's three methods are passed the client instance as their second argument; without using it, the descriptor only has its own state to work with, which carries its own sharing consequences (see the related card on descriptor versus client-instance state).

## Checklist
- Does the same accessor logic genuinely repeat across more than one attribute or class, justifying a descriptor over a property?
- Does the descriptor need internal state or helper methods beyond what plain getter/setter functions could hold?
- Where only one attribute on one class needs managing, has `@property` been ruled out as sufficient first?

## Notes
A property and a descriptor solve the same problem — routing get/set/delete through code instead of a plain instance slot — and a property is in fact built by creating a particular kind of descriptor for you from the functions you pass it. The difference that matters in practice is reuse: a property's accessor functions live inside the one class that defines them, while a descriptor is an ordinary class that can be instantiated once per attribute, once per class, or imported and reused anywhere the same managed behavior is needed, with its own `__init__`, helper methods, and inheritance hierarchy available the way they would be for any other class.
