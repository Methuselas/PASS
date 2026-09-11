---
object_id: PAT_avoid_overloading_on_universal_references
object_type: pattern
name: Avoid Unconstrained Overloading on Forwarding References
library_path:
- software-engineering
- languages
- cpp
- move-semantics
stage_binding: 0 design
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- cpp
- move_semantics
- overloading
- templates
- api_design
cross_links:
- rel: related_to
  target_object_id: PAT_tell_a_universal_reference_from_an_rvalue_reference
- rel: related_to
  target_object_id: PAT_delete_the_functions_you_want_to_forbid
- rel: related_to
  target_object_id: PAT_understand_special_member_generation
- rel: related_to
  target_object_id: PAT_make_interfaces_hard_to_misuse
reference:
  source_title: 'Effective Modern C++: 42 Specific Ways to Improve Your Use of C++11 and C++14'
  author: Scott Meyers
confidence: high
references: []
variants: []
---

# Avoid Unconstrained Overloading on Forwarding References

## Pattern Rule
**IF** you are adding a forwarding-reference overload to an overload set
**THEN** prefer a different name, a value or const-reference parameter, or a C++20-constrained template whose declared domain excludes the overloads it could hijack
**ELSE** where no overload set exists, an unconstrained forwarding entry point may be appropriate and its broad domain is explicit.

## Do
- Expect the forwarding-reference overload to win far more often than it looks like it should. It can instantiate to an exact match for almost any argument, so another overload requiring even a trivial conversion loses.
- Treat a perfect-forwarding constructor as the dangerous case rather than one case among several. It is a better match than the copy constructor for a non-const lvalue of the same class, so copying a non-const object calls the forwarding constructor instead. And in a derived class, the base copy and move constructors are hijacked the same way.
- Take the simplest alternative that works: give the functions different names. Perfect forwarding is not tied to a shared name, and abandoning the overload set costs nothing where the operations are conceptually distinct.
- Pass by reference to const where the efficiency of forwarding is not what the code needs. It gives up a move in some cases and it restores ordinary, predictable overload resolution.
- Pass by value where the parameter will be copied into the object anyway and the type is cheap to move. That gives most of the forwarding benefit with none of the overload-resolution behaviour.
- Use tag dispatch where one function must handle several argument categories: keep a single unconstrained entry point that forwards to implementation functions selected by a type tag rather than by overload resolution on the argument itself.
- Use a named C++20 concept or `requires` clause where forwarding references and overloading genuinely must coexist. Exclude the owning class itself in a forwarding constructor and state the accepted argument relation at the declaration.

## Don't
- Don't add an unconstrained forwarding-reference overload to an existing function and expect existing calls to keep resolving as they did.
- Don't try to fix a hijacked copy constructor by adding more overloads. Each addition is another candidate the forwarding constructor outranks, and the resulting error messages are among the worst the language produces.
- Don't assume a deleted overload solves it in the constructor case. Deleting an overload removes a candidate, but the forwarding constructor is still selected for anything you did not think to delete.
- Don't write a dense ad-hoc constraint when a different name or by-value interface makes the API clearer. When a shared name is important, a small named concept is preferable to leaving the candidate unconstrained.

## Checklist
- Does this overload set contain a forwarding-reference parameter?
- For each other overload: is there an argument type for which it would now lose to the forwarding one?
- If this is a constructor, what happens when a non-const lvalue of the class is copied?
- If the class has derived classes, what happens to their copy and move constructors?
- Have distinct names, reference to const, and by value been considered, and does any retained forwarding overload have a stated concept?

## Notes
The reason this goes wrong so reliably is that a forwarding-reference parameter can instantiate to an exact match for almost anything it is given. Overload resolution then prefers it over candidates needing a conversion, including conversions so small a reader may not register them — a string literal against a parameter taking a string, or a non-const lvalue against a reference-to-const parameter.

The constructor case is worth separating because the competing overloads are not ones you wrote. Copy and move constructors are generated or declared elsewhere, so the hijack shows up as a copy that no longer works rather than as an obviously wrong overload being chosen, and in a hierarchy the failure appears in a derived class whose author never saw the forwarding constructor.

Different names, reference to const, and by value are ordinary design moves with well-understood costs. When the overload set genuinely needs a forwarding candidate, C++20 concepts let the interface state its intended domain directly. The constraint must be treated as part of the contract and tested against the nearby overloads, especially copy and move construction.
