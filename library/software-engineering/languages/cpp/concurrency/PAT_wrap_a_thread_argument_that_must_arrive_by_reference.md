---
object_id: PAT_wrap_a_thread_argument_that_must_arrive_by_reference
object_type: pattern
name: Wrap a Thread Argument That Must Arrive by Reference
library_path:
- software-engineering
- languages
- cpp
- concurrency
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- cpp
- concurrency
- threading
- parameter_passing
- lifetime
cross_links:
- rel: related_to
  target_object_id: PAT_make_threads_unjoinable_on_every_path
- rel: related_to
  target_object_id: PAT_name_every_lambda_capture
- rel: related_to
  target_object_id: PAT_know_when_two_accesses_are_a_data_race
reference:
  source_title: 'Concurrency with Modern C++: What every professional C++ programmer should know about concurrency'
  author: Rainer Grimm
confidence: high
references: []
variants: []
---

# Wrap a Thread Argument That Must Arrive by Reference

## Pattern Rule
**IF** you are handing an argument to a thread's callable and that callable declares the corresponding parameter as a reference
**THEN** pass `std::ref(object)` (or `std::cref` for an explicit const reference) and prove the referred object outlives the work, because the thread otherwise stores a decayed value and a non-const reference commonly cannot bind while a const reference may observe the stored copy
**ELSE** where the callable takes the parameter by value, or the work is a lambda that captures what it needs, no wrapper belongs there and adding one only reintroduces a lifetime obligation you did not have.

## Do
- Distinguish the two routes an argument takes into a thread, because only one of them has this problem. Arguments passed to the thread's constructor are stored by the thread and then forwarded; things a lambda captures are captured by the lambda under whatever capture mode you wrote, and a capture by reference already refers to the original.
- Make the wrapping visible at the construction site rather than buried in the callable's signature. The function's declaration says it takes a reference; nothing at the call site says whether it will receive one, so the wrapper is the only thing distinguishing the two behaviours to a reader.
- Take on the lifetime obligation deliberately once you have wrapped. A reference that genuinely reaches the thread is a reference into the creator's scope, and that scope must outlive the thread — which turns this into a question about how the thread is joined rather than a question about arguments.
- Prefer passing by copy where the work does not need to write back. The copy has no lifetime obligation at all, and the cost is usually smaller than the reasoning the alternative requires.

## Don't
- Don't assume a reference parameter defeats argument decay. A callable requiring a mutable lvalue reference will commonly make construction ill-formed without `std::ref`; a callable accepting a const reference can bind to the stored value and silently observe a copy rather than the caller's object.
- Don't combine a wrapped reference with work whose lifetime is detached from the owner. Program termination, static-object destruction, and scope exit can invalidate resources a detached thread still uses; structured ownership with `std::jthread`, joining, or another explicit lifetime boundary is safer.
- Don't reach for the wrapper to avoid a copy you have not measured. Its purpose is to make write-back reach the caller, and using it as an optimization buys a lifetime problem in exchange for an unquantified saving.

## Checklist
- Does the thread's callable declare any parameter as a reference?
- Is the corresponding argument wrapped at the construction site?
- If it is, what guarantees the referred-to object outlives the thread?
- Is the thread detached, and if so does it refer to anything in the creator's scope?

## Notes
The default is a copy for a good reason, which is worth knowing so the wrapper reads as an opt-in rather than as boilerplate. A thread outlives the expression that created it, so decaying arguments to copies is the choice that is safe by construction; binding references into a scope that may already be gone is the dangerous case, and the language makes you ask for it by name.

What makes the failure hard to catch is that both halves look right in isolation. The function signature says reference and the construction passes a variable, but decay and storage occur between them. The mutable-reference case often diagnoses the mismatch; the const-reference case may compile against the stored copy, which is why the call site must make reference transport explicit.

The lifetime consequence is the same one that governs joining and detaching, approached from the other side. There the question is what happens to the thread when the scope ends; here it is what the thread is still pointing at when it does. A thread that owns copies of everything it needs makes both questions go away.
