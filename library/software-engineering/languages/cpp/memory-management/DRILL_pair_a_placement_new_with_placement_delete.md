---
object_id: DRILL_pair_a_placement_new_with_placement_delete
object_type: drill
name: Pair a Placement new with a Placement delete and Restore Hidden Forms
target_skill: Matching placement new/delete and re-exposing standard new forms
library_path:
- software-engineering
- languages
- cpp
- memory-management
stage_binding: 2 block
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- cpp
- memory_management
- placement_new
- name_hiding
cross_links:
- rel: related_to
  target_object_id: PAT_pair_placement_new_with_placement_delete
reference:
  source_title: 'Effective C++, Third Edition: 55 Specific Ways to Improve Your Programs and Designs'
  author: Scott Meyers
confidence: high
references: []
variants: []
---

# Pair a Placement new with a Placement delete and Restore Hidden Forms

## Practice Task
Given a class with a logging placement operator new (taking an ostream) but only a normal operator delete, fix the memory leak when the constructor throws, and restore the standard new forms the class new hid.

## Target Skill
Declaring a placement delete matching a placement new, and re-exposing the standard forms.

## Setup
No special setup required.

## Instructions
- Reproduce the leak: construct an object with the placement new and have its constructor throw; observe that no delete runs, and record any warning the compiler gave.
- Add a placement operator delete taking the same ostream parameter, and check that its parameters match the placement new's beyond the first.
- Change that extra parameter so it differs from the placement new's by a qualifier, rebuild, run the exception path, and record the result and the warnings. Then restore the exact match.
- Run the exception path again and show the matching delete executing.
- Keep the normal operator delete for ordinary delete on the pointer, and exercise ordinary deletion separately. Then remove the normal delete, compile the ordinary deletion again, and record the result.
- Before restoring anything, compile an ordinary new, a nothrow new, and a buffer placement new of the class, and record each diagnostic.
- Restore the ordinary, nothrow, and buffer placement forms hidden by the class declaration, and include alignment-aware forms if the class may be over-aligned. Compile every supported form rather than treating a base-class `using` declaration as proof.

## Success Check
- The leak is reproduced by making the constructor throw, with the absent release observed rather than reasoned about.
- The near-match is built and run: a placement delete differing only by a qualifier compiles, is never called, and leaks exactly as the missing one did, and any warning the build gives is the same one the missing delete drew. A rebuild that looks clean after a delete was added proves nothing about the pairing.
- The exception path is run again after the exact match is restored, and the matching delete is shown to execute.
- Ordinary deletion is exercised separately, and with the normal delete removed it fails to compile at the delete expression: a class that declares only a placement delete hides the global one. The placement pair and the normal path are different routes, and each needs its own function.
- Each hidden form is compiled before the repair with its diagnostic recorded — the ordinary, nothrow, and buffer placement forms are all refused — and compiled again after it is restored, including alignment-aware allocation when applicable. A diagnostic need not mention hiding at all, which is why the forms are compiled rather than reasoned about.

## Common Failures
- Declaring a placement new without its matching placement delete.
- Forgetting that the class operator new hides the normal and nothrow forms.
- Restoring the nothrow form and forgetting the buffer placement form, which the class declaration hides too.
- Accepting a near-match as the pairing because the rebuild succeeds.

## Notes
The runtime undoes a failed placement new only through the placement delete whose extra parameters match exactly, and any class operator new hides the ordinary, nothrow, and buffer placement forms until you bring them back.
