---
object_id: PAT_give_polymorphic_base_a_virtual_destructor
object_type: pattern
name: Give Polymorphic Base Classes a Virtual Destructor
library_path:
- software-engineering
- languages
- cpp
- destructors
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- cpp
- destructors
- inheritance
- polymorphism
cross_links:
- rel: related_to
  target_object_id: PAT_no_virtual_calls_in_constructors_or_destructors
- rel: related_to
  target_object_id: AP_design_a_customization_point
reference:
  source_title: 'Effective C++, Third Edition: 55 Specific Ways to Improve Your Programs and Designs'
  author: Scott Meyers
confidence: high
references: []
variants: []
---

# Give Polymorphic Base Classes a Virtual Destructor

## Pattern Rule
**IF** clients may destroy derived objects through a base-class pointer
**THEN** make the base destructor public and virtual so deletion destroys the complete object; if deletion through the base is forbidden, make the destructor protected and non-virtual instead.

## Do
- Make a polymorphic ownership interface explicit: a public virtual destructor permits deletion through the base, while a protected non-virtual destructor prevents that deletion without adding a new virtual slot to a non-polymorphic mixin.
- To make an abstract base that has no other pure virtual function, declare a pure virtual destructor and still provide its definition, since derived destructors call it.
- For a base that is inherited but never deleted through — a mixin, a template parameter a class inherits, a stateless helper — prefer a protected non-virtual destructor. Protected access rejects the dangerous call; non-virtual destruction is appropriate because the interface did not promise polymorphic deletion.
- Mark a class `final` when it has virtual behavior but is not intended to be a base. That prevents a derived object from creating a deletion contract the class never offered.

## Don't
- Don't leave a public non-virtual destructor on a type intended for polymorphic use. It makes deletion through the base look valid while producing undefined behavior for a derived object.
- Don't publicly derive from standard containers or `std::string` to create a polymorphic abstraction. They were not designed as polymorphic bases; use composition and publish the interface you actually own.
- Don't claim a virtual destructor necessarily adds a vptr to a class that is already polymorphic. Such a class already has virtual dispatch machinery; the important cost decision applies when making an otherwise non-polymorphic base virtual.

## Checklist
- May clients delete through the base, and does destructor access/virtuality state that answer?
- Is the class a base at all, or should it be `final`?
- If it is a non-owning mixin base, is its destructor protected and non-virtual?
- Is composition a better boundary than deriving from a standard-library value or container type?

## Notes
Deleting a derived object through a base pointer with a non-virtual destructor is undefined. The durable guideline is about the ownership operation, not a count of virtual members: a base destructor should usually be public and virtual when polymorphic deletion is supported, or protected and non-virtual when it is forbidden. An already-polymorphic base already carries virtual dispatch machinery, so adding the correct destructor is primarily a semantic decision. A non-polymorphic mixin can keep its compact representation while making misuse fail at compile time through protected access.
