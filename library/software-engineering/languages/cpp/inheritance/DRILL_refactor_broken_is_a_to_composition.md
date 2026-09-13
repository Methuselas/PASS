---
object_id: DRILL_refactor_broken_is_a_to_composition
object_type: drill
name: Refactor a Broken Is-A Hierarchy to Composition
target_skill: Detecting a false is-a and remodeling it with composition
library_path:
- software-engineering
- languages
- cpp
- inheritance
stage_binding: 2 block
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- cpp
- inheritance
- composition
- refactoring
cross_links:
- rel: related_to
  target_object_id: PAT_model_has_a_with_composition
reference:
  source_title: 'Effective C++, Third Edition: 55 Specific Ways to Improve Your Programs and Designs'
  author: Scott Meyers
confidence: high
references: []
variants: []
---

# Refactor a Broken Is-A Hierarchy to Composition

## Practice Task
Given a `Set` template publicly inheriting from `std::list`, show why the is-a fails and remodel it with composition.

## Target Skill
Testing an inheritance link for true substitutability and replacing a false is-a with composition.

## Setup
No special setup required.

## Instructions
- Write, as code that compiles against the inheritance version, a base operation the derived class cannot honor. Run it and record the wrong result.
- Fail substitutability in practice: pass the derived object where the base is expected and observe the breakage.
- Remodel with composition: give `Set` a private `std::list` member and forward member, insert, remove, and size to it, exposing only the Set interface. Enumerate the forwarded members with a reason for each, and name any member deliberately not forwarded.
- Decide whether clients may iterate the Set and, if so, what iterator type the forwarded `begin` and `end` return. Then write through a forwarded iterator to turn one element into a value the Set already holds, compile it, and record the result.
- List the new type's public surface, then compile a base operation and a base-typed call against the new type and record the results.
- Exercise the new type's own contract against the case that broke before and show it holds.

## Success Check
- The broken operation is written as code that compiles against the inheritance version and produces a wrong result when run. A stated invariant violation is the argument; the failing call is the evidence.
- Substitutability is failed in practice, by passing the derived object where the base is expected and observing the breakage rather than reasoning about the relationship.
- After remodelling, the base's interface is confirmed absent from the new type's public surface by listing that surface and by the base operation and the base-typed call each being rejected. A composition forwarding everything has reproduced the inheritance with more typing.
- The forwarded members are enumerated with a reason each, and any member deliberately not forwarded is named. That omission is what composition bought.
- Iteration is decided and the write through the forwarded iterator is compiled: a forwarded constant iterator rejects it, and a forwarded mutable iterator lets the client write a duplicate the Set's own insert would refuse. Forwarding the list's ordinary iterators hands clients the invariant along with the elements.
- The new type's own contract is exercised against the case that broke before and shown to hold.

## Common Failures
- Keeping public inheritance because the base has convenient functions to reuse.
- Exposing the contained object's full interface instead of only the new type's.
- Forwarding the contained list's mutable iterators, so clients can break the invariant through them.

## Notes
The reuse temptation is real, but is-a demands substitutability, and Set-on-list fails it: a list accepts duplicates a Set must refuse. Composition with delegation is the fix, and what composition buys is exactly the interface it declines to forward.
