---
object_id: PAT_manually_initialize_builtin_objects
object_type: pattern
name: Give Every Object a Defined Initial Value
library_path:
- software-engineering
- languages
- cpp
- initialization
stage_binding: 3 rough
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- cpp
- initialization
- undefined_behavior
- builtins
cross_links:
- rel: related_to
  target_object_id: PAT_adapt_rules_to_active_cpp_sublanguage
- rel: related_to
  target_object_id: PAT_initialize_members_with_init_list
reference:
  source_title: 'Effective C++, Third Edition: 55 Specific Ways to Improve Your Programs and Designs'
  author: Scott Meyers
confidence: high
references: []
variants: []
---

# Give Every Object a Defined Initial Value

## Pattern Rule
**IF** an object could be read before a successful write is guaranteed
**THEN** initialize it at its declaration—prefer value initialization or a meaningful value—because default initialization of many scalar and aggregate objects leaves indeterminate state that cannot be read safely.

## Do
- Use value initialization such as `int count{};`, `double total{};`, and `Point origin{};` when zero or the type's value-initialized state is the intended default.
- Give class members default member initializers when the same default applies across constructors, and override that default only where a constructor has a different value.
- Treat input as a fallible assignment, not as initialization. Initialize the destination first or read into a temporary, test the stream state, and publish the value only after extraction succeeds.
- Value-initialize arrays and aggregates with braces when all elements should begin in their zero/value-initialized state.

## Don't
- Don't assume `int x;` or `Point p;` comes out zeroed; the storage duration and initialization form decide that.
- Don't use `std::cin >> value` as the first operation on an otherwise uninitialized scalar and then read it unconditionally. A failed extraction does not leave a usable value either way: since C++11 a failed numeric parse stores zero and an out-of-range one stores the type's limit, while a failure before any parsing begins, such as empty input, leaves the destination untouched, so an uninitialized destination stays indeterminate in exactly that case.

## Checklist
- Does every object receive a defined value before its first read on every path?
- Am I relying on a zero-initialization the standard does not actually guarantee in this context?
- Can value initialization or a default member initializer express the intended default directly?
- If input supplies the value, is failure checked before the destination is used?

## Notes
C++ preserves default-initialization forms that do no work for performance and compatibility, so a declaration alone does not always produce a usable scalar value. Modern brace value initialization, default member initializers, and direct construction make the intended state explicit with little ceremony. The important boundary is not built-in versus library type but whether every path establishes a value before any read, including the failure path of an input operation.
