---
object_id: PAT_add_a_computed_or_validated_attribute_with_property
object_type: pattern
name: Add a Computed or Validated Attribute with property
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
- encapsulation
cross_links:
- rel: related_to
  target_object_id: PAT_intercept_attribute_access_without_recursing
- rel: related_to
  target_object_id: PAT_expose_clean_api_hide_implementation
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Add a Computed or Validated Attribute with property

## Pattern Rule
**IF** one named attribute needs to be computed on access, validated on assignment, or kept consistent with other state — and callers should keep using plain dotted access
**THEN** define it with the `@property` decorator and an optional `@name.setter`, which routes just that name through your methods and leaves every other attribute untouched
**ELSE** when the names to manage are not known until runtime, or arbitrary attributes must be intercepted generically, fall back to `__getattr__`/`__setattr__`, which can handle names no decorator could be written for

## Do
- Start plain: expose an ordinary attribute, and convert it to a property only when a real need for computation or validation appears. Callers do not have to change, because the dotted syntax is identical.
- Write the getter under `@property` and the setter under a decorator named after that same property (for example `@temperature.setter`), storing the real value in a differently named attribute (conventionally prefixed with an underscore) so the setter does not call itself.
- Raise from the setter to reject an invalid value, so bad state is refused at the moment of assignment rather than discovered later by whatever reads it.
- Make a value read-only by defining only the getter; assignment then raises `AttributeError` with no extra code.
- Prefer a property over a `get_x()`/`set_x()` method pair: it keeps the attribute-shaped interface callers already expect and costs a method call only on the managed name.

## Don't
- Don't give a property side effects or significant cost. It looks like an attribute access at the call site, so readers will assume it is cheap and repeatable, and will not hesitate to use it in a loop.
- Don't store the value under the property's own name inside the setter; `self.name = value` re-enters the setter and recurses.
- Don't convert every attribute to a property defensively. A property that only reads and writes a private twin adds indirection and nothing else — plain attributes are the Pythonic default precisely because they can be upgraded later without breaking callers.
- Don't expect a property to intercept names other than its own; it manages exactly the one attribute it defines.

## Checklist
- Does each property genuinely compute, validate, or maintain consistency, rather than just forward to a private field?
- Does every setter assign to a different name than the property itself?
- Is a read-only value expressed by omitting the setter rather than by convention alone?
- Is a property doing work expensive enough that callers should have been told to expect a method call?

## Notes
A property is a descriptor stored on the class: accessing the name on an instance finds the property object on the class and calls its getter with the instance. Because the lookup happens at the class level for one specific name, the cost falls only on that name — unlike `__setattr__`, which intercepts every assignment the class ever makes. That difference is the whole reason to prefer properties where they apply, and the reason they cannot cover the generic case: you must know the name to write the property.
