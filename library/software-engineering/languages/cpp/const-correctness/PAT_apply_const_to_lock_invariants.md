---
object_id: PAT_apply_const_to_lock_invariants
object_type: pattern
name: Apply const Wherever a Value Should Not Change
library_path:
- software-engineering
- languages
- cpp
- const-correctness
stage_binding: 3 rough
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: PAT_prefer_immutable_objects
tags:
- cpp
- const
- immutability
- pointers
cross_links:
- rel: related_to
  target_object_id: PAT_prefer_immutable_objects
- rel: related_to
  target_object_id: PAT_return_values_without_top_level_const
- rel: related_to
  target_object_id: AP_make_a_class_const_correct
reference:
  source_title: 'Effective C++, Third Edition: 55 Specific Ways to Improve Your Programs and Designs'
  author: Scott Meyers
confidence: high
references: []
variants: []
---

# Apply const Wherever a Value Should Not Change

## Pattern Rule
**IF** an object, reference, pointer target, parameter, or view should not permit modification
**THEN** declare it `const` so the compiler enforces the constraint and the invariant is visible to other programmers.

## Do
- Place `const` precisely on pointers: in `const char * const p`, `const` left of the `*` freezes the pointee and `const` right of the `*` freezes the pointer — reading the declaration right-to-left makes this fall out.
- Reach for `const_iterator` when you want the pointed-to element to stay fixed; a plain `const` iterator only stops the iterator from moving.
- Mark parameters and locals `const` unless you must change them, so an accidental write to one of them is a compile error. Do not expect that to catch the `if (a * b = c)` typo: `a * b` produces a new non-const value whatever the constness of `a` and `b`, so for a class type the typo compiled with every operand const. For built-in types it is already an error; for a class type, a ref-qualified assignment operator is what refuses it.
- Return a reference or pointer to const when callers may observe but not modify an existing object. Return newly produced values without top-level `const`; their operations should control valid value categories directly.

## Don't
- Don't leave a "never changes" value non-const; you give up the compiler's help and let accidental writes slip through.
- Don't treat a `const` iterator (a fixed iterator) and a `const_iterator` (a fixed element) as interchangeable — they constrain different things.
- Don't add top-level `const` to a by-value return. It does not protect persistent state and can inhibit moves or valid rvalue-qualified operations.

## Checklist
- Have I marked every value that should stay put as `const`?
- For each pointer, is `const` on the side(s) matching what must not change?
- Do I actually need a `const_iterator` here rather than a const iterator?
- Is this return exposing an existing object through a reference or pointer, or producing a new value?

## Notes
`const` lets you state a semantic constraint — this should not change — and hands enforcement to the compiler, which is why it is the C++ mechanism behind immutability. It spans pointers, references, iterators, parameters, locals, and member functions. Return types require one distinction: const on a reference or pointed-to object protects existing state, while top-level const on a newly produced value usually restricts useful value semantics without protecting an invariant.
