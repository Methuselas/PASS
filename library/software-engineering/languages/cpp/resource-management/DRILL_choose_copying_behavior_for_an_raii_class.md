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
Given a `Lock` class that holds a raw pointer to a mutex, locks it in its constructor and unlocks it in its destructor, decide what copying should mean and implement it.

## Target Skill
Picking among scope-pinned, move-only, shared, and deep-copy ownership, then implementing and testing the choice correctly.

## Setup
Use a mutex stand-in that counts its locks and unlocks.

## Instructions
- Compare four ownership options — pinned to its scope (neither copyable nor movable), move-only, reference-counted sharing, and deep copy — give a reason for and against each in this specific case, and argue which fits a mutex lock guard.
- Write out concretely what the compiler-generated copy would do, then build it, copy a guard, and count locks and unlocks. Say whether the defect would be caught at compile time, at run time, or not at all.
- Implement the guard as move-only: delete both copy operations and write move operations that leave a moved-from guard safe to destroy.
- Compile a deliberate copy attempt and retain the rejection.
- Move-construct a guard and count unlocks across both lifetimes. Then move-assign a guard onto one holding a different mutex, and count each mutex's unlocks.
- Replace the hand-written move operations with `= default`, rerun the move-construction count, and record the result.
- Name the rejected option closest to the choice, along with the condition that would flip the decision.

## Success Check
- All four ownership options are stated with a reason for and against each in this specific case, rather than the chosen one accompanied by three names.
- What the compiler-generated copy does is written out and then observed — one lock and two unlocks of the same mutex — and the run says whether that would be caught at compile time, at run time, or not at all. An answer of "compile time" that was never built has not been checked.
- Copying is rejected by the compiler, and the diagnostic is retained as evidence.
- Moving is exercised both ways: exactly one unlock across the two lifetimes of a move construction, and a move assignment that releases the target's original mutex at once, with each mutex unlocked exactly once overall. A move assignment that overwrites the handle without releasing it passes the construction count and never unlocks the first mutex.
- The defaulted moves are observed unlocking twice — a defaulted move copies the raw pointer and leaves the source still owning it — and the hand-written moves are kept for that reason, rather than defaulted because the copies were deleted.
- The rejected option closest to the choice is named, along with the condition that would flip the decision, so the choice is bounded rather than absolute. Where that option is the pinned guard, the condition names a use that must hand a named guard on, since a pinned guard can still be returned from a factory as a prvalue.

## Common Failures
- Leaving the compiler-generated copy in place, so the mutex is released more than once.
- Deleting copy operations but forgetting that declaring a destructor can suppress implicit moves.
- Moving the handle without clearing the source's ownership state.
- Defaulting the move operations of a guard that holds a raw handle.

## Notes
This drills the modern form of the ownership decision. A mutex lock guard normally has one active responsibility, so it is either pinned to its scope or transferred by a move, and copying is rejected either way; the exercise implements the move-only form because it carries the harder contract. Defaulted moves are correct only when every member is itself an owner that empties its source; a raw handle is not. If the application instead needs multiple handles to one shared lock state, that is a different abstraction whose final owner performs the unlock.
