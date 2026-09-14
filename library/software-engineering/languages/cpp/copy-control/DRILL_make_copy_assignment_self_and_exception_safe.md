---
object_id: DRILL_make_copy_assignment_self_and_exception_safe
object_type: drill
name: Make a Copy Assignment Operator Self- and Exception-Safe
target_skill: Writing a resource-owning copy assignment operator that survives self-assignment and allocation failure
library_path:
- software-engineering
- languages
- cpp
- copy-control
stage_binding: 3 rough
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- cpp
- copy_control
- self_assignment
- exception_safety
cross_links:
- rel: related_to
  target_object_id: PAT_handle_self_assignment_in_copy_assignment
reference:
  source_title: 'Effective C++, Third Edition: 55 Specific Ways to Improve Your Programs and Designs'
  author: Scott Meyers
confidence: high
references: []
variants: []
---

# Make a Copy Assignment Operator Self- and Exception-Safe

## Practice Task
Start from a legacy `Widget` whose data layout must not change: it owns a raw `Bitmap` pointer, and its assignment operator does `delete pb; pb = new Bitmap(*rhs.pb); return *this;`. Make it safe under self-assignment and allocation failure, then write the class as it would be if its layout were free to change.

## Target Skill
Statement ordering and copy-and-swap for a safe resource-owning copy assignment operator, and knowing how much of that work a standard owning member takes over.

## Setup
Give `Bitmap` a copy constructor that can be made to throw on demand. Build every run twice: once plain, and once under an address sanitizer or with a `Bitmap` that marks itself dead on destruction, so a read of a released resource is visible.

## Instructions
- Before editing, state whether a `Bitmap` value member or a `std::unique_ptr` member owning the `Bitmap` would remove the need for a hand-written assignment operator, and what keeps this class writing its own.
- Reproduce the naive version, execute a self-assignment against it in both builds, and record what each build reports.
- Rewrite it to copy first: save the original pointer, allocate the new copy, then delete the original; return a reference to *this.
- State whether that version needs an identity test, and why.
- Make the `Bitmap` copy throw during an assignment, and record the target's state afterwards and what happens when it is destroyed, for both the naive version and the rewrite.
- Exercise chaining through the returned reference.
- Rewrite it a second time using copy-and-swap. Count allocations and `Bitmap` copies per assignment for the copy-first version, the copy-and-swap version, and an in-place `*pb = *rhs.pb`, and state what each form costs and what guarantee each gives.
- Write the class with a `std::unique_ptr` member owning the `Bitmap`, run the same self-assignment, failure, chaining, and move cases against it, and list which special member functions still have to be written by hand.

## Success Check
- Self-assignment is executed against the naive version in both builds and each result recorded: the plain build can print a garbage or plausible value and exit normally, while the instrumented build shows the resource released and then read. Reasoning about this correctly is common; producing it is what dislodges the belief that an identity check is the fix.
- The run says the copy-first version needs no identity test because the new copy exists before the old one is released — the ordering, not a guard, is what makes it safe.
- The throwing copy is actually triggered: the rewrite leaves the target unchanged, and the naive version is shown leaving a pointer to released memory that its destructor frees a second time. A version that merely looks exception-safe satisfies every other bullet here.
- The operator returns a reference to the object and chaining is exercised. Returning void passes every other bullet and breaks the convention every caller was written against.
- The cost comparison is counted, not asserted. For this class copy-first and copy-and-swap each make one allocation and one `Bitmap` copy per assignment, so neither carries an extra copy over the other; the form that saves the allocation is the in-place assignment, and its guarantee is only whatever `Bitmap`'s own assignment provides. A run that prices copy-and-swap as the version with the extra copy has repeated a claim instead of counting.
- The opening statement names the member that would remove the hand-written operator and the fixed layout that rules it out, and the `unique_ptr` rewrite shows which pieces disappear: the destructor is no longer written and the moves can be defaulted, while both copy operations still have to be written because the member does not copy what it points to, and the moves must be declared because writing the copies suppressed them. A run that answers "use the Rule of Zero" without writing that class has not established what the member removes.

## Common Failures
- Deleting the current resource before copying the new one.
- Adding an identity test but leaving the exception-unsafe ordering underneath it.
- Writing the copy operations over a `unique_ptr` member and not declaring the moves, so `std::move` silently copies the `Bitmap`.

## Notes
Copying before releasing fixes self-assignment and allocation failure at once; the identity test is an optional efficiency tweak, not the fix. A class free to choose its members starts from a value or standard owning member and writes no destructor. This exercise keeps the raw owner because a fixed layout forbids that, and its last rewrite shows how much of the work the member takes over and how much it cannot.
