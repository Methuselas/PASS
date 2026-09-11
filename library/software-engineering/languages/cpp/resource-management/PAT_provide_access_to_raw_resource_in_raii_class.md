---
object_id: PAT_provide_access_to_raw_resource_in_raii_class
object_type: pattern
name: Provide Access to the Raw Resource in an RAII Class
library_path:
- software-engineering
- languages
- cpp
- resource-management
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- cpp
- raii
- resource_management
- conversions
cross_links:
- rel: related_to
  target_object_id: PAT_manage_resources_with_raii_objects
- rel: related_to
  target_object_id: AP_give_an_acquired_resource_an_owner
reference:
  source_title: 'Effective C++, Third Edition: 55 Specific Ways to Improve Your Programs and Designs'
  author: Scott Meyers
confidence: high
references: []
variants: []
---

# Provide Access to the Raw Resource in an RAII Class

## Pattern Rule
**IF** an RAII class wraps a resource that other APIs need in raw form
**THEN** expose a clearly non-owning view through an explicit accessor such as `get()` or `native_handle()`, and keep release or ownership transfer on a separately named operation.

## Do
- Return the raw pointer or platform handle from a named observer without changing ownership. State how long that view remains valid and which operations invalidate it.
- Provide `operator*` and `operator->` only when the wrapper intentionally models pointer-like access to an object. Those operators expose use of the pointee without making the owner implicitly convertible to a raw owning-looking value.
- Use an explicit boolean conversion when clients need a validity test, and a named `release()`-style operation only when callers are allowed to assume the cleanup obligation.

## Don't
- Don't add an implicit conversion to the raw resource merely to shorten calls. It lets non-owning handles escape silently, participates in unrelated overload resolution, and hides the lifetime boundary at the call site.
- Don't make `get()` transfer ownership. Observation and release must have visibly different operations and postconditions.

## Checklist
- Can clients reach the raw resource when an API requires it?
- Is the returned handle explicitly documented as non-owning, with a clear validity interval?
- Are observation, validity testing, and ownership transfer separate operations?
- Would pointer-like operators accurately describe this wrapper rather than merely save spelling?

## Notes
Real APIs demand raw resources, so an RAII class that hides its resource completely becomes unusable. Standard smart pointers show the modern separation: `get()` observes, dereference operators provide pointer-like access, boolean conversion is explicit, and `release()`—where supported—transfers the cleanup obligation by name. Exposing a non-owning handle is not a design failure; making observation look like ownership or an unrestricted implicit conversion is the hazard.
