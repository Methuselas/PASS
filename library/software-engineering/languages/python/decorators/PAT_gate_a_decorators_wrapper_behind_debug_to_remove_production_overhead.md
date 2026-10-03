---
object_id: PAT_gate_a_decorators_wrapper_behind_debug_to_remove_production_overhead
object_type: pattern
name: Gate a Decorator's Wrapper Behind __debug__ to Remove Production Overhead
library_path:
- software-engineering
- languages
- python
- decorators
stage_binding: 2 block
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- python
- decorators
- debug
- performance
cross_links:
- rel: related_to
  target_object_id: PAT_use_assert_for_development_time_constraints_not_runtime_errors
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Gate a Decorator's Wrapper Behind __debug__ to Remove Production Overhead

## Pattern Rule
**IF** a decorator exists purely to aid development (argument validation, tracing, timing) and its wrapping layer's call overhead is unwanted once a program ships
**THEN** check `__debug__` inside the decorator itself, at decoration time, and return the original function or class completely unwrapped when it is `False`, so no wrapper call happens at all in optimized mode
**ELSE** when the decorator provides behavior the program actually depends on at runtime (not just a development aid), never gate it behind `__debug__`; doing so would silently remove required behavior under the `-O` flag

## Do
- Place the `if not __debug__: return func` check in the decorator function itself, outside the nested wrapper, so the wrapper is never created at all when optimization is enabled — not merely skipped on each call.
- Reach for this only for decorators whose entire purpose is a development-time aid; the decision naturally follows from classifying what the decorator does in the first place.
- Document that running under `-O` changes behavior by removing the decorator's effect entirely, the same documentation obligation that applies to `assert`-based checks removed the same way.

## Don't
- Don't put the `__debug__` check inside the wrapper function and still construct and return a wrapper either way; that still pays the extra-call cost on every invocation, defeating the purpose of gating on `__debug__` at all.
- Don't gate a decorator behind `__debug__` if any of its effects are relied upon for correct production behavior, such as access control that is also a security boundary; `-O` would then silently disable that boundary.
- Don't assume `-O` is commonly used in production deployments before relying on this as a performance strategy; verify it is actually part of the deployment process before designing around its effect.

## Checklist
- Is the `__debug__` check placed in the decorator function, before the wrapper is created, rather than inside the wrapper itself?
- Is this decorator's entire effect something the program can correctly do without once it ships, rather than depended-upon behavior?
- Does anything in the deployment process actually pass `-O`, making this gating meaningful rather than theoretical?

## Notes
`__debug__` and the `-O` flag give a decorator the same two-mode behavior `assert` already has built in: full checking during ordinary development runs, and zero overhead when the interpreter is told to optimize. Checking `__debug__` once, at decoration time, and branching to return the bare original object is what makes the saving real — the wrapper function is never constructed, so there is no extra call for `-O` runs to pay for, as opposed to building the wrapper regardless and merely skipping its body's logic on each call.
