---
object_id: DRILL_refactor_manual_cleanup_to_raii
object_type: drill
name: Refactor Manual Resource Cleanup into an RAII Object
target_skill: Replacing manual delete/release with RAII ownership
library_path:
- software-engineering
- languages
- cpp
- resource-management
stage_binding: 3 rough
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- cpp
- raii
- resource_management
- refactoring
cross_links:
- rel: related_to
  target_object_id: PAT_manage_resources_with_raii_objects
reference:
  source_title: 'Effective C++, Third Edition: 55 Specific Ways to Improve Your Programs and Designs'
  author: Scott Meyers
confidence: high
references: []
variants: []
---

# Refactor Manual Resource Cleanup into an RAII Object

## Practice Task
Take a function that calls a factory such as `createInvestment`, uses the returned raw pointer, and deletes it at the end, and make it leak-proof with RAII — first at the call site, then at the factory.

## Target Skill
Handing an acquired resource to a manager whose destructor releases it, on every exit path, and moving that handover to the point where the resource is created.

## Setup
Give the managed type a live-instance counter so a leak or a release can be observed.

## Instructions
- Enumerate every exit before changing anything — each early return, each break, each call that can throw — and state the count.
- Wrap the returned pointer in a `std::unique_ptr` at the point of acquisition, in one statement, and confirm there is no statement between acquisition and handover where a throw would strand the resource.
- Delete the manual delete statement and establish it is gone by searching rather than by recollection.
- Demonstrate release on the throwing path, before and after the change.
- Change the factory's return type to an owning one, rebuild the callers, and state whether it should return `std::unique_ptr` or `std::shared_ptr`, with the reason.
- Name the array case with the reason a single-object manager is wrong for it, and say what it would use instead.

## Success Check
- Every exit is enumerated before the change — each early return, each break, each call that can throw — and the count is stated. Those are the paths the manual release had to be right on, and the count is reliably larger than the function appears to have.
- Acquisition and handover occur in one statement, checked by confirming there is no statement between them where a throw would strand the resource. A pointer assigned on one line and wrapped on the next is the original defect with a smart pointer added to it.
- The manual release is gone, established by searching rather than by recollection.
- Release on the throwing path is observed on the counter, leaking before the change and released after it, rather than inferred. That is the path the original got wrong and the one no ordinary test exercises.
- The factory returns the owner, and the choice between exclusive and shared ownership is argued: exclusive ownership costs nothing extra and a `std::unique_ptr` result still converts to `std::shared_ptr` for a caller who needs sharing, while the reverse conversion does not exist. Wrapping at this one call site while the factory still returns a raw pointer fixes one caller and leaves the window open for every other.
- The array case is named with the reason a single-object manager is wrong for it, and the run says what it would use instead — a standard container first, the array form of the owning pointer only when the array itself must be owned — rather than noting only that a difference exists.

## Common Failures
- Storing the raw pointer in a variable and forgetting to wrap it before the risky code.
- Using a single-object smart pointer for an array allocation, so the wrong delete form runs.
- Repairing the call site and leaving the factory's raw-pointer return type in place.

## Notes
The leak is not a coding slip but a structural weakness of manual cleanup, which RAII removes by tying release to destruction. The strongest form moves the handover into the factory, so no caller ever holds the resource unowned.
