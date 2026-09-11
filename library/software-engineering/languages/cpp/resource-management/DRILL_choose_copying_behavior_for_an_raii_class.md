---
object_id: DRILL_choose_copying_behavior_for_an_raii_class
object_type: drill
name: Choose and Implement an RAII Class's Copying Behavior
target_skill: Selecting and implementing copy semantics for a resource-managing class
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
- copy_control
- resource_management
cross_links:
- rel: related_to
  target_object_id: PAT_choose_raii_copying_behavior_deliberately
reference:
  source_title: 'Effective C++, Third Edition: 55 Specific Ways to Improve Your Programs and Designs'
  author: Scott Meyers
confidence: high
references: []
variants: []
---

# Choose and Implement an RAII Class's Copying Behavior

## Practice Task
Given a `Lock` class that locks a mutex in its constructor and unlocks it in its destructor, decide what copying should mean and implement it.

## Target Skill
Picking among move-only, shared, and deep-copy ownership, then implementing and testing the choice correctly.

## Setup
No special setup required.

## Instructions
- Compare move-only, reference-counted sharing, and deep copy, give a reason for and against each in this specific case, and argue which fits a mutex lock guard.
- Write out concretely what the compiler-generated copy would do — the same handle released twice — and say whether that would be caught at compile time, at run time, or not at all.
- Implement the guard as move-only: delete both copy operations, implement or default correct move operations, and leave a moved-from guard safe to destroy.
- Compile a deliberate copy attempt and retain the rejection. Then move the guard and observe one unlock across both object lifetimes.
- Name the rejected option closest to the choice, along with the condition that would flip the decision.

## Success Check
- All three ownership options are stated with a reason for and against each in this specific case, rather than the chosen one accompanied by two names.
- What the compiler-generated copy would do is written out concretely — the same handle released twice — and the run says whether that would be caught at compile time, at run time, or not at all.
- Copying is rejected by the compiler, and the diagnostic is retained as evidence.
- Moving is exercised, the source becomes harmless, and exactly one unlock is observed across both lifetimes.
- The rejected option closest to the choice is named, along with the condition that would flip the decision, so the choice is bounded rather than absolute.

## Common Failures
- Leaving the compiler-generated copy in place, so the mutex is released more than once.
- Deleting copy operations but forgetting that declaring a destructor can suppress implicit moves.
- Moving the handle without clearing the source's ownership state.

## Notes
This drills the modern form of the ownership decision. A mutex lock guard normally has one active responsibility, so transfer is a move and copying is rejected. If the application instead needs multiple handles to one shared lock state, that is a different abstraction whose final owner performs the unlock.
