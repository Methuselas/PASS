---
object_id: PAT_share_a_representation_until_a_write_forces_a_copy
object_type: pattern
name: Share a Representation Until a Write Forces a Private Copy
library_path:
- software-engineering
- languages
- cpp
- copy-control
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- cpp
- copy_control
- copy_on_write
- reference_counting
- performance
cross_links:
- rel: related_to
  target_object_id: PAT_price_shared_ownership_before_choosing_it
- rel: related_to
  target_object_id: PAT_choose_lazy_or_eager_by_how_often_the_result_is_needed
- rel: related_to
  target_object_id: PAT_dont_return_handles_to_internals
- rel: related_to
  target_object_id: AP_write_copy_control_for_a_resource_owning_class
reference:
  source_title: 'More Effective C++: 35 New Ways to Improve Your Programs and Designs'
  author: Scott Meyers
confidence: high
references: []
variants: []
---

# Share a Representation Until a Write Forces a Private Copy

## Pattern Rule
**IF** many objects of a type are expected to hold equal values, those values are large or expensive to construct, and copying between objects is common
**THEN** move the value into a separate object carrying a count of how many holders refer to it, let copies share it, and split off a private copy only when a holder is about to write
**ELSE** where values are rarely equal, or cheap enough that copying them does not show up in a measurement, the counting machinery costs more in space, time, and code than the sharing recovers.

## Do
- Put the count with the value rather than with the holder, because there is one count per value and not one per object. Nesting the value type privately inside the holder gives every member of the holder full access to it while denying access to everyone else, which is what you want and what a nested public type would not give you.
- Split before the write and not after, and remember that the count itself decides: a holder about to modify a value that other holders share must first take its own copy, decrement the old count, and point at the new one.
- Keep mutable aliases behind the abstraction. Prefer observers that return values or read-only views and mutations that re-enter the owner, where it can detach before exposing writable state. If compatibility forces a mutable pointer or reference to escape, detaching once cannot protect later copies; the representation must remain unshareable for the alias's possible lifetime, which is difficult to prove.
- Encapsulate ownership bookkeeping in a tested value-like member rather than spreading manual increments and decrements through every special member. A standard shared owner can manage the control-block lifetime, but it does not implement detach-on-write or make access to the representation thread-safe.

## Don't
- Don't expose mutable handles and then describe cross-holder mutation as merely a caller mistake. Either prevent the alias, keep the representation permanently private after escape under a sound lifetime rule, or choose ordinary eager value semantics.
- Don't assume a defaulted copy produces an independent representation when the representation directly owns raw resources or contains aliases. Defaulted copying is correct for value-like members; otherwise give the representation explicit ownership semantics so detaching produces a semantically independent value.
- Don't apply this where the objects can refer to one another. A group of objects holding references into each other keeps every count above zero even after nothing outside the group refers to any of them, and the whole group leaks; escaping that needs machinery this technique does not have.
- Don't infer that the conditions hold. The ratio of objects to distinct values and the cost of constructing one are both measurable, and both have to be favorable — sharing a value that nothing else holds is pure overhead.

## Checklist
- What is the measured ratio of live objects to distinct values?
- Does any member hand out a pointer or reference into the shared value, and what happens to sharing when it does?
- Does detaching create a semantically independent representation under the value type's actual copy semantics?
- Can objects of this type form a cycle of references?
- After a write through one holder, is any other holder's value observably changed?

## Notes
Two separate motivations get bundled under this heading and it is worth keeping them apart, because a design may want one without the other. The first is that the value owns itself, so nobody has to track who is responsible for releasing it. The second is that identical values are stored once. The first survives even when values are never shared for long; the second is the one that requires the frequency argument.

The reason a non-const subscript operator has to assume the worst is structural: the operator cannot see whether its result will be read or assigned to, so it must split the value on every call that might write. That pessimism is real overhead on reads, and the technique that recovers it — deferring the read-or-write decision to an interposed object that sees what happens to the result — is a separate move with its own consequences.

This is now a technique for your own types rather than something to expect from the library. The standard string type was permitted to work this way when Meyers wrote, and the standard has since required behavior — around when references and iterators may be invalidated — that rules it out. The aliasing hazard above is a large part of why.

One consideration absent from the original treatment and unavoidable now: the ownership count and the represented value have separate concurrency requirements. A standard shared owner makes ownership changes on distinct handle objects safe according to its contract, but it does not make simultaneous reads and writes of the represented value safe. A home-grown count needs its own synchronization, and an atomic count alone does not protect detach-versus-write behavior.
