---
object_id: PAT_declare_single_argument_constructors_explicit
object_type: pattern
name: Make Conversions Explicit Unless They Are the Interface
library_path:
- software-engineering
- languages
- cpp
- interface-design
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- cpp
- interface_design
- type_conversion
- class_design
- explicit
cross_links:
- rel: related_to
  target_object_id: PAT_make_interfaces_hard_to_misuse
- rel: related_to
  target_object_id: PAT_make_operator_nonmember_for_conversions
reference:
  source_title: 'More Effective C++: 35 New Ways to Improve Your Programs and Designs'
  author: Scott Meyers
confidence: high
references: []
variants: []
---

# Make Conversions Explicit Unless They Are the Interface

## Pattern Rule
**IF** a constructor or conversion operator could let the compiler change types without an explicit request at the call site
**THEN** make it `explicit` unless substitutability is a deliberate part of the interface; use C++20 conditional `explicit` when that decision depends on a template property
**ELSE** where the conversion really is the point — a wrapper meant to be interchangeable with what it wraps at every call — the implicit form is the design, and what you owe is a reason recorded next to it.

## Do
- Review every non-copy, non-move constructor, not only one-parameter spellings. Since C++11, a non-explicit constructor can participate in conversion through copy initialization or list initialization even when it takes more than one argument.
- Mark conversion operators `explicit` when the conversion is useful only when requested. Keep a named function when the operation is lossy, fallible, expensive, or semantically richer than a type conversion.
- Use `explicit(bool-condition)` in C++20 template code when a wrapper conversion should be implicit exactly when the wrapped conversion is implicit.
- Use `explicit operator bool` for truth testing when contextual conversion to bool is intended without opening general arithmetic conversions.
- Where you must keep the conversion available for genuine construction while blocking it for argument matching, note that no legal conversion sequence contains more than one user-defined step — a fact you can build against deliberately, and the mechanism the pre-keyword workarounds all relied on.

## Don't
- Don't assume a missing overload gives you a compile error. Faced with a call that does not match, compilers go looking for a conversion sequence that makes it match, and a one-argument constructor is exactly such a sequence; the call then succeeds and does something you never wrote.
- Don't treat the resulting bug as rare because the conversion looks implausible. The classic instance is a dropped subscript — comparing a container to an element instead of element to element — which compiles into a comparison against a temporary container built from the element's value, constructed and destroyed once per loop iteration.
- Don't remove every conversion operator mechanically. An explicit conversion operator can provide a type-safe requested conversion; judge whether a named operation communicates important cost or failure semantics better.

## Checklist
- Which constructors can participate in copy or list initialization, including multi-argument converting constructors?
- Does the class declare any conversion operator, and would a named function serve the same clients?
- For each conversion left implicit, is there a recorded reason it should happen without appearing in the source?
- If an argument of the wrong type were passed to a function taking this class, would that be a diagnostic or a silent temporary?

## Notes
The reason this is worth a decision rather than a habit is that both mechanisms are invisible at the call site. A conversion inserted by the compiler leaves nothing in the source to grep for, so when the resulting behavior is wrong there is no line to look at — which is what makes the failures so expensive to diagnose relative to how simple they are.

Experience tends to push in one direction here. The more C++ a programmer has written, the more likely they are to have stopped writing conversion operators altogether, and the committee members who designed the standard library largely did the same.

Before the language offered `explicit`, code sometimes introduced an intermediate type so an unwanted conversion would require two user-defined steps and fail. That workaround is obsolete. Modern C++ can make constructors and conversion operators explicit directly, and C++20 can make explicitness conditional for generic wrappers without maintaining separate overload sets.
