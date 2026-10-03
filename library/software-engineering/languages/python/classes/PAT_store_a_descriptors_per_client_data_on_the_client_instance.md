---
object_id: PAT_store_a_descriptors_per_client_data_on_the_client_instance
object_type: pattern
name: Store a Descriptor's Per-Client Data on the Client Instance, Not the Descriptor
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
- state
cross_links:
- rel: related_to
  target_object_id: PAT_write_a_descriptor_class_to_reuse_managed_attribute_logic
- rel: related_to
  target_object_id: PAT_put_shared_state_on_the_class_and_per_object_state_on_the_instance
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Store a Descriptor's Per-Client Data on the Client Instance, Not the Descriptor

## Pattern Rule
**IF** a descriptor's managed value should vary independently for each instance of the class that uses it
**THEN** store that value as an attribute on the `instance` argument passed to `__get__`/`__set__`, not on the descriptor object (`self`)
**ELSE** store a value on the descriptor itself (`self`) only when it is genuinely meant to be shared across every client instance that uses this attribute, or is internal bookkeeping the descriptor needs regardless of which instance is asking

## Do
- Read and write through the `instance` argument (`instance._name = value`, `return instance._name`) whenever the attribute should hold a different value per object.
- Give the client-stored attribute a name that won't collide with the descriptor's own public name — an underscore-prefixed form is the common convention, the same as with properties.
- Reserve descriptor-instance (`self`) storage for data that is deliberately shared by every object using that attribute, or for counters and caches that belong to the descriptor's own implementation rather than to any one client.
- Verify the choice by creating two client instances and confirming that changing one's managed attribute leaves the other's value alone, when per-instance behavior is intended.

## Don't
- Don't store a per-client value as `self.value` inside the descriptor and expect each client instance to keep its own copy; a single descriptor instance is a *class* attribute, shared by every instance of the client class, so the most recent client to set it overwrites what every other client reads.
- Don't assume this mistake will announce itself; the code runs without error, and the symptom is a later-created instance's data silently overwriting an earlier instance's, which surfaces as a data bug far from where the descriptor was written.
- Don't mix the two storage policies for the same attribute without a clear reason; pick instance-state or descriptor-state for a given managed name and apply it consistently in that descriptor's methods.

## Checklist
- Does this descriptor's managed value need to differ between two different instances of the client class?
- If so, is the value read from and written to the `instance` argument rather than `self`?
- Has a two-instance test actually confirmed that one client's assignment does not change what another client reads back?

## Notes
A descriptor object assigned to a class attribute is itself shared the same way any other class attribute is: there is exactly one `Descriptor()` instance no matter how many objects use the class that holds it. Storing a value in that one shared object's own state (`self.value`) therefore does not create per-client storage at all — it creates one value that every client instance's `__get__` and `__set__` calls read and write together, which is invisible until a second client instance reveals that the first one's data quietly changed.
