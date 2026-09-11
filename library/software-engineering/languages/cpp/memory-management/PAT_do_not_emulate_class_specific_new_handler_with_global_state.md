---
object_id: PAT_do_not_emulate_class_specific_new_handler_with_global_state
object_type: pattern
name: Do Not Emulate a Class-Specific new_handler with Global State
library_path:
- software-engineering
- languages
- cpp
- memory-management
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- cpp
- memory_management
- new_handler
- concurrency
cross_links:
- rel: related_to
  target_object_id: PAT_write_a_well_behaved_new_handler
- rel: related_to
  target_object_id: PAT_reach_for_a_custom_allocator_only_for_what_it_can_buy
- rel: related_to
  target_object_id: AP_replace_new_and_delete_for_a_named_reason
reference:
  source_title: PASS software-engineering canonical synthesis
  author: Modern C++ correction of accepted allocation guidance
confidence: high
references: []
variants: []
---

# Do Not Emulate a Class-Specific new_handler with Global State

## Pattern Rule
**IF** one class needs allocation-failure behavior different from the process-wide `std::new_handler`
**THEN** express that policy in the class's allocator, factory, memory resource, or fallible creation API instead of temporarily replacing the global handler around an allocation.

## Do
- Keep `std::set_new_handler` for a process-wide policy whose effects on every allocation are intended.
- Give a class or subsystem a dedicated allocator or `std::pmr::memory_resource` when it needs a distinct storage pool, accounting policy, or exhaustion behavior.
- Use a factory returning the project's explicit result type when allocation failure is meant to be recoverable locally rather than thrown as `std::bad_alloc`.

## Don't
- Don't install a class handler globally, call `::operator new`, and restore the previous handler with RAII. Exception safety restores the value on one thread, but it does not make the process-global mutation isolated from concurrent allocations.
- Don't serialize all allocation merely to preserve that emulation unless a measured, process-wide design explicitly accepts the bottleneck and reentrancy hazards.
- Don't let a local failure policy surprise unrelated library code that allocates during the temporary global interval.

## Checklist
- Is the desired policy truly process-wide, or only local to one type or subsystem?
- Can another thread or reentrant call allocate while the global handler is temporarily changed?
- Would an allocator, memory resource, factory, or explicit result make the scope of the policy visible?

## Notes
The historical CRTP recipe stored one handler per class, installed it with `std::set_new_handler`, delegated to global allocation, and restored the old handler in a destructor. RAII makes restoration exception-safe but cannot make global mutable state thread-local. Under a C++20 baseline, a local policy should have local state. Keep the old construction recognizable for legacy diagnosis; do not use it as a reusable modern facility.
