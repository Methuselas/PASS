---
object_id: PAT_state_the_guarantees_a_function_can_honor
object_type: pattern
name: State the Guarantees a Function Can Honor
library_path:
- software-engineering
- languages
- cpp
- foundations
stage_binding: 0 design
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- cpp
- interface_design
- exception_safety
- performance
- compile_time
cross_links:
- rel: related_to
  target_object_id: PAT_define_your_code_contract_explicitly
- rel: related_to
  target_object_id: PAT_lift_a_stable_runtime_value_to_compile_time
- rel: related_to
  target_object_id: PAT_understand_special_member_generation
- rel: related_to
  target_object_id: PAT_optimize_for_what_the_compiler_can_prove
reference:
  source_title: 'Effective Modern C++: 42 Specific Ways to Improve Your Use of C++11 and C++14'
  author: Scott Meyers
confidence: high
references: []
variants: []
---

# State the Guarantees a Function Can Honor

## Pattern Rule
**IF** you are declaring a function that will never emit an exception, or whose result can be computed from compile-time arguments
**THEN** say so in the declaration, because the compiler and your callers can both act on the promise — and take it as an interface commitment you will not be able to withdraw
**ELSE** where the guarantee is not one you can hold for the function's whole future, leave it off; a false promise changes failure behavior and can invalidate caller assumptions.

## Do
- Declare a genuinely non-throwing function `noexcept`. Generic code can inspect the declaration, overload resolution can depend on it, and an escaping exception calls `std::terminate`; any code-generation benefit is toolchain and target dependent rather than the contract's justification.
- Give the promise priority on move operations, swap, and deallocation because library code inspects it. During vector reallocation, a copyable type with a potentially throwing move may be copied to preserve the strong guarantee; a non-copyable type may still have to be moved, with the resulting guarantee governed by the container operation's specification.
- Mark a suitable function `constexpr` so it *may* participate in constant evaluation. A call becomes a constant expression only when its arguments and executed path satisfy constant-expression rules and the surrounding context requires or permits it; ordinary runtime calls remain available.
- Notice what a compile-time value unlocks: array sizes, template arguments, enumerator values, and alignment specifiers all require one, and a function that can produce it can be used in all of those places. An object declared compile-time-constant is also const.
- Treat both as part of the signature rather than as annotations. A caller may write code that depends on the guarantee, and a later revision that withdraws it breaks that caller — which is the ordinary consequence of changing an interface, and worth recognizing as one before the promise is made.

## Don't
- Don't attach either guarantee speculatively, in the hope of a faster build or a faster program. The declaration is a commitment about every future implementation of the function, and the correct question is whether the promise is true rather than whether it would be useful.
- Don't expect the non-throwing guarantee to be checked for you. It is a promise, and violating it at run time terminates the program rather than propagating the exception — so a function that might throw and says otherwise fails harder than one that says nothing.
- Don't assume a move operation is used because it exists. Library code may prefer copying when a move can throw and copying is available; when copying is unavailable, it may move under a weaker conditional guarantee.
- Don't confuse a compile-time-constant object with one that is merely const. Every such object is const; most const objects are not compile-time constants, since their value may not be known until run time.

## Checklist
- Can this function throw, under any implementation you can foresee for it?
- Are the move operations, swap, and any deallocation function declared non-throwing?
- Could this function's result be computed at compile time when given compile-time inputs?
- Is any caller depending on a guarantee here that a future change would remove?
- Where the guarantee is absent, is that a decision or an omission?

## Notes
These two declarations do different jobs and share one property that is easy to miss: both are promises to callers rather than requests to the compiler. That is why they cannot be added and removed freely. A function that gains a guarantee can be relied on; a function that loses one breaks code that relied on it, and the breakage is not always a compile error.

The container-growth example explains why the non-throwing promise on move operations matters out of proportion to its size. `std::move_if_noexcept` captures the usual choice: move when moving is non-throwing or copying is unavailable, otherwise copy. Containers specify their own operation guarantees, but the same trade remains—`noexcept` lets generic code choose the efficient destructive transfer without giving up rollback solely because a copy was available.

The compile-time guarantee reads as an optimization and is better understood as a widening of where the function can appear. Contexts that demand a constant — array bounds, template arguments, enumerator values — are closed to ordinary functions entirely, so the declaration is less about speed than about which code becomes expressible at all.
