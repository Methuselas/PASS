---
object_id: PAT_manage_resources_with_raii_objects
object_type: pattern
name: Manage Every Resource with an RAII Object
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
- smart_pointers
cross_links:
- rel: related_to
  target_object_id: PAT_prefer_make_functions_to_direct_new
- rel: related_to
  target_object_id: PAT_never_let_exceptions_leave_a_destructor
- rel: related_to
  target_object_id: AP_give_an_acquired_resource_an_owner
- rel: related_to
  target_object_id: AP_make_a_function_exception_safe
reference:
  source_title: 'Effective C++, Third Edition: 55 Specific Ways to Improve Your Programs and Designs'
  author: Scott Meyers
confidence: high
references: []
variants: []
---

# Manage Every Resource with an RAII Object

## Pattern Rule
**IF** you acquire a resource that must later be released — heap memory, a file descriptor, a mutex lock, a socket, a database connection
**THEN** immediately give it to an object that takes ownership in its constructor and releases it in its destructor (RAII), instead of relying on a manual release that a return, break, or exception can skip.

## Do
- Acquire the resource and hand it to the managing object in the same statement (Resource Acquisition Is Initialization), so it is guarded the instant it exists.
- For heap objects use a ready-made smart pointer, and start with `std::unique_ptr` rather than `std::shared_ptr`: exclusive ownership is cheaper and clearer, and it can be moved into shared ownership later. `std::auto_ptr` was removed in C++17 and is not an option in the C++20 baseline.
- Let the manager's destructor perform the release, so it happens automatically on every path out of the scope.

## Don't
- Don't count on reaching a manual delete or release at the end of a function; a premature return, a loop break, or a thrown exception skips it and leaks the resource plus everything it owns.
- Don't construct the managing object without a name. A declaration that gives it a name binds it to the enclosing scope; the same constructor call written as a bare expression creates a temporary that is destroyed at the end of that statement, so the resource is released immediately and the code that follows runs unprotected. The two forms differ by an identifier, both compile, and only the named one does anything.
- Don't represent a dynamic array with the wrong smart-pointer specialization. Prefer `std::vector` or `std::string`; when array ownership itself is required, use the array specialization of `std::unique_ptr`, or the array specialization of `std::shared_ptr` only when the array truly has shared ownership.

## Checklist
- Is every acquired resource owned by an object that releases it in its destructor?
- Is the resource handed to its manager at the moment of acquisition?
- Am I still calling delete or a release function by hand anywhere outside a resource-managing class?

## Notes
The `createInvestment`/`f` example shows why manual release fails: any early exit or exception between acquisition and the release call leaks. RAII closes every path by tying release to destruction, which C++ runs automatically at scope exit. Historical examples used `auto_ptr` and `tr1::shared_ptr`; the C++20 forms are `std::unique_ptr` and `std::shared_ptr`. The mechanism is broader than memory: an object, not control-flow discipline, owns every acquired resource.
